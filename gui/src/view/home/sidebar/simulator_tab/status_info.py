import dash_bootstrap_components as dbc
from dash import html


def status_info():
	impact_names = ["Cost", "Time", "CO2"]
	impacts_values = [10.5, 24.0, 3.7]
	expected_values = [12.2, 22.1, 4.0]

	def make_table_card(title, names, values):
		header_row = html.Tr([
			html.Th(name, style={
				"whiteSpace": "nowrap",
				"overflow": "hidden",
				"textOverflow": "ellipsis",
				"maxWidth": "80px"
			}) for name in names
		])
		data_row = html.Tr([
			html.Td(str(val)) for val in values
		])
		return dbc.Card([
			dbc.CardHeader(html.H6(title), style={"padding": "0.5rem 1rem", "marginBottom": "0px"}),
			dbc.CardBody([
				dbc.Table([
					html.Thead(header_row),
					html.Tbody([data_row])
				],
					bordered=True,
					striped=True,
					responsive=True,
					className="table-sm",
					style={"borderCollapse": "collapse", "marginBottom": "0px"})
			], style={"padding": "0.5rem 1rem"})
		], style={
			"minWidth": "250px",
			"marginBottom": "10px"
		})

	return dbc.Card([
		dbc.CardHeader(html.H5('Status Info')),
		dbc.CardBody(
			html.Div([
				dbc.Row([
					dbc.Col(html.Div([
						html.Strong("Time: "),
						html.Span(id="execution-time", children="12")
					]), width=6),
					dbc.Col(html.Div([
						html.Strong("Probability: "),
						html.Span(id="execution-probability", children="85%")
					]), width=6),
				], className="mb-3"),

				dbc.Row([
					dbc.Col(make_table_card("Impacts", impact_names, impacts_values)),
					dbc.Col(make_table_card("Expected Impacts", impact_names, expected_values))
				])
			], style={
				"maxHeight": "250px",
				"overflowY": "auto",
				"overflowX": "hidden",
				"padding": "0.5rem"
			})
		)
	], className="mb-3", style={"minHeight": "300px"})
