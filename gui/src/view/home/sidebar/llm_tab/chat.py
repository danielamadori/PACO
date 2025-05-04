from dash import html

def get_message(msg):
	return html.Div(
		msg['text'],
		style={
			'alignSelf': 'flex-end' if msg['type'] == 'user' else 'flex-start',
			'backgroundColor': '#d1e7dd' if msg['type'] == 'user' else '#e2e3e5',
			'padding': '8px 12px',
			'borderRadius': '12px',
			'maxWidth': '75%'
		}
	)