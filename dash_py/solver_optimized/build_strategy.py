import copy
from solver.tree_lib import CNode
from solver_optimized.execution_tree import ExecutionTree, ExecutionViewPoint
from solver_optimized.found_strategy import frontier_info


def build_strategy(frontier: set[ExecutionTree], strategy: dict[CNode, dict[CNode, set[ExecutionViewPoint]]] = {}) -> (set[ExecutionTree], dict[CNode, dict[CNode, set[ExecutionViewPoint]]]):
	print("building_strategy:frontier: ", frontier_info(frontier))
	if len(frontier) == 0:
		return frontier, strategy

	newFrontier = set()
	newStrategy = copy.deepcopy(strategy)
	for tree in frontier:
		if tree.root.parent is None: #Is root because parent is None
			continue

		#print(f"ID: {tree.root.id}")
		for d in tree.root.decisions:
			#print(f"ID:{d.id}, Parent id: {d.parent.id}, type: {d.parent.type}")
			if d.parent.type == 'choice':
				if d.parent not in newStrategy:
					newStrategy[d.parent] = {d: {tree.root.parent}}
				elif d not in newStrategy[d.parent]:
					newStrategy[d.parent][d] = {tree.root.parent}
				else:
					newStrategy[d.parent][d].add(tree.root.parent)

		newFrontier.add(tree.root.parent)

	return build_strategy(newFrontier, newStrategy)
