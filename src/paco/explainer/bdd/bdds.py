import json

from paco.explainer.bdd.bdd import Bdd
from paco.parser.parse_node import ParseNode
from paco.parser.parse_tree import ParseTree


def bdds_from_json(parseTree: 'ParseTree', data) -> dict[ParseNode:Bdd]:
	if isinstance(data, str):
		data = json.loads(data)

	parseTreeNodes = parseTree.root.to_dict_id_node()
	return {parseTreeNodes[int(choice_id)]: Bdd.from_dict(bdd_data, parseTreeNodes)
							 for choice_id, bdd_data in data.items()}


def bdds_to_dict(bdds: dict[ParseNode:Bdd]) -> dict[int, dict]:
	return {choice.id: bdd.to_dict() for choice, bdd in bdds.items()}


def bdds_to_json(bdds: dict[ParseNode:Bdd]) -> str:
	return json.dumps(bdds_to_dict(bdds), indent=2)
