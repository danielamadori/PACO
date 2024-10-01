from datetime import datetime
import os

import numpy as np

from utils.print_sese_diagram import print_sese_diagram
from solver.solver import paco_solver

bpmn_ex = {
    "stateful_example" : [
        {'impacts_names': ['a', 'b'],
         'expression': '((T1 /[C1] T2) || (( (T3 ^[N2] T4), TU1) ^[N1] ( (T5 ^[N3] T6), TU2)))',
         'impacts': {'T1': [3, 1], 'T2': [1, 3], 'T3': [2, 0], 'T4': [0, 2], 'TU1': [3, 1], 'T5': [2, 0], 'T6': [0, 2], 'TU2': [1, 3]}, 'durations': {'T1': [0, 1], 'T2': [0, 1], 'T3': [0, 1], 'T4': [0, 1], 'TU1': [0, 1], 'T5': [0, 1], 'T6': [0, 1], 'TU2': [0, 1]}, 'probabilities': {'N2': 0.2, 'N1': 0.3, 'N3': 0.4},
         'loops_prob': {},
         'names': {'C1': 'C1', 'N2': 'N2', 'N1': 'N1', 'N3': 'N3'},
         'delays': {'C1': 1}, 'loop_round': {}, 'h': 0,
         }, [5, 6]
    ],
    "unavoidable_example" : [
        {'impacts_names': ['a', 'b'],
         'expression': '((T1 /[C1] T2) || ((TD1, (T3 ^[N2] T4), TU1) ^[N1] (TD2,  (T5 ^[N3] T6), TU2)))',
         'impacts': {'T1': [3, 1], 'T2': [1, 3], 'T3': [2, 0], 'T4': [0, 2], 'TU1': [3, 1], 'T5': [2, 0], 'T6': [0, 2], 'TU2': [1, 3], 'TD1': [0, 0], 'TD2': [0, 0]},
         'durations': {'T1': [0, 1], 'T2': [0, 1], 'T3': [0, 1], 'T4': [0, 1], 'TU1': [0, 1], 'T5': [0, 1], 'T6': [0, 1], 'TU2': [0, 1], 'TD1': [0, 2], 'TD2': [0, 2]}, 'probabilities': {'N2': 0.2, 'N1': 0.3, 'N3': 0.4},
         'loops_prob': {},
         'names': {'C1': 'C1', 'N2': 'N2', 'N1': 'N1', 'N3': 'N3'},
         'delays': {'C1': 1}, 'loop_round': {}, 'h': 0,
         }, [5, 6]
    ],
    "natures of natures": [
        {"expression": "(Task1 ^ [N1] T2) ^[N] (T3 ^ [N2] T4)",
        "h": 0,
        "impacts": {"Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
        "durations": {"Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
        "impacts_names": ["cost", "hours"],
        "probabilities": {"N": 0.5, "N1": 0.6, "N2": 0.7}, "names": {}, "delays": {}, 'loops_prob' : {}, 'loop_round': {}
        }, [23.3, 24.4]],

    "just task, no strategy (no choice)": [{"expression": "T1, T2",
          "h": 0, 
          "impacts": {"T1": [11, 15], "T2": [4, 2]},
          "durations": {"T1": [0, 100], "T2": [0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loop_round': {}
        }, [15, 17]],

    "one choice, strategy with one obligated decision (current impacts)": [{"expression": "T0, (T1 / [C1] T2)",
          "h": 0, 
          "impacts": {"T0": [11, 15], "T1": [4, 2] , "T2": [3, 3]},
          "durations": {"T0": [0, 100], "T1": [0, 100], "T2":[0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 0},'loops_prob' : {}, 'loop_round': {}
        }, [14, 18]], #[15, 17]
    
    "only natures, no strategy (no choice)": [{"expression": "SimpleTask1, (Task1 ^ [N1] T2)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100]}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {'N1':'N1'}, "delays": {},'loops_prob' : {}, 'loop_round': {}
        }, [14.7, 16.7]],
    
    "sequential choices": [{"expression": "SimpleTask1,  (Task1 / [C1] T2),  (T3 / [C2] T4)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {'C1':'C1', 'C2':'C2'}, "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loop_round': {}
        }, [23, 26]], #[23, 26], [25, 22], [22, 25], [24, 21]

    "bpmn_seq_natures": [{"expression": "SimpleTask1,  (Task1 ^ [N1] T2),  (T3 ^ [N2] T4)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6, "N2": 0.7}, "names": {}, "delays": {}, 'loops_prob' : {}, 'loop_round': {}
        }, [23.3, 24.4]],

    "bpmn_choices_natures": [{"expression": "(Cutting, ((HP ^ [N1]LP ) || ( FD / [C1] RD)), (HPHS / [C2] LPLS))",
          "h": 0, 
          "impacts": {"Cutting": [11, 15], "HP": [4, 2], "LP": [3, 1] , "FD": [8, 9], "RD": [10, 5] , "HPHS": [4, 7], "LPLS": [3, 8]}, 
          "durations": {"Cutting": 1, "HP": 1, "LP": 1, "FD": 1, "RD":1 , "HPHS": 1, "LPLS": 1}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {"C1": "C1", "C2": "C2", "N1": "N1"}, "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loop_round': {}
        }, [26, 33.3]],

    "bpmn_prof": [{"expression": "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3)",
        "h": 0,
        "impacts": {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0]},
        "durations": {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100},
        "impacts_names": ["cost", "r", "s", "e"],
        "probabilities": {"N1": 0.5, "N2": 0.5},
        "loops_prob": {},
        "names": {"N1": "N1", "N2": "N2", "c1": "c1"},
        "delays": {"c1": 0}, "loop_round": {}
        }, [1, 1, 1, 1]],

    "bpmn_unavoidable_tasks": [{"expression": "(TaskA ^ [C1] TaskB), Task2",
        "h": 0,
        "impacts": {"TaskA": [10], "TaskB": [10], "Task2": [10]},
        "durations": {"TaskA": 100, "TaskB": 100, "Task2": 100},
        "impacts_names": ["cost"],
        "probabilities": {"C1": 0.5}, "names": {"C1": "C1"}, "delays": {"C1": 0},'loops_prob' : {}, 'loop_round': {}
        }, [20]],

    "bpmn_unavoidable_tasks2": [{"expression": "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3), t4",
                   "h": 0,
                   "impacts": {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0], "t4": [1, 1, 1, 1]},
                   "durations": {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100, "t4": 100},
                   "impacts_names": ["cost", "r", "s", "e"],
                   "probabilities": {"N1": 0.5, "N2": 0.5},
                   "loops_prob": {},
                   "names": {"N1": "N1", "N2": "N2", "c1": "c1"},
                   "delays": {"c1": 0}, "loop_round": {}
                   }, [2, 2, 2, 2]],

    "bpmn_unavoidable_tasks3": [{"expression": "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3), t4, t5",
                    "h": 0,
                    "impacts": {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0], "t4": [1, 1, 1, 1], "t5": [1, 1, 1, 1]},
                    "durations": {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100, "t4": 100, "t5": 100},
                    "impacts_names": ["cost", "r", "s", "e"],
                    "probabilities": {"N1": 0.5, "N2": 0.5},
                    "loops_prob": {},
                    "names": {"N1": "N1", "N2": "N2", "c1": "c1"},
                    "delays": {"c1": 0}, "loop_round": {}
                    }, [3, 3, 3, 3]],

    "choice not explained": [{
        "expression": "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), (TA_C2 / [C2] TB_C2))",
        "h": 0,
        "impacts": {"T1": [11, 15], "TA_N1": [4, 2], "TB_N1": [3, 1] , "TA_C1": [8, 9], "TB_C1": [10, 5] , "TA_C2": [4, 7], "TB_C2": [3, 8]},
        "durations": {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1},
        "impacts_names": ["cost", "hours"],
        "probabilities": {"N1": 0.6}, "names": {"C1": "C1", "C2": "C2", "N1": "N1"},
        "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loop_round': {}
        }, [30, 30]],

    #TODO
    "complete coloring strategy tree example": [{
        "expression": "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), ((TA_C2 / [C2] TB_C2) || (TA_N2 ^[N2] TB_N2)))",
        "h": 0,
        "impacts": {"T1": [1, 2], "TA_N1": [10, 5], "TB_N1": [5, 10] , "TA_C1": [20, 10], "TB_C1": [21, 11] , "TA_C2": [20, 10], "TB_C2": [10, 20], "TA_N2": [10, 5], "TB_N2": [5, 10]},
        "durations": {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1, "TA_N2": 1, "TB_N2": 1},
        "impacts_names": ["A", "B"],
        "probabilities": {"N1": 0.6, "N2": 0.5}, "names": {"C1": "C1", "C2": "C2", "N1": "N1", "N2": "N2"},
        "delays": {"C1": 1, "C2": 0},'loops_prob' : {}, 'loop_round': {}
    }, [57, 48]],

    # TODO "multi condition BDD"
}


def test(name, bpmn, bound):
    print('Type bpmn: ', name)
    text_result, found, choices, name_svg = paco_solver(bpmn, np.array(bound, dtype=np.float64))
    print('Type bpmn: ', name)


def test_calc_strategy_paco(bpmn_ex_dicts:dict, selected:int = -1):
    if selected == -1:
        for name, example in bpmn_ex_dicts.items():
            print(name, example[0], example[1])
            test(name, example[0], example[1])
            #ask a string in input if the string is not yes exit
            answer = input("Do you want to continue? (yes/no): ")
            if answer != "yes" and answer != "y":
                break
    else:
        name, example = list(bpmn_ex_dicts.items())[selected]
        test(name, example[0], example[1])



bpmn_paper_example = {
    "Figure 1": [{
        "expression": "(Cutting, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))), (HPHS / [C2] LPLS))",
        "h": 0,
        "impacts": {"Cutting": [10, 1], "Bending": [20, 1], "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1], "FD": [30, 1], "RD": [10, 1], "HPHS": [40, 1], "LPLS": [20, 3]},
        "durations": {"Cutting": [0, 1], "Bending": [0, 1], "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1], "FD": [0, 1], "RD": [0, 1], "HPHS": [0, 1], "LPLS": [0, 2]},
        "impacts_names": ["electric energy", "worker hours"],
        "probabilities": {"N1": 0.2}, "names": {"C1": "C1", "C2": "C2", "N1": "N1"}, "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loop_round': {}
        }, [135, 7]],
    #TODO loops
    "loop": [{
        "expression": "(T1, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))))",
        "h": 0,
        "impacts": {"T1": [10, 1], "Bending": [20, 1], "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1], "FD": [30, 1], "RD": [10, 1]},
        "durations": {"T1": [0, 1], "Bending": [0, 1], "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1], "FD": [0, 1], "RD": [0, 1]},
        "impacts_names": ["electric energy", "worker hours"],
        "probabilities": {"N1": 0.2}, "names": {"C1": "C1", "N1": "N1"}, "delays": {"C1": 0},'loops_prob' : {}, 'loop_round': {}
    }, [100, 7]],
}

#test_calc_strategy_paco(bpmn_paper_example, 0)

test_calc_strategy_paco(bpmn_ex, 14)

#test_calc_strategy_paco(bpmn_ex, 0) #statefull example
#test_calc_strategy_paco(bpmn_ex, 1) #unavoidable example
#test_calc_strategy_paco(bpmn_ex, 4) #current impacts (one obligated decision)
#test_calc_strategy_paco(bpmn_ex, 8) #current impacts


#test_calc_strategy_paco(bpmn_ex, 14)


#Testing StrategyTree:
#test_calc_strategy_paco(bpmn_ex, 0) # Not pruned ask if okay, stateful example
#test_calc_strategy_paco(bpmn_ex, 1) # Not pruned ask if okay, unavoidable example
#test_calc_strategy_paco(bpmn_ex, 4) # Okay, current impacts (one obligated decision)
#test_calc_strategy_paco(bpmn_ex, 6) # Okay, current impacts (two obligated decision)
#test_calc_strategy_paco(bpmn_ex, 8) # Okay, current impacts
#test_calc_strategy_paco(bpmn_ex, 9) # Not pruned ask if okay, all leaves in the frontier
