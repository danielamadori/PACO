---
title: Home
layout: default
---
## Tool for Designing, Simulating, and Analyzing Multi-objective Stochastic Processes

## Features

- Models complex business processes with probabilistic decision points
- Provides a strategy synthesis algorithm for BPMN+CPI diagrams
- Web-based interface using Dash for visualizations

## Description

In the context of increasingly complex business processes, accurately modeling decision points, their probabilities, and resource utilization is essential for optimizing operations. To tackle this challenge, we propose an extension to the Business Process Model and Notation (BPMN) called BPMN+CPI. This extension incorporates choices, probabilities, and impacts, emphasizing precise control in business process management. Our approach introduces a timeline-based semantics for BPMN+CPI, allowing for the analysis of process flows and decision points over time. Notably, we assume that all costs, energies, and resources are positive and exhibit additive characteristics, leading to favorable computational properties. Real-world examples demonstrate the role of probabilistic decision models in resource management.

### Solver

PACO is an algorithm that given a *BPMN + CPI*  diagram and a bound impact vector can determine if there exists a feasible strategy such that the process can be completed while remaining under the bound vector. Moreover, We explain the synthesized strategies to users by labeling choice gateways in the BPMN diagram, making the strategies more interpretable and actionable.

## Authors

* **Daniel Amadori**
* **Emanuele Chini**
* **Pietro Sala**
* **Sidra Nasir Rajput**
* **Matteo Baldi**
* **Mattia Cappelletti**

## Publication

PACO was published as a tool paper at **PETRI NETS 2026**:

> Chini, E., Amadori, D., Sala, P., Nasir Rajput, S., Baldi, M., Cappelletti, M.:
> *PACO: A Petri Net-Based Tool for Designing, Simulating, and Analyzing Multi-objective Stochastic Processes.*
> In: Desel, J., Kalenkova, A. (eds.) Application and Theory of Petri Nets and Concurrency.
> LNCS, vol. 16567, pp. 335–346. Springer, Cham (2026).
> [doi:10.1007/978-3-032-27879-1_16](https://doi.org/10.1007/978-3-032-27879-1_16)

The formal foundations are described in the companion paper *Reactive Synthesis for Expected Impacts* (EPTCS 409, pp. 35–52, 2024 — [doi:10.4204/EPTCS.409.7](https://doi.org/10.4204/EPTCS.409.7)).

## Acknowledgements — Upstream Project

This tool is an extended fork of the PACO project by **Emanuele Chini, Pietro Sala, Andrea Simonetti, and Omid Zare** ([ansimonetti/PACO](https://github.com/ansimonetti/PACO)), which implements the strategy-existence solver introduced in the GandALF 2024 paper *Reactive Synthesis for Expected Impacts*. This fork extends it with the explainer, interactive simulator, LLM-assisted design, web application, and validation pipeline described in the PETRI NETS 2026 tool paper.

## Contributing

If you want to contribute to PACO, you can create your own branch and start programming.

## License

Licensed under MIT license.
