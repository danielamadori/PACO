from dash import html, dcc

from view.main_content.zoom import get_zoom_bar


def get_main_content():

	return html.Div([
		get_zoom_bar(),
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
