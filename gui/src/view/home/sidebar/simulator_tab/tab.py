from dash import dcc, html
import dash_bootstrap_components as dbc
from view.home.sidebar.simulator_tab.simulate_control import get_control
from view.home.sidebar.simulator_tab.pending_decisions import get_pending_decisions
from view.home.sidebar.simulator_tab.status_info import status_info


def get_simulator_tab():
	return dcc.Tab(
		label='Simulator',
		value='tab-simulator',
		style={'flex': 1, 'textAlign': 'center'},
		children=[
			dcc.Store(id="simulation-store", data={
				"gateway_decisions": {},
				"impacts": {},
				"expected_impacts": {},
				"execution_time": 0,
				"probability": 1.0
			}),
			html.Div(
				dbc.Container(
					dbc.Row([
						dbc.Col(get_control()),
						dbc.Col(status_info()),
						dbc.Col(get_pending_decisions())
					], className="g-3"),
					fluid=True,
					className="p-3"
				),
				className="sidebar-box"
			)
		]
	)
