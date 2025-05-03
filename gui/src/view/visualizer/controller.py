from uuid import uuid4
from dash import Output, Input, State, ctx, html
from dash.exceptions import PreventUpdate


def register_render_svg(callback, input_id, visualizer_id, id_div_svg, zoom_in_id, zoom_slider_id, zoom_out_id, zoom_reset_id, zoom_min, zoom_max):
	print("register_render_svg")

	@callback(
		Output(id_div_svg, "children"),
		Output(zoom_slider_id, "value"),
		Input(input_id, "data"),
		Input(zoom_slider_id, "value"),
		Input(zoom_reset_id, "n_clicks"),
		Input(zoom_in_id, "n_clicks"),
		Input(zoom_out_id, "n_clicks"),
		State(visualizer_id, "clientWidth"),
		State(visualizer_id, "clientHeight"),
		prevent_initial_call=True
	)
	def render_and_zoom(dot_data, zoom_value, reset_clicks, plus_clicks, minus_clicks,
						container_width, container_height):
		print(dot_data)
		if not dot_data or "bpmn" not in dot_data:
			raise PreventUpdate
		print("ok")
		svg = dot_data["bpmn"]
		triggered = ctx.triggered_id
		zoom = zoom_value

		if triggered == zoom_reset_id:
			zoom = 1.0
		elif triggered == zoom_in_id:
			zoom = round(min(zoom_max, zoom + 0.1), 1)
		elif triggered == zoom_out_id:
			zoom = round(max(zoom_min, zoom - 0.1), 1)

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
