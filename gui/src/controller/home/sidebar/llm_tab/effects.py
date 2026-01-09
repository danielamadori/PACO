from dash import Output, Input


def register_llm_effects_callbacks(callback, clientside_callback):
	@callback(
		Output('chat-send-btn', 'disabled'),
		Output('chat-send-btn', 'style'),
		Output('chat-clear-btn', 'disabled'),
		Output('chat-clear-btn', 'style'),
		Output('llm-provider', 'disabled'),
		Output('llm-model', 'disabled'),
		Output('llm-api-key', 'disabled'),
		Output('llm-model-custom', 'disabled'),
		Input('pending-message', 'data'),
		Input('reset-trigger', 'data'),
		prevent_initial_call=False
	)
	def toggle_buttons(pending, resetting):
		is_disabled = pending is not None or resetting
		style = {
			'padding': '10px 20px',
			'borderRadius': '5px',
			'backgroundColor': '#007bff',
			'color': 'white',
			'border': 'none',
			'cursor': 'not-allowed' if is_disabled else 'pointer',
			'opacity': '0.6' if is_disabled else '1'
		}
		clear_style = style.copy()
		clear_style['backgroundColor'] = '#dc3545'
		return is_disabled, style, is_disabled, clear_style, is_disabled, is_disabled, is_disabled, is_disabled

	clientside_callback(
		"""
		function(children) {
			var chatOutput = document.getElementById('chat-output');
			if (chatOutput) {
				chatOutput.scrollTop = chatOutput.scrollHeight;
			}
			return '';
		}
		""",
		Output('dummy-output', 'children'),
		Input('chat-output', 'children'),
		prevent_initial_call=True
	)
