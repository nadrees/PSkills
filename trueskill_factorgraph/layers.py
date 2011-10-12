from factorgraphs import FactorGraphLayer, ScheduleSequence, ScheduleStep, FactorGraph, FactorList
from factors import GaussianPriorFactor, GaussianLikelihoodFactor, GaussianWithinFactor, GaussianGreaterThanFactor
from numerics import getDrawMarginFromDrawProbability
from math import e

class TrueSkillFactorGraph(FactorGraph):
	def __init__(self, gameInfo, teams, teamRanks):
		self._priorLayer = PlayerPriorValuesToSkillsLayer(self, teams)
		self._gameInfo = gameInfo
		self._variableFactory = VariableFactory(lambda: fromPrecisionMean(0, 0))
		self._layers = [self._priorLayer, 
				PlayerSkillsToPerformancesLayer(self), 
				PlayerPerformancesToTeamPerformancesLayer(self), 
				IteratedTeamDifferencesInnerLayer(
					self, 
					TeamPerformancesToTeamPerformancesDifferencesLayer(self), 
					TeamDifferencesComparisonLayer(self, teamRanks)
					)
				]
	
	@property
	def gameInfo(self):
		return self._gameInfo
		
	def buildGraph(self):
		lastOutput = None
		for currentLayer in self._layers:
			if lastOutput is not None:
				currentLayer.inputVariablesGroups = lastOutput
			currentLayer.buildLayer()
			lastOutput = currentLayer.outputVariablesGroups
			
	def runSchedule(self):
		fullSchedule = self._createFullSchedule()
		fullSchedule.visit()
		
	def getProbabilityOfRanking(self):
		factorList = FactorList()
		for currentLayer in self._layers:
			for currentFactor in currentLayer.factors:
				factorList.addFactor(currentFactor)
		logZ = factorList.logNormalization
		return e**logZ
		
	def _createFullSchedule(self):
		fullSchedule = list()
		for currentLayer in self._layers:
			currentPriorSchedule = currentLayer.createPriorSchedule()
			if currentPriorSchedule is not None:
				fullSchedule.append(currentPriorSchedule)
		for currentLayer in reversed(self._layers):
			currentPosteriorSchedule = currentLayer.createPosteriorSchedule()
			if currentPosteriorSchedule is not None:
				fullSchedule.append(currentPosteriorSchedule)
		return ScheduleSequence("Full Schedule", fullSchedule)
		
	def getUpdatedRatings(self):
		result = dict()
		for currentTeam in self._priorLayer.outputVariablesGroups:
			for currentPlayer in currentTeam:
				result[currentPlayer.key] = Rating(currentPlayer.value.mean, currentPlayer.value.standardDeviation)
		return result

class IteratedTeamDifferencesInnerLayer(FactorGraphLayer):
	def __init__(self, parentGraph, teamPerformancesToPerformanceDifferences, teamDifferencesComparisonLayer):
		super(IteratedTeamDifferenceInnerLayer, self).__init__(parentGraph)
		self._teamPerformancesToPerformanceDifferences = teamPerformancesToPerformanceDifferences
		self._teamDifferencesComparisonLayer = teamDifferencesComparisonLayer
		
	def buildLayer(self):
		self._teamPerformancesToTeamPerformanceDifferencesLayer.inputVariablesGroups = self._inputVariablesGroups
		self._teamPerformancesToTeamPerformanceDifferencesLayer.buildLayer()
		self._teamDifferencesComparisonLayer.inputVariablesGroups = self._teamPerformancesToTeamPerformanceDifferencesLayer.outputVariablesGroups
		self._teamDifferencesComparisonLayer.buildLayer()
		
	def createPriorSchedule(self):
		loop = None
		count = len(self._inputVariablesGroups)
		if count == 0 or count == 1:
			raise Exception()
		elif count == 2:
			loop = self._createTwoTeamInnerPriorLoopSchedule()
		else:
			loop = self._createMultipleTeamInnerPriorLoopSchedule()
			
		totalTeamDifferences = len(self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors)
		totalteams = totalTeamDifferences + 1
		
		step1 = ScheduleStep("teamPerformanceToPerformanceDifferenceFactors[0] @ 1",	self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[0], 1)
		step2 = ScheduleStep("teamPerformanceToPerformanceDifferenceFactors[teamTeamDifferences = %i - 1] @ 2" % totalTeamDifferences, self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[totalTeamDifferences - 1], 2)
		
		return ScheduleSequence("inner schedule", [loop, step1, step2])
	
	def _createTwoTeaminnerPriorLoopSchedule(self):
		return ScheduleSequence("loop of just two teams inner sequence", [
				ScheduleStep("send team perf to perf differences",
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[0], 0),
				ScheduleStep("send to greater than or within factor",
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[0], 0)])
					
	def _createMultipleTeamInnerPriorLoopSchedule(self):
		totalTeamDifferences = len(self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors)
		
		forwardScheduleList = list()
		for i in range(totalTeamDifferences):
			currentForwardSchedulePiece = ScheduleSequence("current forward schedule piece %i" % i, [
				ScheduleStep("team perf to perf diff %i" % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[i], 0),
				ScheduleStep("greater than or within result factor %i", % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[i], 0),
				ScheduleStep("team perf to perf diff factors [%i], 2", % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[i], 2)
				])
			forwardScheduleList.append(currentForwardSchedulePiece)
		
		forwardSchedule = ScheduleSequence("forward schedule", forwardScheduleList)
		
		backwardScheduleList = list()
		for i in range(totalTeamDifferences):
			currentBackwardSchedulePiece = ScheduleSequence("current backward schedule piece %i" % i, [
				ScheduleStep("teamPerformanceToPerformanceDifferenceFactors[totalTeamDifferences - 1 - %i]" % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[totalTeamDifferences - 1 - i], 0),
				ScheduleStep("greaterThanOrWithinResultFactors[totalTeamDifferences - 1 - %i] @ 0" % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[totalTeamDifferences - 1 - i], 0),
				ScheduleStep("teamPerformanceToPerformanceDifferenceFactors[totalTeamDifferences - 1 - %i]" % i,
					self._teamPerformancesToTeamPerformanceDifferencesLayer.localFactors[totalTeamDifferences - 1 - i], 1)
				])
			backwardScheduleList.append(currentBackwardSchedulePiece)
		
		backwardSchedule = ScheduleSequence("backward schedule", backwardScheduleList)
		
		forwardBackwardScheduleToLoop = ScheduleSequence("foward backward schedule to loop", [forwardSchedule, backwardSchedule])
		
		initialMaxDelta = 0.0001
		loop = ScheduleLoop("loop with max delta of %f" % initialMaxDelta, forwardBackwardScheduleToLoop, initialMaxDelta)
		
		return loop
	
class PlayerPriorValuesToSkillsLayer(FactorGraphLayer):
	def __init__(self, parentGraph, teams):
		super(PlayerPriorValuesToSkillsLayer, self).__init__(parentGraph)
		self._teams = teams
		
	def buildLayer(self):
		for currentTeam in self._teams:
			currentTeamSkills = list()
			for player, rating in currentTeam.iteritems():
				playerSkill = self._createSkillOutputVariable(player)
				self.addLayerFactor(self._createPriorFactor(player, rating, playerSkill))
				currentTeamSkills.append(playerSkill)
			self._outputVariablesGroups.append(currentTeamSkills)
			
	def createPriorSchedule(self):
		schedules = list()
		for prior in self._localFactors:
			schedules.append(ScheduleStep("Prior to skill step", prior, 0))
		return ScheduleSequence("All priors", schedules)
		
	def _createPriorFactor(self, player, priorRating, skillsVariable):
		return GaussianPriorFactor(priorRating.mean, priorRating.standardDeviation**2.0, self_parentFactorGraph.gameInfo.dynamicsFactor**2.0, skillsVariable)
		
	def _createSkillOutputVariable(self, player):
		return self._paretFactorGraph.variableFactory.createKeyedVariable("%s's skill" % player, player)
		
class PlayerSkillsToPerformancesLayer(FactorGraphLayer):
	def buildLayer(self):
		for currentTeam in self._inputVariablesGroups:
			currentTeamPlayerPerformances = list()
			for player, rating in currentTeam.iteritems():
				playerPerformance = self._createOutputVariable(player)
				self.addLayerFactor(self._createLikelihood(rating, playerPerformance)
				currentTeamPlayerPerformances.append(playerPerformance)
			self._outputVariableGroups.append(currentTeamPlayerPerformances)
	
	def _createLikelihood(self, playerSkill, playerPerformance):
		return GaussianLikelihoodFactor(self._parentFactorGraph.gameInfo.beta**2.0, playerPerformance, playerSkill)
		
	def _createOutputVariable(self, key):
		return self._parentFactorGraph.variableFactory.createKeyedVariable("%s's performance" % key, key)
		
	def createPriorSchedule(self):
		schedules = list()
		for likelihood in self._localFactors:
			schedules.append(ScheduleStep("Skill to perf step", likelihood, 0))
		return ScheduleSequence("All skill to performance sending", schedules)
		
	def createPosteriorSchedule(self):
		schedules = list()
		for likelihood in self._localFactors:
			schedules.append(ScheduleStep("name", likelihood, 1))
		return ScheduleSequence("All skill to performance sending", schedules)
		
class TeamDifferenceComparisonLayer(FactorGraphLayer):
	def __init__(self, parentGraph, teamRanks):
		super(TeamDifferenceComparisonLayer, self).__init__(parentGraph)
		self._teamRanks = teamRanks
		self._epsilon = getDrawMarginFromDrawProbability(parentGraph.gameInfo.drawProbability, parentGraph.gameInfo.beta)
		
	def buildLayer(self):
		for i in range(len(self._inputVariableGroups)):
			isDraw = (self._teamRanks[i] == self._teamRanks[i + 1])
			teamDifference = self._inputVariablesGroups[i][0]
			factor = GaussianWithinFactor(self._epsilon, teamDifference) if isDraw else GaussianGreaterThanFactor(self._epsilon, teamDifference)
			self.addLayerFactor(factor)
