import dash_bootstrap_components as dbc
from src.env import APP_NAME

def navbar():
	return dbc.NavbarSimple(
		children=[
			dbc.NavItem(dbc.NavLink("Home", href="/")),
			dbc.NavItem(dbc.NavLink("Syntax", href="/syntax")),
			dbc.NavItem(dbc.NavLink("Example", href="/example")),
		],
		brand=APP_NAME,
		brand_href="/",
		color="primary",
		dark=True,
	)

