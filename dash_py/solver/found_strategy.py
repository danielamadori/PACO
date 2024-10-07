import random
import numpy as np
from solver.execution_tree import ExecutionTree

'''
def compare_bound(cei: np.ndarray, bound: np.ndarray):
	print(cei, bound, [-1 if v1 < v2 else 0 if v1 == v2 else 1 for v1, v2 in zip(cei, bound)])
	return [-1 if v1 < v2 else 0 if v1 == v2 else 1 for v1, v2 in zip(cei, bound)]
'''

def compare_bound(cei: np.ndarray, bound: np.ndarray):
	#print("CEI: ", cei, " bound: ", bound, "res: ", np.where(cei <= bound, 0, 1))
	#print("type cei:", cei.dtype, "type bound:", bound.dtype)
	#return np.where(cei <= bound, 0, 1)
	return np.where(cei <= bound + np.finfo(np.float64).eps*10, 0, 1) #TODO fix eps value


def pick(frontier: list[ExecutionTree], method: str = 'random') -> ExecutionTree:
	return random.choices(frontier, weights=[tree.root.probability for tree in frontier], k=1)[0]
	#return frontier[random.randint(0, len(frontier) - 1)]



def natural_closure(tree: ExecutionTree, selected_tree: ExecutionTree) -> list[ExecutionTree]:
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


def frontier_info(frontier: list[ExecutionTree]) -> str:
	result = ""
	for tree in frontier:
		decisions = ""
		for decision in tree.root.decisions:
			decisions += str(decision.id) + ", "

		choices_natures = ""
		for choice_nature in tree.root.choices_natures:
			choices_natures += str(choice_nature.id) + ", "

		result += f"ID:{tree.root.id}:<<" + decisions[:-2] + ">,<" + choices_natures[:-2] + ">>, "

	return "[" + result[:-2] + "]"


def found_strategy(frontier: list[ExecutionTree], bound: np.ndarray) -> (list[ExecutionTree], list[np.ndarray], list[np.ndarray]):
	#print("frontier: ", frontier_info(frontier))

	frontier_value_bottom_up:np.ndarray = np.sum([tree.root.cei_bottom_up for tree in frontier], axis=0)
	frontier_value_top_down:np.ndarray = np.sum([tree.root.cei_top_down for tree in frontier], axis=0)

	if np.all(compare_bound(frontier_value_bottom_up, bound) <= 0):
		return frontier, [frontier_value_bottom_up], [frontier_value_top_down]

	if np.all(compare_bound(frontier_value_top_down, bound) > 0) or all(tree.root.is_final_state for tree in frontier):
		print("Failed top_down: not a valid choose")
		return None, [], [frontier_value_top_down]

	tree = pick([tree for tree in frontier if not tree.root.is_final_state])

	tested_frontier_solution = []
	failed_frontier_solution_value_bottom_up = []
	failed_frontier_solution_value_top_down = []
	while len(tested_frontier_solution) < len(tree.root.transitions.values()):
		to_pick_frontier = [subTree for subTree in tree.root.transitions.values() if subTree not in tested_frontier_solution]
		#print("to_pick_frontier: ", frontier_info(to_pick_frontier))

		chose = pick(to_pick_frontier)
		chose_frontier = natural_closure(tree, chose)
		#print("frontier_nat: ", frontier_info(chose_frontier))

		new_frontier = frontier.copy()
		new_frontier.remove(tree)
		new_frontier.extend(chose_frontier)
		#print("new_frontier: ", frontier_info(new_frontier))
		frontier_solution, frontier_solution_value_bottom_up, frontier_solution_value_top_down = found_strategy(new_frontier, bound)
		#print("end_rec")
		if frontier_solution is None:
			failed_frontier_solution_value_bottom_up.extend(frontier_solution_value_bottom_up)
			failed_frontier_solution_value_top_down.extend(frontier_solution_value_top_down)
			tested_frontier_solution.extend(chose_frontier)
		else:
			return frontier_solution, frontier_solution_value_bottom_up, frontier_solution_value_top_down

	#print("tested_frontier_solution", frontier_info(tested_frontier_solution))
	print("Failed: No choose left")
	return None, failed_frontier_solution_value_bottom_up, failed_frontier_solution_value_top_down
