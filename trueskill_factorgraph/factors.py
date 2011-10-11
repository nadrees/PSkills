from factorgraphs import Factor, Message
from numerics import logProductNormalization, fromPrecisionMean, cumulativeTo, logRatioNormalization, GaussianDistribution
from math import log, sqrt
from trueskill_simple import wExceedsMargin, vExceedsMargin
from copy import deepcopy

class GaussianFactor(Factor):
	def sendMessage(self, message, variable):
		marginal = variable.value
		messageValue = message.value
		logZ = logProductNormalization(marginal, messageValue)
		variable.value = marginal*messageValue
		return logZ
		
	def createVariableToMessageBinding(variable):
		message = Message(fromPrecisionMean(0, 0), "message from %s to %s" % (self, variable))
		return self._createVariableToMessageBindingInternal(variable, message)
		
class GaussianGreaterThanFactor(GaussianFactor):
	'''Factor representing a team difference that has exceeded the draw margin'''
	def __init__(self, epsilon, variable):
		super(GaussianGreaterThanFactor, self).__init__("%s > %f" % (variable, epsilon))
		self._epsilon = epsilon
		self.createVariableToMessageBinding(variable)
		
	@property
	def logNormalization(self):
		marginal = self._variables[0].value
		message = self._messages[0].value
		messageFromVariable = marginal/message
		return -1.0*logProductNormalization(messageFromVariable, message) + log(cumulativeTo((messageFromVariable.mean - self._epsilon) / messageFromVariable.standardDeviation))
		
	def _updateMessageInternal(self, message, variable):
		oldMarginal = deepcopy(variable.value)
		oldMessage = deepcopy(message.value)
		messageFromVar = oldMarginal/oldMessage
		
		c = messageFromVar.precision
		d = messageFromVar.precisionMean
		sqrtC = sqrt(c)
		dOnSqrtC = d/sqrtC
		epsilonTimesSqrtC = self._epsilon*sqrtC
		
		denom = 1.0 - wExceedsMargin(dOnSqrtC, epsilonTimesSqrtC)
		
		newPrecision = c/denom
		newPrecisionMean = (d + sqrtC*vExceedsMarin(dOnSqrtC, epsilonTimesSqrtC))/denom
		
		newMarginal = fromPrecisionMean(newPrecisionMean, newPrecision)
		newMessage = oldMessage*newMarginal/oldMarginal
		
		message.value = newMessage
		variable.value = newMarginal
		
		return newMarginal - oldMarginal
		
class GaussianLikelihoodFactor(GaussianFactor):
	'''Connects tow variables and adds uncertainty'''
	def __init__(self, betaSquared, variable1, variable2):
		super(GaussianLikelihoodFactor, self).__init__("Likelihood of %s going to %s" % (variable1, variable2))
		self._precision = 1.0/betaSquared
		self.createVariableToMessageBinding(variable1)
		self.createVariableToMessageBinding(variable2)
		
	@property
	def logNormalization(self):
		return logRatioNormalization(self._variables[0].value, self._messages[0].value)
		
	def updateMessage(self, messageIndex):
		if messageIndex == 0:
			return self._updateHelper(self._messages[0], self._messages[1], self._variables[0], self._variables[1])
		elif messageIndex == 1:
			return self._updateHelper(self._messages[1], self._messages[0], self._variables[1], self._varaibles[0])
		else:
			raise IndexError()	
			
	def _updateHelper(self, message1, message2, variable1, variable2):
		message1Value = deepcopy(message1.value)
		message2Value = deepcopy(message2.value)
		
		marginal1 = deepcopy(variable1.value)
		marginal2 = deepcopy(variable2.value)
		
		a = self._precision/(self._precision + marginal2.precision - message2Value.precision)
		newMessage = fromPrecisionMean(a * (marginal2.precisionMean - message2Value.precisionMean), a*(marignal2.precision - message2Value.precision))
		
		oldMarginalWithoutMessage = marginal1/message1Value
		newMarginal = oldMariginalWithoutMessage*newMessage
		
		message1.value = newMessage
		variable1.value = newMarginal
		
		return newMarginal - marginal1
		
class GaussianPriorFactor(GaussianFactor):
	'''Supplies the factor graph with prior information'''
	def __init__(self, mean, variance, varible):
		super(GaussianPriorFactor, self).__init__("Prior value going to %s" % variable)
		self._newMessage = GaussianDistribution(mean, sqrt(variance))
		self.createVariableToMessageBinding(variable)
		
	def _updateMessageInternal(self, message, variable):
		oldMarginal = deepcopy(variable.value)
		oldMessage = message
		newMarginal = fromPrecisionMean(oldMarginal.precisionMean + self._newMessage.precisionMean - oldMessage.value.precisionMean, oldMarginal.precision + self._newMessage.precision - oldMessage.value.precision)
		variable.value = newMarginal
		message.value = self._newMessage
		return oldMarginal - newMarginal
		
class GaussianWeightedSumFactor(GaussianFactor):
	'''Factor that sums together multiple Gaussians'''
	def __init__(self, sumVariable, variablesToSum, variableWeights = None):
		name = self._createName(sumVariable, variablesToSum, varaiableWeights)
		super(GaussianWeightedSumFactor, self).__init__(name)
		self._weights = [list() for i in range(len(variableWeights) + 1)]
		self._weightsSquared = [list() for i in range(len(self._weights))]
		self._variableIndexOrdersForWeights = list()
		
		# the first weights are a straightforward copy
		# v_0 = a_1 * v_1 + a_2 * v_2 + ... + a_n * v_n
		for variableWeight in variableWeights:
			self._weights[0].append(variableWeight)
			self._weightsSquared[0].append(variableWeight**2)
		
		# 0..n-1
		temp = [i for i in range(len(variablesToSum))]
		self._variableIndexOrdersForWeights.append(temp)
		
		# the rest move the variables around and divide out the constant
		# for example:
		# v_1 = (-a_2 / a_1) * v_2 + (-a_3 / a_1) * v_3 + ... + (1.0 / a_1) * v_0
		# by convention, we'll put the v_0 term at the end
		for weightsIndex in range(1, len(self._weights)):
			currentWeights = [0]*len(variableWeights)
			self._weights[weightsIndex] = currentWeights
			
			variableIndices = [0]*(len(variableWeights) + 1)
			variableIndicies[0] = weightsIndex
			
			currentWeightsSquared = [0]*len(variableWeights)
			self._weightsSquared[weightsIndex] = currentWeightsSquared
			
			currentDestinationWeightIndex = 0
			for currentWeightSourceIndex in range(len(variableWeights)):
				if currentWeightSourceIndex == weightsIndex - 1:
					continue
				currentWeight = 0.0
				if variableWeights[weightsIndex - 1] != 0:
					currentWeight = -1.0*variableWeights[currentWeightSourceIndex]/variableWeights[weightsIndex - 1]
				currentWeights[currentDestinationWeightIndex] = currentWeight
				currentWeightsSquared[currentDestinationWeightIndex] = currentWeight**2.0
				variableIndicies[currentDestinationWeightIndex + 1] = currentWeightSourceIndex + 1
				currentDestinationWeightIndex += 1
			
			finalWeight = 0.0
			if variableWeights[weightsIndex - 1] != 0:
				finalWeight = 1.0/variableWeights[weightsIndex - 1]
			currentWeights[currentDestinationWeightIndex] = finalWeight
			currentWeightsSquared[currentDestinationWeightIndex] = finalWeight**2.0
			variableIndicies[len(variableIndicies) - 1] = 0
			self._variableIndexOrdersForWeights.append(variableIndicies)
			
		self.createVariableToMessageBinding(sumVariable)
		for currentVariable in variablesToSum:
			self.createVariableToMessageBinding(currentVariable)
			
	@property
	def logNormalization(self):
		result = 0.0
		for i in range(len(self._variables)):
			result += logRatioNormalization(self._variables[i].value, self._messages[i].value)
		return result
