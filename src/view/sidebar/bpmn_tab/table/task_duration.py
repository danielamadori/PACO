from dash import html, dcc

from env import DURATIONS


def get_duration_table_header():
	return [
		html.Th("Min", style={'width': '80px', 'vertical-align': 'middle'}),
		html.Th("Max", style={'width': '80px', 'vertical-align': 'middle'}),
	]


def get_duration_table_row(task, bpmn_store):
	if task not in bpmn_store[DURATIONS]:
		bpmn_store[DURATIONS][task] = (0, 1)

	(min_d, max_d) = bpmn_store[DURATIONS][task]

	return [
		html.Td(html.Span(task, style={"whiteSpace": "nowrap", "overflow": "hidden", "textOverflow": "ellipsis", "minWidth": "100px", "display": "inline-block"})),
		html.Td(dcc.Input(value=min_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'min-duration', 'index': task})),
		html.Td(dcc.Input(value=max_d, type='number', min=0, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"}, id={'type': 'max-duration', 'index': task})),
	]
