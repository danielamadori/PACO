from dash import html, dcc
import dash_bootstrap_components as dbc

def get_bpmn_view():
	return html.Div([
		dbc.Card(
			[
				dbc.CardHeader(
					html.Div([
						html.H5("Expression", className="mb-0"),
					], style={"textAlign": "left"})
				),
				dbc.CardBody(
					dcc.Input(type="text", debounce=True, id='expression-bpmn', style={'width': '100%', 'height': '48px'}, value='')
				)
			],
			style={"width": "100%", "marginBottom": "1rem"}
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

