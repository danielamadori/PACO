import datetime
import json
from src.experiments.telegram.telegram_bot import send_telegram_message
from src.paco.parser.create import create
from src.utils import check_syntax as cs
from src.experiments.etl.cpi_translations import cpi_to_standard_format
from src.paco.optimizer.refinements import refine_bounds
from src.paco.evaluations.sampler_expected_impact import sample_expected_impact
from src.paco.parser.bpmn_parser import create_parse_tree
from src.utils.env import DURATIONS


def single_experiment(D, num_refinements = 10):
    bpmn = cpi_to_standard_format(D)
    bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration

    parse_tree, pending_choices, pending_natures, pending_loops = create_parse_tree(bpmn)
    initial_bounds = parse_tree.sample_expected_impact()
    if not initial_bounds:
        raise ValueError("No impacts found in the model")

    parse_tree, pending_choices, pending_natures, execution_tree, times = create(bpmn, parse_tree, pending_choices, pending_natures)

    return refine_bounds(bpmn, parse_tree, pending_choices, pending_natures, initial_bounds, num_refinements)


def single_execution(cursor, conn, x, y, w, bundle):
    # Check if experiment already exists
    cursor.execute(
        "SELECT COUNT(*) FROM experiments WHERE x=? AND y=? AND w=?",
        (x, y, w)
    )
    if cursor.fetchone()[0] > 0:
        print(f"Experiment x={x}, y={y}, w={w} already exists, trying another...")
        return

    # Get dictionary and metadata
    D = bundle[w].copy()
    T = D.pop('metadata')

    # Write to current_benchmark.cpi
    with open('validation/cpi-to-prism/CPIs/current_benchmark.cpi', 'w') as f:
        json.dump(D, f)

    # Record start time
    vts = datetime.datetime.now().isoformat()

    # Insert initial record
    cursor.execute(
        """
		INSERT INTO experiments (
			x, y, w, z, num_impacts, choice_distribution, 
			generation_mode, duration_interval_min, duration_interval_max,
			vts
		) 
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
		""",
        (
            x, y, w,
            T['z'],
            T['num_impacts'],
            T['choice_distribution'],
            T['generation_mode'],
            T['duration_interval'][0],
            T['duration_interval'][1],
            vts
        )
    )
    conn.commit()
    error = ""
    # Run refinement analysis
    print(f"\nRunning benchmark for x={x}, y={y}, w={w}")
    times = {}
    try:
        times = single_experiment(D, num_refinements=10)
    except Exception as e:
        s = f"Error during benchmark x={x}, y={y}, w={w}: {str(e)}"
        send_telegram_message(s)
        error = s
        times['time_create_execution_tree'] = 0.0
        times['time_evaluate_cei_execution_tree'] = 0.0
        times['found_strategy_time'] = 0.0
        times['build_strategy_time'] = 0.0
        times['time_explain_strategy'] = 0.0
        times['time_explain_strategy_impacts_based'] = 0.0
        times['time_explain_strategy_decision_based'] = 0.0
        times['time_explain_strategy_hybrid'] = 0.0
        times['explain_strategy_impacts_based_status'] = "not_attempted"
        times['explain_strategy_decision_based_status'] = "not_attempted"
        times['explain_strategy_hybrid_status'] = "not_attempted"
        times['explainer_leaves_impacts_based'] = 0
        times['explainer_leaves_decision_based'] = 0
        times['explainer_leaves_hybrid'] = 0
        times['explainer_leaves_total'] = 0
        times['explainer_choices_impacts_based_total'] = 0
        times['explainer_choices_impacts_based_forced'] = 0
        times['explainer_choices_impacts_based_arbitrary'] = 0
        times['explainer_choices_impacts_based_impacts'] = 0
        times['explainer_choices_impacts_based_decision'] = 0
        times['explainer_choices_decision_based_total'] = 0
        times['explainer_choices_decision_based_forced'] = 0
        times['explainer_choices_decision_based_arbitrary'] = 0
        times['explainer_choices_decision_based_impacts'] = 0
        times['explainer_choices_decision_based_decision'] = 0
        times['explainer_choices_hybrid_total'] = 0
        times['explainer_choices_hybrid_forced'] = 0
        times['explainer_choices_hybrid_arbitrary'] = 0
        times['explainer_choices_hybrid_impacts'] = 0
        times['explainer_choices_hybrid_decision'] = 0
        times['strategy_tree_time'] = 0.0
        times['initial_bounds'] = 0
        times['final_bounds'] = 0
        times['frontier_size'] = 0

    for k, v in times.items():
        print(f"{k}: {v}")


    # Record end time
    vte = datetime.datetime.now().isoformat()

    # Update record with end time
    cursor.execute(
        """
			UPDATE experiments 
			SET vte = ?, time_create_execution_tree = ?, time_evaluate_cei_execution_tree = ?,
					found_strategy_time = ?, build_strategy_time = ?, time_explain_strategy = ?, 
					time_explain_strategy_impacts_based = ?, time_explain_strategy_decision_based = ?,
					time_explain_strategy_hybrid = ?, explain_strategy_impacts_based_status = ?,
					explain_strategy_decision_based_status = ?, explain_strategy_hybrid_status = ?,
					explainer_leaves_impacts_based = ?, explainer_leaves_decision_based = ?, explainer_leaves_hybrid = ?,
					explainer_leaves_total = ?,
					explainer_choices_impacts_based_total = ?, explainer_choices_impacts_based_forced = ?,
					explainer_choices_impacts_based_arbitrary = ?, explainer_choices_impacts_based_impacts = ?,
					explainer_choices_impacts_based_decision = ?, explainer_choices_decision_based_total = ?,
					explainer_choices_decision_based_forced = ?, explainer_choices_decision_based_arbitrary = ?,
					explainer_choices_decision_based_impacts = ?, explainer_choices_decision_based_decision = ?,
					explainer_choices_hybrid_total = ?, explainer_choices_hybrid_forced = ?,
					explainer_choices_hybrid_arbitrary = ?, explainer_choices_hybrid_impacts = ?,
					explainer_choices_hybrid_decision = ?, strategy_tree_time = ?, initial_bounds = ?, final_bounds = ?, error = ?,
					frontier_size = ?
				WHERE x = ? AND y = ? AND w = ?
				""",
        (vte,
         times.get('time_create_execution_tree', 0.0),
         times.get('time_evaluate_cei_execution_tree', 0.0),
         times.get('found_strategy_time', 0.0),
         times.get('build_strategy_time', 0.0),
         times.get('time_explain_strategy', 0.0),
         times.get('time_explain_strategy_impacts_based', 0.0),
         times.get('time_explain_strategy_decision_based', 0.0),
         times.get('time_explain_strategy_hybrid', 0.0),
         times.get('explain_strategy_impacts_based_status', 'not_attempted'),
         times.get('explain_strategy_decision_based_status', 'not_attempted'),
         times.get('explain_strategy_hybrid_status', 'not_attempted'),
         times.get('explainer_leaves_impacts_based', 0),
         times.get('explainer_leaves_decision_based', 0),
         times.get('explainer_leaves_hybrid', 0),
         times.get('explainer_leaves_total', 0),
         times.get('explainer_choices_impacts_based_total', 0),
         times.get('explainer_choices_impacts_based_forced', 0),
         times.get('explainer_choices_impacts_based_arbitrary', 0),
         times.get('explainer_choices_impacts_based_impacts', 0),
         times.get('explainer_choices_impacts_based_decision', 0),
         times.get('explainer_choices_decision_based_total', 0),
         times.get('explainer_choices_decision_based_forced', 0),
         times.get('explainer_choices_decision_based_arbitrary', 0),
         times.get('explainer_choices_decision_based_impacts', 0),
         times.get('explainer_choices_decision_based_decision', 0),
         times.get('explainer_choices_hybrid_total', 0),
         times.get('explainer_choices_hybrid_forced', 0),
         times.get('explainer_choices_hybrid_arbitrary', 0),
         times.get('explainer_choices_hybrid_impacts', 0),
         times.get('explainer_choices_hybrid_decision', 0),
         times.get('strategy_tree_time', 0.0),
         str(times.get('initial_bounds', 0)),
         str(times.get('final_bounds', 0)),
         str(error),
         times.get('frontier_size', 0),
         x, y, w)
    )
    conn.commit()

    print(f"\nCompleted benchmark x={x}, y={y}, w={w}")
    print(f"Metadata: {T}")
    print(f"Start time: {vts}")
    print(f"End time: {vte}")
