import copy
import enum
import numpy as np
from parser.tree_lib import CNode, CTree
from solver.execution_tree import ExecutionTree
from evaluations.evaluate_execution_path import evaluate_execution_path, find_all_decisions
from evaluations.evaluate_impacts import evaluate_unavoidable_impacts


class TypeStrategy(enum.IntEnum):
	CURRENT_IMPACTS = 0
	UNAVOIDABLE_IMPACTS = 1
	DECISION_BASED = 2

	def __str__(self):
		return str(self.value)


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


def decision_based(region_tree: CTree, decisions_taken: dict[CNode, set[ExecutionTree]]) -> (list[CNode], list[np.ndarray], list):
	decisions, decisions_names = find_all_decisions(region_tree)
	decision_vectors, labels = [], []
	for decision_taken, executionTrees in decisions_taken.items():
		for executionTree in executionTrees:
			decision_vector, label = evaluate_execution_path(decisions, executionTree.root.states.activityState)
			decision_vectors.append(decision_vector)
			labels.append(label)

	return decisions_names, decision_vectors, labels
