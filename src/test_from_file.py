import json
import numpy as np
from paco.solver import paco
from utils.env import IMPACTS_NAMES, TASK_SEQ, H, IMPACTS, DURATIONS, IMPACTS_NAMES, LOOP_PROB, DELAYS, PROBABILITIES, LOOP_ROUND, NAMES

# Read bpmn dict from file
bpmn = json.load(open('test' + '.json'))
bpmn = {eval(k):v  for k, v in bpmn.items()}
#print(bpmn['IMPACTS_NAMES'])
bound = np.zeros(len(bpmn[IMPACTS_NAMES]), dtype=np.float64)
#np array of ones
#bound = np.ones(len(bpmn[IMPACTS_NAMES]), dtype=np.float64)

text_result, parse_tree, execution_tree, found, min_expected_impacts, max_expected_impacts, choices = paco(bpmn, np.array(bound, dtype=np.float64))
