import copy

from evaluations.evaluate_execution_path import evaluate_execution_path
from evaluations.evaluate_impacts import evaluate_unavoidable_impacts
from solver.tree_lib import CNode, CTree
from solver_optimized.execution_tree import ExecutionTree


def current_impacts(decisions: dict[CNode, set[ExecutionTree]]) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			impacts.append(copy.deepcopy(executionTree.root.impacts))
			impacts_labels.append(decision.id)

	return impacts, impacts_labels


def unavoidable_impacts(region_tree: CTree, decisions: dict[CNode, set[ExecutionTree]]) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			impacts.append(
				evaluate_unavoidable_impacts(region_tree.root,
											 executionTree.root.states,
											 executionTree.root.impacts)
			)
			impacts_labels.append(decision.id)

	return impacts, impacts_labels


def stateful(decisions: dict[CNode, set[ExecutionTree]]):
	states_vectors, labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			states_vectors.append(executionTree.root.states.activityState)
			labels.append(decision.id)

	all_nodes, states_vectors = evaluate_execution_path(states_vectors)
	#print each state_vector with the corresponding label
	s = ''
	for node in all_nodes:
		s += str(node.id) + ', '
	print("\t\t  ID: ", s [:-2])
	for i in range(len(states_vectors)):
		print(f"State vector: {states_vectors[i]}, label: {labels[i]}")

	return all_nodes, states_vectors, labels
