from dash import Output, Input, dcc
from model.bpmn import validate_bpmn_dict
from model.etl import load_bpmn_dot
from view.visualizer.RenderSVG import RenderSvg


def register_example_callbacks(callback, id, example_path):
	RenderSvg.register_callbacks(callback, id + "-svg")

	@callback(
		Output(id + "-download", "data"),
		Input(id + "-download-btn", "n_clicks"),
		prevent_initial_call=True
	)
	def download_bpmn_example(n_clicks):
		with open(example_path, "r") as file:
			content = file.read()
		return dcc.send_string(
			content,
			filename="example_bpmn.json"
		)


def render_example(data):
	bpmn = validate_bpmn_dict(data.get("bpmn", {}))
	try:
		bpmn_dot = load_bpmn_dot(bpmn)
	except Exception as exception:
		raise RuntimeError(f"Failed to load BPMN dot: {exception}")

	return bpmn, bpmn_dot
