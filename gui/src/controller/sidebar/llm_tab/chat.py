from dash import Input, Output, State
import random, dash

from controller.sidebar.llm_tab.effects import register_llm_effects_callbacks
from controller.sidebar.llm_tab.reset import register_llm_reset_callbacks
from model.etl import load_bpmn_dot
from model.llm import llm_response
from view.sidebar.llm_tab.chat import get_message
from controller.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from view.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from view.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from view.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from env import IMPACTS_NAMES, BOUND, EXPRESSION, SESE_PARSER, extract_nodes


def register_llm_callbacks(callback, clientside_callback):
	register_llm_reset_callbacks(callback)
	register_llm_effects_callbacks(callback, clientside_callback)

	@callback(
		Output('chat-history', 'data', allow_duplicate=True),
		Output('pending-message', 'data', allow_duplicate=True),
		Output('chat-input', 'value'),
		Input('chat-send-btn', 'n_clicks'),
		State('chat-input', 'value'),
		State('chat-history', 'data'),
		prevent_initial_call=True
	)
	def send_message(n_clicks, user_input, history):
		if not user_input:
			raise dash.exceptions.PreventUpdate
		if history is None:
			history = []
		loading_id = f'loading-{random.randint(1000,9999)}'
		history.append({'type': 'user', 'text': user_input})
		history.append({'type': 'ai', 'text': '...', 'id': loading_id})
		return history, loading_id, ''

	@callback(
		Output('chat-history', 'data', allow_duplicate=True),
		Output('pending-message', 'data', allow_duplicate=True),
		Output('bpmn-store', 'data', allow_duplicate=True),
		Output('bound-store', 'data', allow_duplicate=True),
		Output('dot-store', 'data', allow_duplicate=True),
		Output('task-impacts-table', 'children', allow_duplicate=True),
		Output('task-durations-table', 'children', allow_duplicate=True),
		Output('choice-table', 'children', allow_duplicate=True),
		Output('nature-table', 'children', allow_duplicate=True),
		Output('loop-table', 'children', allow_duplicate=True),
		Input('pending-message', 'data'),
		State('chat-history', 'data'),
		State('bpmn-store', 'data'),
		State('bound-store', 'data'),
		prevent_initial_call=True
	)
	def resolve_response(pending_id, history, bpmn_store, bound_store):
		if not pending_id or not history:
			raise dash.exceptions.PreventUpdate

		replaced = False
		for i in range(len(history) - 1, -1, -1):
			if history[i].get('id') == pending_id:
				history[i]['text'], new_bpmn = llm_response(bpmn_store, history[i - 1]['text'])
				del history[i]['id']
				replaced = True
				break

		if not replaced:
			raise dash.exceptions.PreventUpdate

		tasks_impacts_table = dash.no_update
		tasks_duration_table = dash.no_update
		choices_table = dash.no_update
		natures_table = dash.no_update
		loops_table = dash.no_update
		bpmn_dot = dash.no_update

		if EXPRESSION not in new_bpmn:
			history[i]['text'] += "\nNo expression found in the BPMN"
			return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

		new_bpmn[EXPRESSION] = new_bpmn[EXPRESSION].replace("\n", "").replace("\t", "").strip().replace(" ", "")
		if new_bpmn[EXPRESSION] == '':
			history[i]['text'] += "\nEmpty expression found in the BPMN"
			return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

		try:
			SESE_PARSER.parse(new_bpmn[EXPRESSION])
		except Exception as e:
			history[i]['text'] += f"\nParsing error: {str(e)}"
			return history, None, bpmn_store, bound_store, bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table


		tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(new_bpmn[EXPRESSION]))
		#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
		tasks_impacts_table = create_tasks_impacts_table(new_bpmn, tasks)
		tasks_duration_table = create_tasks_duration_table(new_bpmn, tasks)

		#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
		choices_table = create_choices_table(new_bpmn, choices)
		#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
		natures_table = create_natures_table(new_bpmn, natures)
		#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
		loops_table = create_loops_table(new_bpmn, loops)

		try:
			bpmn_dot = {"bpmn" : load_bpmn_dot(new_bpmn)}
			#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
			return history, None, new_bpmn, sync_bound_store_from_bpmn(new_bpmn, bound_store), bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

		except Exception as exception:
			history[i]['text'] += f"\nProcessing bpmn image error: {str(exception)}"
		return history, None, new_bpmn, sync_bound_store_from_bpmn(bpmn_store, bound_store), bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table


	@callback(
		Output('chat-output', 'children'),
		Input('chat-history', 'data'),
		prevent_initial_call=True
	)
	def render_chat(history):
		if not history:
			return []
		return [ get_message(msg) for msg in history ]

