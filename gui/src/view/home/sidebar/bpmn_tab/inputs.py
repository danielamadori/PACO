from dash import html, dcc
import dash_bootstrap_components as dbc

def get_bpmn_view():
	return html.Div([
		dbc.Card([
				dbc.CardHeader(
					html.Div([
						html.H5("Expression", className="mb-0"),
					], style={"textAlign": "left"})
				),
				dbc.CardBody(
					html.Div([
						dcc.Input(
							type="text", 
							debounce=True, 
							id='expression-bpmn', 
							style={'flex': '1', 'height': '38px', 'marginRight': '10px'}, 
							value='',
							placeholder="Enter BPMN expression..."
						),
						dbc.Button(
							"Generate", 
							id='generate-bpmn-btn', 
							color="primary", 
							className="me-1",
							style={'height': '38px'}
						)
					], style={'display': 'flex', 'alignItems': 'center'})
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

