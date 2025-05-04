from dash import html, dcc


from view.visualizer.RenderSVG import RenderSvg


def get_bdds(bdds: dict):
	elements = []

	for choice in sorted(bdds.keys()):
		type_strategy, svg = bdds[choice]
		label = type_strategy.replace("_", " ").title()

		elements.append(
			dcc.Store(id={"type": "bdd-store", "index": choice}, data=svg)
		)
		visualizer = RenderSvg(type="bdd", index=choice, zoom_bar_placement="right", zoom_bar_height=250, default_zoom=0.4)
		elements.append(html.Div([
			html.Div([
				html.H5(choice, className="mb-0"),
				html.P(f"Type: {label}", className="text-body mb-0"),
			], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center"}, className="mb-2"),
			html.Div(
				visualizer.get_visualizer(),
				style={"height": "300px", "width": "100%", "overflow": "auto"}
			),
			html.Hr()
		]))

	return html.Div(
		elements,
		className="p-3 sidebar-box",
		style={"height": "100%", "width": "100%", "overflow": "auto"}
	)
