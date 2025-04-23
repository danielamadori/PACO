import json
from dash import Input, Output, State, dcc, callback

from env import extract_nodes, SESE_PARSER, EXPRESSION
from model.etl import filter_bpmn


def register_download_callbacks(callback):
	@callback(
		Output("download-bpmn", "data"),
		Input("download-bpmn-btn", "n_clicks"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def download_bpmn_callback(n_clicks, bpmn_store):
		tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
		bpmn = filter_bpmn(bpmn_store, tasks, choices, natures, loops)

		return dcc.send_string(json.dumps({"bpmn": bpmn}, indent=2), filename="bpmn.json")
