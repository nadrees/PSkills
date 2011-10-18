from copy import deepcopy
from factorgraphs import Factor, Message
from math import log, sqrt
from numerics import logProductNormalization, fromPrecisionMean, cumulativeTo, \
	logRatioNormalization, GaussianDistribution, wExceedsMargin, vExceedsMargin, \
	wWithinMargin, vWithinMargin, Decimal

class GaussianFactor(Factor):
	def sendMessage(self, message, variable):
		marginal = variable.value
		messageValue = message.value
		logZ = logProductNormalization(marginal, messageValue)
		variable.value = marginal*messageValue
		return logZ
		
	def createVariableToMessageBinding(self, variable):
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
		newPrecisionMean = (d + sqrtC*vExceedsMargin(dOnSqrtC, epsilonTimesSqrtC))/denom
		
		newMarginal = fromPrecisionMean(newPrecisionMean, newPrecision)
		newMessage = oldMessage*newMarginal/oldMarginal
		
		message.value = newMessage
		variable.value = newMarginal
		
		return newMarginal - oldMarginal
		
class GaussianLikelihoodFactor(GaussianFactor):
	'''Connects two variables and adds uncertainty'''
	def __init__(self, betaSquared, variable1, variable2):
		super(GaussianLikelihoodFactor, self).__init__("Likelihood of %s going to %s" % (variable1, variable2))
		self._precision = Decimal(1.0)/betaSquared
		self.createVariableToMessageBinding(variable1)
		self.createVariableToMessageBinding(variable2)
		
	@property
	def logNormalization(self):
		return logRatioNormalization(self._variables[0].value, self._messages[0].value)
		
	def updateMessage(self, messageIndex):
		if messageIndex == 0:
			return self._updateHelper(self._messages[0], self._messages[1], self._variables[0], self._variables[1])
		elif messageIndex == 1:
			return self._updateHelper(self._messages[1], self._messages[0], self._variables[1], self._variables[0])
		else:
			raise IndexError()	
			
	def _updateHelper(self, message1, message2, variable1, variable2):
		message1Value = deepcopy(message1.value)
		message2Value = deepcopy(message2.value)
		
		marginal1 = deepcopy(variable1.value)
		marginal2 = deepcopy(variable2.value)
		
		a = self._precision/(self._precision + marginal2.precision - message2Value.precision)
		newMessage = fromPrecisionMean(a * (marginal2.precisionMean - message2Value.precisionMean), a*(marginal2.precision - message2Value.precision))
		
		oldMarginalWithoutMessage = marginal1/message1Value
		newMarginal = oldMarginalWithoutMessage*newMessage
		
		message1.value = newMessage
		variable1.value = newMarginal
		
		return newMarginal - marginal1
		
class GaussianPriorFactor(GaussianFactor):
	'''Supplies the factor graph with prior information'''
	def __init__(self, mean, variance, variable):
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
		name = self._createName(sumVariable, variablesToSum, variableWeights)
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
		temp = [i for i in range(len(variablesToSum) + 1)]
		self._variableIndexOrdersForWeights.append(temp)
		
		# the rest move the variables around and divide out the constant
		# for example:
		# v_1 = (-a_2 / a_1) * v_2 + (-a_3 / a_1) * v_3 + ... + (1.0 / a_1) * v_0
		# by convention, we'll put the v_0 term at the end
		for weightsIndex in range(1, len(self._weights)):
			currentWeights = [0]*len(variableWeights)
			self._weights[weightsIndex] = currentWeights
			
			variableIndices = [0]*(len(variableWeights) + 1)
			variableIndices[0] = weightsIndex
			
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
				variableIndices[currentDestinationWeightIndex + 1] = currentWeightSourceIndex + 1
				currentDestinationWeightIndex += 1
			
			finalWeight = 0.0
			if variableWeights[weightsIndex - 1] != 0:
				finalWeight = 1.0/variableWeights[weightsIndex - 1]
			currentWeights[currentDestinationWeightIndex] = finalWeight
			currentWeightsSquared[currentDestinationWeightIndex] = finalWeight**2.0
			variableIndices[len(variableIndices) - 1] = 0
			self._variableIndexOrdersForWeights.append(variableIndices)
			
		self.createVariableToMessageBinding(sumVariable)
		for currentVariable in variablesToSum:
			self.createVariableToMessageBinding(currentVariable)
			
	@property
	def logNormalization(self):
		result = 0.0
		for i in range(len(self._variables)):
			result += logRatioNormalization(self._variables[i].value, self._messages[i].value)
		return result
		
	def _updateHelper(self, weights, weightsSquared, messages, variables):
		message0 = deepcopy(messages[0].value)
		marginal0 = deepcopy(variables[0].value)
		
		inverseOfNewPrecisionSum = Decimal(0.0)
		anotherInverseOfNewPrecisionSum = Decimal(0.0)
		weightedMeanSum = Decimal(0.0)
		anotherWeightedMeanSum = Decimal(0.0)
		
		for i in range(len(weightsSquared)):
			inverseOfNewPrecisionSum += Decimal(weightsSquared[i])/(variables[i + 1].value.precision - messages[i + 1].value.precision)
			diff = (variables[i + 1].value/messages[i + 1].value)
			anotherInverseOfNewPrecisionSum += Decimal(weightsSquared[i])/diff.precision
			
			weightedMeanSum += Decimal(weights[i]) * (variables[i + 1].value.precisionMean - messages[i + 1].value.precisionMean) / (variables[i + 1].value.precision - messages[i + 1].value.precision)
			anotherWeightedMeanSum += Decimal(weights[i]) * diff.precisionMean/diff.precision
			
		newPrecision = Decimal(1.0)/inverseOfNewPrecisionSum
		
		newPrecisionMean = newPrecision*weightedMeanSum
		
		newMessage = fromPrecisionMean(newPrecisionMean, newPrecision)
		oldMarginalWithoutMessage = marginal0/message0
		
		newMarginal = oldMarginalWithoutMessage*newMessage
		
		messages[0].value = newMessage
		variables[0].value = newMarginal
		
		return newMarginal - marginal0
		
	def updateMessage(self, messageIndex):
		updatedMessages = list()
		updatedVariables = list()
		
		indiciesToUse = self._variableIndexOrdersForWeights[messageIndex]
		
		for i in range(len(self._messages)):
			updatedMessages.append(self._messages[indiciesToUse[i]])
			updatedVariables.append(self._variables[indiciesToUse[i]])
			
		return self._updateHelper(self._weights[messageIndex], self._weightsSquared[messageIndex], updatedMessages, updatedVariables)
		
	def _createName(self, sumVariable, variablesToSum, weights):
		name = "%s=" % sumVariable
		for i in range(len(variablesToSum)):
			isFirst = (i == 0)
			if isFirst and (weights[i] < 0):
				name += "-"
			name += "%2f*[%s]" % (abs(weights[i]), variablesToSum[i])
			isLast = (i == len(variablesToSum) - 1)
			if isLast == False:
				if weights[i + 1] >= 0:
					name += " + "
				else:
					name += " - "
		return name
		
class GaussianWithinFactor(GaussianFactor):
	def __init__(self, epsilon, variable):
		super(GaussianWithinFactor, self).__init__("%s <= %f" % (variable, epsilon))
		self._epsilon = epsilon
		self.createVariableToMessageBinding(variable)
	
	@property
	def logNormalization(self):
		marginal = self._variables[0].value
		message = self._messages[0].value
		messageFromVariable = marginal/message
		mean = messageFromVariable.mean
		std = messageFromVariable.standardDeviation
		z = cumulativeTo((self._epsilon - mean) / std) - cumulativeTo((-1.0 * self._epsilon - mean) / std)
		return -1.0 * logProductNormalization(messageFromVariable, message) + log(z)
		
	def updateMessage(self, message, variable):
		oldMarginal = deepcopy(variable.value)
		oldMessage = deepcopy(message.value)
		messageFromVariable = oldMarginal/oldMessage
		
		c = messageFromVariable.precision
		d = messageFromVariable.precisionMean
		
		sqrtC = sqrt(c)
		dOnSqrtC = d/sqrt(c)
		
		epsilonTimesSqrtC = self._epsilon*sqrtC
	
		denominator = 1.0 - wWithinMargin(dOnSqrtC, epsilonTimesSqrtC)
		newPrecision = c/denominator
		newPrecisionMean = (d + sqrtC * vWithinMargin(dOnSqrtC, epsilonTimesSqrtC))/denominator
		
		newMarginal = fromPrecisionMean(newPrecisionMean, newPrecision)
		newMessage = oldMessage*newMarginal/oldMarginal
		
		message.value = newMessage
		variable.value = newMarginal
		
		return newMarginal - oldMarginal
