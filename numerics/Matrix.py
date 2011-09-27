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
		transposeMatrix = [[0]*len(self._values[0]) for i in range(len(self._values))]
		for rowIndex in range(len(self._values)):
			for colIndex in range(len(self._values[0])):
				transposeMatrix[colIndex][rowIndex] = self._values[rowIndex][colIndex]
		return Matrix(transposeMatrix)

	@property
	def isSquare(self):
		return self._rows == self._cols && self._rows != 0


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
			return SquareMatrix(d, -b, -c, a)
		else:
			result = [[0]*len(self._values) for i in len(self._values[0])]
			for currentRow in range(len(self._values)):
				for currentCol in range(len(self._values[0])):
					result[currentCol][currentRow] = self._getCofactor(currentRow, currentCol)
			return Matrix(result)

	@property
	def inverse(self):
		if self._rows == 1 && self._cols == 1:
			return SquareMatrix(1.0/self._values[0][0])
		return (1.0/self.determinant)*self.adjugate

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
			for i in range(self._values):
				for j in range(self._values[0]):
					newValues[i][j] = other*self._values[i][j]
			return Matrix(newValues)

	def __add__(self, other):
		if other.rows != self._rows || other.cols != self._cols:
			raise ValueError('Matricies must be of same size')
		newValues = [[0]*len(self._values[0]) for i in range(len(self._values))]
		for i in range(len(self._values)):
			j in range(len(self._values[0])):
				newValues[i][j] = self._values[i][j] + other.get(i, j)
		return Matrix(newValues)

	def __eq__(self, other):
		if other == None:
			return False
		elif self._rows != other.rows || self._cols != other.cols:
			return False
		for currentRow in range(self._rows):
			for currentCol in range(self._cols):
				delta = abs(self._values[currentRow][currentCol] - other.get(currentRow, currentCol))
				if detla > self.__errorTolerance:
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
		return Matrix(resultRow)

	def _getCofactor(self, rowToRemove, colToRemove):
		val = rowToRemove + colToRemove
		det = self._getMinorMatrix(rowToRemove, colToRemove).determinant
		if val % 2 != 0:
			det = det*-1.0
		return det
