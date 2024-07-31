import numpy as np

from solver.tree_lib import CTree, CNode
from solver_optimized.execution_tree import ExecutionViewPoint
from solver_optimized.saturate_execution.states import States, node_info, ActivityState


def unavoidable_tasks(tree: CTree, states: States) -> set[CTree]:
	root = tree.root
	#print(node_info(root, states))
	if root in states.activityState and states.activityState[root] in [ActivityState.WILL_NOT_BE_EXECUTED, ActivityState.COMPLETED, ActivityState.COMPLETED_WIHTOUT_PASSING_OVER]:
		#print("general node with: -1, 2, 3")
		return {}
	if root.type == 'task':
		if root not in states.activityState or (root in states.activityState and states.activityState[root] == ActivityState.WAITING):
			#print("task")
			return {root}
		return {}
	if root.type in ['sequential', 'parallel']:
		#print("seq, par")
		result = set[CTree]()
		for child in root.childrens:
			result.update(unavoidable_tasks(child, states))
		return result

	if root.type in ['choice', 'natural'] and root in states.activityState and states.activityState[root] == ActivityState.ACTIVE:
		#print("choice, natural")
		for child in root.childrens:
			if child.root in states.activityState and states.activityState[child.root] == ActivityState.ACTIVE:
				return unavoidable_tasks(child, states)

	return {}


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionViewPoint]]]):
	currentImpactsStrategy = dict[CNode, dict[CNode, list[np.ndarray]]]()
	unavoidableImpactsStrategy = dict[CNode, dict[CNode, list[np.ndarray]]]()
	statefulStrategy = dict[CNode, dict[CNode, list[np.ndarray]]]()

	for choice in strategy:
		#print(f"Choice {choice}:")
		currentImpactsStrategy[choice] = dict[CNode, list[np.ndarray]]()
		unavoidableImpactsStrategy[choice] = dict[CNode, list[np.ndarray]]()
		statefulStrategy[choice] = dict[CNode, list[np.ndarray]]()

		for decision in strategy[choice]:
			#print(f"Decision {decision}:")
			currentImpactsStrategy[choice][decision] = list[np.ndarray]()
			unavoidableImpactsStrategy[choice][decision] = list[np.ndarray]()
			statefulStrategy[choice][decision] = list[np.ndarray]()

			for tree in strategy[choice][decision]:
				#print("Final States:", tree.root.id)
				unavoidableTasks = unavoidable_tasks(region_tree, tree.root.states)
				#print("end")

				currentImpacts = tree.root.impacts
				unavoidableImpacts = np.zeros(len(currentImpacts))
				if unavoidableTasks:
					for unavoidableTask in unavoidableTasks:
						#print(f'id:{unavoidableTask.id}; {"" if unavoidableTask.name is None else "name:" + unavoidableTask.name + '; '}type:{unavoidableTask.type};')
						unavoidableImpacts += np.array(unavoidableTask.impact)

				stateful = currentImpacts + unavoidableImpacts

				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Current impacts: ", currentImpacts)
				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Unavoidable impacts: ", unavoidableImpacts)
				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Stateful impacts: ", stateful)
			currentImpactsStrategy[choice][decision].append(currentImpacts)
			unavoidableImpactsStrategy[choice][decision].append(unavoidableImpacts)
			statefulStrategy[choice][decision].append(stateful)

	return currentImpactsStrategy, unavoidableImpactsStrategy, statefulStrategy