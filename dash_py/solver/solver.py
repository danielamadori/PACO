import os
import numpy as np
from explainer.strategy_tree import write_strategy_tree
from explainer.full_strategy import full_strategy
from explainer.strategy_type import TypeStrategy
from parser.parse_tree import create_parse_tree
from solver.build_strategy import build_strategy
from explainer.explain_strategy import explain_strategy
from evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from solver.execution_tree import create_execution_tree, write_execution_tree, ExecutionTree
from solver.found_strategy import found_strategy
from solver.pareto import get_non_dominated_impacts, get_dominated_impacts
from utils import check_syntax as cs
from utils.env import IMPACTS_NAMES, DURATIONS
from datetime import datetime
from utils.print_sese_diagram import print_sese_diagram


def create(bpmn: dict):
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
    write_execution_tree(execution_tree)

    return parse_tree, execution_tree


def solve(parse_tree, execution_tree: ExecutionTree, bound: np.ndarray, impacts_names: list, name_svg: str):
    print(f"{datetime.now()} FoundStrategy:")
    t = datetime.now()
    frontier_solution, frontier_cei_bottom_up, frontier_cei_top_down = found_strategy([execution_tree], bound)
    t1 = datetime.now()
    print(f"{t1} FoundStrategy:completed: {(t1 - t).total_seconds()*1000} ms")

    frontier_dominated_cei_top_down = get_dominated_impacts(frontier_cei_top_down)

    if frontier_solution is None:
        frontier_non_dominated_cei_bottom_up = get_non_dominated_impacts(frontier_cei_bottom_up)
        #TODO plot_pareto_frontier
        return False, frontier_non_dominated_cei_bottom_up, frontier_dominated_cei_top_down, [], name_svg

    print(f"Success:\t\t{impacts_names}\nBound Impacts:\t{bound}\nExp. Impacts:\t{frontier_cei_bottom_up[0]}")
    write_execution_tree(execution_tree, frontier_solution)


    print(f'{datetime.now()} BuildStrategy:')
    t = datetime.now()
    _, strategy = build_strategy(frontier_solution)
    t1 = datetime.now()
    print(f"{t1} Build Strategy:completed: {(t1 - t).total_seconds()*1000} ms")
    if len(strategy) == 0:
        return True, frontier_cei_bottom_up, frontier_dominated_cei_top_down, [], name_svg

    print(f'{t1} Explain Strategy: ')
    t = datetime.now()
    type_strategy, bdds = explain_strategy(parse_tree, strategy, impacts_names)#TypeStrategy.DECISION_BASED
    t1 = datetime.now()
    print(f"{t1} Explain Strategy:completed: {(t1 - t).total_seconds()*1000} ms\n")
    choices = [choice.name for choice in bdds.keys()]
    print(f"{t1} Strategy: {choices}, type: {type_strategy}")

    print(f'{t1} StrategyTree: ')
    t = datetime.now()
    strategy_tree, _ = full_strategy(parse_tree, type_strategy, bdds, len(impacts_names))
    t1 = datetime.now()
    print(f"{t1} StrategyTree:completed: {(t1 - t).total_seconds()*1000} ms\n")
    write_strategy_tree(strategy_tree)
    #name_svg =  "assets/bpmnSvg/bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    #print_sese_diagram(**bpmn, outfile_svg=name_svg)

    return True, frontier_cei_bottom_up, frontier_dominated_cei_top_down, choices, name_svg


def paco(bpmn:dict, bound:np.ndarray, parse_tree=None, execution_tree=None):
    #print(f'{datetime.now()} Testing PACO...')
    print(f'{datetime.now()} Bound {bound}')
    bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration
    #print(f'{datetime.now()} bpmn + cpi {bpmn}')

    directory = "assets/bpmnSvg/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    name_svg =  directory + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    print_sese_diagram(**bpmn, outfile_svg=name_svg)

    if parse_tree is None or execution_tree is None:
        parse_tree, execution_tree = create(bpmn)

    found, min_cei, max_cei, choices, name_svg = solve(parse_tree, execution_tree, bound, bpmn[IMPACTS_NAMES], name_svg)
    #flexible

    if not found:
        text_result = ""
        for i in range(len(min_cei)):
            text_result += f"Exp. Impacts {i}:\t{np.round(min_cei[i], 2)}\n"
        print(f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nBound Impacts:\t{bound}\n" + text_result)
        text_result = ""
        for i in range(len(max_cei)):
            text_result += f"Guaranteed Bound {i}:\t{np.ceil(max_cei[i])}\n"
    else:
        expected_impact = min_cei[0]
        impacts = " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impact]))
        if len(choices) == 0:
            text_result = f"Any choice taken will provide a winning strategy with an expected impact of: {impacts}"
        else:
            text_result = f"This is the strategy, with an expected impact of: {impacts}"
        print(str(datetime.now()) + " " + text_result)

    #TODO Return strategy tree if found
    return text_result, parse_tree, execution_tree, found, min_cei, max_cei, choices, name_svg
