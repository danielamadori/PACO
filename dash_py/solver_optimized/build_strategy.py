import copy
from solver.tree_lib import CNode
from solver_optimized.solution_tree import SolutionTree, SolutionNode


def build_strategy(frontier: set[SolutionTree], strategy: dict[CNode, dict[CNode, list[SolutionNode]]] = {}) -> (list[SolutionTree], dict[CNode, dict[CNode, list[SolutionNode]]]):
	print("building_strategy:len(frontier):", len(frontier), frontier)
	if len(frontier) == 0:
		return frontier, strategy

	newFrontier = set()
	newStrategy = copy.deepcopy(strategy)
	for tree in frontier:
		print(f"ID:{tree.root}")
		if tree.root.parent is None: #Is root because parent is None
			continue

		# {id_choice0: {id_decision1: [s1, s2], id_decision2: [s3, s4] }, id_choice4: {id_decision5: [s5, s6], id_decision6: [s7, s8] }}
		for d in tree.root.decisions:
			#print(f"ID:{d.id}, Parent id: {d.parent.id}, type: {d.parent.type}")
			if d.parent.type == 'choice':
				if d.parent not in newStrategy:
					newStrategy[d.parent] = {d: [tree]}
				elif d not in newStrategy[d.parent]:
					newStrategy[d.parent][d] = [tree]
				else:
					newStrategy[d.parent][d].append(tree)

		newFrontier.add(tree.root.parent)

	print("OK")
	return build_strategy(newFrontier, newStrategy)
