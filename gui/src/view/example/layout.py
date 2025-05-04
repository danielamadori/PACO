import json
import dash
import dash_bootstrap_components as dbc
from view.example.first_example.layout import get_first_example
from controller.example.render import register_example_callbacks, render_example
from view.example.second_example import get_second_example
from view.example.third_example import get_third_example

FIRST_EXAMPLE_PATH = "gui/src/assets/bpmn_fig8_bound_135_15.json"
SECOND_EXAMPLE_PATH = "gui/src/assets/bpmn_unavoidable_impacts_bound_5_6.json"
THIRD_EXAMPLE_PATH = "gui/src/assets/bpmn_random_bound_300_272.json"

def layout():
    with open(FIRST_EXAMPLE_PATH, "r") as file:
        data = json.load(file)
    bpmn, bpmn_dot = render_example(data)

    with open(SECOND_EXAMPLE_PATH, "r") as file:
        data = json.load(file)
    bpmn2, bpmn_dot2 = render_example(data)

    with open(THIRD_EXAMPLE_PATH, "r") as file:
        data = json.load(file)
    bpmn3, bpmn_dot3 = render_example(data)

    return dbc.Container([
        dbc.Row([
            dbc.Col([
                get_first_example("bpmn-example", bpmn, bpmn_dot)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                get_second_example("bpmn-example2", bpmn2, bpmn_dot2)
            ], width=12)
        ]),
        dbc.Row([
            dbc.Col([
                get_third_example("bpmn-example3", bpmn3, bpmn_dot3)
            ], width=12)
        ])
    ], fluid=True)


register_example_callbacks(dash.callback, id = "bpmn-example", example_path = FIRST_EXAMPLE_PATH)
register_example_callbacks(dash.callback, id = "bpmn-example2", example_path = SECOND_EXAMPLE_PATH)
register_example_callbacks(dash.callback, id = "bpmn-example3", example_path = THIRD_EXAMPLE_PATH)
