class Schedule(object):
	def __init__(self, name):
		self._name = name

	def visit(self, depth = -1, maxDepth = 0):
		raise NotImplementedError()

	def __str__(self):
		return self._name

class ScheduleStep(Schedule):
	def __init__(self, name, factor, index):
		super(Schedule, self).__init__(name)
		self._factor = factor
		self._index = index

	def visit(self, depth = -1, maxDepth = 0):
		return self._factor.updateMessage(self._index)

class ScheduleSequence(Schedule):
	def __init__(self, name, schedules):
		super(Schedule, self).__init__(name)
		self._schedules = schedules

	def visit(self, depth = -1, maxDepth = 0):
		maxDelta = 0
		for schedule in self._schedules:
			lastVisit = schedule.visit(depth + 1, maxDepth)
			maxDelta = lastVisit if lastVisit > maxDelta else maxDelta
		return maxDelta

class ScheduleLoop(Schedule):
	def __init__(self, name, scheduleToLoop, maxDelta):
		super(Schedule, self).__init__(self)
		self._scheduleToLoop = scheduleToLoop
		self._maxDelta = maxDelta

	def visit(self, depth = -1, maxDepth = 0):
		delta = self._scheduleToLoop.visit(depth + 1, maxDepth)
		while delta > self._maxDelta:
			delta = self._scheduleToLoop.visit(depth + 1, maxDepth)
		return delta
