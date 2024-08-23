import numpy as np
import pandas as pd

from solver.tree_lib import CTree, CNode
from solver_optimized.execution_tree import ExecutionViewPoint
from solver_optimized.explainer.dag import Dag
from solver_optimized.explainer.bdd import BDD
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
	currentImpactsStrategy = {}
	unavoidableImpactsStrategy = {}
	statefulStrategy = {}

	for choice in strategy:
		currentImpactsStrategy[choice] = {}
		unavoidableImpactsStrategy[choice] = {}
		statefulStrategy[choice] = {}

		for decision in strategy[choice]:
			currentImpactsStrategy[choice][decision] = []
			unavoidableImpactsStrategy[choice][decision] = []
			statefulStrategy[choice][decision] = []

			for tree in strategy[choice][decision]:
				unavoidableTasks = unavoidable_tasks(region_tree, tree.root.states)

				currentImpacts = tree.root.impacts
				unavoidableImpacts = np.zeros(len(currentImpacts))
				if unavoidableTasks:
					for unavoidableTask in unavoidableTasks:
						unavoidableImpacts += np.array(unavoidableTask.impact)

				stateful = currentImpacts + unavoidableImpacts

				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Current impacts: ", currentImpacts)
				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Unavoidable impacts: ", unavoidableImpacts)
				print(f"<c:{choice}, d:{decision}, s:{tree.root.id}> Stateful impacts: ", stateful)

				currentImpactsStrategy[choice][decision].append(currentImpacts)
				unavoidableImpactsStrategy[choice][decision].append(unavoidableImpacts)
				statefulStrategy[choice][decision].append(stateful)

	return currentImpactsStrategy, unavoidableImpactsStrategy, statefulStrategy


def test_strategy(strategy):
	for choice in strategy:
		print(f"strategy[{choice}] {strategy[choice]}")
		impacts = []
		labels = []
		i = 0
		for decision in strategy[choice]:
			print(f"Choice {choice}, Decision {decision}: strategy[{choice}][{decision}] {strategy[choice][decision]}")
			for state in strategy[choice][decision]:
				print(f"\tState: {state}")
				impacts.append(state)
				labels.append(i)
			i += 1

		vector_size = len(impacts[0])
		print("Impacts:", impacts)
		print("Labels:", labels)
		print("Impacts size:", vector_size)


		df = pd.DataFrame(impacts, columns=[f'impact_{i}' for i in range(vector_size)])
		df['class'] = labels

		dag = Dag(df)
		dag.run(file_path="out/output")
		#print(dag.transitions_str())

		min_tree = BDD(dag)
		print(min_tree.build())
		min_tree.to_file("out/bdd_tree")
