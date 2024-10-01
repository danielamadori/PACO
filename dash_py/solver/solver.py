import os
import numpy as np
from explainer.strategy_tree import write_strategy_tree
from explainer.full_strategy import full_strategy
from parser.parse_tree import create_parse_tree
from solver.build_strategy import build_strategy
from explainer.explain_strategy import explain_strategy
from evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from solver.execution_tree import create_execution_tree, write_execution_tree
from solver.found_strategy import found_strategy
from solver.pareto import get_non_dominated_impacts
from utils import check_syntax as cs
from utils.env import IMPACTS_NAMES, DURATIONS
from datetime import datetime
from utils.print_sese_diagram import print_sese_diagram


def solve(bpmn: dict, bound: np.ndarray, name_svg: str):
    print(f"{datetime.now()} CreateParseTree:")
    t = datetime.now()
    parse_tree = create_parse_tree(bpmn)
    t1 = datetime.now()
    print(f"{t1} CreateParseTree:completed: {(t1 - t).total_seconds()*1000} ms")

    print(f"{datetime.now()} CreateExecutionTree:")
    t = datetime.now()
    execution_tree = create_execution_tree(parse_tree, bpmn[IMPACTS_NAMES])
    t1 = datetime.now()
    print(f"{t1} CreateExecutionTree:completed: {(t1 - t).total_seconds()*1000} ms")
    t = datetime.now()
    evaluate_cumulative_expected_impacts(execution_tree)
    t1 = datetime.now()
    print(f"{t1} CreateExecutionTree:CEI evaluated: {(t1 - t).total_seconds()*1000} ms")
    print(f"{t1} FoundStrategy:")
    t = datetime.now()
    frontier_solution, frontier_solution_value_bottom_up = found_strategy([execution_tree], bound)
    t1 = datetime.now()
    print(f"{t1} FoundStrategy:completed: {(t1 - t).total_seconds()*1000} ms")
    write_execution_tree(execution_tree, frontier_solution)

    if frontier_solution is None:
        non_dominated_impacts = get_non_dominated_impacts(frontier_solution_value_bottom_up)
        #TODO plot_pareto_frontier
        return False, non_dominated_impacts, [], name_svg

    print(f"Success:\t\t{bpmn[IMPACTS_NAMES]}\nBound Impacts:\t{bound}\nExp. Impacts:\t{frontier_solution_value_bottom_up[0]}")

    print(f'{datetime.now()} BuildStrategy:')
    t = datetime.now()
    _, strategy = build_strategy(frontier_solution)
    t1 = datetime.now()
    print(f"{t1} Build Strategy:completed: {(t1 - t).total_seconds()*1000} ms")
    if len(strategy) == 0:
        return True, frontier_solution_value_bottom_up, [], name_svg

    print(f'{t1} Explain Strategy: ')
    t = datetime.now()
    type_strategy, bdds = explain_strategy(parse_tree, strategy, bpmn[IMPACTS_NAMES])
    t1 = datetime.now()
    print(f"{t1} Explain Strategy:completed: {(t1 - t).total_seconds()*1000} ms\n")
    choices = [choice.name for choice in bdds.keys()]
    print(f"{t1} Strategy: {choices}")

    print(f'{t1} StrategyTree: ')
    t = datetime.now()
    strategy_tree, _ = full_strategy(parse_tree, type_strategy, bdds, len(bpmn[IMPACTS_NAMES]))
    t1 = datetime.now()
    print(f"{t1} StrategyTree:completed: {(t1 - t).total_seconds()*1000} ms\n")
    write_strategy_tree(strategy_tree)
    #name_svg =  "assets/bpmnSvg/bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    #print_sese_diagram(**bpmn, outfile_svg=name_svg)

    return True, frontier_solution_value_bottom_up, choices, name_svg


def paco_solver(bpmn:dict, bound:np.ndarray):
    print(f'{datetime.now()} Testing PACO...')
    print(f'{datetime.now()} Bound {bound}')
    bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration
    print(f'{datetime.now()} bpmn + cpi {bpmn}')

    directory = "assets/bpmnSvg/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    name_svg =  directory + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    print_sese_diagram(**bpmn, outfile_svg=name_svg)

    found, expected_impacts, choices, name_svg = solve(bpmn, bound, name_svg)

    if not found:
        text_result = ""
        for i in range(len(expected_impacts)):
            text_result += f"Exp. Impacts {i}:\t{expected_impacts[i]}\n"
        print(f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nBound Impacts:\t{bound}\n" + text_result)
    else:
        expected_impact = expected_impacts[0]
        impacts = " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impact]))
        if len(choices) == 0:
            text_result = f"Any choice taken will provide a winning strategy with an expected impact of: {impacts}"
        else:
            text_result = f"This is the strategy, with an expected impact of: {impacts}"
        print(str(datetime.now()) + " " + text_result)

    return text_result, found, choices, name_svg
