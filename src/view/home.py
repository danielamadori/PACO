import dash
from dash import html, callback, Output, Input
import dash_bootstrap_components as dbc
from dash import dcc

from controller.bound_table import register_bound_callbacks
from src.env import DELAYS, DURATIONS, H, IMPACTS, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, LOOP_PROBABILITY
from src.controller.expression import register_expression_callbacks
from src.controller.gateways_table import register_gateway_callbacks
from src.controller.tasks_table import register_task_callbacks
from src.controller.strategy import register_strategy_callbacks
from src.view.components.tabs import getTabs


def layout():
    return html.Div([
        dcc.Store(id='bpmn-store', data={
            EXPRESSION: 'Task',
            H: 0,
            IMPACTS: {},
            DURATIONS: {},
            IMPACTS_NAMES : ['impact'],
            DELAYS: {},
            PROBABILITIES: {},
            LOOP_PROBABILITY: {},
            LOOP_ROUND: {},
            "svg": ""
        }, storage_type='session'),


        dbc.Row([
            dbc.Col([
                getTabs()
            ], width='auto', style={"borderRight": "1px solid #ccc", "padding": "1rem", "maxWidth": "500px"}),

            dbc.Col([
                dbc.Spinner(
                    html.Div(id="svg-container"),
                    color="primary",
                    type="grow",
                    fullscreen=False,  # oppure True se vuoi che copra tutto lo schermo
                    spinner_style={"width": "4rem", "height": "4rem"}
                )
            ], width=True, style={"padding": "2rem"})
        ])
    ])


register_task_callbacks(dash.callback)
register_gateway_callbacks(dash.callback)
register_expression_callbacks(dash.callback)
register_bound_callbacks(dash.callback)
register_strategy_callbacks(dash.callback)

@callback(
    Output("svg-container", "children"),
    Input("bpmn-store", "data")
)
def update_svg(data):
    if not data or not data.get("svg"):
        return ""

    return html.Iframe(src=data["svg"], style={"width": "100%", "height": "600px", "border": "none"})
