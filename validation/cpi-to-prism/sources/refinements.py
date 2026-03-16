from typing import Dict, List
import json
from pathlib import Path
from cpi_to_prism_etl import cpi_to_model
from sampler import sample_expected_impact
from analysis import analyze_bounds

def _find_cpi_to_prism_root(start: Path) -> Path:
    for parent in start.parents:
        if parent.name == "cpi-to-prism":
            return parent
    raise RuntimeError(f"Unable to locate cpi-to-prism root from {start}")

_CPI_TO_PRISM_DIR = _find_cpi_to_prism_root(Path(__file__).resolve())
_CPIS_DIR = _CPI_TO_PRISM_DIR / "CPIs"

def refine_bounds(process_name: str, num_refinements: int, verbose: bool=False) -> Dict[str, float]:
    """
    Refine impact bounds through dichotomous search.
    
    Args:
        process_name: Name of the process (without extension)
        num_refinements: Number of refinement iterations
        
    Returns:
        Dictionary of refined bounds for each impact
    """
    if num_refinements < 0:
        raise ValueError("Number of refinements must be positive")
        
    # Load CPI file
    cpi_path = _CPIS_DIR / f'{process_name}.cpi'
    try:
        with open(cpi_path, 'r') as f:
            cpi_dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Error loading CPI file: {str(e)}")
        
    # Create MDP model
    cpi_to_model(process_name)
    
    # Get initial bounds via sampling
    initial_bounds = sample_expected_impact(cpi_dict)
    if not initial_bounds:
        raise ValueError("No impacts found in the model")
        
    # Initialize intervals for each impact
    intervals = {
        impact_name: [0.0, bound_value]
        for impact_name, bound_value in initial_bounds.items()
    }
    final_bounds = initial_bounds

    # Perform refinements
    for iteration in range(num_refinements):
        for current_impact in intervals.keys():
            # Create test bounds - split current impact, keep others at upper bound
            test_bounds = {
                name: intervals[name][1] if name != current_impact 
                else (intervals[name][0] + intervals[name][1]) / 2
                for name in intervals
            }
            
            # Test these bounds
            result = analyze_bounds(process_name, test_bounds)
            
            # Update interval based on result
            if result['result']:  # Property satisfied
                final_bounds = {
                    impact_name: interval[1] for impact_name, interval in intervals.items()
                }
                intervals[current_impact][1] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
            else:  # Property not satisfied
                intervals[current_impact][0] = (intervals[current_impact][0] + intervals[current_impact][1]) / 2
    
            # Print progress
            print_refinement_progress(iteration, current_impact, intervals, test_bounds, result['result']) if verbose else None


    result = analyze_bounds(process_name, final_bounds)

    s = ""
    if not result['result']: # Solution not found
        s = "No solution found"

    return initial_bounds, final_bounds, s

def print_refinement_progress(iteration: int, impact_name: str, intervals: Dict[str, List[float]],
                            test_bounds: Dict[str, float], result: bool) -> None:
    """Helper function to print refinement progress."""
    print(f"\nIteration {iteration + 1}:")
    print(f"Testing impact: {impact_name}")
    print("Current intervals:", {k: [round(v[0], 6), round(v[1], 6)] for k, v in intervals.items()})
    print("Test bounds:", {k: round(v, 6) for k, v in test_bounds.items()})
    print("Result:", "Satisfied" if result else "Not satisfied")
