from datetime import datetime
import os
from agent import define_agent
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
import json
from pydantic import BaseModel
from typing import List, Dict, Optional
import numpy as np
from paco.explainer.build_explained_strategy import build_explained_strategy
from paco.parser.create import create
from paco.searcher.search import search
from paco.parser.bpmn_parser import SESE_PARSER
from paco.parser.print_sese_diagram import print_sese_diagram
from paco.explainer.explanation_type import ExplanationType
from paco.parser.parse_tree import ParseTree
from utils.env import ALGORITHMS, DELAYS, DURATIONS, IMPACTS, IMPACTS_NAMES, LOOP_PROB, NAMES, PATH_EXECUTION_TREE_STATE, PATH_EXECUTION_TREE_STATE_TIME, PATH_EXECUTION_TREE_STATE_TIME_EXTENDED, PATH_EXECUTION_TREE_TIME, PATH_EXPLAINER_BDD, PATH_EXPLAINER_DECISION_TREE, PATH_PARSE_TREE, PATH_STRATEGY_TREE_STATE, PATH_STRATEGY_TREE_STATE_TIME, PATH_STRATEGY_TREE_STATE_TIME_EXTENDED, PATH_STRATEGY_TREE_TIME, PROBABILITIES
from paco.solver import paco
from utils.check_syntax import check_algo_is_usable, checkCorrectSyntax, check_input
from fastapi.middleware.cors import CORSMiddleware
from utils import check_syntax as cs
import uvicorn
# https://blog.futuresmart.ai/integrating-google-authentication-with-fastapi-a-step-by-step-guide
# http://youtube.com/watch?v=B5AMPx9Z1OQ&list=PLqAmigZvYxIL9dnYeZEhMoHcoP4zop8-p&index=26
# https://www.youtube.com/watch?v=bcYmfHOrOPM
# TO EMBED DASH IN FASAPI
# https://medium.com/@gerardsho/embedding-dash-dashboards-in-fastapi-framework-in-less-than-3-mins-b1bec12eb3
# swaggerui al link  http://127.0.0.1:8000/docs
# server al link http://127.0.0.1:8000/

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"] 
)

class LoginRequest(BaseModel):
    username: str
    password: str
class BPMNDefinition(BaseModel):
    """
    Pydantic model for BPMN process definition
    
    Attributes:
        expression (str): BPMN process expression
        h (int, optional): Horizon value, defaults to 0
        probabilities (Dict, optional): Nature probabilities mapping
        impacts (Dict): Impact values for tasks
        loop_thresholds (Dict, optional): Thresholds for loops
        durations (Dict, optional): Task durations
        names (Dict, optional): Custom names mapping
        delays (Dict, optional): Delay values for choices
        impacts_names (List, optional): Names of impact metrics
        loop_round (Dict, optional): Loop round configurations
        loops_prob (Dict, optional): Loop probabilities
    """
    expression: str = "(Cutting, ((Bending, (HP^[N1]LP)) || (Milling, (FD/[C1]RD))), (HPHS / [C2] LPLS))" 
    h: Optional[int] = 0
    probabilities: Optional[Dict] = {"N1": 0.2}
    impacts: Dict = {"Cutting": [10, 1], "Bending": [20, 1],
        "Milling": [50, 1], "HP": [5, 4], "LP": [8, 1],
        "FD": [30, 1], "RD": [10, 1], "HPHS": [40, 1],
        "LPLS": [20, 3]
    }
    loop_thresholds: Optional[Dict] = {}    
    durations: Optional[Dict] = {"Cutting": [0, 1], "Bending": [0, 1],
        "Milling": [0, 1], "HP": [0, 2], "LP": [0, 1],
        "FD": [0, 1], "RD": [0, 1], "HPHS": [0, 1],
        "LPLS": [0, 2]}
    names: Optional[Dict] = {"C1": "C1", "C2": "C2", "N1": "N1"}
    delays: Optional[Dict] = {"C1": 0, "C2": 0}
    impacts_names: Optional[List] = ["electric_energy", "worker hours"]   
    loop_round: Optional[Dict] = {}
    loop_probability: Optional[Dict] = {}

class BPMNPrinting(BaseModel):
    """
    Model for BPMN diagram printing options
    
    Attributes:
        bpmn (BPMNDefinition): BPMN process definition
        graph_options (Dict, optional): Graph rendering options
    """    
    bpmn: BPMNDefinition
    graph_options: Optional[Dict] = {}

class StrategyFounderAlgo(BaseModel):
    """
    Model for strategy finding request
    
    Attributes:
        bpmn (BPMNDefinition): BPMN process definition
        bound (list[float]): Impact bounds vector
        algo (str): Algorithm selected
    """
    bpmn: BPMNDefinition
    bound: list[float] = [20., 100.]
    algo: str = "paco"
class AgentRequest(BaseModel):
    prompt: str
    session_id: str  # Unique ID to track chat history
    url: str = 'http://157.27.193.108'
    api_key: str = 'lm-studio'
    model: str = 'gpt-3.5-turbo'
    temperature: float = 0.7
    verbose: bool = False

chat_histories = {}
#######################################################
############ GET  #####################################
#######################################################
@app.get("/")
async def get():
    """
    Root endpoint that returns a welcome message
    Returns:
        str: Welcome message
    """
    return f"welcome to PACO server"

@app.get("/check_correct_process_expression")
async def check_correct_process_expression(expression: str) -> bool:
    """
    Checks if the given BPMN process expression is correct according to the SESE diagram grammar.

    Args:
        expression (str): The BPMN process expression to be checked.

    Returns:
        bool: True if the expression is correct and can be parsed by SESE_PARSER, False otherwise.

    Raises:
        Exception: If the expression cannot be parsed, an exception is caught and False is returned.
        403: If the token is not provided, an exception not authorized.
    """
    try:
        SESE_PARSER.parse(expression)
        return True
    except Exception as e:
        return False



@app.get("/check_input")
async def check_input_bpmn(bpmn: BPMNDefinition, bound: list[float]) -> tuple[str, List[int]]:
    """
    Checks the input of the given BPMN process and bound.

    Args:
        bpmn (BPMNDefinition): The BPMN process to be checked.
        bound (list[float]): The bound to be checked.

    Returns:
        str: An error message if the input is not valid, an empty string otherwise.

    Raises:
        400: If the input is not valid, an exception is raised.
        403: If the token is not provided, an exception not authorized.
    """
    if not isinstance(bpmn, BPMNDefinition) or not isinstance(bound, list):
        return HTTPException(status_code=400, detail="Invalid input")
    try:

        check_input(dict(bpmn), bound)
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/check_algo_usable")
async def check_algo_usable(sfa :StrategyFounderAlgo) -> bool:
    """
    Checks if the given algorithm is usable for the given BPMN process.

    Args:
        bpmn (BPMNDefinition): The BPMN process to be checked.
        algo (str): The algorithm to be checked.

    Returns:
        bool: True if the algorithm is usable, False otherwise.

    Raises:
        400: If the algorithm is not valid, an exception is raised.
        403: If the token is not provided, an exception not authorized.
    """
    if not isinstance(sfa.bpmn, BPMNDefinition) or not isinstance(sfa.algo, str):
        return HTTPException(status_code=400, detail="Invalid input")
    if not check_algo_is_usable(sfa.bpmn.expression, sfa.algo):
        return False
    return True

@app.get("/check_syntax")
async def check_syntax(bpmn: BPMNDefinition) -> bool:
    """
    Checks the syntax of the given BPMN process.

    Args:
        bpmn (BPMNDefinition): The BPMN process to be checked.

    Returns:
        bool: True if the syntax is correct, False otherwise.

    Raises:
        400: If the input is not valid, an exception is raised.
        403: If the token is not provided, an exception not authorized.
    """
    if not isinstance(bpmn, BPMNDefinition):
        return HTTPException(status_code=400, detail="Invalid input")
    return checkCorrectSyntax(dict(bpmn))

@app.get("/get_algorithms") 
async def get_algorithms(token:str = None) -> dict:
    """
    Returns the list of available algorithms.

    Returns:
        dict: Dictionary of available algorithms with their descriptions

    Raises:
        403: If the token is not provided, an exception not authorized.
    """
    if token == None:
        return HTTPException(status_code=403, detail="Not authorized")
    try:
        return ALGORITHMS
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get("/calc_strategy_general")
async def calc_strategy_and_explainer(request: StrategyFounderAlgo, ) -> dict:
    """
    Calculates strategy using PACO algorithm
    Args:
        request (StrategyFounderAlgo): Strategy calculation parameters
    Returns:
        dict: Calculation results
    Raises:
        HTTPException: 400 for invalid input, 500 for server errors
    """
    if not isinstance(request.bpmn, BPMNDefinition):
        return HTTPException(status_code=400, detail="Invalid input")
    bpmn = dict(request.bpmn)
    if not checkCorrectSyntax(bpmn):
        return HTTPException(status_code=400, detail="Invalid BPMN syntax")
    if not check_algo_is_usable(bpmn, request.algo):
        return HTTPException(status_code=400, detail="The algorithm is not usable")       
    try:
        bound = np.array(request.bound, dtype=np.float64)            
        if request.algo == list(ALGORITHMS.keys())[0]:
            text_result, parse_tree, pending_choices, pending_natures, execution_tree, expected_impacts, possible_min_solution, solutions, choices, times = paco(bpmn, bound)
            #TODO JSON
            parse_tree_json = parse_tree.to_json()
            execution_tree_json = execution_tree.to_json()
            print(f"{datetime.now()} parse_tree_json: ", parse_tree_json)
            print(f"{datetime.now()} execution_tree_json: ", execution_tree_json)

            result = {
                "result": text_result,
                "expected_impacts": str(expected_impacts) if expected_impacts is not None else None,
                "possible_min_solution": str(possible_min_solution),
                "solutions": str(solutions),
                "choices": str(choices),
            }
            result.update(times)
            return result
        # elif request.algo == list(ALGORITHMS.keys())[1]:
        #     text_result, found, choices = None, None, None, None
        # elif request.algo == list(ALGORITHMS.keys())[2]:
        #     text_result, found, choices = None, None, None, None
        else:
            return HTTPException(status_code=400, detail="Invalid algorithm")
                
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/create_execution_tree")
async def get_excecution_tree(bpmn:BPMNDefinition = None) -> dict:
    """
    Get the execution tree.

    Args:
        
        bpmn (BPMNDefinition): The BPMN process.

    Returns:
        The parse tree & execution tree.

    Raises:
        400: If the input is not valid, an exception is raised.
        500: If an error occurs, an exception is raised.
    """
    if not isinstance(bpmn, BPMNDefinition) or bpmn == None:
        return HTTPException(status_code=400, detail="Invalid input")
    try:
        bpmn = dict(bpmn) 
        bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])       
        parse_tree, execution_tree , time_create_parse_tree, time_create_execution_tree, time_evaluate_cei_execution_tree = create(bpmn)
        
        return {
            "execution_tree": str(execution_tree),
            "time_create_parse_tree": time_create_parse_tree,
            "time_create_execution_tree": time_create_execution_tree,
            "time_evaluate_cei_execution_tree": time_evaluate_cei_execution_tree
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_parse_tree")
async def get_parse_tree() -> JSONResponse:
    """
    Get the parse tree from a JSON file.

    Returns:
        JSONResponse: The parse tree data.
    """
    try:
        with open(PATH_PARSE_TREE + '.json', "r") as file:
            parse_tree_data = json.load(file)
        return JSONResponse(content=parse_tree_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
     
@app.get("/search_only_strategy")
async def search_strategy(
    impacts_names: list[str], execution_tree:str,
    bound: list[float], search_only: bool = False
    ) -> dict:
    """
    calcolate ONLY the strategy.
    Args:
        impacts_names (list[str]): The impacts names.
        execution_tree (ExecutionTreeModel): The execution tree.
        bound (np.ndarray): The bound.
        search_only (bool): If True, only search for a solution without building the strategy.
        

    Returns:
        dict: The expected impacts, possible min solution, solutions, and strategy and times associated with the computations.

    Raises:
        403: If the token is not provided, an exception not authorized.
        400: If the input is not valid, an exception is raised.
        500: If an error occurs, an exception is raised.
    """
    if not isinstance(bound, np.ndarray) or not isinstance(search_only, bool):
        return HTTPException(status_code=400, detail="Invalid input")
    try:

        expected_impacts, possible_min_solution, solutions, strategy, found_strategy_time, build_strategy_time = search(
            execution_tree, bound, impacts_names, search_only
        )

        if expected_impacts is None:
            text_result = ""
            for i in range(len(possible_min_solution)):
                text_result += f"Exp. Impacts {i}:\t{np.round(possible_min_solution[i], 2)}\n"
            #print(f"Failed:\t\t\t{bpmn.impacts_names}\nPossible Bound Impacts:\t{bound}\n" + text_result)
            text_result = ""
            for i in range(len(solutions)):
                text_result += f"Guaranteed Bound {i}:\t{np.ceil(solutions[i])}\n"

            #print(str(datetime.now()) + " " + text_result)
            return {
                "text_result": text_result,
                "expected_impacts": expected_impacts,
                "possible_min_solution": possible_min_solution,
                "solutions": solutions,
                "strategy": [],
                "found_strategy_time": found_strategy_time,
                "build_strategy_time": build_strategy_time
            }

        if strategy is None:
            text_result = f"Any choice taken will provide a winning strategy with an expected impact of: "
            text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(impacts_names,  [item for item in expected_impacts]))
            print(str(datetime.now()) + " " + text_result)
            return {
                "text_result": text_result,
                "expected_impacts": expected_impacts,
                "possible_min_solution": possible_min_solution,
                "solutions": solutions,
                "strategy": [],
                "found_strategy_time": found_strategy_time,
                "build_strategy_time": build_strategy_time
            }
        text_result = f"This is the strategy, with an expected impact of: "
        text_result += " ".join(f"{key}: {round(value,2)}" for key, value in zip(impacts_names,  [item for item in expected_impacts]))

        return {
            "text_result": text_result,
            "expected_impacts": expected_impacts,
            "possible_min_solution": possible_min_solution,
            "solutions": solutions,
            "strategy": strategy,
            "found_strategy_time": found_strategy_time,
            "build_strategy_time": build_strategy_time
        }

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/explainer")
async def get_explainer(
    parse_tree: dict, impacts_names: list[str], strategy: dict = {}, type_explainer: int = 3) -> dict:
    """
    Get the explainer.

    Args:
        parse_tree (json): The parse tree.
        strategy: The strategy.
        type_explainer (int): The type of explainer:
            CURRENT_IMPACTS = 0
            UNAVOIDABLE_IMPACTS = 1
            DECISION_BASED = 2
            HYBRID = 3 default
        impacts_names (list[str]): The impacts names.        

    Returns:
        tuple: The strategy tree, expected impacts, strategy expected time, choices, and name svg.

    Raises:
        400: If the input is not valid, an exception is raised.
        500: If an error occurs, an exception is raised.
    """
    if not isinstance(strategy, dict) or not isinstance(type_explainer, int):
        return HTTPException(status_code=400, detail="Invalid input")
    # if strategy == {}:
    #     return None
    try:
        if type_explainer == 0:
            type_explainer = ExplanationType.CURRENT_IMPACTS
        elif type_explainer == 1:
            type_explainer = ExplanationType.UNAVOIDABLE_IMPACTS
        elif type_explainer == 2:
            type_explainer = ExplanationType.DECISION_BASED
        else:
            type_explainer = ExplanationType.HYBRID
        parse_tree = ParseTree.from_json(parse_tree)
        print(parse_tree)
        print(type(parse_tree))
        print(type_explainer)
        print(type(type_explainer))
        strategy_tree, expected_impacts, strategy_expected_time, choices, time_explain_strategy, strategy_tree_time = build_explained_strategy(
            parse_tree, strategy, type_explainer, impacts_names
        )
        return  {
            "strategy_tree": str(strategy_tree),
            "expected_impacts": expected_impacts,
            "strategy_expected_time": strategy_expected_time,
            "choices": choices,
            "time_explain_strategy": time_explain_strategy,
            "strategy_tree_time": strategy_tree_time,
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

#######################################################
###             LLMS API                            ###
#######################################################
@app.get("/agent_definition")
async def get_agent(
    url: str, api_key: str, 
    model: str, temperature: float,
    ):
    """
    Define the agent with the given parameters.

    Args:
        url (str): The url of the agent.
        api_key (str): The api key of the agent.
        model (str): The model of the agent.
        temperature (float): The temperature of the agent.
        

    Returns:
       tuple: The agent defined and the configuration.
    """
    if not isinstance(url, str) or not isinstance(api_key, str) or not isinstance(model, str) or not isinstance(temperature, float):
        return HTTPException(status_code=400, detail="Invalid input")
    try:
        llm, config =  define_agent(
            url=url, api_key=api_key, 
            model=model, temperature=temperature)
        return {
            "llm": llm,
            "config": config
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_chat_history")
async def get_chat_history(session_id: str) -> list:
    """
    Get the chat history.

    Args:
        session_id (str): The session id.

    Returns:
        list: The chat history.
    """
    if not isinstance(session_id, str):
        return HTTPException(status_code=400, detail="Invalid input")
    try:
        return chat_histories[session_id]
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
#######################################################
########### GET SVG TREES #############################
#######################################################

#------------------------------------------------------
#           EXCECUTION TREES
#------------------------------------------------------
@app.get("/get_execution_tree_state")
async def get_execution_tree_state() -> FileResponse:
    """
    Get the execution state tree.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXECUTION_TREE_STATE+ '.svg', 
            media_type="image/svg", 
            filename="execution_tree_state.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_execution_tree_state_time")
async def get_execution_tree_state_time() -> FileResponse:
    """
    Get the execution tree with states and times contracted.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXECUTION_TREE_STATE_TIME+ '.svg', 
            media_type="image/svg", 
            filename="execution_tree_state_time.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_execution_tree_state_time_extended")
async def get_execution_tree_state_time_extended() -> FileResponse:
    """
    Get the execution tree with states and times extended.

    Returns:
        FileResponse:The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXECUTION_TREE_STATE_TIME_EXTENDED+ '.svg', 
            media_type="image/svg", 
            filename="execution_tree_state_time_extended.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_execution_tree_time")
async def get_execution_tree_time() -> FileResponse:
    """
    Get the execution tree  only times.

    Returns:
        FileResponse:The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXECUTION_TREE_TIME+ '.svg', 
            media_type="image/svg", 
            filename="execution_tree_time.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    

#------------------------------------------------------
#           EXPLAINER TREES
#------------------------------------------------------

@app.get("/get_explainer_decision_tree")
async def get_explainer_decision_tree() -> FileResponse:
    """
    Get the execution tree with states and times extended.

    Returns:
        FileResponse:The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXPLAINER_DECISION_TREE+ '.svg', 
            media_type="image/svg", 
            filename="explainer_decision_tree.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_explainer_bdd")
async def get_explainer_bdd() -> FileResponse:
    """
    Get the execution tree  only times.

    Returns:
        FileResponse:The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_EXPLAINER_BDD+ '.svg', 
            media_type="image/svg", 
            filename="explainer_bdd.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    


#------------------------------------------------------
#       STRATEGY TREES
#------------------------------------------------------
@app.get("/get_strategy_tree_state")
async def get_strategy_tree_state() -> FileResponse:
    """
    Get the strategy tree with states.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_STRATEGY_TREE_STATE+ '.svg', 
            media_type="image/svg", 
            filename="strategy_tree_state.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
@app.get("/get_strategy_tree_state_time")
async def get_strategy_tree_state_time() -> FileResponse:
    """
    Get the strategy tree with states and times contracted.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_STRATEGY_TREE_STATE_TIME + '.svg', 
            media_type="image/svg", 
            filename="strategy_tree_state_time.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


@app.get("/get_strategy_tree_state_time_extended")
async def get_strategy_tree_state_time_extended() -> FileResponse:
    """
    Get the strategy tree with states and times extended.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_STRATEGY_TREE_STATE_TIME_EXTENDED+ '.svg', 
            media_type="image/svg", 
            filename="strategy_tree_state_time_extended.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.get("/get_strategy_tree_time")
async def get_strategy_tree_time() -> FileResponse:
    """
    Get the strategy tree  only times.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_STRATEGY_TREE_TIME+ '.svg', 
            media_type="image/svg", 
            filename="strategy_tree_time.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e)) 

#------------------------------------------------------
#      PARSE TREE
# -----------------------------------------------------

@app.get("/get_parse_tree")    
async def get_region_tree() -> FileResponse:
    """
    Get the parse tree.

    Returns:
        FileResponse: The tree in svg format.
    """
    try:
        return FileResponse(
            PATH_PARSE_TREE+ '.svg', 
            media_type="image/svg", 
            filename="parse_tree.svg"
        )
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
#######################################################
############ POST #####################################
#######################################################

@app.post("/set_bpmn")
async def set_bpmn(
    bpmn_lark: dict, impacts_table, 
    durations, task: str,
    loops, probabilities, delays, ):
    try:
        bpmn_lark[IMPACTS] = cs.extract_impacts_dict(bpmn_lark[IMPACTS_NAMES], impacts_table) 
        # print(bpmn_lark[IMPACTS])
        bpmn_lark[IMPACTS] = cs.impacts_dict_to_list(bpmn_lark[IMPACTS])     
        # print(bpmn_lark[IMPACTS], ' AS LISTR')   

        bpmn_lark[DURATIONS] = cs.create_duration_dict(task=task, durations=durations)
    
        list_choises = cs.extract_choises(task)        
        loops_chioses = cs.extract_loops(task) 
        choises_nat = cs.extract_choises_nat(task) + loops_chioses
        bpmn_lark[PROBABILITIES] = cs.create_probabilities_dict(choises_nat, probabilities)
        bpmn_lark[PROBABILITIES], bpmn_lark[LOOP_PROB] = cs.divide_dict(bpmn_lark[PROBABILITIES], loops_chioses)
        bpmn_lark[NAMES] = cs.create_probabilities_names(list_choises)
        bpmn_lark[DELAYS] = cs.create_probabilities_dict(cs.extract_choises_user(task), delays)
        bpmn_lark[LOOP_PROB] = cs.create_probabilities_dict(loops_chioses,loops)
        if cs.checkCorrectSyntax(bpmn_lark):
            return bpmn_lark
        else:
            return HTTPException(status_code=400, detail="Invalid BPMN syntax")
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))

@app.post("/create_sese_diagram")
async def print_bpmn(request: BPMNPrinting):
    """
    Generates and returns a BPMN diagram str that then can be converted to a pydot object.
    Args:
        request (BPMNPrinting): BPMN printing configuration
    Returns:
        FileResponse: PNG image of the BPMN diagram
    returns:
        HTTPException: 400 for invalid input, 500 for server errors, 403 for unauthorized access
    """
    bpmn = request.bpmn
    if not isinstance(request, BPMNPrinting):
        return HTTPException(status_code=400, detail="Invalid input")
    if not checkCorrectSyntax(dict(bpmn)):
        return HTTPException(status_code=400, detail="Invalid BPMN syntax")   
    try:        
        print('BPMN', dict(bpmn))
        print(request)
        img = print_sese_diagram(expression=bpmn.expression,
            h=bpmn.h, 
            probabilities=bpmn.probabilities, 
            impacts=bpmn.impacts, 
            loop_thresholds=bpmn.loop_thresholds, 
            graph_options=request.graph_options, 
            durations=bpmn.durations, 
            names=bpmn.names, 
            delays=bpmn.delays, 
            impacts_names=bpmn.impacts_names, 
            loop_round=bpmn.loop_round, 
            loop_probability=bpmn.loop_probability
        )
        return {
            "graph": img
        }
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))



@app.post("/invoke_agent")
async def invoke_agent(request: AgentRequest) ->  dict:
    """
    Invoke the agent with the given prompt.

    Args:
        prompt (str): The prompt to be used.
        
        llm: The agent defined.
        history: The history of the agent.

    Returns:
        str: The response from the agent.
        list[tuple]: The history of the agent.
    """
    if not isinstance(request, AgentRequest):
        return HTTPException(status_code=400, detail="Invalid input")
    print(request)
    try:
        # Retrieve or initialize chat history
        if request.session_id not in chat_histories:
            chat_histories[request.session_id] = []
        
        # Append new input to history
        chat_history = chat_histories[request.session_id]
        chat_history.append({"role": "human", "content": request.prompt})

        # Format chat history as input
        formatted_history = "\n".join(
            [f"{msg['role']}: {msg['content']}" for msg in chat_history]
        )
        # Define agent
        llm, _ = define_agent(
            url=request.url,
            verbose=request.verbose,
            api_key=request.api_key,
            model=request.model,
            temperature=request.temperature
        )

        response = llm.invoke({"input": formatted_history})
        chat_history.append({"role": "ai", "content": response.content})
        print(chat_history)
        return {"session_id": request.session_id, "response": response.content}

    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))


#######################################################
#### MAIN #############################################
#######################################################

if __name__ == '__main__':   
    uvicorn.run(
        app, 
        host="0.0.0.0", port=8000
    )