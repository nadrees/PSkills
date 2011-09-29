import Gaurd
import unittest

def sortByRank(teams, ranks):
	'''
	Sorts the teams in increasing order of their ranks. len(teams) must equal len(ranks), and both teams and ranks are lists. Returns
	the sorted teams list.
	'''
	Gaurd.argumentNotNone(teams, "teams")
	Gaurd.argumentNotNone(ranks, "ranks")
	Gaurd.isEqual(len(teams), len(ranks), "length of args")
	team_tuples = []
	for i in range(len(teams)):
		team_tuples.append((teams[i], ranks[i]))
	team_tuples.sort(key=lambda currentTuple: currentTuple[1])
	teams = list()
	for i in range(len(team_tuples)):
		teams.append(team_tuples[i][0])
	return teams

class RankSorterTests(unittest.TestCase):
	def test_sortAlreadySortedTest(self):
		people = ['one', 'two', 'three']
		ranks = [1, 2, 3]
		people = sortByRank(people, ranks)
		self.assertEqual(people, ['one', 'two', 'three'])

	def test_sortUnsortedTest(self):
		people = ['five', 'two1', 'two2', 'one', 'four']
		ranks = [5, 2, 2, 1, 4]
		people = sortByRank(people, ranks)
		self.assertEqual(people, ['one', 'two1', 'two2', 'four', 'five'])

if __name__ == "__main__":
	unittest.main()
