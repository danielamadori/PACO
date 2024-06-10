import copy

from solver.tree_lib import CTree, CNode
from solver_optimized.states import States, ActivityState, check_state, node_info, print_states
import math


def next_state(tree: CTree, states: States, k: int):
	root: CNode = tree.root

	#check_state(root, states)
	#print(f"next_state: " + node_info(root, states))

	if root.type == 'task':
		remaining_time = root.duration - states.executed_time[root]
		#print("next_state:Task: " + node_info(root, states))
		if remaining_time >= k:
			#print(f"next_state:Task:remaining_time >= k: {remaining_time} >= {k} ; Remaining time T/F: {remaining_time == k}")
			states.activityState[root] = ActivityState.ACTIVE
			states.executed_time[root] += k

			return states, 0, remaining_time == k

		states.activityState[root] = ActivityState.COMPLETED
		#print(f"next_state:Task:remaining_time < k: {remaining_time} < {k}; ActivityCompleted!")
		return states, states.executed_time[root] + k - root.duration, True

	leftSubTree = root.childrens[0]
	rightSubTree = root.childrens[1]

	if root.type == 'choice' or root.type == 'natural':
		childSx = states.activityState[leftSubTree.root] >= ActivityState.ACTIVE
		childDx = states.activityState[rightSubTree.root] >= ActivityState.ACTIVE
		if childSx or childDx:
			childTree = leftSubTree if childSx else rightSubTree
			childStates, childK, childCl = next_state(childTree, copy.deepcopy(states), k)

			if childStates.activityState[childTree.root] == ActivityState.COMPLETED:
				childStates.activityState[root] = ActivityState.COMPLETED

			return childStates, childK, childCl

		remaining_time = root.max_delay - states.executed_time[root]
		if root.type == 'choice' and remaining_time < k:
			#print(f"next_state:Choice:remaining_time < k: {remaining_time} <= {k}")
			states.executed_time[root] += k
			return states, 0, False

		if remaining_time == k:
			#print(f"next_state:Choice/Nature:remaining_time == k: {remaining_time} == {k}")
			states.activityState[root] = ActivityState.ACTIVE
			states.executed_time[root] += k
			return states, 0, True # TODO check if True or False

		print(f"next_state:Choice/Nature:remaining_time > k: {remaining_time} > {k}")
		print("Choice/Natural: " + node_info(root, states) + " k: " + str(k))
		raise Exception(root)

	if root.type == 'sequential':
		#leftStates = States(leftSubTree.root, ActivityState.WAITING, 0)
		leftStates = copy.deepcopy(states)

		leftK = k
		leftCl = True

		if states.activityState[root] != ActivityState.COMPLETED:
			leftStates, leftK, leftCl = next_state(leftSubTree, states, k)

		#print(f"next_state:Sequential: {node_info(root, states)} leftK: {leftK} leftCl: {leftCl}")
		#print("next_state:Sequential:LeftStates:")
		#print_states(leftStates)

		if not leftCl:
			#print("next_state:Sequential:Not leftCl")
			leftStates.activityState[root] = ActivityState.ACTIVE
			return leftStates, leftK, leftCl

		if leftK == 0:
			#print("next_state:Sequential:leftK: 0")
			leftStates.activityState[root] = ActivityState.ACTIVE
			leftStates.activityState[rightSubTree.root] = ActivityState.ACTIVE
			return leftStates, leftK, False

		rightStates, rightK, rightCl = next_state(rightSubTree, copy.deepcopy(states), leftK)
		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK} rightCl: {rightCl}")

		if not rightCl:
			#print("next_state:Sequential:Not rightCl")
			rightStates.activityState[root] = ActivityState.ACTIVE
			rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
			return rightStates, rightK, rightCl

		if rightK == 0:
			#print("next_state:Sequential:rightK: 0")
			rightStates.activityState[root] = ActivityState.ACTIVE
			rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
			return rightStates, rightK, True

		rightStates.activityState[root] = ActivityState.COMPLETED
		rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED

		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK} rightCl: {rightCl}")
		return rightStates, rightK, True

	if root.type == 'parallel':
		# leftStates = States(leftSubTree.root, ActivityState.WAITING, 0)
		# rightStates = States(rightSubTree.root, ActivityState.WAITING, 0)
		leftStates = copy.deepcopy(states)
		rightStates = copy.deepcopy(states)

		leftK = rightK = math.inf
		leftCl = rightCl = True

		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			leftStates, leftK, leftCl = next_state(leftSubTree, leftStates, k)
			print("next_state:Parallel:LeftStates:")
			print_states(leftStates)

		if states.activityState[rightSubTree.root] != ActivityState.COMPLETED:
			rightStates, rightK, rightCl = next_state(rightSubTree, rightStates, k)
			print("next_state:Parallel:RightStates:")
			print_states(rightStates)

		if leftK != math.inf and rightK != math.inf:
			maxK = max(leftK, rightK)

			if leftCl and rightCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, maxK - k, True

			if leftCl:
				rightStates.activityState[root] = ActivityState.ACTIVE
				rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
				return rightStates, k - rightK, False

			if rightCl:
				leftStates.activityState[root] = ActivityState.ACTIVE
				leftStates.activityState[rightSubTree.root] = ActivityState.COMPLETED
				return leftStates, k - leftK, False

			# Union of the two states
			leftStates.activityState.update(rightStates.activityState)
			leftStates.activityState[root] = ActivityState.ACTIVE
			leftStates.executed_time.update(rightStates.executed_time)

			# TODO: check if k - maxK == 0; if true put 0 instead
			# print(f"k-maxK: {k - maxK}")
			return leftStates, k - maxK, False

		if leftK != math.inf:
			if leftCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, k - leftK, True

			leftStates.activityState[root] = ActivityState.ACTIVE
			leftStates.activityState[rightSubTree.root] = ActivityState.COMPLETED

			return leftStates, k - leftK, False

		if rightK != math.inf:
			if rightCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, k - rightK, True

			rightStates.activityState[root] = ActivityState.ACTIVE
			rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED

			return rightStates, k - rightK, False

		raise Exception(root)

	print(f"Unknown case: {root}")
	raise Exception(root)
