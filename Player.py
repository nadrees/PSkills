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

	def __eq__(self, other):
		return self._id == other.id and self._partialPlayPercentage == other.partialPlayPercentage and self._partialUpdatePercentage == other.partialUpdatePercentage

	def __ne__(self, other):
		return (self == other) == False

class Team(object):
	'''Helper class for working with a team'''
	def __init__(self, player = None, rating = None):
		'''
		Constructs a team with the specified player who has the specified rating
		player should be an instance of the Player class
		rating should be an instance of the Rating class
		'''
		self._playerRatings = list()
		if player is not None and rating is not None:
			self._playerRatings.append((player, rating))

	def addPlayer(self, player, rating):
		self._playerRatings.append((player, rating))

	@property
	def asListOfTuples(self):
		return self._playerRatings
