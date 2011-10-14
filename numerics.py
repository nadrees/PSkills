from math import sqrt, pi, log, e
import sys

_intMinValue = -sys.maxint - 1

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

def mean(items):
	return sum(items)/len(items)

def fromRating(rating):
	return GaussianDistribution(rating.mean, rating.standardDeviation)

def fromGaussianDistribution(distribution):
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
	return numerator / denominator

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

	def __mul__(self, gaussian):
		return fromPrecisionMean(self._precisionMean + gaussian.precisionMean, self._precision + gaussian.precision)

	def __div__(self, gaussian):
		return fromPrecisionMean(self._precisionMean - gaussian.precisionMean, self._precision - gaussian.precision)

class Matrix(object):
	__errorTolerance = 0.0000000001
	
	@property
	def rows(self):
		return self._rows

	@property
	def cols(self):
		return self._cols

	def __init__(self, matrixValues):
		'''Constructs a new matrix. Matrix values must be a list of lists, and each inner list must be of the same size'''
		values=list()
		lastRowLength = None
		for row in matrixValues:
			if lastRowLength is not None and len(row) != lastRowLength:
				raise ValueError('All rows must be the same length')
			lastRowLength = len(row)
			rowValues = list()
			for value in row:
				rowValues.append(value)
			values.append(rowValues)
		self._rows = len(matrixValues)
		self._cols = len(matrixValues[0])
		self._values = values

	def get(self, row, col):
		return self._values[row][col]

	@property
	def transpose(self):
		'''The transpose of this matrix'''
		transposeMatrix = [[0]*len(self._values) for i in range(len(self._values[0]))]
		for rowIndex in range(len(self._values)):
			for colIndex in range(len(self._values[0])):
				transposeMatrix[colIndex][rowIndex] = self._values[rowIndex][colIndex]
		return Matrix(transposeMatrix)

	@property
	def isSquare(self):
		return self._rows == self._cols and self._rows != 0


	@property
	def determinant(self):
		if self.isSquare == False:
			raise AttributeError('The matrix is not square')
		elif self._rows == 1:
			return self._values[0][0]
		elif self._rows == 2:
			a = self._values[0][0]
			b = self._values[0][1]
			c = self._values[1][0]
			d = self._values[1][1]
			return a*d-b*c
		else:
			result = 0.0
			for i in range(len(self._values[0])):
				firstRowColValue = self._values[0][i]
				cofactor = self._getCofactor(0, i)
				itemToAdd = firstRowColValue*cofactor
				result = result + itemToAdd
			return result

	@property
	def adjugate(self):
		if self.isSquare == False:
			raise AttributeError('The matrix is not square')
		elif self._rows == 2:
			a = self._values[0][0]
			b = self._values[0][1]
			c = self._values[1][0]
			d = self._values[1][1]
			return _SquareMatrix([d, -b, -c, a])
		else:
			result = [[0]*len(self._values) for i in range(len(self._values[0]))]
			for currentRow in range(len(self._values)):
				for currentCol in range(len(self._values[0])):
					result[currentCol][currentRow] = self._getCofactor(currentRow, currentCol)
			return Matrix(result)

	@property
	def inverse(self):
		if self._rows == 1 and self._cols == 1:
			return _SquareMatrix([1.0/self._values[0][0]])
		return self.adjugate*(1.0/self.determinant)

	def __mul__(self, other):
		if isinstance(other, Matrix):
			if self._cols != other.rows:
				raise AttributeError('The width of the left matrix must match the height of the right matrix')
			resultRows = self._rows
			resultCols = other.cols
			resultValues = [[0]*resultCols for i in range(resultRows)]
			for currentRow in range(resultRows):
				for currentColumn in range(resultCols):
					productValue = 0
					for vectorIndex in range(self._cols):
						leftValue = self._values[currentRow][vectorIndex]
						rightValue = other.get(vectorIndex, currentColumn)
						productValue = productValue + (leftValue * rightValue)
					resultValues[currentRow][currentColumn] = productValue
			return Matrix(resultValues)
		else:
			newValues = [[0]*len(self._values[0]) for i in range(len(self._values))]
			for i in range(len(self._values)):
				for j in range(len(self._values[0])):
					newValues[i][j] = other*self._values[i][j]
			return Matrix(newValues)

	def __add__(self, other):
		if other.rows != self._rows or other.cols != self._cols:
			raise ValueError('Matricies must be of same size')
		newValues = [[0]*len(self._values[0]) for i in range(len(self._values))]
		for i in range(len(self._values)):
			for j in range(len(self._values[0])):
				newValues[i][j] = self._values[i][j] + other.get(i, j)
		return Matrix(newValues)

	def __eq__(self, other):
		if other == None:
			return False
		elif self._rows != other.rows or self._cols != other.cols:
			return False
		for currentRow in range(self._rows):
			for currentCol in range(self._cols):
				delta = abs(self._values[currentRow][currentCol] - other.get(currentRow, currentCol))
				if delta > self.__errorTolerance:
					return False
		return True

	def __ne__(self, other):
		return (self == other) == False

	def _getMinorMatrix(self, rowToRemove, columnToRemove):
		result = [[0]*(self._cols - 1) for i in range(self._rows - 1)]
		resultRow = 0
		for currentRow in range(self._rows):
			if currentRow == rowToRemove:
				continue
			resultColumn = 0
			for currentColumn in range(self._cols):
				if currentColumn == columnToRemove:
					continue
				result[resultRow][resultColumn] = self._values[currentRow][currentColumn]
				resultColumn = resultColumn + 1
			resultRow = resultRow + 1
		return Matrix(result)

	def _getCofactor(self, rowToRemove, colToRemove):
		val = rowToRemove + colToRemove
		det = self._getMinorMatrix(rowToRemove, colToRemove).determinant
		if val % 2 != 0:
			det = det*-1.0
		return det

class _DiagonalMatrix(Matrix):
	'''A matrix with values on the diagonal, and 0 everywhere else'''
	def __init__(self, diagonalValues):
		'''Creates a diagonal matrix from the list diagnoal values'''
		self._rows = len(diagonalValues)
		self._cols = self._rows
		self._values = [[0]*self._cols for i in range(self._rows)]
		for i in range(self._rows):
			self._values[i][i] = diagonalValues[i]

class _IdentityMatrix(_DiagonalMatrix):
	'''The identity matrix'''
	def __init__(self, numRows):
		'''Creates an identity matrix with the number of rows specified'''
		values = [1]*numRows
		super(_IdentityMatrix, self).__init__(values)

class _Vector(Matrix):
	'''A matrix with only 1 row'''
	def __init__(self, values):
		'''Creates a matrix with the values in the list values in one row'''
		super(_Vector, self).__init__(values)

class _SquareMatrix(Matrix):
	'''A matrix where the number of rows equals the number of columns'''
	def __init__(self, allValues):
		'''Creates a square matrix from the list allValues'''
		self._rows = int(sqrt(len(allValues)))
		self._cols = self._rows
		allValuesIndex = 0
		values = [[0]*self._cols for i in range(self._rows)]
		for currentRow in range(self._rows):
			for currentCol in range(self._cols):
				values[currentRow][currentCol] = allValues[allValuesIndex]
				allValuesIndex += 1
		self._values = values

class Range(object):
	'''
	An immutable range of Integers, including endpoints. Ranges are not empty.
	'''
	def __init__(self, minimum = None, maximum = None):
		if (maximum is None and minimum is None):
			raise ValueError('Empty ranges are disallowed')
		if (maximum is not None and minimum is not None and minimum > maximum):
			raise ValueError('Min was greater than max')
		self._minimum = minimum
		self._maximum = maximum
	
	def isInRange(self, value):
		return (self._minimum is None or self._minimum <= value) and (self._maximum is None or self._maximum >= value)

	@property
	def minimum(self):
		"""The minimum value for this range"""
		return self._minimum

	@property
	def maximum(self):
		"""The maximum value for this range"""
		return self._maximum

class PlayersRange(Range):
	def __init__(self, minimum = _intMinValue, maximum = _intMinValue):
		super(Range, self).__init__(minimum, maximum)

class TeamsRange(Range):
	def __init__(self, minimum = _intMinValue, maximum = _intMinValue):
		super(Range, self).__init__(minimum, maximum)

def inclusive(minimum, maximum):
	return Range(minimum, maximum)

def exactly(value):
	return Range(value, value)

def atLeast(minimum):
	return Range(minimum)

def atMost(maximum):
	return Range(maximum=maximum)
