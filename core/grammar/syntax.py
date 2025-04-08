import re
import json

from lark import ParseTree

from core.config import ALGORITHMS, ALGORITHMS_MISSING_SYNTAX, DURATIONS, IMPACTS, EXPRESSION, ALL_SYNTAX, SESE_PARSER


def check_algo_is_usable(expression: str, algo: str) -> bool:
    """
    Check if the costructs in the BPMN is suitable fro the algo.
    """
    print('checking expression within algo in progress...')
    if expression == '' or algo == '' or algo not in ALGORITHMS.keys():
        return False
    if algo in ALGORITHMS_MISSING_SYNTAX.keys() and list(ALGORITHMS_MISSING_SYNTAX.get(algo)) != []:
        for element in list(ALGORITHMS_MISSING_SYNTAX.get(algo)):
            #print(element)
            if element in expression:
                return False        
    return True



def extract_nodes(lark_tree: ParseTree) -> (list, list, list, list):
    tasks = []
    choices = []
    natures = []
    loops = []

    if lark_tree.data == 'task':
        return [lark_tree.children[0].value], [], [], []

    if lark_tree.data in {'choice', 'natural'}:
        if lark_tree.data == 'choice':
            choices.append(lark_tree.children[1].value)
        else:
            natures.append(lark_tree.children[1].value)

        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[2])

    elif lark_tree.data in {'sequential', 'parallel'}:
        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[1])
    elif lark_tree.data == 'loop':#TODO
        left_task, left_choices, left_natures, left_loops = extract_nodes(lark_tree.children[0])
        right_task, right_choices, right_natures, right_loops = [], [], [], []
    elif lark_tree.data == 'loop_probability':
        loops.append(lark_tree.children[0].value)
        left_task, left_choices, left_natures, left_loops = [], [], [], []
        right_task, right_choices, right_natures, right_loops = extract_nodes(lark_tree.children[1])

    tasks.extend(left_task)
    choices.extend(left_choices)
    natures.extend(left_natures)
    loops.extend(left_loops)
    tasks.extend(right_task)
    choices.extend(right_choices)
    natures.extend(right_natures)
    loops.extend(right_loops)

    return tasks, choices, natures, loops


def impacts_from_dict_to_list(dictionary:dict):
    """
    Convert the values of a dictionary to a list and check if all values are integers.

    Parameters:
    dictionary (dict): The dictionary to process.

    Returns:
    list: A list of the dictionary's values if all values are integers, otherwise an empty list.
    """
    # Convert the dictionary values to a list
    values = list(dictionary.values())
    # Print the list of values
    #print(values)
    # Check if all values are integers
    if all(isinstance(v, int) for v in values):
        # If all values are integers, return the list
        return values
    # If not all values are integers, return an empty list
    return []



#######################

def impacts_dict_to_list(impacts: dict):
    return {key: list(inner_dict.values()) for key, inner_dict in impacts.items()}

def divide_dict(dictionary, keys):
    # Initialize an empty dictionary for the loop
    loop = {}

    # Iterate over the keys
    for key in keys:
        # If the key is in the dictionary, remove it and add it to the loop dictionary
        if key in dictionary:
            loop[key] = dictionary.pop(key)

    # Return the modified original dictionary and the loop dictionary
    return dictionary, loop