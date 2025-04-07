import base64
import json

import dash_bootstrap_components as dbc
import pandas as pd
from dash import callback, Output, Input, State, dcc, html
from fastapi import requests

from core.api.remote_api import headers
from core.config import EXPRESSION, URL_SERVER


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
        print("TODO")
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
        print("TODO")
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
        print("TODO")
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
        print("TODO")
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
        bpmn = {}
        resp = requests.get(f'{URL_SERVER}create_bpmn', json={'bpmn': bpmn},  headers=headers)
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
    return []


@callback(
    Output('choose-bound-dict', 'children'),
    Input('create-diagram-button', 'n_clicks'),
    State('input-impacts', 'value'),
    allow_duplicate=True
)
def add_task(n_clicks, impacts):
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
                min= 0,
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
    return []


@callback(
    Output('delays', 'children',allow_duplicate=True),
    Input('input-bpmn', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_delays(tasks_):
    return []



@callback(
    [Output('impacts-table', 'children',allow_duplicate=True), Output('bpmn-lark-store', 'data', allow_duplicate=True)],
    Input('input-bpmn', 'value'),
    Input('input-impacts', 'value'),
    State('bpmn-lark-store', 'data'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_impacts(tasks_, impacts, bpmn_lark):
    return [[], {}]


@callback(
    Output('loops', 'children',allow_duplicate=True),
    Input('input-bpmn', 'value'),
    allow_duplicate=True,
    prevent_initial_call=True
)
def add_loops_number(tasks_):
    return []



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
            '''
            task_duration = prepare_task_duration(tasks_=tasks, durations=bpmn_lark[DURATIONS])
            task_impacts = prepare_task_impacts(tasks_=tasks, impacts=",".join(bpmn_lark[IMPACTS_NAMES]), impacts_dict=bpmn_lark[IMPACTS])
            print(task_impacts)
            task_probabilities = prepare_task_probabilities(tasks_=tasks, prob=bpmn_lark[PROBABILITIES])
            task_delays = prepare_task_delays(tasks_=tasks, delays=bpmn_lark[DELAYS])
            task_loops = prepare_task_loops(tasks_=tasks, loops=bpmn_lark[LOOP_ROUND])
            '''
            tasks = html.P(f"""Here is provided the bpmn schema from the file: 
						   {tasks} 
						   If you want to modify it, just copy and paste in the textarea below. 
						   Note that this will reset all the other values to the default one.""")
            return tasks#, task_duration, task_impacts, task_probabilities, task_delays, task_loops, bpmn_lark, ", ".join(bpmn_lark[IMPACTS_NAMES])
    except Exception as e:
        print(e)
        return None#, None, None, None, None, None, {}, None


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
