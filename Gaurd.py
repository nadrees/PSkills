def ArgumentNotNone(arg, argName):
	assert arg is not None, argName

def ArgumentIsValidIndex(index, count, argName):
	assert index >= 0 and index < count, argName

def ArgumentInRangeInclusive(value, minimum, maximum, argName):
	assert value >= minimum and value <= maximum, argName
