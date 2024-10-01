import numpy as np


def get_non_dominated_impacts(frontier):
	non_dominated_impacts = []

	for i, arr in enumerate(frontier):
		dominated = False
		for j, other_arr in enumerate(frontier):
			if (i != j and # arr is_dominated by other_arr
				np.all(arr >= other_arr) and np.any(arr > other_arr)):
				dominated = True
				break
		if not dominated:
			# Check for duplicates
			if not any(np.array_equal(arr, x) for x in non_dominated_impacts):
				non_dominated_impacts.append(arr)

	return non_dominated_impacts

def get_dominated_impacts(frontier):
	dominated_impacts = []

	for i, arr in enumerate(frontier):
		dominated = False
		for j, other_arr in enumerate(frontier):
			if (i != j and  # arr is dominated by other_arr
					np.all(arr >= other_arr) and np.any(arr > other_arr)):
				dominated = True
				break
		if dominated:
			# Check for duplicates
			if not any(np.array_equal(arr, x) for x in dominated_impacts):
				dominated_impacts.append(arr)

	return dominated_impacts