from lark import Lark, Tree, Token
import numpy as np
import random

# Grammar definition for process expressions
# Defines the syntax for processes with XOR (^), parallel (||), and sequential (,) operations
# Each basic process is represented by a NAME token
PROCESS_GRAMMAR = r"""
?start: xor

?xor: parallel
    | xor "^" parallel -> xor

?parallel: sequential
    | parallel "||" sequential  -> parallel

?sequential: region
    | sequential "," region -> sequential

?region: 
     | NAME   -> task
     | "(" xor ")"

%import common.CNAME -> NAME
%import common.NUMBER
%import common.WS_INLINE

%ignore WS_INLINE
"""

# Initialize the Lark parser with LALR parsing strategy
PARSER = Lark(PROCESS_GRAMMAR, parser='lalr')

def max_nested_xor(expression):
    """
    Calculate the maximum depth of nested XOR operations in a process expression.
    
    Args:
        expression (str): Process expression string
    
    Returns:
        int: Maximum depth of nested XOR operations
    """
    tree = PARSER.parse(expression)
    
    def _max_nested_xor(node):
        # Base case: tokens or task nodes have depth 0
        if isinstance(node, Token) or (isinstance(node, Tree) and node.data == 'task'):
            return 0
        
        if isinstance(node, Tree):
            if node.data == 'xor':
                # For XOR nodes, take max of children depths and add 1
                return max(_max_nested_xor(child) for child in node.children) + 1
            elif node.data in ['sequential', 'parallel']:
                # For sequential and parallel nodes, take max of children depths
                return max(_max_nested_xor(child) for child in node.children)
        
        return 0
    
    return _max_nested_xor(tree)

def max_independent_xor(expression):
    """
    Calculate the maximum number of independent XOR operations in a process expression.
    Independent XORs are those that can be executed concurrently.
    
    Args:
        expression (str): Process expression string
    
    Returns:
        int: Maximum number of independent XOR operations
    """
    tree = PARSER.parse(expression)
    
    def _max_independent_xor(node):
        # Base case: tokens or task nodes have 0 independent XORs
        if isinstance(node, Token) or (isinstance(node, Tree) and node.data == 'task'):
            return 0
        
        if isinstance(node, Tree):
            if node.data == 'xor':
                # For XOR nodes, take max of children counts and ensure at least 1
                max_child = max(_max_independent_xor(child) for child in node.children)
                return max(1, max_child)
            elif node.data in ['sequential', 'parallel']:
                # For sequential and parallel nodes, sum the children counts
                return sum(_max_independent_xor(child) for child in node.children)
        
        return 0
    
    return _max_independent_xor(tree)

def get_process_from_file(x, y, z):
    """
    Retrieve a specific process expression from a generated file.
    
    Args:
        x, y: Parameters determining the file name
        z: Line number to retrieve
    
    Returns:
        str: Process expression from the specified line
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If the specified line number doesn't exist
    """
    filename = f'generated_processes/generated_processes_full_{x}_{y}.txt'
    try:
        with open(filename, 'r') as file:
            for i, line in enumerate(file, 1):
                if i == z:
                    return line.strip()
        raise ValueError(f"Line {z} not found in the file. The file has fewer lines.")
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {filename} does not exist.")

def generate_vectors(num_vec, dim, mode="random"):
    """
    Generate impact vectors for tasks using different strategies.
    
    Args:
        num_vec (int): Number of vectors to generate
        dim (int): Dimension of each vector
        mode (str): Generation strategy ("random", "bagging_divide", "bagging_remove", etc.)
    
    Returns:
        list: List of numpy arrays representing impact vectors
    """
    vectors = []
    for _ in range(num_vec):
        vector = np.random.random(dim)
        if mode != "random":
            # Generate random indices for vector modification
            indexes = [random.randint(0, dim-1) for _ in range(dim)]
            
            # Apply different vector modification strategies based on mode
            if mode == "bagging_divide":
                # Divide selected elements by 10
                for i in indexes:
                    vector[i] /= 10
            elif mode == "bagging_remove":
                # Keep only selected elements
                new_vector = np.zeros(dim)
                for i in indexes:
                    new_vector[i] = vector[i]
                vector = new_vector
            elif mode == "bagging_remove_divide":
                # Keep and divide selected elements
                new_vector = np.zeros(dim)
                for i in indexes:
                    new_vector[i] = vector[i] / 10
                vector = new_vector
            elif mode == "bagging_remove_reverse":
                # Zero out selected elements
                new_vector = vector.copy()
                for i in indexes:
                    new_vector[i] = 0
                vector = new_vector
            elif mode == "bagging_remove_reverse_divide":
                # Zero out selected elements and divide some non-zero elements
                new_vector = vector.copy()
                for i in indexes:
                    new_vector[i] = 0
                non_zero_indexes = np.nonzero(new_vector)[0]
                if len(non_zero_indexes) > 0:
                    divide_indexes = [random.choice(non_zero_indexes) for _ in range(dim)]
                    for i in divide_indexes:
                        new_vector[i] /= 10
                vector = new_vector
        vectors.append(vector)
    return vectors

def translate_to_cpi(process_str, choice_distribution, duration_interval, num_impacts, vector_generation_mode="random"):
    """
    Translates a process string into a CPI (Configurable Process Instance) dictionary.
    
    Args:
        process_str (str): Process string following the grammar in PROCESS_GRAMMAR
        choice_distribution (float): Probability of XOR node becoming a choice (vs nature)
        duration_interval (tuple): (min, max) duration for tasks
        num_impacts (int): Number of impact keys per task
        vector_generation_mode (str): Mode for generating impact vectors
        
    Returns:
        dict: CPI process dictionary with nested structure
    """
    parser = Lark(PROCESS_GRAMMAR, parser='lalr')
    tree = parser.parse(process_str)
    
    # Single global counter for unique IDs
    id_counter = 0
    
    def count_tasks(node):
        """Count total number of tasks in the process tree"""
        if isinstance(node, Token) or (isinstance(node, Tree) and node.data == 'task'):
            return 1
        return sum(count_tasks(child) for child in node.children)
    
    total_tasks = count_tasks(tree)
    
    # Generate impact vectors for all tasks
    impact_vectors = generate_vectors(total_tasks, num_impacts, mode=vector_generation_mode)
    task_counter = 0  # Counter to assign impact vectors to tasks
    
    def process_node(node):
        """
        Recursively process nodes in the parse tree to build CPI dictionary
        """
        nonlocal id_counter, task_counter
        
        if isinstance(node, Token):
            # Create task node with random duration and impacts
            current_id = id_counter
            id_counter += 1
            
            impact_vector = impact_vectors[task_counter]
            task_counter += 1
            impacts = {f"impact_{i+1}": float(val) for i, val in enumerate(impact_vector)}
            
            return {
                "type": "task",
                "id": current_id,
                "duration": random.randint(duration_interval[0], duration_interval[1]),
                "impacts": impacts
            }
            
        if isinstance(node, Tree):
            if node.data == 'task':
                return process_node(node.children[0])
                
            elif node.data == 'sequential':
                # Create sequence node with head and tail
                current_id = id_counter
                id_counter += 1
                return {
                    "type": "sequence",
                    "id": current_id,
                    "head": process_node(node.children[0]),
                    "tail": process_node(node.children[1])
                }
                
            elif node.data == 'parallel':
                # Create parallel node with first and second splits
                current_id = id_counter
                id_counter += 1
                return {
                    "type": "parallel",
                    "id": current_id,
                    "first_split": process_node(node.children[0]),
                    "second_split": process_node(node.children[1])
                }
                
            elif node.data == 'xor':
                # Create either choice or nature node based on probability
                is_choice = random.random() < choice_distribution
                node_type = 'choice' if is_choice else 'nature'
                
                current_id = id_counter
                id_counter += 1
                
                result = {
                    "type": node_type,
                    "id": current_id,
                    "true": process_node(node.children[0]),
                    "false": process_node(node.children[1])
                }
                
                # Add probability for nature nodes
                if not is_choice:
                    result["probability"] = random.random()
                    
                return result
    
    return process_node(tree)