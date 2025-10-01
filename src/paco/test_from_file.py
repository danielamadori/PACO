import json
import numpy as np
from src.paco.solver import paco
from src.utils.env import (
    IMPACTS_NAMES,
    EXPRESSION,
    H,
    IMPACTS,
    DURATIONS,
    LOOP_PROBABILITY,
    DELAYS,
    PROBABILITIES,
    LOOP_ROUND,
)

# Read bpmn dict from file
bpmn = json.load(open('test' + '.json'))
bpmn = {eval(k):v  for k, v in bpmn.items()}


bound = np.array([0.1] * len(bpmn[IMPACTS_NAMES]), dtype=np.float64)

results = paco(bpmn, bound)

print(results)