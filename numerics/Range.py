import sys

'''
An immutable range of Integers, including endpoints. Ranges are not empty.
'''
_intMinValue = -sys.maxint - 1

class Range(object):
	def __init__(self, minimum = None, maximum = None):
		if (maximum is None and minimum is None):
			raise ValueError('Empty ranges are disallowed')
		if (maximum is not None and minimum is not None and minimum > maximum):
			raise ValueError('Min was greater than max')
		self._minimum = minimum
		self._maximum = maximum
	
	def isInRange(self, value):
		return (self._minimum is None or self._minimum <= value) and (self._maximum is None or self._maximum >= value)

	@property
	def minimum(self):
		"""The minimum value for this range"""
		return self._minimum

	@property
	def maximum(self):
		"""The maximum value for this range"""
		return self._maximum

class PlayersRange(Range):
	def __init__(self, minimum = _intMinValue, maximum = _intMinValue):
		super(Range, self).__init__(minimum, maximum)

class TeamsRange(Range):
	def __init__(self, minimum = _intMinValue, maximum = _intMinValue):
		super(Range, self).__init__(minimum, maximum)

def inclusive(minimum, maximum):
	return Range(minimum, maximum)

def exactly(value):
	return Range(value, value)

def atLeast(minimum):
	return Range(minimum)

def atMost(maximum):
	return Range(maximum=maximum)
