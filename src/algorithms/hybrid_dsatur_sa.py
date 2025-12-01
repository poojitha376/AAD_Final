"""
Hybrid DSatur + Simulated Annealing Graph Coloring Algorithm

Author: Algorithm Analysis & Design Team
Description:
    A hybrid algorithm that combines the strength of two approaches:
    1. DSatur (constructive): Generates high-quality initial solution quickly
    2. Simulated Annealing (improvement): Refines solution to escape local optima
    
    This hybrid approach often achieves better results than either algorithm alone,
    balancing speed and solution quality.

    Time Complexity: O(V^2 + max_iterations * E)
    Space Complexity: O(V)
    where V = number of vertices, E = number of edges

Strategy:
    - Use DSatur's intelligent vertex ordering for initial coloring
    - Apply SA to reduce number of colors and improve quality
    - Iteratively try with fewer colors until no valid solution exists

Reference:
    Hybrid metaheuristic approaches are widely studied in graph coloring literature.
    Combining constructive heuristics with local search often yields state-of-the-art results.
"""

import random
import math
from typing import Dict, Tuple, List, Optional, Set
import networkx as nx


def dsatur_initial_coloring(G: nx.Graph) -> Tuple[Dict[int, int], int]:
    """
    Generate initial coloring using DSatur algorithm.
    
    Args:
        G (nx.Graph): NetworkX graph object to color.
    
    Returns:
        Tuple[Dict[int, int], int]:
            - coloring: Dictionary mapping each vertex to its assigned color
            - num_colors: Total number of colors used
    """
    if G is None or len(G) == 0:
        return {}, 0
    
    # Initialize data structures
    coloring = {v: None for v in G.nodes()}
    saturation_degree = {v: set() for v in G.nodes()}
    vertex_degrees = dict(G.degree())
    
    uncolored = set(G.nodes())
    
    # Start with highest degree vertex
    if uncolored:
        start_vertex = max(uncolored, key=lambda v: vertex_degrees[v])
        coloring[start_vertex] = 0
        uncolored.remove(start_vertex)
        
        for neighbor in G.neighbors(start_vertex):
            saturation_degree[neighbor].add(0)
    
    # Main DSatur loop
    while uncolored:
        # Select vertex with max saturation degree, break ties by degree
        next_vertex = max(
            uncolored,
            key=lambda v: (len(saturation_degree[v]), vertex_degrees[v])
        )
        
        # Find smallest available color
        neighbor_colors = set()
        for neighbor in G.neighbors(next_vertex):
            if coloring[neighbor] is not None:
                neighbor_colors.add(coloring[neighbor])
        
        color = 0
        while color in neighbor_colors:
            color += 1
        
        coloring[next_vertex] = color
        uncolored.remove(next_vertex)
        
        # Update saturation degrees
        for neighbor in G.neighbors(next_vertex):
            if coloring[neighbor] is None:
                saturation_degree[neighbor].add(color)
    
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


def get_conflicting_vertices(G: nx.Graph, coloring: Dict[int, int]) -> Set[int]:
    """
    Get set of vertices involved in color conflicts.
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Vertex to color assignment
    
    Returns:
        Set[int]: Set of vertices in conflicts
    """
    conflicting = set()
    for u, v in G.edges():
        if coloring.get(u) == coloring.get(v):
            conflicting.add(u)
            conflicting.add(v)
    return conflicting


def smart_recolor_vertex(G: nx.Graph, coloring: Dict[int, int], 
                        num_colors: int, vertex: int) -> Dict[int, int]:
    """
    Intelligently recolor a vertex to minimize conflicts.
    
    Tries colors in order of decreasing preference (colors used less by neighbors).
    
    Args:
        G (nx.Graph): The graph
        coloring (Dict[int, int]): Current coloring
        num_colors (int): Number of available colors
        vertex (int): Vertex to recolor
    
    Returns:
        Dict[int, int]: New coloring
    """
    new_coloring = coloring.copy()
    
    # Count neighbor colors
    neighbor_color_count = {c: 0 for c in range(num_colors)}
    for neighbor in G.neighbors(vertex):
        if neighbor in coloring:
            neighbor_color_count[coloring[neighbor]] += 1
    
    # Try color with minimum conflicts first
    best_color = min(range(num_colors), key=lambda c: neighbor_color_count.get(c, 0))
    new_coloring[vertex] = best_color
    
    return new_coloring


def simulated_annealing_refinement(
    G: nx.Graph,
    initial_coloring: Dict[int, int],
    num_colors: int,
    T0: float = 10.0,
    alpha: float = 0.95,
    max_iterations: int = 50000,
    stall_limit: int = 5000,
    seed: Optional[int] = None
) -> Tuple[Dict[int, int], bool, int]:
    """
    Refine a coloring using Simulated Annealing to achieve valid k-coloring.
    
    Args:
        G (nx.Graph): The graph
        initial_coloring (Dict[int, int]): Starting coloring
        num_colors (int): Target number of colors
        T0 (float): Initial temperature
        alpha (float): Cooling rate (0 < alpha < 1)
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
    
    # Start from initial coloring, adjust to use num_colors
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
        
        # Generate neighbor solution
        if random.random() < 0.7:  # 70% - recolor conflicting vertex
            conflicting = list(get_conflicting_vertices(G, current_coloring))
            if conflicting:
                vertex = random.choice(conflicting)
                new_coloring = smart_recolor_vertex(G, current_coloring, num_colors, vertex)
            else:
                vertex = random.choice(list(G.nodes()))
                new_coloring = current_coloring.copy()
                new_coloring[vertex] = random.randint(0, num_colors - 1)
        else:  # 30% - random recoloring for exploration
            vertex = random.choice(list(G.nodes()))
            new_coloring = current_coloring.copy()
            new_coloring[vertex] = random.randint(0, num_colors - 1)
        
        new_conflicts = count_conflicts(G, new_coloring)
        delta = new_conflicts - current_conflicts
        
        # Accept or reject new solution
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
        
        # Cool down temperature
        T *= alpha
        
        # Check stall limit
        if stall_count >= stall_limit:
            break
    
    is_valid = (best_conflicts == 0)
    return best_coloring, is_valid, iteration + 1


def hybrid_dsatur_sa(
    G: nx.Graph,
    T0: float = 10.0,
    alpha: float = 0.95,
    max_iterations: int = 50000,
    stall_limit: int = 5000,
    seed: Optional[int] = None,
    aggressive: bool = True
) -> Tuple[Dict[int, int], int, Dict]:
    """
    Hybrid DSatur + Simulated Annealing graph coloring algorithm.
    
    Algorithm:
    1. Generate initial high-quality coloring using DSatur
    2. Try to reduce number of colors using SA refinement
    3. Binary search or sequential reduction to find minimum colors
    4. Return best valid coloring found
    
    Args:
        G (nx.Graph): NetworkX graph object to color
        T0 (float): Initial temperature for SA
        alpha (float): Cooling rate for SA
        max_iterations (int): Max iterations per SA run
        stall_limit (int): Stall limit for SA
        seed (int, optional): Random seed for reproducibility
        aggressive (bool): If True, tries to minimize colors; if False, stops at first valid
    
    Returns:
        Tuple[Dict[int, int], int, Dict]:
            - coloring: Final vertex-to-color mapping
            - num_colors: Number of colors used
            - stats: Dictionary with algorithm statistics
    
    Example:
        >>> G = nx.karate_club_graph()
        >>> coloring, k, stats = hybrid_dsatur_sa(G)
        >>> print(f"Colored with {k} colors")
        >>> print(f"DSatur initial: {stats['dsatur_colors']}, Final: {k}")
    """
    if G is None or len(G) == 0:
        return {}, 0, {'dsatur_colors': 0, 'final_colors': 0, 'reduction': 0}
    
    # Phase 1: DSatur initial coloring
    initial_coloring, dsatur_colors = dsatur_initial_coloring(G)
    
    stats = {
        'dsatur_colors': dsatur_colors,
        'sa_iterations': 0,
        'total_sa_runs': 0
    }
    
    if not aggressive:
        # Quick mode: just return DSatur result
        stats['final_colors'] = dsatur_colors
        stats['reduction'] = 0
        return initial_coloring, dsatur_colors, stats
    
    # Phase 2: Try to reduce colors using SA
    best_coloring = initial_coloring
    best_num_colors = dsatur_colors
    
    # Try reducing colors one at a time
    for target_colors in range(dsatur_colors - 1, 0, -1):
        refined_coloring, is_valid, iterations = simulated_annealing_refinement(
            G, best_coloring, target_colors, T0, alpha, 
            max_iterations, stall_limit, seed
        )
        
        stats['sa_iterations'] += iterations
        stats['total_sa_runs'] += 1
        
        if is_valid:
            best_coloring = refined_coloring
            best_num_colors = target_colors
        else:
            # Failed to reduce further, stop
            break
    
    stats['final_colors'] = best_num_colors
    stats['reduction'] = dsatur_colors - best_num_colors
    
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
