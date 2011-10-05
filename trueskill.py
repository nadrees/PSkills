from objects import SkillCalculator, SupportedOptions, argumentNotNone, sortByRank, PairwiseComparison, Rating
from numerics import atLeast, exactly, inverseCumulativeTo, cumulativeTo, at
from math import sqrt, e

def getDrawMarginFromDrawProbability(drawProbability, beta):
	return inverseCumulativeTo(0.5*(drawProbability + 1), 0, 1)*sqrt(1 + 1.0)*beta
	
def vExceedsMargin(teamPerformanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	denominator = cumulativeTo(teamPerformanceDifference - drawMargin)
	if denominator < 2.222758749e-162:
		return -1.0 * teamPerformanceDifference + drawMargin
	else:
		return at(teamPerformanceDifference - drawMargin) / denominator
		
def wExceedsMargin(teamPerformanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	denominator = cumulativeTo(teamPerformanceDifference - drawMargin)
	if denominator < 2.222758749e-162:
		if teamPerformanceDifference < 0.0:
			return 1.0
		return 0.0
	vWin = vExceedsMargin(teamPerformanceDifference, drawMargin)
	return vWin*(vWin + teamPerformanceDifference - drawMargin)
	
def vWithinMargin(teamPerformanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	teamPerformanceDifferenceAbsoluteValue = abs(teamPerformanceDifference)
	denominator = cumulativeTo(drawMargin - teamPerformanceDifferenceAbsoluteValue) - cumulativeTo(-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue)
	if denominator < 2.222758749e-162:
		if teamPerformanceDifference < 0.0:
			return -1.0*teamPerformanceDifference - drawMargin
		return -1.0*teamPerformanceDifference + drawMargin
	numerator = at(-1.0*drawMargin - teamPerformanceDifferenceAbsoluteValue) - at(drawMargin - teamPerformanceDifferenceAbsoluteValue)
	if teamPerformanceDifference < 0.0:
		return -1.0*numerator/denominator
	return numerator / denominator
	
def wWithinMargin(teamPerformanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	teamPerformanceDifferenceAbsoluteValue = abs(teamPerformanceDifference)
	denominator = cumulativeTo(drawMargin - teamPerformanceDifferenceAbsoluteValue) - cumulativeTo(-1*drawMargin - teamPerformanceDifferenceAbsoluteValue)
	if denominator < 2.222758749e-162:
		return 1.0
	vt = vWithinMargin(teamPerformanceDifferenceAbsoluteValue, drawMargin)
	return vt**2.0 + ((drawMargin - teamPerformanceDifferenceAbsoluteValue)	* at(drawMargin - teamPerformanceDifferenceAbsoluteValue) - (-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue) * at(-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue))/denominator

class TwoTeamTrueSkillCalculator(SkillCalculator):
	'''
	Calculates the new ratings for only two teams where each team has at least 1 player

	When you only have two teams, the math is still simple: no factor graphs are used yet
	'''
	def __init__(self):
		super(TwoTeamTrueSkillCalculator, self).__init__(SupportedOptions.NONE, exactly(2), atLeast(1))
		
	def calculateNewRatings(self, gameInfo, teams, teamRanks):
		'''Implementation for a 2 team game. Returns a list of tuples of (player, rating)'''
		argumentNotNone(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		teams, teamRanks = sortByRank(teams, teamRanks)
		
		team1 = teams[0]
		team2 = teams[1]
		
		wasDraw = (teamRanks[0] == teamRanks[1])
		
		results = list()
		self._updatePlayerRatings(gameInfo, results, team1, team2, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.WIN)
		self._updatePlayerRatings(gameInfo, results, team2, team1, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.LOSE)
		return results
		
	def _updatePlayerRatings(self, gameInfo, newPlayerRatings, selfTeam, otherTeam, selfToOtherComparison):
		drawMargin = getDrawMarginFromDrawProbability(gameInfo.drawProbability, gameInfo.beta)
		betaSquared = gameInfo.beta**2.0
		tauSquared = gameInfo.dynamicsFactor**2.0

		totalPlayers = selfTeam.size + otherTeam.size
		
		selfTeamMeanSum = selfTeam.meanSum
		otherTeamMeanSum = otherTeam.meanSum
		selfTeamStandardDeviationSum = selfTeam.standardDeviationSquaredSum
		otherTeamStandardDeviationSum = otherTeam.standardDeviationSquaredSum
		
		c = sqrt(selfTeamStandardDeviationSum + otherTeamStandardDeviationSum + totalPlayers*betaSquared)
		winningMean = selfTeamMeanSum
		losingMean = otherTeamMeanSum
		if selfToOtherComparison == PairwiseComparison.LOSE:
			winningMean = otherTeamMeanSum
			losingMean = selfTeamMeanSum
		meanDelta = winningMean - losingMean
		
		v = None
		w = None
		rankMultiplier = None
		if selfToOtherComparison != PairwiseComparison.DRAW:
			v = vExceedsMargin(meanDelta, drawMargin, c)
			w = wExceedsMargin(meanDelta, drawMargin, c)
			rankMultiplier = selfToOtherComparison
		else:
			v = vWithinMargin(meanDelta, drawMargin, c)
			w = wWithinMargin(meanDelta, drawMargin, c)
			rankMultiplier = 1
		
		for playerTuple in selfTeam.asListOfTuples:
			previousPlayerRating = playerTuple[1]
			meanMultiplier = ((previousPlayerRating.standardDeviation**2.0) + tauSquared) / c
			stdDevMultiplier = ((previousPlayerRating.standardDeviation**2.0) + tauSquared) / (c**2.0)
			playerMeanDelta = rankMultiplier*meanMultiplier*v
			newMean = previousPlayerRating.mean + playerMeanDelta
			newStdDev = sqrt(((previousPlayerRating.standardDeviation**2.0) + tauSquared) * (1 - w*stdDevMultiplier))
			newPlayerRatings.append((playerTuple[0], Rating(newMean, newStdDev)))
			
	def calculateMatchQuality(self, gameInfo, teams):
		argumentNotNone(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		
		team1 = teams[0]
		team2 = teams[1]
		
		totalPlayers = team1.size + team2.size
		betaSquared = gameInfo.beta**2.0
		
		team1MeanSum = team1.meanSum
		team1StdDevSum = team1.standardDeviationSquaredSum
		
		team2MeanSum = team2.meanSum
		team2StdDevSum = team2.standardDeviationSquaredSum
		
		sqrtPart = sqrt((totalPlayers*betaSquared) / (totalPlayers*betaSquared + team1StdDevSum + team2StdDevSum))
		expPart = e**((-1.0*(team1MeanSum - team2MeanSum)**2.0) / (2*(totalPlayers*betaSquared +team1StdDevSum + team2StdDevSum)))
		return sqrtPart * expPart

class TwoPlayerTrueSkillCalculator(SkillCalculator):
	'''
	Calculates the new ratings for only two players
	
	When you only have two players, a lot of the math simlifies. The main purpose of this class is to show 
	the bare minimum of what a TrueSkill implementation should have
	'''
	def __init__(self):
		super(TwoPlayerTrueSkillCalculator, self).__init__(SupportedOptions.NONE, exactly(2), exactly(1))
		
	def calculateNewRatings(self, gameInfo, teams, teamRanks):
		'''Implementation for a 2 player game. returns a list of tuples of (player, newRating)'''
		argumentNotNone(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		teams, teamRanks = sortByRank(teams, teamRanks)

		winningTeamPlayers = teams[0].asListOfTuples
		#since we know each team has one player, we know the player is the first one
		winningPlayer = winningTeamPlayers[0][0]
		winningPlayerOldRating = winningTeamPlayers[0][1]
		
		losingTeamPlayers = teams[1].asListOfTuples
		losingPlayer = losingTeamPlayers[0][0]
		losingPlayerOldRating = losingTeamPlayers[0][1]
		
		wasDraw = (teamRanks[0] == teamRanks[1])
		results = list()
		results.append(
			(winningPlayer, 
			self._calculateNewRating(
				gameInfo, winningPlayerOldRating, losingPlayerOldRating, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.WIN)
		))
		results.append(
			(losingPlayer,
			self._calculateNewRating(
				gameInfo, losingPlayerOldRating, winningPlayerOldRating, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.LOSE)
		))
		return results
		
	def _calculateNewRating(self, gameInfo, selfRating, opponentRating, comparison):
		drawMargin = getDrawMarginFromDrawProbability(gameInfo.drawProbability, gameInfo.beta)
		c = sqrt((selfRating.standardDeviation**2.0) + (opponentRating.standardDeviation**2.0) + 2.0*(gameInfo.beta**2.0))
		winningMean = selfRating.mean
		losingMean = opponentRating.mean
		if comparison == PairwiseComparison.LOSE:
			winningMean = opponentRating.mean
			losingMean = selfRating.mean
		meanDelta = winningMean - losingMean
		v = None
		w = None
		rankMultiplier = None
		if comparison != PairwiseComparison.DRAW:
			v = vExceedsMargin(meanDelta, drawMargin, c)
			w = wExceedsMargin(meanDelta, drawMargin, c)
			rankMultiplier = comparison
		else:
			v = vWithinMargin(meanDelta, drawMargin, c)
			w = wWithinMargin(meanDelta, drawMargin, c)
			rankMultiplier = 1.0
		meanMultiplier = ((selfRating.standardDeviation**2.0) + (gameInfo.dynamicsFactor**2.0)) / c
		varianceWithDynamics = (selfRating.standardDeviation**2) + (gameInfo.dynamicsFactor**2)
		stdDevMultiplier = varianceWithDynamics/(c**2.0)
		newMean = selfRating.mean + (rankMultiplier*meanMultiplier*v)
		newStdDev = sqrt(varianceWithDynamics*(1 - w*stdDevMultiplier))
		return Rating(newMean, newStdDev)
		
	def calculateMatchQuality(self, gameInfo, teams):
		argumentNotNone(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		player1Rating = teams[0].asListOfTuples[0][1]
		player2Rating = teams[1].asListOfTuples[0][1]
		betaSquared = (gameInfo.beta**2.0)
		player1SigmaSquared = (player1Rating.standardDeviation**2.0)
		player2SigmaSquared = (player2Rating.standardDeviation**2.0)
		sqrtPart = sqrt((2.0*betaSquared) / (2.0*betaSquared + player1SigmaSquared + player2SigmaSquared))
		expPart = e**((-1.0*((player1Rating.mean - player2Rating.mean)**2.0)) / (2.0*(2.0*betaSquared + player1SigmaSquared + player2SigmaSquared)))
		return sqrtPart*expPart
