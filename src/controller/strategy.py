import requests
from dash import Input, Output, State, callback, html

from controller.db import get_execution_and_parse_tree
from env import URL_SERVER, HEADERS, EXPRESSION, IMPACTS_NAMES
from model.bpmn import SESE_PARSER, extract_nodes, filter_bpmn



def create_execution_tree(bpmn):
	resp = requests.get(URL_SERVER + "create_execution_tree", json={"bpmn": bpmn}, headers=HEADERS)
	resp.raise_for_status()

	r = resp.json()

	return r["parse_tree"], r["execution_tree"]



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

		execution_tree, parse_tree = get_execution_and_parse_tree(bpmn)
		try:
			if execution_tree is None or parse_tree is None:
				parse_tree, execution_tree = create_execution_tree(bpmn)


			bound = [data["bound"][impact_name] for impact_name in bpmn[IMPACTS_NAMES]]

			resp = requests.get(URL_SERVER + "create_strategy", json={"bpmn": bpmn, "bound": bound, "parse_tree": parse_tree, "execution_tree": execution_tree}, headers=HEADERS)
			resp.raise_for_status()

			response = resp.json()

			print(response.keys())

			return html.P(response["result"])
		except requests.exceptions.HTTPError as e:
			return html.Div(f"HTTP Error ({resp.status_code}): {resp.text}", style={"color": "red"})
