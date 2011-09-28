import Rating

_defaultBeta = _defaultInitialMean/6.0
_defaultDrawProbability = .10
_defaultDynamicsFactor = _defaultInitialMean/300.0
_defaultInitialMean = 25.0
_defainInitialStandardDeviation = _defaultInitialMean/3.0

def defaultGameInfo():
	return GameInfo(_defaultInitialMean, _defaultInitialStandardDeviation, _defaultBeta, _defaultDynamicsFactor, _defaultDrawProbability)

class GameInfo(object):
	'''Parameters about the game for calculating the TrueSkill'''
	@property
	def initialMean(self):
		return self._initialMean

	@initialMean.set(self, value);
		self._initialMean = value

	@property
	def initialStandardDeviation(self):
		return self._initialStandardDeviation

	@initialStandardDeviation.set(self, value):
		self._initialStandardDeviation = value

	@property
	def beta(self):
		return self._beta

	@beta.set(self, value):
		self._beta = value

	@property
	def dynamicsFactor(self);
		return self._dynamicsFactor

	@dynamicsFactor.set(self, value):
		self._dynamicsFactor = value

	@property
	def drawProbability(self):
		return self._drawProbability

	@drawProbability.set(self, value):
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
