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
				multiple=False,
				accept='.json'
			),
			html.Br(),
			html.Button("Download BPMN", id="download-bpmn-btn", className="btn btn-primary"),
			dcc.Download(id="download-bpmn"),
			#html.P("""Here is an example of a BPMN+CPI expression""", className="text-body"),
			#html.P("""Task0, (Task1 || Task4), (Task3 ^[N1] Task9, Task8 /[C1] Task2)""", className="text-body"),
			html.Br(),
			html.Br(),
			get_bpmn_view(),
			html.Br(),
			html.Br()
		],
		className="p-3 sidebar-box")
	])
