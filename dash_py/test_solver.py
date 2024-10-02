import numpy as np
from utils.env import TASK_SEQ, H, IMPACTS, DURATIONS, IMPACTS_NAMES, PROBABILITIES, NAMES, DELAYS, LOOPS_PROB, LOOP
from utils.print_sese_diagram import print_sese_diagram
from solver.solver import paco



bpmn_ex = {
    "decision_based_example" : [{
        TASK_SEQ: '((T1 /[C1] T2) || (( (T3 ^[N2] T4), TU1) ^[N1] ( (T5 ^[N3] T6), TU2)))',
        IMPACTS_NAMES: ['a', 'b'],
        IMPACTS: {'T1': [3, 1], 'T2': [1, 3], 'T3': [2, 0], 'T4': [0, 2], 'TU1': [3, 1], 'T5': [2, 0], 'T6': [0, 2], 'TU2': [1, 3]},
        DURATIONS: {'T1': [0, 1], 'T2': [0, 1], 'T3': [0, 1], 'T4': [0, 1], 'TU1': [0, 1], 'T5': [0, 1], 'T6': [0, 1], 'TU2': [0, 1]},
        PROBABILITIES: {'N2': 0.2, 'N1': 0.3, 'N3': 0.4},
        LOOPS_PROB: {},
        NAMES: {'C1': 'C1', 'N2': 'N2', 'N1': 'N1', 'N3': 'N3'},
        DELAYS: {'C1': 1}, LOOP: {}, H: 0,
        }, [5, 6]
    ],
    "unavoidable_example" : [{
        TASK_SEQ: '((T1 /[C1] T2) || ((TD1, (T3 ^[N2] T4), TU1) ^[N1] (TD2,  (T5 ^[N3] T6), TU2)))',
        IMPACTS_NAMES: ['a', 'b'],
        IMPACTS: {'T1': [3, 1], 'T2': [1, 3], 'T3': [2, 0], 'T4': [0, 2], 'TU1': [3, 1], 'T5': [2, 0], 'T6': [0, 2], 'TU2': [1, 3], 'TD1': [0, 0], 'TD2': [0, 0]},
        DURATIONS: {'T1': [0, 1], 'T2': [0, 1], 'T3': [0, 1], 'T4': [0, 1], 'TU1': [0, 1], 'T5': [0, 1], 'T6': [0, 1], 'TU2': [0, 1], 'TD1': [0, 2], 'TD2': [0, 2]},
        PROBABILITIES: {'N2': 0.2, 'N1': 0.3, 'N3': 0.4},
        LOOPS_PROB: {},
        NAMES: {'C1': 'C1', 'N2': 'N2', 'N1': 'N1', 'N3': 'N3'},
        DELAYS: {'C1': 1}, LOOP: {}, H: 0,
    }, [5, 6]
    ],
    "natures of natures": [{
        TASK_SEQ: "(Task1 ^ [N1] T2) ^[N] (T3 ^ [N2] T4)",
        H: 0,
        IMPACTS: {"Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
        DURATIONS: {"Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N": 0.5, "N1": 0.6, "N2": 0.7}, NAMES: {}, DELAYS: {}, LOOPS_PROB : {}, LOOP: {}
    }, [23.3, 24.4]],

    "just task, no strategy (no choice)": [{
        TASK_SEQ: "T1, T2",
        H: 0,
        IMPACTS: {"T1": [11, 15], "T2": [4, 2]},
        DURATIONS: {"T1": [0, 100], "T2": [0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {}, NAMES: {}, DELAYS: {}, LOOPS_PROB: {}, LOOP: {}
    }, [15, 17]],

    "one choice, strategy with one obligated decision (current impacts)": [{
        TASK_SEQ: "T0, (T1 / [C1] T2)",
        H: 0,
        IMPACTS: {"T0": [11, 15], "T1": [4, 2] , "T2": [3, 3]},
        DURATIONS: {"T0": [0, 100], "T1": [0, 100], "T2":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {}, NAMES: {'C1':'C1'}, DELAYS: {"C1": 0},LOOPS_PROB : {}, LOOP: {}
    }, [14, 18]], #[15, 17]

    "only natures, no strategy (no choice)": [{
        TASK_SEQ: "SimpleTask1, (Task1 ^ [N1] T2)",
        H: 0,
        IMPACTS: {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1]},
        DURATIONS: {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6}, NAMES: {'N1':'N1'}, DELAYS: {},LOOPS_PROB : {}, LOOP: {}
    }, [14.7, 16.7]],

    "sequential choices": [{TASK_SEQ: "SimpleTask1,  (Task1 / [C1] T2),  (T3 / [C2] T4)",
                            H: 0,
                            IMPACTS: {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
                            DURATIONS: {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
                            IMPACTS_NAMES: ["cost", "hours"],
                            PROBABILITIES: {}, NAMES: {'C1':'C1', 'C2':'C2'}, DELAYS: {"C1": 0, "C2": 0},LOOPS_PROB : {}, LOOP: {}
                            }, [23, 26]], #[23, 26], [25, 22], [22, 25], [24, 21]

    "bpmn_seq_natures": [{
        TASK_SEQ: "SimpleTask1,  (Task1 ^ [N1] T2),  (T3 ^ [N2] T4)",
        H: 0,
        IMPACTS: {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
        DURATIONS: {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6, "N2": 0.7}, NAMES: {}, DELAYS: {}, LOOPS_PROB : {}, LOOP: {}
    }, [23.3, 24.4]],

    "bpmn_choices_natures": [{
        TASK_SEQ: "(Cutting, ((HP ^ [N1]LP ) || ( FD / [C1] RD)), (HPHS / [C2] LPLS))",
        H: 0,
        IMPACTS: {"Cutting": [11, 15], "HP": [4, 2], "LP": [3, 1] , "FD": [8, 9], "RD": [10, 5] , "HPHS": [4, 7], "LPLS": [3, 8]},
        DURATIONS: {"Cutting": 1, "HP": 1, "LP": 1, "FD": 1, "RD":1 , "HPHS": 1, "LPLS": 1},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6},
        NAMES: {"C1": "C1", "C2": "C2", "N1": "N1"},
        DELAYS: {"C1": 0, "C2": 0}, LOOPS_PROB : {}, LOOP: {}
    }, [26, 33.3]],

    "bpmn_prof": [{
        TASK_SEQ: "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3)",
        H: 0,
        IMPACTS: {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0]},
        DURATIONS: {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100},
        IMPACTS_NAMES: ["cost", "r", "s", "e"],
        PROBABILITIES: {"N1": 0.5, "N2": 0.5},
        LOOPS_PROB: {},
        NAMES: {"N1": "N1", "N2": "N2", "c1": "c1"},
        DELAYS: {"c1": 0}, LOOP: {}
    }, [1, 1, 1, 1]],

    "bpmn_unavoidable_tasks": [{
        TASK_SEQ: "(TaskA ^ [C1] TaskB), Task2",
        H: 0,
        IMPACTS: {"TaskA": [10], "TaskB": [10], "Task2": [10]},
        DURATIONS: {"TaskA": 100, "TaskB": 100, "Task2": 100},
        IMPACTS_NAMES: ["cost"],
        PROBABILITIES: {"C1": 0.5}, NAMES: {"C1": "C1"}, DELAYS: {"C1": 0},LOOPS_PROB : {}, LOOP: {}
    }, [20]],

    "bpmn_unavoidable_tasks2": [{
        TASK_SEQ: "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3), t4",
        H: 0,
        IMPACTS: {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0], "t4": [1, 1, 1, 1]},
        DURATIONS: {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100, "t4": 100},
        IMPACTS_NAMES: ["cost", "r", "s", "e"],
        PROBABILITIES: {"N1": 0.5, "N2": 0.5},
        LOOPS_PROB: {},
        NAMES: {"N1": "N1", "N2": "N2", "c1": "c1"},
        DELAYS: {"c1": 0}, LOOP: {}
    }, [2, 2, 2, 2]],

    "bpmn_unavoidable_tasks3": [{
        TASK_SEQ: "(HP ^ [N1]LP ), (HPHS ^ [N2] LPLS), (t1  / [c1] t3), t4, t5",
        H: 0,
        IMPACTS: {"HP": [1, 0, 0, 0], "LP": [0, 1, 0, 0], "HPHS": [0, 0, 1, 0], "LPLS": [0, 0, 0, 1], "t1": [1, 0, 0, 0], "t3": [0, 1, 0, 0], "t4": [1, 1, 1, 1], "t5": [1, 1, 1, 1]},
        DURATIONS: {"HP": 100, "LP": 100, "HPHS": 100, "LPLS": 100, "t1": 100, "t3": 100, "t4": 100, "t5": 100},
        IMPACTS_NAMES: ["cost", "r", "s", "e"],
        PROBABILITIES: {"N1": 0.5, "N2": 0.5},
        LOOPS_PROB: {},
        NAMES: {"N1": "N1", "N2": "N2", "c1": "c1"},
        DELAYS: {"c1": 0}, LOOP: {}
    }, [3, 3, 3, 3]],

    "choice not explained": [{
        TASK_SEQ: "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), (TA_C2 / [C2] TB_C2))",
        H: 0,
        IMPACTS: {"T1": [11, 15], "TA_N1": [4, 2], "TB_N1": [3, 1] , "TA_C1": [8, 9], "TB_C1": [10, 5] , "TA_C2": [4, 7], "TB_C2": [3, 8]},
        DURATIONS: {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1},
        IMPACTS_NAMES: ["cost", "hours"],
        PROBABILITIES: {"N1": 0.6}, NAMES: {"C1": "C1", "C2": "C2", "N1": "N1"},
        DELAYS: {"C1": 0, "C2": 0},LOOPS_PROB : {}, LOOP: {}
    }, [30, 30]],

    #TODO
    "complete coloring strategy tree example": [{
        TASK_SEQ: "(T1, ((TA_N1 ^[N1] TB_N1) || ( TA_C1 / [C1] TB_C1)), ((TA_C2 / [C2] TB_C2) || (TA_N2 ^[N2] TB_N2)))",
        H: 0,
        IMPACTS: {"T1": [1, 2], "TA_N1": [10, 5], "TB_N1": [5, 10] , "TA_C1": [20, 10], "TB_C1": [21, 11] , "TA_C2": [20, 10], "TB_C2": [10, 20], "TA_N2": [10, 5], "TB_N2": [5, 10]},
        DURATIONS: {"T1": 1, "TA_N1": 1, "TB_N1": 1, "TA_C1": 1, "TB_C1":1 , "TA_C2": 1, "TB_C2": 1, "TA_N2": 1, "TB_N2": 1},
        IMPACTS_NAMES: ["A", "B"],
        PROBABILITIES: {"N1": 0.6, "N2": 0.5}, NAMES: {"C1": "C1", "C2": "C2", "N1": "N1", "N2": "N2"},
        DELAYS: {"C1": 1, "C2": 0},LOOPS_PROB : {}, LOOP: {}
    }, [57, 48]],

    # TODO "multi condition BDD"
}
def test(name, bpmn, bound):
    print('Type bpmn: ', name)
    text_result, parse_tree, execution_tree, found, expected_impacts, choices, name_svg = paco(bpmn, np.array(bound, dtype=np.float64))
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
        TASK_SEQ: "(Cutting, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))), (HPHS / [C2] LPLS))",
        H: 0,
        IMPACTS: {"Cutting": [10, 1], "Bending": [20, 1], "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1], "FD": [30, 1], "RD": [10, 1], "HPHS": [40, 1], "LPLS": [20, 3]},
        DURATIONS: {"Cutting": [0, 1], "Bending": [0, 1], "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1], "FD": [0, 1], "RD": [0, 1], "HPHS": [0, 1], "LPLS": [0, 2]},
        IMPACTS_NAMES: ["electric energy", "worker hours"],
        PROBABILITIES: {"N1": 0.2}, NAMES: {"C1": "C1", "C2": "C2", "N1": "N1"}, DELAYS: {"C1": 0, "C2": 0},LOOPS_PROB : {}, LOOP: {}
        }, [135, 7]],
    #TODO loops
    "loop": [{
        TASK_SEQ: "(T1, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))))",
        H: 0,
        IMPACTS: {"T1": [10, 1], "Bending": [20, 1], "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1], "FD": [30, 1], "RD": [10, 1]},
        DURATIONS: {"T1": [0, 1], "Bending": [0, 1], "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1], "FD": [0, 1], "RD": [0, 1]},
        IMPACTS_NAMES: ["electric energy", "worker hours"],
        PROBABILITIES: {"N1": 0.2}, NAMES: {"C1": "C1", "N1": "N1"}, DELAYS: {"C1": 0},LOOPS_PROB : {}, LOOP: {}
    }, [100, 7]],
}

#test_calc_strategy_paco(bpmn_paper_example, 0)

test_calc_strategy_paco(bpmn_ex, 14)

#test_calc_strategy_paco(bpmn_ex, 0) #decision_based example
#test_calc_strategy_paco(bpmn_ex, 1) #unavoidable example
#test_calc_strategy_paco(bpmn_ex, 4) #current impacts (one obligated decision)
#test_calc_strategy_paco(bpmn_ex, 8) #current impacts


#test_calc_strategy_paco(bpmn_ex, 14)


#Testing StrategyTree:
#test_calc_strategy_paco(bpmn_ex, 0) # Not pruned ask if okay, decision_based example
#test_calc_strategy_paco(bpmn_ex, 1) # Not pruned ask if okay, unavoidable example
#test_calc_strategy_paco(bpmn_ex, 4) # Okay, current impacts (one obligated decision)
#test_calc_strategy_paco(bpmn_ex, 6) # Okay, current impacts (two obligated decision)
#test_calc_strategy_paco(bpmn_ex, 8) # Okay, current impacts
#test_calc_strategy_paco(bpmn_ex, 9) # Not pruned ask if okay, all leaves in the frontier
