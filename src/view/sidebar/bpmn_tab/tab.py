from dash import dcc, html

from view.sidebar.bpmn_tab.inputs import get_bpmn_view


def get_BPMN_CPI_tab():
	return dcc.Tab(label='BPMN + CPI', value='tab-bpmn', style={'flex': 1, 'textAlign': 'center'}, children=[
		html.Div([
			html.Div(id='bpmn-alert'),
			dcc.Upload(
				id='upload-data',
				children=html.Div([
					'Drag and Drop or ',
					html.A('Select a JSON File')
				]),
				style={
					'width': '90%',
					'height': '60px',
					'lineHeight': '60px',
					'borderWidth': '1px',
					'borderStyle': 'dashed',
					'borderRadius': '5px',
					'textAlign': 'center',
					'margin': '10px'
				},
				multiple=True
			),
			html.Div(id='output-data-upload'),
			html.Br(),
			html.P("""Here is an example of a BPMN+CPI expression""", className="text-body"),
			html.P("""Task0, (Task1 || Task4), (Task3 ^[N1] Task9, Task8 /[C1] Task2)""", className="text-body"),
			html.Br(),
			get_bpmn_view(),
			html.Br(),
			html.Br()
		],
		className="p-3 sidebar-box")
	])

'''
elements.append(html.H5("Expected Impacts", className="mt-2"))
elements.append(html.P(expected_impacts, className="text-body"))
else:
elements.append(html.H5("Guaranteed Bounds", className="mt-3"))
for bound in guaranteed_bounds:
	elements.append(html.P(f"• {bound}", className="text-body"))

elements.append(html.H5("Possible Min Solution", className="mt-3"))
for bound in possible_min_solution:
	elements.append(html.P(f"• {bound}", className="text-body"))

return html.Div(
	elements,
	className="p-3 sidebar-box"
)
'''