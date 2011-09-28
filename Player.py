import ContractsAndValues
from Gaurd import argumentInRangeInclusive

_defaultPartialPlayPercentage = 1.0
_defaultPartialUpdatePercentage = 1.0

class Player(ContractsAndValues.SupportPartialPlay, ContractsAndValues.SupportPartialUpdate):
	'''Represents a player who has a Rating'''
	@property
	def id(self):
		return self._id

	@property
	def partialPlayPercentage(self):
		return self._partialPlayPercentage

	@property
	def partialUpdatePercentage(self):
		return self._partialUpdatePercentage

	def __init__(self, ID, partialPlayPercentage = _defaultPartialPlayPercentage, partialUpdatePercentage = _defaultPartialUpdatePercentage):
		argumentInRangeInclusive(partialPlayPercentage, 0, 1.0, "partialPlayPercentage")
		argumentInRangeInclusive(partialUpdatePercentage, 0, 1.0, "partialUpdatePercentage")
		self._id = ID
		self._partialPlayPercentage = partialPlayPercentage
		self._partialUpdatePercentage = partialUpdatePercentage

