"""
Hybrid Welsh-Powell + Simulated Annealing Graph Coloring Algorithm

Author: Algorithm Analysis & Design Team
Description:
    Combines Welsh-Powell's fast degree-based greedy approach with 
    Simulated Annealing's powerful optimization capabilities.
    
    Welsh-Powell provides a quick initial solution, then SA refines it
    to potentially achieve better coloring with fewer colors.

    Time Complexity: O(V^2 + E + max_iterations * E)
    Space Complexity: O(V)
    where V = number of vertices, E = number of edges

Strategy:
    - Welsh-Powell is faster than DSatur but may use more colors
    - SA refinement compensates for initial solution quality
    - Good for large graphs where speed matters

Reference:
    Hybrid approaches combining constructive and improvement methods
    are standard in practical graph coloring applications.
"""

import random
import math
from typing import Dict, Tuple, List, Optional, Set
import networkx as nx


def welsh_powell_initial_coloring(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """
    Generate initial coloring using Welsh-Powell algorithm.
    
    Args:
        G (nx.Graph): NetworkX graph object to color.
    
    Returns:
        Tuple[Dict[int, int], int]:
            - coloring: Dictionary mapping each vertex to its assigned color
            - num_colors: Total number of colors used
    """
    if G is None or len(G) == 0:
        return {}, 0
    
    # Sort vertices by decreasing degree
    vertices_by_degree = sorted(G.nodes(), key=lambda v: G.degree(v), reverse=True)
    
    # Initialize color assignment
    coloring = {}
    
    # Assign colors to each vertex in order
    for vertex in vertices_by_degree:
        # Find colors used by neighbors
        neighbor_colors = set()
        for neighbor in G.neighbors(vertex):
            if neighbor in coloring:
                neighbor_colors.add(coloring[neighbor])
        
        # Find smallest available color
        color = 0
        while color in neighbor_colors:
            color += 1
        
        coloring[vertex] = color
    
    num_colors = max(coloring.values()) + 1 if coloring else 0
    return coloring, num_colors


def count_conflicts(G: nx.Graph, coloring: Dict[int, int]) -> int:
    """
    Count number of edges where both endpoints have the same color.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        int: Number of conflicting edges
    """
    conflicts = 0
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            conflicts += 1
    return conflicts


def get_neighbor_solution(G: nx.Graph, coloring: Dict[int, int], 
                         num_colors: int, strategy: str = 'random') -> Dict[int, int]:
    """
    Generate a neighbor solution by modifying current coloring.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Current coloring
        num_colors (int): Number of available colors
        strategy (str): 'random', 'swap', or 'greedy'
    
    Returns:
        Dict[int, int]: New neighbor coloring
    """
    new_coloring = coloring.copy()
    
    if strategy == 'swap':
        # Swap colors of two vertices
        v1, v2 = random.sample(list(G.nodes()), 2)
        new_coloring[v1], new_coloring[v2] = coloring[v2], coloring[v1]
    elif strategy == 'greedy':
        # Recolor a random vertex to minimize conflicts
        vertex = random.choice(list(G.nodes()))
        neighbor_colors = [coloring.get(n, -1) for n in G.neighbors(vertex)]
        color_conflicts = {c: neighbor_colors.count(c) for c in range(num_colors)}
        best_color = min(range(num_colors), key=lambda c: color_conflicts.get(c, 0))
        new_coloring[vertex] = best_color
    else:  # random
        vertex = random.choice(list(G.nodes()))
        new_coloring[vertex] = random.randint(0, num_colors - 1)
    
    return new_coloring


def simulated_annealing_improvement(
    G: nx.Graph,
    initial_coloring: Dict[int, int],
    num_colors: int,
    T0: float = 100.0,
    alpha: float = 0.97,
    max_iterations: int = 100000,
    stall_limit: int = 10000,
    seed: Optional[int] = None
) -> Tuple[Dict[int, int], bool, int]:
    """
    Improve coloring using Simulated Annealing.
    
    Args:
        G (nx.Graph): The graph
        initial_coloring (Dict[int, int]): Starting coloring
        num_colors (int): Target number of colors
        T0 (float): Initial temperature
        alpha (float): Cooling rate
        max_iterations (int): Maximum iterations
        stall_limit (int): Stop if no improvement for this many iterations
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        Tuple[Dict[int, int], bool, int]:
            - best_coloring: Best coloring found
            - is_valid: Whether a valid coloring was found
            - iterations: Number of iterations performed
    """
    if seed is not None:
        random.seed(seed)
    
    # Adjust initial coloring to use target number of colors
    current_coloring = {v: c % num_colors for v, c in initial_coloring.items()}
    current_conflicts = count_conflicts(G, current_coloring)
    
    best_coloring = current_coloring.copy()
    best_conflicts = current_conflicts
    
    T = T0
    stall_count = 0
    
    for iteration in range(max_iterations):
        # Early termination if valid coloring found
        if current_conflicts == 0:
            return current_coloring, True, iteration
        
        # Generate neighbor (adaptive strategy selection)
        if iteration % 3 == 0:
            strategy = 'greedy'
        elif iteration % 3 == 1:
            strategy = 'random'
        else:
            strategy = 'swap'
        
        new_coloring = get_neighbor_solution(G, current_coloring, num_colors, strategy)
        new_conflicts = count_conflicts(G, new_coloring)
        delta = new_conflicts - current_conflicts
        
        # Acceptance criterion
        if delta < 0 or (T > 0 and random.random() < math.exp(-delta / T)):
            current_coloring = new_coloring
            current_conflicts = new_conflicts
            
            if current_conflicts < best_conflicts:
                best_coloring = current_coloring.copy()
                best_conflicts = current_conflicts
                stall_count = 0
            else:
                stall_count += 1
        else:
            stall_count += 1
        
        # Cool down
        T *= alpha
        
        # Check stall
        if stall_count >= stall_limit:
            break
    
    is_valid = (best_conflicts == 0)
    return best_coloring, is_valid, iteration + 1


def hybrid_wp_sa(
    G: nx.Graph,
    T0: float = 100.0,
    alpha: float = 0.97,
    max_iterations: int = 100000,
    stall_limit: int = 10000,
    seed: Optional[int] = None,
    aggressive: bool = True
) -> Tuple[Dict[int, int], int, Dict]:
    """
    Hybrid Welsh-Powell + Simulated Annealing graph coloring algorithm.
    
    Algorithm:
    1. Generate initial coloring using Welsh-Powell (fast, degree-based)
    2. Attempt to reduce colors using SA refinement
    3. Return best valid coloring found
    
    Args:
        G (nx.Graph): NetworkX graph object to color
        T0 (float): Initial temperature for SA
        alpha (float): Cooling rate for SA (0 < alpha < 1)
        max_iterations (int): Max iterations per SA run
        stall_limit (int): Stall limit for SA
        seed (int, optional): Random seed for reproducibility
        aggressive (bool): If True, tries to minimize colors aggressively
    
    Returns:
        Tuple[Dict[int, int], int, Dict]:
            - coloring: Final vertex-to-color mapping
            - num_colors: Number of colors used
            - stats: Dictionary with algorithm statistics
    
    Example:
        >>> G = nx.erdos_renyi_graph(50, 0.3, seed=42)
        >>> coloring, k, stats = hybrid_wp_sa(G)
        >>> print(f"WP initial: {stats['wp_colors']}, Final: {k}")
        >>> print(f"Improvement: {stats['reduction']} colors")
    """
    if G is None or len(G) == 0:
        return {}, 0, {'wp_colors': 0, 'final_colors': 0, 'reduction': 0}
    
    # Phase 1: Welsh-Powell initial coloring
    initial_coloring, wp_colors = welsh_powell_initial_coloring(G)
    
    stats = {
        'wp_colors': wp_colors,
        'sa_iterations': 0,
        'total_sa_runs': 0
    }
    
    if not aggressive:
        # Quick mode: return WP result
        stats['final_colors'] = wp_colors
        stats['reduction'] = 0
        return initial_coloring, wp_colors, stats
    
    # Phase 2: Try to reduce colors using SA
    best_coloring = initial_coloring
    best_num_colors = wp_colors
    
    # Sequential color reduction
    for target_colors in range(wp_colors - 1, 0, -1):
        refined_coloring, is_valid, iterations = simulated_annealing_improvement(
            G, best_coloring, target_colors, T0, alpha,
            max_iterations, stall_limit, seed
        )
        
        stats['sa_iterations'] += iterations
        stats['total_sa_runs'] += 1
        
        if is_valid:
            best_coloring = refined_coloring
            best_num_colors = target_colors
        else:
            # Cannot reduce further
            break
    
    stats['final_colors'] = best_num_colors
    stats['reduction'] = wp_colors - best_num_colors
    
    return best_coloring, best_num_colors, stats


def validate_coloring(G: nx.Graph, coloring: Dict[int, int]) -> bool:
    """
    Verify that a coloring is valid (no adjacent vertices share the same color).
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        bool: True if coloring is valid, False otherwise
    """
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            return False
    return True
