from dash import html


def get_bdds(bdds: dict):
	elements = []
	for choice, v in bdds.items():
		type_strategy, bdd_dot = v
		label = type_strategy.replace("_", " ").title()

		elements.append(html.Div([
			html.Div([
				html.H5(choice, className="mb-0"),
				html.P(f"Type: {label}", className="text-body mb-0"),
			], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, className="mb-2"),
			html.Div(
				html.Iframe(
					src=bdd_dot,
					style={"width": "100%", "height": "100%", "border": "none"}
				),
				style={
					"minHeight": "200px",
					"maxHeight": "400px",
					"overflow": "auto",
					"border": "1px solid #eee"
				}
			),
			html.Hr()
		]))

	return html.Div(elements, className="p-3 sidebar-box")
