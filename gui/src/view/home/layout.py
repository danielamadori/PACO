import dash
from dash import dcc, html
from dash_split_pane import DashSplitPane
from controller.home.sidebar.bpmn_tab.download import register_download_callbacks
from controller.home.sidebar.bpmn_tab.table.tasks_impacts_names import register_task_impacts_names_callbacks
from controller.home.sidebar.bpmn_tab.upload import register_upload_callbacks
from controller.home.sidebar.llm_tab.chat import register_llm_callbacks
from controller.home.sidebar.sidebar import register_sidebar_callbacks
from controller.home.sidebar.simulator_tab.random_decision import register_pending_decision_random_callbacks
from controller.home.sidebar.strategy_tab.table.bound_table import register_bound_callbacks
from env import DELAYS, DURATIONS, H, IMPACTS, EXPRESSION, IMPACTS_NAMES, PROBABILITIES, LOOP_ROUND, \
    LOOP_PROBABILITY, BOUND
from controller.home.sidebar.bpmn_tab.expression import register_expression_callbacks
from controller.home.sidebar.bpmn_tab.table.gateways_table import register_gateway_callbacks
from controller.home.sidebar.bpmn_tab.table.tasks_impacts_table import register_task_impacts_callbacks
from controller.home.sidebar.strategy_tab.strategy import register_strategy_callbacks
from view.home.sidebar.sidebar import get_sidebar
from view.visualizer.RenderSVG import RenderSvg


def layout():
    sidebar_min_width = 450

    bpmn_visualizer = RenderSvg(type="bpmn-svg", index="main", zoom_min=0.1, zoom_max=5.5)

    return html.Div([
        dcc.Store(id='bpmn-store', data={
            EXPRESSION: '',
            H: 0,
            IMPACTS: {},
            DURATIONS: {},
            IMPACTS_NAMES: [],
            DELAYS: {},
            PROBABILITIES: {},
            LOOP_PROBABILITY: {},
            LOOP_ROUND: {},
        }, storage_type='session'),
        dcc.Store(id={"type": "bpmn-svg-store", "index": "main"}, data="", storage_type='session'),
        dcc.Store(id='bound-store', data={BOUND: {}}, storage_type='session'),

        dcc.Store(id='chat-history', data=[], storage_type='session'),
        dcc.Store(id='pending-message', data=None, storage_type='session'),
        dcc.Store(id='reset-trigger', data=False, storage_type='session'),

        dcc.Store(id="sidebar-visible", data=True, storage_type='session'),
        dcc.Store(id="sidebar-width", data=sidebar_min_width, storage_type='session'),

        DashSplitPane(
            id="split-pane",
            split="vertical",
            resizerStyle={"width": "20px"},
            minSize=sidebar_min_width,
            size=sidebar_min_width,
            children=[
                get_sidebar(),
                bpmn_visualizer.get_visualizer()
            ],
            style={"height": "calc(100vh - 60px)", "display": "flex", "flexDirection": "row"}

    )
    ])


RenderSvg.register_callbacks(dash.callback, "bpmn-svg")
RenderSvg.register_callbacks(dash.callback, "bdd")
register_task_impacts_callbacks(dash.callback)
register_task_impacts_names_callbacks(dash.callback)
register_gateway_callbacks(dash.callback)
register_expression_callbacks(dash.callback)
register_bound_callbacks(dash.callback)
register_strategy_callbacks(dash.callback)
register_sidebar_callbacks(dash.callback)
register_llm_callbacks(dash.callback, dash.clientside_callback)
register_upload_callbacks(dash.callback)
register_download_callbacks(dash.callback)
register_pending_decision_random_callbacks(dash.callback)