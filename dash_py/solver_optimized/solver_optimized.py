import random
from solver_optimized.solution_tree import SolutionTree


def compare_bound(cei: list, bound: list):
	return [-1 if v1 < v2 else 0 if v1 == v2 else 1 for v1, v2 in zip(cei, bound)]


def pick(frontier: list[SolutionTree],  method: str = 'random') -> SolutionTree:

	return frontier[random.randint(0, len(frontier) - 1)]


def natural_closure(tree: SolutionTree, selected_tree: SolutionTree) -> list[SolutionTree]:
	nats = [node for node in tree.root.choices_natures if node.type == 'natural']
	frontier = []
	#print("nat_nodes: ", [node.id for node in nat_nodes], "chose_id: ", [node.id for node in chose_id])

	for transition, next_child in tree.root.transitions.items():
		check_nat = len(nats) == 0
		check_choice = len(selected_tree.root.decisions) != 0
		for t in transition:
			#print("t: ", t[0].type, t[0].id, t[1].id)
			if t[0].type == 'natural':# and t[0] in nats:
				#print("ok nat")
				check_nat = True
			elif t[0].type == 'choice' and t[1] not in selected_tree.root.decisions:
				#print("not ok choice")
				check_choice = False

			if check_nat and not check_choice:
				break

		if check_nat and check_choice:
			frontier.append(next_child)

	return frontier


def frontier_info(frontier: list[SolutionTree]) -> str:
	result = ""
	for graph in frontier:
		decisions = ""
		for decision in graph.root.decisions:
			decisions += str(decision.id) + ", "

		choices_natures = ""
		for choice_nature in graph.root.choices_natures:
			choices_natures += str(choice_nature.id) + ", "

		result += "<<" + decisions[:-2] + ">,<" + choices_natures[:-2] + ">>, "

	return "[" + result[:-2] + "]"


def found_strategy(frontier: list[SolutionTree], bound: list) -> (list[SolutionTree], list[int]):
	print("frontier: ", frontier_info(frontier))

	frontier_value_bottom_up = sum(tree.root.cei_bottom_up for tree in frontier)

	if all(result <= 0 for result in compare_bound(frontier_value_bottom_up, bound)):
		print("Win", frontier_value_bottom_up, bound, compare_bound(frontier_value_bottom_up, bound))
		return frontier, [frontier_value_bottom_up]

	frontier_value_top_down = sum(tree.root.cei_top_down for tree in frontier)

	if (all(result > 0 for result in compare_bound(frontier_value_top_down, bound))
			or all(tree.root.is_final_state for tree in frontier)):
		print("Failed top_down: not a valid choose")
		return None, [frontier_value_top_down]

	tree = pick([tree for tree in frontier if not tree.root.is_final_state])

	failed = []
	tested = []
	while len(tested) < len(tree.root.transitions.values()):
		to_pick_frontier = [subTree for subTree in tree.root.transitions.values() if subTree not in tested]
		print("to_pick_frontier: ", frontier_info(to_pick_frontier))

		chose = pick(to_pick_frontier)
		chose_frontier = natural_closure(tree, chose)
		print("frontier_nat: ", frontier_info(chose_frontier))

		new_frontier = frontier.copy()
		new_frontier.remove(tree)
		new_frontier.extend(chose_frontier)
		print("new_frontier: ", frontier_info(new_frontier))
		r, fvs = found_strategy(new_frontier, bound)
		print("end_rec")
		if r is None:
			failed.append(fvs)
			tested.extend(chose_frontier)
		else:
			return r, fvs

		print("tested", frontier_info(tested))
		print("n.children", frontier_info(tree.root.transitions.values()))

	print("Failed: No choose left")
	return None, failed
