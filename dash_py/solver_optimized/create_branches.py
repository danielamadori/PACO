import copy
from solver.tree_lib import CNode
from solver_optimized.states import States, ActivityState, node_info, states_info
from itertools import product


def create_branches(states: States):
	choice_nature = []
	node: CNode
	for node in list(states.activityState.keys()):
		#TODO: check check_state(node, states)
		# print(f"create_branches: {node_info(node, states)}")
		if ((node.type == 'choice' or node.type == 'natural')
				and states.activityState[node] == ActivityState.ACTIVE
				and states.executed_time[node] == node.max_delay
				and states.activityState[node.childrens[0].root] == ActivityState.WAITING
				and states.activityState[node.childrens[1].root] == ActivityState.WAITING):

			choice_nature.append(node)
			#choice_nature_id.append(node.id)
			print(f"create_branches:active_choice-nature:" + node_info(node, states))

	branches = {}

	#TODO check if is corret to assign the id of a node with the max val
	actual_node_id = str(max(s.id for s in states.activityState.keys() if states.activityState[s] > ActivityState.WAITING))
	choice_nature_dim = len(choice_nature)
	if choice_nature_dim == 0:
		print("create_branches:no_active_choice-nature:id: ", actual_node_id)
		return actual_node_id, branches

	print("create_branches:active_choice-nature:" + str(choice_nature_dim))
	branches_choices = list(product([True, False], repeat=choice_nature_dim))
	#print(f"create_branches:cardinality:{choice_nature_dim}:combinations:{branches_choices}")

	for branch_choices in branches_choices:
		branch_states = copy.deepcopy(states)
		transition_id = ""
		for i in range(choice_nature_dim):
			node = choice_nature[i]

			if branch_choices[i]:
				activeNode = node.childrens[0].root
				inactiveNode = node.childrens[1].root
			else:
				activeNode = node.childrens[1].root
				inactiveNode = node.childrens[0].root

			transition_id += str(node.id) + ":" + str(activeNode.id) + "; "

			branch_states.activityState[activeNode] = ActivityState.ACTIVE
			branch_states.activityState[inactiveNode] = ActivityState.WILL_NOT_BE_EXECUTED

		#Remove "; " from the end
		branches[transition_id[:-2]] = branch_states

	#for transition_id in branches.keys():
	#	print(f"create_branches:branches:id:{transition_id}:\n" + states_info(branches[transition_id]))

	return actual_node_id, branches
