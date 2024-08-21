import copy

import numpy as np


def find_best_threshold(vl: tuple[list, list], column_index: int):
	values_by_label = {}
	for vector, label in zip(vl[0], vl[1]):
		if label not in values_by_label:
			values_by_label[label] = [vector[column_index]]
		else:
			values_by_label[label].append(vector[column_index])

	if len(values_by_label) == 1:
		return None #Only one cluster, impossible to find a threshold

	# Find the max and min of each cluster
	min_max_by_label = {label: (min(values), max(values)) for label, values in values_by_label.items()}
	label_0_min, label_0_max = min_max_by_label[0]
	label_1_min, label_1_max = min_max_by_label[1]

	# Threshold: the midpoint between the max of one and the min of the other
	return (max(label_0_min, label_1_min) + min(label_0_max, label_1_max)) / 2


def generate_clauses(vl: tuple[list, list], column_index: int):
	threshold = find_best_threshold(vl, column_index)
	if threshold is None:
		return []
	return [
		f"v[{column_index}] < {threshold}", f"v[{column_index}] <= {threshold}",
		f"v[{column_index}] >= {threshold}", f"v[{column_index}] > {threshold}"
	]


def separate(vectors:list, labels: list, formula):
	tv, tl, fl = [], [], []
	for v, l in zip(vectors, labels):
		if eval(formula):
			tv.append(v)
			tl.append(l)
		else:
			fl.append(l)

	return all(l == tl[0] for l in tl) and all(l == fl[0] for l in fl), (tv, tl)


def generate_CNFS(vectors:list, labels: list, vectors_size: int, formula, sat: tuple[list, list]):
	sat_len = len(sat[0])
	new_formulas = []
	for idx in range(vectors_size):
		for clause in generate_clauses(sat, idx):
			if formula == "":
				and_formula = clause
				or_formula = ""
			else:
				if clause in formula:
					continue
				and_formula = f"({formula} and {clause})"
				or_formula = f"({formula} or {clause})"

			is_separated, new_sat = separate(vectors, labels, and_formula)
			if is_separated:
				#print(f"Found: and_formula: {and_formula}, new_sat_v: {new_sat[0]} new_sat_l: {new_sat[1]}")
				return True, [(and_formula, new_sat)]

			# Bigger than one because we need at least one element in each cluster
			if 1 < len(new_sat[0]) < sat_len:
				#print(f"and_formula: {and_formula}, new_sat_v: {new_sat[0]} new_sat_l: {new_sat[1]}")
				new_formulas.append((and_formula, new_sat))

			if or_formula != "":
				is_separated, new_sat = separate(vectors, labels, or_formula)
				if is_separated:
					#print(f"Found: or_formula: {or_formula}, new_sat_v: {new_sat[0]} new_sat_l: {new_sat[1]}")
					return True, [(or_formula, new_sat)]
				if 1 < len(new_sat[0]):
					#print(f"or_formula: {or_formula}, new_sat_v: {new_sat[0]} new_sat_l: {new_sat[1]}")
					new_formulas.append((or_formula, new_sat))

	return False, new_formulas


def bnf_search_min_cnf(vectors: list, labels: list, vectors_size: int, k: int, formula, sat: tuple[list, list]):
	#print(f"depth: {depth}, formula: {formula}, sat_v: {sat[0]}, sat_l: {sat[1]}")
	found, frontier = generate_CNFS(vectors, labels, vectors_size, formula, sat)
	if len(frontier) == 0:
		#print("No frontier")
		return False, []
	if found or k <= 1:
		#print("Found or depth limit")
		return found, frontier

	depth = 1 # Actual number of clauses in the formula
	while depth < k:
		failed_frontier = []
		for (new_formula, new_sat) in frontier:
			found, new_frontier = bnf_search_min_cnf(vectors, labels, vectors_size, 1, new_formula, new_sat)
			#for f, f_sat in new_frontier:
			#	print(f"new_formula: {f}, new_sat_v: {f_sat[0]} new_sat_l: {f_sat[1]}")
			if found:
				return True, new_frontier
			if len(new_frontier) > 0:
				failed_frontier.extend(new_frontier)
				# TODO check if there are formulas that have the same sat, in this case there is an equivalence
		if len(failed_frontier) == 0:
			print("Impossible to separate")
			return False, frontier

		frontier = failed_frontier
		depth += 1

		#print(f"depth: {depth}")
		#for f, f_sat in frontier:
		#	print(f"new_formula: {f}, new_sat_v: {f_sat[0]} new_sat_l: {f_sat[1]}")



	return False, frontier


def get_min_cnf(vectors: list, labels: list, vectors_size: int, k: int):
	return bnf_search_min_cnf(vectors, labels, vectors_size, k, "", (vectors, labels))


def exe_test(vectors, labels, vector_size, k):
	found, formula = get_min_cnf(vectors, labels, vector_size, k)
	if found:
		print("Found formula:", formula[0])
	else:
		print("Failed CNFs")
		for f in formula:
			print(f"{f[0]}: {f[1]}")
	print()

def exe_tests(tests):
	for i, test in enumerate(tests):
		print(f"Running test {i + 1}, comment: {test['comment']}")
		exe_test(test['vectors'], test['labels'], test['vector_size'], test['k'])


test_single_vector = {
	'comment': 'Single vector, should return no formula possible',
	'vectors': [
		np.array([1.0, 1.0, 1.0, 1.0])
	], 'labels': [1],
	'vector_size': 4, 'k': 1
}
test_identical_vectors = {
	'comment': 'Identical vectors with different labels, impossible to separate',
	'vectors': [
		np.array([1.0, 1.0, 1.0, 1.0]),
		np.array([1.0, 1.0, 1.0, 1.0])
	], 'labels': [1, 0],
	'vector_size': 4, 'k': 100
}
test_boundary_values = {
	'comment': 'Values on the boundary, should handle correctly with k = 2',
	'vectors': [
		np.array([0.5, 0.5, 0.5, 0.5]),
		np.array([0.5, 0.5, 0.5, 0.5]),
		np.array([1.0, 1.0, 1.0, 1.0]),
		np.array([0.0, 0.0, 0.0, 0.0])
	], 'labels': [1, 1, 0, 0],
	'vector_size': 4, 'k': 2
}

test_boundary_values_k_bigger = copy.deepcopy(test_boundary_values)
test_boundary_values_k_bigger['comment'] = 'Values on the boundary, should handle correctly with k = 2, but k = 3'
test_boundary_values_k_bigger['k'] = 3

test_overlapping_vectors = {
	'comment': 'Overlapping vector ranges, challenging threshold selection',
	'vectors': [
		np.array([0.5, 0.5, 0.5, 0.5]),
		np.array([0.6, 0.6, 0.6, 0.6]),
		np.array([0.7, 0.7, 0.7, 0.7]),
		np.array([0.8, 0.8, 0.8, 0.8])
	], 'labels': [1, 1, 0, 0],
	'vector_size': 4, 'k': 1
}
test_two_different_features = {
	'comment': 'Need two different features to separate, min k = 3',
	'vectors': [
		np.array([0., 1., 0., 1.]),
		np.array([1., 1., 1., 0.5]),
		np.array([1., 1., 1., 0.6]),
		np.array([1., 0., 1., 0.])
	], 'labels': [1, 1, 0, 0],
	'vector_size': 4, 'k': 3
}

test_two_different_features_complex = {
	'comment': 'Need more complex conditions with multiple features to separate, min k = 4',
	'vectors': [
		np.array([0., 1., 0., 1.]),
		np.array([1., 1., 1., 0.5]),
		np.array([1., 1., 1., 0.6]),
		np.array([1., 0., 1., 0.]),
		np.array([0.5, 0.5, 0.5, 0.5]),
		np.array([0., 0., 0., 0.]),
		np.array([1., 1., 0., 1.]),
		np.array([1., 0., 0., 1.])
	],
	'labels': [1, 1, 0, 0, 1, 0, 0, 1],
	'vector_size': 4,
	'k': 4
}
#Random ChatGPT vectors:
test_two_conditions = {
	'comment': 'Need one feature to separate, min k = 2',
	'vectors': [
		np.array([0., 0.]),
		np.array([1., 0.]),
		np.array([1., 1.]),
		np.array([0., 1.])
	], 'labels': [0, 1, 1, 0],
	'vector_size': 2, 'k': 2
}

test_three_conditions = {
	'comment': 'Need two different features to separate, min k = 3',
	'vectors': [
		np.array([0., 1., 0., 1.]),
		np.array([1., 1., 1., 0.5]),
		np.array([1., 1., 1., 0.6]),
		np.array([1., 0., 1., 0.])
	], 'labels': [1, 1, 0, 0],
	'vector_size': 4, 'k': 3
}
test_four_conditions = {
	'comment': 'Need four different conditions to separate, min k = 4',
	'vectors': [
		np.array([0., 0., 1., 1.]),
		np.array([1., 1., 0., 0.]),
		np.array([0., 1., 0., 1.]),
		np.array([1., 0., 1., 0.]),
	],
	'labels': [1, 1, 0, 0],
	'vector_size': 4, 'k': 4
}


tests = [
	test_single_vector,
	test_identical_vectors,
	test_boundary_values,
	test_boundary_values_k_bigger,
	test_overlapping_vectors,
	test_two_different_features,
	test_two_different_features_complex
]

hard_tests = [
	test_two_conditions,
	test_three_conditions,
	test_four_conditions,
]
exe_tests(tests)
#exe_tests([tests[-1]])

#exe_tests([test_four_conditions])
#exe_tests(hard_tests)

