import numpy as np

def get_pareto_frontier(frontier):
	pareto_frontier = []

	for i, arr in enumerate(frontier):
		dominated = False
		for j, other_arr in enumerate(frontier):
			if (i != j and # arr is_dominated by other_arr
				np.all(arr >= other_arr) and np.any(arr > other_arr)):
				dominated = True
				break
		if not dominated:
			# Check for duplicates
			if not any(np.array_equal(arr, x) for x in pareto_frontier):
				pareto_frontier.append(arr)

	return np.array(pareto_frontier)
