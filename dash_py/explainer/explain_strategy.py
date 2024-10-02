import numpy as np
from explainer.bdd import Bdd
from explainer.strategy_type import current_impacts, unavoidable_impacts, decision_based, TypeStrategy
from parser.tree_lib import CNode, CTree
from solver.execution_tree import ExecutionTree


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


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: TypeStrategy = TypeStrategy.CURRENT_IMPACTS) -> (TypeStrategy, dict[CNode, Bdd]):
	bdds = dict[CNode, Bdd]()
	for choice, decisions_taken in strategy.items():
		print("Explaining: choice", choice)

		if typeStrategy == TypeStrategy.CURRENT_IMPACTS:
			print("Current impacts:")
			impacts, impacts_labels = current_impacts(decisions_taken)
			for i in range(len(impacts)):
				print(f"I({impacts_labels[i]}): {impacts[i]}")

			bdd = explain_choice(choice, list(decisions_taken.keys()), impacts, impacts_labels, impacts_names)
			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.UNAVOIDABLE_IMPACTS)

		elif typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			print("Unavoidable impacts:")
			unavoidableImpacts, unavoidableImpacts_labels = unavoidable_impacts(region_tree, decisions_taken)
			for i in range(len(unavoidableImpacts)):
				print(f"I({unavoidableImpacts_labels[i]}): {unavoidableImpacts[i]}")

			bdd = explain_choice(choice, list(decisions_taken.keys()), unavoidableImpacts, unavoidableImpacts_labels, impacts_names)

			if bdd is not None:
				bdds[choice] = bdd
				continue

			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy.DECISION_BASED)

		print("Decision based:")
		decisions, decision_vectors, labels = decision_based(region_tree, decisions_taken)
		print("Decisions:", decisions)
		for i in range(len(decision_vectors)):
			print(f"{labels[i]}: {decision_vectors[i]}")

		bdd = explain_choice(choice, list(decisions_taken.keys()), decision_vectors, labels, decisions)

		if bdd is not None:
			bdds[choice] = bdd
		else:
			raise Exception("No explanation found")

	return typeStrategy, bdds
