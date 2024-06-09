import copy
from solver.tree_lib import CNode
from solver_optimized.states import States, ActivityState, node_info
from itertools import product


def create_branches(states: States):
	active_branches = []

	node: CNode
	nodes = states.activityState.keys()
	for node in nodes:
		# check_state(node, states)
		# print(f"create_branches: {node_info(node, states)}")
		if (node.type == 'choice' or node.type == 'natural'
				and states.activityState[node] == ActivityState.ACTIVE
				and states.executed_time[node] == node.max_delay
				and states.activityState[node.childrens[0].root] == ActivityState.WAITING
				and states.activityState[node.childrens[1].root] == ActivityState.WAITING):
			active_branches.append(node)
			print(f"create_branches:active_branches: " + node_info(node, states))

	combinations = list(product([True, False], repeat=len(active_branches)))
	print(f"create_branches:cardinality:{len(active_branches)}; combinations: {combinations}")

	branches = []
	for combination in combinations:
		branches_states = create_branch(combination, active_branches, copy.deepcopy(states))
		branches.append(branches_states)

	return branches


def create_branch(choices, active_branches: [], states: States):
	'''
	node: CNode
	for node in active_branches:
		print(f"create_branch: choice: {}; node: {node_info(node, states)}")
		states.activityState[node] = ActivityState.COMPLETED
	'''
	for i in range(len(active_branches)):
		sxNode = active_branches[i].childrens[0].root
		dxNode = active_branches[i].childrens[1].root
		choice = choices[i]

		if choice:
			states.activityState[sxNode] = ActivityState.ACTIVE
			states.activityState[dxNode] = ActivityState.WILL_NOT_BE_EXECUTED
		else:
			states.activityState[sxNode] = ActivityState.WILL_NOT_BE_EXECUTED
			states.activityState[dxNode] = ActivityState.ACTIVE

		print(
			f"create_branch: choice: {choice}\n sxNode: {node_info(sxNode, states)}\n dxNode: {node_info(dxNode, states)}\n")

	return states
