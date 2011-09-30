class FactorGraphLayerBase(object):
	def buildLayer(self):
		raise NotImplementedError()

	def createPriorSchedule(self):
		return None

	def createPosteriorSchedule(self):
		return None

class FactorGraphLayer(FactorGraphLayerBase):
	def __init__(self, parentGraph):
		self._parentFactoryGraph = parentGraph
		self._localFactors = list()
		self._outputVariablesGroups = list()

	@property
	def outputVariablesGroups(self):
		return self._outputVariablesGroups

	@property
	def inputVariablesGroups(self):
		return self._inputVariablesGroups

	@property
	def parentFactoryGraph(self):
		return self._parentFactoryGraph

	@parentFactoryGraph.set
	def parentFactoryGraph(self, value):
		self._parentFactoryGraph = parentFactoryGraph

	@property
	def localFactors(self):
		return self._localFactors

	def _scheduleSequence(self, itemsToSequence, nameFormat, args):
		formattedName = nameFormat % args
		return ScheduleSequence(formattedName, itemsToSequence)

	def _addLayerFactor(self, factor):
		self._localFactors.append(factor)

class FactorList(object):
	'''helper class for computing the factor graph's normalization constant'''
	def __init__(self):
		self._list = list()

	@property
	def logNormalization(self):
		sumLogZ = 0.0
		sumLogS = 0.0
		for item in self._list:
			item.resetMarginals()
			for j in range(item.numberOfMessages):
				sumLogZ += item.sendMessage(j)
			sumLogS += item.logNormalization
		return sumLogZ + sumLogS

	@property
	def count(self):
		return len(self._list)

	def addFactor(self, factor):
		self._list.append(factor)
		return factor
