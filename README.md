# PACO

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

- Models complex business processes with probabilistic decision points (BPMN+CPI), with a formal semantics given by **Synchronous Probabilistic Impactful Networks (SPIN)**, an enriched Petri net model
- Provides an **on-the-fly strategy synthesis** algorithm for BPMN+CPI diagrams, with multi-dimensional bound vectors over positive cumulative impacts (cost, energy, time, risk, ...)
- **Explains** synthesized strategies by decomposing them into *minimal decision trees* attached to individual choices, using *impact-based* explainers with automatic fallback to *decision-based* ones
- **Interactive simulator** for step-by-step execution, what-if analysis, and strategy-guided decision making
- **LLM-assisted process design**: translates natural-language descriptions into syntactically valid BPMN+CPI models (always validated by the parser)
- Web-based interface using Dash for visualizations

## Description

In the context of increasingly complex business processes, accurately modeling decision points, their probabilities, and resource utilization is essential for optimizing operations. To tackle this challenge, we propose an extension to the Business Process Model and Notation (BPMN) called BPMN+CPI. This extension incorporates choices, probabilities, and impacts, emphasizing precise control in business process management. Our approach introduces a timeline-based semantics for BPMN+CPI, allowing for the analysis of process flows and decision points over time. Notably, we assume that all costs, energies, and resources are positive and exhibit additive characteristics, leading to favorable computational properties. Real-world examples demonstrate the role of probabilistic decision models in resource management.

### Solver

PACO is tool that given a *BPMN + CPI*  diagram and a bound impact vector can determine if there exists a feasible strategy such that the process can be completed while remaining under the bound vector. Moreover, We explain the synthesized strategies to users by labeling choice gateways in the BPMN diagram, making the strategies more interpretable and actionable.
![alt text](image.png)

### Usage

To set up the project (install dependencies or build Docker image), you can use the automated scripts:

- **Linux/macOS**: `./run.sh` (use `--docker` for Docker mode)
- **Windows**: `.\run.bat` (use `--docker` for Docker mode)

Please refer to the [Installation and Usage Documentation](docs/installation_and_usage.md) for detailed instructions and all available options.


### Validation / CPI Generation / PRISM Benchmarking

#### Generate CPI processes
Go to `validation/CPI_generation/` (inside Docker or native environment), install dependencies, and run the notebook / scripts to generate synthetic CPI bundles.
This generates process templates in `validation/CPI_generation/generated_processes/` and CPI bundles in `validation/cpi-to-prism/CPIs/`.

#### Translate CPI to PRISM / run benchmarks
Navigate to `validation/cpi-to-prism/`. Make sure PRISM is available (e.g. binaries included or installed).

> ⚠️ **BPMN+CPI TO PRISM & SPIN TO PRISM Translations**  
> For the ecoding details please refer to: 
> * Check [BPMN+CPI → PRISM translation](validation/cpi-to-prism/cpi_to_prism_translation.md) for the translation of BPMN+CPI processes into PRISM (and so STORM) MDPs.
> * Check [SPIN → PRISM translation](validation/cpi-to-prism/spin_to_prism_translation.md) for the translation of BPMN+CPI processes into PRISM (and so STORM) MDPs.

Run:
```
chmod +x run_benchmark.sh
./run_benchmark.sh
```

This will convert CPI bundles into PRISM models, run PRISM on them, and store results (e.g. into SQLite database, logs).

> ⚠️ **CPIs:**  
> The canonical CPI dataset used by experiments is in `validation/cpi-to-prism/CPIs`.  
> The generation pipeline and benchmark pipeline both read/write from this folder.


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

CPI generation outputs: in `validation/cpi-to-prism/CPIs/`

Intermediate model / log data in validation/cpi-to-prism/ (e.g. PRISM models, CPIs, database files)


## Citation

If you use PACO in your research, please cite the tool paper:

> Chini, E., Amadori, D., Sala, P., Nasir Rajput, S., Baldi, M., Cappelletti, M.:
> *PACO: A Petri Net-Based Tool for Designing, Simulating, and Analyzing Multi-objective Stochastic Processes.*
> In: Desel, J., Kalenkova, A. (eds.) Application and Theory of Petri Nets and Concurrency.
> PETRI NETS 2026. LNCS, vol. 16567, pp. 335–346. Springer, Cham (2026).
> [doi:10.1007/978-3-032-27879-1_16](https://doi.org/10.1007/978-3-032-27879-1_16)

```bibtex
@inproceedings{chini2026paco,
  author    = {Chini, Emanuele and Amadori, Daniel and Sala, Pietro and Nasir Rajput, Sidra and Baldi, Matteo and Cappelletti, Mattia},
  title     = {{PACO}: A {Petri} Net-Based Tool for Designing, Simulating, and Analyzing Multi-objective Stochastic Processes},
  booktitle = {Application and Theory of Petri Nets and Concurrency},
  editor    = {Desel, J{\"o}rg and Kalenkova, Anna},
  series    = {Lecture Notes in Computer Science},
  volume    = {16567},
  pages     = {335--346},
  publisher = {Springer},
  address   = {Cham},
  year      = {2026},
  doi       = {10.1007/978-3-032-27879-1_16},
  note      = {47th International Conference, PETRI NETS 2026, Hamburg, Germany, June 22--26, 2026}
}
```

The formal foundations (semantics and synthesis problem) are described in the companion paper, presented at **GandALF 2024** (*Games, Automata, Logics, and Formal Verification*):

> Chini, E., Sala, P., Simonetti, A., Zare, O.:
> *Reactive Synthesis for Expected Impacts.* In: Proceedings of GandALF 2024.
> EPTCS, vol. 409, pp. 35–52 (2024).
> [doi:10.4204/EPTCS.409.7](https://doi.org/10.4204/EPTCS.409.7) — arXiv:[2410.22760](https://arxiv.org/abs/2410.22760)

```bibtex
@inproceedings{chini2024reactive,
  author    = {Chini, Emanuele and Sala, Pietro and Simonetti, Andrea and Zare, Omid},
  title     = {Reactive Synthesis for Expected Impacts},
  booktitle = {Proceedings of the 15th International Symposium on Games, Automata, Logics, and Formal Verification (GandALF 2024)},
  series    = {Electronic Proceedings in Theoretical Computer Science (EPTCS)},
  volume    = {409},
  pages     = {35--52},
  year      = {2024},
  doi       = {10.4204/EPTCS.409.7}
}
```

## Acknowledgements — Upstream Project

This repository is an extended fork of the PACO project by
**Emanuele Chini, Pietro Sala, Andrea Simonetti, and Omid Zare**
([ansimonetti/PACO](https://github.com/ansimonetti/PACO)).

The upstream project implements the *strategy-existence* algorithm (the **solver**) introduced in the
GandALF 2024 paper *Reactive Synthesis for Expected Impacts* (see the [Citation](#citation) section).
Building on that core, this fork extends PACO into a full **web-based, multi-objective tool**, adding:

- the **explainer** module (minimal decision trees: impact-based / decision-based),
- the **interactive simulator** ([`simulator/`](simulator/)),
- the **LLM-assisted process design** component ([`src/ai/`](src/ai/)),
- the **Dash web application** and REST APIs ([`src/`](src/), [`gui/`](gui/)),
- the **validation pipeline** (BPMN+CPI → PRISM/STORM translation, synthetic CPI generation, benchmarks — [`validation/`](validation/)).

This extended tool is the one described in the PETRI NETS 2026 tool paper.

## Contributing

If you want to contribute to PACO, you can create your own branch and start programming.

## License

Licensed under MIT license.
