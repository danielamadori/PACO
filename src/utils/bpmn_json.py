import base64
import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, Output, Input, State, dcc, html
from fastapi import requests

from env import EXPRESSION, IMPACTS, IMPACTS_NAMES, DURATIONS, PROBABILITIES, LOOP_ROUND, DELAYS, LOOP_PROB
from pages.home import min_duration
from utils import check_syntax as cs
from utils.utils_preparing_diagram import prepare_task_duration, prepare_task_probabilities, prepare_task_delays, \
	prepare_task_impacts, prepare_task_loops


@callback(
    [Output('logging', 'children'), Output('lark-frame', 'src'), Output('bpmn-lark-store', 'data', allow_duplicate=True)],
    Input('create-diagram-button', 'n_clicks'),
    State('input-bpmn', 'value'), # task seq
    State('input-impacts', 'value'), # # impacts name list
    State('task-duration', 'children'), # durations   durations-task-table
    State('probabilities', 'children'),
    State('delays', 'children'),
    State('impacts-table', 'children'),
    State('loops', 'children'),
    State('bpmn-lark-store', 'data'),
    prevent_initial_call=True,
)
def create_sese_diagram(n_clicks, expression, impacts, durations = {}, probabilities = {}, delays = {}, impacts_table = {}, loops = {}, bpmn_lark:dict = {}):
    print(impacts_table)
    if not bpmn_lark:
        return [ None, None, bpmn_lark]
    # check the syntax of the input if correct print the diagram otherwise an error message
    expression = expression.replace("\n", "").replace("\t", "")
    try:
        if expression == '' and bpmn_lark[EXPRESSION] == '':
            raise Exception
        elif expression != '':
            print('task non vuota ')
            bpmn_lark[EXPRESSION] = expression
        else:
            print('task  vuota  bpmn no')
            expression = bpmn_lark[EXPRESSION]
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN tasks sequence: {e}')
        return [  # dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None, bpmn_lark
            ]
    try:
        bpmn_lark[IMPACTS] = cs.extract_impacts_dict(bpmn_lark[IMPACTS_NAMES], impacts_table)
        print(bpmn_lark[IMPACTS])
        bpmn_lark[IMPACTS] = cs.impacts_dict_to_list(bpmn_lark[IMPACTS])
        print(bpmn_lark[IMPACTS], ' AS LISTR')
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN impacts: {e}')
        return [  # dbc.Alert(f'Error while parsing the bpmn: {e}', color="danger")]
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None, bpmn_lark
            ]
    try:
        if durations:
            bpmn_lark[DURATIONS] = cs.create_duration_dict(task=expression, durations=durations)
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN durations: {e}')
        return [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None, bpmn_lark
            ]
    try:
        loops_choices = cs.extract_loops(expression)
        choices_nat = cs.extract_choises_nat(expression) + loops_choices
        bpmn_lark[PROBABILITIES] = cs.create_probabilities_dict(choices_nat, probabilities)
        bpmn_lark[PROBABILITIES], bpmn_lark[LOOP_ROUND] = cs.divide_dict(bpmn_lark[PROBABILITIES], loops_choices)
        bpmn_lark[DELAYS] = cs.create_probabilities_dict(cs.extract_choises_user(expression), delays)
        bpmn_lark[LOOP_PROB] = cs.create_probabilities_dict(loops_choices,loops)
    except Exception as e:
        print(f'Error at 1st step while parsing the BPMN choises: {e}')
        return [
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"), class_name="bg-danger"),
                        dbc.ModalBody(f'Error at 1st step while parsing the bpmn: {e}'),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None, bpmn_lark
            ]

    try:
        resp = requests.get(f'{url}create_bpmn', json={'bpmn': bpmn},  headers=headers)
        resp.raise_for_status()
        filename_svg = 'TODO'
        #display(SVG(graphviz.Source(resp.json()['bpmn_dot']).pipe(format="svg")))

        return [None, filename_svg, bpmn_lark]

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error ({resp.status_code}):", resp.json())
        return  [dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("ERROR"),  class_name="bg-danger"),
                        dbc.ModalBody(resp.json()),
                    ],
                    id="modal",
                    is_open=True,
                ),
                None, bpmn_lark
                ]


@callback(
    [Output('task-duration', 'children',allow_duplicate=True), Output('bpmn-lark-store', 'data', allow_duplicate=True)],
    Input('input-bpmn', 'value'),
    State('bpmn-lark-store', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_task_durations( tasks_,bpmn_lark): #tasks_
    """
    This function takes a list of tasks and adds a range slider for each task's duration.
    The range slider allows the user to select a duration for each task.
    The function is decorated with a callback that updates the task duration component
    whenever the 'input-bpmn' value changes.

    Parameters:
    tasks_ (list): The list of tasks.

    Returns:
    dbc table with the tables
    """
    print(f' in add_task_durations {tasks_}')
    # If no tasks are provided, return an empty list
    if not tasks_:
        return [[], {}]
    tasks_ = tasks_.replace("\n", "").replace("\t", "")
    bpmn_lark[EXPRESSION] = tasks_

    # Convert the task data list into a DataFrame and then into a Table component
    return [prepare_task_duration(tasks_), bpmn_lark]


@callback(
    Output('choose-bound-dict', 'children'),
    Input('create-diagram-button', 'n_clicks'),
    State('input-impacts', 'value'),
    allow_duplicate=True
)
def add_task(n_clicks, impacts):
    """
    This function takes the number of button clicks and a string of impacts.
    It converts the string of impacts into a dictionary and normalizes it.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'choose-bound-dict' component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    n_clicks (int): The number of button clicks.
    impacts (str): The string of impacts.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no impacts are provided, return None
    if impacts == '' or impacts == None:
        return None

    # Convert the string of impacts into a dictionary and normalize it
    impacts = impacts.split(sep=',')
    # Initialize an empty list to store the task data
    task_data = []

    # Iterate over the impacts
    for i, task in enumerate(impacts):
        # For each impact, append a dictionary to the task data list
        # The dictionary contains the impact and an input field for the impact
        task_data.append({
            'Impacts': task,
            'Set Bound': dcc.Input(
                id=f'range-slider-{i}',
                type='number',
                value=20,
                min= min_duration,
            )
        })

    # Convert the task data list into a DataFrame and then into a Table component
    # The Table component is returned and will be displayed in the 'choose-bound-dict' component
    return dbc.Table.from_dataframe(
        pd.DataFrame(task_data),
        id = 'choose-bound-dict-df',
        style = {'width': '100%', 'textalign': 'center'}
    )


@callback(
    Output('probabilities', 'children',allow_duplicate=True),
    Input('input-bpmn', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_probabilities(tasks_):
    """
    This function takes the bpmn, extract the choises and assign them with a probability.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the probailities component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    bpmn (str): The string of bpmn.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []
    tasks_ = tasks_.replace("\n", "").replace("\t", "")
    return prepare_task_probabilities(tasks_=tasks_)


@callback(
    Output('delays', 'children',allow_duplicate=True),
    Input('input-bpmn', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_delays(tasks_):
    """
    This function takes the bpmn, extract the choises and assign them with a delay.
    Then, it creates a list of unique impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'delays' component
    whenever the 'create-diagram-button' is clicked and the 'input-impacts' value changes.

    Parameters:
    bpmn (str): The string of bpmn.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []
    tasks_ = tasks_.replace("\n", "").replace("\t", "")
    return prepare_task_delays(tasks_=tasks_)


@callback(
    [Output('impacts-table', 'children',allow_duplicate=True), Output('bpmn-lark-store', 'data', allow_duplicate=True)],
    Input('input-bpmn', 'value'),
    Input('input-impacts', 'value'),
    State('bpmn-lark-store', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_impacts(tasks_, impacts, bpmn_lark):
    """
    This function takes the bpmn and a string of impacts.
    It converts the string of impacts into a list of impacts and generates a table where each row contains an impact and an input field.
    The function is decorated with a callback that updates the 'impacts-table' component
    whenever the 'input-impacts' value changes.

    Parameters:
    tasks_ (list): The list of tasks.
    impacts (str): The string of impacts.

    Returns:
    dbc.Table: A table where each row contains an impact and an input
    """
    # If no tasks are provided, return an empty list
    if not tasks_ or not impacts:
        return [[], {}]
    bpmn_lark[IMPACTS_NAMES] = impacts.replace(" ",'').split(sep=',')
    tasks_ = tasks_.replace("\n", "").replace("\t", "")
    return [prepare_task_impacts(tasks_=tasks_, impacts=impacts), bpmn_lark]


@callback(
    Output('loops', 'children',allow_duplicate=True),
    Input('input-bpmn', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_loops_number(tasks_):
    """


    Parameters:
    bpmn (str): The string of bpmn.

    Returns:
    dbc.Table: A table where each row contains an impact and an input field.
    """
    # If no tasks are provided, return an empty list
    if not tasks_:
        return []
    tasks_ = tasks_.replace("\n", "").replace("\t", "")
    return prepare_task_loops(tasks_=tasks_)


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:
        print(filename)
        if 'json' in filename:
            # Assume that the user uploaded a json file
            data = json.loads(decoded)
            bpmn_lark = data['bpmn']
            tasks = bpmn_lark[EXPRESSION]
            print(bpmn_lark)
            task_duration = prepare_task_duration(tasks_=tasks, durations=bpmn_lark[DURATIONS])
            task_impacts = prepare_task_impacts(tasks_=tasks, impacts=",".join(bpmn_lark[IMPACTS_NAMES]), impacts_dict=bpmn_lark[IMPACTS])
            print(task_impacts)
            task_probabilities = prepare_task_probabilities(tasks_=tasks, prob=bpmn_lark[PROBABILITIES])
            task_delays = prepare_task_delays(tasks_=tasks, delays=bpmn_lark[DELAYS])
            task_loops = prepare_task_loops(tasks_=tasks, loops=bpmn_lark[LOOP_ROUND])
            tasks = html.P(f"""Here is provided the bpmn schema from the file: 
                           {tasks} 
                           If you want to modify it, just copy and paste in the textarea below. 
                           Note that this will reset all the other values to the default one.""")
            return tasks, task_duration, task_impacts, task_probabilities, task_delays, task_loops, bpmn_lark, ", ".join(bpmn_lark[IMPACTS_NAMES])
    except Exception as e:
        print(e)
        return None, None, None, None, None, None, {}, None


@callback([
        Output('loaded-bpmn-file', 'children'),
        Output('task-duration', 'children',allow_duplicate=True),
        Output('impacts-table', 'children',allow_duplicate=True),
        Output('probabilities', 'children',allow_duplicate=True),
        Output('delays', 'children',allow_duplicate=True),
        Output('loops', 'children',allow_duplicate=True),
        Output('bpmn-lark-store', 'data',allow_duplicate=True),
        Output('input-impacts', 'value', allow_duplicate=True),
    ],
    [Input('upload-data', 'contents')],
    [State('upload-data', 'filename')],
    allow_duplicate=True,
    prevent_initial_call=True
    )
def update_output(list_of_contents, list_of_names):
    if list_of_contents is not None and len(list_of_contents) == 1:
        # children = [parse_contents(c, n) for c, n in zip(list_of_contents, list_of_names) ]
        return parse_contents(list_of_contents[0], list_of_names[0])
    return None, None, None, None, None, None, {}, None
