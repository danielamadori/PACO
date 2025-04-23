from uuid import uuid4

from dash import Output, Input, State, ctx, html
from dash.exceptions import PreventUpdate
from view.main_content.zoom import ZOOM_MAX, ZOOM_MIN


def register_render_svg(callback):
	@callback(
		Output("svg-bpmn", "children"),
		Output("zoom-slider", "value"),
		Input("dot-store", "data"),
		Input("zoom-slider", "value"),
		Input("reset-zoom", "n_clicks"),
		Input("increase-zoom", "n_clicks"),
		Input("decrease-zoom", "n_clicks"),
		State("main-content", "clientWidth"),
		State("main-content", "clientHeight"),
		prevent_initial_call=True
	)
	def render_and_zoom(dot_data, zoom_value, reset_clicks, plus_clicks, minus_clicks,
						container_width, container_height):
		if not dot_data or "bpmn" not in dot_data:
			raise PreventUpdate

		svg = dot_data["bpmn"]
		triggered = ctx.triggered_id
		zoom = zoom_value

		#if triggered == "dot-store" or triggered == "reset-zoom":
		if triggered == "reset-zoom":
			zoom = 1.0
		elif triggered == "increase-zoom":
			zoom = round(min(ZOOM_MAX, zoom + 0.1), 1)
		elif triggered == "decrease-zoom":
			zoom = round(max(ZOOM_MIN, zoom - 0.1), 1)

		return html.Div([
			html.Div(
				html.ObjectEl(
					data=svg,
					type="image/svg+xml",
					style={
						"width": "100%",
						"height": "100%",
						"transform": f"scale({zoom})",
						"transformOrigin": "0 0",
						"cursor": "grab"
					}
				),
				style={
					"display": "flex",
					"alignItems": "center",
					"justifyContent": "center",
					"height": "100%",
					"width": "100%",
				}
			)
		], key=str(uuid4())), zoom

