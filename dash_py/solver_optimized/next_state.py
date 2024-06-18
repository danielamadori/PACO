import copy

from solver.tree_lib import CTree, CNode
from solver_optimized.states import States, ActivityState, check_state, node_info, print_states
import math


def next_state(tree: CTree, states: States, k: int):
	root: CNode = tree.root

	#check_state(root, states)
	print(f"next_state: " + node_info(root, states))

	if root.type == 'task':
		remaining_time = root.duration - states.executed_time[root]
		#print("next_state:Task: " + node_info(root, states))
		if remaining_time > k:
			states.activityState[root] = ActivityState.ACTIVE
			states.executed_time[root] += k

			#print(f"next_state:Task:remaining_time > k: {remaining_time} > {k}")
			return states, 0, False

		states.activityState[root] = ActivityState.COMPLETED
		#print(f"next_state:Task:remaining_time <= k: {remaining_time} <= {k}: ActivityCompleted!")
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
			return states, 0, False

		print(f"next_state:Choice/Nature:remaining_time > k: {remaining_time} > {k}")
		print("Choice/Natural: " + node_info(root, states) + " k: " + str(k))
		raise Exception(root)

	leftStates = States(root, ActivityState.ACTIVE, 0)
	leftStates.add(leftSubTree.root, ActivityState.WAITING, 0)
	rightStates = States(root, ActivityState.ACTIVE, 0)
	rightStates.add(rightSubTree.root, ActivityState.WAITING, 0)

	if root.type == 'sequential':
		leftK = k
		leftCl = True

		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			leftStates, leftK, leftCl = next_state(leftSubTree, states, k)

		#print(f"next_state:Sequential: {node_info(root, states)} leftK: {leftK} leftCl: {leftCl}")
		#print("next_state:Sequential:LeftStates:")
		#print_states(leftStates)

		if not leftCl:
			#print("next_state:Sequential:Not leftCl")
			leftStates.activityState[root] = ActivityState.ACTIVE
			return leftStates, leftK, False

		if leftK == 0:
			#print("next_state:Sequential:leftK: 0")
			leftStates.activityState[root] = ActivityState.ACTIVE
			leftStates.activityState[rightSubTree.root] = ActivityState.ACTIVE
			return leftStates, leftK, False


		rightStates, rightK, rightCl = next_state(rightSubTree, states, leftK)
		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK} rightCl: {rightCl}")
		#print("Sequential:right " + node_info(rightSubTree.root, states))
		#print(f"Sequential:right:{rightCl} {rightK}")

		if not rightCl:
			#print("next_state:Sequential:Not rightCl")
			rightStates.activityState[root] = ActivityState.ACTIVE
			rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
			return rightStates, rightK, False

		if rightK == 0:
			#print("next_state:Sequential:rightK: 0")
			# TODO: check
			#rightStates.activityState[root] = ActivityState.ACTIVE
			#rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
			#return rightStates, rightK, True

			rightStates.activityState[root] = ActivityState.COMPLETED
			rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED
			return rightStates, 0, True

		# Not original
		print("next_state:Sequential:Exception" + node_info(root, states))
		raise Exception(root)
		# End not original

		rightStates.activityState[root] = ActivityState.COMPLETED
		rightStates.activityState[leftSubTree.root] = ActivityState.COMPLETED

		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK} rightCl: {rightCl}")
		return rightStates, rightK, True

	if root.type == 'parallel':
		leftK = rightK = math.inf
		leftCl = rightCl = True

		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			leftStates, leftK, leftCl = next_state(leftSubTree, states, k)
			#print("next_state:Parallel:LeftStates:")
			#print_states(leftStates)

		if states.activityState[rightSubTree.root] != ActivityState.COMPLETED:
			rightStates, rightK, rightCl = next_state(rightSubTree, states, k)
			#print("next_state:Parallel:RightStates:")
			#print_states(rightStates)

		if leftK != math.inf and rightK != math.inf:
			if leftCl and rightCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, min(leftK, rightK), True

			if leftCl:
				states.update(rightStates)
				states.activityState[root] = ActivityState.ACTIVE
				states.activityState[leftSubTree.root] = ActivityState.COMPLETED
				return states, rightK, False

			if rightCl:
				states.update(leftStates)
				states.activityState[root] = ActivityState.ACTIVE
				states.activityState[rightSubTree.root] = ActivityState.COMPLETED
				return states, leftK, False

			#print(f"next_state:Parallel:Both branches are active: ! {leftCl} {rightCl}")
			# Union of the two states
			states.update(leftStates)
			states.update(rightStates)
			states.activityState[root] = ActivityState.ACTIVE

			#print(f"minK: {min(leftK, rightK)}") # TODO: check if minK == 0; if true put 0 instead
			return states, min(leftK, rightK), False

		if leftK != math.inf:
			if leftCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, leftK, True

			states.update(leftStates)
			states.activityState[root] = ActivityState.ACTIVE
			states.activityState[rightSubTree.root] = ActivityState.COMPLETED

			return states, leftK, False

		if rightK != math.inf:
			if rightCl:
				states.activityState[root] = ActivityState.COMPLETED
				states.executed_time[root] = 0
				return states, rightK, True

			states.update(rightStates)
			states.activityState[root] = ActivityState.ACTIVE
			states.activityState[leftSubTree.root] = ActivityState.COMPLETED

			return states, rightK, False

		print("next_state:Parallel:Exception" + node_info(root, states))
		raise Exception(root)

	print(f"Unknown case: {root}")
	raise Exception(root)
