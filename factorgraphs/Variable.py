class Variable(object):
	@property
	def value(self):
		return self._value

	@value.set
	def value(self, value):
		self._value = value

	def __init__(self, name, prior):
		self._name = name
		self._value = prior
		self._prior = prior

	def resetToPrior(self):
		self._value = self._prior

	def __str__(self):
		return self._name

class DefaultVariable(Variable):
	def __init__(self):
		super(Variable, self).__init__("Default", 0)

	@property
	def value(self):
		return 0

	@value.set
	def value(self, value):
		raise NotImplementedError()

class KeyedVariable(Variable):
	def __init__(self, key, name, prior):
		super(Variable, self).__init__(name, prior)
		self._key = key

	@property
	def key(self):
		return self._key

class VariableFactory(object):
	def __init__(self, variablePriorInitializer):
		self._variablePriorInitializer
		
	def createBasicVariable(self, nameFormat, args):
		name = nameFormat % args
		return Variable(name, self._variablePriorInitializer)

	def createKeyedVariable(self, key, nameFormat, args):
		name = nameFormat % args
		return KeyedVariable(key, name, self._variablePriorInitializer)
