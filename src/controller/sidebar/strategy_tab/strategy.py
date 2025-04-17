import requests
from dash import Input, Output, State, html
from controller.sidebar.strategy_tab.table.update_advaced_table import register_advance_table_callbacks
from model.etl import load_strategy
from env import IMPACTS_NAMES
from view.sidebar.strategy_tab.strategy_result import strategy_results
import dash


def register_strategy_callbacks(strategy_callback):
	register_advance_table_callbacks(strategy_callback)

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

			g = {"sort_by": None, "sort_order": "asc", "data": guaranteed_bounds}
			p ={"sort_by": None, "sort_order": "asc", "data": possible_min_solution}

			return (strategy_results(
						result, expected_impacts,
						guaranteed_bounds, possible_min_solution,
						bdds, sorted(bpmn_store[IMPACTS_NAMES])),
					g, p)

		except requests.exceptions.HTTPError as e:
			return html.Div(f"HTTP Error ({e})", style={"color": "red"}), dash.no_update, dash.no_update

