import dash_bootstrap_components as dbc
from dash import html


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
