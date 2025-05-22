import dash_bootstrap_components as dbc
from dash import html, dcc


def get_pending_decisions():
	return dbc.Card([
		dbc.CardHeader(
			html.Div([
				html.H5("Pending Decisions", style={"margin": 0}),
				dbc.Button("Random", id="global-random", color="secondary", size="sm")
			], style={
				"display": "flex",
				"justifyContent": "space-between",
				"alignItems": "center"
			})
		),
		dbc.CardBody(
			html.Div(
				id="pending-decisions-body",
				style={
					"maxHeight": "200px",
					"overflowY": "auto",
					"padding": "5px"
				}
			)
		)
	], className="mb-3", style={
		"width": "100%",
		"minWidth": "300px"
	})


def update_pending_decisions(gateway_decisions):
	rows = []
	for gateway in sorted(gateway_decisions.keys()):
		decisions = gateway_decisions[gateway]
		options = list(decisions.keys())

		rows.append(
			html.Div([
				html.Div(gateway, style={"fontWeight": "bold", "whiteSpace": "nowrap"}),

				html.Div(
					dcc.Dropdown(
						id={"type": "gateway", "id": gateway},
						options=[{'label': d, 'value': d} for d in options],
						value=options[0],
						clearable=False,
						style={
							"textAlign": "left",
							"width": "auto",
							"minWidth": "100px"
						}
					),
					style={"margin": "0 auto"}
				),

				html.Div(
					dbc.Button("Random", id={"type": "random-button", "id": gateway}, color="primary", size="sm"),
					style={"marginLeft": "auto"}
				)
			], style={
				"display": "flex",
				"alignItems": "center",
				"marginBottom": "8px",
				"gap": "10px",
				"flexWrap": "nowrap",
				"width": "100%"
			})
		)
	return rows
