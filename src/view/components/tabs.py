from dash import dcc
from view.components.bpmn_tab import get_BPMN_CPI_tab
from view.components.strategy_tab import get_Strategy_tab


def getTabs():
    return dcc.Tabs(id='bpmn-tabs', value='tab-bpmn', style={'display': 'flex'}, children=[
		get_BPMN_CPI_tab(),
		get_Strategy_tab(),
    ])