import copy

from solver.tree_lib import CTree, CNode
from solver_optimized.states import States, ActivityState, node_info, states_info
import math


def next_state(tree: CTree, states: States, k: int):
	root: CNode = tree.root

	#check_state(root, states)
	#print(f"next_state: " + node_info(root, states))

	if root.type == 'task':
		#print("next_state:Task: " + node_info(root, states))

		remaining_time = root.duration - states.executed_time[root]
		if remaining_time >= k:
			#print(f"next_state:Task:remaining_time >= k: {remaining_time} >= {k}")
			return (States(root,
						ActivityState.ACTIVE if remaining_time > k else ActivityState.COMPLETED_WIHTOUT_PASSING_OVER,
						states.executed_time[root] + k),
					0)

		states.activityState[root] = ActivityState.COMPLETED
		#print(f"next_state:Task:remaining_time < k: {remaining_time} < {k}: ActivityCompleted!")
		return (States(root, ActivityState.COMPLETED, root.duration),
				states.executed_time[root] + k - root.duration)

	leftSubTree = root.childrens[0]
	rightSubTree = root.childrens[1]

	if root.type == 'choice' or root.type == 'natural':
		childSx = states.activityState[leftSubTree.root] >= ActivityState.ACTIVE
		childDx = states.activityState[rightSubTree.root] >= ActivityState.ACTIVE
		if childSx or childDx:
			childTree = leftSubTree if childSx else rightSubTree
			childStates, childK = next_state(childTree, states, k)

			childStates.activityState[root] = childStates.activityState[childTree.root]
			childStates.executed_time[root] = states.executed_time[root] + k - childK
			return childStates, childK

		if root.type == 'natural':
			if k > 0:
				raise Exception("ExceedingStepsException:Natural")
			#print(f"next_state:Natural:k: 0")
			return States(root, ActivityState.ACTIVE, 0), 0
		else:
			if states.executed_time[root] + k > root.max_delay:
				raise Exception("ExceedingStepsException:Choice")

			#print(f"next_state:Choice:remaining_time == k: k={k}")
			return (States(root,
						ActivityState.ACTIVE,
						states.executed_time[root] + k),
					0)

	leftStates = States()
	rightStates = States()

	if root.type == 'sequential':
		#print("next_state:Sequential: " + node_info(root, states))
		leftK = k
		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			leftStates, leftK = next_state(leftSubTree, states, k)

			#print(f"next_state:Sequential: {node_info(root, states)} leftK: {leftK}")
			#print("next_state:Sequential:LeftStates:")
			#print_states(leftStates)

			if leftStates.activityState[leftSubTree.root] == ActivityState.ACTIVE:
				leftStates.activityState[root] = ActivityState.ACTIVE
				return leftStates, leftK

		rightStates, rightK = next_state(rightSubTree, states, leftK)
		#print(f"next_state:Sequential: {node_info(root, states)} rightK: {rightK}")
		#print("Sequential:right " + node_info(rightSubTree.root, states))
		#print(f"Sequential:right:{rightCl} {rightK}")

		#TODO: Union of the left and right states
		leftStates.update(rightStates)
		#leftStates.activityState.update(rightStates.activityState)
		#leftStates.executed_time.update(rightStates.executed_time)

		leftStates.activityState[root] = rightStates.activityState[rightSubTree.root]
		leftStates.executed_time[root] = states.executed_time[root] + k - rightK

		return leftStates, rightK

	if root.type == 'parallel':
		#print("next_state:Parallel: " + node_info(root, states))
		leftK = rightK = math.inf

		#print("next_state:Parallel:LeftCheck ")# + node_info(leftSubTree.root, states))
		if states.activityState[leftSubTree.root] != ActivityState.COMPLETED:
			#print("next_state:Parallel:Left")
			leftStates, leftK = next_state(leftSubTree, states, k)
			#print("next_state:Parallel:LeftStates:")
			#print_states(leftStates)

		#print("next_state:Parallel:RightCheck ")# + node_info(rightSubTree.root, states))
		if states.activityState[rightSubTree.root] != ActivityState.COMPLETED:
			#print("next_state:Parallel:Right")
			rightStates, rightK = next_state(rightSubTree, states, k)
			#print("next_state:Parallel:RightStates:")
			#print_states(rightStates)

		if (leftStates.activityState[leftSubTree.root] == ActivityState.ACTIVE or
			rightStates.activityState[rightSubTree.root] == ActivityState.ACTIVE):

			status = ActivityState.ACTIVE
		elif (leftStates.activityState[leftSubTree.root] == ActivityState.COMPLETED and
			rightStates.activityState[rightSubTree.root] == ActivityState.COMPLETED):

			status = ActivityState.COMPLETED
		else:
			status = ActivityState.COMPLETED_WIHTOUT_PASSING_OVER

		# TODO: Union of the left and right states
		leftStates.update(rightStates)
		#leftStates.activityState.update(rightStates.activityState)
		#leftStates.executed_time.update(rightStates.executed_time)

		leftStates.activityState[root] = status
		leftStates.executed_time[root] = states.executed_time[root] + k - min(leftK, rightK)

		return leftStates, min(leftK, rightK)

	print(f"Unknown case: {root}")
	raise Exception(root)
