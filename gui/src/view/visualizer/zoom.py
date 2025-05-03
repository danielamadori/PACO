import dash_bootstrap_components as dbc
from dash import html, dcc

def get_zoom_bar(visualizer_id, zoom_min, zoom_max):
	marks= {
		x: str(x)
		for x in sorted(set(
			[zoom_min, zoom_max] +
			[round(i * 0.5, 1) for i in range(int(zoom_min * 2) + 1, int(zoom_max * 2) + 1)]
		))
	}
	zoom_in_id = visualizer_id + "_increase-zoom"
	zoom_slider_id = visualizer_id + "_zoom-slider"
	zoom_out_id = visualizer_id + "_decrease-zoom"
	zoom_reset_id = visualizer_id + "_reset-zoom"

	return html.Div([
		dbc.Button("+", id=zoom_in_id, color="light", size="sm", className="mb-1"),
		dcc.Slider(
			id=zoom_slider_id,
			min=zoom_min,
			max=zoom_max,
			step=0.1,
			value=1.0,
			included=False,
			vertical=True,
			tooltip={"placement": "right", "always_visible": True},
			updatemode="drag",
			marks = marks

		),
		dbc.Button("−", id=zoom_out_id, color="light", size="sm", className="mt-1"),
		dbc.Button("1x", id=zoom_reset_id, color="light", size="sm", className="mt-1")
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
	}), zoom_in_id, zoom_slider_id, zoom_out_id, zoom_reset_id
