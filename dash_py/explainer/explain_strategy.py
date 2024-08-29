import numpy as np
from explainer.dag import Dag
from explainer.impacts import current_impacts, unavoidable_impacts
from solver.tree_lib import CNode
from solver_optimized.execution_tree import ExecutionTree


def explain_choice(choice:CNode, decisions:list[CNode], impacts:list[np.array], impacts_labels:list, impacts_names:list) -> Dag:
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
	else:
		dag = None

	return dag


def explain_strategy(strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str]) -> list[Dag]:
	bdds = []
	for choice, decisions in strategy.items():
		print("Explaining: choice", choice)

		print("Current impacts:")
		impacts, impacts_labels = current_impacts(decisions)
		print(impacts, impacts_labels)
		bdd = explain_choice(choice, list(decisions.keys()), impacts, impacts_labels, impacts_names)
		if bdd is not None:
			bdds.append(bdd)
			continue

		print("Unavoidable impacts:")
		unavoidableImpacts, unavoidableImpacts_labels = unavoidable_impacts(choice, decisions, len(impacts_names))
		print(unavoidableImpacts, unavoidableImpacts_labels)
		impacts.extend(unavoidableImpacts)
		impacts_labels.extend(unavoidableImpacts_labels)
		bdd = explain_choice(choice, list(decisions.keys()), impacts, impacts_labels, impacts_names)
		if bdd is not None:
			bdds.append(bdd)
			continue

		#stateful stuff
		print("Stateful impacts")

	return bdds
