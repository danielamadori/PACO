from dash import html, dcc
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
	)

	return html.Div([
		dcc.Store(id={"type": "bdd-store", "index": choice}, data=svg),
		visualizer.get_visualizer()],
		style={"height": "auto", "maxHeight": "350px", "minHeight": "150px", "width": "100%", "overflow": "auto"}
	)
