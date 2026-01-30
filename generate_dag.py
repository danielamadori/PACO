import json
import re

def sanitize_id(node_id):
    """Sanitizes the node ID for Mermaid usage."""
    # If it is a string representation of a dict, try to parse it
    if isinstance(node_id, str) and node_id.startswith('{'):
        try:
            id_dict = json.loads(node_id)
            # Create a readable label
            label = []
            if 'type' in id_dict:
                t = id_dict['type']
                if isinstance(t, list): t = str(t)
                label.append(str(t))
            if 'index' in id_dict:
                i = id_dict['index']
                if isinstance(i, list): i = str(i)
                label.append(f"({str(i)})")
            elif 'id' in id_dict:
                label.append(f"({str(id_dict['id'])})")
            
            clean_label = " ".join(label)
            return clean_label.replace('"', "'")
        except:
            pass
    return str(node_id).replace('"', "'")

def get_node_id(node_str):
    """Generates a valid Mermaid ID from a string."""
    # Hash or simple extraction. Simple extraction to keep it readable if possible
    # But for complex IDs, a hash or index is better.
    # Let's use the full string as ID but escaped, or map to an index.
    return node_mappings.setdefault(node_str, f"n{len(node_mappings)}")

node_mappings = {}

def parse_output_string(output_str):
    """Parses Dash output string '..id.prop...id2.prop2..'."""
    # Remove leading/trailing dots
    cleaned = output_str.strip('.')
    # Split by '...' which separates multiple outputs
    parts = cleaned.split('...')
    outputs = []
    
    for part in parts:
        # Last index of '.' separates ID and property
        if '.' in part:
            last_dot = part.rfind('.')
            id_part = part[:last_dot]
            prop_part = part[last_dot+1:]
            outputs.append({"id": id_part, "property": prop_part})
        else:
            outputs.append({"id": part, "property": "unknown"})
    return outputs

with open('dependencies.json', 'r') as f:
    dependencies = json.load(f)

print("graph LR")

for i, dep in enumerate(dependencies):
    callback_id = f"cb{i}"
    # Callback node
    print(f"    {callback_id}((Callback {i}))")
    
    # Inputs
    for inp in dep['inputs']:
        node_label = sanitize_id(inp['id'])
        full_id = f"{inp['id']}.{inp['property']}"
        mermaid_id = get_node_id(full_id)
        
        print(f'    {mermaid_id}["{node_label}<br/>.{inp["property"]}"] --> {callback_id}')

    # States (as dotted lines)
    for state in dep['state']:
        node_label = sanitize_id(state['id'])
        full_id = f"{state['id']}.{state['property']}"
        mermaid_id = get_node_id(full_id)
        
        print(f'    {mermaid_id}["{node_label}<br/>.{state["property"]}"] -.-> {callback_id}')

    # Outputs
    outputs = []
    if isinstance(dep['output'], str):
        outputs = parse_output_string(dep['output'])
    else:
        # List of strings? Assuming singular format or list of strings
        # Adjust based on observed structure if needed, but usually it's string representation
        # If it is a list of strings (which Dash sometimes does), handle it.
        pass # The provided JSON shows output as a string.

    for out in outputs:
        node_label = sanitize_id(out['id'])
        full_id = f"{out['id']}.{out['property']}"
        mermaid_id = get_node_id(full_id)
        
        print(f'    {callback_id} --> {mermaid_id}["{node_label}<br/>.{out["property"]}"]')
