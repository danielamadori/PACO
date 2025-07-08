import dash
from dash import html, dcc, Output, Input
import dash_bootstrap_components as dbc
from pathlib import Path
from env import APP_NAME
from view.navbar import navbar
from view.home.layout import layout as home_layout
from view.syntax.layout import layout as syntax_layout
from view.example.layout import layout as example_layout



def load_doc(name: str) -> str | None:
    if name == "/about":
        name = "/index"

    docs_dir = Path(__file__).resolve().parents[2] / "docs"
    doc_path = docs_dir / f"{name.lstrip('/')}.md"

    if not doc_path.exists():
        return None

    text = doc_path.read_text(encoding="utf-8")

    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) == 3:
            text = parts[2]

    text = text.replace("{% include navbar.html %}", "")
    return dcc.Markdown(text, dangerously_allow_html=True)


app = dash.Dash(
    __name__,
    use_pages=False,
    pages_folder="",
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
)

server = app.server
app.title = APP_NAME

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh=False),
        html.Div(id="navbar-container"),
        html.Div(id="page-content"),
    ]
)


@app.callback(
    Output("navbar-container", "children"),
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    nav = navbar(pathname)

    if pathname == "/syntax":
        return nav, syntax_layout()
    elif pathname == "/example":
        return nav, example_layout()
    elif pathname == "/":
        return nav, home_layout()
    elif pathname == "/about" or pathname == "/installation_and_usage":
        page = load_doc(pathname)
        if page is not None:
            return nav, page

    return nav, html.Div(
        [
            html.H1("404 - Page not found"),
        ]
    )


if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
