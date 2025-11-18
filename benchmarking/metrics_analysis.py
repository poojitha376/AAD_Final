#!/usr/bin/env python3
"""
Advanced Metrics Analysis Script

Computes and compares comprehensive metrics across all algorithms.
Generates detailed analysis tables and visualizations.
"""

import sys
import os
import csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import networkx as nx
from src.algorithms.welshpowell import welsh_powell
from src.algorithms.dsatur import dsatur
from src.algorithms.simulated_annealing import simulated_annealing
from src.algorithms.dynamic_programming import find_chromatic_number
from src.utils.graph_generator import (
    generate_erdos_renyi_graph, generate_petersen_graph
)
from src.utils.graph_loader import load_karate_graph
from src.utils.metrics import compute_all_metrics
from benchmarking import config


def run_metrics_analysis():
    """Run comprehensive metrics analysis on multiple graphs."""
    
    print("="*80)
    print("ADVANCED METRICS ANALYSIS FOR GRAPH COLORING ALGORITHMS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    all_results = []
    
    # Test graphs
    test_graphs = {
        'Petersen': nx.petersen_graph(),
        'Karate Club': load_karate_graph(),
        'Random G(20, 0.3)': generate_erdos_renyi_graph(20, 0.3, seed=42),
        'Random G(25, 0.5)': generate_erdos_renyi_graph(25, 0.5, seed=42),
        'Complete K(5)': nx.complete_graph(5),
        'Bipartite K(5,5)': nx.complete_bipartite_graph(5, 5),
    }
    
    print("-"*80)
    print("TEST 1: METRIC COMPUTATION ON VARIOUS GRAPHS")
    print("-"*80)
    
    for graph_name, G in test_graphs.items():
        print(f"\n{graph_name} ({G.number_of_nodes()} nodes, {G.number_of_edges()} edges)")
        print("  Computing bounds...")
        
        # Run algorithms
        results = {}
        
        # Welsh-Powell
        import time
        start = time.perf_counter()
        coloring, k = welsh_powell(G)
        elapsed = (time.perf_counter() - start) * 1000
        results['Welsh-Powell'] = compute_all_metrics(G, coloring, 'Welsh-Powell', elapsed)
        
        # D-Satur
        start = time.perf_counter()
        coloring, k = dsatur(G)
        elapsed = (time.perf_counter() - start) * 1000
        results['D-Satur'] = compute_all_metrics(G, coloring, 'D-Satur', elapsed)
        
        # Simulated Annealing
        start = time.perf_counter()
        coloring, k, _, elapsed_s = simulated_annealing(G, initial_num_colors=6, seed=42)
        results['Simulated Annealing'] = compute_all_metrics(
            G, coloring, 'Simulated Annealing', elapsed_s * 1000
        )
        
        # Dynamic Programming (if small enough)
        if G.number_of_nodes() <= config.DP_MAX_VERTICES:
            start = time.perf_counter()
            k_opt, coloring_opt = find_chromatic_number(G)
            elapsed = (time.perf_counter() - start) * 1000
            if k_opt:
                results['DP'] = compute_all_metrics(
                    G, coloring_opt, 'Dynamic Programming', elapsed, 
                    optimal_chromatic=k_opt
                )
        
        # Print key metrics
        print(f"\n  Algorithm Comparison:")
        print(f"  {'Algorithm':<20} {'Colors':<8} {'Conflicts':<12} {'Time(ms)':<10} {'Efficiency':<12}")
        print(f"  {'-'*70}")
        
        for algo_name, metrics in results.items():
            print(f"  {algo_name:<20} {metrics['num_colors']:<8} "
                  f"{metrics['conflicts']:<12} {metrics['execution_time_ms']:>8.2f} "
                  f"{metrics['chromatic_efficiency']:>11.2%}")
        
        # Print bounds
        print(f"\n  Graph Bounds:")
        print(f"    Lower bound (χ): {results[list(results.keys())[0]]['chromatic_lower_bound']}")
        print(f"    Upper bound: {results[list(results.keys())[0]]['chromatic_upper_bound']}")
        print(f"    Fractional χ_f: {results[list(results.keys())[0]]['fractional_chromatic_approx']:.2f}")
        print(f"    Degeneracy: {results[list(results.keys())[0]]['degeneracy']}")
        
        # Store results
        for algo_name, metrics in results.items():
            metrics['graph_name'] = graph_name
            all_results.append(metrics)
    
    # Save detailed results
    print("\n" + "-"*80)
    print("Saving detailed metrics...")
    
    os.makedirs(config.RESULTS_DATA_PATH, exist_ok=True)
    
    metrics_file = os.path.join(config.RESULTS_DATA_PATH, 'detailed_metrics.csv')
    if all_results:
        # Flatten nested dictionaries for CSV
        flat_results = []
        for result in all_results:
            flat = result.copy()
            conflict_stats = flat.pop('conflict_vertex_stats', {})
            for key, value in conflict_stats.items():
                flat[f'conflict_{key}'] = value
            flat_results.append(flat)
        
        keys = flat_results[0].keys()
        with open(metrics_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(flat_results)
        
        print(f"✓ Metrics saved to {metrics_file}")
    
    # Print summary analysis
    print("\n" + "="*80)
    print("SUMMARY ANALYSIS")
    print("="*80)
    
    # Aggregate statistics
    color_imbalances = [r['color_imbalance'] for r in all_results]
    efficiencies = [r['chromatic_efficiency'] for r in all_results]
    achromatic_powers = [r['achromatic_power'] for r in all_results if r['achromatic_power'] is not None]
    
    print(f"\nColor Imbalance Statistics:")
    print(f"  Average: {sum(color_imbalances)/len(color_imbalances):.3f}")
    print(f"  Min: {min(color_imbalances):.3f} (best balance)")
    print(f"  Max: {max(color_imbalances):.3f}")
    
    print(f"\nChromatic Efficiency Statistics:")
    print(f"  Average: {sum(efficiencies)/len(efficiencies):.3%}")
    print(f"  Min: {min(efficiencies):.3%}")
    print(f"  Max: {max(efficiencies):.3%}")
    
    print(f"\nAchromatic Power Statistics:")
    if achromatic_powers:
        print(f"  Average: {sum(achromatic_powers)/len(achromatic_powers):.3f}")
        print(f"  Min: {min(achromatic_powers):.3f} (more conflicts)")
        print(f"  Max: {max(achromatic_powers):.3f} (fewer conflicts)")
    
    print("\n" + "="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    return all_results


if __name__ == "__main__":
    results = run_metrics_analysis()
