import os
from datetime import datetime

import numpy as np
from torch.fx.experimental.unification.utils import freeze

from utils.env import ALGORITHMS, DURATIONS, IMPACTS, IMPACTS_NAMES  # , DELAYS, NAMES, PROBABILITIES
from solver.test_aalpy import automata_search_strategy
from utils import check_syntax as cs
from utils.print_sese_diagram import print_sese_diagram


def check_input(bpmn:dict, bound:dict):
    bound_list = []
    if bpmn['expression'] == '' or bpmn['expression'] == None:
        return "The expression is empty or None", bound_list
    if bound == {} or bound == None:
        return "The bound is empty or None", bound_list

    try:
        bound_list = list(cs.extract_values_bound(bound))
    except Exception as e:
        return f'Error while parsing the bound: {e}', bound_list

    if bound_list == []:
        return  "The bound is empty or None", bound_list

    return "", bound_list


def calc_strat(bpmn:dict, bound:list, algo:str) -> dict:
    print('calc_strat...')

    # TODO ask emanuele
    if algo == list(ALGORITHMS.keys())[0]:
        bound = np.array(bound, dtype=np.float64)
        text_result, found, choices, name_svg = calc_strategy_paco(bpmn, bound)
    elif algo == list(ALGORITHMS.keys())[1]:
        text_result, found, choices, name_svg = calc_strategy_algo1(bpmn, bound)
    elif algo == list(ALGORITHMS.keys())[2]:
        text_result, found, choices, name_svg = calc_strategy_algo2(bpmn, bound)

    return text_result, found, choices, name_svg





def calc_strategy_paco(bpmn:dict, bound:np.ndarray) -> dict:
    print(f'{datetime.now()} Testing PACO...')
    print(f'{datetime.now()} Bound {bound}')
    bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS]) # set max duration
    print(f'{datetime.now()} bpmn + cpi {bpmn}')

    directory = "assets/bpmnSvg/"
    if not os.path.exists(directory):
        os.makedirs(directory)

    name_svg =  directory + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".svg"
    print_sese_diagram(**bpmn, outfile_svg=name_svg)

    found, expected_impacts, choices, name_svg = automata_search_strategy(bpmn, bound, name_svg)

    if not found:
        text_result = ""
        for i in range(len(expected_impacts)):
            text_result += f"Exp. Impacts {i}:\t{expected_impacts[i]}\n"
        print(f"Failed:\t\t\t{bpmn[IMPACTS_NAMES]}\nBound Impacts:\t{bound}\n" + text_result)
    else:
        expected_impact = expected_impacts[0]
        impacts = "\n".join(f"{key}: {round(value,2)}" for key, value in zip(bpmn[IMPACTS_NAMES],  [item for item in expected_impact]))
        if len(choices) == 0:
            text_result = f"Any choice taken will provide a winning strategy with an expected impact of: {impacts}"
        else:
            text_result = f"This is the strategy, which has as an expected impact of : {impacts}"
        print(str(datetime.now()) + " " + text_result)

    return text_result, found, choices, name_svg


def calc_strategy_algo1(bpmn:dict, bound:list):
    return {}, {}, {}, {}

def calc_strategy_algo2(bpmn:dict, bound:list):
    return {}, {}, {}, {}
