import numpy as np
import random
from paco.searcher.pareto import get_min_dominated_impacts, get_max_dominating_vectors, get_dominated_vectors
from paco.solver import paco
from utils.env import IMPACTS_NAMES


def compare_element_wise(A, B):
	if len(A) != len(B):
		raise ValueError("Lists A and B must have the same length.")

	less_than = []
	greater_equal = []

	# Loop through each pair of arrays in A and B
	for a, b in zip(A, B):
		if np.all(a < b):
			less_than.append((a, b))
		if np.all(a >= b):
			greater_equal.append((a, b))

	return less_than, greater_equal


def pareto_optimal_impacts(bpmn: dict, decimal_number: int = 0):
	parse_tree = None
	execution_tree = None

	bound = np.zeros(len(bpmn[IMPACTS_NAMES]), dtype=np.float64)

	text_result, parse_tree, execution_tree, expected_impacts, possible_min_solution, min_solutions, choices, name_svg = paco(bpmn, bound, parse_tree, execution_tree, search_only=True)

	i = 0
	found_optimal = False
	while True:
		s = ""
		for j in range(len(min_solutions)):
			s += f"Impacts {j}:\t{min_solutions[j]}\n"
		print(f"Guaranteed Bound:\n", s)

		s = ""
		for j in range(len(possible_min_solution)):
			s += f"Impacts {j}:\t{possible_min_solution[j]}\n"
		print(f"Possible Bound:\n", s)

		print(f"Attempt {i}:\t{bpmn[IMPACTS_NAMES]}\nSelected:\t{bound}\n")


		if len(possible_min_solution) == 0:
			print("Min solutions found")
			found_optimal = True
			bound = min_solutions.pop(random.randint(0, len(min_solutions)-1))
		else:
			bound = possible_min_solution.pop(random.randint(0, len(possible_min_solution)-1))

		#min_bound = np.minimum.reduce(possible_min_solution)
		#	max_bound = np.maximum.reduce(min_solutions)

		#	mean_bound = np.round(np.mean([min_bound, max_bound], axis=0), decimals=decimal_number)
		#else:
		#	mean_bound = possible_min_solution.pop(random.randint(0, len(possible_min_solution)-1))


		text_result, parse_tree, execution_tree, expected_impacts, new_possible_min_solution, new_min_solutions, choices, name_svg = paco(bpmn, bound, parse_tree, execution_tree, search_only=not found_optimal)
		if found_optimal:
			print("Optimal solution found")
			break

		possible_min_solution.extend([np.round(ei, decimal_number) for ei in new_possible_min_solution])
		min_solutions.extend([np.round(ei, decimal_number) for ei in new_min_solutions])
		if expected_impacts is not None:
			min_solutions.append(expected_impacts)

		#Finds the vectors in possible_min_solution dominated by vectors in min_solutions.
		#Finds the vectors in min_solutions dominated by vectors in possible_min_solution.
		new_possible_min_solution, new_min_solution = get_dominated_vectors(possible_min_solution, min_solutions)

		if len(new_min_solution) > 0:
			possible_min_solution = [s for s in possible_min_solution if not any(np.array_equal(s, t) for t in new_possible_min_solution)]
			min_solutions = min_solutions + new_min_solution

		possible_min_solution = get_max_dominating_vectors(possible_min_solution)
		min_solutions = get_min_dominated_impacts(min_solutions)


		i += 1

	return bound, expected_impacts, min_solutions, parse_tree, execution_tree, choices



'''
from multiprocessing import Process, Queue

# Worker function to execute paco and send results via a queue
def paco_worker(bpmn, bound, parse_tree, execution_tree, decimal_number, queue):
	try:
		result = paco(bpmn, bound, parse_tree, execution_tree)
		if result:
			text_result, parse_tree, execution_tree, found, expected_impacts, choices, name_svg = result
			expected_impacts_rounded = [np.round(ei, decimal_number) for ei in expected_impacts]
			queue.put((text_result, parse_tree, execution_tree, found, expected_impacts_rounded, choices, name_svg))
		else:
			queue.put(None)
	except Exception as e:
		queue.put(f"Error: {e}")

def pareto_optimal_impacts_parallel(bpmn: dict, decimal_number: int = 0, max_workers: int = 1):
	bound = np.zeros(len(bpmn[IMPACTS_NAMES]), dtype=np.float64)
	parse_tree = None
	execution_tree = None

	found = False
	pareto_frontier_impacts = [bound]

	i = 0
	while not found:
		n_workers = min(max_workers, len(pareto_frontier_impacts))
		if n_workers <= 0:
			n_workers = 1

		processes = []
		result_queue = Queue()

		# Start the processes
		for _ in range(n_workers):
			p = Process(target=paco_worker, args=(bpmn, bound, parse_tree, execution_tree, decimal_number, result_queue))
			p.start()
			processes.append(p)

		# Collect results from the queue
		for p in processes:
			p.join()  # Ensure each process has finished
			result = result_queue.get()

			if result is not None and isinstance(result, tuple):
				text_result, parse_tree, execution_tree, found, expected_impacts, choices, name_svg = result
				pareto_frontier_impacts.extend(expected_impacts)

				if found:
					break
			elif isinstance(result, str) and result.startswith("Error"):
				print(result)  # Log the error

		# Get the non-dominated impacts
		pareto_frontier_impacts = get_non_dominated_impacts(pareto_frontier_impacts)

		# If not found, select a new bound
		if not found and pareto_frontier_impacts:
			try:
				bound = pareto_frontier_impacts.pop(random.randint(0, len(pareto_frontier_impacts) - 1))
			except IndexError:
				print("Error: pareto_frontier_impacts is empty after popping.")
				break

		# Logging impacts after each attempt
		s = "\n".join([f"Impacts {j}:\t{pareto_frontier_impacts[j]}" for j in range(len(pareto_frontier_impacts))])
		print(f"Attempt {i}:\t{bpmn[IMPACTS_NAMES]}\nSelected:\t{bound}\n{s}")

		i += 1

	return bound, pareto_frontier_impacts, parse_tree, execution_tree, choices
'''