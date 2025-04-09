import dash_bootstrap_components as dbc
from dash import dcc, html
from src.env import ALGORITHMS
from src.view.components.bpmn import get_bpmn_view

def getTabs():
    return dcc.Tabs(id='bpmn-tabs', value='tab-bpmn', style={'display': 'flex'}, children=[
		get_BPMN_CPI_tab(),
		get_Strategy_tab(),
    ])


def get_BPMN_CPI_tab():
	return dcc.Tab(label='BPMN + CPI', value='tab-bpmn', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			html.Div(id='bpmn-alert'),
			dcc.Upload(
				id='upload-data',
				children=html.Div([
					'Drag and Drop or ',
					html.A('Select a JSON File')
				]),
				style={
					'width': '100%',
					'height': '60px',
					'lineHeight': '60px',
					'borderWidth': '1px',
					'borderStyle': 'dashed',
					'borderRadius': '5px',
					'textAlign': 'center',
					'margin': '10px'
				},
				multiple=True
			),
			html.Div(id='output-data-upload'),
			html.Br(),
			html.P("""Here is an example of a BPMN complete diagram:\n Task0, (Task1 || Task4), (Task3 ^[N1] Task9, Task8 /[C1] Task2)"""),
			html.Br(),
			get_bpmn_view()
		])
	])


def get_Strategy_tab():
	return dcc.Tab(label='Define Strategy', value='tab-strategy', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			html.Div(id="strategy", children=[
				html.H4("Choose the algorithm to use:"),
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
				html.H5('Insert the bound'),
				html.Div(id='bound-table'),
				html.Br(),
				dbc.Button('Find strategy', id='find-strategy-button'),
				html.Div(id='execution-tree-svg')
			]),
		])
	])