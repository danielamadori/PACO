from dash import Input, Output, State
import random, dash

from controller.sidebar.llm_tab.effects import register_llm_effects_callbacks
from controller.sidebar.llm_tab.reset import register_llm_reset_callbacks
from model.llm import llm_response
from view.sidebar.llm_tab.chat import get_message


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
		Input('pending-message', 'data'),
		State('chat-history', 'data'),
		State('bpmn-store', 'data'),
		prevent_initial_call=True
	)
	def resolve_response(pending_id, history, bpmn_store):
		if not pending_id or not history:
			raise dash.exceptions.PreventUpdate
		for i in range(len(history) - 1, -1, -1):
			if history[i].get('id') == pending_id:
				history[i]['text'], bpmn_store = llm_response(bpmn_store, history[i - 1]['text'])
				del history[i]['id']
				break
		return history, None, bpmn_store

	@callback(
		Output('chat-output', 'children'),
		Input('chat-history', 'data'),
		prevent_initial_call=True
	)
	def render_chat(history):
		if not history:
			return []
		return [ get_message(msg) for msg in history ]

