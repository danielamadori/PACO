from uuid import uuid4
from dash import Output, Input, State, ctx, html, dcc
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

class RenderSvg:
	def __init__(self,
				 input_store_id="dot-store",
				 visualizer_id="main-content",
				 svg_div_id="svg-bpmn",
				 zoom_slider_id="zoom-slider",
				 zoom_reset_id="reset-zoom",
				 zoom_in_id="increase-zoom",
				 zoom_out_id="decrease-zoom",
				 zoom_min=0.1,
				 zoom_max=3.0):

		self.input_store_id = input_store_id
		self.visualizer_id = visualizer_id
		self.svg_div_id = svg_div_id
		self.zoom_slider_id = zoom_slider_id
		self.zoom_reset_id = zoom_reset_id
		self.zoom_in_id = zoom_in_id
		self.zoom_out_id = zoom_out_id
		self.zoom_min = zoom_min
		self.zoom_max = zoom_max

	def register_callbacks(self, callback):
		@callback(
			Output(self.svg_div_id, "children"),
			Output(self.zoom_slider_id, "value"),
			Input(self.input_store_id, "data"),
			Input(self.zoom_slider_id, "value"),
			Input(self.zoom_reset_id, "n_clicks"),
			Input(self.zoom_in_id, "n_clicks"),
			Input(self.zoom_out_id, "n_clicks"),
			State(self.visualizer_id, "clientWidth"),
			State(self.visualizer_id, "clientHeight"),
			prevent_initial_call=True
		)
		def render_and_zoom(dot_data, zoom_value, reset_clicks, plus_clicks, minus_clicks,
							container_width, container_height):
			if not dot_data or "bpmn" not in dot_data:
				raise PreventUpdate

			svg = dot_data["bpmn"]
			triggered = ctx.triggered_id
			zoom = zoom_value

			if triggered == self.zoom_reset_id:
				zoom = 1.0
			elif triggered == self.zoom_in_id:
				zoom = round(min(self.zoom_max, zoom + 0.1), 1)
			elif triggered == self.zoom_out_id:
				zoom = round(max(self.zoom_min, zoom - 0.1), 1)

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

	def get_visualizer(self, callback):
		self.register_callbacks(callback)

		return html.Div([
			html.Div(id=self.svg_div_id, style={
				"flex": "1",
				"overflow": "scroll",
				"height": "100%",
				"width": "100%"
			}),
			self.get_zoom_bar()
		], id=self.visualizer_id, style={
			"flex": "1",
			"height": "100%",
			"overflow": "hidden",
			"padding": "0",
			"display": "flex",
			"flexDirection": "column",
			"gap": "0.5rem",
			"position": "relative"
		})

	def get_zoom_bar(self):
		marks= {
			x: str(x)
			for x in sorted(set(
				[self.zoom_min, self.zoom_max] +
				[round(i * 0.5, 1) for i in range(int(self.zoom_min * 2) + 1, int(self.zoom_max * 2) + 1)]
			))
		}
		return html.Div([
			dbc.Button("+", id=self.zoom_in_id, color="light", size="sm", className="mb-1"),
			dcc.Slider(id=self.zoom_slider_id, min=self.zoom_min, max=self.zoom_max, step=0.1, value=1.0,
					   included=False,
					   vertical=True,
					   tooltip={"placement": "right", "always_visible": True},
					   updatemode="drag",
					   marks = marks
					   ),
			dbc.Button("−", id=self.zoom_out_id, color="light", size="sm", className="mt-1"),
			dbc.Button("1x", id=self.zoom_reset_id, color="light", size="sm", className="mt-1")
		], style={
			"position": "absolute",
			"bottom": "1rem",
			"left": "1rem",
			"height": "300px",
			"display": "flex",
			"flexDirection": "column",
			"alignItems": "center",
			"background": "rgba(255,255,255,0.9)",
			"padding": "0.5rem",
			"borderRadius": "0.5rem",
			"boxShadow": "0 0 5px rgba(0,0,0,0.2)",
			"zIndex": 10
		})

