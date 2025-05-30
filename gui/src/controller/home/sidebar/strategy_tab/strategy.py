import requests
from dash import Input, Output, State, html
from controller.home.sidebar.strategy_tab.table.update_advaced_table import register_advance_table_callbacks
from model.etl import load_strategy
from env import IMPACTS_NAMES
import dash

from view.home.sidebar.strategy_tab.strategy_result import strategy_results
import dash_bootstrap_components as dbc

def register_strategy_callbacks(strategy_callback):
	register_advance_table_callbacks(strategy_callback)

	@strategy_callback(
		Output("strategy_output", "children", allow_duplicate=True),
		Output("sort_store_guaranteed", "data", allow_duplicate=True),
		Output("sort_store_possible_min", "data", allow_duplicate=True),
		Output("strategy-alert", "children"),
		Input("find-strategy-button", "n_clicks"),
		State("bpmn-store", "data"),
		State("bound-store", "data"),
		prevent_initial_call=True
	)
	def find_strategy(n_clicks, bpmn_store, bound_store):
		try:
			alert = ''
			try:
				result, expected_impacts, guaranteed_bounds, possible_min_solution, bdds = load_strategy(bpmn_store, bound_store)
			except ValueError as e:
				alert = dbc.Alert(str(e), color="warning", dismissable=True)
				return html.Div(), dash.no_update, dash.no_update, alert

			g = {"sort_by": None, "sort_order": "asc", "data": guaranteed_bounds}
			p ={"sort_by": None, "sort_order": "asc", "data": possible_min_solution}

			results = strategy_results(
				result, expected_impacts,
				guaranteed_bounds, possible_min_solution, bdds,
				sorted(bpmn_store[IMPACTS_NAMES]))

			return results, g, p, alert

		except requests.exceptions.HTTPError as e:
			alert = dbc.Alert(f"HTTP Error ({e})", color="danger", dismissable=True)
			return html.Div(), dash.no_update, dash.no_update, alert
