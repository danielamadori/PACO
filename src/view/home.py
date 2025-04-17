import dash
from dash import dcc, html
from dash_split_pane import DashSplitPane

from controller.sidebar.sidebar import register_sidebar_callbacks
from controller.sidebar.strategy_tab.bound_table import register_bound_callbacks
from controller.main_content.render_svg import register_render_svg
from src.env import DELAYS, DURATIONS, H, IMPACTS, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, \
    LOOP_PROBABILITY, BOUND
from controller.sidebar.bpmn_tab.expression import register_expression_callbacks
from controller.sidebar.bpmn_tab.table.gateways_table import register_gateway_callbacks
from controller.sidebar.bpmn_tab.table.tasks_table import register_task_callbacks
from controller.sidebar.strategy_tab.strategy import register_strategy_callbacks
from view.main_content.render_svg import get_main_content
from view.sidebar.sidebar import get_sidebar


def layout():
    sidebar_min_width = 450

    return html.Div([
        dcc.Store(id='bpmn-store', data={
            EXPRESSION: 'Task',
            H: 0,
            IMPACTS: {},
            DURATIONS: {},
            IMPACTS_NAMES: ['impact'],
            DELAYS: {},
            PROBABILITIES: {},
            LOOP_PROBABILITY: {},
            LOOP_ROUND: {},
        }, storage_type='session'),
        dcc.Store(id='dot-store', data={"bpmn": "", "bdds": ""}, storage_type='session'),
        dcc.Store(id='bound-store', data={BOUND: {}}, storage_type='session'),
        dcc.Store(id="sidebar-visible", data=True),
        dcc.Store(id="sidebar-width", data=sidebar_min_width),
        dcc.Store(id="svg-zoom", data=1.0),
        dcc.Interval(id="interval", interval=1000, n_intervals=0),

        DashSplitPane(
            id="split-pane",
            split="vertical",
            minSize=sidebar_min_width,
            size=sidebar_min_width,
            children=[
                get_sidebar(),
                get_main_content()
            ],
            style={"height": "calc(100vh - 60px)", "display": "flex", "flexDirection": "row"}

    )
    ])


register_task_callbacks(dash.callback)
register_gateway_callbacks(dash.callback)
register_expression_callbacks(dash.callback)
register_bound_callbacks(dash.callback)
register_strategy_callbacks(dash.callback)
register_render_svg(dash.callback)
register_sidebar_callbacks(dash.callback)
