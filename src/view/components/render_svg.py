from dash import html


def render(svg_str:str):
	return html.Iframe(
		src=svg_str,
		style={"width": "100%", "height": "100%", "border": "none"}
	)