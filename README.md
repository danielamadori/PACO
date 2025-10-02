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

## Prerequisites

To run the application, you can use either **Python** or **Docker**. Only one of these is required.

- **Python 3.12+**
- **Docker**

To install **Python**, follow the instructions on [Python's official website](https://www.python.org/downloads/). For **Docker**, you can find installation steps on [Docker's official website](https://docs.docker.com/get-docker/).

---

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

### Using Python
To start the application using Python, follow these steps:
1. **Environment Setup**
   - **Using Conda**
       ```bash
       conda create --name paco python=3.12
       conda activate paco
       ```
   - **Using venv**
     ```bash
     python3.12 -m venv paco_env
     source paco_env/bin/activate  # On macOS/Linux
     paco_env\Scripts\activate     # On Windows
     ```
2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3. Run the **PACO app**:
   - Only API:
   ```bash
    python3 src --api
    ```
   - GUI and API:
   ```bash
    python3 src --gui
    ```
   - Open a browser and navigate to `http://127.0.0.1:8050` to view the app.
   - Open a browser and navigate to `http://127.0.0.1:8000` to access the application via REST API. The docs are available at `http://127.0.0.1:8000/docs`
   - Open a browser and navigate to `http://127.0.0.1:8001` to access the application via BPMN-CPI Simulator API. The docs are available at `http://127.0.0.1:8001/docs`
4. Run the **jupyter notebook**:
    ```bash
    jupyter notebook --port=8888
    ```
5. Open another browser tab and go to `http://127.0.0.1:8888` to access the Jupyter environment.  
   You will find multiple `.ipynb` notebooks available — **we recommend [starting with `tutorial.ipynb`](https://nbviewer.org/github/danielamadori/PACO/blob/main/tutorial.ipynb)**, which provides a guided walkthrough of the main functionalities.

---
NB! This application is currently under development. There may be some issues and bugs.


## Running Benchmark

Ensure all dependencies are installed and your environment is correctly configured before running benchmarks.

### Preparing CPI Bundle

Place your CPI bundle into the `CPIs` folder. If you don't have a CPI bundle, you can create one by following the instructions in the repository [synthetic-cpi-generation](https://github.com/danielamadori/synthetic-cpi-generation), or you can download the pre-built bundle used in the paper for validation [here](https://univr-my.sharepoint.com/:f:/g/personal/emanuele_chini_univr_it/EuMjJi6L03lCp0e348YPAYwBMJ5jTGO1lojwuIlOAhpaaA?e=u9oXl1).

### Running the Script

Execute the benchmark script according to your operating system:

**Run the script**
- Linux
    ```bash
    chmod +x run_benchmark.sh
    ./run_benchmark.sh
    ```
- Windows
    ```batch
    .\run_benchmark.bat
    ```

After execution, benchmark results and logs will be generated in the main directory:

- `benchmarks.sqlite` – Benchmark results database
- `benchmarks_output.log` – Detailed benchmark execution log


## Authors

* **Daniel Amadori**
* **Emanuele Chini**
* **Pietro Sala**
* **Andrea Simonetti**
* **Omid Zare**

## Contributing

If you want to contribute to RESPISE, you can create your own branch and start programming.

## License

RESPISE is licensed under MIT license.