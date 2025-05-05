import dash
from dash import Input, Output, State, ALL, ctx
from env import IMPACTS_NAMES, BOUND
from view.home.sidebar.strategy_tab.table.bound_table import get_bound_table


def sync_bound_store_from_bpmn(bpmn_store, bound_store):
	for name in sorted(bpmn_store[IMPACTS_NAMES]):
		#print("sync_bound_store_from_bpmn: bpmn_store:impacts_names:", name)
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
		if not bpmn_store or not bound_store or BOUND not in bound_store:
			raise dash.exceptions.PreventUpdate

		#print("regenerate_bound_table", bound_store[BOUND])
		return get_bound_table(bound_store, sorted(bpmn_store[IMPACTS_NAMES]))


	@bound_callbacks(
		Output('bound-store', 'data', allow_duplicate=True),
		Input({'type': 'bound-input', 'index': ALL}, 'value'),
		State({'type': 'bound-input', 'index': ALL}, 'id'),
		State('bound-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_bounds(values, ids, bound_store):
		#print("before: update_bounds", bound_store[BOUND])
		for value, id_obj in zip(values, ids):
			bound_store[BOUND][id_obj["index"]] = float(value)

		#print("after: update_bounds", bound_store[BOUND])
		return bound_store


	@bound_callbacks(
		Output("bound-store", "data", allow_duplicate=True),
		Input({"type": "selected_bound", "index": ALL, "table": ALL}, "n_clicks"),
		State("sort_store_guaranteed", "data"),
		State("sort_store_possible_min", "data"),
		State("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_bound_from_select(n_clicks_list, store_guaranteed, store_possible, bound_store, bpmn_store):
		trigger = ctx.triggered_id
		if not trigger or not isinstance(trigger, dict):
			raise dash.exceptions.PreventUpdate

		index = trigger["index"]
		table = trigger["table"]

		n_clicks = n_clicks_list[index] if index < len(n_clicks_list) else 0
		if not n_clicks:
			raise dash.exceptions.PreventUpdate

		if table == "guaranteed":
			selected_store = store_guaranteed
		elif table == "possible_min":
			selected_store = store_possible
		else:
			raise dash.exceptions.PreventUpdate

		if "data" not in selected_store or index >= len(selected_store["data"]):
			raise dash.exceptions.PreventUpdate

		selected_bound = selected_store["data"][index]

		#print("before:update_bound_from_select", bound_store[BOUND])
		for name, value in zip(sorted(bpmn_store[IMPACTS_NAMES]), selected_bound):
			bound_store[BOUND][name] = float(value)
		#print("after:update_bound_from_select", bound_store[BOUND])

		return bound_store
