import numpy as np
from datetime import datetime
from src.paco.explainer.bdd.bdd import Bdd
from src.paco.explainer.bdd.bdds import bdds_count_leaves
from src.paco.explainer.explanation_type import current_impacts, decision_based, ExplanationType
from src.paco.parser.parse_tree import ParseTree
from src.paco.parser.parse_node import ParseNode
from src.paco.execution_tree.execution_tree import ExecutionTree


def explanation_mode_name(typeStrategy: ExplanationType) -> str:
	if typeStrategy == ExplanationType.CURRENT_IMPACTS:
		return "impacts_based"
	if typeStrategy == ExplanationType.DECISION_BASED:
		return "decision_based"
	if typeStrategy == ExplanationType.HYBRID:
		return "hybrid"
	return str(typeStrategy).lower()


def hybrid_has_mixed_explanations(bdds: dict[ParseNode, Bdd]) -> bool:
	has_impacts = False
	has_decision = False
	for bdd in bdds.values():
		if bdd.typeStrategy == ExplanationType.CURRENT_IMPACTS:
			has_impacts = True
		elif bdd.typeStrategy == ExplanationType.DECISION_BASED:
			has_decision = True

	# Forced decisions are neutral; hybrid is valid only when both explainer
	# kinds are present among explainable choices.
	return has_impacts and has_decision


def explain_choice(choice:ParseNode, decisions:list[ParseNode], impacts:list[np.ndarray], labels:list, features_names:list, typeStrategy:ExplanationType, debug=False) -> Bdd:
	if len(decisions) == 0:
		raise Exception(f"explain_choice:Choice {choice.name} has no decisions")
	elif len(decisions) > 2:
		raise Exception(f"explain_choice:Choice {choice.name} has more than 2 decisions")

	is_unavoidable_decision = len(decisions) == 1
	if is_unavoidable_decision:
		decisions.append(None)

	bdd = Bdd(choice, decisions[0], decisions[1], typeStrategy,
			  impacts=impacts, labels=labels, features_names=features_names)

	is_separable = bdd.build(debug=debug) #Debug write on files
	if not is_separable:
		return None

	if debug:
		bdd.save_bdd()

	return bdd


def explain_strategy_full(
	region_tree: ParseTree,
	strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]],
	impacts_names: list[str],
	typeStrategy: ExplanationType = ExplanationType.CURRENT_IMPACTS,
	debug=False,
	allow_type_fallback: bool = True,
) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
		elif typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
		else:
			raise Exception(f"Choice {choice.name} is impossible to explain")

		bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)

		if bdd is None:
			#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
			if allow_type_fallback and typeStrategy < ExplanationType.HYBRID:
				return explain_strategy(
					region_tree,
					strategy,
					impacts_names,
					ExplanationType(typeStrategy + 1),
					debug,
					allow_type_fallback=allow_type_fallback,
				)
			raise Exception(f"Choice {choice.name} is impossible to explain with {typeStrategy}")

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

	return typeStrategy, bdds


def explain_strategy_hybrid(region_tree: ParseTree, strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]], impacts_names: list[str], debug=False) -> (ExplanationType, dict[ParseNode, Bdd]):
	bdds = dict[ParseNode, Bdd]()

	worstType = ExplanationType.CURRENT_IMPACTS
	for choice, decisions_taken in strategy.items():
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer:")
		features_names = impacts_names
		typeStrategy = ExplanationType.CURRENT_IMPACTS
		bdd = None

		if typeStrategy == ExplanationType.CURRENT_IMPACTS:
			vectors, labels = current_impacts(decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)
			if bdd is None:
				#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: failed")
				typeStrategy = ExplanationType(typeStrategy + 1)

		if typeStrategy == ExplanationType.DECISION_BASED:
			features_names, vectors, labels = decision_based(region_tree, decisions_taken)
			bdd = explain_choice(choice, list(decisions_taken.keys()), vectors, labels, features_names, typeStrategy, debug)
			if bdd is None:
				raise Exception(f"Choice {choice.name} is impossible to explain")

		bdds[choice] = bdd
		#print(f"Explaining choice {choice.name}, using {typeStrategy} explainer: done")

		if worstType < typeStrategy:
			worstType = typeStrategy

	return worstType, bdds


def explain_strategy(
	region_tree: ParseTree,
	strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]],
	impacts_names: list[str],
	typeStrategy: ExplanationType = ExplanationType.HYBRID,
	debug=False,
	allow_type_fallback: bool = True,
) -> (ExplanationType, dict[ParseNode, Bdd]):
	if typeStrategy == ExplanationType.HYBRID:
		return explain_strategy_hybrid(region_tree, strategy, impacts_names, debug)

	return explain_strategy_full(
		region_tree,
		strategy,
		impacts_names,
		typeStrategy,
		debug,
		allow_type_fallback=allow_type_fallback,
	)


def explain_strategy_with_attempts(
	region_tree: ParseTree,
	strategy: dict[ParseNode, dict[ParseNode, set[ExecutionTree]]],
	impacts_names: list[str],
	debug=False,
) -> (ExplanationType, dict[ParseNode, Bdd], list[dict], dict[str, dict[ParseNode, Bdd]]):
	"""
	Always try all explainers in this exact order:
	1) impacts_based (CURRENT_IMPACTS)
	2) decision_based (DECISION_BASED)
	3) hybrid (HYBRID)

	The selected explainer used by callers is the first successful mode in the order above.
	All attempts are still recorded with status, timing and leaves.
	"""
	attempt_plan = [
		("impacts_based", ExplanationType.CURRENT_IMPACTS),
		("decision_based", ExplanationType.DECISION_BASED),
		("hybrid", ExplanationType.HYBRID),
	]

	attempts = []
	last_error = None
	selected_result = None
	attempt_bdds_by_mode: dict[str, dict[ParseNode, Bdd]] = {}
	for mode_name, mode in attempt_plan:
		started_at = datetime.now()
		try:
			worst_type, bdds = explain_strategy(
				region_tree,
				strategy,
				impacts_names,
				mode,
				debug,
				allow_type_fallback=False,
			)
			leaves_total, leaves_per_choice = bdds_count_leaves(bdds)
			hybrid_mixed_explanations = (
				hybrid_has_mixed_explanations(bdds)
				if mode == ExplanationType.HYBRID
				else None
			)
			ended_at = datetime.now()
			duration_ms = (ended_at - started_at).total_seconds() * 1000
			attempts.append({
				"mode": mode_name,
				"type": str(mode),
				"status": "success",
				"success": True,
				"duration_ms": duration_ms,
				"error": "",
				"leaves_total": leaves_total,
				"leaves_per_choice": leaves_per_choice,
				"hybrid_mixed_explanations": hybrid_mixed_explanations,
				"captured_at": ended_at.isoformat(timespec="milliseconds"),
			})
			attempt_bdds_by_mode[mode_name] = bdds
			if selected_result is None:
				selected_result = (worst_type, bdds)
		except Exception as exc:
			ended_at = datetime.now()
			duration_ms = (ended_at - started_at).total_seconds() * 1000
			last_error = exc
			attempts.append({
				"mode": mode_name,
				"type": str(mode),
				"status": "failed",
				"success": False,
				"duration_ms": duration_ms,
				"error": str(exc),
				"leaves_total": 0,
				"leaves_per_choice": {},
				"captured_at": ended_at.isoformat(timespec="milliseconds"),
			})

	if selected_result is not None:
		return selected_result[0], selected_result[1], attempts, attempt_bdds_by_mode

	raise Exception(
		"All explain strategy modes failed: "
		+ "; ".join(f"{a['mode']} -> {a['error']}" for a in attempts)
	) from last_error
