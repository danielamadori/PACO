from src.paco.evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from src.paco.explainer.explain_strategy import explain_strategy
from src.paco.explainer.full_strategy import full_strategy
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


def record_stage_timing(stage_timings: list[dict], stage_name: str, started_at: datetime) -> float:
	ended_at = datetime.now()
	duration_ms = (ended_at - started_at).total_seconds() * 1000
	stage_timings.append({
		"stage": stage_name,
		"captured_at": ended_at.isoformat(timespec="milliseconds"),
		"duration_ms": duration_ms,
	})
	return duration_ms


def refine_bounds(bpmn, parse_tree, pending_choices, pending_natures, initial_bounds, num_refinements = 10):
	t = datetime.now()
	execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES], pending_choices, pending_natures)
	metadata = {"time_create_execution_tree" : (datetime.now() - t).total_seconds()*1000}
	print(f"{datetime.now()} CreateExecutionTree: {metadata["time_create_execution_tree"]} ms")
	t = datetime.now()
	evaluate_cumulative_expected_impacts(execution_tree)
	metadata["time_evaluate_cei_execution_tree"] = (datetime.now() - t).total_seconds()*1000
	print(f"{datetime.now()} CreateExecutionTree:CEI: {metadata["time_evaluate_cei_execution_tree"]} ms")

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
	print(f"{datetime.now()} Build Strategy: {metadata["build_strategy_time"]} ms")

	if strategy is not None:
		t = datetime.now()
		worst_type_strategy, bdds = explain_strategy(parse_tree, strategy, bpmn[IMPACTS_NAMES])
		metadata["time_explain_strategy"] = record_stage_timing(post_frontier_stage_timings, "explain_strategy", t)
		print(f"{datetime.now()} Explain Strategy: {metadata['time_explain_strategy']} ms")

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
