import dash
import dash_bootstrap_components as dbc
from dash import Output, Input, State, ALL

from controller.db import load_bpmn_dot
from env import IMPACTS_NAMES, extract_nodes, SESE_PARSER, EXPRESSION, IMPACTS
from view.sidebar.bpmn_tab.table.tasks_table import create_tasks_table


def register_task_impacts_callbacks(tasks_callbacks):
	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Output('task-table', 'children', allow_duplicate=True),
		Input('add-impact-button', 'n_clicks'),
		State('new-impact-name', 'value'),
		State('bpmn-store', 'data'),
		prevent_initial_call='initial_duplicate'
	)
	def add_impact_column(n_clicks, new_impact_name, bpmn_store):
		tasks_table = dash.no_update

		if not new_impact_name or new_impact_name.strip() == '':
			return bpmn_store, dash.no_update, "", tasks_table

		new_impact_name = new_impact_name.strip()
		if new_impact_name in bpmn_store[IMPACTS_NAMES]:
			return dash.no_update, dash.no_update, dbc.Alert(f"Impact '{new_impact_name}' already exists.", color="warning", dismissable=True), tasks_table

		bpmn_store[IMPACTS_NAMES].append(new_impact_name)

		tasks, _, _, _ = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
		for task in tasks:
			if new_impact_name not in bpmn_store[IMPACTS][task]:
				bpmn_store[IMPACTS][task][new_impact_name] = 0.0

		tasks_table = create_tasks_table(bpmn_store, tasks)

		try:
			#print(f"tasks_impacts.py add: {bpmn_store[IMPACTS]}")
			bpmn_dot = load_bpmn_dot(bpmn_store)
		except Exception as exception:
			return dash.no_update, dash.no_update, dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True), tasks_table

		return bpmn_store, {"bpmn" : bpmn_dot}, '', tasks_table


	@tasks_callbacks(
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output("dot-store", "data", allow_duplicate=True),
		Output('bpmn-alert', 'children', allow_duplicate=True),
		Output('task-table', 'children', allow_duplicate=True),
		Input({'type': 'remove-impact', 'index': ALL}, 'n_clicks'),
		State('bpmn-store', 'data'),
		State({'type': 'remove-impact', 'index': ALL}, 'id'),
		prevent_initial_call='initial_duplicate'
	)
	def remove_impact_column(n_clicks_list, bpmn_store, id_list):
		changed = False
		tasks_table = dash.no_update
		last_impacts = ''
		alert = ''
		for n_clicks, id_obj in zip(n_clicks_list, id_list):
			if n_clicks > 0:
				impact_to_remove = id_obj['index']
				if impact_to_remove in bpmn_store[IMPACTS_NAMES]:
					bpmn_store[IMPACTS_NAMES].remove(impact_to_remove)
					last_impacts = impact_to_remove
					changed = True
				else:
					return dash.no_update, dash.no_update, dbc.Alert(f"Impact '{impact_to_remove}' does not exist.", color="warning", dismissable=True), tasks_table

		if changed:
			if len(bpmn_store[IMPACTS_NAMES]) == 0:
				bpmn_store[IMPACTS_NAMES].append(last_impacts)
				alert = dbc.Alert("At least one impact must be present.", color="danger", dismissable=False)

			tasks, _, _, _ = extract_nodes(SESE_PARSER.parse(bpmn_store[EXPRESSION]))
			tasks_table = create_tasks_table(bpmn_store, tasks)

			try:
				#print(f"tasks_impacts.py remove: {bpmn_store[IMPACTS]}")
				bpmn_dot = load_bpmn_dot(bpmn_store)
			except Exception as exception:
				if alert == '':
					dbc.Alert(f"Processing error: {str(exception)}", color="danger", dismissable=True)

				return bpmn_store, dash.no_update, alert, tasks_table

			return bpmn_store, {"bpmn" : bpmn_dot}, alert, tasks_table

		return bpmn_store, dash.no_update, alert, tasks_table
