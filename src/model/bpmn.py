from copy import deepcopy

import dash
import dash_bootstrap_components as dbc
from lark import ParseTree
from src.controller.db import load_bpmn_dot
from src.env import EXPRESSION, SESE_PARSER, IMPACTS, IMPACTS_NAMES, DURATIONS, DELAYS, PROBABILITIES, \
	LOOP_PROBABILITY, LOOP_ROUND, HEADERS


def filter_bpmn(bpmn_store, tasks, choices, natures, loops):
    # Filter the data to keep only the relevant tasks, choices, natures, and loops
    bpmn = deepcopy(bpmn_store)
    bpmn[IMPACTS_NAMES] = sorted(bpmn_store[IMPACTS_NAMES])
    bpmn[IMPACTS] = {
        task: [bpmn_store[IMPACTS][task][impact_name] for impact_name in bpmn[IMPACTS_NAMES]]
        for task in tasks if task in bpmn_store[IMPACTS]
    }
    bpmn[DURATIONS] = {task: bpmn_store[DURATIONS][task] for task in tasks if task in bpmn_store[DURATIONS]}
    bpmn[DELAYS] = {choice: bpmn_store[DELAYS][choice] for choice in choices if choice in bpmn_store[DELAYS]}
    bpmn[PROBABILITIES] = {nature: bpmn_store[PROBABILITIES][nature] for nature in natures if nature in bpmn_store[PROBABILITIES]}
    bpmn[LOOP_PROBABILITY] = {loop: bpmn_store[LOOP_PROBABILITY][loop] for loop in loops if loop in bpmn_store[LOOP_PROBABILITY]}
    bpmn[LOOP_ROUND] = {loop: bpmn_store[LOOP_ROUND][loop] for loop in loops if loop in bpmn_store[LOOP_ROUND]}

    return bpmn



def update_bpmn_data(bpmn_store):
    alert = ''

    if bpmn_store[EXPRESSION] == '':
        return dash.no_update, dash.no_update, alert

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
    for task in tasks:
        if task not in bpmn_store[IMPACTS]:
            bpmn_store[IMPACTS][task] = {}

        for impact_name in bpmn_store[IMPACTS_NAMES]:
            if impact_name in bpmn_store[IMPACTS][task]:
                continue
            bpmn_store[IMPACTS][task][impact_name] = 0.0

        if task not in bpmn_store[DURATIONS]:
            bpmn_store[DURATIONS][task] = [0, 1]

    for task in tasks:
        bpmn_store.setdefault(IMPACTS, {}).setdefault(task, {})
        for impact_name in bpmn_store[IMPACTS_NAMES]:
            bpmn_store[IMPACTS][task].setdefault(impact_name, 0.0)


    for choice in choices:
        if choice not in bpmn_store[DELAYS]:
            bpmn_store[DELAYS][choice] = 0
    for nature in natures:
        if nature not in bpmn_store[PROBABILITIES]:
            bpmn_store[PROBABILITIES][nature] = 0.5
    for loop  in loops:
        if loop not in bpmn_store[LOOP_PROBABILITY]:
            bpmn_store[LOOP_PROBABILITY][loop] = 0.5
        if loop not in bpmn_store[LOOP_ROUND]:
            bpmn_store[LOOP_ROUND][loop] = 1


    if len(bpmn_store[IMPACTS_NAMES]) == 0:
        return bpmn_store, dash.no_update, dbc.Alert(f"Add an impacts", color="danger", dismissable=True)

    bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

    bpmn_dot, exception = load_bpmn_dot(bpmn)
    if bpmn_dot is None:
        alert = dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

    return bpmn_store, {"bpmn" : bpmn_dot}, alert


def validate_expression_and_update(current_expression, bpmn_store):
    print(f"Current expression: {current_expression}, data: {bpmn_store}")
    alert = ''
    if current_expression is None:
        return bpmn_store, None, alert

    current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if current_expression == '':
        return bpmn_store, dbc.Alert("The expression is empty.", color="warning", dismissable=True)

    if current_expression != bpmn_store.get(EXPRESSION, ''):
        try:
            SESE_PARSER.parse(current_expression)
        except Exception as e:
            return bpmn_store, None, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True)
        bpmn_store[EXPRESSION] = current_expression

    return update_bpmn_data(bpmn_store)


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
