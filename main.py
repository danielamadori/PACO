import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
import dash_auth
import os

# App init
app = dash.Dash(__name__,
                use_pages=True,
                pages_folder="interface/pages",
                external_stylesheets=[dbc.themes.BOOTSTRAP],
                suppress_callback_exceptions=True
                )

app.title = "PACO"
server = app.server
server.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key')

# Basic auth credentials (placeholder)
auth = dash_auth.BasicAuth(app, {
    "admin": "admin"
})

# Layout con navbar e pagine
app.layout = html.Div([
    dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                label="Pages",
                children=[
                    dbc.DropdownMenuItem(page["name"], href=page["path"])
                    for page in dash.page_registry.values()
                ],
                nav=True,
                in_navbar=True,
            ),
        ],
        brand="PACO",
        color="primary",
        dark=True,
    ),
    dash.page_container
])

if __name__ == "__main__":
    app.run_server(debug=True)
