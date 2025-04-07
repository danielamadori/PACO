from lark import Lark

URL_SERVER = 'http://127.0.0.1:8000/' #'http://host.docker.internal:8000/'

###############
# MODEL
###############
MODEL = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF/Llama-3.1-Nemotron-70B-Instruct-HF-Q4_K_M.gguf"
MODEL_1 = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF"
MODEL_2 = "lmstudio-community/Llama-3.1-Nemotron-70B-Instruct-HF-GGUF/Llama-3.1-Nemotron-70B-Instruct-HF-Q4_K_M.gguf:2"


###############
# GRAMMAR
###############
sese_diagram_grammar = r"""
?start: xor

?xor: parallel
    | xor "/" "[" NAME "]" parallel -> choice
    | xor "^" "[" NAME "]" parallel -> natural

?parallel: sequential
    | parallel "||" sequential  -> parallel

?sequential: region
    | sequential "," region -> sequential    

?region: 
    | NAME   -> task
    | "<" xor ">" -> loop
    | "<" "[" NAME "]"  xor ">" -> loop_probability
    | "(" xor ")"

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE

%ignore WS_INLINE
"""
SESE_PARSER = Lark(sese_diagram_grammar, parser='lalr')

### args for tree LARK
EXPRESSION = 'expression'
IMPACTS = 'impacts'
NAMES = 'names'
PROBABILITIES = 'probabilities'
LOOP_THRESHOLD = 'loop_threshold'
DURATIONS = 'durations'
DELAYS = 'delays'
H = 'h'
IMPACTS_NAMES ='impacts_names'
LOOP_ROUND = 'loop_round'
### SYNTAX
LOOP_PROBABILITY = 'loop_probability'
LOOP_ROUND = 'loop_round'
# BPMN RESOLUTION #######################
RESOLUTION = 300
#############################
# STRATEGY 
STRATEGY = 'strategy'
BOUND = 'bound'



#############################
# PATHS
#############################

PATH_ASSETS = 'assets/'
BPMN_FOLDER = 'bpmnSvg/'
PATH_IMAGE_BPMN_FOLDER = PATH_ASSETS + BPMN_FOLDER
PATH_BPMN = PATH_ASSETS + 'bpmn'

PATH_BPMN = PATH_ASSETS + 'bpmn'
PATH_PARSE_TREE = PATH_ASSETS + 'parse_tree'

PATH_EXECUTION_TREE = PATH_ASSETS + 'execution_tree/'
PATH_EXECUTION_TREE_STATE = PATH_EXECUTION_TREE + 'state'
PATH_EXECUTION_TREE_STATE_TIME = PATH_EXECUTION_TREE + 'state_time'
PATH_EXECUTION_TREE_STATE_TIME_EXTENDED = PATH_EXECUTION_TREE + 'state_time_extended'

PATH_EXECUTION_TREE_TIME = PATH_EXECUTION_TREE + 'time'

PATH_EXPLAINER = PATH_ASSETS + 'explainer/'
PATH_EXPLAINER_DECISION_TREE = PATH_EXPLAINER + 'decision_tree'
PATH_EXPLAINER_BDD = PATH_EXPLAINER + 'bdd'
PATH_STRATEGIES = PATH_ASSETS + 'strategies'

PATH_STRATEGY_TREE = PATH_ASSETS + 'strategy_tree/'
PATH_STRATEGY_TREE_STATE = PATH_STRATEGY_TREE + 'state'
PATH_STRATEGY_TREE_STATE_TIME = PATH_STRATEGY_TREE + 'state_time'
PATH_STRATEGY_TREE_STATE_TIME_EXTENDED = PATH_STRATEGY_TREE + 'state_time_extended'
PATH_STRATEGY_TREE_TIME = PATH_STRATEGY_TREE + 'time'

#############################
# ALGORITHMS
#############################
ALGORITHMS = {  # strategies with labels
    's1': 'PACO',
    's2': 'Strategy 2',
    's3': 'Strategy 3'
}

ALGORITHMS_MISSING_SYNTAX = {
    's1': [],
    's2': [],
    's3': []
}

ALL_SYNTAX = ['^', '/', '||', '<', '>', '[', ']', ',', '', '(', ')'] # all syntax characters available