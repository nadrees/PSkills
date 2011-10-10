from factorgraphs import FactorGraphLayer, ScheduleSequence, ScheduleStep
from factors import GaussianPriorFactor

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
				self._addLayerFactor(self._createPriorFactor(player, rating, playerSkill))
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
				#TODO finish
