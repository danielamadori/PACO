import json
from collections import defaultdict

def parse_dash_output(output_str):
    """
    Parses a Dash output string which might contain multiple outputs separated by '...'
    and might contain 'MultiplexerTransform' hashes (e.g. id.prop@hash).
    """
    # Remove leading/trailing dots
    cleaned = output_str.strip('.')
    # Split by '...'
    parts = cleaned.split('...')
    outputs = []
    
    for part in parts:
        pk = part
        # Check for hash usually added by MultiplexerTransform (e.g., @somehash)
        # It usually looks like id.property@hash or just id.property
        # If ID is a dictionary string, it might contain dots too?
        # A safer split is rsplit on the *last* dot, but the hash is after the property.
        
        # Heuristic: split by first '@' if present to check for hash
        has_hash = False
        if '@' in part:
            # But wait, could @ be in ID? Unlikely for standard IDs.
            # dash-extensions adds it.
            has_hash = True
            pk = part.split('@')[0]
        
        # Now split id and property
        # Dash IDs can be JSON strings `{"type":"...","index":"..."}`.
        # Find the last dot that separates ID and property.
        last_dot = pk.rfind('.')
        if last_dot != -1:
            comp_id = pk[:last_dot]
            prop = pk[last_dot+1:]
        else:
            comp_id = pk
            prop = "unknown"
            
        outputs.append({
            "full": part,
            "id": comp_id,
            "property": prop,
            "has_hash": has_hash
        })
    return outputs

def analyze_dependencies(json_file):
    with open(json_file, "r") as f:
        deps = json.load(f)

    # 1. Map Outputs to Callbacks
    # Key: "id.property", Value: list of callback_indices
    output_map = defaultdict(list)
    
    # 2. Map Callbacks to Inputs (for cycle detection)
    callback_inputs = defaultdict(list)
    callback_outputs = defaultdict(list)
    
    # 3. Connect Component Inputs to Component Outputs (for global graph cycles)
    # This is a bit complex because a callback is a hyperedge. 
    # Valid cycle: C1 writes A -> C2 reads A, writes B -> C1 reads B.
    
    god_callbacks = []
    multiplexed_outputs = set()
    
    print("## Analysis Report\n")
    
    for i, dep in enumerate(deps):
        cb_name = f"Callback_{i}"
        
        # Parse Outputs
        outs = parse_dash_output(dep['output'])
        for out in outs:
            output_key = f"{out['id']}.{out['property']}"
            output_map[output_key].append(i)
            callback_outputs[i].append(output_key)
            if out['has_hash']:
                multiplexed_outputs.add(output_key)
        
        # Parse Inputs
        for inp in dep['inputs']:
            inp_key = f"{inp['id']}.{inp['property']}"
            callback_inputs[i].append(inp_key)

        # Check for God Callbacks (heuristic: > 5 outputs or > 8 inputs)
        if len(outs) > 5:
            god_callbacks.append((cb_name, len(outs), "High Output Count"))
        
        # Check for direct loops (Input is also Output)
        # Note: 'State' does not trigger loops in Dash execution, only 'Input'.
        input_keys = [f"{inp['id']}.{inp['property']}" for inp in dep['inputs']]
        output_keys = [f"{o['id']}.{o['property']}" for o in outs]
        
        common = set(input_keys).intersection(output_keys)
        if common:
             print(f"- [WARNING] **Direct Circular Dependency** in {cb_name}: {common}")
             print("  (Note: If these inputs are used to calculate the new value of themselves, this creates an infinite loop unless prevented explicitly by Dash's update semantics or `no_update`).")

    # Check for Multiple Writers (standard Dash violation)
    print("### Multiple Writers Check")
    violations = 0
    for k, v in output_map.items():
        if len(v) > 1:
            if k in multiplexed_outputs:
                # Expected if using MultiplexerTransform
                pass 
            else:
                # If NOT using MultiplexerTransform detected via hash, this is a crash risk
                print(f"- [CRITICAL] Property `{k}` is written by multiple callbacks: {v}. This will crash standard Dash apps unless MultiplexerTransform is used.")
                violations += 1
    
    if len(multiplexed_outputs) > 0:
        print(f"- [INFO] Detected `MultiplexerTransform` usage on {len(multiplexed_outputs)} outputs. This allows multiple callbacks to target the same output.")
    
    if violations == 0 and len(multiplexed_outputs) == 0:
        print("- [OK] No multiple writers detected.")
        
    # God Callbacks
    if god_callbacks:
        print("\n### High Complexity Callbacks (God Components)")
        print("These callbacks touch many parts of the state and are fragility risks:")
        for name, count, reason in god_callbacks:
            print(f"- **{name}**: {count} outputs. ({reason})")
            # Print inputs/outputs for context
            inputs = [x.split('.')[-1] for x in callback_inputs[int(name.split('_')[1])]]
            outputs = [x.split('.')[-1] for x in callback_outputs[int(name.split('_')[1])]]
            print(f"  - Inputs ({len(inputs)}): {inputs[:5]}...")
            print(f"  - Outputs: {outputs[:5]}...")

    # Data Flow Gaps
    print("\n### Data Flow Gaps")
    # Store components that are written to but never read (Dead Stores)
    # or components read from but never written to (might be static or external)
    
    all_inputs = set()
    for v in callback_inputs.values():
        for x in v: all_inputs.add(x)
        
    all_outputs = set()
    for v in callback_outputs.values():
        for x in v: all_outputs.add(x)
        
    # Ignore simple UI properties like 'n_clicks', 'value' which are user-driven
    # Focus on 'store' type components or main data containers
    
    dead_stores = []
    magic_stores = []
    
    for out in all_outputs:
        if 'store' in out and out not in all_inputs:
            dead_stores.append(out)
            
    for inp in all_inputs:
        if 'store' in inp and inp not in all_outputs:
            # Might be defined in layout but never updated by callback
            magic_stores.append(inp)
            
    if dead_stores:
        print(f"- [WARNING] **Dead Stores** (Written but never read):")
        for x in dead_stores: print(f"  - {x}")
        
    if magic_stores:
        print(f"- [INFO] **Static/Layout Stores** (Read but never written by callback):")
        for x in magic_stores: print(f"  - {x}")

if __name__ == "__main__":
    analyze_dependencies('dependencies.json')
