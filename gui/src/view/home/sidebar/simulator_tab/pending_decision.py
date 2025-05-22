import dash_bootstrap_components as dbc
from dash import html, dcc

gateway_decisions = {
	"C1": {"T1": 0.5, "T2": 0.3, "T3": 0.2},
	"N2": {"T10": 0.2, "T20": 0.5, "T30": 0.3},
	"C3": {"A": 0.7, "B": 0.3},
	"N4": {"X1": 0.1, "X2": 0.2, "X3": 0.4, "X4": 0.3},
	"C5": {"FinalA": 0.6, "FinalB": 0.4}
}


def get_pending_decisions():
	rows = []
	for gateway_id, decisions in gateway_decisions.items():
		options = list(decisions.keys())

		rows.append(
			html.Div([
				html.Div(gateway_id, style={"fontWeight": "bold", "whiteSpace": "nowrap"}),

				html.Div(
					dcc.Dropdown(
						id=f"{gateway_id}-gateway",
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
					dbc.Button("Random", id=f"{gateway_id}-random", color="primary", size="sm"),
					style={"marginLeft": "auto"}
				)
			],
				style={
					"display": "flex",
					"alignItems": "center",
					"marginBottom": "8px",
					"gap": "10px",
					"flexWrap": "nowrap",
					"width": "100%"
				})
		)

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
				rows,
				style={
					"maxHeight": "150px",
					"overflowY": "auto",
					"overflowX": "auto",
					"padding": "5px"
				}
			)
		)
	],
		className="mb-3",
		style={
			"width": "100%",
			"minWidth": "300px",
			"overflow": "hidden"
		})
