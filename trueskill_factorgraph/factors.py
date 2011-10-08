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
