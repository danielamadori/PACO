import copy

import pydot

from solver.automaton_graph import AGraph, ANode
from solver.tree_lib import CTree
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, states_info, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation


def create_automa(region_tree: CTree, states: States, automa: AGraph, node_id: str = ""):
	branches = {}

	while len(branches) < 2 and states.activityState[region_tree.root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("step_to_saturation:")
		#print_states(states)
		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k)
		#print_states(states)

		#print("next_state:")
		states, k = next_state(region_tree, states, k)
		#print('next_state:k:', k)
		#print_states(states)
		#print("create_branches:")
		actual_id, branches = create_branches(states)
		#print("Branches:" + str(len(branches)))
		#print("Root activity state: ", states.activityState[region_tree.root])
		#print_states(states)

	if node_id == "":# It happens just for the root
		node_id = actual_id

	node = AGraph(ANode(
		states=states,
		process_ids=node_id,
		is_final_state=states.activityState[region_tree.root] == ActivityState.COMPLETED))

	automa.init_node.add_transition(node)

	for next_node_id in branches.keys():
		branch = branches[next_node_id]
		print(f"create_automa:next_node_id:{next_node_id}:\n" + states_info(branch))
		create_automa(region_tree, branch, node, next_node_id)
