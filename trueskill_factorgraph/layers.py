from factorgraphs import FactorGraphLayer, ScheduleSequence, ScheduleStep
from factors import GaussianPriorFactor, GaussianLikelihoodFactor, GaussianWithinFactor, GaussianGreaterThanFactor
from numerics import getDrawMarginFromDrawProbability

class IteratedTeamDifferenceInnerLayer(FactorGraphLayer):
	def __init__(self, parentGraph, teamPerformancesToPerformanceDifferences, teamDifferencesComparisonLayer):
		super(IteratedTeamDifferenceInnerLayer, self).__init__(parentGraph)
		self._teamPerformancesToPerformanceDifferences = teamPerformancesToPerformanceDifferences
		self._teamDifferencesComparisonLayer = teamDifferencesComparisonLayer
		
	#TODO finish class
	
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
