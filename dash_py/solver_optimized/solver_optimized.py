import numpy as np

from solver.automaton_graph import AGraph
from solver_optimized.states import states_info


def add_cei_to_automa(automa: AGraph):
	node = automa.init_node

	node.cei_bottom_up = np.zeros(len(node.impacts)) #Useless, already done in the constructor
	node.cei_top_down = node.probability * np.array(node.impacts)

	print(states_info(node.states))
	print("cei_bottom_up: " + str(node.cei_bottom_up) + " cei_top_down: " + str(node.cei_top_down))
	print("probability: " + str(node.probability) + " impacts: " + str(node.impacts) + "\n")

	for subGraph in node.transitions.values():
		child = subGraph.init_node

		if child.is_final_state:
			child.cei_bottom_up = child.cei_top_down = child.probability * np.array(child.impacts)
			node.cei_bottom_up += child.cei_bottom_up
		else:
			node.cei_bottom_up += add_cei_to_automa(subGraph)

	return node.cei_bottom_up


