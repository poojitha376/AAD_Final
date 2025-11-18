"""
Graph Generator Module

Author: Algorithm Analysis & Design Team
Description:
    Generates synthetic graphs for benchmarking and experimentation.
    Supports Erdős-Rényi random graphs and planar map-like graphs.
"""

import random
import networkx as nx
from typing import Tuple, Optional


def generate_erdos_renyi_graph(n: int, p: float, seed: Optional[int] = None) -> nx.Graph:
    """
    Generate an Erdős-Rényi random graph G(n, p).
    
    Each edge appears independently with probability p.
    
    Args:
        n (int): Number of vertices
        p (float): Edge probability (0 <= p <= 1)
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        nx.Graph: Generated random graph
    
    Time Complexity: O(n^2) for graph generation
    
    Example:
        >>> G = generate_erdos_renyi_graph(50, 0.3, seed=42)
        >>> print(f"Generated graph with {G.number_of_nodes()} nodes")
    """
    if seed is not None:
        random.seed(seed)
    
    G = nx.erdos_renyi_graph(n, p, seed=seed)
    return G


def generate_map_graph(num_regions: int = 8) -> nx.Graph:
    """
    Generate a planar map-like graph resembling regional map.
    
    Creates a small graph where nodes represent regions and edges represent
    shared borders. Useful for demonstrating map coloring problems.
    
    Args:
        num_regions (int): Number of regions to generate (default 8)
    
    Returns:
        nx.Graph: Planar graph representing map
    
    Example:
        >>> G = generate_map_graph(8)
        >>> print(f"Map graph with {G.number_of_nodes()} regions")
    """
    
    G = nx.Graph()
    nodes = [f"R{i}" for i in range(1, num_regions + 1)]
    G.add_nodes_from(nodes)
    
    # Create a planar-like adjacency structure
    edges = []
    if num_regions >= 8:
        edges = [
            ("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("R2", "R4"),
            ("R3", "R5"), ("R4", "R5"), ("R4", "R6"), ("R5", "R7"),
            ("R6", "R7"), ("R6", "R8"), ("R7", "R8"),
            ("R2", "R5"), ("R3", "R4")
        ]
    elif num_regions >= 5:
        edges = [
            ("R1", "R2"), ("R1", "R3"), ("R2", "R3"), ("R2", "R4"),
            ("R3", "R5"), ("R4", "R5")
        ]
    else:
        # For small graphs, create simple structure
        for i in range(num_regions - 1):
            edges.append((f"R{i+1}", f"R{i+2}"))
    
    G.add_edges_from(edges)
    return G


def generate_complete_graph(n: int) -> nx.Graph:
    """
    Generate a complete graph K_n.
    
    Every pair of vertices is connected by an edge.
    Chromatic number = n (requires n colors).
    
    Args:
        n (int): Number of vertices
    
    Returns:
        nx.Graph: Complete graph on n vertices
    
    Example:
        >>> G = generate_complete_graph(5)
        >>> print(f"Complete graph K_5 needs 5 colors")
    """
    return nx.complete_graph(n)


def generate_bipartite_graph(n1: int, n2: int, edge_prob: float = 0.5, 
                             seed: Optional[int] = None) -> nx.Graph:
    """
    Generate a random bipartite graph.
    
    Creates two sets of vertices; edges only between sets (not within).
    Bipartite graphs have chromatic number exactly 2.
    
    Args:
        n1 (int): Size of first partition
        n2 (int): Size of second partition
        edge_prob (float): Probability of edge between partitions
        seed (int, optional): Random seed
    
    Returns:
        nx.Graph: Bipartite graph
    
    Example:
        >>> G = generate_bipartite_graph(10, 10, 0.3, seed=42)
        >>> print("Bipartite graph (chromatic number = 2)")
    """
    if seed is not None:
        random.seed(seed)
    
    G = nx.Graph()
    
    # Add vertices in two sets
    set1 = [f"A{i}" for i in range(n1)]
    set2 = [f"B{i}" for i in range(n2)]
    
    G.add_nodes_from(set1)
    G.add_nodes_from(set2)
    
    # Add edges between sets with given probability
    for u in set1:
        for v in set2:
            if random.random() < edge_prob:
                G.add_edge(u, v)
    
    return G


def generate_cycle_graph(n: int) -> nx.Graph:
    """
    Generate a cycle graph C_n.
    
    Vertices form a single cycle.
    Chromatic number = 2 if n is even, 3 if n is odd.
    
    Args:
        n (int): Number of vertices
    
    Returns:
        nx.Graph: Cycle graph
    
    Example:
        >>> G = generate_cycle_graph(5)
        >>> print("5-cycle needs 3 colors (odd)")
    """
    return nx.cycle_graph(n)


def generate_petersen_graph() -> nx.Graph:
    """
    Generate the Petersen graph.
    
    Famous example with chromatic number 3 and interesting properties.
    Has 10 vertices, 15 edges, is 3-regular.
    
    Returns:
        nx.Graph: Petersen graph
    
    Example:
        >>> G = generate_petersen_graph()
        >>> print(f"Petersen graph: {G.number_of_nodes()} nodes, chromatic number = 3")
    """
    return nx.petersen_graph()


def graph_info(G: nx.Graph) -> dict:
    """
    Get basic information about a graph.
    
    Args:
        G (nx.Graph): Graph to analyze
    
    Returns:
        dict: Information about the graph
    """
    return {
        'vertices': G.number_of_nodes(),
        'edges': G.number_of_edges(),
        'density': nx.density(G),
        'max_degree': max(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0,
        'min_degree': min(dict(G.degree()).values()) if G.number_of_nodes() > 0 else 0,
        'avg_degree': sum(dict(G.degree()).values()) / G.number_of_nodes() if G.number_of_nodes() > 0 else 0,
        'is_connected': nx.is_connected(G),
        'num_components': nx.number_connected_components(G)
    }
