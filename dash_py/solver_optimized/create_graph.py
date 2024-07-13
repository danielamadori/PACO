import copy
import numpy as np
from solver.tree_lib import CTree
from solver.automaton_graph import AGraph, ANode
from solver_optimized.saturate_graph_node import saturate_graph_node
from solver_optimized.states import States, states_info, ActivityState


def graph_node_info(node: ANode) -> str:
	result = "decisions:<"
	for n in node.decisions:
		result += str(n.id) + ";"

	result = result[:-1] + ">:choices_natures:<"
	tmp = ""
	for n in node.choices_natures:
		tmp += str(n.id) + ";"

	return result + tmp[:-1] + ">:status:" + states_info(node.states)


def create_graph(region_tree: CTree) -> (AGraph, list[AGraph]):
	states, choices_natures, branches = saturate_graph_node(region_tree, States(region_tree.root, ActivityState.WAITING, 0))

	graph = AGraph(ANode(
		states=states,
		decisions=(region_tree.root,),
		choices_natures=choices_natures,
		is_final_state=states.activityState[region_tree.root] >= ActivityState.COMPLETED)
	)

	print("create_graph:", graph_node_info(graph.init_node))

	final_states = []
	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		final_states.extend(create_graph_node(region_tree, decisions, branch, graph))

	return graph, final_states


def create_graph_node(region_tree: CTree, decisions: tuple, states: States, graph: AGraph) -> list[AGraph]:
	saturatedStates, choices_natures, branches = saturate_graph_node(region_tree, states)
	states.update(saturatedStates)
	#print("create_graph_node:start_id:" + str(start_ids) + ":exit_id:" + str(exit_id) + states_info(states))

	is_final_state = states.activityState[region_tree.root] >= ActivityState.COMPLETED
	final_states = []
	next_node = AGraph(ANode(
		states=states,
		decisions=decisions,
		choices_natures=choices_natures,
		is_final_state=is_final_state)
	)

	print("create_graph_node:", graph_node_info(next_node.init_node))

	if is_final_state:
		final_states.append(next_node)

	graph.init_node.add_transition(decisions, next_node)

	for decisions, branch_states in branches.items():
		branch = copy.deepcopy(states)
		branch.update(branch_states)
		final_states.extend(create_graph_node(region_tree, decisions, branch, next_node))

	return final_states

def evaluate_cumulative_expected_impacts(graph: AGraph) -> np.ndarray:
	node = graph.init_node

	#print(node.impacts)
	node.cei_bottom_up = np.zeros(len(node.impacts)) #Useless, already done in the constructor
	node.cei_top_down = node.probability * np.array(node.impacts)

	#print(states_info(node.states))
	#print("cei_bottom_up: " + str(node.cei_bottom_up) + " cei_top_down: " + str(node.cei_top_down))
	#print("probability: " + str(node.probability) + " impacts: " + str(node.impacts) + "\n")

	for subGraph in node.transitions.values():
		child = subGraph.init_node

		if child.is_final_state:
			child.cei_bottom_up = child.cei_top_down = child.probability * np.array(child.impacts)
			node.cei_bottom_up += child.cei_bottom_up
		else:
			node.cei_bottom_up += evaluate_cumulative_expected_impacts(subGraph)

	return node.cei_bottom_up

