from datetime import datetime
import os
from utils.env import *
from utils.print_sese_diagram import print_sese_diagram
from utils.automa import calc_strategy_paco


bpmn_ex = {
    "natures of natures": [{"expression": "(Task1 ^ [N1] T2) ^[N] (T3 ^ [N2] T4)",
                          "h": 0,
                          "impacts": {"Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]},
                          "durations": {"Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
                          "impacts_names": ["cost", "hours"],
                          "probabilities": {"N": 0.5, "N1": 0.6, "N2": 0.7}, "names": {}, "delays": {}, 'loops_prob' : {}, 'loops_round': {}
                          }, [23.3, 24.4]],

    "just task, no strategy (no choice)": [{"expression": "T1, T2",
          "h": 0, 
          "impacts": {"T1": [11, 15], "T2": [4, 2]},
          "durations": {"T1": [0, 100], "T2": [0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {}, "delays": {}, 'loops_prob': {}, 'loops_round': {}
        }, [15, 17]],

    "one choice, strategy with one decision (always True)": [{"expression": "SimpleTask1, (Task1 / [C1] T2)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2] , "T2": [3, 3]},
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100]}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {'C1':'C1'}, "delays": {"C1": 0},'loops_prob' : {}, 'loops_round': {}
        }, [14, 18]], #[15, 17]
    
    "only natures, no strategy (no choice)": [{"expression": "SimpleTask1, (Task1 ^ [N1] T2)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100]}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {'N1':'N1'}, "delays": {},'loops_prob' : {}, 'loops_round': {}
        }, [14.7, 16.7]],
    
    "sequential choices": [{"expression": "SimpleTask1,  (Task1 / [C1] T2),  (T3 / [C2] T4)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {}, "names": {'C1':'C1', 'C2':'C2'}, "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loops_round': {}
        }, [23, 26]], #[23, 26], [25, 22], [22, 25], [24, 21]

    "bpmn_seq_natures": [{"expression": "SimpleTask1,  (Task1 ^ [N1] T2),  (T3 ^ [N2] T4)",
          "h": 0, 
          "impacts": {"SimpleTask1": [11, 15], "Task1": [4, 2], "T2": [3, 1] , "T3": [8, 9], "T4": [10, 5]}, 
          "durations": {"SimpleTask1": [0, 100], "Task1": [0, 100], "T2":[0, 100], "T3":[0, 100], "T4":[0, 100]},
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6, "N2": 0.7}, "names": {}, "delays": {}, 'loops_prob' : {}, 'loops_round': {}
        }, [23.3, 24.4]],

    "bpmn_choices_natures": [{"expression": "(Cutting, ((HP ^ [N1]LP ) || ( FD / [C1] RD)), (HPHS / [C2] LPLS))",
          "h": 0, 
          "impacts": {"Cutting": [11, 15], "HP": [4, 2], "LP": [3, 1] , "FD": [8, 9], "RD": [10, 5] , "HPHS": [4, 7], "LPLS": [3, 8]}, 
          "durations": {"Cutting": 1, "HP": 1, "LP": 1, "FD": 1, "RD":1 , "HPHS": 1, "LPLS": 1}, 
          "impacts_names": ["cost", "hours"], 
          "probabilities": {"N1": 0.6}, "names": {"C1": "C1", "C2": "C2", "N1": "N1"}, "delays": {"C1": 0, "C2": 0},'loops_prob' : {}, 'loops_round': {}
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
        "probabilities": {"C1": 0.5}, "names": {"C1": "C1"}, "delays": {"C1": 0},'loops_prob' : {}, 'loops_round': {}
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
}


def test(name, bpmn):
    print(f' type bpmn: {name}, strategy {bpmn}')

    # per disegnare

    bpmn_svg_folder = "assets/bpmnTest/"
    if not os.path.exists(bpmn_svg_folder):
        os.makedirs(bpmn_svg_folder)
    # Create a new SESE Diagram from the input
    name_svg =  bpmn_svg_folder + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".png"
    print(name_svg)
    print_sese_diagram(**bpmn, outfile=name_svg)

    # strategies = calc_strategy_paco(bpmn[0], bpmn[1])
    # print(f'Type bpmn: {name}, strategy {strategies}')


def test_calc_strategy_paco(bpmn_ex_dicts:dict, selected:int = -1):
    if selected == -1:
        for name, bpmn in bpmn_ex_dicts.items():
            test(name, bpmn)
            #ask a string in input if the string is not yes exit
            answer = input("Do you want to continue? (yes/no): ")
            if answer != "yes" and answer != "y":
                break
    else:
        problem = list(bpmn_ex_dicts.items())[selected]
        test(problem[0], problem[1])


#test_calc_strategy_paco(bpmn_ex)
#test_calc_strategy_paco(bpmn_ex, 1)
import random

# Define tasks and choices from the expression
tasks = ["T" + str(i) for i in range(1, 39)]
choices = ["C" + str(i) for i in range(1, 9)]
natures = ["N" + str(i) for i in range(1, 8)]

# Generate impacts
impacts = {task: [random.randint(1, 50), random.randint(1, 20)] for task in tasks}

# Generate durations
durations = {task: random.randint(1, 100) for task in tasks}

# Generate probabilities
probabilities = {nature: round(random.uniform(0.1, 0.9), 2) for nature in natures}

# Generate names
names = {choice: choice for choice in choices}
names.update({nature: nature for nature in natures})

# Generate delays
delays = {choice: 0 for choice in choices}

# Print the generated components
# print("Impacts:", impacts)
# print("Durations:", durations)
# print("Probabilities:", probabilities)
# print("Names:", names)
# print("Delays:", delays)

bpmn_ex_article = {
    "expression": "(((((((T1 , T2) ^ [C1] ((T3 , T4) || T5)) , ((T6 , T7) / [N1] T8)) , ((T9 ^ [C2] T10) , (T11 , ((T12 , T13) , T14)))) , (((T15 ^ [C3] T16) / [N3] T17) / [N2] (T18 , T19))) ^ [C4] ((((T20 , T21) , T22) || T23) , ((T24 , T25) ^ [C5] T26))) || ((T27 || ((T28 / [N4] T29) ^ [N5] (T30 ^ [C6] (((T31 , T32) , ((T33 / [N7] T34) ^ [C7] T35)) , (T36 , T37))))) || T38))",
    #"(((((T1 || T2), T3), (T4 || (T5, (T6 || T7)))) ^ [N1] T8) || (((((T9 / [C1] T10), ((T11 || T12) || T13)) ^ [N2] T14), (T15 / [C2] ((T16 / [C3] (T17 || T18)) / [C4] (T19, T20),((((T21, T22) / [C5] T23), (((T24 || T25) / [C6] ((T26 / [C7] (T27, T28)), T29)), T30),      (T31 || (T32 || T33))) )))) / [C8] (T34 / [C9] T35)), ((((T36 || (T37, T38)) || ((( T39 ^ [N4] ((T40, T41), ((T42 || (T43 || ((T44, T45), T46))) / [C11] (T47 || (((T48, (T49 || T50)) / [C12] T51) / [C13] ((T52 || (T53 / [C14] T54)), (T55 / [C15] (T56 / [C16] T57)))))))),  (T58 / [C17] ((T59 / [C18] (T60 || T61)), (T62 || T63))))) || ((T64 / [C19] (T65 || T66)) / [C20] ((T67, (((T68 || T69), T70), T71)), (T72, T73))))    ) / [C21] (((T74, (((T75, (T76 || (T77, T78)))), T79) ^ [N3] T80) / [C23] (T81, T82)) || ((((T83 || T84) / [C24] T85), (T86 || (T87, T88))), (((T89, (T90, T91)) || T92) || T93))))) / [C25] (((((T94 || T95), T96) / [C26] (T97 || T98)), ((((T99, T100) || ((T101 ^ [N5] T102), T103)), T104) / [C28] ((T105 || ((T106 / [C29] (T107, (T108 || T109))), T110)) || (((T111, T112), (T113, ((T114, T115) / [C30] T116))) / [C31] (T117, T118)))))    ) || ((((((T119 / [C32] T120) || T121) || T122) || (((T123 || T124) / [C33] T125) ^ [N6] T126)) / [C35] T127) / [C36] ((T128 / [C37] (T129, T130)) / [C38] (((T131, T132) || T133) || T134))))) / [C39] (((T135, ((T136 || (T137 / [C40] ((T138 || T139) / [C41] T140))), ((T141 / [C42] (T142, T143)), T144))), (T145, ((((T146 / [C43] T147) || T148) || (T149, (T150 || T151))) || ((T152, (T153, T154)) || T155))))) / [C44] (((((((((T156 || T157) || T158) / [C45] T159), (T160 || T161)) / [C46] ((((T162 || T163), ((T164, T165) / [C47] T166)) || ((T167 || (T168, T169)) || T170)), (((T171 || T172), (T173, T174)), (T175, T176)))) || ((((T177 / [C48] T178) / [C49] ((T179, ((T180 || T181) / [C50] T182)) / [C51] (T183, T184))) / [C52] T185) || (((T186 || T187) / [C53] T188) || T189))) / [C54] (T190 || ((T191 || (T192, T193)), T194))) / [C55] (T195 / [C56] ((T196, (T197 / [C57] T198)) / [C58] T199))) ) / [C59] ((((T200 / [C60] ((T201, T202), T203)), ((((((T204 || T205) || T206) / [C61] (T207 / [C62] T208)) / [C34] (T209, (((T210 || T211) / [C27] T212), T213))) || (T214, T215)) || (T216, (T217 / [C10] (T218 || T219))))) || ((T220 || T221), ((T222, (T223 / [C22] T224)), T225))) || T226)))))",
    "h": 0,
    "impacts": impacts,
    "durations": durations,
    "impacts_names": ["cost", "energy"],
    "loops_prob": {},
    "delays": delays,
    "probabilities": probabilities,
    "names": names,
    "loop_round": {}
}
try:
    SESE_PARSER.parse(bpmn_ex_article["expression"])
    error = False
except Exception as e:
    print(f'Error: {e}')
    error = True
if not error:
    try: 
        bpmn_svg_folder = "assets/bpmnTest/"
        if not os.path.exists(bpmn_svg_folder):
            os.makedirs(bpmn_svg_folder)
        # Create a new SESE Diagram from the input
        # name_svg =  bpmn_svg_folder + "bpmn_"+ str(datetime.timestamp(datetime.now())) +".png"
        # print(name_svg)
        # print_sese_diagram(**bpmn_ex_article, outfile=name_svg)
        strategies = calc_strategy_paco(bpmn_ex_article, [280, 130])
        print(f'Type bpmn strategy {strategies}')
    except Exception as e:
        print(f'Error: {e}')