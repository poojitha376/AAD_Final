"""
Visualization Module

Author: Algorithm Analysis & Design Team
Description:
    Creates plots, dashboards, and visualizations for graph colorings,
    algorithm comparisons, and performance analysis.
"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import networkx as nx
from typing import Dict, List, Optional, Tuple
import json


def plot_colored_graph(G: nx.Graph, coloring: Dict, title: str = "Graph Coloring",
                       layout: str = 'spring', figsize: Tuple = (10, 8),
                       save_path: Optional[str] = None) -> None:
    """
    Visualize a graph with vertex coloring.
    
    Args:
        G (nx.Graph): The graph to visualize
        coloring (Dict): Vertex to color mapping
        title (str): Title of the plot
        layout (str): Layout algorithm ('spring', 'circular', 'kamada_kawai')
        figsize (Tuple): Figure size (width, height)
        save_path (str, optional): Path to save figure
    
    Returns:
        None (displays or saves figure)
    
    Example:
        >>> from src.algorithms.welshpowell import welsh_powell
        >>> G = nx.erdos_renyi_graph(20, 0.3)
        >>> coloring, k = welsh_powell(G)
        >>> plot_colored_graph(G, coloring, title=f"Welsh-Powell Coloring (k={k})")
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Choose layout
    if layout == 'spring':
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=50)
    elif layout == 'circular':
        pos = nx.circular_layout(G)
    elif layout == 'kamada_kawai':
        pos = nx.kamada_kawai_layout(G)
    else:
        pos = nx.spring_layout(G)
    
    # Create color map
    num_colors = max(coloring.values()) + 1 if coloring else 1
    colors = plt.cm.tab20([(coloring.get(node, 0) % 20) / 20 for node in G.nodes()])
    
    # Draw graph
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=300, ax=ax)
    nx.draw_networkx_edges(G, pos, alpha=0.3, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=8, font_weight='bold', ax=ax)
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_comparison(results: Dict[str, Dict], metric: str = 'colors_used',
                    title: str = "Algorithm Comparison", figsize: Tuple = (12, 6),
                    save_path: Optional[str] = None) -> None:
    """
    Create a bar chart comparing algorithm performance.
    
    Args:
        results (Dict): Dictionary mapping algorithm names to result dictionaries
                       Each result dict should contain the metric
        metric (str): Metric to plot ('colors_used', 'time_ms', 'conflicts', etc.)
        title (str): Plot title
        figsize (Tuple): Figure size
        save_path (str, optional): Path to save figure
    
    Returns:
        None
    
    Example:
        >>> results = {
        ...     'Welsh-Powell': {'colors_used': 4, 'time_ms': 0.5},
        ...     'D-Satur': {'colors_used': 3, 'time_ms': 0.8},
        ... }
        >>> plot_comparison(results, metric='colors_used')
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    algorithms = list(results.keys())
    values = [results[alg].get(metric, 0) for alg in algorithms]
    
    bars = ax.bar(algorithms, values, color=plt.cm.Set2(range(len(algorithms))))
    
    ax.set_ylabel(metric, fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_convergence(history: List[float], algorithm_name: str = "Algorithm",
                     title: str = "Convergence Plot", figsize: Tuple = (10, 6),
                     save_path: Optional[str] = None) -> None:
    """
    Plot convergence history for iterative algorithms.
    
    Args:
        history (List[float]): List of metric values over iterations
        algorithm_name (str): Name of algorithm for legend
        title (str): Plot title
        figsize (Tuple): Figure size
        save_path (str, optional): Path to save figure
    
    Returns:
        None
    
    Example:
        >>> from src.algorithms.simulated_annealing import simulated_annealing
        >>> G = nx.erdos_renyi_graph(30, 0.3)
        >>> coloring, k, history, time_s = simulated_annealing(G, 5)
        >>> plot_convergence(history, algorithm_name="Simulated Annealing")
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    iterations = range(len(history))
    ax.plot(iterations, history, linewidth=2, label=algorithm_name, color='steelblue')
    
    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cost (Conflicts)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def plot_multiple_convergences(histories: Dict[str, List[float]],
                               title: str = "Algorithm Convergence Comparison",
                               figsize: Tuple = (12, 6),
                               save_path: Optional[str] = None) -> None:
    """
    Plot convergence curves for multiple algorithms.
    
    Args:
        histories (Dict): Mapping algorithm names to convergence histories
        title (str): Plot title
        figsize (Tuple): Figure size
        save_path (str, optional): Path to save figure
    
    Returns:
        None
    """
    
    fig, ax = plt.subplots(figsize=figsize)
    
    colors = plt.cm.Set1(range(len(histories)))
    
    for (alg_name, history), color in zip(histories.items(), colors):
        iterations = range(len(history))
        ax.plot(iterations, history, linewidth=2, label=alg_name, color=color, alpha=0.8)
    
    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('Cost (Conflicts)', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {save_path}")
    else:
        plt.show()
    
    plt.close()


def save_results_json(results: Dict, file_path: str) -> None:
    """
    Save experiment results to JSON file.
    
    Args:
        results (Dict): Results dictionary
        file_path (str): Path to save JSON
    
    Returns:
        None
    """
    with open(file_path, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved to {file_path}")


def load_results_json(file_path: str) -> Dict:
    """
    Load experiment results from JSON file.
    
    Args:
        file_path (str): Path to JSON file
    
    Returns:
        Dict: Loaded results
    """
    with open(file_path, 'r') as f:
        results = json.load(f)
    return results
