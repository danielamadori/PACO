# Synthetic CPI generation
![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![GitHub issues](https://img.shields.io/github/issues/danielamadori/synthetic-cpi-generation)
![GitHub pull requests](https://img.shields.io/github/issues-pr/danielamadori/synthetic-cpi-generation)
![GitHub contributors](https://img.shields.io/github/contributors/danielamadori/synthetic-cpi-generation)


## Description
This repository contains the code and resources for generating synthetic data as described in the validation section of the paper.  
By executing the main file, it is possible to reproduce all the synthetic datasets used in the validation. The `CPIs` folder contains all the BPMN+CPI models employed in the experiments.  
It should be noted, however, that the BPMN+CPI models are generated randomly within their respective complexity classes (i.e., the values of MNXN and MIX remain fixed, while the processes are generated randomly within the same complexity class).  
The generation method is run as described in the Section 5.

## Prerequisites

- **Python 3.12+**

To install **Python**, follow the instructions on [Python's official website](https://www.python.org/downloads/).

---

## Quick Start

### Using Python
To start the application using Python, follow these steps:
1. **Environment Setup**
- **Using Conda**
    ```bash
    conda create --name cpi python=3.12
    conda activate cpi
    ```
- **Using venv**
    ```bash
    python3.12 -m venv cpi_env
    source cpi_env/bin/activate  # On macOS/Linux
    cpi_env\Scripts\activate     # On Windows
    ```

2. **Install required dependencies**
    ```bash
    pip install -r requirements.txt
    ```
   
3. **Running the `main.ipynb` Notebook**
   To start the `main.ipynb` notebook, use the following command:
    ```bash
    jupyter notebook --port=8888
    ```
    Open a browser and go to `http://127.0.0.1:8888` to access the Jupyter environment and select the `main.ipynb` notebook, open it and run it.

---

## Output
The generated bundle will be saved in the `CPI_generation/CPIs` folder.
