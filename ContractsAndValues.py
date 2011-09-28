class SupportPartialPlay(object):
	'''Class to be extended and implemented for denoting that a class supports partial play'''
	@property
	def partialPlayPercentage(self):
		'''
		Indicates the percent of time the player should be weighted where 0.0 indicates the player didn't play
		and 1.0 indicates the player played 100% of the time
		'''
		raise NotImplementedError()

class SupportPartialUpdate(object):
	'''Class to be extended and implemented for denoting that a class supports partial updates'''
	@property
	def partialUpdatePercentage(self):
		'''
		Indicated how much of a skill update a player should receive where 0.0 represents no update and 1.0
		represents 100% of the update
		'''
		raise NotImplementedError()

class PairwiseComparison(object):
	'''Enum like class for pairwise comparisons between players'''
	WIN = 1
	DRAW = 0
	LOSE = -1

def getPartialPlayPercentage(player):
	if isinstance(player, SupportPartialPlay):
		partialPlayPercentage = player.partialPlayPercentage
		return partialPlayPercentage if partialPlayPercentage is > .0001 else .0001
	else # assume 100% since the player doesnt support partial play
		return 1.0
