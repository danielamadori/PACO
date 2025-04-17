from fastapi.encoders import jsonable_encoder
from agent import define_agent
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np

from paco.execution_tree.execution_tree import ExecutionTree
from paco.explainer.bdd.bdds import bdds_to_dict
from paco.parser.create import create
from paco.parser.bpmn_parser import SESE_PARSER, create_parse_tree
from paco.parser.print_sese_diagram import print_sese_diagram
from paco.parser.parse_tree import ParseTree
from paco.solver import paco
from utils.env import DURATIONS, IMPACTS_NAMES, EXPRESSION
from utils.check_syntax import check_bpmn_syntax
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

@app.get("/create_bpmn")
async def check_bpmn(request: dict) -> dict:
    bpmn = request.get("bpmn")
    if bpmn is None:
        raise HTTPException(status_code=400, detail="No BPMN found")

    try:
        lark_tree = check_bpmn_syntax(dict(bpmn))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        return { "bpmn_dot": print_sese_diagram(bpmn, lark_tree) }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/create_parse_tree")
async def get_parse_tree(request: dict) -> dict:
    bpmn = request.get("bpmn")
    if bpmn is None:
        raise HTTPException(status_code=400, detail="No BPMN found")

    try:
        lark_tree = check_bpmn_syntax(dict(bpmn))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
        parse_tree, pending_choices, pending_natures = create_parse_tree(bpmn)

        return {"parse_tree": parse_tree.to_dict()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/create_execution_tree")
async def get_execution_tree(request: dict) -> dict:
    bpmn = request.get("bpmn")
    if bpmn is None:
        raise HTTPException(status_code=400, detail="No BPMN found")
    try:
        bpmn = dict(bpmn)
        bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])
        lark_tree = check_bpmn_syntax(bpmn)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        parse_tree, pending_choices, pending_natures, execution_tree, times = create(bpmn)
        return {"parse_tree": parse_tree.to_dict(),
                "execution_tree": execution_tree.to_dict(),
                "times": times}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/create_strategy")
async def search_strategy(request: dict) -> dict:
    bpmn = request.get("bpmn")
    bound = request.get("bound")
    parse_tree = request.get("parse_tree")
    execution_tree = request.get("execution_tree")
    search_only = request.get("search_only")

    if bpmn is None:
        raise HTTPException(status_code=400, detail="No BPMN found")
    if not isinstance(bpmn, dict):
        raise HTTPException(status_code=400, detail="Invalid BPMN format, expected a dictionary")
    if bound is None or not isinstance(bound, list):
        raise HTTPException(status_code=400, detail="Invalid 'bound' format, expected a list of float")
    if len(bound) != len(bpmn[IMPACTS_NAMES]):
        raise HTTPException(status_code=400, detail="Invalid 'bound' format, expected a list of float with the same size of impacts")
    if parse_tree is None:
        raise HTTPException(status_code=400, detail="No parse tree provided")
    if execution_tree is None:
        raise HTTPException(status_code=400, detail="No execution tree provided")
    if search_only is None or not isinstance(search_only, bool):
        search_only = False

    # BPMN Preprocessing
    try:
        bpmn = dict(bpmn)  # Ensure BPMN is a dictionary
        bpmn[DURATIONS] = cs.set_max_duration(bpmn[DURATIONS])  # Modify durations
        lark_tree = check_bpmn_syntax(bpmn)  # Validate BPMN syntax and Parse the BPMN expression
        bound = np.array(bound, dtype=np.float64)
        parse_tree, pending_choices, pending_natures = ParseTree.from_json(parse_tree, impact_size=len(bpmn[IMPACTS_NAMES]), non_cumulative_impact_size=0)
        execution_tree = ExecutionTree.from_json(parse_tree, execution_tree, pending_choices, pending_natures)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        text_result, result, times = paco(bpmn, bound, parse_tree=parse_tree, execution_tree=execution_tree, search_only=search_only)

        result_dict = {
            "result": text_result, "times": times,
            "bpmn": result["bpmn"], "bound": str(result["bound"]),
            "parse_tree": result["parse_tree"].to_dict(),
            "execution_tree": result["execution_tree"].to_dict(),
            "possible_min_solution": str([str(bound) for bound in result["possible_min_solution"]]),
            "guaranteed_bounds": str([str(bound) for bound in result["guaranteed_bounds"]])
        }


        x = result.get("expected_impacts")
        y = result.get("frontier_solution")
        if x is not None and y is not None:# Search Win
            result_dict.update({
                "expected_impacts" : str(x),
                "frontier_solution" : str([execution_tree.root.id for execution_tree in y])
            })

        x = result.get("strategy_tree")
        y = result.get("strategy_expected_impacts")
        z = result.get("strategy_expected_time")
        w = result.get("bdds")
        if x is not None and y is not None and z is not None and w is not None: # Strategy Explained Done
            result_dict.update({
                "strategy_tree": x.to_dict(),
                "strategy_expected_impacts": str(y),
                "strategy_expected_time": str(z),
                "bdds": bdds_to_dict(w),
                "bdds_dot": [bdd.bdd_to_dot() for bdd in w]
            })

        return jsonable_encoder(result_dict)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



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
        raise HTTPException(status_code=400, detail="Invalid input")
    try:
        llm, config =  define_agent(
            url=url, api_key=api_key, 
            model=model, temperature=temperature)
        return {
            "llm": llm,
            "config": config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(status_code=400, detail="Invalid input")
    try:
        return chat_histories[session_id]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





#######################################################
############ POST #####################################
#######################################################




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
        raise HTTPException(status_code=400, detail="Invalid input")
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
        raise HTTPException(status_code=500, detail=str(e))


#######################################################
#### MAIN #############################################
#######################################################

if __name__ == '__main__':   
    uvicorn.run(
        app, 
        host="0.0.0.0", port=8000
    )