import dash_bootstrap_components as dbc
from dash import html
from dash import Input, Output, State, ALL, ctx
from env import BOUND, EXPRESSION, IMPACTS_NAMES
from view.home.sidebar.strategy_tab.table.bound_table import get_bound_table

'''
def register_status_info_callbacks(status_info_callbacks):
	@status_info_callbacks(
		Output("bound-table", "children"),
		Input("bound-store", "data"),
		State("bpmn-store", "data"),
		prevent_initial_call=True
	)
	def regenerate_bound_table(bound_store, bpmn_store):
		if not bpmn_store or bpmn_store[EXPRESSION] == '' or not bound_store or BOUND not in bound_store:
			return html.Div()

		return get_bound_table(bound_store, sorted(bpmn_store[IMPACTS_NAMES]))
'''

def status_info():
	#html.Div(id='bound-table')
	return dbc.Card([
		dbc.CardHeader(html.H5('Status Info')),
		dbc.CardBody([
			dbc.Row([
				dbc.Col(html.Div([
					html.Strong("Execution Time: "),
					html.Span(id="execution-time", children="–")
				]), width=6),

				dbc.Col(html.Div([
					html.Strong("Probability: "),
					html.Span(id="execution-probability", children="–")
				]), width=6),
			], className="mb-2"),

			dbc.Row([
				dbc.Col(html.Div([
					html.Strong("Impacts: "),
					html.Span(id="impacts", children="–")
				]), width=6),

				dbc.Col(html.Div([
					html.Strong("Expected Impacts: "),
					html.Span(id="expected-impacts", children="–")
				]), width=6),
			])
		])
	])
