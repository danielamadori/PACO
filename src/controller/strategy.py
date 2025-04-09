import requests
from dash import Input, Output, State, callback, html
from env import URL_SERVER, HEADERS, EXPRESSION
from model.bpmn import SESE_PARSER, extract_nodes, filter_bpmn

def register_strategy_callbacks(strategy_callback):

	@strategy_callback(
		Output('execution-tree-svg', 'children'),
		Input('find-strategy-button', 'n_clicks'),
		State('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def compute_execution_tree(n_clicks, data):
		tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
		bpmn = filter_bpmn(data, tasks, choices, natures, loops)
		try:

			resp = requests.get(URL_SERVER + "create_execution_tree", json={"bpmn": bpmn}, headers=HEADERS)
			# resp = requests.get(f'{url}create_strategy', json={"bpmn": bpmn, "bound": bound, "parse_tree": parse_tree.to_dict(), "execution_tree": execution_tree.to_dict()}, headers=headers)
			resp.raise_for_status()

			response = resp.json()

			return html.P(f"Execution Tree ok")
		except requests.exceptions.HTTPError as e:
			return html.Div(f"HTTP Error ({resp.status_code}): {resp.text}", style={"color": "red"})
