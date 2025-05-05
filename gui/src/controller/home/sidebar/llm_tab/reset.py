import dash
from dash import Output, Input


def register_llm_reset_callbacks(callback):
	@callback(
		Output('chat-history', 'data', allow_duplicate=True),
		Output('pending-message', 'data', allow_duplicate=True),
		Output('reset-trigger', 'data', allow_duplicate=True),
		Input('chat-clear-btn', 'n_clicks'),
		prevent_initial_call=True
	)
	def reset_chat(n_clicks):
		return [], None, True


	@callback(
		Output('reset-trigger', 'data', allow_duplicate=True),
		Input('reset-trigger', 'data'),
		prevent_initial_call=True
	)
	def acknowledge_reset(trigger):
		if trigger:
			return False
		raise dash.exceptions.PreventUpdate
