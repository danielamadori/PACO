import json
from datetime import datetime

from experiments.cpi_translations import cpi_to_standard_format
from experiments.read import read_cpi_bundles
from experiments.refinements import refinements
from experiments.sampler_expected_impact import sample_expected_impact
from paco.parser.bpmn_parser import create_parse_tree

start_time = datetime.now()

bundles = read_cpi_bundles(x=2,y=3)
for i in range(len(bundles)):
	bpmn = cpi_to_standard_format(bundles[i])
	print("Process: ", i)

	parse_tree, pending_choices, pending_natures = create_parse_tree(bpmn)
	json_parse_tree = json.loads(parse_tree.to_json())
	initial_bounds = sample_expected_impact(json_parse_tree, track_choices=False)
	if not initial_bounds:
		raise ValueError("No impacts found in the model")

	refinements(bpmn, initial_bounds, num_refinements = 10)


final_time = datetime.now()

print("Time taken: ", final_time - start_time)