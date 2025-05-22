from view.home.sidebar.simulator_tab.pending_decisions import update_pending_decisions
import random
from dash import callback, Input, Output, State, ctx, no_update
from dash.dependencies import ALL

def register_pending_decision_callbacks(callback):
	@callback(
		Output("pending-decisions-body", "children"),
		Input("simulation-store", "data"),
		prevent_initial_call=False
	)
	def populate_pending_decisions(data):
		return update_pending_decisions(data["gateway_decisions"])


	@callback(
		Output({"type": "gateway", "id": ALL}, "value"),
		Input({"type": "random-button", "id": ALL}, "n_clicks"),
		Input("global-random", "n_clicks"),
		State({"type": "gateway", "id": ALL}, "id"),
		State("simulation-store", "data"),
		prevent_initial_call=True
	)
	def update_random_decisions(individual_clicks, global_click, gateway_ids, sim_data):
		triggered = ctx.triggered_id
		result = []

		for i, gw_obj in enumerate(gateway_ids):
			gw = gw_obj["id"]
			if triggered == {"type": "random-button", "id": gw} or triggered == "global-random":
				options = list(sim_data["gateway_decisions"][gw].keys())
				weights = list(sim_data["gateway_decisions"][gw].values())
				result.append(random.choices(options, weights=weights)[0])
			else:
				result.append(no_update)

		return result