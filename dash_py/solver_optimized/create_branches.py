import copy
from solver.tree_lib import CNode
from solver_optimized.states import States, ActivityState, node_info, check_state
from itertools import product


def create_branches(states: States):
	active_branches = []

	node: CNode
	print("create_branches:states:len:" + str(len(states.activityState.keys())))

	for node in list(states.activityState.keys()):
		check_state(node, states)
		# print(f"create_branches: {node_info(node, states)}")
		if ((node.type == 'choice' or node.type == 'natural')
				and states.activityState[node] == ActivityState.ACTIVE
				and states.executed_time[node] == node.max_delay
				and states.activityState[node.childrens[0].root] == ActivityState.WAITING
				and states.activityState[node.childrens[1].root] == ActivityState.WAITING):
			active_branches.append(node)
			print(f"create_branches:active_branches:" + node_info(node, states))


	active_branches_dim = len(active_branches)
	print("create_branches:active branches:" + str(active_branches_dim))
	if active_branches_dim == 0:
		print("create_branches:no active branches")
		return []

	branches_choices = list(product([True, False], repeat=active_branches_dim))
	#print(f"create_branches:cardinality:{active_branches_dim}:combinations:{branches_choices}")

	branches = []
	for branch_choices in branches_choices:
		branch_states = copy.deepcopy(states)

		for i in range(active_branches_dim):
			sxNode = active_branches[i].childrens[0].root
			dxNode = active_branches[i].childrens[1].root

			branch_states.activityState[sxNode] = ActivityState.ACTIVE if branch_choices[i] else ActivityState.WILL_NOT_BE_EXECUTED
			branch_states.activityState[dxNode] = ActivityState.WILL_NOT_BE_EXECUTED if branch_choices[i] else ActivityState.ACTIVE

			#print(f"create_branch: choice: {branch_choices[i]}\n sxNode: {node_info(sxNode, branch_states)}\n dxNode: {node_info(dxNode, branch_states)}\n")

		branches.append(branch_states)

	return branches
