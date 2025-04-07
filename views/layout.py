# views/layout.py
from dash import html, dcc
import dash_bootstrap_components as dbc

layout = html.Div([
	dcc.Store(id='bpmn-store', storage_type='session'),  # session storage
	dcc.Tabs(id='tabs', value='expression', children=[
		dcc.Tab(label='Expression', value='expression'),
		dcc.Tab(label='Duration', value='duration'),
		dcc.Tab(label='Details', value='details'),
		dcc.Tab(label='Output', value='output'),
	]),
	html.Div(id='tab-content'),
	# Modal dialog (Bootstrap) for feedback
	dbc.Modal([
		dbc.ModalHeader(dbc.ModalTitle(id="modal-header")),
		dbc.ModalBody(id="modal-body"),
		dbc.ModalFooter(dbc.Button("Close", id="close-modal", className="ml-auto", n_clicks=0))
	], id="modal", is_open=False, centered=True),
])
