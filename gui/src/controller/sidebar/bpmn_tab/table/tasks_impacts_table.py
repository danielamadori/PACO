import dash
from dash import Input, Output, State, ALL
import dash_bootstrap_components as dbc
from model.etl import load_bpmn_dot
from env import IMPACTS


def register_task_impacts_callbacks(tasks_callbacks):
	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': ALL, 'index': ALL}, 'value'),
		State({'type': ALL, 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_impacts(values, ids, bpmn_store):
		updated = False
		for value, id_obj in zip(values, ids):
			id_type = id_obj['type']
			if id_type.startswith('impact-'):
				impact_name = id_type.replace('impact-', '')
				task = id_obj['index']

				updated = True
				if task not in bpmn_store[IMPACTS]:
					bpmn_store[IMPACTS][task] = {}
					value = 0.0

				bpmn_store[IMPACTS][task][impact_name] = float(value)

		if updated:
			try:
				#print(f"tasks_table.py impacts: {bpmn_store[IMPACTS]}")
				bpmn_dot = load_bpmn_dot(bpmn_store)
			except Exception as exception:
				return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

			return bpmn_store, {"bpmn" : bpmn_dot}, ''

		return bpmn_store, dash.no_update, ''
