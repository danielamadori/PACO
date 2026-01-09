import dash_bootstrap_components as dbc
from dash import html
from gui.src.env import IMPACTS_NAMES
from gui.src.view.example.standard_layout import get_download_layout, get_description, get_render_example


def get_fourth_example(id, bpmn, bpmn_dot):
	return dbc.Card([
		dbc.CardHeader("Example of BPMN+CPI"),
		dbc.CardBody([
			dbc.Container([
				dbc.Row([
					dbc.Col([
						html.Div([
							get_description(bpmn, '''The BPMN diagram (shown in figure) represents a container terminal harbor process used as a use case in the tool paper. 
							It models vessel unloading operations, container handling with different equipment (MRG for large containers, trailers for small ones), 
							storage decisions, and final transportation via train or truck.''', impacts=True)
						], style={'width': '100%', 'textAlign': 'left'}, className="mb-3"),
						get_download_layout(id + "-download",
											f'''Now it's your turn!
								Download the BPMN JSON file and try to find a winning strategy that respects the expected impact bounds [173.75, 66.4, 1.172, 18.3525],
								respectively for [{', '.join(bpmn[IMPACTS_NAMES])}].
							''')
					], width=4),
					dbc.Col(get_render_example(bpmn_dot, id, zoom_min=1.0, zoom_max=5.0), width=8)
				], class_name="mb-4")
			], fluid=True)
		])])


