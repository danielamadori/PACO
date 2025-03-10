import json
from paco.parser.create import create
from utils import check_syntax as cs
from experiments.cpi_translations import cpi_to_standard_format
from experiments.refinements import refine_bounds
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