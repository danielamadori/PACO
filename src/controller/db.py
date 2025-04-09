from src.model.sqlite import fetch_diagram_by_bpmn

def load_svg_if_cached(data, bpmn):
	record = fetch_diagram_by_bpmn(bpmn)
	if record and record.bpmn_dot:
		data["svg"] = record.bpmn_dot
		return data, True
	return data, False


def get_execution_and_parse_tree(bpmn):
	record = fetch_diagram_by_bpmn(bpmn)
	if record and record.execution_tree and record.parse_tree:
		return record.execution_tree, record.parse_tree
	return None, None
