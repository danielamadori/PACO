import numpy as np
from saturate_execution.states import States, ActivityState
from solver.tree_lib import CNode
from solver_optimized.execution_tree import ExecutionTree


def current_impacts(decisions: dict[CNode, set[ExecutionTree]]) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			impacts.append(executionTree.root.impacts)
			impacts_labels.append(decision.id)

	return impacts, impacts_labels

def unavoidable_tasks(root: CNode, states: States) -> set[CNode]:
	#print(node_info(root, states))
	if root in states.activityState and states.activityState[root] in [ActivityState.WILL_NOT_BE_EXECUTED, ActivityState.COMPLETED, ActivityState.COMPLETED_WIHTOUT_PASSING_OVER]:
		#print("general node with: -1, 2, 3")
		return set()
	if root.type == 'task':
		if root not in states.activityState or (root in states.activityState and states.activityState[root] == ActivityState.WAITING):
			return set([root])
		return set()
	if root.type in ['sequential', 'parallel']:
		result = set[CNode]()
		for child in root.childrens:
			result.union(unavoidable_tasks(child.root, states))
		return result

	if root.type in ['choice', 'natural'] and root in states.activityState and states.activityState[root] == ActivityState.ACTIVE:
		for child in root.childrens:
			if child.root in states.activityState and states.activityState[child.root] == ActivityState.ACTIVE:
				return unavoidable_tasks(child.root, states)

	return set()

def unavoidable_impacts(choice_sub_region: CNode, decisions: dict[CNode, set[ExecutionTree]], impacts_size:int) -> (list, list):
	impacts, impacts_labels = [], []
	for decision, executionTrees in decisions.items():
		for executionTree in executionTrees:
			unavoidableImpacts = np.zeros(impacts_size)
			for unavoidableTask in unavoidable_tasks(choice_sub_region, executionTree.root.states):
				unavoidableImpacts += np.array(unavoidableTask.impact)

			impacts.append(unavoidableImpacts)
			impacts_labels.append(decision.id)

	return impacts, impacts_labels
