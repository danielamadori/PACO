import numpy as np
import random

from solver.found_strategy import compare_bound
from solver.pareto import get_non_dominated_impacts, get_dominated_impacts
from solver.solver import paco
from utils.env import IMPACTS_NAMES


def pareto_optimal_impacts(bpmn: dict, bound: np.ndarray = None, decimal_number: int = 0):
	parse_tree = None
	execution_tree = None
	if bound is None:
		bound = np.zeros(len(bpmn[IMPACTS_NAMES]))

	mean_bound = bound
	text_result, parse_tree, execution_tree, found, min_frontier_expected_impacts, choices, name_svg = paco(bpmn, mean_bound, parse_tree, execution_tree)
	max_frontier_expected_impacts = [execution_tree.root.cei_bottom_up]

	i = 0
	while True:
		min_bound = np.minimum.reduce(min_frontier_expected_impacts)
		if found:
			#if np.all(compare_bound(mean_bound, bound) <= 0) or i >= 10:
			#	break
			max_frontier_expected_impacts.append(mean_bound)
			max_bound = mean_bound
		else:
			max_bound = np.maximum.reduce(max_frontier_expected_impacts)

		mean_bound = (min_bound + max_bound) / 2

		#min_bound = min_frontier_expected_impacts.pop(random.randint(0, len(min_frontier_expected_impacts)-1))

		text_result, parse_tree, execution_tree, found, min_expected_impacts, choices, name_svg = paco(bpmn, mean_bound, parse_tree, execution_tree)

		'''
		max_frontier_expected_impacts.extend([np.round(ei, decimal_number) for ei in max_expected_impacts])
		max_frontier_expected_impacts = get_dominated_impacts(max_frontier_expected_impacts)
		'''
		min_frontier_expected_impacts.extend([np.round(ei, decimal_number) for ei in min_expected_impacts])
		min_frontier_expected_impacts = get_non_dominated_impacts(min_frontier_expected_impacts)

		s = ""
		for j in range(len(min_frontier_expected_impacts)):
			s += f"Impacts {j}:\t{min_frontier_expected_impacts[j]}\n"
		print(f"Attempt {i}:\t{bpmn[IMPACTS_NAMES]}\nSelected:\t{mean_bound}\n" + s)

		i += 1

	return bound, min_frontier_expected_impacts, parse_tree, execution_tree, choices



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