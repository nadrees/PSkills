from objects import SkillCalculator, SupportedOptions, argumentNotNone, getPartialPlayPercentage, sortByRank
from numerics import atLeast, _Vector, _DiagonalMatrix, Matrix, fromPrecisionMean
from math import e, sqrt
from layers import TrueSkillFactorGraph

class FactorGraphTrueSkillCalculator(SkillCalculator):
	def __init__(self):
		super(FactorGraphTrueSkillCalculator, self).__init__(SupportedOptions.PARTIAL_PLAY | SupportedOptions.PARTIAL_UPDATE, atLeast(2), atLeast(1))
	
	def calculateNewRatings(self, gameInfo, teams, teamRanks):
		argumentNotNone(gameInfo, "gameInfo")
		self._validateTeamCountAndPlayersCountPerTeam(teams)
		teams, teamRanks = sortByRank(teams, teamRanks)
		
		factorGraph = TrueSkillFactorGraph(gameInfo, teams, teamRanks)
		factorGraph.buildGraph()
		factorGraph.runSchedule()
		return factorGraph.getUpdatedRatings()
		
	def calculateMatchQuality(self, gameInfo, teams):
		skillsMatrix = self._getPlayerCovarianceMatrix(teams)
		meanVector = self._getPlayerMeansVector(teams)
		meanVectorTranspose = meanVector.transpose
		
		playerTeamAssignmentsMatrix = self._createPlayerTeamAssignmentMatrix(teams, meanVector.rows)
		playerTeamAssignmentsMatrixTranspose = playerTeamAssignmentsMatrix.transpose
		
		betaSquared = gameInfo.beta**2.0
		
		start = meanVectorTranspose * playerTeamAssignmentsMatrix
		aTa = (betaSquared * playerTeamAssignmentsMatrixTranspose) * playerTeamAssignmentsMatrix
		aTSA = playerTeamAssigmentsMatrixTranspose * skillsMatrix * playerTeamAssignmentsMatrix
		middle = aTa + aTSA
		
		middleInverse = middle.inverse
		
		end = playerTeamAssignmentsMatrixTranspose * meanVector
		
		expPartMatrix = (start * middleInverse * end) * -0.5
		expPart = expPartMatrix.determinant
		
		sqrtPartNumerator = aTa.determinant
		sqrtPartDenominator = middle.determinant
		sqrtPart = sqrtPartNumerator / sqrtPartDenominator
		
		result = (e**expPart) * sqrt(sqrtPart)
		
		return result
		
	def _getPlayerMeansVector(self, teamAssignmentsList):
		return _Vector(self._getPlayerRatingValues(teamAssigmentsList, lambda rating: rating.mean))
		
	def _getPlayerCovarianceMatrix(self, teamAssignmentList):
		return _DiagonalMatrix(self._getPlayerRatingValues(teamAssigmentsList, lambda rating: rating.standardDeviation**2.0))
		
	def _getPlayerRatingValues(self, teamAssigmentsList, playerRatingFunction):
		playerRatingValues = list()
		for currentTeam in teamAssigmentsList:
			for currentRating in currentTeam.values:
				playerRatingValues.append(playerRatingFunction(currentRating))
		return playerRatingValues
	
	def _createPlayerTeamAssignmentMatrix(self, teamAssigmentsList, totalPlayers):
		playerAssignments = list()
		totalPreviousPlayers = 0
		
		for i in range(leng(teamAssignmentsList)):
			currentTeam = teamAssigmentsList[i]
			currentRowValues = [0] * totalPreviousPlayers
			playerAssignments.append(currentRowValues)
			
			for currentRating in currentTeam:
				currentRowValues.append(getPartialPlayPercentage(currentRating[0]))
				totalPreviousPlayers += 1
				
			nextTeam = teamAssignmentsList[i + 1]
			for nextTeamPlayerPair in nextTeam:
				currentRowValues.append(-1 * getPartialPlayPercentage(nextTeamPlayerPair[0]))
				
		return Matrix(totalPlayers, len(teamAssignmentsList) - 1, playerAssignments)
