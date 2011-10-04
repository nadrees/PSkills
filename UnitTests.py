from numerics import GaussianDistribution, logRatioNormalization, absoluteDifference, at, cumulativeTo, logProductNormalization, Matrix, _SquareMatrix, _IdentityMatrix
from objects import sortByRank
from math import sqrt
import unittest

class SortByRankTests(unittest.TestCase):
	def test_sortAlreadySortedTest(self):
		people = ['one', 'two', 'three']
		ranks = [1, 2, 3]
		people = sortByRank(people, ranks)
		self.assertEqual(people, ['one', 'two', 'three'])

	def test_sortUnsortedTest(self):
		people = ['five', 'two1', 'two2', 'one', 'four']
		ranks = [5, 2, 2, 1, 4]
		people = sortByRank(people, ranks)
		self.assertEqual(people, ['one', 'two1', 'two2', 'four', 'five'])

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
