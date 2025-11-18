#!/usr/bin/env python3
"""
Main Benchmarking Script

Runs all graph coloring algorithms on various datasets and saves results.
Generates comparison plots and metrics for the final report.
"""

import sys
import os
import time
import csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import networkx as nx
from src.algorithms.welshpowell import welsh_powell, get_color_statistics as wp_stats
from src.algorithms.dsatur import dsatur, get_color_statistics as ds_stats
from src.algorithms.simulated_annealing import simulated_annealing, get_color_statistics as sa_stats
from src.algorithms.dynamic_programming import find_chromatic_number, get_color_statistics as dp_stats
from src.utils.graph_generator import (
    generate_erdos_renyi_graph, generate_map_graph, generate_complete_graph,
    generate_cycle_graph, generate_petersen_graph
)
from src.utils.graph_loader import load_karate_graph
from src.utils.visualizer import plot_colored_graph, plot_comparison, save_results_json
from src.utils.metrics import compute_all_metrics
from benchmarking import config


def benchmark_algorithm(algorithm_name: str, G: nx.Graph, **kwargs) -> dict:
    """
    Run one algorithm on a graph and return results.
    
    Args:
        algorithm_name (str): 'wp', 'dsatur', 'sa', or 'dp'
        G (nx.Graph): Graph to color
        **kwargs: Algorithm-specific parameters
    
    Returns:
        dict: Results including colors used, time, validity
    """
    
    start_time = time.perf_counter()
    
    try:
        if algorithm_name == 'wp':
            coloring, num_colors = welsh_powell(G)
            elapsed = time.perf_counter() - start_time
            stats = wp_stats(G, coloring)
            return {
                'algorithm': 'Welsh-Powell',
                'success': True,
                'colors': num_colors,
                'time_ms': elapsed * 1000,
                'valid': stats['is_valid'],
                'edges': G.number_of_edges(),
                'nodes': G.number_of_nodes()
            }
        
        elif algorithm_name == 'dsatur':
            coloring, num_colors = dsatur(G)
            elapsed = time.perf_counter() - start_time
            stats = ds_stats(G, coloring)
            return {
                'algorithm': 'D-Satur',
                'success': True,
                'colors': num_colors,
                'time_ms': elapsed * 1000,
                'valid': stats['is_valid'],
                'edges': G.number_of_edges(),
                'nodes': G.number_of_nodes()
            }
        
        elif algorithm_name == 'sa':
            initial_colors = kwargs.get('initial_colors', 5)
            coloring, num_colors, history, elapsed = simulated_annealing(
                G, initial_colors,
                T0=config.SA_INITIAL_TEMP,
                alpha=config.SA_COOLING_RATE,
                max_iterations=config.SA_MAX_ITERATIONS,
                seed=42
            )
            stats = sa_stats(G, coloring, kwargs.get('conflicts'))
            return {
                'algorithm': 'Simulated Annealing',
                'success': True,
                'colors': num_colors,
                'time_ms': elapsed * 1000,
                'conflicts': stats.get('conflicts', 0),
                'valid': stats['is_valid'],
                'edges': G.number_of_edges(),
                'nodes': G.number_of_nodes()
            }
        
        elif algorithm_name == 'dp':
            if G.number_of_nodes() > config.DP_MAX_VERTICES:
                return {
                    'algorithm': 'Dynamic Programming',
                    'success': False,
                    'error': f'Graph too large ({G.number_of_nodes()} > {config.DP_MAX_VERTICES})',
                    'nodes': G.number_of_nodes()
                }
            
            chromatic_num, coloring = find_chromatic_number(G, config.DP_MAX_COLORS)
            elapsed = time.perf_counter() - start_time
            
            if chromatic_num is None:
                return {
                    'algorithm': 'Dynamic Programming',
                    'success': False,
                    'error': 'No solution found',
                    'nodes': G.number_of_nodes()
                }
            
            stats = dp_stats(G, coloring, chromatic_num)
            return {
                'algorithm': 'Dynamic Programming',
                'success': True,
                'colors': chromatic_num,
                'time_ms': elapsed * 1000,
                'valid': stats['is_valid'],
                'edges': G.number_of_edges(),
                'nodes': G.number_of_nodes()
            }
        
        else:
            return {'algorithm': algorithm_name, 'success': False, 'error': 'Unknown algorithm'}
    
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            'algorithm': algorithm_name,
            'success': False,
            'error': str(e),
            'time_ms': elapsed * 1000,
            'nodes': G.number_of_nodes()
        }


def run_benchmark_suite():
    """Run complete benchmark suite on all graph types and sizes."""
    
    print("="*70)
    print("GRAPH COLORING ALGORITHMS - BENCHMARKING SUITE")
    print("="*70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # 1. Test on small, fixed graphs
    print("\n" + "-"*70)
    print("SECTION 1: Small Known Graphs")
    print("-"*70)
    
    test_graphs = {
        'Triangle (K3)': nx.complete_graph(3),
        'Cycle-5 (C5)': nx.cycle_graph(5),
        'Cycle-6 (C6)': nx.cycle_graph(6),
        'Petersen': nx.petersen_graph(),
        'Bipartite K(3,3)': nx.complete_bipartite_graph(3, 3),
        'Karate Club': load_karate_graph(),
    }
    
    for graph_name, G in test_graphs.items():
        print(f"\n{graph_name} ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")
        
        for algo in ['wp', 'dsatur', 'dp', 'sa']:
            result = benchmark_algorithm(algo, G)
            if result['success']:
                print(f"  {result['algorithm']:20} → {result['colors']} colors in {result['time_ms']:.3f} ms")
            else:
                print(f"  {result['algorithm']:20} → SKIP ({result.get('error', 'Unknown error')})")
            
            result['graph_name'] = graph_name
            results.append(result)
    
    # 2. Test on random graphs of various sizes
    print("\n" + "-"*70)
    print("SECTION 2: Random Graphs - Varying Size")
    print("-"*70)
    
    for n in config.GRAPH_SIZES:
        p = 0.3
        print(f"\nRandom G({n}, {p})")
        G = generate_erdos_renyi_graph(n, p, seed=42)
        print(f"  Nodes: {G.number_of_nodes()}, Edges: {G.number_of_edges()}")
        
        for algo in ['wp', 'dsatur', 'sa']:
            result = benchmark_algorithm(algo, G)
            if result['success']:
                print(f"  {result['algorithm']:20} → {result['colors']} colors in {result['time_ms']:.3f} ms")
            else:
                print(f"  {result['algorithm']:20} → ERROR")
            
            result['graph_type'] = 'random'
            result['graph_params'] = f"G({n}, {p})"
            results.append(result)
    
    # 3. Test on graphs of fixed size, varying density
    print("\n" + "-"*70)
    print("SECTION 3: Random Graphs - Varying Density (n=20)")
    print("-"*70)
    
    for p in config.EDGE_PROBABILITIES:
        print(f"\nRandom G(20, {p})")
        G = generate_erdos_renyi_graph(20, p, seed=42)
        print(f"  Edges: {G.number_of_edges()}, Density: {nx.density(G):.3f}")
        
        for algo in ['wp', 'dsatur', 'sa']:
            result = benchmark_algorithm(algo, G)
            if result['success']:
                print(f"  {result['algorithm']:20} → {result['colors']} colors in {result['time_ms']:.3f} ms")
            else:
                print(f"  {result['algorithm']:20} → ERROR")
            
            result['graph_type'] = 'random_density'
            result['graph_params'] = f"G(20, {p})"
            results.append(result)
    
    # Save results to CSV
    print("\n" + "-"*70)
    print("Saving results...")
    
    os.makedirs(config.RESULTS_DATA_PATH, exist_ok=True)
    
    results_file = os.path.join(config.RESULTS_DATA_PATH, 'benchmark_results.csv')
    if results:
        keys = results[0].keys()
        with open(results_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(results)
        print(f"✓ Results saved to {results_file}")
    
    # Save JSON
    json_file = os.path.join(config.RESULTS_DATA_PATH, 'benchmark_results.json')
    save_results_json(results, json_file)
    
    print("\n" + "="*70)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    return results


if __name__ == "__main__":
    results = run_benchmark_suite()
