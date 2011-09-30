class Message(object):
	@property
	def value(self):
		return self._value

	@value.set
	def value(self, value):
		self._value = value

	def __init__(self, value, nameFormat = None, nameFormatArgs = None):
		self._value = value
		self._nameFormat = nameFormat
		self._nameFormatArgs = nameFormatArgs

	def __str__(self):
		if self._nameFormat is not None:
			return self._nameFormat % self._nameFormatArgs
		return ""

class Factor(object):
	def __init__(self, name):
		self._name = "Factor[%s]" % name
		self._messages = list()
		self._messageToVariableBinding = list()
		self._variables = list()

	@property
	def logNormalization(self):
		return 0

	@property
	def numberOfMessages(self):
		return len(self._messages)

	@property
	def messages(self):
		return self._messages

	@property
	def variables(self):
		return self._variables

	def _getVariable(self, message):
		for messageToVariable in self._messageToVariableBinding:
			if messageToVariable[0] == message:
				return messageToVariable[1]

	def updateMessage(self, messageIndex):
		'''Update the message and marginal of the i-th variable that the factor is connected to'''
		message = self._messages[messageIndex]
		variable = self._getVariable(message)
		return self._updateMessageInternal(message, variable)

	def _updateMessageInternal(self, message, variable):
		raise NotImplementedError()

	def resetMarginals(self):
		'''resets the marginal of the variables a factor is connected to'''
		for messageToVariable in self._messageToVariableBinding:
			variable = messageToVariable[0]
			variable.resetToPrior()

	def sendMessage(self, messageIndex):
		'''sends the ith message to the marginal and returns the log-normalization constant'''
		message = self._messages[messageIndex]
		variable = self._getVariable(message)
		return self._sendMessageInternal(message, variable)

	def _sendMessageInternal(self, message, variable):
		raise NotImplementedError()

	def createVariableToMessageBinding(self, message, variable):
		raise NotImplementedError()

	def _createVariableToMessageBindingInternal(self, message, variable):
		self._messages.append(message)
		self._variables.append(variable)
		self._messageToVariableBinding.append([message, variable])

class FactorGraph(object):
	@property
	def variableFactory(self):
		return self._variableFactory
