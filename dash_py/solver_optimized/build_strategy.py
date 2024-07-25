import copy
from solver.tree_lib import CNode
from solver_optimized.execution_tree import ExecutionTree, ExecutionViewPoint
from solver_optimized.found_strategy import frontier_info


def build_strategy(frontier: set[ExecutionTree], strategy: dict[CNode, dict[CNode, list[ExecutionViewPoint]]] = {}) -> (list[ExecutionTree], dict[CNode, dict[CNode, list[ExecutionViewPoint]]]):
	print("building_strategy:frontier: ", frontier_info(frontier))
	if len(frontier) == 0:
		return frontier, strategy

	newFrontier = set()
	newStrategy = copy.deepcopy(strategy)
	for tree in frontier:
		if tree.root.parent is None: #Is root because parent is None
			continue

		print(f"ID:{tree.root}")

		# {id_choice0: {id_decision1: [s1, s2], id_decision2: [s3, s4] }, id_choice4: {id_decision5: [s5, s6], id_decision6: [s7, s8] }}
		for d in tree.root.decisions:
			#print(f"ID:{d.id}, Parent id: {d.parent.id}, type: {d.parent.type}")
			if d.parent.type == 'choice':
				'''
				if d.parent not in newStrategy:
					newStrategy[d.parent] = {d: [tree]}
				elif d not in newStrategy[d.parent]:
					newStrategy[d.parent][d] = [tree]
				else:
					newStrategy[d.parent][d].append(tree)
				'''
				#Original code: get just the parent
				if d.parent not in newStrategy:
					newStrategy[d.parent] = {d: [tree.root.parent]}
				elif d not in newStrategy[d.parent]:
					newStrategy[d.parent][d] = [tree.root.parent]
				else:
					newStrategy[d.parent][d].append(tree.root.parent)

		newFrontier.add(tree.root.parent)

	return build_strategy(newFrontier, newStrategy)