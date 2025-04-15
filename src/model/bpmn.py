import dash


'''
def update_bpmn_data(bpmn_store):
    for task in tasks:
        if task not in bpmn_store[IMPACTS]:
            bpmn_store[IMPACTS][task] = {}

        if task not in bpmn_store[DURATIONS]:
            bpmn_store[DURATIONS][task] = [0, 1]

    for task in tasks:
        bpmn_store.setdefault(IMPACTS, {}).setdefault(task, {})
        for impact_name in bpmn_store[IMPACTS_NAMES]:
            bpmn_store[IMPACTS][task].setdefault(impact_name, 0.0)

    for choice in choices:
        if choice not in bpmn_store[DELAYS]:
            bpmn_store[DELAYS][choice] = 0
    for nature in natures:
        if nature not in bpmn_store[PROBABILITIES]:
            bpmn_store[PROBABILITIES][nature] = 0.5
    for loop in loops:
        if loop not in bpmn_store[LOOP_PROBABILITY]:
            bpmn_store[LOOP_PROBABILITY][loop] = 0.5
        if loop not in bpmn_store[LOOP_ROUND]:
            bpmn_store[LOOP_ROUND][loop] = 1
'''