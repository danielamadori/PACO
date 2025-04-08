import re
import json

from lark import ParseTree

from core.config import ALGORITHMS, ALGORITHMS_MISSING_SYNTAX, DURATIONS, IMPACTS, EXPRESSION, ALL_SYNTAX, SESE_PARSER


def check_algo_is_usable(expression: str, algo: str) -> bool:
    """
    Check if the costructs in the BPMN is suitable fro the algo.
    """
    print('checking expression within algo in progress...')
    if expression == '' or algo == '' or algo not in ALGORITHMS.keys():
        return False
    if algo in ALGORITHMS_MISSING_SYNTAX.keys() and list(ALGORITHMS_MISSING_SYNTAX.get(algo)) != []:
        for element in list(ALGORITHMS_MISSING_SYNTAX.get(algo)):
            #print(element)
            if element in expression:
                return False        
    return True



def extract_nodes(lark_tree: ParseTree) -> (list, list, list, list):
    tasks = []
    choices = []
    natures = []
    loops = []

    if lark_tree.data == 'task':
        return [lark_tree.children[0].value], [], [], []

    if lark_tree.data in {'choice', 'natural'}:
        if lark_tree.data == 'choice':
            choices.append(lark_tree.children[1].value)
        else:
            natures.append(lark_tree.children[1].value)

        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[2])

    elif lark_tree.data in {'sequential', 'parallel'}:
        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[1])
    elif lark_tree.data == 'loop':#TODO
        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = [], [], [], []
    elif lark_tree.data == 'loop_probability':
        loops.append(lark_tree.children[0].value)
        left_task, left_choices, left_natures, left_loops = [], [], [], []
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[1])

    tasks.extend(left_task)
    choices.extend(left_choices)
    natures.extend(left_natures)
    loops.extend(left_loops)
    tasks.extend(right_task)
    choices.extend(right_choices)
    natures.extend(right_natures)
    loops.extend(right_loops)

    return tasks, choices, natures, loops
