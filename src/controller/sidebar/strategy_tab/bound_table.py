import dash
from dash import Input, Output, State, ALL
from env import IMPACTS_NAMES
from view.sidebar.strategy_tab.bound_table import bound_table


def register_bound_callbacks(bound_callbacks):
	@bound_callbacks(
		Output('bound-table', 'children'),
		Input('bound-store', 'data'),
		Input('bpmn-store', 'data'),

		prevent_initial_call=True
	)
	def generate_bound_table(bound_store, bpmn_store):
		if len(bpmn_store[IMPACTS_NAMES]) == 0:
			return dash.no_update

		return bound_table(bound_store, bpmn_store[IMPACTS_NAMES])

	@bound_callbacks(
		Output('bound-store', 'data', allow_duplicate=True),
		Input({'type': 'bound-input', 'index': ALL}, 'value'),
		State({'type': 'bound-input', 'index': ALL}, 'id'),
		State('bound-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_bounds(values, ids, bound_store):
		for value, id_obj in zip(values, ids):
			bound_store.setdefault("bound", {})[id_obj["index"]] = value
		return bound_store
