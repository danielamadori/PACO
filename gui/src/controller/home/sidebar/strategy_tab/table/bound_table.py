import dash
from dash import Input, Output, State, ALL, ctx
from env import IMPACTS_NAMES, BOUND, EXPRESSION
from view.home.sidebar.strategy_tab.table.bound_table import get_bound_table
from dash import html

def sync_bound_store_from_bpmn(bpmn_store, bound_store):
	for name in sorted(bpmn_store[IMPACTS_NAMES]):
		if name not in bound_store[BOUND]:
			bound_store[BOUND][name] = 1.0

	return bound_store

def register_bound_callbacks(bound_callbacks):
	@bound_callbacks(
		Output("bound-table", "children"),
		Input("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def regenerate_bound_table(bound_store, bpmn_store):
		if not bpmn_store or bpmn_store[EXPRESSION] == '' or not bound_store or BOUND not in bound_store:
			return html.Div()

		return get_bound_table(bound_store, sorted(bpmn_store[IMPACTS_NAMES]))

	@bound_callbacks(
		Output('bound-store', 'data', allow_duplicate=True),
		Input({'type': 'bound-input', 'index': ALL}, 'value'),
		State({'type': 'bound-input', 'index': ALL}, 'id'),
		State('bound-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_bounds(values, ids, bound_store):
		for value, id_obj in zip(values, ids):
			bound_store[BOUND][id_obj["index"]] = float(value)
		return bound_store

	@bound_callbacks(
		Output("bound-store", "data", allow_duplicate=True),
		Input({"type": "selected_bound", "index": ALL, "table": "guaranteed"}, "n_clicks"),
		State({"type": "selected_bound", "index": ALL, "table": "guaranteed"}, "value"),
		State("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_bound_from_guaranteed(n_clicks_list, values, bound_store, bpmn_store):
		trigger = ctx.triggered_id
		if not trigger:
			raise dash.exceptions.PreventUpdate

		idx = trigger["index"]
		if idx >= len(n_clicks_list) or not n_clicks_list[idx]:
			raise dash.exceptions.PreventUpdate

		selected_bound = values[idx]

		for name, value in zip(sorted(bpmn_store[IMPACTS_NAMES]), selected_bound):
			bound_store[BOUND][name] = float(value)

		return bound_store


	@bound_callbacks(
		Output("bound-store", "data", allow_duplicate=True),
		Input({"type": "selected_bound", "index": ALL, "table": "possible_min"}, "n_clicks"),
		State({"type": "selected_bound", "index": ALL, "table": "possible_min"}, "value"),
		State("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_bound_from_possible_min(n_clicks_list, values, bound_store, bpmn_store):
		trigger = ctx.triggered_id
		if not trigger:
			raise dash.exceptions.PreventUpdate

		idx = trigger["index"]
		if idx >= len(n_clicks_list) or not n_clicks_list[idx]:
			raise dash.exceptions.PreventUpdate

		selected_bound = values[idx]

		for name, value in zip(sorted(bpmn_store[IMPACTS_NAMES]), selected_bound):
			bound_store[BOUND][name] = float(value)

		return bound_store

