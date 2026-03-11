# RESPISE
![Build Status](https://github.com/danielamadori/PACO/actions/workflows/tests.yml/badge.svg)
![License](https://img.shields.io/github/license/danielamadori/PACO)
![Docker Pulls](https://img.shields.io/docker/pulls/danielamadori/paco)
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![GitHub release (latest by date)](https://img.shields.io/github/v/release/danielamadori/PACO)
![GitHub issues](https://img.shields.io/github/issues/danielamadori/PACO)
![GitHub pull requests](https://img.shields.io/github/issues-pr/danielamadori/PACO)
![GitHub contributors](https://img.shields.io/github/contributors/danielamadori/PACO)


## Strategy finder for *BPMN + CPI*

## Features

- Models complex business processes with probabilistic decision points
- Provides a strategy synthesis algorithm for BPMN+CPI diagrams
- Web-based interface using Dash for visualizations

## Description

In the context of increasingly complex business processes, accurately modeling decision points, their probabilities, and resource utilization is essential for optimizing operations. To tackle this challenge, we propose an extension to the Business Process Model and Notation (BPMN) called BPMN+CPI. This extension incorporates choices, probabilities, and impacts, emphasizing precise control in business process management. Our approach introduces a timeline-based semantics for BPMN+CPI, allowing for the analysis of process flows and decision points over time. Notably, we assume that all costs, energies, and resources are positive and exhibit additive characteristics, leading to favorable computational properties. Real-world examples demonstrate the role of probabilistic decision models in resource management.

### Solver
RESPISE is an algorithm that given a *BPMN + CPI*  diagram and a bound impact vector can determine if there exists a feasible strategy such that the process can be completed while remaining under the bound vector. Moreover, We explain the synthesized strategies to users by labeling choice gateways in the BPMN diagram, making the strategies more interpretable and actionable.
![alt text](image.png)

### Usage
To set up the project (install dependencies or build Docker image), you can use the automated scripts:

- **Linux/macOS**: `./run.sh` (use `--docker` for Docker mode)
- **Windows**: `.\run.bat` (use `--docker` for Docker mode)

Please refer to the [Installation and Usage Documentation](docs/installation_and_usage.md) for detailed instructions and all available options.


### Validation / CPI Generation / PRISM Benchmarking

#### Generate CPI processes
Go to `validation/CPI_generation/` (inside Docker or native environment), install dependencies, and run the notebook / scripts to generate synthetic CPI bundles.
This outputs CPI bundles into `validation/CPI_generation/generated_processes/`.

#### Translate CPI to PRISM / run benchmarks
Navigate to `validation/cpi-to-prism/`. Make sure PRISM is available (e.g. binaries included or installed).
Run:
```
chmod +x run_benchmark.sh
./run_benchmark.sh
```

This will convert CPI bundles into PRISM models, run PRISM on them, and store results (e.g. into SQLite database, logs).

> ⚠️ **CPIs:**  
> The folders `validation/cpi-to-prism/CPIs` and `tool/CPIs` are intended to contain the **same set of CPI files**.  
> Currently, **only** the folder `validation/cpi-to-prism/CPIs` includes all the CPI instances used in the experiments, due to storage constraints.  
>
> To use these CPIs within the tool, simply **copy** the contents of  
> `validation/cpi-to-prism/CPIs` → `tool/CPIs`.
>
>
> This ensures both components (the tool and the validation pipeline) operate on the same CPI set.


### Analyze results
The generated results are stored in `validation/results/` (e.g. benchmarks_our.sqlite, benchmarks_prism.sqlite) along with the analysis notebook (e.g. Validation_Expalining_Strategies_for_Expected_Impacts.ipynb).
You can open that notebook (locally or via Jupyter) to reproduce plots, tables, and comparisons.

## Configuration & Dependencies

Python version: 3.12+ (as indicated in the original README) 


Dependencies: each submodule (tool, cpi-to-prism, CPI_generation) has a requirements.txt with needed Python packages.

PRISM: version 4.8.1 or higher (binaries should be placed into `cpi-to-prism/prism-*` folders). 


Other external tools / libraries (e.g. for GUI, matplotlib, etc.) as per the requirements files.

Ensure file system permissions allow execution of shell scripts (chmod +x).

Ensure Docker is installed and functioning (if using Docker).

## Results & Output

Benchmark output from the tool component: logs, result files, possibly intermediate strategy / model artifacts.

### Validation / Results:

- `validation/results/benchmarks_our.sqlite`

- `validation/results/benchmarks_prism.sqlite`

- Final analysis notebook: `Validation_Expalining_Strategies_for_Expected_Impacts.ipynb`

CPI generation outputs: in `validation/CPI_generation/CPIs/`

Intermediate model / log data in validation/cpi-to-prism/ (e.g. PRISM models, CPIs, database files)


## Contributing

If you want to contribute to RESPISE, you can create your own branch and start programming.

## License

Licensed under MIT license.
