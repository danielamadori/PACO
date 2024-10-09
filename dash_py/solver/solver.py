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


def solve(parse_tree, execution_tree: ExecutionTree, bound: np.ndarray, impacts_names: list, search_only: bool, name_svg: str, type_strategy = TypeStrategy.HYBRID):
    print(f"{datetime.now()} FoundStrategy:")
    t = datetime.now()
    frontier_solution, expected_impacts, solutions, possible_min_solution = found_strategy([execution_tree], bound)
    t1 = datetime.now()
    print(f"{t1} FoundStrategy:completed: {(t1 - t).total_seconds()*1000} ms")

    if frontier_solution is None:
        #TODO plot_pareto_frontier
        return None, possible_min_solution, solutions, [], name_svg
    if search_only:
        return expected_impacts, possible_min_solution, solutions, [], name_svg

    print(f"Success:\t\t{impacts_names}\nBound Impacts:\t{bound}\nExp. Impacts:\t{expected_impacts}")
    write_execution_tree(execution_tree, frontier_solution)

    print(f'{datetime.now()} BuildStrategy:')
    t = datetime.now()
    _, strategy = build_strategy(frontier_solution)
    t1 = datetime.now()
    print(f"{t1} Build Strategy:completed: {(t1 - t).total_seconds()*1000} ms")
    if len(strategy) == 0:
        return expected_impacts, possible_min_solution, solutions, [], name_svg

    print(f'{t1} Explain Strategy: ')
    t = datetime.now()
    worst_type_strategy, bdds = explain_strategy(parse_tree, strategy, impacts_names, type_strategy)
    t1 = datetime.now()
    print(f"{t1} Explain Strategy:completed: {(t1 - t).total_seconds()*1000} ms\n")

    s = ""
    if type_strategy == TypeStrategy.HYBRID:
        s += f"with worst type of choice: {worst_type_strategy}\n"
    else:
        s += f": {worst_type_strategy}"
    print(f"{t1} Strategy {s}"+ "".join(f"{choice.name}:\t{bdd.typeStrategy}\n" for choice, bdd in bdds.items()))

    print(f'{t1} StrategyTree: ')
    t = datetime.now()
    strategy_tree, children, strategy_expected_impacts, strategy_expected_time, _ = full_strategy(parse_tree, bdds, len(impacts_names))
    t1 = datetime.now()
    print(f"{t1} StrategyTree:completed: {(t1 - t).total_seconds()*1000} ms\n")
    print(f"Strategy Expected Impacts: {strategy_expected_impacts}\nStrategy Expected Time: {strategy_expected_time}")
    write_strategy_tree(strategy_tree)
    #name_svg =  "assets/bpmnSvg/bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    #print_sese_diagram(**bpmn, outfile_svg=name_svg)
    choices = [choice.name for choice in bdds.keys()]

    return expected_impacts, possible_min_solution, solutions, choices, name_svg


def paco(bpmn:dict, bound:np.ndarray, parse_tree=None, execution_tree=None, search_only=False):
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

    type_strategy = TypeStrategy.HYBRID #TypeStrategy.CURRENT_IMPACTS
    expected_impacts, possible_min_solution, solutions, choices, name_svg = solve(parse_tree, execution_tree, bound, bpmn[IMPACTS_NAMES], search_only, name_svg, type_strategy)

    if expected_impacts is None:
        text_result = ""
        for i in range(len(possible_min_solution)):
            text_result += f"Exp. Impacts {i}:\t{np.round(possible_min_solution[i], 2)}\n"
        print(f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nPossible Bound Impacts:\t{bound}\n" + text_result)
        text_result = ""
        for i in range(len(solutions)):
            text_result += f"Guaranteed Bound {i}:\t{np.ceil(solutions[i])}\n"
    else:
        impacts = " ".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impacts]))
        if len(choices) == 0 and search_only == False:
            text_result = f"Any choice taken will provide a winning strategy with an expected impact of: {impacts}"
        else:
            text_result = f"This is the strategy, with an expected impact of: {impacts}"
        print(str(datetime.now()) + " " + text_result)

    #TODO Return strategy tree if found
    return text_result, parse_tree, execution_tree, expected_impacts, possible_min_solution, solutions, choices, name_svg
