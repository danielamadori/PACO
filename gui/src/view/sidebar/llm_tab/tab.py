from dash import dcc, html

from view.sidebar.llm_tab.header import get_header
from view.sidebar.llm_tab.input_bar import get_input_bar


def get_llm_tab():
	return dcc.Tab(
		label='Copilot',
		value='tab-llm',
		style={'flex': 1, 'textAlign': 'center'},
		children=[
			html.Div([
				get_header(),

				html.Div(
					id='chat-output',
					style={
						'height': '380px',
						'overflowY': 'auto',
						'backgroundColor': '#f9f9f9',
						'padding': '10px',
						'border': '1px solid #ccc',
						'borderRadius': '10px',
						'display': 'flex',
						'flexDirection': 'column',
						'gap': '10px',
						'textAlign': 'left'
					}
				),

				get_input_bar(),

				html.Div(id='dummy-output', style={'display': 'none'}),
			], style={'padding': '20px'})
		]
	)
