# Advanced Metrics & Analysis Guide

## Overview

The project now includes **20+ advanced metrics** for analyzing graph coloring algorithm performance beyond just "colors used" and "time taken".

## Metrics Categories

### 1. **Solution Quality Metrics**

#### Color Imbalance
- **Definition**: Measures how evenly colors are distributed
- **Formula**: `(max_freq - min_freq) / avg_freq`
- **Range**: 0 (perfectly balanced) to ∞ (very unbalanced)
- **Why It Matters**: Equal color distribution is more elegant and may indicate robustness
- **Example**: Balanced distribution {1,1,1,1} vs unbalanced {4,0,0,0}

#### Color Utilization
- **Definition**: Percentage of vertices vs. colors used
- **Formula**: `(num_colors / num_vertices) * 100`
- **Range**: 0-100%
- **Why It Matters**: High utilization means colors are efficiently used
- **Example**: Using 4 colors for 20 vertices = 20% utilization

#### Chromatic Efficiency
- **Definition**: How close solution is to optimal (if known)
- **Formula**: `optimal_chromatic / num_colors_used`
- **Range**: 0 to 1.0 (1.0 = optimal)
- **Why It Matters**: Direct measure of solution quality
- **Note**: Requires knowing optimal chromatic number

#### Achromatic Power
- **Definition**: Fraction of edges NOT forming conflicts
- **Formula**: `1 - (conflicts / total_edges)`
- **Range**: 0 to 1.0 (1.0 = valid coloring)
- **Why It Matters**: Measures overall solution "goodness" for iterative algorithms
- **Use Case**: Simulated Annealing can improve this gradually

### 2. **Conflict Analysis Metrics**

#### Conflict Density
- **Definition**: Percentage of edges with both endpoints same color
- **Formula**: `(num_conflicts / total_edges) * 100`
- **Range**: 0-100%
- **Interpretation**:
  - 0% = valid coloring (no conflicts)
  - >0% = partial/invalid coloring

#### Conflict Vertex Statistics
- **Metrics**:
  - `num_conflict_vertices`: How many vertices are involved in conflicts
  - `percent_conflict`: Percentage of vertices in conflicts
  - `avg_degree_conflict`: Average degree of conflicting vertices
  - `max_degree_conflict`: Maximum degree among conflicting vertices
- **Why It Matters**: Shows which vertices are problematic (high-degree vertices?)

### 3. **Color Class Metrics**

#### Largest Color Class
- **Definition**: Size of the largest independent set in the coloring
- **Formula**: `max(count for each color)`
- **Why It Matters**: Shows if colors are balanced or one dominant

#### Color Class Variance
- **Definition**: Statistical variance of color class sizes
- **Formula**: `variance(color_frequencies)`
- **Range**: 0 (perfectly equal) to high (very unequal)
- **Use Case**: Measure of color class balance

#### Color Class Independence
- **Definition**: Verify each color class is actually an independent set
- **Returns**: Boolean for each color
- **Why It Matters**: Validation that coloring is correct

### 4. **Graph Theory Bounds**

#### Chromatic Number Lower Bound
- **Definition**: Minimum colors definitely needed
- **Computation**: `max(clique_number, max_degree_lower_bound)`
- **Why It Matters**: Sets minimum target for any algorithm
- **Example**: Triangle (K3) has clique size 3, so χ(K3) ≥ 3

#### Chromatic Number Upper Bound
- **Definition**: Maximum colors any greedy algorithm will use
- **Formula**: `max_degree + 1`
- **Guarantee**: All greedy algorithms use ≤ this many colors
- **Why It Matters**: Sets ceiling on solution quality

#### Fractional Chromatic Number
- **Definition**: Continuous relaxation of chromatic number
- **Formula**: `n / independence_number`
- **Range**: [lower_bound, chromatic_number]
- **Why It Matters**: Shows difficulty of the graph (gap between χ and χ_f)

#### Degeneracy
- **Definition**: Smallest k such that every subgraph has vertex of degree ≤ k
- **Guarantee**: Degeneracy ordering produces coloring with ≤ degeneracy + 1 colors
- **Why It Matters**: Theoretical guarantee for degeneracy-based algorithms

## Usage Examples

### Computing Metrics for a Coloring

```python
from src.utils.metrics import compute_all_metrics
import networkx as nx
from src.algorithms.welsh_powell import welsh_powell

# Get a graph and color it
G = nx.petersen_graph()
coloring, k = welsh_powell(G)

# Compute all metrics
metrics = compute_all_metrics(
    G, 
    coloring, 
    algorithm_name='Welsh-Powell',
    execution_time_ms=0.5
)

# Access metrics
print(f"Colors used: {metrics['num_colors']}")
print(f"Conflicts: {metrics['conflicts']}")
print(f"Chromatic efficiency: {metrics['chromatic_efficiency']:.2%}")
print(f"Achromatic power: {metrics['achromatic_power']:.3f}")
```

### Running Comprehensive Analysis

```bash
# Run metrics analysis on multiple graphs
python3 -m benchmarking.metrics_analysis

# Results saved to: results/data/detailed_metrics.csv
```

## Interpreting Results

### Perfect Coloring
```
is_valid: True
conflicts: 0
conflict_density_percent: 0.0
achromatic_power: 1.0
color_class_independence: All True
```

### Good Coloring (Few Conflicts)
```
conflicts: 1-3
conflict_density_percent: < 5%
achromatic_power: 0.95+
```

### Algorithm Comparison Using Metrics

| Metric | Welsh-Powell | D-Satur | Simulated Annealing | DP |
|--------|-------------|---------|-------------------|-----|
| Colors Used | 5 | 4 | 3 | 3 |
| Conflicts | 0 | 0 | 0 | 0 |
| Time (ms) | 0.07 | 0.14 | 3102 | 0.15 |
| Color Imbalance | 0.0 | 0.2 | 0.5 | 0.2 |
| Chromatic Efficiency | 0.60 | 0.75 | 1.0 | 1.0 |

**Interpretation**:
- **DP**: Optimal (k=3), fast, but limited to small graphs
- **D-Satur**: Good quality (k=4), fast, balanced
- **Welsh-Powell**: Decent (k=5), fastest, but larger imbalance
- **SA**: Optimal if it finds best solution, very slow

## Advanced Analysis Insights

### 1. **Trade-off Analysis**
- Plot: `chromatic_efficiency` vs `execution_time_ms`
- Shows quality vs. speed trade-off
- Example: DP is fast but limited; SA is slow but finds optima

### 2. **Scalability Analysis**
- Plot: `num_colors` vs `graph_nodes` for fixed density
- Shows how algorithm scales with graph size
- Example: Some algorithms may degrade faster

### 3. **Density Sensitivity**
- Plot: `num_colors` vs `edge_probability` for fixed size
- Shows robustness to graph density
- Example: D-Satur more stable than Welsh-Powell

### 4. **Color Distribution**
- Plot: Histogram of color class sizes
- Shows evenness of distribution
- Example: A few large classes vs. many small classes

## Running Metrics Analysis

```bash
# Run comprehensive metrics analysis
cd /home/poojithajsiri/course_project/AAD/AAD_Final
python3 -m benchmarking.metrics_analysis

# Output includes:
# 1. Metrics for each graph-algorithm pair
# 2. Summary statistics
# 3. CSV export for further analysis
```

## Metrics Files Generated

- **`results/data/detailed_metrics.csv`**: Complete metrics table
  - One row per graph-algorithm combination
  - 30+ columns with different metrics
  - Ready for Excel/Python analysis

## Key Insights to Highlight in Report

1. **Chromatic Efficiency Gap**: Show how far each algorithm is from optimal
2. **Conflict Evolution**: For SA, show how conflicts decrease over time
3. **Color Class Balance**: Demonstrate which algorithms produce more balanced distributions
4. **Scalability**: Show performance degradation with graph size
5. **Density Sensitivity**: Show how algorithm performance changes with edge density

## Statistical Analysis

You can perform additional analysis:

```python
import pandas as pd

# Load metrics
df = pd.read_csv('results/data/detailed_metrics.csv')

# Compare algorithms
comparison = df.groupby('algorithm')[
    ['num_colors', 'execution_time_ms', 'chromatic_efficiency']
].agg(['mean', 'std'])

print(comparison)

# Analyze by graph size
by_size = df.groupby('graph_name')['chromatic_efficiency'].mean()
print(by_size)

# Correlation analysis
correlation = df[['num_colors', 'execution_time_ms', 'color_imbalance']].corr()
print(correlation)
```

## Summary

These metrics provide **comprehensive analysis beyond just colors and time**, enabling:
- Detailed algorithm comparison
- Quality assessment even for partial colorings
- Theoretical bounds verification
- Performance trade-off analysis
- Robustness and scalability evaluation
