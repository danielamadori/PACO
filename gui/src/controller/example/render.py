from dash import Output, Input, dcc
from gui.src.model.bpmn import validate_bpmn_dict
from gui.src.model.etl import load_bpmn_dot, bpmn_snapshot_to_dot, dot_to_base64svg, _bpmn_to_dot
from gui.src.view.visualizer.RenderSVG import RenderSvg


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
	print("render_example", bpmn)
	try:
		bpmn_dot = _bpmn_to_dot(bpmn)

	except Exception as exception:
		raise RuntimeError(f"Failed to load BPMN dot: {exception}")

	return bpmn, bpmn_dot
