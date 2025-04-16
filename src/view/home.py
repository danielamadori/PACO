import dash
import dash_bootstrap_components as dbc
from dash import dcc, html

from controller.sidebar.strategy_tab.bound_table import register_bound_callbacks
from controller.render_svg import register_render_svg
from src.env import DELAYS, DURATIONS, H, IMPACTS, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, \
    LOOP_PROBABILITY, BOUND
from controller.sidebar.bpmn_tab.expression import register_expression_callbacks
from controller.sidebar.bpmn_tab.table.gateways_table import register_gateway_callbacks
from controller.sidebar.bpmn_tab.table.tasks_table import register_task_callbacks
from controller.sidebar.strategy_tab.strategy import register_strategy_callbacks
from view.sidebar.tabs import getTabs


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
        }, storage_type='session'),
        dcc.Store(id='dot-store', data={"bpmn": "", "execution_tree": "", "strategy": "", "bdds": ""}, storage_type='session'),
        dcc.Store(id='bound-store', data={BOUND: {}}, storage_type='session'),

        dbc.Row([
            dbc.Col([
                getTabs()
            ], width='auto', style={"borderRight": "1px solid #ccc", "padding": "1rem", "maxWidth": "500px"}),

            dbc.Col([
                dbc.Spinner(
                html.Div(id="svg-bpmn"),
                    color="primary",
                    type="grow",
                    fullscreen=False,
                    spinner_style={"width": "4rem", "height": "4rem"}
                ),
                html.Div(id="svg-execution-tree"),
                html.Div(id="svg-strategy"),
                html.Div(id="svg-bdds"),
            ], width=True, style={"padding": "2rem"})
        ])
    ])


register_task_callbacks(dash.callback)
register_gateway_callbacks(dash.callback)
register_expression_callbacks(dash.callback)
register_bound_callbacks(dash.callback)
register_strategy_callbacks(dash.callback)
register_render_svg(dash.callback)



