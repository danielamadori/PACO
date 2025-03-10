import numpy as np
from paco.explainer.bdd.bdd import Bdd
from paco.explainer.explanation_type import current_impacts, unavoidable_impacts, decision_based, ExplanationType
from paco.parser.parse_tree import ParseTree
from paco.parser.parse_node import ParseNode
from paco.execution_tree.execution_tree import ExecutionTree


def explain_choice(choice:ParseNode, decisions:list[ParseNode], impacts:list[np.ndarray], labels:list, features_names:list, typeStrategy:ExplanationType, write_bdd=False, write_decision_tree=False) -> Bdd:
	decisions = list(decisions)
	decision_0 = decisions[0]
	decision_1 = None
	is_unavoidable_decision = len(decisions) == 1
	if not is_unavoidable_decision:
		decision_1 = decisions[1]

	bdd = Bdd(choice, decision_0, decision_1, impacts, labels, features_names, typeStrategy)

	success = True
	if not is_unavoidable_decision:
		success = bdd.build(write=write_decision_tree)
	if success and write_bdd:
		bdd.bdd_to_file()
	elif not success:
		bdd = None

	return bdd


def explain_strategy_full(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: ExplanationType = ExplanationType.CURRENT_IMPACTS) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
		elif typeStrategy == ExplanationType.UNAVOIDABLE_IMPACTS:
			vectors, labels = unavoidable_impacts(region_tree, decisions_taken)
		elif typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
		else:
			raise Exception(f"Choice {choice.name} is impossible to explain")

		bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)

		if bdd is None:
			#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
			return explain_strategy(region_tree, strategy, impacts_names, ExplanationType(typeStrategy + 1))

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

	return typeStrategy, bdds


def explain_strategy_hybrid(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str]) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()

	worstType = ExplanationType.CURRENT_IMPACTS
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names
		typeStrategy = ExplanationType.CURRENT_IMPACTS
		bdd = None

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = ExplanationType(typeStrategy + 1)

		if typeStrategy == ExplanationType.UNAVOIDABLE_IMPACTS:
			vectors, labels = unavoidable_impacts(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = ExplanationType(typeStrategy + 1)

		if typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy)
			if bdd is None:
				raise Exception(f"Choice {choice.name} is impossible to explain")

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

		if worstType < typeStrategy:
			worstType = typeStrategy

	return worstType, bdds


def explain_strategy(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], typeStrategy: ExplanationType = ExplanationType.HYBRID) -> (ExplanationType, dict[ParseNode, Bdd]):
	if typeStrategy == ExplanationType.HYBRID:
		return explain_strategy_hybrid(region_tree, strategy, impacts_names)

	return explain_strategy_full(region_tree, strategy, impacts_names, typeStrategy)


