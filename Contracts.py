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

