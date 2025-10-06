---
title: Installation and Usage
layout: default
---

{% include navbar.html %}

# Installation and Usage

## Prerequisites

To run the application, you can use either **Python** or **Docker**. Only one of these is required.

- **Python 3.12+**
- **Docker**

To install **Python**, follow the instructions on [Python's official website](https://www.python.org/downloads/). For **Docker**, you can find installation steps on [Docker's official website](https://docs.docker.com/get-docker/).

---

## Quick Start

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

### Verifying the Tree-Expansion Helper

The `tree_expansion.ipynb` notebook defines the `get_active_decision_transition` helper that drives execution-tree exploration.
You can run the dedicated regression tests from the repository root to confirm the helper behaves as expected:

```bash
pytest tests/test_tree_expansion_utils.py
```

The test suite loads the helper directly from the notebook and exercises representative Petri-net markings (ready, not ready, and invalid inputs).
All tests must pass before relying on notebook changes.

## Installation
1. Clone the repository with submodules:
    ```bash
    git clone --recurse-submodules https://github.com/danielamadori/PACO.git
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
3. Run the **PACO server**:
    ```bash
    python3 src
    ```
   - Open a browser and navigate to `http://127.0.0.1:8050` to view the app.
   - Open a browser and navigate to `http://127.0.0.1:8000` to access the application via REST API.
   - The docs are available at `http://127.0.0.1:8000/docs`

3. Run the **jupyter notebook**:
    ```bash
    jupyter notebook --port=8888
    ```
4. Open another browser tab and go to `http://127.0.0.1:8888` to access the Jupyter environment.
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
    .\\run_benchmark.bat
    ```

After execution, benchmark results and logs will be generated in the main directory:

- `benchmarks.sqlite` – Benchmark results database
- `benchmarks_output.log` – Detailed benchmark execution log
