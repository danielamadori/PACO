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

	branches_choices = list(product([True, False], repeat=len(active_branches)))
	print(f"create_branches:cardinality:{len(active_branches)}; combinations: {branches_choices}")

	branches = []
	for branch_choices in branches_choices:
		branch_states = copy.deepcopy(states)

		for i in range(len(active_branches)):
			sxNode = active_branches[i].childrens[0].root
			dxNode = active_branches[i].childrens[1].root
			branch_choice = branch_choices[i]

			branch_states.activityState[sxNode] = ActivityState.ACTIVE if branch_choice else ActivityState.WILL_NOT_BE_EXECUTED
			branch_states.activityState[dxNode] = ActivityState.WILL_NOT_BE_EXECUTED if branch_choice else ActivityState.ACTIVE

			print(f"create_branch: choice: {branch_choice}\n sxNode: {node_info(sxNode, branch_states)}\n dxNode: {node_info(dxNode, branch_states)}\n")

		branches.append(branch_states)

	return branches
