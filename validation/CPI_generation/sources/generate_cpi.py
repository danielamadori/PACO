import os
import json
import gzip
from generated_processes import get_process_from_file, translate_to_cpi
from tqdm import tqdm
from itertools import product
from typing import List, Tuple, Dict, Union, Optional

DEFAULT_GENERATION_MODES = [
    "random",
    "bagging_divide",
    "bagging_remove",
    "bagging_remove_divide",
    "bagging_remove_reverse",
    "bagging_remove_reverse_divide"
]

DEFAULT_CHOICE_DISTRIBUTIONS = [round(i/10, 1) for i in range(1, 10)]  # 0.1 to 0.9

def read_cpi_bundles(
    bundle_pattern: Optional[str] = None,
    x: Optional[int] = None,
    y: Optional[int] = None
) -> List[Dict]:
    """
    Read compressed CPI bundles from files and return a list of CPI dictionaries.
    
    Args:
        bundle_pattern: Optional pattern to match specific bundle files (e.g., "x1_y*")
        x: Optional specific x value to load
        y: Optional specific y value to load
        
    Returns:
        List of CPI dictionaries from all matching bundle files
    """
    bundle_dir = 'CPIs'
    all_cpis = []
    
    # Get list of files to process
    if x is not None and y is not None:
        files = [f"cpi_bundle_x{x}_y{y}.cpis.gz"]
    elif bundle_pattern:
        files = [f for f in os.listdir(bundle_dir) 
                if f.endswith('.cpis.gz') and bundle_pattern in f]
    else:
        files = [f for f in os.listdir(bundle_dir) if f.endswith('.cpis.gz')]
    
    # Process each file
    with tqdm(total=len(files), desc="Reading CPI bundles") as pbar:
        for filename in files:
            try:
                filepath = os.path.join(bundle_dir, filename)
                if os.path.exists(filepath):
                    with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                        bundle_data = json.load(f)
                        all_cpis.extend(bundle_data)
            except Exception as e:
                print(f"Error reading bundle {filename}: {str(e)}")
            pbar.update(1)
    
    print(f"\nRead {len(all_cpis)} CPIs from {len(files)} bundle files")
    return all_cpis

def generate_cpi_files_parametrized(
    x_range: Tuple[int, int] = (1, 10),
    y_range: Tuple[int, int] = (1, 10),
    z_range: Tuple[int, int] = (1, 10),
    impact_dims_range: Tuple[int, int] = (1, 10),
    generation_modes: List[str] = None,
    duration_interval: Tuple[int, int] = (1, 10),
    choice_distributions: List[float] = None
) -> List[str]:
    """
    Generate compressed .cpis bundle files for each x,y combination within specified ranges.
    Uses generate_cpi_bundle for each x,y pair.
    
    Args:
        x_range: Tuple of (min_x, max_x) inclusive, default (1, 10)
        y_range: Tuple of (min_y, max_y) inclusive, default (1, 10)
        z_range: Tuple of (min_z, max_z) inclusive, default (1, 10)
        impact_dims_range: Tuple of (min_dims, max_dims) inclusive, default (1, 10)
        generation_modes: List of generation modes to use, default all available modes
        duration_interval: Tuple of (min_duration, max_duration), default (1, 10)
        choice_distributions: List of probabilities for choice vs nature nodes, default [0.1, ..., 0.9]
    
    Returns:
        List[str]: List of generated bundle filenames
    """
    # Set default values if not provided
    if generation_modes is None:
        generation_modes = DEFAULT_GENERATION_MODES
    
    if choice_distributions is None:
        choice_distributions = DEFAULT_CHOICE_DISTRIBUTIONS

    ensure_directory('CPIs')
    generated_bundles = []
    errors = []
    
    # Create combinations for x,y pairs
    xy_combinations = product(
        range(x_range[0], x_range[1] + 1),
        range(y_range[0], y_range[1] + 1)
    )
    
    # Calculate total number of x,y pairs
    total_xy_pairs = (x_range[1] - x_range[0] + 1) * (y_range[1] - y_range[0] + 1)
    
    # Main generation loop with tqdm for x,y pairs
    with tqdm(total=total_xy_pairs, desc="Generating CPI bundles") as pbar:
        for x, y in xy_combinations:
            try:
                # Use generate_cpi_bundle for each x,y pair
                bundle_path = generate_cpi_bundle(
                    x=x,
                    y=y,
                    z_range=z_range,
                    impact_dims_range=impact_dims_range,
                    generation_modes=generation_modes,
                    duration_interval=duration_interval,
                    choice_distributions=choice_distributions
                )
                generated_bundles.append(os.path.basename(bundle_path))
                
            except Exception as e:
                error_msg = f"Error processing bundle for x={x}, y={y}: {str(e)}"
                errors.append(error_msg)
            
            pbar.update(1)
    
    # Print final statistics and errors
    print(f"\nGeneration complete!")
    print(f"Total bundles generated: {len(generated_bundles)}")
    if errors:
        print(f"\nErrors encountered ({len(errors)}):")
        for error in errors:
            print(f"- {error}")
        
        # Save errors to file
        with open('generation_errors.log', 'w') as f:
            f.write('\n'.join(errors))
        print(f"\nErrors have been saved to 'generation_errors.log'")
    
    return generated_bundles

def generate_cpi_bundle(
    x: int,
    y: int,
    z_range: Tuple[int, int] = (1, 10),
    impact_dims_range: Tuple[int, int] = (1, 10),
    generation_modes: List[str] = None,
    duration_interval: Tuple[int, int] = (1, 10),
    choice_distributions: List[float] = None
) -> str:
    """
    Generate a bundle of CPIs for a specific x,y combination with all other parameter combinations.
    Saves the bundle as a compressed JSON file with .cpis.gz extension.
    
    Args:
        x: Fixed x value
        y: Fixed y value
        z_range: Range of z values to generate
        impact_dims_range: Range of impact dimensions to generate
        generation_modes: List of generation modes (defaults to all available modes)
        duration_interval: Task duration interval
        choice_distributions: List of choice probabilities (defaults to [0.1, ..., 0.9])
    
    Returns:
        str: Path to the generated bundle file
    """
    # Set default values if not provided
    if generation_modes is None:
        generation_modes = DEFAULT_GENERATION_MODES
    
    if choice_distributions is None:
        choice_distributions = DEFAULT_CHOICE_DISTRIBUTIONS
    
    # Generate all CPIs for this x,y combination
    cpi_bundle = []
    
    # Create all combinations except x,y
    combinations = product(
        range(z_range[0], z_range[1] + 1),
        range(impact_dims_range[0], impact_dims_range[1] + 1),
        choice_distributions,
        generation_modes
    )
    
    total_combinations = (
        (z_range[1] - z_range[0] + 1)
        * (impact_dims_range[1] - impact_dims_range[0] + 1)
        * len(choice_distributions)
        * len(generation_modes)
    )
    
    # Main generation loop with tqdm
    with tqdm(total=total_combinations, desc=f"Generating CPI bundle for x={x}, y={y}") as pbar:
        for z, num_impacts, choice_dist, mode in combinations:
            try:
                process_str = get_process_from_file(x, y, z)
                cpi_dict = translate_to_cpi(
                    process_str=process_str,
                    choice_distribution=choice_dist,
                    duration_interval=duration_interval,
                    num_impacts=num_impacts,
                    vector_generation_mode=mode
                )
                
                # Add metadata to the CPI
                cpi_dict['metadata'] = {
                    'x': x,
                    'y': y,
                    'z': z,
                    'num_impacts': num_impacts,
                    'choice_distribution': choice_dist,
                    'generation_mode': mode,
                    'duration_interval': duration_interval
                }
                
                cpi_bundle.append(cpi_dict)
            
            except Exception as e:
                print(f"Error processing z={z}, num_impacts={num_impacts}, choice_dist={choice_dist}, mode={mode}: {str(e)}")
            
            pbar.update(1)
    
    # Save the bundle as compressed file with .cpis.gz extension
    ensure_directory('CPIs')
    bundle_filename = f"cpi_bundle_x{x}_y{y}.cpis.gz"
    bundle_path = os.path.join('CPIs', bundle_filename)
    
    with gzip.open(bundle_path, 'wt', encoding='utf-8') as f:
        json.dump(cpi_bundle, f, indent=2)
    
    print(f"\nBundle generation complete! Saved to {bundle_path}")
    print(f"Total CPIs in bundle: {len(cpi_bundle)}")
    
    return bundle_path

def ensure_directory(directory):
    """Create directory if it doesn't exist"""
    if not os.path.exists(directory):
        os.makedirs(directory)