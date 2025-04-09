import base64
from copy import deepcopy

import dash_bootstrap_components as dbc
import graphviz
import requests
from lark import ParseTree

from env import URL_SERVER
from src.env import EXPRESSION, SESE_PARSER, IMPACTS, IMPACTS_NAMES, DURATIONS, DELAYS, PROBABILITIES, \
	LOOP_PROBABILITY, LOOP_ROUND, HEADERS


def filter_bpmn(data, tasks, choices, natures, loops):
    # Filter the data to keep only the relevant tasks, choices, natures, and loops
    bpmn = deepcopy(data)
    bpmn[IMPACTS_NAMES] = sorted(data[IMPACTS_NAMES])
    bpmn[IMPACTS] = {
        task: [data[IMPACTS][task][impact_name] for impact_name in bpmn[IMPACTS_NAMES]]
        for task in tasks if task in data[IMPACTS]
    }
    bpmn[DURATIONS] = {task: data[DURATIONS][task] for task in tasks if task in data[DURATIONS]}
    bpmn[DELAYS] = {choice: data[DELAYS][choice] for choice in choices if choice in data[DELAYS]}
    bpmn[PROBABILITIES] = {nature: data[PROBABILITIES][nature] for nature in natures if nature in data[PROBABILITIES]}
    bpmn[LOOP_PROBABILITY] = {loop: data[LOOP_PROBABILITY][loop] for loop in loops if loop in data[LOOP_PROBABILITY]}
    bpmn[LOOP_ROUND] = {loop: data[LOOP_ROUND][loop] for loop in loops if loop in data[LOOP_ROUND]}

    return bpmn



def update_bpmn_data(data):
    alert = ''

    if data[EXPRESSION] == '':
        return data, alert

    tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
    for task in tasks:
        if task not in data[IMPACTS]:
            data[IMPACTS][task] = {}

        for impact_name in data[IMPACTS_NAMES]:
            if impact_name in data[IMPACTS][task]:
                continue
            data[IMPACTS][task][impact_name] = 0.0

        if task not in data[DURATIONS]:
            data[DURATIONS][task] = [0, 1]

    for choice in choices:
        if choice not in data[DELAYS]:
            data[DELAYS][choice] = 0
    for nature in natures:
        if nature not in data[PROBABILITIES]:
            data[PROBABILITIES][nature] = 0.5
    for loop  in loops:
        if loop not in data[LOOP_PROBABILITY]:
            data[LOOP_PROBABILITY][loop] = 0.5
        if loop not in data[LOOP_ROUND]:
            data[LOOP_ROUND][loop] = 1


    if len(data[IMPACTS_NAMES]) < 1:
        return data, dbc.Alert(f"Add an impacts", color="danger", dismissable=True)

    bpmn = filter_bpmn(data, tasks, choices, natures, loops)
    try:
        resp = requests.get(URL_SERVER + "create_bpmn", json={'bpmn': bpmn}, headers=HEADERS)
        resp.raise_for_status()
        dot = resp.json().get('bpmn_dot', '')
    except requests.exceptions.RequestException as e:
        return data, dbc.Alert(f"Processing error: {str(e)}", color="danger", dismissable=True)

    svg = graphviz.Source(dot).pipe(format='svg')
    encoded_svg = base64.b64encode(svg).decode('utf-8')
    data["svg"] = f"data:image/svg+xml;base64,{encoded_svg}"

    return data, alert


def validate_expression_and_update(current_expression, data):
    print(f"Current expression: {current_expression}, data: {data}")
    alert = ''
    if current_expression is None:
        return data, alert

    current_expression = current_expression.replace("\n", "").replace("\t", "").strip().replace(" ", "")
    if current_expression == '':
        return data, dbc.Alert("The expression is empty.", color="warning", dismissable=True)

    if current_expression != data.get(EXPRESSION, ''):
        try:
            SESE_PARSER.parse(current_expression)
        except Exception as e:
            return data, dbc.Alert(f"Parsing error: {str(e)}", color="danger", dismissable=True)
        data[EXPRESSION] = current_expression

    return update_bpmn_data(data)


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
