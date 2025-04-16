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

