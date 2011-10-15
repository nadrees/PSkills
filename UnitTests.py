from math import sqrt
from numerics import GaussianDistribution, logRatioNormalization, \
	absoluteDifference, at, cumulativeTo, logProductNormalization, Matrix, \
	_SquareMatrix, _IdentityMatrix
from objects import sortByRank, Player, GameInfo, defaultGameInfo, Team, Rating
from trueskill_factorgraph.ts_factorgraph import FactorGraphTrueSkillCalculator
from trueskill_simple import TwoPlayerTrueSkillCalculator, \
	TwoTeamTrueSkillCalculator, getDrawMarginFromDrawProbability
import unittest

_errorTolerance = 0.085

class TwoPlayerTrueSkillCalculatorTests(unittest.TestCase):
	def setUp(self):
		self.calculator = TwoPlayerTrueSkillCalculator()
		self.gameInfo = defaultGameInfo()
		
	def assertRating(self, expectedMean, expectedStandardDeviation, actual):
		self.assertAlmostEqual(expectedMean, actual.mean, delta = _errorTolerance)
		self.assertAlmostEqual(expectedStandardDeviation, actual.standardDeviation, delta = _errorTolerance)
		
	def assertMatchQuality(self, expectedMatchQuality, actualMatchQuality):
		self.assertAlmostEqual(expectedMatchQuality, actualMatchQuality, delta = 0.0005)
	
	def test_twoPlayerTestDrawn(self):
		player1 = Player(1)
		player2 = Player(2)
		gameInfo = defaultGameInfo()
	
		team1 = Team(player1, gameInfo.defaultRating)
		team2 = Team(player2, gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(gameInfo, teams, [1, 1])
	
		for newRating in newRatings:
			self.assertRating(25.0, 6.4575196623173081, newRating[1])
		self.assertMatchQuality(0.447, self.calculator.calculateMatchQuality(gameInfo, teams))
	
	def test_oneOnOneMassiveUpsetDrawTest(self):
		player1 = Player(1)
		player2 = Player(2)
	
		team1 = Team()
		team1.addPlayer(player1, self.gameInfo.defaultRating)
		team2 = Team()
		team2.addPlayer(player2, Rating(50, 12.5))
		teams = [team1, team2]
	
		newRatingsWinLose = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 1])
	
		for newRating in newRatingsWinLose:
			player = newRating[0]
			if player == player1:
				self.assertRating(31.662, 7.137, newRating[1])
			else:
				self.assertRating(35.010, 7.910, newRating[1])
		self.assertMatchQuality(.110, self.calculator.calculateMatchQuality(self.gameInfo, teams))
	
	def test_twoPlayerTestNotDrawn(self):
		player1 = Player(1)
		player2 = Player(2)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team(player2, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2])
	
		for player, rating in newRatings:
			if player == player1:
				self.assertRating(29.39583201999924, 7.171475587326186, rating)
			else:
				self.assertRating(20.60416798000076, 7.171475587326186, rating)
		self.assertMatchQuality(0.447, self.calculator.calculateMatchQuality(self.gameInfo, teams))
	
	def test_twoPlayerChessTestNotDrawn(self):
		player1 = Player(1)
		player2 = Player(2)
		gameInfo = GameInfo(1200.0, 1200.0 / 3.0, 200.0, 1200.0 / 300.0, 0.03)
	
		team1 = Team(player1, Rating(1301.0007, 42.9232))
		team2 = Team(player2, Rating(1188.7560, 42.5570))
	
		newRatings = self.calculator.calculateNewRatings(gameInfo, [team1, team2], [1, 2])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(1304.7820836053318, 42.843513887848658, newRating[1])
			else:
				self.assertRating(1185.0383099003536, 42.485604606897752, newRating[1])
	
class TwoTeamTrueSkillCalculatorTests(TwoPlayerTrueSkillCalculatorTests):
	def setUp(self):
		self.calculator = TwoTeamTrueSkillCalculator()
		self.gameInfo = defaultGameInfo()
	
	def test_oneOnTwoSomewhatBalanced(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
	
		team1 = Team(player1, Rating(40, 6))
		team2 = Team(player2, Rating(20, 7))
		team2.addPlayer(player3, Rating(25, 8))
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(42.744, 5.602, newRating[1])
			elif player == player2:
				self.assertRating(16.266, 6.359, newRating[1])
			else:
				self.assertRating(20.123, 7.028, newRating[1])
		self.assertMatchQuality(0.478, self.calculator.calculateMatchQuality(self.gameInfo, teams))
		
	def test_oneOnTwoSimple(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team()
		team2.addPlayer(player2, self.gameInfo.defaultRating)
		team2.addPlayer(player3, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(33.730, 7.317, newRating[1])
			elif player == player2:
				self.assertRating(16.270, 7.317, newRating[1])
			else:
				self.assertRating(16.270, 7.317, newRating[1])
		self.assertMatchQuality(0.135, self.calculator.calculateMatchQuality(self.gameInfo, teams))

	def test_oneOnTwoDrawTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team(player2, self.gameInfo.defaultRating)
		team2.addPlayer(player3, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 1])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(31.660, 7.138, newRating[1])
			elif player == player2:
				self.assertRating(18.340, 7.138, newRating[1])
			else:
				self.assertRating(18.340, 7.138, newRating[1])
		self.assertMatchQuality(0.135, self.calculator.calculateMatchQuality(self.gameInfo, teams))
	
	def test_oneOnThreeSimpleTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team(player2, self.gameInfo.defaultRating)
		team2.addPlayer(player3, self.gameInfo.defaultRating)
		team2.addPlayer(player4, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(36.337, 7.527, newRating[1])
			else:
				self.assertRating(13.663, 7.527, newRating[1])
		self.assertMatchQuality(0.012, self.calculator.calculateMatchQuality(self.gameInfo, teams))

		
	def test_oneOnThreeDrawTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team(player2, self.gameInfo.defaultRating)
		team2.addPlayer(player3, self.gameInfo.defaultRating)
		team2.addPlayer(player4, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		newRatings = self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 1])
	
		for newRating in newRatings:
			player = newRating[0]
			if player == player1:
				self.assertRating(34.990, 7.455, newRating[1])
			else:
				self.assertRating(15.010, 7.455, newRating[1])
		self.assertMatchQuality(0.012, self.calculator.calculateMatchQuality(self.gameInfo, teams))
		
	def test_oneOnSevenSimpleTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
		player5 = Player(5)
		player6 = Player(6)
		player7 = Player(7)
		player8 = Player(8)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team2 = Team(player2, self.gameInfo.defaultRating)
		team2.addPlayer(player3, self.gameInfo.defaultRating)
		team2.addPlayer(player4, self.gameInfo.defaultRating)
		team2.addPlayer(player5, self.gameInfo.defaultRating)
		team2.addPlayer(player6, self.gameInfo.defaultRating)
		team2.addPlayer(player7, self.gameInfo.defaultRating)
		team2.addPlayer(player8, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		for newRating in self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2]):
			player = newRating[0]
			if player == player1:
				self.assertRating(40.582, 7.917, newRating[1])
			else:
				self.assertRating(9.418, 7.917, newRating[1])
		self.assertMatchQuality(0.000, self.calculator.calculateMatchQuality(self.gameInfo, teams))
		
	def test_twoOnTwoSimpleTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team1.addPlayer(player2, self.gameInfo.defaultRating)
		team2 = Team(player3, self.gameInfo.defaultRating)
		team2.addPlayer(player4, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		for newRating in self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2]):
			player = newRating[0]
			if player == player1 or player == player2:
				self.assertRating(28.108, 7.774, newRating[1])
			else:
				self.assertRating(21.892, 7.774, newRating[1])
		self.assertMatchQuality(0.447, self.calculator.calculateMatchQuality(self.gameInfo, teams))

	def test_twoOnTwoUnbalancedDrawTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
	
		team1 = Team(player1, Rating(15, 8))
		team1.addPlayer(player2, Rating(20, 6))
		team2 = Team(player3, Rating(25, 4))
		team2.addPlayer(player4, Rating(30, 3))
		teams = [team1, team2]
	
		for newRating in self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 1]):
			player = newRating[0]
			if player == player1:
				self.assertRating(21.570, 6.556, newRating[1])
			elif player == player2:
				self.assertRating(23.696, 5.418, newRating[1])
			elif player == player3:
				self.assertRating(23.357, 3.833, newRating[1])
			else:
				self.assertRating(29.075, 2.931, newRating[1])
		self.assertMatchQuality(0.214, self.calculator.calculateMatchQuality(self.gameInfo, teams))

	def test_twoOnTwoDrawTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
	
		team1 = Team(player1, self.gameInfo.defaultRating)
		team1.addPlayer(player2, self.gameInfo.defaultRating)
		team2 = Team(player3, self.gameInfo.defaultRating)
		team2.addPlayer(player4, self.gameInfo.defaultRating)
		teams = [team1, team2]
	
		for newRating in self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 1]):
			self.assertRating(25, 7.455, newRating[1])
		self.assertMatchQuality(0.447, self.calculator.calculateMatchQuality(self.gameInfo, teams))
		
	def test_twoOnTwoUpsetTest(self):
		player1 = Player(1)
		player2 = Player(2)
		player3 = Player(3)
		player4 = Player(4)
	
		team1 = Team(player1, Rating(20, 8)).addPlayer(player2, Rating(25, 6))
		team2 = Team(player3, Rating(35, 7)).addPlayer(player4, Rating(40, 5))
		teams = [team1, team2]
	
		for newRating in self.calculator.calculateNewRatings(self.gameInfo, teams, [1, 2]):
			player = newRating[0]
			if player == player1:
				self.assertRating(29.698, 7.008, newRating[1])
			elif player == player2:
				self.assertRating(30.455, 5.594, newRating[1])
			elif player == player3:
				self.assertRating(27.575, 6.346, newRating[1])
			else:
				self.assertRating(36.211, 4.768, newRating[1])
		self.assertMatchQuality(0.084, self.calculator.calculateMatchQuality(self.gameInfo, teams))
		
class FactorGraphTrueSkillCalculatorTests(TwoTeamTrueSkillCalculatorTests):
	def setUp(self):
		self.calculator = FactorGraphTrueSkillCalculator()
		self.gameInfo = defaultGameInfo()

class DrawMarginTests(unittest.TestCase):
	_errorTolerance = 0.000001
	
	def test_getDrawMarginFromDrawProbabilityTest(self):
		beta = 25.0 / 6.0
		self.assertDrawMargin(0.10, beta, 0.74046637542690541)
		self.assertDrawMargin(0.25, beta, 1.87760059883033)
		self.assertDrawMargin(0.33, beta, 2.5111010132487492)
		
	def assertDrawMargin(self, drawProbability, beta, expected):
		actual = getDrawMarginFromDrawProbability(drawProbability, beta)
		self.assertAlmostEqual(expected, actual, delta = self._errorTolerance)

class SortByRankTests(unittest.TestCase):
	def test_sortAlreadySortedTest(self):
		people = ['one', 'two', 'three']
		ranks = [1, 2, 3]
		people = sortByRank(people, ranks)
		self.assertEqual(people, (['one', 'two', 'three'], [1, 2, 3]))

	def test_sortUnsortedTest(self):
		people = ['five', 'two1', 'two2', 'one', 'four']
		ranks = [5, 2, 2, 1, 4]
		people = sortByRank(people, ranks)
		self.assertEqual(people, (['one', 'two1', 'two2', 'four', 'five'], [1, 2, 2, 4, 5]))

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
		product = standardNormal*shiftedGaussian
		self.assertAlmostEqual(first=0.2, second=product.mean, delta=self.__errorTolerance)
		self.assertAlmostEqual(first=(3.0/sqrt(10)), second=product.standardDeviation, delta=self.__errorTolerance)
		m4s5 = GaussianDistribution(4, 5)
		m6s7 = GaussianDistribution(6, 7)
		product2 = m4s5*m6s7
		expectedMean = (4.0*(7**2)+6*(5**2)) / ((5**2) + (7**2))
		self.assertAlmostEqual(first=expectedMean, second=product2.mean, delta=self.__errorTolerance)
		expectedSigma = sqrt(((5**2)*(7.0**2))/((5**2)+(7**2)))
		self.assertAlmostEqual(first=expectedSigma, second=product2.standardDeviation, delta=self.__errorTolerance)

	def test_divisionTests(self):
		product = GaussianDistribution(0.2, 3.0 / sqrt(10))
		standardNormal = GaussianDistribution(0, 1)
		productDividedByStandardNormal = product/standardNormal
		self.assertAlmostEqual(2.0, productDividedByStandardNormal.mean, delta=self.__errorTolerance)
		self.assertAlmostEqual(3.0, productDividedByStandardNormal.standardDeviation, delta=self.__errorTolerance)
		product2 = GaussianDistribution((4.0*(7**2)+6*(5**2))/((5**2)+(7**2)), sqrt(((5.0**2)*(7**2))/((5**2)+(7**2))))
		m4s5 = GaussianDistribution(4, 5)
		product2DividedByM4S5 = product2/m4s5
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
