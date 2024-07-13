import random
from solver.automaton_graph import AGraph


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


def pick(frontier: list[AGraph],  method: str = 'random'):

	return frontier[random.randint(0, len(frontier) - 1)]


def natural_clousure(graph: AGraph, chose_graph: AGraph):
	node = graph.init_node
	chose_child = chose_graph.init_node
	nats = [node for node in node.choices_natures if node.type == 'natural']
	frontier = []
	#print("nat_nodes: ", [node.id for node in nat_nodes], "chose_id: ", [node.id for node in chose_id])

	for transition, next_child in node.transitions.items():
		check_nat = len(nats) == 0
		check_choice = len(chose_child.decisions) != 0
		for t in transition:
			#print("t: ", t[0].type, t[0].id, t[1].id)
			if t[0].type == 'natural' and t[0] in nats:
				#print("ok nat")
				check_nat = True
			elif t[0].type == 'choice' and t[1] not in chose_child.decisions:
				#print("not ok choice")
				check_choice = False

			if check_nat and not check_choice:
				break

		if check_nat and check_choice:
			frontier.append(next_child)

	print("frontier_nat: ", frontier_info(frontier))
	return frontier


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


def frontier_info(frontier: list[AGraph]):
	result = ""
	for graph in frontier:
		result += str(graph.init_node) + ", "

	return "[" + result[:-2] + "]"


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

		chose_frontier = natural_clousure(graph, pick(new_frontier))

		new_frontier = frontier.copy()
		new_frontier.extend(chose_frontier)
		print("new_frontier:after_pick: ", frontier_info(new_frontier))
		r, fvs = found_strategy(new_frontier, bound)
		print("end_rec")
		if r is None:
			failed.append(fvs)
			tested.extend(chose_frontier)
		else:
			return r, fvs

		print("tested", frontier_info(tested))
		print("n.children", frontier_info(graph.init_node.transitions.values()))

	print("Failed: No choose left")
	return None, failed
