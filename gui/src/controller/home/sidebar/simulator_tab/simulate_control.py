from dash import callback, Input, Output, State, ctx
from model.petri_net import simulate_execution


def register_simulator_callbacks(callback):
	@callback(
		Output("simulation-store", "data"),
		Input("btn-back", "n_clicks"),
		Input("btn-forward", "n_clicks"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def run_simulation_on_step(btn_back_clicks, btn_forward_clicks, bpmn_store):
		triggered = ctx.triggered_id
		step = -1 if triggered == "btn-back" else 1 if triggered == "btn-forward" else 0

		if step == 0:
			return ctx.states.get("simulation-store.data", {})

		return simulate_execution(bpmn_store, step)
