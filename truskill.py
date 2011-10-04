from objects import SkillCalculator, SupportedOptions, argumentNotNull, sortByRank, PairwiseComparison, Rating
from numerics import exactly, inverseCumulativeTo, cumulativeTo, at
from math import sqrt, e

def getDrawMarginFromDrawProbability(drawProbability, beta):
	return inverseCumulativeTo(0.5*(drawProbability + 1), 0, 1)*sqrt(1 + 1)*beta
	
def vExceedsMargin(teamPerfomanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerfofmanceDifference / c
		drawMargin = drawMargin / c
	denominator = cumulativeTo(teamPerformaceDifference - drawMargin)
	if denominator < 2.222758749e-162:
		return -1 * teamPerfomanceDifference + drawMargin
	else:
		return at(teamPerformanceDifference - drawMargin) / denominator
		
def wExceedsMargin(teamPerfomanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerformanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	denominator = cumulativeTo(teamPerformanceDifference - drawMargin)
	if denominator < 2.222758749e-162:
		if teamPerformanceDifference < 0.0:
			return 1.0
		return 0.0
	vWin = vExceedMargin(teamPerformanceDifference, drawMargin)
	return vWin*(vWin + teamPerformanceDifference - drawMargin)
	
def vWithinMargin(teamPerformanceDifference, drawMargin, c = None):
	if c is not None:
		teamPerfomanceDifference = teamPerformanceDifference / c
		drawMargin = drawMargin / c
	teamPerformanceDifferenceAbsoluteValue = abs(teamPerformanceDifference)
	denominator = cumulativeTo(drawMargin - teamPerformanceDifferenceAbsoluteValue) - cumulativeTo(-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue)
	if denominator < 2.222758749e-162:
		if teamPerformanceDifference < 0.0:
			return -1*teamPerformanceDifference - drawMargin
		return -1*teamPerformanceDifference + drawMargin
	numerator = at(-1*drawMaring - teamPerformanceDifferenceAbsoluteValue) - at(drawMargin - treamPerformanceDifferenceAbsoluteValue)
	if teamPerformanceDifference < 0.0:
		return -1*numerator/denomintor
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
	return vt**2.0 + 
		((drawMargin - teamPerformanceDifferenceAbsoluteValue)
		*
		at(drawMargin - teamPerformanceDifferenceAbsoluteValue)
		-
		(-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue)
		*
		at(-1 * drawMargin - teamPerformanceDifferenceAbsoluteValue))/denominator

class TwoPlayerTrueSkillCalculator(SkillCalculator):
	'''
	Calculates the new ratings for only two players
	
	When you only have two players, a lot of the math simlifies. The main purpose of this class is to show the bare minimum of what 
	a TrueSkill implementation should have
	'''
	def __init__(self):
		super(SkillCalculator, self).__init__(SupportedOptions.NONE, exactly(2), exactly(1))
		
	def calculateNewRatings(self, gameInfo, teams, teamRanks):
		argumentNotNull(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		teams, teamRanks = sortByRank(teams, teamRanks)

		winningTeamPlayers = teams[0].asListOfTuples()
		#since we know each team has one player, we know the player is the first one
		winningPlayer = winningTeamPlayers[0][0]
		winningPlayerOldRating = winningTeamPlayers[0][1]
		
		losingTeamPlayers = teams[1].asListOfTuples()
		losingPlayer = losingTeamPlayers[0][0]
		losingPlayerOldRating = losingTeamPlayers[0][1]
		
		wasDraw = (teamRanks[0] == teamRanks[1])
		results = list()
		results.append(
			(teams[0], 
			self._calculateNewRating(
				gameInfo, winningPlayerOldRating, losingPlayerOldRating, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.WIN)
		))
		results.append(
			(teams[1],
			self._calculateNewRating(
				gameInfo, losingPlayerOldRating, winningPlayerOldRating, PairwiseComparison.DRAW if wasDraw else PairwiseComparison.LOSE)
		))
		return results
		
	def _calculateNewRating(self, gameInfo, selfRating, opponentRating, comparison):
		drawMargin = getDrawMarginFromDrawProbability(gameInfo.drawProbability, gameInfo.beta)
		c = sqrt((selfRating.standardDeviation**2) + (opponentRating.standardDeviation**2) + 2*(gameInfo.beta**2)
		winningMean = selfRating.mean if comparison != PairwiseComparison.LOSE else opponentRating.mean
		losingMean = opponentRating.mean if comparison != PairwiseComparison.LOSE else selfRating.mean
		meanDelta = winningMean - losingMean
		v = None
		w = None
		rankMultiplier = None
		if comparison != PairwiseComparison.DRAW:
			v = vExceedsMargin(meanDelta, drawMargin, c)
			w = wExceedsMargin(meanDelta, drawMargin, c)
			rankMultiplier = int(comparison)
		else:
			v = vWithinMargin(meanDelta, drawMargin, c)
			w = wWithinMargin(meanDelta, drawMargin, c)
			rankMultiplier = 1
		meanMultiplier = ((selfRating.standardDeviation**2) + (gameInfor.dynamicsFactor**2)) / c
		varianceWithDynamics = (selfRating.standardDeviation**2) + (gameInfor.dynamicsFactor**2)
		stdDevMultiplier = varianceWithDynamics/(c**2)
		newMean = selfRating.mean + (rankMultiplier*meanMultiplier*v)
		netStdDev = sqrt(varianceWithDynamics*(1 - w*stdDevMultiplier))
		return Rating(newMean, newStdDev)
		
	def calculateMatchQuality(self, gameInfo, teams):
		argumentNotNull(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		player1Rating = teams[0].asListOfTuples()[0][1]
		player2Rating = teams[1].asListOfTuples()[0][1]
		betaSquared = (gameInfo.beta**2)
		player1SigmaSquared = (player1Rating.standardDeviation**2)
		player2SigmaSquared = (player2Rating.standardDeviation**2)
		sqrtPart = sqrt((2*betaSquared) / (2*betaSquared + player1SigmaSquared + player2SigmaSquared))
		expPart = e**((-1*((player1Rating.mean - player2Rating.mean)**2)) / (2*(2*betaSquared + player1SigmaSquared + player2SigmaSquared)))
		return sqrtPart*expPart
