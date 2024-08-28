import copy
import numpy as np
from solver_optimized.execution_tree import ExecutionTree

'''
def evaluate_cumulative_expected_impacts(solution_tree: SolutionTree):
	solution_tree.root.cei_top_down = solution_tree.root.probability * np.array(solution_tree.root.impacts)
	# solution_tree.root.cei_bottom_up = np.zeros(len(solution_tree.root.impacts))
	# Useless, already done in the constructor

	if solution_tree.root.is_final_state:
		solution_tree.root.cei_bottom_up = solution_tree.root.cei_top_down
		return

	for sub_tree in solution_tree.root.transitions.values():
		evaluate_cumulative_expected_impacts(sub_tree)
		solution_tree.root.cei_bottom_up += sub_tree.root.child.bottom_up
'''


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


'''
def worst_impacts(tree: CTree, states: States):
	root = tree.root
	#print(node_info(root, states))
	if root in states.activityState and states.activityState[root] == ActivityState.WILL_NOT_BE_EXECUTED:
		return States()

	if root.type == 'task':
		return States(root, ActivityState.COMPLETED, root.duration)

	if root.type in ['sequential', 'parallel']:
		result = States()
		for child in root.childrens:
			result.update(worst_impacts(child, states))
		return result

	if root.type in ['choice', 'natural']:
		for child in root.childrens:
			#print(node_info(child.root, states))
			if child.root in states.activityState and states.activityState[child.root] >= ActivityState.ACTIVE:
				return worst_impacts(child, states)

	return States()
'''