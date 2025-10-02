from dash import Input, Output

from gui.src.view.home.sidebar.simulator_tab.status_info import (
    update_status_info,
)


def register_status_info_callbacks(callback):
    @callback(
        Output("status-info-content", "children"),
        Input("simulation-store", "data"),
        prevent_initial_call=False,
    )
    def update(data):
        impacts = data.get("impacts", {})
        expected_values = data.get("expected_impacts", {})
        time = data.get("execution_time", 0.0)
        probability = data.get("probability", 1.0)

        return update_status_info(impacts, expected_values, time, probability)

