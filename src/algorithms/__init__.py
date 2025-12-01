"""
Graph Coloring Algorithms Package

This package contains implementations of various graph coloring algorithms,
including greedy heuristics, metaheuristics, exact algorithms, and hybrid approaches.

Base Algorithms:
    - Welsh-Powell: Greedy degree-based coloring
    - DSatur: Greedy saturation-degree-based coloring
    - Simulated Annealing: Metaheuristic optimization
    - Dynamic Programming: Exact algorithm with backtracking

Hybrid Algorithms:
    - Hybrid DSatur + SA: Combines DSatur initialization with SA refinement
    - Hybrid Welsh-Powell + SA: Fast WP initialization with SA optimization
    - Hybrid Tabu Search: Greedy + Tabu Search metaheuristic
    - Adaptive Hybrid: Automatically selects best algorithm based on graph properties

All algorithms are implemented from scratch using only standard Python
data structures and NetworkX for graph representation.
"""

# Base algorithms
from .welshpowell import welsh_powell, validate_coloring
from .dsatur import dsatur
from .simulated_annealing import simulated_annealing
from .dynamic_programming import (
    find_chromatic_number,
    find_chromatic_number_with_bounds
)

# Hybrid algorithms
from .hybrid_dsatur_sa import hybrid_dsatur_sa
from .hybrid_wp_sa import hybrid_wp_sa
from .hybrid_tabu import hybrid_tabu
from .adaptive_hybrid import adaptive_hybrid, analyze_graph_characteristics

__all__ = [
    # Base algorithms
    'welsh_powell',
    'dsatur',
    'simulated_annealing',
    'find_chromatic_number',
    'find_chromatic_number_with_bounds',
    'validate_coloring',
    
    # Hybrid algorithms
    'hybrid_dsatur_sa',
    'hybrid_wp_sa',
    'hybrid_tabu',
    'adaptive_hybrid',
    'analyze_graph_characteristics',
]

__version__ = '2.0.0'
__author__ = 'Algorithm Analysis & Design Team'
