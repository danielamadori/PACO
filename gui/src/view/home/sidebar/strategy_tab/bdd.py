from dash import html, dcc
import dash_bootstrap_components as dbc

from view.visualizer.RenderSVG import RenderSvg

def get_bdds_visualizer(choice, type_strategy, svg):
	if type_strategy == "FORCED_DECISION":
		return html.Div(
			html.Iframe(
				src=svg,
				style={"width": "100%", "height": "100%", "border": "none"}
			),
			style={
					"height": "180px",
					"border": "1px solid #eee"
				}
		)

	visualizer = RenderSvg(
		type="bdd",
		index=choice,
		zoom_bar_placement="right",
		zoom_bar_height=250,
		max_height=350
	)

	return html.Div([
		dcc.Store(id={"type": "bdd-store", "index": choice}, data=svg),
		visualizer.get_visualizer()],
		style={"height": "auto", "maxHeight": "350px", "minHeight": "150px", "width": "100%", "overflow": "auto"}
	)



def get_bdds(bdds: dict):
	elements = []

	for choice in sorted(bdds.keys()):
		type_strategy, svg = bdds[choice]

		visualizer = get_bdds_visualizer(choice, type_strategy, svg)

		label = type_strategy.replace("_", " ").title()


		card = dbc.Card(
			[
				dbc.CardHeader(
					html.Div([
						html.H5(choice, className="mb-0"),
						html.P(f"Type: {label}", className="text-body mb-0"),
					], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"})
				),
				dbc.CardBody(visualizer)
			],
			style={"width": "100%", "marginBottom": "1rem"}
		)

		elements.append(card)

	return html.Div(
		elements,
		className="p-3 sidebar-box",
		style={"height": "100%", "width": "100%", "overflow": "auto"}
	)
