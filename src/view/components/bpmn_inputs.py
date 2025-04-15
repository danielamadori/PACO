import dash_bootstrap_components as dbc
from dash import html, dcc


def get_bpmn_view():
	return html.Div([
		dcc.Input(type="text", debounce=True, id='input-bpmn', style={'width': '90%'}, value=''),
		html.Div([
			dbc.Input(
				id='new-impact-name',
				placeholder='New impact',
				debounce=True,
				style={'flexGrow': 1, 'marginRight': '4px'}
			),
			dbc.Button(
				"+",
				id='add-impact-button',
				n_clicks=0,
				color="success",
				size="sm",
				style={"padding": "0.25rem 0.4rem", "lineHeight": "1"}
			),
		], style={'width': '180px', 'display': 'flex', 'alignItems': 'center'}),
		html.Div(id='task-duration'),
		html.Div(id='choice-table'),
		html.Div(id='nature-table'),
		html.Div(id='loop-table'),
	], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})
