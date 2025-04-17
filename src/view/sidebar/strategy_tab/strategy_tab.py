import dash_bootstrap_components as dbc
from dash import dcc, html

from env import ALGORITHMS


def get_Strategy_tab():
	return dcc.Tab(label='Define Strategy', value='tab-strategy', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			html.Div(id="strategy", children=[
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
					html.H5('Insert the bound'),
					dbc.Button('Find strategy', id='find-strategy-button')],
					style={
						"display": "flex",
						"gap": "20px",
						"justifyContent": "center"
					}
				),
				html.Div(id='bound-table'),
				html.Br(),
				html.Div(id='find_strategy_message')
			]),
		], style={
			"display": "flex",
			"gap": "20px",
			"flexWrap": "wrap",
			"justifyContent": "center"
		})
	])
