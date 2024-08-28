import numpy as np
from explainer.dag import Dag
from explainer.impacts import current_impacts, unavoidable_impacts
from solver.tree_lib import CNode
from solver_optimized.execution_tree import ExecutionTree


def explain_choice(choice:CNode, decisions:list[CNode], impacts:list[np.array], impacts_labels:list, impacts_names):
	decisions = list(decisions)
	decision_0 = decisions[0]
	decision_1 = None
	is_unavoidable_decision = len(decisions) == 1
	if not is_unavoidable_decision:
		decision_1 = decisions[1]

	dag = Dag(choice, decision_0, decision_1, impacts, impacts_labels, impacts_names)

	success = True
	if not is_unavoidable_decision:
		success = dag.explore(write=True)
	if success:
		dag.bdd_to_file()

	return success


def explain_strategy(strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str]):
	impacts = {}
	for choice, decisions in strategy.items():
		print("Explaining: choice", choice)

		print("Current impacts:")
		impacts[choice], impacts_labels = current_impacts(decisions)
		print(impacts[choice], impacts_labels)
		if explain_choice(choice, list(decisions.keys()), impacts[choice], impacts_labels, impacts_names):
			continue

		print("Unavoidable impacts:")
		imp, imp_labels = unavoidable_impacts(choice, decisions, len(impacts_names))
		print(imp, imp_labels)
		impacts[choice].extend(imp)
		impacts_labels.extend(imp_labels)
		if explain_choice(choice, list(decisions.keys()), impacts[choice], impacts_labels, impacts_names):
			continue

		#stateful stuff
		print("Stateful impacts")

	return impacts
