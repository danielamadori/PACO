from dash import html
from view.visualizer.controller import register_render_svg
from view.visualizer.zoom import get_zoom_bar

def get_visualizer(callback, input_id = "dot-store", visualizer_id="main-content", zoom_min = 0.1, zoom_max = 3.0):
	zoom_component, zoom_in_id, zoom_slider_id, zoom_out_id, zoom_reset_id = get_zoom_bar(visualizer_id, zoom_min, zoom_max)

	id_div_svg = visualizer_id + "_svg"
	register_render_svg(callback, input_id, visualizer_id, id_div_svg, zoom_in_id, zoom_slider_id, zoom_out_id, zoom_reset_id, zoom_min, zoom_max)

	return html.Div([
		zoom_component,
		html.Div(
			id=id_div_svg,
			style={
				"flex": "1",
				"overflow": "scroll",
				"height": "100%",
				"width": "100%"
			}
		),
	],
		id=visualizer_id,
		style={
			"flex": "1",
			"height": "100%",
			"overflow": "hidden",
			"padding": "0",
			"display": "flex",
			"flexDirection": "column",
			"gap": "0.5rem",
			"position": "relative"
		})
