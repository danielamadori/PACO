import numpy as np
from saturate_execution.states import ActivityState
from parser.tree_lib import CNode, CTree


def find_all_decisions_rec(tree: CTree) -> list[CNode]:
	if not tree.root.children:
		return []

	decisions = [child.root for child in tree.root.children if tree.root.type in {'choice', 'natural'}]
	for subTree in tree.root.children:
		decisions.extend(find_all_decisions_rec(subTree))

	return decisions

def find_all_decisions(region_tree: CTree) -> list[CNode]:
	decisions = sorted(find_all_decisions_rec(region_tree), key=lambda decision: decision.id)
	decisions_names = []
	for decision in decisions:
		decisions_names.append(str(decision.parent.name) + '_' + ('0' if decision.parent.children[0].root == decision else '1'))

	return decisions, decisions_names

def evaluate_execution_path(decisions: list[CNode], execution: ActivityState) -> (np.ndarray, str):
	decisions_vector = np.array([0 if decision not in execution or execution[decision] < ActivityState.ACTIVE
								 else 1 for decision in decisions], dtype='int')

	decisions_taken = [node for node in execution if node.parent and node.parent.type in {'choice', 'natural'}]
	decisions_taken = sorted(decisions_taken, key=lambda decision: decision.id)

	label = ''
	for decision_taken in decisions_taken:
		if execution[decision_taken] >= ActivityState.ACTIVE:
			choice_nature = decision_taken.parent
			label += str(choice_nature.name) + '_' + ('0' if choice_nature.children[0].root == decision_taken else '1') + ';'

	return decisions_vector, label[:-1]
