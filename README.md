# Graph Coloring Algorithms - Comprehensive Implementation

A rigorous implementation and analysis of four graph coloring algorithms for the Algorithm Analysis & Design final project.

## Project Overview

This project implements four distinct algorithms for the NP-hard graph coloring problem:
1. **Welsh-Powell** - Greedy algorithm with degree-based ordering
2. **D-Satur (Degree of Saturation)** - Enhanced greedy algorithm considering neighbor constraints
3. **Simulated Annealing** - Metaheuristic optimization algorithm
4. **Dynamic Programming with Backtracking** - Exact algorithm for optimal coloring

Each algorithm is implemented **from scratch** using only standard Python data structures (no external graph coloring libraries).

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Algorithms](#algorithms)
- [Benchmarking](#benchmarking)
- [Results & Analysis](#results--analysis)

## Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd graph-coloring-project

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Dependency Installation

```bash
# Install required packages
pip install networkx matplotlib numpy

# Optional: for geographic visualization (world map coloring)
pip install geopandas shapely
```

## Project Structure

```
graph-coloring-project/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── Makefile                           # Build and test automation
├── src/
│   ├── __init__.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── welshpowell.py            # Welsh-Powell algorithm
│   │   ├── dsatur.py                 # D-Satur algorithm
│   │   ├── simulated_annealing.py    # Simulated Annealing
│   │   └── dynamic_programming.py    # DP with backtracking
│   └── utils/
│       ├── __init__.py
│       ├── graph_generator.py        # Synthetic graph generation
│       ├── graph_loader.py           # Load graphs from files
│       └── visualizer.py             # Plotting and visualization
├── benchmarking/
│   ├── __init__.py
│   ├── config.py                     # Experiment configuration
│   ├── run_experiments.py            # Main benchmarking script
│   └── test_correctness.py           # Unit tests
├── data/
│   ├── dimacs/                       # DIMACS benchmark graphs
│   └── real-world/                   # Real-world datasets
└── results/
    ├── data/                         # CSV/JSON results
    └── plots/                        # Generated charts and visualizations
```

## Usage

### Running Tests

Verify algorithm correctness on known graphs:

```bash
# Run all unit tests
python -m benchmarking.test_correctness

# Or use make
make test
```

Expected output:
```
============================================================
GRAPH COLORING ALGORITHM CORRECTNESS TESTS
============================================================

=== Test: Triangle (K3) ===
✓ Welsh-Powell: 3 colors (correct)
✓ D-Satur: 3 colors (correct)
✓ Dynamic Programming: 3 colors (optimal)

... (more tests)

✓ ALL TESTS PASSED
```

### Running Benchmarks

Execute comprehensive performance benchmarks:

```bash
# Run all benchmarks
python benchmarking/run_experiments.py

# Or use make
make benchmark
```

This will:
- Test all algorithms on various graph sizes (10-30 vertices)
- Test on graphs with different densities (p = 0.2 to 0.7)
- Measure execution time and color count
- Save results to `results/data/benchmark_results.csv`
- Generate comparison plots

### Using Algorithms Directly

```python
import networkx as nx
from src.algorithms.welshpowell import welsh_powell
from src.algorithms.dsatur import dsatur
from src.algorithms.simulated_annealing import simulated_annealing
from src.algorithms.dynamic_programming import find_chromatic_number
from src.utils.graph_generator import generate_erdos_renyi_graph

# Create a test graph
G = generate_erdos_renyi_graph(n=20, p=0.3, seed=42)

# Welsh-Powell
coloring_wp, k_wp = welsh_powell(G)
print(f"Welsh-Powell used {k_wp} colors")

# D-Satur
coloring_ds, k_ds = dsatur(G)
print(f"D-Satur used {k_ds} colors")

# Simulated Annealing
coloring_sa, k_sa, history, time_s = simulated_annealing(
    G, initial_num_colors=5, T0=10.0, alpha=0.99, max_iterations=100000
)
print(f"SA used {k_sa} colors in {time_s:.3f} seconds")

# Dynamic Programming (for small graphs)
if G.number_of_nodes() <= 15:
    chromatic_num, coloring_dp = find_chromatic_number(G)
    print(f"DP found chromatic number: {chromatic_num}")
```

## Algorithms

### 1. Welsh-Powell (Greedy)

**Complexity:**
- Time: O(V² + E)
- Space: O(V)

**Characteristics:**
- Simple greedy algorithm
- Orders vertices by degree (highest first)
- Colors vertices sequentially with smallest available color
- No guarantee of optimal solution
- Fast and predictable

**Reference:** Welsh & Powell (1967)

### 2. D-Satur (Enhanced Greedy)

**Complexity:**
- Time: O(V²)
- Space: O(V)

**Characteristics:**
- Considers "saturation degree" (distinct colors used by neighbors)
- Prioritizes vertices with more constraints
- Generally produces better colorings than Welsh-Powell
- Still fast with better quality
- Heuristic, not exact

**Reference:** Brélaz (1979)

### 3. Simulated Annealing (Metaheuristic)

**Complexity:**
- Time: O(max_iterations × E)
- Space: O(V)

**Characteristics:**
- Probabilistic algorithm inspired by metallurgical annealing
- Accepts worse solutions with decreasing probability (escapes local optima)
- Temperature cooling schedule controls exploration vs. exploitation
- Can find better solutions than greedy algorithms
- Requires parameter tuning (T₀, α, iterations)
- Slower but potentially better quality

**Reference:** Kirkpatrick et al. (1983)

### 4. Dynamic Programming with Backtracking (Exact)

**Complexity:**
- Time: O(k^V) worst case, where k is chromatic number
- Space: O(V) recursion stack

**Characteristics:**
- Guarantees optimal solution (chromatic number)
- Uses backtracking with branch-and-bound optimizations
- Practical only for small graphs (≤15-20 vertices)
- Exponential time complexity
- Lower and upper bounds used for pruning search space

**Optimizations:**
- Vertex ordering by degree (descending)
- Clique-based lower bound
- Early termination when optimal found

## Benchmarking

### Running the Benchmark Suite

```bash
make benchmark
```

### Configuration

Edit `benchmarking/config.py` to customize:

```python
# Graph sizes to test
GRAPH_SIZES = [10, 15, 20, 25, 30]

# Edge probabilities (density)
EDGE_PROBABILITIES = [0.2, 0.3, 0.5, 0.7]

# Simulated Annealing parameters
SA_INITIAL_TEMP = 10.0
SA_COOLING_RATE = 0.99
SA_MAX_ITERATIONS = 100000

# Dynamic Programming limits
DP_MAX_VERTICES = 15  # Don't run DP on larger graphs
```

### Interpreting Results

Results are saved to:
- **CSV**: `results/data/benchmark_results.csv`
- **JSON**: `results/data/benchmark_results.json`

Each row contains:
- `algorithm`: Algorithm name
- `graph_type`: Type of graph tested
- `nodes`: Number of vertices
- `edges`: Number of edges
- `colors`: Number of colors used
- `time_ms`: Execution time in milliseconds
- `valid`: Whether coloring is valid
- `conflicts`: Number of edge conflicts (for SA)

## Results & Analysis

### Key Findings

1. **Solution Quality**: D-Satur and Simulated Annealing produce better solutions than Welsh-Powell on most graphs

2. **Execution Time**: 
   - Welsh-Powell: O(V²) - fastest
   - D-Satur: O(V²) - slightly slower than WP
   - Simulated Annealing: Depends on parameters, generally 10-1000× slower
   - Dynamic Programming: Exponential, only for V ≤ 15

3. **Graph Density Effect**:
   - Denser graphs: More colors needed
   - Sparser graphs: Algorithms perform better

4. **Scalability**:
   - Greedy: O(n²) scales to thousands of vertices
   - SA: O(n × iterations) practical for n ≤ 100-1000
   - DP: Only practical for n ≤ 15

### Visualizations

After running benchmarks, view plots in `results/plots/`:

```bash
# View specific plots
open results/plots/algorithm_comparison_colors.png
open results/plots/algorithm_comparison_time.png
open results/plots/convergence_simulated_annealing.png
```

## Code Quality

### Standards Followed

✓ **From-Scratch Requirement**: All core algorithm logic implemented without external libraries
✓ **Docstrings**: Every function has comprehensive docstring with args, returns, complexity
✓ **Type Hints**: All functions use Python type hints
✓ **Comments**: Complex sections well-commented
✓ **Modularity**: Each algorithm in separate file with helper utilities
✓ **Testing**: Unit tests for correctness on known graphs
✓ **Reproducibility**: Seeds for random number generation, saved configuration

### Code Structure

Each algorithm module includes:
- Main algorithm function with docstring
- Input validation
- Result validation helper
- Statistics computation
- Example usage

## Make Commands

```bash
# Run all tests
make test

# Run benchmarks
make benchmark

# Clean up generated files
make clean

# Run everything
make all
```

## Troubleshooting

### ImportError: No module named 'networkx'
```bash
pip install networkx
```

### Tests fail on D-Satur
Ensure all neighbors are processed before checking color availability.

### Benchmarks run slowly
- Reduce `MAX_ITERATIONS` in `config.py`
- Use smaller `GRAPH_SIZES`
- Skip Dynamic Programming for large graphs

### Memory errors
- Reduce `GRAPH_SIZES` (maximum size causes memory issues)
- Run tests individually instead of full suite

## References

1. Welsh, D. J. W., and Powell, M. B. (1967). "An upper bound for the chromatic number of a graph and its application to timetabling problems." Journal of the Combinatorial Society, 4(1), 25-29.

2. Brélaz, D. (1979). "New methods to color the vertices of a graph." Communications of the ACM, 22(4), 251-256.

3. Kirkpatrick, S., Gelatt Jr, C. D., and Vecchi, M. P. (1983). "Optimization by simulated annealing." Science, 220(4598), 671-680.

4. NetworkX Documentation: https://networkx.org/

## Team & Contact

**Algorithm Analysis & Design Final Project**
- Implemented by: Algorithm Analysis & Design Team
- Course: Algorithm Analysis & Design
- Date: Fall 2024

## License

This project is provided as-is for educational purposes.
