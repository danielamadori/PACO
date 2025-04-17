from dash import Output, Input, State, ctx, html
from dash.exceptions import PreventUpdate

def get_visible_marks(zoom, min_zoom=0.1, max_zoom=3.0):
	zoom = round(zoom, 1)
	distance = 0.4
	marks = set()

	marks.add(zoom)

	lower = round(zoom - 0.5, 1)
	if lower >= min_zoom + distance:
		marks.add(lower)

	upper = round(zoom + 0.5, 1)
	if upper <= max_zoom - distance:
		marks.add(upper)


	marks.add(min_zoom)
	marks.add(max_zoom)

	return {v: str(v) for v in sorted(marks)}

def register_render_svg(callback):
	@callback(
		Output("svg-bpmn", "children"),
		Output("zoom-slider", "value"),
		Output("zoom-slider", "marks"),
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

		if triggered == "dot-store" or triggered == "reset-zoom":
			zoom = 1.0
		elif triggered == "increase-zoom":
			zoom = round(min(3.0, zoom + 0.1), 1)
		elif triggered == "decrease-zoom":
			zoom = round(max(0.1, zoom - 0.1), 1)

		marks = get_visible_marks(zoom)

		return html.ObjectEl(
			data=svg,
			type="image/svg+xml",
			style={
				"width": "100%",
				"height": "100%",
				"transform": f"scale({zoom})",
				"transformOrigin": "0 0",
				"cursor": "grab"
			}
		), zoom, marks
