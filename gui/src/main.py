import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from env import APP_NAME
from view.navbar import navbar
from view.home import layout as home_layout
from view.syntax import layout as syntax_layout
from view.example import layout as example_layout

app = dash.Dash(
    __name__,
    use_pages=False,
    pages_folder="",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

server = app.server
app.title = APP_NAME

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='navbar-container'),
    html.Div(id='page-content')
])

@app.callback(
    Output('navbar-container', 'children'),
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    nav = navbar(pathname)

    if pathname == '/syntax':
        return nav, syntax_layout()
    elif pathname == '/example':
        return nav, example_layout()
    elif pathname == '/':
        return nav, home_layout()
    else:
        return nav, html.Div([
            html.H1("404 - Page not found"),
        ])



if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
