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

def pick(frontier: list,  method: str = 'random'):
	if method == 'random':
		return frontier[random.randint(0, len(frontier) - 1)]

	#TODO
	return frontier[random.randint(0, len(frontier) - 1)]

def found_strategy2(graph: AGraph, bound: []):
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

			founded, sol, cei_bottom_up = found_strategy2(child, bound)
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
			founded, sol, cei_bottom_up = found_strategy2(child, bound)

			if not founded:
				return False, graph, cei_bottom_up

			sum_cei_bottom_up += cei_bottom_up
			frontier.append(sol)
			print("end nature:sum_cei_bottom_up:", sum_cei_bottom_up)

		return compare_bound(sum_cei_bottom_up, bound) <= 0, frontier, sum_cei_bottom_up

	raise Exception("Unknown case")


def nature_clousure(subgraph: AGraph):
	if subgraph.init_node.node_type == 'natural':
		new_frontier = []
		for child in subgraph.init_node.transitions.values():
			new_frontier.append(nature_clousure(child))

		return new_frontier

	return subgraph

def frontier_info(frontier: list):
	result = "["
	for graph in frontier:
		result += str(graph.init_node) + ", "
	return result[:-2] + "]"

def found_strategy(frontier: list, bound: list):
	print("frontier: ", frontier_info(frontier))

	frontier_value_bottom_up = sum(graph.init_node.cei_bottom_up for graph in frontier)
	if compare_bound(frontier_value_bottom_up, bound) <= 0:
		print("Win")
		return frontier, [frontier_value_bottom_up]

	frontier_value_top_down = sum(graph.init_node.cei_top_down for graph in frontier)
	if (compare_bound(frontier_value_top_down, bound) > 0 or
			all(graph.init_node.is_final_state for graph in frontier)):
		print("Failed top_down: not a valid choose", compare_bound(frontier_value_top_down, bound) > 0)
		return None, [frontier_value_top_down]

	graph = pick([graph for graph in frontier if not graph.init_node.is_final_state])
	frontier.remove(graph)

	failed = []
	tested = []
	while len(tested) < len(graph.init_node.transitions.values()):
		new_frontier = [subgraph for subgraph in graph.init_node.transitions.values() if subgraph not in tested]
		print("new_frontier: ", frontier_info(new_frontier))

		subgraph = pick(new_frontier)
		#subgraph = nature_clousure(subgraph)

		new_frontier = frontier.copy()
		new_frontier.append(subgraph)
		print("new_frontier:after_pick: ", frontier_info(new_frontier))
		r, fvs = found_strategy(new_frontier, bound)
		print("end_rec")
		if r is None:
			failed.append(fvs)
			tested.append(subgraph)
		else:
			return r, fvs

		print("tested", frontier_info(tested))
		print("n.children", frontier_info(graph.init_node.transitions.values()))

	print("Failed: No choose left")
	return None, failed










