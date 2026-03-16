from uuid import uuid4
from dash import Output, Input, State, html, dcc, MATCH, ctx
import dash_bootstrap_components as dbc

class RenderSvg:
	def __init__(self, type, index, zoom_min=0.1, zoom_max=2.0, zoom_bar_placement="left", zoom_bar_height=300, default_zoom=1.0):

		self.type = type
		self.index = index

		self.input_store_id = {"type": f"{type}-store", "index": index}
		self.visualizer_id = {"viz_type": f"{type}-content", "index": index}
		self.svg_div_id = {"viz_type": f"{type}-svg", "index": index}
		self.svg_wrap_id = {"viz_type": f"{type}-svg-wrap", "index": index}
		self.zoom_reset_id = {"viz_type": f"{type}-reset-zoom", "index": index}
		self.zoom_in_id = {"viz_type": f"{type}-increase-zoom", "index": index}
		self.zoom_out_id = {"viz_type": f"{type}-decrease-zoom", "index": index}
		self.zoom_fit_id = {"viz_type": f"{type}-fit-zoom", "index": index}
		self.orientation_toggle_id = {"viz_type": f"{type}-orientation-toggle", "index": index}
		self.zoom_settings_id = {"viz_type": f"{type}-zoom-settings", "index": index}
		self.zoom_value_id = {"viz_type": f"{type}-zoom-value", "index": index}
		self.orientation_value_id = {"viz_type": f"{type}-orientation", "index": index}
		self.zoom_label_id = {"viz_type": f"{type}-zoom-label", "index": index}

		self.zoom_min = zoom_min
		self.zoom_max = zoom_max
		self.default_zoom = default_zoom

		self.zoom_bar_placement = zoom_bar_placement
		self.zoom_bar_height = zoom_bar_height

	def get_visualizer(self, zoom_bar_placement=True, height=0):
		elements = [
			dcc.Store(id=self.zoom_settings_id, data={"min": self.zoom_min, "max": self.zoom_max, "default": self.default_zoom}),
			dcc.Store(id=self.zoom_value_id, data=self.default_zoom),
			dcc.Store(id=self.orientation_value_id, data="horizontal"),
		]

		svg_style = {"height": "100%", "overflow": "auto"}
		if zoom_bar_placement:
			elements.append(self.get_zoom_bar())
			svg_style["width"] = "100%"

		elements.append(html.Div(id=self.svg_div_id, style=svg_style))

		if height > 0:
			return html.Div(elements, id=self.visualizer_id,
					style={"position": "relative", "height": f"{height}px", "width": "calc(100% - 60px)", "display": "flex",
			"flexDirection": "column", "flex": "1"})


		return html.Div(elements, id=self.visualizer_id, style={"position": "relative", "height": "100%", "width": "100%", "display": "flex",
										 "flexDirection": "column", "flex": "1" })

	def get_zoom_bar(self):
		return html.Div([
			dbc.Button("+", id=self.zoom_in_id, color="light", size="sm", className="mb-1"),
			dbc.Button("−", id=self.zoom_out_id, color="light", size="sm", className="mt-1"),
			html.Div("100%", id=self.zoom_label_id, style={"fontSize": "0.8rem", "marginTop": "0.35rem"}),
			# dbc.Button("Rotate", id=self.orientation_toggle_id, color="light", size="sm", className="mt-1"),
			dbc.Button("Auto", id=self.zoom_fit_id, color="light", size="sm", className="mt-1"),
			dbc.Button("Reset", id=self.zoom_reset_id, color="light", size="sm", className="mt-1")
		], style={
			"position": "absolute",
			"top": "3.5rem",
			self.zoom_bar_placement: "1.2rem",
			"display": "flex",
			"flexDirection": "column",
			"alignItems": "center",
			"background": "rgba(255,255,255,0.9)",
			"padding": "0.5rem",
			"borderRadius": "0.5rem",
			"boxShadow": "0 0 5px rgba(0,0,0,0.2)",
			"zIndex": 10
		})

	@staticmethod
	def register_callbacks(callback, type, clientside_callback):

		@callback(
			Output({"viz_type": f"{type}-svg", "index": MATCH}, "children"),
			Input({"type": f"{type}-store", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-zoom-value", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-zoom-settings", "index": MATCH}, "data")
		)
		def render_and_zoom(dot_data, zoom_value, orientation_value, zoom_settings):

			if not dot_data:
				return html.Div("")

			if not zoom_settings or "min" not in zoom_settings or "max" not in zoom_settings:
				default_zoom = 1.0
			else:
				default_zoom = zoom_settings.get("default", 1.0)

			svg = dot_data
			zoom = zoom_value if zoom_value is not None else default_zoom
			is_vertical = orientation_value == "vertical"
			rotation = " rotate(90deg)" if is_vertical else ""
			transform_origin = "center center" if is_vertical else "0 0"

			current_index = None
			try:
				current_index = ctx.outputs_list[0]["id"]["index"]
			except Exception:
				current_index = "main"

			return html.Div([
				html.Div(
					html.ObjectEl(
						data=svg,
						type="image/svg+xml",
						style={
							"width": "100%",
							"height": "100%",
							"transform": f"scale({zoom}){rotation}",
							"transformOrigin": transform_origin,
							"cursor": "grab"
						}
					),
					id={"viz_type": f"{type}-svg-wrap", "index": current_index},
					style={
						"display": "flex",
						"alignItems": "center",
						"justifyContent": "center",
						"height": "100%",
						"width": "100%",
					}
				)
			], key=str(uuid4()))

		clientside_callback(
			"""
			function(plusClicks, minusClicks, resetClicks, fitClicks, orientationValue, svgData, zoomValue, zoomSettings, containerId) {
				var ctx = dash_clientside.callback_context;
				if (!ctx.triggered || ctx.triggered.length === 0) {
					return window.dash_clientside.no_update;
				}

				var zoomMin = 0.1;
				var defaultZoom = 1.0;
				if (zoomSettings) {
					if (zoomSettings.min !== undefined && zoomSettings.min !== null) {
						zoomMin = zoomSettings.min;
					}
					if (zoomSettings.default !== undefined && zoomSettings.default !== null) {
						defaultZoom = zoomSettings.default;
					}
				}

				var zoom = (zoomValue === null || zoomValue === undefined) ? defaultZoom : zoomValue;
				var triggered = ctx.triggered_id;

				if (triggered && triggered.viz_type === """ + f"\"{type}-increase-zoom\"" + """) {
					return Math.round((zoom + 0.1) * 10) / 10;
				}
				if (triggered && triggered.viz_type === """ + f"\"{type}-decrease-zoom\"" + """) {
					return Math.round(Math.max(zoomMin, zoom - 0.1) * 10) / 10;
				}
				var isFitTrigger = triggered && triggered.viz_type === """ + f"\"{type}-fit-zoom\"" + """;
				var isOrientationTrigger = triggered && triggered.viz_type === """ + f"\"{type}-orientation\"" + """;
				if (isFitTrigger || isOrientationTrigger) {
					if (!svgData || !containerId) {
						return zoom;
					}

					var comma = svgData.indexOf(",");
					if (comma === -1) {
						return zoom;
					}

					var svgText = "";
					try {
						svgText = atob(svgData.slice(comma + 1));
					} catch (e) {
						return zoom;
					}

					var viewBoxMatch = svgText.match(/viewBox="([^"]+)"/);
					var width = null;
					var height = null;
					if (viewBoxMatch && viewBoxMatch[1]) {
						var parts = viewBoxMatch[1].trim().split(/[\\s,]+/);
						if (parts.length >= 4) {
							width = parseFloat(parts[2]);
							height = parseFloat(parts[3]);
						}
					}

					if (!width || !height) {
						var widthMatch = svgText.match(/width="([^"]+)"/);
						var heightMatch = svgText.match(/height="([^"]+)"/);
						if (widthMatch && heightMatch) {
							width = parseFloat(widthMatch[1]);
							height = parseFloat(heightMatch[1]);
						}
					}

					if (!width || !height) {
						return zoom;
					}

					var idString = JSON.stringify(containerId);
					var container = document.getElementById(idString);
					if (!container) {
						container = document.querySelector('[id*="' + containerId.viz_type + '"]');
					}
					if (!container) {
						return zoom;
					}

					var cw = container.clientWidth;
					var ch = container.clientHeight;
					if (!cw || !ch) {
						return zoom;
					}

				var orientation = orientationValue || "horizontal";
				var availableHeight = ch;
				if (orientation === "vertical") {
					var nav = document.querySelector(".navbar");
					var navBottom = nav && nav.getBoundingClientRect ? nav.getBoundingClientRect().bottom : 0;
					var rect = container.getBoundingClientRect ? container.getBoundingClientRect() : null;
					var overlap = 0;
					if (rect && navBottom > rect.top) {
						overlap = navBottom - rect.top;
					}
					if (overlap > 0) {
						availableHeight = Math.max(0, ch - overlap) || ch;
					}
				}

					var fitScale = Math.min(cw / width, availableHeight / height);
					if (!isFinite(fitScale) || fitScale <= 0) {
						return zoom;
					}

					if (orientation === "vertical") {
						var fitScaleRot = Math.min(cw / height, availableHeight / width);
						if (!isFinite(fitScaleRot) || fitScaleRot <= 0) {
							return zoom;
						}
						return fitScaleRot / fitScale;
					}

					return 1.0;
				}
				if (triggered && triggered.viz_type === """ + f"\"{type}-reset-zoom\"" + """) {
					if (!svgData || !containerId) {
						return zoom;
					}

					var comma = svgData.indexOf(",");
					if (comma === -1) {
						return zoom;
					}

					var svgText = "";
					try {
						svgText = atob(svgData.slice(comma + 1));
					} catch (e) {
						return zoom;
					}

					var viewBoxMatch = svgText.match(/viewBox="([^"]+)"/);
					var width = null;
					var height = null;
					if (viewBoxMatch && viewBoxMatch[1]) {
						var parts = viewBoxMatch[1].trim().split(/[\\s,]+/);
						if (parts.length >= 4) {
							width = parseFloat(parts[2]);
							height = parseFloat(parts[3]);
						}
					}

					if (!width || !height) {
						var widthMatch = svgText.match(/width="([^"]+)"/);
						var heightMatch = svgText.match(/height="([^"]+)"/);
						if (widthMatch && heightMatch) {
							width = parseFloat(widthMatch[1]);
							height = parseFloat(heightMatch[1]);
						}
					}

					if (!width || !height) {
						return zoom;
					}

					var idString = JSON.stringify(containerId);
					var container = document.getElementById(idString);
					if (!container) {
						container = document.querySelector('[id*="' + containerId.viz_type + '"]');
					}
					if (!container) {
						return zoom;
					}

					var cw = container.clientWidth;
					var ch = container.clientHeight;
					if (!cw || !ch) {
						return zoom;
					}

					var baseScale = Math.min(cw / width, ch / height);
					if (!isFinite(baseScale) || baseScale <= 0) {
						return zoom;
					}

					return 1 / baseScale;
				}

				return zoom;
			}
			""",
			Output({"viz_type": f"{type}-zoom-value", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-increase-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-decrease-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-reset-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-fit-zoom", "index": MATCH}, "n_clicks"),
			Input({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			State({"type": f"{type}-store", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-zoom-value", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-zoom-settings", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-svg", "index": MATCH}, "id"),
			prevent_initial_call=True
		)

		clientside_callback(
			"""
			function(zoomValue, svgData, orientationValue, containerId) {
				var zoom = (zoomValue === null || zoomValue === undefined) ? 1.0 : zoomValue;
				var label = Math.round(zoom * 100) + "%";
				if (!svgData || !containerId) {
					return label;
				}

				var comma = svgData.indexOf(",");
				if (comma === -1) {
					return label;
				}

				var svgText = "";
				try {
					svgText = atob(svgData.slice(comma + 1));
				} catch (e) {
					return label;
				}

				var viewBoxMatch = svgText.match(/viewBox="([^"]+)"/);
				var width = null;
				var height = null;
				if (viewBoxMatch && viewBoxMatch[1]) {
					var parts = viewBoxMatch[1].trim().split(/[\\s,]+/);
					if (parts.length >= 4) {
						width = parseFloat(parts[2]);
						height = parseFloat(parts[3]);
					}
				}

				if (!width || !height) {
					var widthMatch = svgText.match(/width="([^"]+)"/);
					var heightMatch = svgText.match(/height="([^"]+)"/);
					if (widthMatch && heightMatch) {
						width = parseFloat(widthMatch[1]);
						height = parseFloat(heightMatch[1]);
					}
				}

				if (!width || !height) {
					return label;
				}

				var idString = JSON.stringify(containerId);
				var container = document.getElementById(idString);
				if (!container) {
					container = document.querySelector('[id*="' + containerId.viz_type + '"]');
				}
				if (!container) {
					return label;
				}

				var cw = container.clientWidth;
				var ch = container.clientHeight;
				if (!cw || !ch) {
					return label;
				}

				var orientation = orientationValue || "horizontal";
				var availableHeight = ch;
				if (orientation === "vertical") {
					var nav = document.querySelector(".navbar");
					var navBottom = nav && nav.getBoundingClientRect ? nav.getBoundingClientRect().bottom : 0;
					var rect = container.getBoundingClientRect ? container.getBoundingClientRect() : null;
					var overlap = 0;
					if (rect && navBottom > rect.top) {
						overlap = navBottom - rect.top;
					}
					if (overlap > 0) {
						availableHeight = Math.max(0, ch - overlap) || ch;
					}
				}

				var baseScale = Math.min(cw / width, availableHeight / height);
				if (!isFinite(baseScale) || baseScale <= 0) {
					return label;
				}

				var effective = baseScale * zoom;
				return Math.round(effective * 100) + "%";
			}
			""",
			Output({"viz_type": f"{type}-zoom-label", "index": MATCH}, "children"),
			Input({"viz_type": f"{type}-zoom-value", "index": MATCH}, "data"),
			Input({"type": f"{type}-store", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-svg", "index": MATCH}, "id"),
		)

		clientside_callback(
			"""
			function(toggleClicks, currentValue) {
				var value = currentValue || "horizontal";
				if (!toggleClicks) {
					return [value, "Rotate"];
				}
				var next = value === "horizontal" ? "vertical" : "horizontal";
				return [next, "Rotate"];
			}
			""",
			Output({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			Output({"viz_type": f"{type}-orientation-toggle", "index": MATCH}, "children"),
			Input({"viz_type": f"{type}-orientation-toggle", "index": MATCH}, "n_clicks"),
			State({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			prevent_initial_call=True
		)

		clientside_callback(
			"""
			function(orientationValue, zoomValue, svgData, wrapId) {
				var orientation = orientationValue || "horizontal";
				var paddingTop = "0px";
				return {
					display: "flex",
					alignItems: orientation === "vertical" ? "flex-start" : "center",
					justifyContent: orientation === "vertical" ? "flex-start" : "center",
					height: "100%",
					width: "100%",
					paddingTop: paddingTop,
					boxSizing: "border-box"
				};
			}
			""",
			Output({"viz_type": f"{type}-svg-wrap", "index": MATCH}, "style"),
			Input({"viz_type": f"{type}-orientation", "index": MATCH}, "data"),
			Input({"viz_type": f"{type}-zoom-value", "index": MATCH}, "data"),
			Input({"type": f"{type}-store", "index": MATCH}, "data"),
			State({"viz_type": f"{type}-svg-wrap", "index": MATCH}, "id"),
			prevent_initial_call=True
		)
