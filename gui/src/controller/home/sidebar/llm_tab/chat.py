from dash import Input, Output, State
import random, dash

from gui.src.controller.home.sidebar.llm_tab.effects import register_llm_effects_callbacks
from gui.src.controller.home.sidebar.llm_tab.model_selector import register_llm_model_selector_callbacks
from gui.src.controller.home.sidebar.llm_tab.reset import register_llm_reset_callbacks
from gui.src.model.etl import load_bpmn_dot
from gui.src.model.llm import llm_response
from gui.src.view.home.sidebar.llm_tab.chat import get_message
from gui.src.controller.home.sidebar.strategy_tab.table.bound_table import sync_bound_store_from_bpmn
from gui.src.view.home.sidebar.bpmn_tab.table.task_impacts import create_tasks_impacts_table
from gui.src.view.home.sidebar.bpmn_tab.table.task_duration import create_tasks_duration_table
from gui.src.view.home.sidebar.bpmn_tab.table.gateways_table import create_choices_table, create_natures_table, create_loops_table
from gui.src.env import EXPRESSION, SESE_PARSER, extract_nodes, IMPACTS, IMPACTS_NAMES, DURATIONS, DELAYS, PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND, H


def register_llm_callbacks(callback, clientside_callback):
	register_llm_reset_callbacks(callback)
	register_llm_effects_callbacks(callback, clientside_callback)
	register_llm_model_selector_callbacks(callback)

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
		Output({"type": "bpmn-svg-store", "index": "main"}, 'data', allow_duplicate=True),
		Output('task-impacts-table', 'children', allow_duplicate=True),
		Output('task-durations-table', 'children', allow_duplicate=True),
		Output('choice-table', 'children', allow_duplicate=True),
		Output('nature-table', 'children', allow_duplicate=True),
		Output('loop-table', 'children', allow_duplicate=True),
		Input('pending-message', 'data'),
		State('chat-history', 'data'),
		State('bpmn-store', 'data'),
		State('bound-store', 'data'),
		State('llm-provider', 'value'),
		State('llm-model', 'value'),
		State('llm-model-custom', 'value'),
		State('llm-api-key', 'value'),
		prevent_initial_call=True
	)
	def resolve_response(pending_id, history, bpmn_store, bound_store, provider, model_choice, custom_model, api_key):
		if not pending_id or not history:
			raise dash.exceptions.PreventUpdate

		replaced = False
		for i in range(len(history) - 1, -1, -1):
			if history[i].get('id') == pending_id:
				history[i]['text'], new_bpmn = llm_response(
					bpmn_store,
					history[i - 1]['text'],
					provider,
					model_choice,
					custom_model,
					api_key,
				)
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
		
		# Ensure all tasks have impacts
		if IMPACTS not in new_bpmn:
			new_bpmn[IMPACTS] = {}
		if IMPACTS_NAMES not in new_bpmn:
			new_bpmn[IMPACTS_NAMES] = bpmn_store.get(IMPACTS_NAMES, [])

		for task in tasks:
			if task not in new_bpmn[IMPACTS]:
				new_bpmn[IMPACTS][task] = {name: 0.0 for name in new_bpmn[IMPACTS_NAMES]}
			# Ensure no missing impact names
			for name in new_bpmn[IMPACTS_NAMES]:
				if name not in new_bpmn[IMPACTS][task]:
					new_bpmn[IMPACTS][task][name] = 0.0

		# Ensure Durations
		if DURATIONS not in new_bpmn:
			new_bpmn[DURATIONS] = {}
		for task in tasks:
			if task not in new_bpmn[DURATIONS]:
				new_bpmn[DURATIONS][task] = [0, 1]

		# Ensure Delays for Choices
		if DELAYS not in new_bpmn:
			new_bpmn[DELAYS] = {}
		for choice in choices:
			if choice not in new_bpmn[DELAYS]:
				new_bpmn[DELAYS][choice] = [0, 0]

		# Ensure Probabilities for Natures
		if PROBABILITIES not in new_bpmn:
			new_bpmn[PROBABILITIES] = {}
		for nature in natures:
			if nature not in new_bpmn[PROBABILITIES]:
				# Default probability? Usually dict of {branch: prob}
				# For now assume nature is just a node ID, probability map is {nature_id: {path: 0.5}}?
				# Let's check etl.py usage. 
				# In etl.py: bpmn[PROBABILITIES] is {nature: bpmn_store...}
				# It seems probability is linked to outgoing paths.
				# If we don't have paths, we can't set it easily.
				# But let's init empty dict if missing.
				new_bpmn[PROBABILITIES][nature] = {} 

		if LOOP_PROBABILITY not in new_bpmn: new_bpmn[LOOP_PROBABILITY] = {}
		if LOOP_ROUND not in new_bpmn: new_bpmn[LOOP_ROUND] = {}
		
		# Ensure Horizon is 0 to avoid parsing issues with scalar impacts
		new_bpmn[H] = 0


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
			bpmn_dot = load_bpmn_dot(new_bpmn)
			#print("resolve_response: bpmn_store:impacts_names:", new_bpmn[IMPACTS_NAMES])
			return history, None, new_bpmn, sync_bound_store_from_bpmn(new_bpmn, bound_store), bpmn_dot, tasks_impacts_table, tasks_duration_table, choices_table, natures_table, loops_table

		except Exception as exception:
			history[i]['text'] += f"\nProcessing bpmn image error: {str(exception)}\nDEBUG BPMN: {str(new_bpmn)}"
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

