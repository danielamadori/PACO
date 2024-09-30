from random import seed
import numpy as np
from explainer.strategy_tree import write_strategy_tree
from explainer.full_strategy import full_strategy
from utils.print_sese_diagram import print_sese_diagram
from solver.build_strategy import build_strategy
from explainer.explain_strategy import explain_strategy
from evaluations.evaluate_cumulative_expected_impacts import evaluate_cumulative_expected_impacts
from solver.execution_tree import create_execution_tree, write_execution_tree
from solver.found_strategy import found_strategy
from solver.pareto import get_non_dominated_impacts

seed(42)

import os, sys
from datetime import datetime
from solver.tree_lib import print_sese_custom_tree
from solver.tree_lib import from_lark_parsed_to_custom_tree as Lark_to_CTree
from utils.env import LOOPS_PROB, SESE_PARSER, TASK_SEQ, \
    IMPACTS, NAMES, PROBABILITIES, DURATIONS, DELAYS, H, IMPACTS_NAMES

current_directory = os.path.dirname(os.path.realpath('tree_lib.py'))
# Add the current directory to the Python path
sys.path.append(current_directory)

os.environ["PATH"] += os.pathsep + 'C:/Program Files/Graphviz/bin/'

# sese_diagram_grammar = r"""
# ?start: xor

# ?xor: parallel
#     | xor "/" "[" NAME "]" parallel -> choice
#     | xor "^" "[" NAME "]" parallel -> natural

# ?parallel: sequential
#     | parallel "||" sequential  -> parallel

# ?sequential: region
#     | sequential "," region -> sequential

# ?region:
#      | NAME   -> task
#      | "(@" xor "@)" -> loop
#      | "(@" "[" NAME "]"  xor "@)" -> loop_probability
#      | "(" xor ")"

# %import common.CNAME -> NAME
# %import common.NUMBER
# %import common.WS_INLINE

# %ignore WS_INLINE
# """

#SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')

# ex = "((Task8 ^ [N1] Task3), (Task1 / [C3] Task2),(Task6 / [C1] Task7))|| (Task9, (Task4 / [C2] Task5))"
# exi = {"Task1": [0,1], "Task2": [0,2], "Task3": [3,3], "Task4": [1,2], "Task5": [2,1], "Task6": [1,0], "Task7": [1,5], "Task8": [0,3], "Task9": [0,3]}
# exd = {"Task1": 1, "Task2": 1,"Task4": 1, "Task3": 1, "Task5": 1, "Task6": 1, "Task7": 1, "Task8": 3, "Task9": 2}
# exn = {"C1": 'Choice1', "C2": 'Choice2', "C3": 'Choice3'}
# exdl = {"C1": np.Inf, "C2": 0, "C3": 0} #maximum delays for the choices
# exp = {"N1": 0.2}

# ex = "(Task1, Task2), (Task3, Task4)"
# exi = {"Task1": [0,1], "Task2": [0,1], "Task3": [0,1], "Task4": [0,1]}
# exd = {"Task1": 1, "Task2": 1, "Task3": 1, "Task4": 1}
# exn = {}
# exdl = {} #maximum delays for the choices
# exp = {}

ex = "(Task1 ^ [N1] Task2) || (Task3 / [C1] Task4)"
exi = {"Task1": [1,1], "Task2": [0,1], "Task3": [2,1], "Task4": [0,1]}
exd = {"Task1": 3, "Task2": 1, "Task3": 3, "Task4": 4}
exn = {"C1": 'Choice1'}
exdl = {"C1": 2} #maximum delays for the choices
exp = {"N1":0.3}

# ex = "Task1 || (Task2, (Task3 / [C1] Task4))"
# exi = {"Task1": [0,1], "Task2": [0,2], "Task3": [3,3], "Task4": [1,2]}
# exd = {"Task1": 1, "Task2": 1,"Task4": 1, "Task3": 1}
# exn = {"C1": 'Choice1'}
# exdl = {"C1": 5} #maximum delays for the choices
# exp = {}

# ex = "(T1 ^ [N1] T2),((T3 / [C1] T4)||(T5 / [C2] T6))"
# exi = {"T1": [2,3], "T2": [4,1], "T3": [2,3], "T4": [3,1], "T5": [2,1], "T6": [1,2]}
# exd = {"T1": 1, "T2": 1,"T4": 1, "T3": 1, "T5":4, "T6":2}
# exn = {"C1": 'Choice1', "C2": 'Choice2'}
# exdl = {"C1": 5, "C2": 2} #maximum delays for the choices
# exp = {"N1": 0.3}

args = {
    'expression': ex,
    'impacts': exi,
    'names': exn,
    'probabilities': exp,
    'loop_thresholds': {},
    'durations': exd,
    'delays': exdl,
    'h': 0
}

# tree = SESE_PARSER.parse(args['expression'])
# custom_tree, last_id = Lark_to_CTree(tree, args['probabilities'], args['impacts'], args['durations'], args['names'], args['delays'], h=args['h'])
# number_of_nodes = last_id + 1


def automata_search_strategy(bpmn: dict, bound: np.ndarray, name_svg: str) -> str:
    # Parse the task sequence from the BPMN diagram
    tree = SESE_PARSER.parse(bpmn[TASK_SEQ])
    print(tree.pretty)

    # Convert the parsed tree into a custom tree and get the last ID
    parse_tree, last_id = Lark_to_CTree(tree, bpmn[PROBABILITIES], bpmn[IMPACTS], bpmn[DURATIONS], bpmn[NAMES], bpmn[DELAYS], h=bpmn[H], loops_prob=bpmn[LOOPS_PROB])
    print_sese_custom_tree(parse_tree, outfile='parsed_tree.png')

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
