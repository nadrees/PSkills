import numerics

__defaultConservativeStandardDeviationMultiplier = 3.0

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
		self._conservativeStandardDeviationMultiplier = conservativeStandardDeviationMultiplier if conservativeStandardDeviationMultiplier is not None else __defaultConservativeStandardDeviationMultiplier
		self._conservativeRating = self._mean - self._conservativeStandardDeviationMultipler*self._standardDeviation

