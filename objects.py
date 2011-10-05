_defaultPartialPlayPercentage = 1.0
_defaultPartialUpdatePercentage = 1.0

_defaultInitialMean = 25.0
_defaultBeta = _defaultInitialMean/6.0
_defaultDrawProbability = .10
_defaultDynamicsFactor = _defaultInitialMean/300.0
_defaultInitialStandardDeviation = _defaultInitialMean/3.0

_defaultConservativeStandardDeviationMultiplier = 3.0

def defaultGameInfo():
	return GameInfo(_defaultInitialMean, _defaultInitialStandardDeviation, _defaultBeta, _defaultDynamicsFactor, _defaultDrawProbability)

def getPartialPlayPercentage(player):
	if isinstance(player, SupportPartialPlay):
		partialPlayPercentage = player.partialPlayPercentage
		return partialPlayPercentage if partialPlayPercentage > .0001 else .0001
	else:
		return 1.0 # assume 100% since the player doesnt support partial play

def argumentNotNone(arg, argName):
	assert arg is not None, argName

def argumentIsValidIndex(index, count, argName):
	assert index >= 0 and index < count, argName

def argumentInRangeInclusive(value, minimum, maximum, argName):
	assert value >= minimum and value <= maximum, argName

def isEqual(arg1, arg2, argName):
	assert arg1 == arg2, argName

def sortByRank(teams, ranks):
	'''
	Sorts the teams in increasing order of their ranks. len(teams) must equal len(ranks), and both teams and ranks are lists.
	Returns a tuple of two sorted lists: the teams first, and then the ranks
	'''
	argumentNotNone(teams, "teams")
	argumentNotNone(ranks, "ranks")
	isEqual(len(teams), len(ranks), "length of args")
	team_tuples = []
	for i in range(len(teams)):
		team_tuples.append((teams[i], ranks[i]))
	team_tuples.sort(key=lambda currentTuple: currentTuple[1])
	teams = list()
	ranks = list()
	for i in range(len(team_tuples)):
		teams.append(team_tuples[i][0])
		ranks.append(team_tuples[i][1])
	return (teams, ranks)

def partialUpdate(prior, fullPosterior, updatePercentage):
	priorGaussian = GaussianDistribution.fromRating(prior)
	posteriorGaussian = GaussianDistribution.fromRating(fullPosterior)
	precisionDifference = posteriorGaussian.precision - priorGaussian.precision
	partialPrecisionDifference = updatePercentage*precisionDifference
	precisionMeanDifference = posteriorGaussian.precisionMean - priorGaussian.precisionMean
	partialPrecisionMeanDifference = updatePercentage*precisionMeanDifference
	partialPosteriorGaussian = GaussianDistribtuion.fromPrecisionMean(priorGaussian.precisionMean + partialPrecisionMeanDifference, priorGaussian.precision + partialPrecisionMeanDifference)
	return Rating(partialPosteriorGaussian.mean, partialPosteriorGaussian.standardDeviation, prior.conservativeStandardDeviationMultiplier)

def calcMeanMean(ratings):
	ret = 0
	for rating in ratings:
		ret = ret + rating.mean
	return ret/len(ratings)

def _validateTeamCountAndPlayersCountPerTeam(teams, totalTeams, playersPerTeam):
	argumentNotNone(teams, "teams")
	countOfTeams = 0
	for currentTeam in teams:
		numPlayers = len(currentTeam.asListOfTuples)
		assert playersPerTeam.isInRange(numPlayers), currentTeam
		countOfTeams += 1
	assert totalTeams.isInRange(countOfTeams), countOfTeams

class GameInfo(object):
	'''Parameters about the game for calculating the TrueSkill'''
	@property
	def initialMean(self):
		return self._initialMean

	@initialMean.setter
	def initialMean(self, value):
		self._initialMean = value

	@property
	def initialStandardDeviation(self):
		return self._initialStandardDeviation

	@initialStandardDeviation.setter
	def initialStandardDeviation(self, value):
		self._initialStandardDeviation = value

	@property
	def beta(self):
		return self._beta

	@beta.setter
	def beta(self, value):
		self._beta = value

	@property
	def dynamicsFactor(self):
		return self._dynamicsFactor

	@dynamicsFactor.setter
	def dynamicsFactor(self, value):
		self._dynamicsFactor = value

	@property
	def drawProbability(self):
		return self._drawProbability

	@drawProbability.setter
	def drawProbability(self, value):
		self._drawProbability = value

	@property
	def defaultRating(self):
		return Rating(self._initialMean, self._initialStandardDeviation)

	def __init__(self, initialMean, initialStandardDeviation, beta, dynamicFactor, drawProbability):
		self._initialMean = initialMean
		self._initialStandardDeviation = initialStandardDeviation
		self._beta = beta
		self._dynamicsFactor = dynamicFactor
		self._drawProbability = drawProbability

class SupportPartialPlay(object):
	'''Class to be extended and implemented for denoting that a class supports partial play'''
	@property
	def partialPlayPercentage(self):
		'''
		Indicates the percent of time the player should be weighted where 0.0 indicates the player didn't play
		and 1.0 indicates the player played 100% of the time
		'''
		raise NotImplementedError()

class SupportPartialUpdate(object):
	'''Class to be extended and implemented for denoting that a class supports partial updates'''
	@property
	def partialUpdatePercentage(self):
		'''
		Indicated how much of a skill update a player should receive where 0.0 represents no update and 1.0
		represents 100% of the update
		'''
		raise NotImplementedError()

class PairwiseComparison(object):
	'''Enum like class for pairwise comparisons between players'''
	WIN = 1
	DRAW = 0
	LOSE = -1

class Player(SupportPartialPlay, SupportPartialUpdate):
	'''Represents a player who has a Rating'''
	@property
	def id(self):
		return self._id

	@property
	def partialPlayPercentage(self):
		return self._partialPlayPercentage

	@property
	def partialUpdatePercentage(self):
		return self._partialUpdatePercentage

	def __init__(self, ID, partialPlayPercentage = _defaultPartialPlayPercentage, partialUpdatePercentage = _defaultPartialUpdatePercentage):
		argumentInRangeInclusive(partialPlayPercentage, 0, 1.0, "partialPlayPercentage")
		argumentInRangeInclusive(partialUpdatePercentage, 0, 1.0, "partialUpdatePercentage")
		self._id = ID
		self._partialPlayPercentage = partialPlayPercentage
		self._partialUpdatePercentage = partialUpdatePercentage

	def __eq__(self, other):
		return isinstance(other, Player) and self._id == other.id

	def __ne__(self, other):
		return (self == other) == False

class Team(object):
	'''Helper class for working with a team'''
	def __init__(self, player = None, rating = None):
		'''
		Constructs a team with the specified player who has the specified rating
		player should be an instance of the Player class
		rating should be an instance of the Rating class
		'''
		self._playerRatings = list()
		if player is not None and rating is not None:
			self._playerRatings.append((player, rating))

	def addPlayer(self, player, rating):
		self._playerRatings.append((player, rating))

	@property
	def asListOfTuples(self):
		return self._playerRatings
		
	@property
	def size(self):
		return len(self._playerRatings)
		
	@property
	def meanSum(self):
		return sum(map(lambda playerTuple: playerTuple[1].mean, self._playerRatings))
		
	@property
	def standardDeviationSquaredSum(self):
		return sum(map(lambda playerTuple: playerTuple[1].standardDeviation**2.0, self._playerRatings))

class Rating(object):
	'''Container for a player's rating'''
	@property
	def conservativeStandardDeviationMultiplier(self):
		return self._conservativeStandardDeviationMultiplier

	@conservativeStandardDeviationMultiplier.setter
	def conservativeStandardDeviationMultipler(self, value):
		self._conservativeStandardDeviationMultiplier = value

	@property
	def mean(self):
		'''Mu'''
		return self._mean

	@mean.setter
	def mean(self, value):
		self._mean = value

	@property
	def standardDeviation(self):
		'''Sigma'''
		return self._standardDeviation

	@standardDeviation.setter
	def standardDeviation(self, value):
		self._standardDeviation = value

	def getVariance(self):
		'''The variance of the rating (standard deviation squared)'''
		return self._standardDeviation**2

	@property
	def conservativeRating(self):
		'''A conservative estimate of skill based on the mean and standard deviation'''
		return self._conservativeRating

	@conservativeRating.setter
	def conservativeRating(self, value):
		self._conservativeRating = value

	def __init__(self, mean, standardDeviation, conservativeStandardDeviationMultiplier = None):
		'''
		Constructs a rating
		mean - the statistical mean value of the rating (mu)
		standardDeviation - the standard deviation of the rating (sigma)
		conservativeStandardDeviationMultipler - the number of standardDeviations to subtract from the mean to achieve a conservative rating
		'''
		self._mean = mean
		self._standardDeviation = standardDeviation
		self._conservativeStandardDeviationMultiplier = conservativeStandardDeviationMultiplier if conservativeStandardDeviationMultiplier is not None else _defaultConservativeStandardDeviationMultiplier
		self._conservativeRating = self._mean - self._conservativeStandardDeviationMultiplier*self._standardDeviation

class SupportedOptions(object):
	'''Enum like class to represent the options supported by the skill calculator'''
	NONE = 0x00
	PARTIAL_PLAY = 0x01
	PARTIAL_UPDATE = 0x02

_options = SupportedOptions()

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
		returns a list of tuples of (team, new rating)
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
