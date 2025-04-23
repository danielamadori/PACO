import dash_bootstrap_components as dbc
from dash import html, dcc

ZOOM_MIN = 0.1
ZOOM_MAX = 3.0


def get_zoom_bar():
	marks= {
		x: str(x)
		for x in sorted(set(
			[ZOOM_MIN, ZOOM_MAX] +
			[round(i * 0.5, 1) for i in range(int(ZOOM_MIN * 2) + 1, int(ZOOM_MAX * 2) + 1)]
		))
	}
	return html.Div([
		dbc.Button("+", id="increase-zoom", color="light", size="sm", className="mb-1"),
		dcc.Slider(
			id="zoom-slider",
			min=ZOOM_MIN,
			max=ZOOM_MAX,
			step=0.1,
			value=1.0,
			included=False,
			vertical=True,
			tooltip={"placement": "right", "always_visible": True},
			updatemode="drag",
			marks = marks

		),
		dbc.Button("−", id="decrease-zoom", color="light", size="sm", className="mt-1"),
		dbc.Button("1x", id="reset-zoom", color="light", size="sm", className="mt-1")
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
