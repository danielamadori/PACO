from dash import html, dcc

from view.sidebar.bpmn_tab.table.new_impact_button import get_new_impact_button


def get_bpmn_view():
	return html.Div([
		dcc.Input(type="text", debounce=True, id='expression-bpmn', style={'width': '90%'}, value=''),
		html.Div(id='task-table'),
		get_new_impact_button(),
		html.Div(id='choice-table'),
		html.Div(id='nature-table'),
		html.Div(id='loop-table'),
	], style={
		"display": "flex",
		"gap": "20px",
		"flexWrap": "wrap",
		"justifyContent": "center"
	})
