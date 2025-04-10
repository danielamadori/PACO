import ast

import requests
from dash import Input, Output, State, html
from controller.db import load_parse_and_execution_tree
from env import URL_SERVER, HEADERS, EXPRESSION, IMPACTS_NAMES, BOUND
from model.bpmn import SESE_PARSER, extract_nodes, filter_bpmn


def strategy_results(response:dict):
	elements = [
		html.P(response["result"]),
		html.Br()
	]

	if 'expected_impacts' in response:
		elements.append(html.H5(f"Expected Impacts: {response['expected_impacts']}"))
	else:
		elements.append(html.H5("Guaranteed Bounds"))

		guaranteed_bounds = [
			[float(x) for x in s.strip('[]').split()]
			for s in ast.literal_eval(response['guaranteed_bounds'])
		]
		for bound in guaranteed_bounds:
			elements.append(html.P(f"Bound: {bound}"))


		elements.append(html.H5("Possible Min Solution"))
		possible_min_solution = [
			[float(x) for x in s.strip('[]').split()]
			for s in ast.literal_eval(response['possible_min_solution'])
		]
		for bound in possible_min_solution:
			elements.append(html.P(f"Bound: {bound}"))

	#strategy_tree = response["strategy_tree"]
	#bdds = response["bdds"]
	#save_strategy_results(bpmn, json.dumps(strategy_tree), json.dumps(bdds))

	#'possible_min_solution',  'frontier_solution', 'strategy_expected_impacts', 'strategy_expected_time'
	return html.Div(elements)




def register_strategy_callbacks(strategy_callback):
	@strategy_callback(
		Output("find_strategy_message", "children", allow_duplicate=True),
		Input("find-strategy-button", "n_clicks"),
		State("bpmn-store", "data"),
		State("bound-store", "data"),
		prevent_initial_call=True
	)
	def find_strategy(n_clicks, bpmn_store, bound_store):
		tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
		bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)
		bound = [bound_store[BOUND][impact_name] for impact_name in bpmn[IMPACTS_NAMES]]

		try:
			parse_tree, execution_tree = load_parse_and_execution_tree(bpmn)

			resp = requests.get(URL_SERVER + "create_strategy",
								json={"bpmn": bpmn, "bound": bound,
									  "parse_tree": parse_tree, "execution_tree": execution_tree},
								headers=HEADERS)
			resp.raise_for_status()

			response = resp.json()
			return strategy_results(response)

		except requests.exceptions.HTTPError as e:
			return html.Div(f"HTTP Error ({resp.status_code}): {resp.text}", style={"color": "red"})
