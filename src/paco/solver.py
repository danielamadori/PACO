import json
import numpy as np
from paco.execution_tree.execution_tree import ExecutionTree
from paco.explainer.build_explained_strategy import build_explained_strategy
from paco.explainer.explanation_type import ExplanationType
from paco.explainer.bdd.bdds import bdds_to_dict
from paco.parser.create import create
from paco.parser.parse_tree import ParseTree
from paco.searcher.search import search
from utils import check_syntax as cs
from utils.env import IMPACTS_NAMES, DURATIONS
from datetime import datetime


def paco(bpmn:dict, bound:np.ndarray, parse_tree=None, pending_choices=None, pending_natures=None, execution_tree=None, search_only=False, type_strategy=ExplanationType.HYBRID, debug = False):
	bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration

	result = {"bpmn": bpmn, "bound": bound}

	parse_tree, pending_choices, pending_natures, execution_tree, times = create(bpmn, parse_tree, pending_choices, pending_natures, execution_tree, debug)
	result.update({"parse_tree": parse_tree,
					"pending_choices": pending_choices,
					"pending_natures": pending_natures,
					"execution_tree": execution_tree})

	frontier_solution, expected_impacts, possible_min_solution, frontier_values, strategy, search_times = search(execution_tree, bound, bpmn[IMPACTS_NAMES], search_only, debug)

	result.update({"possible_min_solution": possible_min_solution,
				   "guaranteed_bounds": frontier_values})
	times.update(search_times)

	if frontier_solution is None:# Also expected_impacts is None
		text_result = ""
		for i in range(len(possible_min_solution)):
			text_result += f"Exp. Impacts {i}:\t{np.round(possible_min_solution[i], 2)}\n"

		text_result = f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nPossible Bound Impacts:\t{bound}\n" + text_result
		for i in range(len(frontier_values)):
			text_result += f"Guaranteed Bound {i}:\t{np.ceil(frontier_values[i])}\n"

		#print(str(datetime.now()) + " " + text_result)
		return text_result, result, times

	result.update({"frontier_solution": frontier_solution,
				   "expected_impacts": expected_impacts})

	if strategy is None:
		text_result = f"Any choice taken will provide a winning strategy with an expected impact of: "
		text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impacts]))
		#print(str(datetime.now()) + " " + text_result)
		return text_result, result, times


	strategy_tree, strategy_expected_impacts, strategy_expected_time, bdds, explainer_times = build_explained_strategy(parse_tree, strategy, type_strategy, bpmn[IMPACTS_NAMES], pending_choices, pending_natures, debug)
	times.update(explainer_times)

	text_result = f"This is the strategy, with an expected impact of: "
	text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in strategy_expected_impacts]))
	print(str(datetime.now()) + " " + text_result)

	result.update({"strategy_tree": strategy_tree,
				   "strategy_expected_impacts": strategy_expected_impacts,
				   "strategy_expected_time": strategy_expected_time,
				   "bdds": bdds})

	return text_result, result, times



def json_to_paco(json_input, search_only = False, type_strategy=ExplanationType.HYBRID):
	x, y = json_input.get("bpmn"), json_input.get("bound")
	if not x and not y:
		raise ValueError("Missing BPMN and Bound")
	else:
		bpmn = x
		print(y)
		bound = np.array(y.strip("[]").split(","), dtype=np.float64)

	# Create
	x = json_input.get("parse_tree")
	if x:
		parse_tree, pending_choices, pending_natures = ParseTree.from_json(x, len(bpmn[IMPACTS_NAMES]),0)
	else:
		parse_tree, pending_choices, pending_natures = None, None, None

	x = json_input.get("execution_tree")
	if x:
		execution_tree = ExecutionTree.from_json(parse_tree, x, bpmn[IMPACTS_NAMES])
	else:
		execution_tree = None

	text_result, result, times = paco(bpmn, bound,
									  parse_tree=parse_tree, pending_choices=pending_choices,
									  pending_natures=pending_natures, execution_tree=execution_tree,
									  search_only=search_only, type_strategy=type_strategy)


	result_dict = {
		"result": text_result, "times": times,
		"bpmn": result["bpmn"], "bound": str(result["bound"]),
		"parse_tree": result["parse_tree"].to_dict(),
		"execution_tree": result["execution_tree"].to_dict(),
	}

	#Search
	x = result.get("possible_min_solution")
	y = result.get("guaranteed_bounds")
	if x is not None and y is not None:# Search Done
		result_dict.update({
			"possible_min_solution": str([str(bound) for bound in x]),
			"guaranteed_bounds": str([str(bound) for bound in y])
		})

	x = result.get("expected_impacts")
	y = result.get("frontier_solution")
	if x is not None and y is not None:# Search Win
		result_dict.update({
			"expected_impacts" : str(x),
			"frontier_solution" : str([execution_tree.root.id for execution_tree in y])
		})



	x = result.get("strategy_tree")
	y = result.get("strategy_expected_impacts")
	z = result.get("strategy_expected_time")
	w = result.get("bdds")
	if x is not None and y is not None and z is not None and w is not None: # Strategy Explained Done
		result_dict.update({
			"strategy_tree": x.to_dict(),
			"strategy_expected_impacts": str(y),
			"strategy_expected_time": str(z),
			"bdds": bdds_to_dict(w)
		})

	return result_dict