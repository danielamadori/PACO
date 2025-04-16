import dash
from dash import Dash, html, dcc, Input, Output, State, ctx
from dash_split_pane import DashSplitPane

app = Dash(__name__)
app.config.suppress_callback_exceptions = True

app.layout = html.Div([
	# Stato della visibilità della sidebar
	dcc.Store(id="sidebar-visible", data=True),

	# Navbar in alto
	html.Div([
		html.Button("☰", id="toggle-sidebar", n_clicks=0, style={
			"fontSize": "24px", "padding": "5px 15px", "margin": "10px", "cursor": "pointer"
		}),
		html.Span("PACO GUI", style={"fontSize": "20px", "marginLeft": "10px", "color": "white"})
	], style={
		"height": "50px",
		"backgroundColor": "#333",
		"color": "white",
		"display": "flex",
		"alignItems": "center"
	}),

	# Contenuto principale sotto la navbar
	html.Div(id="main-layout", style={"height": "calc(100vh - 50px)"})
])

# Callback per disegnare il layout principale in base alla visibilità della sidebar
@app.callback(
	Output("main-layout", "children"),
	Input("sidebar-visible", "data")
)
def render_layout(sidebar_visible):
	if sidebar_visible:
		return DashSplitPane(
			split="vertical",
			minSize=150,
			maxSize="40%",
			size=250,
			children=[
				# Sidebar
				html.Div([
					html.Div([
						html.Button("Tab1", id="tab1-btn", n_clicks=1, style={
							"width": "50%", "padding": "10px", "backgroundColor": "#444", "color": "white"
						}),
						html.Button("Tab2", id="tab2-btn", n_clicks=0, style={
							"width": "50%", "padding": "10px", "backgroundColor": "#444", "color": "white"
						}),
					], style={"display": "flex", "borderBottom": "1px solid #ccc"}),

					html.Div(id="tab-content", style={
						"padding": "10px",
						"backgroundColor": "#ddd",
						"height": "100%",
						"overflow": "auto"
					})
				], style={"backgroundColor": "#ccc", "height": "100%"}),

				# Contenuto principale
				html.Div("Contenuto principale", id="main-content", style={
					"padding": "20px",
					"height": "100%",
					"overflow": "auto",
					"backgroundColor": "#f8f8f8"
				})
			],
			style={"height": "100%"}
		)
	else:
		# Solo contenuto principale quando sidebar nascosta
		return html.Div("Contenuto principale", id="main-content", style={
			"padding": "20px",
			"height": "100%",
			"overflow": "auto",
			"backgroundColor": "#f8f8f8"
		})

# Callback per nascondere/mostrare la sidebar
@app.callback(
	Output("sidebar-visible", "data"),
	Input("toggle-sidebar", "n_clicks"),
	State("sidebar-visible", "data"),
	prevent_initial_call=True
)
def toggle_sidebar(n, current_state):
	return not current_state

# Callback per i contenuti delle tab
@app.callback(
	Output("tab-content", "children"),
	Input("tab1-btn", "n_clicks"),
	Input("tab2-btn", "n_clicks"),
	prevent_initial_call="initial_duplicate"
)
def switch_tab(tab1_clicks, tab2_clicks):
	clicked = ctx.triggered_id
	if clicked == "tab2-btn":
		return html.Div([
			html.Div("Div 1 in Tab2", style={"backgroundColor": "#aaf", "padding": "10px", "marginBottom": "10px"}),
			html.Div("Div 2 in Tab2", style={"backgroundColor": "#faa", "padding": "10px", "marginBottom": "10px"}),
			html.Div("Div 3 in Tab2", style={"backgroundColor": "#afa", "padding": "10px"})
		])
	return html.Div([
		html.Div("Div 1 in Tab1", style={"backgroundColor": "#ffa", "padding": "10px", "marginBottom": "10px"}),
		html.Div("Div 2 in Tab1", style={"backgroundColor": "#aff", "padding": "10px", "marginBottom": "10px"}),
		html.Div("Div 3 in Tab1", style={"backgroundColor": "#faf", "padding": "10px"})
	])

if __name__ == "__main__":
	app.run_server(debug=True)
