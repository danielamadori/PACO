from pony.orm import Database, Required, db_session, select, commit, Optional
import json
import os

db = Database()

class BPMNDiagram(db.Entity):
    bpmn = Required(str, unique=True)
    bpmn_dot = Optional(str)
    parse_tree = Optional(str)
    execution_tree = Optional(str)


def init_db(db_path:str):
    dir_path = os.path.dirname(db_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    db.bind(provider='sqlite', filename=db_path, create_db=True)
    db.generate_mapping(create_tables=True)

@db_session
def fetch_diagram_by_bpmn(bpmn_dict):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    return BPMNDiagram.get(bpmn=bpmn_str)

@db_session
def save_diagram_if_absent(bpmn_dict:str, bpmn_dot:str):
    bpmn_str = json.dumps(bpmn_dict, sort_keys=True)
    if not BPMNDiagram.get(bpmn=bpmn_str):
        BPMNDiagram(bpmn=bpmn_str, bpmn_dot=bpmn_dot, parse_tree="", execution_tree="")
        commit()