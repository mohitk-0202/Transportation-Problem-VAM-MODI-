# Transportation-Problem-VAM-MODI-
Python implementations of classic Operations Research algorithms. Features a Big-M Simplex solver for constrained Linear Programming Problems (LPP) and a complete Transportation Problem solver using VAM, MODI, and automated Stepping Stone iterative improvement.
# Operations Research Optimization Solvers

This repository contains Python implementations of two well-known optimization algorithms used in Operations Research and Supply Chain Management. These scripts were developed to algorithmically handle both standard and degenerate optimization problems from scratch, without relying on external optimization libraries like SciPy.

## 🚀 Features

### 1. Big-M Simplex Method (Linear Programming)
A computationally rigorous solver for constrained Linear Programming Problems (LPP). 
* **Standard Form Conversion:** Automatically accommodates $\ge$, $\le$, and $=$ constraints by integrating appropriate slack, surplus, and artificial variables.
* **Algorithmic Penalty:** Applies the "Big-M" mathematical penalty to artificial variables to force them out of the basic feasible solution.
* **Tableau Iteration:** Performs automated pivot operations to iteratively locate the optimal decision-variable values and minimum/maximum objective-function value.

### 2. Transportation Problem Solver (VAM + MODI)
A fully interactive, end-to-end solver for transportation and logistics optimization.
* **Auto-Balancing:** Detects unbalanced supply/demand scenarios and mathematically injects dummy rows or columns with zero transportation costs.
* **Phase 1 (VAM):** Utilizes Vogel's Approximation Method to generate a highly efficient Initial Basic Feasible Solution (IBFS) based on row and column penalty costs.
* **Phase 2 (MODI):** Implements the Modified Distribution (MODI) method to calculate $u_i$ and $v_j$ potentials and test the opportunity costs ($d_{ij}$) of all non-basic cells.
* **Phase 3 (Stepping Stone Improvement):** Automatically traces rectangular closed-loop paths (using Breadth-First Search logic) to shift unit allocations from expensive routes to cheaper ones, iterating until mathematical optimality is proven.
* **Robust Degeneracy Handling:** Employs a Union-Find algorithm to detect degenerate Initial Basic Feasible Solutions (where allocations $< m + n - 1$) and strategically places zero-value allocations to preserve the basis without creating invalid cycles.

<img width="1600" height="1041" alt="image" src="https://github.com/user-attachments/assets/ae9a9483-6114-4b04-8c99-de3fa5fb6006" />

<img width="1600" height="1041" alt="image" src="https://github.com/user-attachments/assets/ccc025ed-f19b-40cd-a31f-0e9426f1afff" />
