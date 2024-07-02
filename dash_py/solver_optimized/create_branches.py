import copy
from solver.tree_lib import CNode
from solver_optimized.states import States, ActivityState, node_info, states_info
from itertools import product


def create_branches(states: States) -> dict:
	choice_nature = []
	node: CNode
	for node in list(states.activityState.keys()):
		if ((node.type == 'choice' or node.type == 'natural')
				and states.activityState[node] == ActivityState.ACTIVE
				and states.executed_time[node] == node.max_delay
				and states.activityState[node.childrens[0].root] == ActivityState.WAITING
				and states.activityState[node.childrens[1].root] == ActivityState.WAITING):

			choice_nature.append(node)
			print(f"create_branches:active_choice-nature:" + node_info(node, states))

	branches = {}

	if len(choice_nature) == 0:
		return branches

	branches_choices = list(product([True, False], repeat=len(choice_nature)))
	#print(f"create_branches:cardinality:{choice_nature_dim}:combinations:{branches_choices}")
	for branch_choices in branches_choices:
		branch_states = States() # Original code: branch_states = copy.deepcopy(states)
		transition_id = ""
		for i in range(len(choice_nature)):
			node = choice_nature[i]

			if branch_choices[i]:
				activeNode = node.childrens[0].root
				inactiveNode = node.childrens[1].root
			else:
				activeNode = node.childrens[1].root
				inactiveNode = node.childrens[0].root

			transition_id += str(node.id) + ":" + str(activeNode.id) + ";"

			branch_states.activityState[activeNode] = ActivityState.ACTIVE
			branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED

		branches[transition_id] = branch_states

	#for transition_id in branches.keys():
	#	print(f"create_branches:branches:id:{transition_id}:\n" + states_info(branches[transition_id]))

	return branches
