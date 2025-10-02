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



## Installation
1. Clone the repository with submodules:
    ```bash
    git clone --recurse-submodules https://github.com/matthewexe/PACO.git
    ```
2. Create a `.env` file in the root directory. You can copy the example file:
    ```bash
    cp .env.example .env
    ```
   
### Manage Submodules
- Initializing (if you did not use `--recurse-submodules` when cloning)
    ```bash
    git submodule init
    git submodule update
    ```
- Update (to get the latest version of the submodules)
    ```bash
    git submodule update --remote
    ```

## Starting the Application
You can start the application using either **Docker** or **Python**. Choose one of the methods below.
### Using Docker

To start the application using Docker, follow these steps:

1. Pull and start the Docker:
    ```bash
    docker pull danielamadori/paco:latest
    docker run -d -p 8000:8000 -p 8050:8050 -p 8888:8888 -p 8001:8001 -it --name PACO danielamadori/paco:latest
    docker logs PACO
    ```
   Note: Replace latest with a specific version number if needed.

2. Open a browser and navigate to `http://127.0.0.1:8050` to view the app.
3. Open a browser and navigate to `http://127.0.0.1:8000` to access the application via REST API.
   The docs are available at `http://127.0.0.1:8000/docs`
4. Open browser and navigate to `http://127.0.0.1:8001/docs` to access the BPMN-CPI Simulator API documentation.
5. Open another browser tab and go to `http://127.0.0.1:8888` to access the Jupyter environment.  
   You will find multiple `.ipynb` notebooks available — **we recommend [starting with `tutorial.ipynb`](https://nbviewer.org/github/danielamadori/PACO/blob/main/tutorial.ipynb)**, which provides a guided walkthrough of the main functionalities.


### Usage
#link to installation and usage
You can find the installation and usage instructions [here](docs/installation_and_usage.md).

## Authors

* **Daniel Amadori**
* **Emanuele Chini**
* **Pietro Sala**
* **Andrea Simonetti**
* **Omid Zare**

## Contributing

If you want to contribute to RESPISE, you can create your own branch and start programming.

## License

Licensed under MIT license.