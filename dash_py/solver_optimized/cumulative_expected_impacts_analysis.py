from solver.automaton_graph import AGraph
from solver.tree_lib import CTree


def get_next_node(graph: AGraph, decisions: list[CTree]):
	node = graph.init_node
	#If is a nature consider the node with the biggest CEI_top_down

	#

	return node, decisions

def cumulative_expected_impacts_analysis(graph: AGraph, decisions: list[CTree]):
	node = graph.init_node

	if node.is_final_state:
		return [node.cei_top_down]

	return cumulative_expected_impacts_analysis(get_next_node(graph, decisions)).append(node.cei_top_down)



