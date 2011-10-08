class Message(object):
	def __init__(self, value, name):
		self._value = value
		self._name = name
		
	@property
	def value(self):
		return self._value
		
	@value.setter
	def value(self, value):
		return Message(value, self._name)
		
	@property
	def name(self):
		return self._name
		
	def __str__(self):
		return self._name
		
	def __eq__(self, other):
		if isinstance(other, Message) == False:
			return False
		return other.value == self._value and other.name == self._name
	
	def __ne__(self, other):
		return (self == other) == False
		
	def __hash__(self):
		return hash(self._name) ^ hash(self._value)
		
class Variable(object):
	def __init__(self, prior, name):
		self._name = "Variable[%s]" % name
		self._prior = prior
		self.resetToPrior()
		
	@property
	def name(self):
		return self._name
		
	@property
	def prior(self):
		return self._prior
		
	@property
	def value(self):
		return self._value
		
	@value.setter
	def value(self, value):
		self._value = value
	
	def resetToPrior(self):
		self._value = self._prior
		
	def __str__(self):
		return self._name
		
class KeyedVariable(Variable):
	def __init__(self, prior, name, key):
		super(KeyedVariable, self).__init__(prior, name)
		self._key = key
		
	@property
	def key(self):
		return self._key
		
	@key.setter
	def key(self, value):
		self._key = key
		
class VariableFactory(object):
	def __init__(self, variablePriorInitializer):
		self._variablePriorInitializer = variablePriorInitializer
		
	def createBasicVariable(self, name):
		return Variable(self._variablePriorInitializer(), name)
		
	def createKeyedVariable(self, name, key):
		return KeyedVariable(self._variablePriorInitializer(), name, key)
		
class Schedule(object):
	def __init__(self, name):
		self._name = name
		
	@property
	def name(self):
		return self._name
		
	def visit(self, depth = None, maxDepth = None):
		if depth is None and maxDepth is None:
			self.visit(-1, 0)
		else:
			raise NotImplementedError()

	def __str__(self):
		return self._name
		
class ScheduleStep(Schedule):
	def __init__(self, name, factor, index):
		super(ScheduleStep, self).__init__(name)
		self._factor = factor
		self._index = index
		
	@property
	def factor(self):
		return self._factor
	
	@property
	def index(self):
		return self._index
	
	def visit(self, depth, maxDepth):
		return self._factor.updateMessage(self._index)
		
class ScheduleSequence(Schedule):
	def __init__(self, name, schedules):
		super(ScheduleSequence, self).__init__(name)
		self._schedules = schedules
		
	def visit(self, depth, maxDepth):
		maxDelta = 0
		for currentSchedule in self._schedules:
			delta = currentSchedule.visit(depth + 1, maxDepth)
			maxDelta = delta if delta > maxDelta else maxDelta
		return maxDelta
		
class ScheduleLoop(Schedule):
	def __init__(self, name, scheduleToLoop, maxDelta):
		super(ScheduleLoop, self).__init__(name)
		self._scheduleToLoop = scheduleToLoop
		self._maxDelta = maxDelta
		
	def visit(self, depth, maxDepth):
		delta = self._scheduleToLoop.visit(depth+1, maxDepth)
		while delta > self._maxDelta:
			delta = self._scheduleToLoop.visit(depth+1, maxDepth)
		return delta
		
class Factor(object):
	def __init__(self, name):
		self._name = "Factor[%s]" % name
		self._message = list()
		self._variables = list()
		self._messageToVariable = dict()
		
	@property
	def messages(self):
		return self._messages
		
	@property
	def variables(self):
		return self._variables
		
	@property
	def messageToVariable(self):
		return self._messageToVariable
		
	@property
	def logNormalization(self):
		return 0
	
	@property
	def numberOfMessages(self):
		return len(self._messages)
		
	def updateMessage(self, messageIndex):
		message = self._messages[messageIndex]
		return self._updateMessageInternal(message, self._messageToVariable[message])
		
	def _updateMessageInternal(self, message, variable):
		raise NotImplementedError()
		
	def resetMarginals(self):
		for currentVariable in self._variables:
			currentVariable.resetToPrior()
			
	def sendMessage(self, messageIndex):
		message = self._messages[messageIndex]
		variable = self._messageToVariable[message]
		return self._sendMessageInternal(message, variable)
		
	def _sendMessageInternal(self, message, variable):
		raise NotImplementedError()
		
	def createVariableToMessageBinding(self, variable):
		raise NotImplementedError()
		
	def _createVariableToMessageBindingInternal(self, variable, message):
		index = len(self._messages)
		self._messages.append(message)
		self._variables.append(variable)
		self._messageToVariable[message] = variable
		return message
		
	def __str__(self):
		return self._name
		
class FactorGraph(object):
	@property
	def variableFactory(self):
		return self._variableFactory
		
	@variableFactory.setter
	def variableFactory(self, value):
		self._variableFactory = value
		
class FactorGraphLayer(object):
	def __init__(self, parentGraph):
		self._parentFactorGraph = parentGraph
		self._localFactors = list()
		self._outputVariablesGroups = list()
		self._inputVariablesGroups = list()
		
	@property
	def inputVariablesGroups(self):
		return self._inputVariablesGroups
		
	@property
	def parentFactorGraph(self):
		return self._parentFactorGraph
		
	@parentFactorGraph.setter
	def parentFactorGraph(self, value):
		self._parentFactorGraph = value
		
	@property
	def outputVariablesGroups(self):
		return self._outputVariablesGroups
		
	@property
	def localFactors(self):
		return self._localFactors
		
	def scheduleSequence(self, itemsToSequence, name):
		return ScheduleSequence(name, itemsToSequence)
		
	def addLayerFactor(factor):
		self._localFactors.append(factor)
		
class FactorList(object):
	def __init__(self):
		self._list = list()
		
	@property
	def logNormalization(self):
		sumLogZ = 0.0
		sumLogS = 0.0
		for item in self._list:
			item.resetMarginals()
			sumLogS += item.logNormalization
			for i in range(item.numberOfMessage):
				sumLogZ += item.sendMessage[i]
		return sumLogZ + sumLogS

	@property
	def count(self):
		return len(self._list)
		
	def addFactor(self, factor):
		self._list.append(factor)
		return factor
