import dash_bootstrap_components as dbc
from dash import html, dcc

def get_main_content():
	return html.Div([
		dcc.Store(id="svg-zoom", data=1.0),

		html.Div([
			dbc.Button("+", id="increase-zoom", color="light", size="sm", className="mb-1"),
			dcc.Slider(
				id="zoom-slider",
				min=0.1,
				max=3.0,
				step=0.1,
				value=1.0,
				included=False,
				vertical=True,
				tooltip={"placement": "right", "always_visible": False},
				updatemode="drag"
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
		}),

		html.Div(
			id="svg-bpmn",
			style={
				"flex": "1",
				"overflow": "scroll",
				"height": "100%",
				"width": "100%"
			}
		)
	],
		id="main-content",
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
