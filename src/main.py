import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from src.env import APP_NAME
from src.view.components.navbar import navbar
from src.view.home import layout as home_layout
from src.view.syntax import layout as syntax_layout
from src.view.example import layout as example_layout
from src.view.not_found import layout as not_found_layout

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
    navbar(),
    html.Div(id='page-content')
])


@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/syntax':
        return syntax_layout()
    elif pathname == '/example':
        return example_layout()
    elif pathname == '/':
        return home_layout()
    else:
        return not_found_layout()


if __name__ == "__main__":
    app.run_server(debug=True)
