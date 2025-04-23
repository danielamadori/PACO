from dash import html, dcc

def get_bpmn_view():
	return html.Div([
		html.Div([
			html.H5("Expression"),
			dcc.Input(type="text", debounce=True, id='expression-bpmn', style={'width': '90%', 'height': '48px'}, value=''),
			],
			style={"width": "100%", "textAlign": "left"}
		),
		html.Div(id='task-impacts-table'),
		html.Div(id='task-durations-table'),
		html.Div(id='choice-table'),
		html.Div(id='nature-table'),
		html.Div(id='loop-table'),
	], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})
