import json
import numpy as np
from paco.solver import paco, json_to_paco
from utils.env import IMPACTS_NAMES, TASK_SEQ, H, IMPACTS, DURATIONS, IMPACTS_NAMES, LOOP_PROB, DELAYS, PROBABILITIES, LOOP_ROUND, NAMES

# Read bpmn dict from file
bpmn = json.load(open('test' + '.json'))
bpmn = {eval(k):v  for k, v in bpmn.items()}

bound = np.ones(len(bpmn[IMPACTS_NAMES]), dtype=np.float64)

json_input = {
	"bpmn": bpmn,
	"bound": bound
}

json_results = json_to_paco(json_input)