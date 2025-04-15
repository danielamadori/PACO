import dash_bootstrap_components as dbc
from dash import html, dcc
from env import DELAYS, PROBABILITIES, LOOP_PROBABILITY, LOOP_ROUND


def create_table(columns, rows):
	return html.Div([
		dbc.Table(
			[html.Thead(html.Tr([html.Th(col) for col in columns]))] + rows,
			bordered=False,
			hover=True,
			responsive=True,
			striped=True,
			className="table-sm",
			style={
				"width": "auto",
				"margin": "auto",
				"borderCollapse": "collapse"
			}
		)
	], style={
		"display": "inline-block",
		"padding": "10px",
		"border": "1px solid #ccc",
		"borderRadius": "10px",
		"marginTop": "20px",
		"verticalAlign": "top"
	})


def choices_table(data, choices):
	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=data[DELAYS].get(name, 0), type="number", min=0, step=1, debounce=True,
							  id={'type': 'choice-delay', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in choices
	]

	return create_table(["Choices", "Delay"], rows)


def natures_table(data, natures):
	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=data[PROBABILITIES].get(name, 0.5), type="number", min=0, max=1, step=0.001, debounce=True,
							  id={'type': 'nature-prob', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in natures
	]
	return create_table(["Natures", "Probability"], rows)


def loops_table(data, loops):
	rows = [
		html.Tr([
			html.Td(name),
			html.Td(dcc.Input(value=data[LOOP_PROBABILITY].get(name, 0.5), type="number", min=0, max=1, step=0.001, debounce=True,
							  id={'type': 'loop-prob', 'index': name}, style={'width': '7ch', "border": "none"})),
			html.Td(dcc.Input(value=data[LOOP_ROUND].get(name, 1), type="number", min=1, max=100, step=1, debounce=True,
							  id={'type': 'loop-round', 'index': name}, style={'width': '7ch', "border": "none"}))
		]) for name in loops
	]
	return create_table(["Loops", "Probability", "Max Iteration"], rows)
