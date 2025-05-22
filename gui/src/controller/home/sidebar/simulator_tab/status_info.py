from dash import callback, Input, Output, html
from view.home.sidebar.simulator_tab.status_info import update_status_info


def register_status_info_callbacks(callback):
	@callback(
		Output("status-info-content", "children"),
		Input("simulation-store", "data"),
		prevent_initial_call=False
	)
	def update(data):
		impacts = data["impacts"]
		expected_values = data["expected_impacts"]
		time = data["execution_time"]
		probability = data["probability"]

		return update_status_info(impacts, expected_values, time, probability)

