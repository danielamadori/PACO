from pony.orm import Database, Required, db_session, select, commit, Optional
import json
import os

db = Database()

class BPMNDiagram(db.Entity):
    bpmn = Required(str, unique=True)
    bpmn_dot = Optional(str, nullable=True)
    parse_tree = Optional(str, nullable=True)
    execution_tree = Optional(str, nullable=True)
    strategy = Optional(str, nullable=True)
    bdds = Optional(str, nullable=True)


def init_db(db_path:str):
    dir_path = os.path.dirname(db_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    db.bind(provider='sqlite', filename=db_path, create_db=True)
    db.generate_mapping(create_tables=True)

@db_session
def fetch_diagram_by_bpmn(bpmn_dict:dict):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    return BPMNDiagram.get(bpmn=bpmn_str)

@db_session
def save_bpmn_dot(bpmn_dict:dict, bpmn_dot:str):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    if not BPMNDiagram.get(bpmn=bpmn_str):
        BPMNDiagram(bpmn=bpmn_str, bpmn_dot=bpmn_dot, parse_tree="", execution_tree="")
        commit()

@db_session
def save_parse_and_execution_tree(bpmn_dict:dict, parse_tree:str, execution_tree:str):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    record = BPMNDiagram.get(bpmn=bpmn_str)
    if record:
        record.parse_tree = parse_tree or ""
        record.execution_tree = execution_tree or ""
        commit()

@db_session
def save_strategy_results(bpmn_dict:dict, strategy:str, bdds:str):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    record = BPMNDiagram.get(bpmn=bpmn_str)
    if record:
        record.strategy = strategy or ""
        record.bdds = bdds or ""
        commit()
