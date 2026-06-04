# Validation Results — PACO

This folder contains the **results and analysis notebooks** associated with the tool paper
**“PACO: A Petri Net-Based Tool for Designing, Simulating, and Analyzing Multi-objective Stochastic Processes”** (PETRI NETS 2026, LNCS 16567, pp. 335–346 — [doi:10.1007/978-3-032-27879-1_16](https://doi.org/10.1007/978-3-032-27879-1_16)),
whose formal foundations are given in **“Reactive Synthesis for Expected Impacts”** (EPTCS 409, pp. 35–52, 2024 — [doi:10.4204/EPTCS.409.7](https://doi.org/10.4204/EPTCS.409.7)).

It includes all experimental outputs, SQLite databases, and Jupyter notebooks used to reproduce the figures and tables presented in the paper.

---

## Folder Overview
```
validation/results/
├── benchmarks_our.sqlite # Results produced by our synthesis & explainer tool
├── benchmarks_prism.sqlite # Reference results obtained from PRISM
├── Validation_Expalining_Strategies_for_Expected_Impacts.ipynb # Main analysis notebook
```

 **`benchmarks_our.sqlite`** – Results from the proposed BPMN+CPI strategy synthesis algorithm and explainer.  
- **`benchmarks_prism.sqlite`** – Results from the PRISM model checker for comparison.  
- **`Validation_Expalining_Strategies_for_Expected_Impacts.ipynb`** – The notebook that aggregates, compares, and visualizes the results.  

---

## Purpose

This section of the repository is used to:

- Compare performance between our tool and PRISM;  
- Generate plots and tables used in the paper;  
- Allow external users to replicate the validation pipeline easily.

---

## Running the Notebook

> **Note:** Unlike other components of the project, the **result analysis notebook** can be safely run **outside Docker**.  

### Run locally
```bash
cd validation/results
jupyter notebook 
```

## Dependencies

The notebook uses:

- pandas for database loading and analysis;

- matplotlib and seaborn for visualization;

- sqlite3 (built-in) for database access;

- numpy for numerical processing.

If you are running outside Docker, install these manually:
```
pip install pandas matplotlib seaborn numpy jupyter
```

# Notes

Do not edit the SQLite databases directly.

For reproducibility, always ensure the notebook uses the **correct paths** to the databases.