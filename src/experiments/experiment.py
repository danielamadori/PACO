import datetime
import json

from experiments.telegram.telegram_bot import send_telegram_message
from paco.parser.create import create
from utils import check_syntax as cs
from experiments.etl.cpi_translations import cpi_to_standard_format
from paco.optimizer.refinements import refine_bounds
from experiments.sampler_expected_impact import sample_expected_impact
from paco.parser.bpmn_parser import create_parse_tree
from utils.env import DURATIONS


def single_experiment(D, num_refinements = 10):
	bpmn = cpi_to_standard_format(D)
	bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration

	parse_tree, pending_choices, pending_natures = create_parse_tree(bpmn)
	json_parse_tree = json.loads(parse_tree.to_json())
	initial_bounds = sample_expected_impact(json_parse_tree, track_choices=False)
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
    with open('CPIs/current_benchmark.cpi', 'w') as f:
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

    # Run refinement analysis
    print(f"\nRunning benchmark for x={x}, y={y}, w={w}")
    try:
        times = single_experiment(D, num_refinements=10)
    except ValueError as e:
        s = f"Error during benchmark x={x}, y={y}, w={w}: {str(e)}"
        send_telegram_message(s)
        raise ValueError(s)

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
			strategy_tree_time = ?, initial_bounds = ?, final_bounds = ?
		WHERE x = ? AND y = ? AND w = ?
		""",
        (vte,
         times['time_create_execution_tree'],
         times['time_evaluate_cei_execution_tree'],
         times['found_strategy_time'],
         times['build_strategy_time'],
         times['time_explain_strategy'],
         times['strategy_tree_time'],
         str(times['initial_bounds']),
         str(times['final_bounds']),
         x, y, w)
    )
    conn.commit()

    print(f"\nCompleted benchmark x={x}, y={y}, w={w}")
    print(f"Metadata: {T}")
    print(f"Start time: {vts}")
    print(f"End time: {vte}")
