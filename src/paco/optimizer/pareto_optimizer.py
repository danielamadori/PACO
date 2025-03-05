import json

import numpy as np
import random
import ast
from paco.optimizer.pareto import get_min_dominated_impacts, get_max_dominating_vectors, get_dominated_vectors
from paco.searcher.found_strategy import compare_bound
from paco.solver import paco, json_to_paco
from utils.env import IMPACTS_NAMES


def pareto_optimal_impacts(bpmn: dict, max_bound:np.ndarray= None, decimal_number: int = 0):
	min_solutions = []
	possible_min_solution = []
	if max_bound is None:
		possible_min_solution.append(np.zeros(len(bpmn[IMPACTS_NAMES]), dtype=np.float64))
	else:
		possible_min_solution.append(max_bound)

	i = 0
	found_optimal = False

	json_input = json.dumps({
		"bpmn": bpmn,
		"bound": str([0] * len(bpmn[IMPACTS_NAMES]))
	})

	while True:
		json_input = json.loads(json_input)
		s = ""
		for j in range(len(min_solutions)):
			s += f"Impacts {j}:\t{min_solutions[j]}\n"
		#print(f"Guaranteed Bound:\n", s)

		s = ""
		for j in range(len(possible_min_solution)):
			s += f"Impacts {j}:\t{possible_min_solution[j]}\n"
		#print(f"Possible Bound:\n", s)

		solutions = []
		if max_bound is not None:
			solutions = [solution for solution in min_solutions if np.all(compare_bound(solution, max_bound) <= 0)]

		if len(possible_min_solution) == 0 or len(solutions) > 0:
			found_optimal = True

			if len(solutions) > 0:
				print("Max bound found")
				json_input["bound"] = solutions.pop(random.randint(0, len(solutions)-1))

			if len(min_solutions) > 0:
				print("Min solutions found")
				json_input["bound"] = min_solutions.pop(random.randint(0, len(min_solutions)-1))

		else:
			bound = possible_min_solution.pop(random.randint(0, len(possible_min_solution)-1))

		print(f"Attempt {i}:\t{bpmn[IMPACTS_NAMES]}\nSelected:\t{json_input["bound"]}\n")
		json_input.update({"bound": str(bound)})

		json_input = json_to_paco(json_input, search_only=not found_optimal)

		dict_output = json.loads(json_input)

		print(dict_output["times"])

		tmp = ast.literal_eval(dict_output["possible_min_solution"])
		new_possible_min_solution = [np.fromstring(item.strip("[]"), sep=" ") for item in tmp]

		tmp = ast.literal_eval(dict_output["guaranteed_bounds"])
		new_min_solutions = [np.fromstring(item.strip("[]"), sep=" ") for item in tmp]

		expected_impacts = None
		if "expected_impacts" in dict_output.keys():
			expected_impacts = np.array(dict_output["expected_impacts"], dtype=np.float64)

		if found_optimal:
			print("Optimal solution found after", i, "attempts")
			break

		#a: Finds the vectors in new_possible_min_solution dominated by vectors in new_min_solutions.
		#b: Finds the vectors in new_min_solutions dominated by vectors in new_possible_min_solution.
		a, b = get_dominated_vectors(new_possible_min_solution, new_min_solutions)
		if len(b) > 0:
			print("Limit found")
			for ei in b:
				print("Limit:", ei)
		else:
			possible_min_solution.extend([np.round(ei, decimal_number) for ei in new_possible_min_solution])
			min_solutions.extend([np.round(ei, decimal_number) for ei in new_min_solutions])
			if expected_impacts is not None:
				min_solutions.append(expected_impacts)

		possible_min_solution = get_max_dominating_vectors(possible_min_solution)
		min_solutions = get_min_dominated_impacts(min_solutions)
		i += 1

	return dict_output, bound, expected_impacts, min_solutions
