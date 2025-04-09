import dash
from dash import Input, Output, State, ALL
from utils.env import IMPACTS_NAMES
from view.components.bound_table import bound_table


def register_bound_callbacks(bound_callbacks):
	@bound_callbacks(
		Output('bound-table', 'children'),
		Input('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def generate_bound_table(data):
		if len(data[IMPACTS_NAMES]) == 0:
			return dash.no_update

		return bound_table(data, data[IMPACTS_NAMES])

	@bound_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Input({'type': 'bound-input', 'index': ALL}, 'value'),
		State({'type': 'bound-input', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_bounds(values, ids, data):
		for value, id_obj in zip(values, ids):
			data.setdefault("bound", {})[id_obj["index"]] = value
		return data
