import dash
from dash import Input, Output, State, ALL
import dash_bootstrap_components as dbc

from controller.db import load_bpmn_dot
from src.env import DURATIONS, IMPACTS, IMPACTS_NAMES, EXPRESSION, SESE_PARSER
from env import extract_nodes
from src.view.components.tasks_table import tasks_table


def register_task_callbacks(tasks_callbacks):
	@tasks_callbacks(
		Output('task-duration', 'children'),
		Input('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def generate_tasks_table(bpmn_store):
		tasks, _, _, _ = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
		if len(tasks) == 0:
			return dash.no_update

		return tasks_table(bpmn_store, tasks)


	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input('add-impact-button', 'n_clicks'),
		State('new-impact-name', 'value'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def add_impact_column(n_clicks, new_impact_name, bpmn_store):
		if not new_impact_name or new_impact_name.strip() == '':
			return bpmn_store, dash.no_update, ""

		new_impact_name = new_impact_name.strip()
		if new_impact_name in bpmn_store[IMPACTS_NAMES]:
			return dash.no_update, dash.no_update, dbc.Alert(f"Impact '{new_impact_name}' already exists.", color="warning", dismissable=True)

		bpmn_store[IMPACTS_NAMES].append(new_impact_name)

		for task in bpmn_store[IMPACTS]:
			if new_impact_name not in bpmn_store[IMPACTS][task]:
				bpmn_store[IMPACTS][task][new_impact_name] = 0.0

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, {"bpmn" : bpmn_dot}, ''


	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'remove-impact', 'index': ALL}, 'n_clicks'),
		State('bpmn-store', 'data'),
		State({'type': 'remove-impact', 'index': ALL}, 'id'),
		prevent_initial_call='initial_duplicate'
	)
	def remove_impact_column(n_clicks_list, bpmn_store, id_list):
		changed = False
		for n_clicks, id_obj in zip(n_clicks_list, id_list):
			if n_clicks > 0:
				impact_to_remove = id_obj['index']
				print("Removing impact:", impact_to_remove)
				if impact_to_remove in bpmn_store[IMPACTS_NAMES]:
					print("Size: bpmn_store[IMPACTS_NAMES]", len(bpmn_store[IMPACTS_NAMES]))
					bpmn_store[IMPACTS_NAMES].remove(impact_to_remove)
					changed = True

		if changed:
			if len(bpmn_store[IMPACTS_NAMES]) == 0:
				print("Removing all impacts")
				return bpmn_store, dash.no_update, dbc.Alert(f"Add an impacts", color="danger", dismissable=True)

			try:
				bpmn_dot = load_bpmn_dot(bpmn_store)
			except Exception as exception:
				return bpmn_store, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

			return bpmn_store, {"bpmn" : bpmn_dot}, ''

		return bpmn_store, dash.no_update, ''


	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': ALL, 'index': ALL}, 'value'),
		State({'type': ALL, 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_impacts_from_inputs(values, ids, bpmn_store):
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

				bpmn_store[IMPACTS][task][impact_name] = value

		if updated:
			try:
				bpmn_dot = load_bpmn_dot(bpmn_store)
			except Exception as exception:
				return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

			return bpmn_store, {"bpmn" : bpmn_dot}, ''

		return bpmn_store, dash.no_update, ''


	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Input({'type': 'min-duration', 'index': ALL}, 'value'),
		Input({'type': 'max-duration', 'index': ALL}, 'value'),
		State({'type': 'min-duration', 'index': ALL}, 'id'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def update_duration_from_inputs(min_values, max_values, ids, bpmn_store):
		for min_v, max_v, id_obj in zip(min_values, max_values, ids):
			task = id_obj['index']
			if task not in bpmn_store[DURATIONS]:
				min_v = 0
				max_v = 1

			bpmn_store[DURATIONS][task] = [min_v, max_v]

		try:
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

		return bpmn_store, {"bpmn" : bpmn_dot}, ''