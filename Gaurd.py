def argumentNotNone(arg, argName):
	assert arg is not None, argName

def argumentIsValidIndex(index, count, argName):
	assert index >= 0 and index < count, argName

def argumentInRangeInclusive(value, minimum, maximum, argName):
	assert value >= minimum and value <= maximum, argName

def isEqual(arg1, arg2, argName):
	assert arg1 == arg2, argName
