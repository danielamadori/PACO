import random
from dash import callback, ctx, no_update
from dash.dependencies import Input, Output, State
from view.home.sidebar.simulator_tab.pending_decision import gateway_decisions


def register_pending_decision_random_callbacks(callback):
	gateway_ids = list(gateway_decisions.keys())

	@callback(
		[Output(f"{gw}-gateway", "value") for gw in gateway_ids],
		[Input(f"{gw}-random", "n_clicks") for gw in gateway_ids] + [Input("global-random", "n_clicks")],
		[State(f"{gw}-gateway", "value") for gw in gateway_ids],
		prevent_initial_call=True
	)
	def update_random_decision(*args):
		triggered_id = ctx.triggered_id
		n = len(gateway_ids)
		state_values = args[n:]  # current dropdown values
		result = []

		if triggered_id == "global-random":
			# aggiorna tutto secondo le probabilità
			for gw in gateway_ids:
				values = list(gateway_decisions[gw].keys())
				weights = list(gateway_decisions[gw].values())
				result.append(random.choices(values, weights=weights)[0])
		elif triggered_id and triggered_id.endswith("-random"):
			# aggiorna solo il gateway specifico
			for i, gw in enumerate(gateway_ids):
				if triggered_id == f"{gw}-random":
					values = list(gateway_decisions[gw].keys())
					weights = list(gateway_decisions[gw].values())
					result.append(random.choices(values, weights=weights)[0])
				else:
					result.append(no_update)
		else:
			# fallback difensivo
			result = [no_update] * len(gateway_ids)

		return result
