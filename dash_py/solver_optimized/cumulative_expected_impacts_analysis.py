from solver.automaton_graph import AGraph


def get_next_node(graph: AGraph, strategy: dict[tuple, tuple]) -> tuple[AGraph, dict[tuple, tuple]]:
	node = graph.init_node
	#If is a nature consider the node with the biggest CEI_top_down

	for transition, next_child in node.transitions.items():
		decisions = strategy[node.choices_natures]
		check = True
		for t in transition:
			if t[1] not in decisions:
				check = False
				break

		if check:
			return next_child, strategy


def cumulative_expected_impacts_analysis(graph: AGraph, strategy: dict[tuple, tuple]) -> list:
	node = graph.init_node

	if node.is_final_state:
		return [node.cei_top_down]

	next_node, strategy = get_next_node(graph, strategy)

	result = cumulative_expected_impacts_analysis(next_node, strategy)
	result.append(node.cei_top_down)

	return result



