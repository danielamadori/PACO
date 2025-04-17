import dash_bootstrap_components as dbc
from dash import html, dcc

from env import IMPACTS_NAMES, IMPACTS


def get_impacts_table_header(bpmn_store):
	no_delete_button = len(bpmn_store[IMPACTS_NAMES]) < 2

	return [
		html.Th(html.Div([
			html.Span(
				name,
				style={
					"whiteSpace": "nowrap",
					"overflow": "hidden",
					"textOverflow": "ellipsis",
					"maxWidth": "80px",
					"display": "inline-block"
				}
			),
			# Mostra il bottone solo se non è disabilitato
			dbc.Button(
				"×",
				id={'type': 'remove-impact', 'index': name},
				n_clicks=0,
				color="danger",
				size="sm",
				className="ms-1",
				style={"padding": "2px 6px"}
			) if not no_delete_button else None
		], style={
			'display': 'flex',
			'alignItems': 'center',
			'justifyContent': 'space-between'
		}))
		for name in sorted(bpmn_store[IMPACTS_NAMES])
	]


def get_impacts_table_row(task, bpmn_store):
	sorted_impacts_names = sorted(bpmn_store[IMPACTS_NAMES])

	if task not in bpmn_store[IMPACTS]:
		bpmn_store[IMPACTS][task] = {impact_name : 0.0 for impact_name in sorted_impacts_names}

	return [
		html.Td(dcc.Input(
			value=bpmn_store[IMPACTS][task][impact_name],
			type='number', min=0.0, step=0.001, debounce=True, style={'width': '80px', "border": "none", "padding": "0.4rem"},
			id={'type': f'impact-{impact_name}', 'index': task}
		)) for impact_name in sorted_impacts_names
	]
