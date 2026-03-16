import json
import os
from pathlib import Path
from cpi_to_spin.cpitospin import CPIToSPINConverter
from process_to_prism import cpi_to_mdp

def _find_cpi_to_prism_root(start: Path) -> Path:
    for parent in start.parents:
        if parent.name == "cpi-to-prism":
            return parent
    raise RuntimeError(f"Unable to locate cpi-to-prism root from {start}")

_CPI_TO_PRISM_DIR = _find_cpi_to_prism_root(Path(__file__).resolve())
_CPIS_DIR = _CPI_TO_PRISM_DIR / "CPIs"


def cpi_to_model(filename):
    """
    Converts a CPI file to a PRISM model and saves it in the models subfolder.
    
    Args:
        filename (str): Name of the CPI file (with or without .cpi extension)
        include_rewards (bool): Whether to include reward structures in the output (default: True)
        
    Returns:
        str: Path to the generated model file, or None if there was an error
        
    Example:
        convert_cpi_to_prism("test")  # Converts CPIs/test.cpi to models/test.nm
        convert_cpi_to_prism("test", include_rewards=False)  # Converts without reward structures
    """
    # Ensure models directory exists
    os.makedirs('models', exist_ok=True)
    
    # Handle filename with or without extension
    base_name = filename.replace('.cpi', '')
    input_path = _CPIS_DIR / f'{base_name}.cpi'
    output_path = Path('models') / f'{base_name}.nm'
    
    try:
        # Read CPI file
        with open(input_path, 'r') as f:
            cpi_dict = json.load(f)

        try:
            prism_model = cpi_to_mdp(cpi_dict)
        except ValueError as e:
            #print(f"Loops detected in CPI file {input_path}: {str(e)}")
            
            spin_model = CPIToSPINConverter().convert_cpi_to_spin(cpi_dict)
            prism_model = spin_model.generate_prism_model()

        with open(output_path, 'w') as f:
            f.write(prism_model)
            
        print(f"Successfully converted {input_path} to {output_path}")
        return output_path
        
    except FileNotFoundError:
        print(f"Error: Could not find input file {input_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: {input_path} is not a valid JSON file")
        return None
    except Exception as e:
        print(f"Error converting {input_path}: {str(e)}")
        return None
