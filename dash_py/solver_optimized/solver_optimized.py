import random

import numpy as np

from solver.automaton_graph import AGraph, ANode
from solver_optimized.states import states_info, States, ActivityState


def add_cei_to_automa(automa: AGraph):
	node = automa.init_node

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
			node.cei_bottom_up += add_cei_to_automa(subGraph)

	return node.cei_bottom_up


def compare_bound(cei, bound: []):
	for i in range(len(bound)):
		if bound[i] != cei[i]:
			return cei[i] - bound[i]

	return 0


def choose(children: [], method: str = 'random'):
	# Randomly choose a child
	if method == 'random':
		return children[random.randint(0, len(children) - 1)]

	#TODO
	return children[random.randint(0, len(children) - 1)]

def found_strategy(graph: AGraph, bound: []):
	node = graph.init_node

	if compare_bound(node.cei_top_down, bound) > 0:#a > b
		print("a > b")
		return False, [graph], 0#TODO: 0 is not the correct value
	if compare_bound(node.cei_bottom_up, bound) <= 0:#a <= b
		print("a <= b")
		return True, [graph], node.cei_bottom_up

	if node.node_type == 'choice':
		children = list(node.transitions.values())
		print("choice")
		min_cei_bottom_up = 0
		min_graphs = []
		while len(children) > 0:
			child = choose(children, bound)
			children.remove(child)

			founded, sol, cei_bottom_up = found_strategy(child, bound)
			print("end choice:cei_bottom_up:", cei_bottom_up)
			if founded:
				return True, sol, cei_bottom_up

			if cei_bottom_up < min_cei_bottom_up:
				min_cei_bottom_up = cei_bottom_up
				min_graphs = sol

		print("end choice:failed:min_cei_bottom_up:", min_cei_bottom_up)
		return False, min_graphs, min_cei_bottom_up

	if node.node_type == 'natural':
		print("natural")
		sum_cei_bottom_up = 0
		frontier = []
		for child in node.transitions.values():
			founded, sol, cei_bottom_up = found_strategy(child, bound)

			if not founded:
				return False, graph, cei_bottom_up

			sum_cei_bottom_up += cei_bottom_up
			frontier.append(sol)
			print("end nature:sum_cei_bottom_up:", sum_cei_bottom_up)

		return compare_bound(sum_cei_bottom_up, bound) <= 0, frontier, sum_cei_bottom_up

	raise Exception("Unknown case")