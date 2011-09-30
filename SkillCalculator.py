class SupportedOptions(object):
	'''Enum like class to represent the options supported by the skill calculator'''
	NONE = 0x00
	PARTIAL_PLAY = 0x01
	PARTIAL_UPDATE = 0x02

_options = SupportedOptions()

def _validateTeamCountAndPlayersCountPerTeam(teams, totalTeams, playersPerTeam):
	Gaurd.argumentNotNone(teams, "teams")
	countOfTeams = 0
	for currentTeam in teams:
		assert playersPerTeam.isInRange(len(currentTeam)), currentTeam
		countOfTeams += 1
	assert totalTeams.isInRange(countOfTeams), countOfTeams

class SkillCalculator(object):
	'''The abstract super class for calculating updates to players skills'''
	def __init__(self, supportedOptions, totalTeamsAllowed, playersPerTeamAllowed):
		self._supportedOptions = supportedOptions
		self._playersPerTeamAllowed = playersPerTeamAllowed
		self._totalTeamsAllowed = totalTeamsAllowed

	def calculateNewRatings(self, gameInfo, teams, teamRanks):
		'''
		Calculates new ratings based on the prior ratings and team ranks
		gameInfo should be an instance of the GameInfo class
		teams should be a list of mappings of players to their teams
		teamRanks should be a list of the ranks of the teams, where 1 is first place. A tie is represented as a repeated number
		'''
		raise NotImplementedError()

	def calculateMatchQuality(self, gameInfo, teams):
		'''
		Calculates the match quality as the likelihood of all teams drawing
		gameInfo should be an instance of the GameInfo class
		teams should be a list of mappings of players to their teams
		'''
		raise NotImplementedError()

	def isSupported(self, option):
		return (self._supportedOptions & option) == option

	def _validateTeamCountAndPlayersCountPerTeam(self, teams):
		_validateTeamCountAndPlayersCountPerTeam(teams, self._totalTeamsAllowed, self._playersPerTeamAllowed)
