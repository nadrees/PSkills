from math import sqrt
from math import pi
from math import log
from math import e
from MathUtils import mean
import unittest

def fromRating(rating):
	return GaussianDistribution(rating.mean, rating.standardDeviation)

def fromGaussianDistribution(distibution):
	return GaussianDistribution(distribution.mean, distribution.standardDeviation, distribution.precision, distribution.precisionMean)

def fromPrecisionMean(precisionMean, precision):
	return GaussianDistribution(precisionMean / precision, sqrt(1.0 / precision), 1.0 / precision, precision, precisionMean)

def mult(left, right):
	return left.mult(right)

def absoluteDifference(left, right):
	"""Computes the absolute difference between two Gaussians"""
	return max(abs(left.precisionMean - right.precisionMean), sqrt(abs(left.precision - right.precision)))

def sub(left, right):
	"""Computes the absolute difference between two Gaussians"""
	return absoluteDifference(left, right)

def divide(numerator, denominator):
	return numeration.divide(denominator)

def logRatioNormalization(numerator, denominator):
	if numerator.precision == 0 or denominator.precision == 0:
		return 0
	varianceDifference = denominator.variance - numerator.variance
	meanDifference = numerator.mean - denominator.mean
	logSqrt2Pi = log(sqrt(2*pi))
	return log(denominator.variance) + logSqrt2Pi - log(varianceDifference)/2.0 + (meanDifference**2)/(2.0*varianceDifference)

def logProductNormalization(left, right):
	if (left.precision == 0) or (right.precision == 0):
		return 0
	varianceSum = left.variance + right.variance
	meanDifference = left.mean - right.mean
	logSqrt2Pi = log(sqrt(2*pi))
	return -1*logSqrt2Pi - (log(varianceSum)/2.0) - ((meanDifference**2)/(2.0*varianceSum))

def at(x, mean = 0, standardDeviation = 1):
	"""calculates the value at x of a normalized Gaussian"""
	multiplier = 1.0/(standardDeviation*sqrt(2*pi))
	expPart = e**((-1.0*((x - mean)**2))/(2*(standardDeviation**2)))
	return multiplier*expPart

def cumulativeTo(x):
	invsqrt2 = -0.707106781186547524400844362104
	result = errorFunctionCumulativeTo(invsqrt2*x)
	return 0.5*result

def errorFunctionCumulativeTo(x):
	z = abs(x)
	t = 2.0/(2.0 + z)
	ty = 4*t - 2
	coefficients = [-1.3026537197817094, 6.4196979235649026e-1, 1.9476473204185836e-2, -9.561514786808631e-3, -9.46595344482036e-4, 3.66839497852761e-4, 4.2523324806907e-5, -2.0278578112534e-5, -1.624290004647e-6, 1.303655835580e-6, 1.5626441722e-8, -8.5238095915e-8, 6.529054439e-9, 5.059343495e-9, -9.91364156e-10, -2.27365122e-10, 9.6467911e-11, 2.394038e-12, -6.886027e-12, 8.94487e-13, 3.13092e-13, -1.12708e-13, 3.81e-16, 7.106e-15, -1.523e-15,-9.4e-17, 1.21e-16, -2.8e-17]
	d = 0.0
	dd = 0.0
	for j in range(len(coefficients) - 1, 0, -1):
		tmp = d
		d = ty*d - dd + coefficients[j]
		dd = tmp
	ans = t*(e**(-z*z + 0.5*(coefficients[0] + ty*d) - dd))
	return ans if x >= 0 else (2.0 - ans)

def inverseErrorFunctionCumulativeTo(p):
	if p >= 2.0:
		return -100
	elif p <= 0.0:
		return 100
	pp = p if p < 1.0 else 2 - p
	t = sqrt(-2*log(pp/2.0))
	x = -0.70711*((2.30753 + t*0.27061)/(1.0 + t*(0.99229 + t*0.04481)) - t)
	for j in range(0, 2):
		err = errorFunctionCumulativeTo(x) - pp
		x = x + err / (1.12837916709551257 * e**(-(x**2)) - x * err)
	return x if p < 1.0 else -1.0*x

def inverseCumulativeTo(x, mean = 0, standardDeviation = 1):
	return mean - sqrt(2)*standardDeviation*inverseErrorFunctionCumulativeTo(2*x)

class GaussianDistribution(object):
	'''
	An immutable representation of the Gaussian distribution of one variable. Not normalized:
	   	   1	 -(x)^2 / (2*sigma^2)
	p(x) =  -------*e
		sqrt(2*pi)
	
	Normalized:
		   1	 -(x-mu)^2 / (2*sigma^2)
	p(x) =  -------*e
		sqrt(2*pi)
	'''
	@property
	def mean(self):
		"""The peak of the Gaussian, mu"""
		return self._mean

	@property
	def standardDeviation(self):
		""" The width of the Gaussian, sigma, where the height drops to max/e"""
		return self._standardDeviation

	@property
	def variance(self):
		""" The square root of the standard devaition, sigma^2 """
		return self._variance

	@property
	def precision(self):
		"""1/sigma^2"""
		return self._precision

	@property
	def precisionMean(self):
		"""mu/sigma^2"""
		return self._precisionMean

	def getNormalizationContant(self):
		"""The normalization contant multiplies the exponential and causes the integral over (-Inf, Inf) to equal 1"""
		return 1.0/(sqrt(2*pi)*self._standardDeviation)

	def __init__(self, mean, standardDeviation, variance = None, precision = None, precisionMean = None):
		self._mean = mean
		self._standardDeviation = standardDeviation
		self._variance = (variance if variance is not None else standardDeviation**2.0)
		self._precision = (precision if precision is not None else 1.0/(standardDeviation**2.0))
		self._precisionMean = (precisionMean if precisionMean is not None else mean/(standardDeviation**2.0))

	def mult(self, gaussian):
		return fromPrecisionMean(self._precisionMean + gaussian.precisionMean, self._precision + gaussian.precision)

	def divide(self, gaussian):
		return fromPrecisionMean(self._precisionMean - gaussian.precisionMean, self._precision - gaussian.precision)
		

class GaussianDistributionTest(unittest.TestCase):
	__errorTolerance = .000001	

	def test_cumulativeToTests(self):
		desired = 0.691462
		actual = cumulativeTo(0.5)
		self.assertAlmostEqual(first=desired, second=actual, delta=self.__errorTolerance)

	def test_atTests(self):
		desired = 0.352065
		actual = at(0.5)
		self.assertAlmostEqual(first=desired, second=actual, delta=self.__errorTolerance)

	def test_multiplicationTests(self):
		standardNormal = GaussianDistribution(0, 1)
		shiftedGaussian = GaussianDistribution(2, 3)
		product = standardNormal.mult(shiftedGaussian)
		self.assertAlmostEqual(first=0.2, second=product.mean, delta=self.__errorTolerance)
		self.assertAlmostEqual(first=(3.0/sqrt(10)), second=product.standardDeviation, delta=self.__errorTolerance)
		m4s5 = GaussianDistribution(4, 5)
		m6s7 = GaussianDistribution(6, 7)
		product2 = m4s5.mult(m6s7)
		expectedMean = (4.0*(7**2)+6*(5**2)) / ((5**2) + (7**2))
		self.assertAlmostEqual(first=expectedMean, second=product2.mean, delta=self.__errorTolerance)
		expectedSigma = sqrt(((5**2)*(7.0**2))/((5**2)+(7**2)))
		self.assertAlmostEqual(first=expectedSigma, second=product2.standardDeviation, delta=self.__errorTolerance)

	def test_divisionTests(self):
		product = GaussianDistribution(0.2, 3.0 / sqrt(10))
		standardNormal = GaussianDistribution(0, 1)
		productDividedByStandardNormal = product.divide(standardNormal)
		self.assertAlmostEqual(2.0, productDividedByStandardNormal.mean, delta=self.__errorTolerance)
		self.assertAlmostEqual(3.0, productDividedByStandardNormal.standardDeviation, delta=self.__errorTolerance)
		product2 = GaussianDistribution((4.0*(7**2)+6*(5**2))/((5**2)+(7**2)), sqrt(((5.0**2)*(7**2))/((5**2)+(7**2))))
		m4s5 = GaussianDistribution(4, 5)
		product2DividedByM4S5 = product2.divide(m4s5)
		self.assertAlmostEqual(first=6.0, second=product2DividedByM4S5.mean, delta=self.__errorTolerance)
		self.assertAlmostEqual(first=7.0, second=product2DividedByM4S5.standardDeviation, delta=self.__errorTolerance)

	def test_logProductNormalizationTests(self):
		standardNormal = GaussianDistribution(0, 1)
		lpn = logProductNormalization(standardNormal, standardNormal)
		self.assertAlmostEqual(-1.2655121234846454, lpn, delta=self.__errorTolerance)
		m1s2 = GaussianDistribution(1, 2)
		m3s4 = GaussianDistribution(3, 4)
		lpn2 = logProductNormalization(m1s2, m3s4)
		self.assertAlmostEqual(-2.5168046699816684, lpn2, delta=self.__errorTolerance)

	def test_logRatioNormalizationTests(self):
		m1s2 = GaussianDistribution(1, 2)
		m3s4 = GaussianDistribution(3, 4)
		lrn = logRatioNormalization(m1s2, m3s4)
		self.assertAlmostEqual(first=2.6157405972171204, second=lrn, delta=self.__errorTolerance)

	def test_absoluteDifferenceTests(self):
		standardNormal = GaussianDistribution(0, 1)
		absDiff = absoluteDifference(standardNormal, standardNormal)
		self.assertAlmostEqual(first=0.0, second=absDiff, delta=self.__errorTolerance)
		m1s2 = GaussianDistribution(1, 2)
		m3s4 = GaussianDistribution(3, 4)
		absDiff2 = absoluteDifference(m1s2, m3s4)
		self.assertAlmostEqual(first=0.4330127018922193, second=absDiff2, delta=self.__errorTolerance)

if __name__ == "__main__":
	unittest.main()
