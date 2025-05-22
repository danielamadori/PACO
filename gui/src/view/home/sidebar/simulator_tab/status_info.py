import dash_bootstrap_components as dbc
from dash import html


def status_info():
	return dbc.Card([
		dbc.CardHeader(html.H5('Status Info')),
		dbc.CardBody(
			html.Div(id="status-info-content", style={
				"maxHeight": "250px",
				"overflowY": "auto",
				"overflowX": "hidden",
				"padding": "0.5rem"
			})
		)
	], className="mb-3", style={"minHeight": "300px"})


def make_table_card(title, dictionary):
	names = sorted(dictionary.keys())

	header_row = html.Tr([
		html.Th(name, style={
			"whiteSpace": "nowrap",
			"overflow": "hidden",
			"textOverflow": "ellipsis",
			"maxWidth": "80px"
		}) for name in names
	])
	data_row = html.Tr([
		html.Td(str(dictionary[name])) for name in names
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


def update_status_info(impacts, expected_impacts, time, probability):
	return html.Div([
		dbc.Row([
			dbc.Col(html.Div([
				html.Strong("Time: "),
				html.Span(id="execution-time", children=str(time))
			]), width=6),
			dbc.Col(html.Div([
				html.Strong("Probability: "),
				html.Span(id="execution-probability", children=str(round(probability * 100, ndigits=3)) + "%")
			]), width=6),
		], className="mb-3"),
		dbc.Row([
			dbc.Col(make_table_card("Impacts", impacts)),
			dbc.Col(make_table_card("Expected Impacts", expected_impacts))
		])
	])