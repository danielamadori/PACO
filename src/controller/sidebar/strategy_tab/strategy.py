import requests
from dash import Input, Output, State, html
from model.etl import filter_bpmn, load_strategy
from env import EXPRESSION, IMPACTS_NAMES, BOUND, extract_nodes, SESE_PARSER
from view.sidebar.strategy_tab.strategy_result import strategy_results, render_table
import dash
from dash import ctx, ALL

def register_strategy_callbacks(strategy_callback):
	@strategy_callback(
		Output("strategy_output", "children", allow_duplicate=True),
		Output("sort_store_guaranteed", "data", allow_duplicate=True),
		Output("sort_store_possible_min", "data", allow_duplicate=True),
		Input("find-strategy-button", "n_clicks"),
		State("bpmn-store", "data"),
		State("bound-store", "data"),
		prevent_initial_call=True
	)
	def find_strategy(n_clicks, bpmn_store, bound_store):
		try:
			result, expected_impacts, guaranteed_bounds, possible_min_solution, bdds = load_strategy(bpmn_store, bound_store)
			return (
				strategy_results(
					result,
					expected_impacts,
					guaranteed_bounds,
					possible_min_solution,
					bdds,
					sorted(bpmn_store[IMPACTS_NAMES])
				),
				{
					"sort_by": None,
					"sort_order": "asc",
					"data": guaranteed_bounds
				},
				{
					"sort_by": None,
					"sort_order": "asc",
					"data": possible_min_solution
				}
			)
		except requests.exceptions.HTTPError as e:
			return html.Div(f"HTTP Error ({e})", style={"color": "red"}), dash.no_update, dash.no_update

	@strategy_callback(
		Output("guaranteed-table", "children"),
		Output("sort_store_guaranteed", "data"),
		Input({"type": "sort-header", "column": ALL, "table": "guaranteed"}, "n_clicks"),
		State("sort_store_guaranteed", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_guaranteed_table(_, store, bpmn_store):
		if not ctx.triggered_id or ctx.triggered_id.get("table") != "guaranteed":
			raise dash.exceptions.PreventUpdate

		sort_by = ctx.triggered_id["column"]
		current = store.get("sort_by")
		order = store.get("sort_order", "asc")
		new_order = "desc" if sort_by == current and order == "asc" else "asc"

		return render_table(
			sorted(bpmn_store[IMPACTS_NAMES]),
			store["data"],
			include_button=True,
			button_prefix="selected_bound",
			sort_by=sort_by,
			sort_order=new_order,
			table="guaranteed"
		), {
			"sort_by": sort_by,
			"sort_order": new_order,
			"data": store["data"]
		}

	@strategy_callback(
		Output("possible_min-table", "children"),
		Output("sort_store_possible_min", "data"),
		Input({"type": "sort-header", "column": ALL, "table": "possible_min"}, "n_clicks"),
		State("sort_store_possible_min", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def update_possible_min_table(_, store, bpmn_store):
		if not ctx.triggered_id or ctx.triggered_id.get("table") != "possible_min":
			raise dash.exceptions.PreventUpdate

		sort_by = ctx.triggered_id["column"]
		current = store.get("sort_by")
		order = store.get("sort_order", "asc")
		new_order = "desc" if sort_by == current and order == "asc" else "asc"

		return render_table(
			sorted(bpmn_store[IMPACTS_NAMES]),
			store["data"],
			include_button=True,
			button_prefix="selected_bound",
			sort_by=sort_by,
			sort_order=new_order,
			table="possible_min"
		), {
			"sort_by": sort_by,
			"sort_order": new_order,
			"data": store["data"]
		}