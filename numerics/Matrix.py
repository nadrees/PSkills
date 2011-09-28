from math import sqrt
from math import floor
import unittest

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
			rows = self._rows
			columns = self._cols
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

class MatrixTests(unittest.TestCase):
	def test_twoByTwoDeterminantTests(self):
		a = _SquareMatrix([1, 2, 3, 4])
		self.assertEqual(-2, a.determinant)
		b = _SquareMatrix([3, 4, 5, 6])
		self.assertEqual(-2, b.determinant)
		c = _SquareMatrix([1, 1, 1, 1])
		self.assertEqual(0, c.determinant)
		d = _SquareMatrix([12, 15, 17, 21])
		self.assertEqual(12 * 21 - 15 * 17, d.determinant)

	def test_ThreeByThreeDeterminantTests(self):
		a = _SquareMatrix([1, 2, 3, 4, 5, 6, 7, 8, 9])
		self.assertEqual(0, a.determinant)
		b = _SquareMatrix([3, 1, 4, 1, 5, 9, 2, 6, 5])
		self.assertEqual(-90, b.determinant)

	def test_FourByFourDeterminantTests(self):
		a = _SquareMatrix([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16])
		self.assertEqual(0, a.determinant)
		b = _SquareMatrix([3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5, 8, 9, 7, 9, 3])
		self.assertEqual(98, b.determinant)

	def test_EightByEightDeterminantTests(self):
		a = _SquareMatrix([1, 2,  3,  4,  5,  6,  7,  8,
                                   9, 10, 11, 12, 13, 14, 15, 16,
                                   17, 18, 19, 20, 21, 22, 23, 24, 
                                   25, 26, 27, 28, 29, 30, 31, 32,
                                   33, 34, 35, 36, 37, 38, 39, 40,
                                   41, 42, 32, 44, 45, 46, 47, 48,
                                   49, 50, 51, 52, 53, 54, 55, 56,
                                   57, 58, 59, 60, 61, 62, 63, 64])
		self.assertEqual(0, a.determinant)
		b = _SquareMatrix([3, 1, 4, 1, 5, 9, 2, 6, 
                                   5, 3, 5, 8, 9, 7, 9, 3,
                                   2, 3, 8, 4, 6, 2, 6, 4, 
                                   3, 3, 8, 3, 2, 7, 9, 5,
                                   0, 2, 8, 8, 4, 1, 9, 7,
                                   1, 6, 9, 3, 9, 9, 3, 7,
                                   5, 1, 0, 5, 8, 2, 0, 9, 
                                   7, 4, 9, 4, 4, 5, 9, 2])
		self.assertEqual(1378143, b.determinant)

	def test_EqualTests(self):
		a = _SquareMatrix([1, 2, 3, 4])
		b = _SquareMatrix([1, 2, 3, 4])
		self.assertTrue(a == b)
		self.assertEqual(a, b)
		c = Matrix([[1, 2, 3], [4, 5, 6]])
		d = Matrix([[1, 2, 3], [4, 5, 6]])
		self.assertTrue(c == d)
		self.assertEqual(c, d)
		e = Matrix([[1, 4], [2, 5], [3, 6]])
		f = e.transpose
		self.assertTrue(d == f)
		self.assertEqual(d, f)
		# rounding test
		g = _SquareMatrix([1, 2.0000000000000001, 3, 4])
		h = _SquareMatrix([1, 2, 3, 4])
		self.assertTrue(g == h)
		self.assertEqual(g, h)

	def test_adjugateTests(self):
		a = _SquareMatrix([1, 2, 3, 4])
		b = _SquareMatrix([4, -2, -3, 1])
		self.assertEqual(b, a.adjugate)
		c = _SquareMatrix([-3, 2, -5, -1, 0, -2, 3, -4, 1])
		d = _SquareMatrix([-8, 18, -4, -5, 12, -1, 4, -6, 2])
		self.assertEqual(d, c.adjugate)

	def test_inverseTests(self):
		a = _SquareMatrix([4, 3, 3, 2])
		b = _SquareMatrix([-2, 3, 3, -4])
		aInverse = a.inverse
		self.assertEqual(b, aInverse)
		identity2x2 = _IdentityMatrix(2)
		aaInverse = a*aInverse
		self.assertTrue(identity2x2 == aaInverse)
		c = _SquareMatrix([1, 2, 3, 0, 4, 5, 1, 0, 6])
		cInverse = c.inverse
		d = _SquareMatrix([24, -12, -2, 5, 3, -5, -4, 2, 4])*(1.0/22)
		self.assertTrue(d == cInverse)
		identity3x3 = _IdentityMatrix(3)
		ccInverse = c*cInverse
		self.assertTrue(identity3x3 == ccInverse)

if __name__ == "__main__":
	unittest.main()	
