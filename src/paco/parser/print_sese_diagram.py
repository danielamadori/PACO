from lark import Tree, Token
from utils.env import H, PROBABILITIES, IMPACTS, DURATIONS, DELAYS, IMPACTS_NAMES, LOOP_ROUND, \
    LOOP_PROBABILITY

def print_sese_diagram(bpmn:dict, lark_tree) -> str:
    h=bpmn[H]
    probabilities=bpmn[PROBABILITIES]
    impacts=bpmn[IMPACTS]
    durations=bpmn[DURATIONS]
    delays=bpmn[DELAYS]
    impacts_names=bpmn[IMPACTS_NAMES]
    loop_round=bpmn[LOOP_ROUND]
    loop_probability=bpmn[LOOP_PROBABILITY]

    diagram = wrap_sese_diagram(tree=lark_tree, h=h, probabilities= probabilities, impacts= impacts, durations=durations, delays=delays, impacts_names=impacts_names)

    return "digraph bpmn_cpi{ \n rankdir=LR; \n" + diagram +"}"


def dot_sese_diagram(t, id = 0, h = 0, prob={}, imp={}, loops = {}, dur = {}, imp_names = [], choices_list = {}, explainer = False):
    exit_label = ''
    if type(t) == Token:
        label = t.value
        return dot_task(id, label, h, imp[label] if label in imp else None, dur[label] if label in dur else None, imp_names), id, id, exit_label
    if type(t) == Tree:
        label = t.data
        if label == 'task':
            return dot_sese_diagram(t.children[0], id, h, prob, imp, loops, dur, imp_names)
        code = ""
        id_enter = id
        last_id = id_enter + 1
        child_ids = []
        exit_labels = []
        for i, c in enumerate(t.children):
            if (label != 'natural' or i != 1) and (label != 'choice' or i != 1) and (label != 'loop_probability' or i !=0 ):
                dot_code, enid, exid, tmp_exit_label = dot_sese_diagram(c, last_id, h, prob, imp, loops, dur, imp_names)
                exit_labels.append(tmp_exit_label)
                code += f'\n {dot_code}'
                child_ids.append((enid, exid))
                last_id = exid + 1
        if label != "sequential":    
            id_exit = last_id
            if label == "choice":
                code += dot_exclusive_gateway(id_enter, label=t.children[1])
                code += dot_exclusive_gateway(id_exit, label=t.children[1])
            elif label == 'natural':
                code += dot_probabilistic_gateway(id_enter, label=t.children[1])
                code += dot_probabilistic_gateway(id_exit, label=t.children[1])
            elif label in {'loop', 'loop_probability'}: 
                code += dot_loop_gateway(id_enter, label=t.children[0])
                if label == 'loop':
                    code += dot_loop_gateway(id_exit, label=t.children[0])
                else:
                    code += dot_loop_gateway(id_exit, label=t.children[0])
            else: 
                label_sym = '+'    
                node_label = f'[shape=diamond label="{label_sym}"]'
                code += f'\n node_{id_enter}{node_label};'
                id_exit = last_id
                code += f'\n node_{id_exit}{node_label};'
        else: 
            id_enter = child_ids[0][0]
            id_exit = child_ids[-1][1]    
        edge_labels = ['','','']
        if label == "natural":
            prob_key = t.children[1].value
            edge_labels = [f'{prob[prob_key] if prob_key  in prob else 0.5 }',
                           f'{round(1 - prob[prob_key], 2) if prob_key  in prob else 0.5 }']    
        if label == "loop_probability":
            prob_key = t.children[0].value
            proba = loops[prob_key] if prob_key in loops else 0.5
            edge_labels = ['',f'{proba}']
            exit_label = f'{1-proba}'
        if label != "sequential":
            min_id = min(child_ids)
            for ei,i in enumerate(child_ids):
                #print('ei ' , ei)
                edge_label = edge_labels[ei]
                edge_style = ''                
                if i == min_id and label == 'choice':
                    #print('min')
                    edge_style = ', style="dashed"'
                code += f'\n node_{id_enter} -> node_{i[0]} [label="{edge_label}" {edge_style}];'
                code += f'\n node_{i[1]} -> node_{id_exit};'
            if label in  {'loop', 'loop_probability'}:  
                code += f'\n node_{id_exit} -> node_{id_enter} [label="{edge_labels[1]}"];'
            # if label in {'choice'} and explainer and str(t.children[1]) in list(choices_list.keys()):
            #     code += f'\n node_{choices_list[t.children[1]][0]} -> node_{choices_list[t.children[1]][1]+2} [style="dashed"];'
        else:
            for ei,i in enumerate(child_ids):
                edge_label = edge_labels[ei]
                if ei != 0:
                    #code += f'\n node_{child_ids[ei - 1][1]} -> node_{i[0]} [label="{edge_label}"];'
                    code += f'\n node_{child_ids[ei - 1][1]} -> node_{i[0]} [label="{exit_labels[0]}"];'
                    exit_label = exit_labels[1]             
    return code, id_enter, id_exit, exit_label

def wrap_sese_diagram(tree, h = 0, probabilities={}, impacts={}, loop_thresholds = {}, durations={}, delays={}, impacts_names=[],  choices_list = {}, explainer = False):
    code, id_enter, id_exit, exit_label = dot_sese_diagram(tree, 0, h, probabilities, impacts, loop_thresholds, durations, imp_names = impacts_names, choices_list = choices_list, explainer = explainer)
    code = '\n start[label="" style="filled" shape=circle fillcolor=palegreen1]' +   '\n end[label="" style="filled" shape=doublecircle fillcolor=orangered] \n' + code
    code += f'\n start -> node_{id_enter};'
    code += f'\n node_{id_exit} -> end [label="{exit_label}"];'
    return code

def get_tasks(t):
    trees = [subtree for subtree in t.iter_subtrees()]
    v = {subtree.children[0].value for subtree in filter(lambda x: x.data == 'task', trees)}
    return v

def dot_task(id, name, h=0, imp=None, dur=None, imp_names = []):
    label = name
    #print(f"impacts in dot task : {imp}")
    if imp is not None: # modifica per aggiungere impatti e durate in modo leggibile 
        if h == 0:
            imp =  ", ".join(f"\n{key}: {value}" for key, value in zip(imp_names, imp))
            label += f", \n impacts:{imp}"
            label += f", \n duration: {str(dur)}"
        else: 
            label += str(imp[0:-h])
            label += str(imp[-h:]) 
            label += f", dur:{str(dur)}"   
    return f'\n node_{id}[label="{label}", shape=rectangle style="rounded,filled" fillcolor="lightblue"];'

def dot_exclusive_gateway(id, label="X"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=orange];'

def dot_probabilistic_gateway(id, label="N"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=yellowgreen];' 

def dot_loop_gateway(id, label="N"):
    return f'\n node_{id}[shape=diamond label={label} style="filled" fillcolor=yellowgreen];' 

def dot_parallel_gateway(id, label="+"):
    return f'\n node_{id}[shape=diamond label={label}];'

def dot_rectangle_node(id, label):
    return f'\n node_{id}[shape=rectangle label={label}];'  