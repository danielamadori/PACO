import dash
from dash import Input, Output, State, ALL
from src.env import EXPRESSION, SESE_PARSER
from src.model.bpmn import extract_nodes, update_bpmn_data
from utils.env import PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND, DELAYS
from src.view.components.gateways_table import choices_table, natures_table, loops_table


def register_gateway_callbacks(gateway_callbacks):
	@gateway_callbacks(
		Output('choice-table', 'children'),
		Input('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def generate_choice_table(data):
		_, choices, _, _ = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
		if len(choices) == 0:
			return dash.no_update

		return choices_table(data, choices)

	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'choice-delay', 'index': ALL}, 'value'),
		State({'type': 'choice-delay', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_choices(values, ids, data):
		for value, id_obj in zip(values, ids):
			data[DELAYS][id_obj['index']] = value
		return update_bpmn_data(data)

	@gateway_callbacks(
		Output('nature-table', 'children'),
		Input('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def generate_nature_table(data):
		_, _, natures, _ = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
		if len(natures) == 0:
			return dash.no_update

		return natures_table(data, natures)

	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'nature-prob', 'index': ALL}, 'value'),
		State({'type': 'nature-prob', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_natures(values, ids, data):
		for value, id_obj in zip(values, ids):
			data[PROBABILITIES][id_obj['index']] = value
		return update_bpmn_data(data)

	@gateway_callbacks(
		Output('loop-table', 'children'),
		Input('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def generate_loop_table(data):
		_, _, _, loops = extract_nodes(SESE_PARSER.parse(data[EXPRESSION]))
		if len(loops) == 0:
			return dash.no_update

		return loops_table(data, loops)

	@gateway_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'loop-prob', 'index': ALL}, 'value'),
		Input({'type': 'loop-round', 'index': ALL}, 'value'),
		State({'type': 'loop-prob', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_loops(probs, rounds, ids, data):
		for p, r, id_obj in zip(probs, rounds, ids):
			loop = id_obj['index']
			data[LOOP_PROBABILITY][loop] = p
			data[LOOP_ROUND][loop] = r
		return update_bpmn_data(data)
