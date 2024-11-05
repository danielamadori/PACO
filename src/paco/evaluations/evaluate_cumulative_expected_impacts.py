import copy

import numpy as np

from paco.execution_tree.execution_tree import ExecutionTree
from paco.parser.tree_lib import CTree


def evaluate_cumulative_expected_impacts(solution_tree: ExecutionTree):
	root = solution_tree.root
	# root.cei_top_down = root.probability * root.impacts #Useless, already done in the constructor
	if root.is_final_state:
		root.cei_bottom_up = copy.deepcopy(root.cei_top_down)
		return

	onlyChoice = True
	choices_cei_bottom_up = {}
	for Transition, subTree in root.transitions.items():
		evaluate_cumulative_expected_impacts(subTree)

		choices_transitions = []
		for t in Transition:
			if t[0].type == 'choice':
				onlyChoice = False
				choices_transitions.append(t)

		if onlyChoice:
			root.cei_bottom_up += subTree.root.cei_bottom_up
		else:
			choices_transitions = tuple(choices_transitions)
			if choices_transitions not in choices_cei_bottom_up:
				choices_cei_bottom_up[choices_transitions] = copy.deepcopy(subTree.root.cei_bottom_up)
				'''
				message = ""
				for t in range(len(choices_transitions)):
					message += str(choices_transitions[t][0].id) + "->" + str(choices_transitions[t][1].id) + ", "
				print(message[:-2] + " = " + str(result[choices_transitions]))
				'''
			else:
				'''
				message = ""
				for t in range(len(choices_transitions)):
					message += str(choices_transitions[t][0].id) + "->" + str(choices_transitions[t][1].id) + ", "
				print(message[:-2] + " = " + str(result[choices_transitions]) + " + " + str(subTree.root.cei_bottom_up))
				'''
				choices_cei_bottom_up[choices_transitions] += subTree.root.cei_bottom_up

	'''
	for Transition, subTree in root.transitions.items():
		print(subTree.root.cei_bottom_up)
	
	print("choices_cei_bottom_up:")
	for child, cei_bottom_up in choices_cei_bottom_up.items():
		message = ""
		for t in range(len(child)):
			message += str(child[t][0].id) + "->" + str(child[t][1].id) + ", "
		print(message[:-2] + " = " + str(cei_bottom_up))
	print("End")
	'''
	for c in choices_cei_bottom_up.keys():
		for i in range(len(root.impacts)):
			if root.cei_bottom_up[i] < choices_cei_bottom_up[c][i]:
				root.cei_bottom_up[i] = choices_cei_bottom_up[c][i]


def evaluate_min_max_impacts(tree: CTree, decision_impacts: dict, impacts_size: int):
	root = tree.root
	min_impacts = np.zeros(impacts_size, dtype=np.float64)
	max_impacts = np.zeros(impacts_size, dtype=np.float64)

	if root in decision_impacts:
		return min_impacts, max_impacts

	if root.type == 'task':
		min_impacts += np.array(root.impact)
		max_impacts += np.array(root.impact)

	elif root.type in ['sequential', 'parallel']:
		for child in root.children:
			child_min_impacts, child_max_impacts = evaluate_min_max_impacts(child, decision_impacts, impacts_size)
			min_impacts += child_min_impacts
			max_impacts += child_max_impacts

	elif root.type in ['choice', 'natural']:
		sx_child_min_impacts, sx_child_max_impacts = evaluate_min_max_impacts(root.children[0], decision_impacts, impacts_size)
		dx_child_min_impacts, dx_child_max_impacts = evaluate_min_max_impacts(root.children[1], decision_impacts, impacts_size)

		if root.type == 'natural':
			print("okayyyyy")
			min_impacts = root.probability * sx_child_min_impacts + (1 - root.probability) * dx_child_min_impacts
			max_impacts = root.probability * sx_child_max_impacts + (1 - root.probability) * dx_child_max_impacts
		else:
			min_impacts = np.minimum(sx_child_min_impacts, dx_child_min_impacts)
			max_impacts = np.maximum(sx_child_max_impacts, dx_child_max_impacts)


	decision_impacts[root] = (min_impacts, max_impacts)

	return min_impacts, max_impacts