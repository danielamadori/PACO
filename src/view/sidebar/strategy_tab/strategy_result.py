from dash import html, dcc
import dash_bootstrap_components as dbc

def render_table(headers, rows, include_button=False, button_prefix="", sort_by=None, sort_order="asc", table=None):
	table_rows = []

	if sort_by in headers:
		idx = headers.index(sort_by)
		rows = sorted(rows, key=lambda r: r[idx], reverse=(sort_order == "desc"))

	for i, row in enumerate(rows):
		cells = [html.Td(value) for value in row]
		if include_button:
			button_id = {"type": button_prefix, "index": i}
			cells.append(
				html.Td(
					dbc.Button("Select", id=button_id, color="primary", size="sm"),
					style={"width": "70px", "textAlign": "center"}
				)
			)
		table_rows.append(html.Tr(cells))

	header_row = []
	for h in headers:
		print(h)
		arrow = "▲" if h == sort_by and sort_order == "asc" else "▼" if h == sort_by else ""
		header_row.append(
			html.Th(
				f"{h} {arrow}",
				id={"type": "sort-header", "column": h, "table": table},
				style={"cursor": "pointer", "userSelect": "none"}
			)
		)

	if include_button:
		header_row.append(html.Th())

	return dbc.Table([
		html.Thead(html.Tr(header_row)),
		html.Tbody(table_rows)
	],
		bordered=True,
		hover=True,
		responsive=True,
		striped=True,
		className="mt-2"
	)

def strategy_results(result: str, expected_impacts: list, guaranteed_bounds: list, possible_min_solution: list, bdds: list, sorted_impact_names: list, sort_by=None, sort_order="asc"):
	elements = [
		html.H5("Result", className="mt-2"),
		html.P(result, className="text-body"),
		html.Hr()
	]

	if expected_impacts:
		elements.append(html.H5("Expected Impacts", className="mt-3"))
		elements.append(render_table(sorted_impact_names, [expected_impacts], table="expected"))

	if guaranteed_bounds:
		elements.append(html.H5("Guaranteed Bounds", className="mt-3"))
		elements.append(html.Div(
			render_table(
				sorted_impact_names,
				guaranteed_bounds,
				include_button=True,
				button_prefix="selected_bound",
				sort_by=sort_by,
				sort_order=sort_order,
				table="guaranteed"
			),
			id="guaranteed-table"
		))

	if possible_min_solution:
		elements.append(html.H5("Possible Min Bounds", className="mt-3"))
		elements.append(html.Div(
			render_table(
				sorted_impact_names,
				possible_min_solution,
				include_button=True,
				button_prefix="selected_bound",
				sort_by=sort_by,
				sort_order=sort_order,
				table="possible_min"
			),
			id="possible_min-table"
		))

	return html.Div(elements, className="p-3 sidebar-box")