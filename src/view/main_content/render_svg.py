<<<<<<< HEAD
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
=======
import dash_bootstrap_components as dbc
from dash import html


def get_main_content():
	return html.Div(
		dbc.Spinner(
			html.Div(id="svg-bpmn", style={
				"height": "100%",
				"width": "100%",
			}),
			color="primary",
			type="grow",
			fullscreen=False,
			spinner_style={"width": "4rem", "height": "4rem"}
		),
		id="main-content",
		style={
			"flex": "1",                   # cresce rispetto alla sidebar
			"height": "100%",              # altezza massima nel suo contenitore
			"overflow": "hidden",          # evita scroll inutili
			"padding": "0",                # nessun padding verticale
			"display": "flex",             # container flex
			"flexDirection": "column",     # per espandere figlio verticalmente
		}
	)

>>>>>>> origin/sidebar
