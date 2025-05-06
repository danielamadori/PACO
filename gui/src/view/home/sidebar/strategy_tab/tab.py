import dash_bootstrap_components as dbc
from dash import dcc, html
from env import ALGORITHMS

def get_strategy_tab():
	return dcc.Tab(label='Strategy', value='tab-strategy', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			dcc.Store(id="sort_store_guaranteed", data={"sort_by": None, "sort_order": "asc"}),
			dcc.Store(id="sort_store_possible_min", data={"sort_by": None, "sort_order": "asc"}),
			html.Div(id='strategy-alert'),
			get_strategy_input(),
			html.Div(id='strategy_output')
		])
	])

def get_strategy_input():
	return html.Div([
		html.Div(children=[
				html.Br(),
				html.H5("Choose the algorithm to use:"),
				html.Br(),
				dcc.Dropdown(
					id='choose-strategy',
					options=[
						{'label': value, 'value': key}
						for key, value in ALGORITHMS.items()
					],
					value=list(ALGORITHMS.keys())[0]
				),
				html.Br(),
				html.Div([
					html.H5('Insert bound'),
					dbc.Button('Find strategy', id='find-strategy-button')],
					style={
						"display": "flex",
						"gap": "20px",
						"justifyContent": "center"
					}
				),
				html.Div(id='bound-table'),
				html.Br(),
			])
		], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})
