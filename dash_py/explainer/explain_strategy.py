import numpy as np
from explainer.bdd import Bdd
from explainer.strategy_type import current_impacts, unavoidable_impacts, decision_based, TypeStrategy
from parser.tree_lib import CNode, CTree
from solver.execution_tree import ExecutionTree


def explain_choice(choice:CNode, decisions:list[CNode], impacts:list[np.ndarray], labels:list, features_names:list, typeStrategy:TypeStrategy) -> Bdd:
	decisions = list(decisions)
	decision_0 = decisions[0]
	decision_1 = None
	is_unavoidable_decision = len(decisions) == 1
	if not is_unavoidable_decision:
		decision_1 = decisions[1]

	bdd = Bdd(choice, decision_0, decision_1, impacts, labels, features_names, typeStrategy)

	success = True
	if not is_unavoidable_decision:
		success = bdd.build(write=True)
	if success:
		bdd.bdd_to_file()
	else:
		bdd = None

	return bdd


def explain_strategy_full(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: TypeStrategy = TypeStrategy.CURRENT_IMPACTS) -> (TypeStrategy, dict[CNode, Bdd]):
	bdds = dict[CNode, Bdd]()
	for choice, decisions_taken in strategy.items():
		print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names

		if typeStrategy == TypeStrategy.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
		elif typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			vectors, labels = unavoidable_impacts(region_tree, decisions_taken)
		elif typeStrategy == TypeStrategy.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
		else:
			raise Exception("Impossible to explain")

		bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)

		if bdd is None:
			print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
			return explain_strategy(region_tree, strategy, impacts_names, TypeStrategy(typeStrategy + 1))

		bdds[choice] = bdd
		print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

	return typeStrategy, bdds


def explain_strategy_hybrid(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str]) -> (TypeStrategy, dict[CNode, Bdd]):
	bdds = dict[CNode, Bdd]()

	worstType = TypeStrategy.CURRENT_IMPACTS
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names
		typeStrategy = TypeStrategy.CURRENT_IMPACTS
		bdd = None

		if typeStrategy == TypeStrategy.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = TypeStrategy(typeStrategy + 1)

		if typeStrategy == TypeStrategy.UNAVOIDABLE_IMPACTS:
			vectors, labels = unavoidable_impacts(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = TypeStrategy(typeStrategy + 1)

		if typeStrategy == TypeStrategy.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				raise Exception("Impossible to explain")

		bdds[choice] = bdd
		print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

		if worstType < typeStrategy:
			worstType = typeStrategy

	return worstType, bdds


def explain_strategy(region_tree: CTree, strategy: dict[CNode, dict[CNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: TypeStrategy = TypeStrategy.HYBRID) -> (TypeStrategy, dict[CNode, Bdd]):
	if typeStrategy == TypeStrategy.HYBRID:
		return explain_strategy_hybrid(region_tree, strategy, impacts_names)

	return explain_strategy_full(region_tree, strategy, impacts_names, typeStrategy)


