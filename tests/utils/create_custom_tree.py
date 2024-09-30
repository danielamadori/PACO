from parser.tree_lib import CTree
from utils.env import SESE_PARSER, TASK_SEQ, PROBABILITIES, IMPACTS, DURATIONS, NAMES, DELAYS, H, LOOPS_PROB
from parser.parse_tree import from_lark_parsed_to_custom_tree as Lark_to_CTree
from utils import check_syntax as cs

def create_custom_tree(bpmn: dict) -> CTree:
	bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
	custom_tree, last_id = Lark_to_CTree(
			SESE_PARSER.parse(bpmn[TASK_SEQ]),
			bpmn[PROBABILITIES], bpmn[IMPACTS],
			bpmn[DURATIONS], bpmn[NAMES], bpmn[DELAYS],
			h=bpmn[H], loops_prob=bpmn[LOOPS_PROB])

	return custom_tree
