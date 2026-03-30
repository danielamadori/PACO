from src.paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from src.paco.explainer.explain_strategy import explain_strategy_with_attempts
from src.paco.explainer.full_strategy import full_strategy
from src.paco.explainer.explanation_type import ExplanationType
from src.paco.explainer.bdd.bdds import bdds_count_leaves
from src.paco.searcher.build_strategy import build_strategy
from src.paco.searcher.create_execution_tree import create_execution_tree
from src.paco.searcher.found_strategy import found_strategy
import numpy as np
from datetime import datetime
from src.utils.env import IMPACTS_NAMES
from src.paco.execution_tree.execution_tree import ExecutionTree
from src.paco.explainer.strategy_view_point import StrategyViewPoint


def get_strategy_scenarios_count(strategy_tree: ExecutionTree) -> int:
	visited_nodes = set()

	def dfs(node: StrategyViewPoint):
		if node.id in visited_nodes:
			return
		visited_nodes.add(node.id)

		has_arbitrary_choice = False
		for choice in node.choices:
			if choice not in node.explained_choices:
				has_arbitrary_choice = True
				break

		if has_arbitrary_choice:
			return

		for transition_tuple, child_tree in node.transitions.items():
			dfs(child_tree.root)

	dfs(strategy_tree.root)
	return len(visited_nodes)


def get_strategy_choice_typology(strategy_tree: ExecutionTree) -> dict[str, int]:
	visited_nodes = set()
	arbitrary_choices = set()
	forced_choices = set()
	impacts_choices = set()
	decision_choices = set()

	def dfs(node: StrategyViewPoint):
		if node.id in visited_nodes:
			return
		visited_nodes.add(node.id)

		for choice in node.choices:
			choice_id = choice.id
			bdd = node.explained_choices.get(choice)
			if bdd is None:
				arbitrary_choices.add(choice_id)
			elif bdd.typeStrategy == ExplanationType.FORCED_DECISION:
				forced_choices.add(choice_id)
			elif bdd.typeStrategy == ExplanationType.CURRENT_IMPACTS:
				impacts_choices.add(choice_id)
			elif bdd.typeStrategy == ExplanationType.DECISION_BASED:
				decision_choices.add(choice_id)

		for transition_tuple, child_tree in node.transitions.items():
			dfs(child_tree.root)

	dfs(strategy_tree.root)
	total_choices = len(arbitrary_choices.union(forced_choices).union(impacts_choices).union(decision_choices))
	return {
		"choices_total": total_choices,
		"choices_arbitrary": len(arbitrary_choices),
		"choices_forced": len(forced_choices),
		"choices_impacts": len(impacts_choices),
		"choices_decision": len(decision_choices),
	}


def record_stage_timing(stage_timings: list[dict], stage_name: str, started_at: datetime) -> float:
	ended_at = datetime.now()
	duration_ms = (ended_at - started_at).total_seconds() * 1000
	stage_timings.append({
		"stage": stage_name,
		"captured_at": ended_at.isoformat(timespec="milliseconds"),
		"duration_ms": duration_ms,
	})
	return duration_ms


def set_explain_strategy_mode_timings(metadata: dict, explain_attempts: list[dict]) -> None:
	metadata["time_explain_strategy_impacts_based"] = 0.0
	metadata["time_explain_strategy_decision_based"] = 0.0
	metadata["time_explain_strategy_hybrid"] = 0.0
	metadata["explain_strategy_impacts_based_status"] = "not_attempted"
	metadata["explain_strategy_decision_based_status"] = "not_attempted"
	metadata["explain_strategy_hybrid_status"] = "not_attempted"
	metadata["explainer_leaves_impacts_based"] = 0
	metadata["explainer_leaves_decision_based"] = 0
	metadata["explainer_leaves_hybrid"] = 0
	for mode_name in ["impacts_based", "decision_based", "hybrid"]:
		metadata[f"explainer_choices_{mode_name}_total"] = 0
		metadata[f"explainer_choices_{mode_name}_forced"] = 0
		metadata[f"explainer_choices_{mode_name}_arbitrary"] = 0
		metadata[f"explainer_choices_{mode_name}_impacts"] = 0
		metadata[f"explainer_choices_{mode_name}_decision"] = 0
	metadata["explain_strategy_impacts_based_error"] = ""
	metadata["explain_strategy_decision_based_error"] = ""
	metadata["explain_strategy_hybrid_error"] = ""
	for attempt in explain_attempts:
		mode_name = attempt["mode"]
		metadata[f"time_explain_strategy_{mode_name}"] = attempt["duration_ms"]
		metadata[f"explain_strategy_{mode_name}_status"] = attempt.get("status", "success" if attempt["success"] else "failed")
		metadata[f"explain_strategy_{mode_name}_error"] = attempt["error"]
		metadata[f"explainer_leaves_{mode_name}"] = attempt.get("leaves_total", 0)
		metadata[f"explainer_choices_{mode_name}_total"] = attempt.get("choices_total", 0)
		metadata[f"explainer_choices_{mode_name}_forced"] = attempt.get("choices_forced", 0)
		metadata[f"explainer_choices_{mode_name}_arbitrary"] = attempt.get("choices_arbitrary", 0)
		metadata[f"explainer_choices_{mode_name}_impacts"] = attempt.get("choices_impacts", 0)
		metadata[f"explainer_choices_{mode_name}_decision"] = attempt.get("choices_decision", 0)


def refine_bounds(bpmn, parse_tree, pending_choices, pending_natures, initial_bounds, num_refinements = 10, debug=False, not_use_Ur=False):
	t = datetime.now()
	execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES], pending_choices, pending_natures)
	metadata = {"time_create_execution_tree" : (datetime.now() - t).total_seconds()*1000}
	print(f"{datetime.now()} CreateExecutionTree: {metadata['time_create_execution_tree']} ms")
	t = datetime.now()
	evaluate_cumulative_expected_impacts(execution_tree)
	metadata["time_evaluate_cei_execution_tree"] = (datetime.now() - t).total_seconds()*1000
	print(f"{datetime.now()} CreateExecutionTree:CEI: {metadata['time_evaluate_cei_execution_tree']} ms")

	cumulative_found_strategy_time = 0

	intervals = [ [0.0, bound_value] for bound_value in initial_bounds ]
	bounds = []
	for i in range(len(intervals)):
		bounds.append(intervals[i][1])

	for iteration in range(num_refinements):
		for current_impact in range(len(intervals)):
			test_bounds = []
			for i in range(len(intervals)):
				test_bounds.append(intervals[i][1])

			test_bounds[current_impact] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
			t = datetime.now()
			frontier_solution, expected_impacts, frontier_values, possible_min_solution = found_strategy([execution_tree], np.array(test_bounds))
			found_strategy_time = (datetime.now() - t).total_seconds()*1000
			cumulative_found_strategy_time += found_strategy_time

			if frontier_solution is not None:# Success Condition
				intervals[current_impact][1] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
				bounds = test_bounds
				s = "Success"
			else:
				intervals[current_impact][0] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
				s = "Fail"

			print(f"{datetime.now()} FoundStrategy:iteration:{iteration}: {found_strategy_time} ms " + s)


	t = datetime.now()
	final_frontier_solution, expected_impacts, frontier_values, possible_min_solution = found_strategy([execution_tree], np.array(bounds))
	found_strategy_time = (datetime.now() - t).total_seconds()*1000
	cumulative_found_strategy_time += found_strategy_time
	print(f"{datetime.now()} FoundStrategy: {found_strategy_time} ms")
	metadata["found_strategy_time"] = cumulative_found_strategy_time
	found_strategy_calls = (num_refinements * len(intervals)) + 1
	metadata["found_strategy_calls"] = found_strategy_calls
	metadata["found_strategy_time_avg"] = (
		cumulative_found_strategy_time / found_strategy_calls if found_strategy_calls > 0 else 0
	)

	if final_frontier_solution is None:
		raise Exception("No solution found, bounds: " + str(bounds))

	post_frontier_stage_timings = []
	frontier_found_at = datetime.now()
	metadata["frontier_found_at"] = frontier_found_at.isoformat(timespec="milliseconds")
	print(f"{metadata['frontier_found_at']} Frontier found, start post-frontier timings")

	t = datetime.now()
	_, strategy = build_strategy(final_frontier_solution)
	metadata["build_strategy_time"] = record_stage_timing(post_frontier_stage_timings, "build_strategy", t)
	print(f"{datetime.now()} Build Strategy: {metadata['build_strategy_time']} ms")
	strategy = None if len(strategy) == 0 else strategy

	if strategy is not None:
		t = datetime.now()
		_, bdds, explain_attempts, attempt_bdds_by_mode = explain_strategy_with_attempts(parse_tree, strategy, bpmn[IMPACTS_NAMES])
		for attempt in explain_attempts:
			attempt["choices_total"] = 0
			attempt["choices_forced"] = 0
			attempt["choices_arbitrary"] = 0
			attempt["choices_impacts"] = 0
			attempt["choices_decision"] = 0
			if not attempt.get("success", False):
				continue

			mode_name = attempt["mode"]
			mode_bdds = attempt_bdds_by_mode.get(mode_name)
			if mode_bdds is None:
				continue

			mode_pending_choices = set(pending_choices) if pending_choices is not None else set()
			mode_pending_natures = set(pending_natures) if pending_natures is not None else set()
			mode_strategy_tree, _, _, _, _, _, _ = full_strategy(
				parse_tree,
				mode_bdds,
				len(bpmn[IMPACTS_NAMES]),
				mode_pending_choices,
				mode_pending_natures,
			)
			mode_counts = get_strategy_choice_typology(mode_strategy_tree)
			attempt["choices_total"] = mode_counts["choices_total"]
			attempt["choices_forced"] = mode_counts["choices_forced"]
			attempt["choices_arbitrary"] = mode_counts["choices_arbitrary"]
			attempt["choices_impacts"] = mode_counts["choices_impacts"]
			attempt["choices_decision"] = mode_counts["choices_decision"]

		metadata["time_explain_strategy"] = record_stage_timing(post_frontier_stage_timings, "explain_strategy_total", t)
		metadata["explain_strategy_attempts"] = explain_attempts
		set_explain_strategy_mode_timings(metadata, explain_attempts)
		explainer_leaves_total, explainer_leaves_per_choice = bdds_count_leaves(bdds)
		metadata["explainer_leaves_total"] = explainer_leaves_total
		metadata["explainer_leaves_per_choice"] = explainer_leaves_per_choice
		print(f"{datetime.now()} Explain Strategy: {metadata['time_explain_strategy']} ms")
		print(f"{datetime.now()} Explainer leaves total: {metadata['explainer_leaves_total']}")
		for attempt in explain_attempts:
			outcome = attempt.get("status", "success" if attempt["success"] else "failed")
			print(f"{attempt['captured_at']} ExplainStrategy:{attempt['mode']}:{outcome}: {attempt['duration_ms']} ms")

		t = datetime.now()
		strategy_tree, children, expected_impacts, expected_time, pending_choices, pending_natures, _ = full_strategy(parse_tree, bdds, len(bpmn[IMPACTS_NAMES]), pending_choices, pending_natures)
		metadata["strategy_tree_time"] = record_stage_timing(post_frontier_stage_timings, "build_strategy_tree", t)
		print(f"{datetime.now()} StrategyTree: {metadata['strategy_tree_time']} ms\n")

		t = datetime.now()
		frontier_size = get_strategy_scenarios_count(strategy_tree)
		frontier_size_time = record_stage_timing(post_frontier_stage_timings, "count_strategy_scenarios", t)
		metadata["frontier_size_time"] = frontier_size_time
		metadata["frontier_size"] = frontier_size
		print(f"{datetime.now()} Strategy frontier size (stopping at arbitrary choices): {frontier_size} [{frontier_size_time} ms]")
	else:
		print(f"{datetime.now()} No needed: ")
		metadata["frontier_size"] = 1 # 1 scenario valid for any choice if no strategy is defined
		metadata["time_explain_strategy"] = 0.0
		metadata["strategy_tree_time"] = 0.0
		metadata["explain_strategy_attempts"] = []
		set_explain_strategy_mode_timings(metadata, [])
		metadata["explainer_leaves_total"] = 0
		metadata["explainer_leaves_per_choice"] = {}

	metadata["post_frontier_stage_timings"] = post_frontier_stage_timings
	metadata["post_frontier_timing_samples"] = len(post_frontier_stage_timings)
	metadata["post_frontier_total_time"] = sum(stage["duration_ms"] for stage in post_frontier_stage_timings)
	print(f"{datetime.now()} FoundStrategy timings: calls={metadata['found_strategy_calls']}, total={metadata['found_strategy_time']} ms, avg={metadata['found_strategy_time_avg']} ms")
	print(f"{datetime.now()} Post-frontier timings: checkpoints={metadata['post_frontier_timing_samples']}, total={metadata['post_frontier_total_time']} ms")
	for stage_timing in post_frontier_stage_timings:
		print(f"{stage_timing['captured_at']} PostFrontier:{stage_timing['stage']}: {stage_timing['duration_ms']} ms")

	metadata["initial_bounds"] = initial_bounds
	metadata["final_bounds"] = bounds

	return metadata
