import numpy as np
from explainer.bdd import Bdd
from explainer.strategy_type import current_impacts, unavoidable_impacts, stateful, TypeStrategy
from solver.tree_lib import CNode, CTree
from solver_optimized.execution_tree import ExecutionTree


def explain_choice(choice:CNode, decisions:list[CNode], impacts:list[np.ndarray], labels:list, features_names:list) -> Bdd:
	decisions = list(decisions)
	decision_0 = decisions[0]
	decision_1 = None
	is_unavoidable_decision = len(decisions) == 1
	if not is_unavoidable_decision:
		decision_1 = decisions[1]

	bdd = Bdd(choice, decision_0, decision_1, impacts, labels, features_names)

	success = True
	if not is_unavoidable_decision:
		success = bdd.build(write=True)
	if success:
		bdd.bdd_to_file()
	else:
		bdd = None

	return bdd


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: TypeStrategy = TypeStrategy.CURRENT_IMPACTS) -> (
TypeStrategy, dict[CNode, Bdd]):
	bdds = dict[CNode, Bdd]()
	for choice, decisions in strategy.items():
		print("Explaining: choice", choice)

		if typeStrategy == TypeStrategy.CURRENT_IMPACTS:
			print("Current impacts:")
			impacts, impacts_labels = current_impacts(decisions)
			for i in range(len(impacts)):
				print(f"I({impacts_labels[i]}): {impacts[i]}")

			bdd = explain_choice(choice, list(decisions.keys()), impacts, impacts_labels, impacts_names)
			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.UNAVOIDABLE_IMPACTS)

		elif typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			print("Unavoidable impacts:")
			unavoidableImpacts, unavoidableImpacts_labels = unavoidable_impacts(region_tree, decisions)
			for i in range(len(unavoidableImpacts)):
				print(f"I({unavoidableImpacts_labels[i]}): {unavoidableImpacts[i]}")

			bdd = explain_choice(choice, list(decisions.keys()), unavoidableImpacts, unavoidableImpacts_labels, impacts_names)

			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.STATEFUL)

		# if typeStrategy == TypeStrategy.STATEFUL:
		print("Stateful impacts")
		all_nodes, states_vectors, labels = stateful(decisions)
		bdd = explain_choice(choice, list(decisions.keys()), states_vectors, labels, all_nodes)

		if bdd is not None:
			bdds[choice] = bdd
		else:
			raise Exception("No explanation found")

	return typeStrategy, bdds
