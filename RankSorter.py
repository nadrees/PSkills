import Gaurd

def sortByRank(teams, ranks):
	'''Sorts the teams in increasing order of their ranks. len(teams) must equal len(ranks), and both teams and ranks are lists'''
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
