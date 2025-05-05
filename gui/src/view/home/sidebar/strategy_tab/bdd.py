from dash import html
import dash_bootstrap_components as dbc
from view.home.sidebar.strategy_tab.bdd_visualizer import get_bdds_visualizer


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
