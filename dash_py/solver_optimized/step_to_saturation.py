from solver.tree_lib import CTree, CNode
from solver_optimized.states import States, ActivityState, node_info
import math


def steps_to_saturation(tree: CTree, states: States):
	root: CNode = tree.root

	#print("step_to_saturation: " + node_info(root, states))

	if root.type == 'task':
		remaining_time = root.duration - states.executed_time[root]
		#print("step_to_saturation:Task:remaining_time: ", remaining_time)
		return remaining_time

	leftSubTree = root.childrens[0]
	rightSubTree = root.childrens[1]
	#TODO: check check_state(root, states)

	if root.type == 'natural' or root.type == 'choice':
		# print("step_to_saturation:Natural/Choice: " + node_info(root, states))
		# print("step_to_saturation:Natural/Choice:Left: " + node_info(leftSubTree.root, states))
		# print("step_to_saturation:Natural/Choice:Right: " + node_info(rightSubTree.root, states))

		if states.activityState[leftSubTree.root] == ActivityState.ACTIVE:
			return steps_to_saturation(leftSubTree, states)
		if states.activityState[rightSubTree.root] == ActivityState.ACTIVE:
			return steps_to_saturation(rightSubTree, states)

		remaining_time = 0
		if root.type == 'choice':
			remaining_time = root.max_delay - states.executed_time[root]
		#print("step_to_saturation:Natural/Choice:remaining_time: ", remaining_time)
		return remaining_time


	if root.type == 'sequential':
		#print("step_to_saturation:Sequential: " + node_info(root, states))
		#print("step_to_saturation:Sequential:Left: " + node_info(leftSubTree.root, states))
		#print("step_to_saturation:Sequential:Right: " + node_info(rightSubTree.root, states))

		# If the activity state of left child is in active mode (it means that the activity is currently ongoing)
		if states.activityState[rightSubTree.root] == ActivityState.ACTIVE:
			return steps_to_saturation(rightSubTree, states)
		else:
			return steps_to_saturation(leftSubTree, states)

	if root.type == 'parallel':
		#print("step_to_saturation:Parallel:  " + node_info(root, states))
		#print("step_to_saturation:Parallel:Left: " + node_info(leftSubTree.root, states))
		#print("step_to_saturation:Parallel:Right: " + node_info(rightSubTree.root, states))
		dur_left = math.inf
		dur_right = math.inf
		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			dur_left = steps_to_saturation(leftSubTree, states)
		if states.activityState[rightSubTree.root] != ActivityState.COMPLETED:
			dur_right = steps_to_saturation(rightSubTree, states)

		return min(dur_left, dur_right)

	print("Error: Invalid root type!")
	raise Exception(root)
