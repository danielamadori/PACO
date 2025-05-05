from dash import Output, Input, dcc

from env import extract_nodes, SESE_PARSER, EXPRESSION, IMPACTS, IMPACTS_NAMES
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
        tasks, choices, natures, loops = extract_nodes(SESE_PARSER.parse(bpmn[EXPRESSION]))

        converted = {}
        for task in tasks:
            impact = bpmn[IMPACTS][task]
            converted[task] = dict(zip(bpmn[IMPACTS_NAMES], impact))
        bpmn[IMPACTS] = converted

        bpmn_dot = load_bpmn_dot(bpmn)
    except Exception as exception:
        raise RuntimeError(f"Failed to load BPMN dot: {exception}")

    return bpmn, bpmn_dot
