import numpy as np
from explainer.dag import Dag
from explainer.impacts import current_impacts, unavoidable_impacts
from solver.tree_lib import CNode, CTree
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


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str]) -> list[Dag]:
	bdds = []
	for choice, decisions in strategy.items():
		print("Explaining: choice", choice)

		print("Current impacts:")
		impacts, impacts_labels = current_impacts(decisions)
		for i in range(len(impacts)):
			print(f"I({impacts_labels[i]}): {impacts[i]}")

		bdd = explain_choice(choice, list(decisions.keys()), impacts, impacts_labels, impacts_names)
		if bdd is not None:
			bdds.append(bdd)
			continue

		print("Unavoidable impacts:")
		unavoidableImpacts, unavoidableImpacts_labels = unavoidable_impacts(region_tree, decisions)
		for i in range(len(unavoidableImpacts)):
			print(f"I({unavoidableImpacts_labels[i]}): {unavoidableImpacts[i]}")

		bdd = explain_choice(choice, list(decisions.keys()), unavoidableImpacts, unavoidableImpacts_labels, impacts_names)

		if bdd is not None:
			bdds.append(bdd)
			continue

		#stateful stuff
		print("Stateful impacts")

	return bdds
