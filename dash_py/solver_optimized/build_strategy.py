import copy
from solver.tree_lib import CNode, CTree
from solver_optimized.solution_tree import SolutionTree, SolutionNode
from solver_optimized.solver_optimized import frontier_info
from solver_optimized.states import States, ActivityState


def build_strategy(frontier: set[SolutionTree], strategy: dict[CNode, dict[CNode, list[SolutionNode]]] = {}) -> (list[SolutionTree], dict[CNode, dict[CNode, list[SolutionNode]]]):
	print("building_strategy:frontier: ", frontier_info(frontier))
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

	print("OK")
	return build_strategy(newFrontier, newStrategy)

def preview_impacts(tree: CTree, states: States):
	root = tree.root

	if root in states.activityState and states.activityState[root] != ActivityState.WAITING:
		return {}
	if root.type == 'task':
		if root not in states.activityState or (root in states.activityState and states.activityState[root] == ActivityState.WAITING):
			return {root}
		return {}
	if root.type == 'choice' or root.type == 'natural':
		for child in root.childrens:
			if child.root in states.activityState and states.activityState[child.root] == ActivityState.ACTIVE:
				return preview_impacts(child, states)

