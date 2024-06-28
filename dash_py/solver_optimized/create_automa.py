import copy
import time

from solver.automaton_graph import AGraph, ANode
from solver.tree_lib import CTree, CNode
from solver_optimized.create_branches import create_branches
from solver_optimized.next_state import next_state
from solver_optimized.states import States, states_info, ActivityState
from solver_optimized.step_to_saturation import steps_to_saturation
import re


def create_automa(region_tree: CTree) -> AGraph:
	branches, states = create_current_automa_state(
		region_tree.root, region_tree,
		States(region_tree.root, ActivityState.WAITING, 0))

	current_node_id = re.sub(r':[^;]*;', ';', list(branches.keys())[0])
	print("create_automa:root:" + current_node_id)

	automa = AGraph(ANode(
		states=states,
		process_ids=current_node_id,
		is_final_state=states.activityState[region_tree.root] == ActivityState.COMPLETED)
	)

	for next_node_id in branches.keys():
		branch = states
		branch.update(branches[next_node_id])
		print(f"create_automa:next_node_id:{next_node_id}:\n" + states_info(branch))
		create_next_automa_state(region_tree.root, region_tree, branch, automa, next_node_id)

	return automa


def create_current_automa_state(root: CNode, region_tree: CTree, states: States):
	branches = {}
	i = 0
	while len(branches) == 0 and states.activityState[root] < ActivityState.COMPLETED:
		#print("step_to_saturation:")
		#print("start:", states_info(states))

		k = steps_to_saturation(region_tree, states)
		#print('step_to_saturation:k:', k, states_info(states))

		states, k = next_state(region_tree, states, k)
		#print('next_state:k:', k, states_info(states))

		branches = create_branches(states)
		#if len(branches) > 0:
			#print("create_branches:", states_info(states))


	#print("Branches:" + str(len(branches)))
	#print("Root activity state: ", states.activityState[region_tree.root], states_info(states))

	return branches, states


def create_next_automa_state(root: CNode, region_tree: CTree, states: States, automa: AGraph, next_node_id: str):
	branches, childStates = create_current_automa_state(root, region_tree, copy.deepcopy(states))

	print("create_next_automa_state:childStates:" + states_info(childStates))
	states.update(childStates)
	print("create_next_automa_state:states:" + states_info(states))

	next_node = AGraph(ANode(
		states=states,
		process_ids=next_node_id,
		is_final_state=states.activityState[region_tree.root] == ActivityState.COMPLETED)
	)

	automa.init_node.add_transition(next_node)

	for next_node_id in branches.keys():
		branch = copy.deepcopy(states)
		branch.update(branches[next_node_id])
		print("create_automa:next_node_id:" + next_node_id + states_info(branch))
		create_next_automa_state(root, region_tree, branch, next_node, next_node_id)
