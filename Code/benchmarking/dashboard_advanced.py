#!/usr/bin/env python3
"""
ADVANCED Interactive Dashboard Generator with 3D, Animations, and Edge Cases
Generates professional multi-page HTML dashboard with:
- 15+ interactive visualizations
- 3D surface plots showing scalability
- Animated convergence charts
- Edge case analysis (empty, single node, cliques, bipartite, etc.)
"""

import sys
import os
import json
import math
import csv
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import networkx as nx
from src.algorithms.welshpowell import welsh_powell
from src.algorithms.dsatur import dsatur
from src.algorithms.simulated_annealing import simulated_annealing
from src.algorithms.dynamic_programming import find_chromatic_number
from src.utils.graph_generator import generate_erdos_renyi_graph, generate_petersen_graph
from src.utils.graph_loader import load_karate_graph
from src.utils.metrics import compute_all_metrics


def generate_complete_graph(n):
    """Generate complete graph K(n)."""
    return nx.complete_graph(n)


def generate_edge_case_graphs():
    """Generate graphs representing edge cases."""
    edge_cases = {}
    
    # Empty graph
    G = nx.Graph()
    G.add_nodes_from(range(5))
    edge_cases['Empty (5 nodes, 0 edges)'] = G
    
    # Single vertex
    G = nx.Graph()
    G.add_node(0)
    edge_cases['Single Vertex'] = G
    
    # Two isolated vertices
    G = nx.Graph()
    G.add_nodes_from([0, 1])
    edge_cases['Two Isolated'] = G
    
    # Complete graph (clique)
    edge_cases['Complete K(5)'] = nx.complete_graph(5)
    
    # Complete graph K(7)
    edge_cases['Complete K(7)'] = nx.complete_graph(7)
    
    # Bipartite (complete)
    edge_cases['Bipartite K(3,3)'] = nx.complete_bipartite_graph(3, 3)
    
    # Star graph
    edge_cases['Star (5 edges)'] = nx.star_graph(5)
    
    # Cycle graph (even)
    edge_cases['Cycle C(6)'] = nx.cycle_graph(6)
    
    # Cycle graph (odd)
    edge_cases['Cycle C(5)'] = nx.cycle_graph(5)
    
    # Wheel graph
    edge_cases['Wheel W(6)'] = nx.wheel_graph(6)
    
    # Path graph
    edge_cases['Path P(8)'] = nx.path_graph(8)
    
    # Ladder graph
    edge_cases['Ladder L(4)'] = nx.ladder_graph(4)
    
    return edge_cases


def test_algorithm_on_graph(G, algorithm_name):
    """Test a single algorithm on a graph."""
    import time
    import tracemalloc
    
    try:
        # Skip Dynamic Programming for large graphs (>10 nodes) due to exponential complexity
        if algorithm_name == "Dynamic Programming" and len(G.nodes()) > 10:
            return {'coloring': {}, 'num_colors': 0, 'time': 0.0, 'memory_mb': 0.0, 'error': 'Skipped (graph too large for DP)'}
        
        # Start memory and time tracking
        tracemalloc.start()
        start_time = time.time()
        
        if algorithm_name == "Welsh-Powell":
            coloring, k = welsh_powell(G)
            result = {'coloring': coloring, 'num_colors': k, 'error': None}
        elif algorithm_name == "D-Satur":
            coloring, k = dsatur(G)
            result = {'coloring': coloring, 'num_colors': k, 'error': None}
        elif algorithm_name == "Simulated Annealing":
            coloring, k, history, t = simulated_annealing(G, 5)
            result = {'coloring': coloring, 'num_colors': k, 'history': history, 'error': None}
        elif algorithm_name == "Dynamic Programming":
            k, coloring = find_chromatic_number(G)
            result = {'coloring': coloring, 'num_colors': k, 'error': None}
        else:
            tracemalloc.stop()
            return {'coloring': {}, 'num_colors': 0, 'time': 0.0, 'memory_mb': 0.0, 'error': 'Unknown algorithm'}
            
        # End tracking and capture metrics
        end_time = time.time()
        current_memory, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        result['time'] = (end_time - start_time) * 1000  # Convert to milliseconds
        result['memory_mb'] = peak_memory / (1024 * 1024)  # Convert bytes to megabytes
        return result
        
    except Exception as e:
        # Ensure tracemalloc is stopped if an error occurs
        if tracemalloc.is_tracing():
            tracemalloc.stop()
        return {'coloring': {}, 'num_colors': 0, 'time': 0.0, 'memory_mb': 0.0, 'error': str(e)}
    
    return {'coloring': {}, 'num_colors': 0, 'time': 0.0, 'memory_mb': 0.0, 'error': 'Unknown algorithm'}


def generate_3d_data():
    """Generate 3D data: nodes vs density vs colors."""
    sizes = [8, 12, 16, 20, 25, 30]  # Reduced sizes for reasonable execution times
    densities = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]  # Keep density range
    algorithms = ["Welsh-Powell", "D-Satur", "Simulated Annealing"]
    
    data_3d = {algo: {'x': [], 'y': [], 'z': []} for algo in algorithms}
    
    for size in sizes:
        for density in densities:
            G = generate_erdos_renyi_graph(size, density)
            
            for algo in algorithms:
                result = test_algorithm_on_graph(G, algo)
                if result['error'] is None:
                    data_3d[algo]['x'].append(size)
                    data_3d[algo]['y'].append(density)
                    data_3d[algo]['z'].append(result['num_colors'])
    
    return data_3d


def load_dataset_results():
    """Load results from your_datasets_results.csv"""
    csv_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'data', 'your_datasets_results.csv')
    
    if not os.path.exists(csv_path):
        return None
    
    results = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            results.append({
                'dataset': row['dataset'],
                'algorithm': row['algorithm'],
                'colors': int(row['colors']),
                'time': float(row['time']),
                'valid': row['valid'] == 'True'
            })
    
    # Organize by dataset
    datasets = {}
    algorithms = set()
    
    for r in results:
        dataset = r['dataset']
        algorithm = r['algorithm']
        algorithms.add(algorithm)
        
        if dataset not in datasets:
            datasets[dataset] = {}
        
        datasets[dataset][algorithm] = {
            'colors': r['colors'],
            'time': r['time'],
            'valid': r['valid']
        }
    
    return {
        'raw_results': results,
        'datasets': datasets,
        'algorithms': sorted(list(algorithms)),
        'dataset_names': list(datasets.keys())
    }


def generate_datasets_tab_content(dataset_results):
    """Generate HTML content for the datasets tab."""
    datasets = dataset_results['datasets']
    algorithms = dataset_results['algorithms']
    dataset_names = dataset_results['dataset_names']
    raw_results = dataset_results['raw_results']
    
    # Prepare data for overall comparison charts
    colors_data = []
    time_data = []
    for algo in algorithms:
        colors_data.append({
            'x': dataset_names,
            'y': [datasets[ds].get(algo, {}).get('colors', 0) for ds in dataset_names],
            'name': algo,
            'type': 'bar'
        })
        time_data.append({
            'x': dataset_names,
            'y': [datasets[ds].get(algo, {}).get('time', 0) * 1000 for ds in dataset_names],
            'name': algo,
            'type': 'bar'
        })
    
    # Algorithm summary stats
    algo_stats = {}
    for algo in algorithms:
        colors_list = []
        times_list = []
        for ds in dataset_names:
            if algo in datasets[ds]:
                colors_list.append(datasets[ds][algo]['colors'])
                times_list.append(datasets[ds][algo]['time'])
        
        if colors_list:
            algo_stats[algo] = {
                'avg_colors': sum(colors_list) / len(colors_list),
                'avg_time': sum(times_list) / len(times_list),
                'min_colors': min(colors_list),
                'max_colors': max(colors_list)
            }
    
    best_avg_colors = min(s['avg_colors'] for s in algo_stats.values()) if algo_stats else 0
    
    html = f"""
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(algorithms)}</div>
                    <div class="stat-label">Algorithms Tested</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(dataset_names)}</div>
                    <div class="stat-label">Real Datasets</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(raw_results)}</div>
                    <div class="stat-label">Total Tests</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{sum(1 for r in raw_results if r['valid'])}/{len(raw_results)}</div>
                    <div class="stat-label">Valid Colorings</div>
                </div>
            </div>
            
            <h2 style="color: #667eea; font-size: 1.8em; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea;">
                🎯 Algorithm Comparison Across Your Datasets
            </h2>
            
            <div class="dashboard-grid">
                <div class="chart-container">
                    <h3>Colors Used by Algorithm</h3>
                    <div id="dataset-colors-comparison"></div>
                </div>
                <div class="chart-container">
                    <h3>Execution Time by Algorithm (ms, log scale)</h3>
                    <div id="dataset-time-comparison"></div>
                </div>
            </div>
            
            <h2 style="color: #667eea; font-size: 1.8em; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea;">
                📊 Individual Dataset Results
            </h2>
            
            <div class="dashboard-grid">
"""
    
    # Add individual dataset charts
    for i, ds_name in enumerate(dataset_names):
        ds_data = datasets[ds_name]
        html += f"""
                <div class="chart-container">
                    <h3>🗂️ {ds_name}</h3>
                    <div id="dataset-{i}-chart"></div>
                </div>
"""
    
    html += """
            </div>
            
            <h2 style="color: #667eea; font-size: 1.8em; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea;">
                📋 Algorithm Performance Summary
            </h2>
            
            <div class="chart-container">
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>Algorithm</th>
                            <th>Avg Colors</th>
                            <th>Min Colors</th>
                            <th>Max Colors</th>
                            <th>Avg Time (ms)</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for algo in sorted(algorithms):
        if algo in algo_stats:
            stats = algo_stats[algo]
            color_class = 'best' if abs(stats['avg_colors'] - best_avg_colors) < 0.01 else ''
            html += f"""
                        <tr>
                            <td><strong>{algo}</strong></td>
                            <td class="{color_class}">{stats['avg_colors']:.2f}</td>
                            <td>{stats['min_colors']}</td>
                            <td>{stats['max_colors']}</td>
                            <td>{stats['avg_time']*1000:.4f}</td>
                        </tr>
"""
    
    html += """
                    </tbody>
                </table>
            </div>
            
            <h2 style="color: #667eea; font-size: 1.8em; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea;">
                📝 Complete Results Table
            </h2>
            
            <div class="chart-container">
                <table class="metrics-table">
                    <thead>
                        <tr>
                            <th>Dataset</th>
                            <th>Algorithm</th>
                            <th>Colors</th>
                            <th>Time (ms)</th>
                            <th>Valid</th>
                        </tr>
                    </thead>
                    <tbody>
"""
    
    for r in raw_results:
        valid_icon = '✓' if r['valid'] else '✗'
        valid_class = 'best' if r['valid'] else 'worst'
        html += f"""
                        <tr>
                            <td>{r['dataset']}</td>
                            <td><strong>{r['algorithm']}</strong></td>
                            <td>{r['colors']}</td>
                            <td>{r['time']*1000:.4f}</td>
                            <td class="{valid_class}">{valid_icon}</td>
                        </tr>
"""
    
    html += f"""
                    </tbody>
                </table>
            </div>
            
            <script>
                // Overall Colors Comparison
                var datasetColorsData = {json.dumps(colors_data)};
                var datasetColorsLayout = {{
                    barmode: 'group',
                    xaxis: {{ title: 'Dataset' }},
                    yaxis: {{ title: 'Number of Colors' }},
                    legend: {{ orientation: 'h', y: -0.2 }},
                    margin: {{ t: 20, b: 100 }}
                }};
                Plotly.newPlot('dataset-colors-comparison', datasetColorsData, datasetColorsLayout, {{responsive: true}});
                
                // Overall Time Comparison
                var datasetTimeData = {json.dumps(time_data)};
                var datasetTimeLayout = {{
                    barmode: 'group',
                    xaxis: {{ title: 'Dataset' }},
                    yaxis: {{ title: 'Time (ms)', type: 'log' }},
                    legend: {{ orientation: 'h', y: -0.2 }},
                    margin: {{ t: 20, b: 100 }}
                }};
                Plotly.newPlot('dataset-time-comparison', datasetTimeData, datasetTimeLayout, {{responsive: true}});
"""
    
    # Add individual dataset charts
    for i, ds_name in enumerate(dataset_names):
        ds_data = datasets[ds_name]
        algos = list(ds_data.keys())
        colors_vals = [ds_data[a]['colors'] for a in algos]
        times_vals = [ds_data[a]['time'] * 1000 for a in algos]
        
        html += f"""
                
                // {ds_name} - Combined chart
                var ds{i}Data = [
                    {{
                        x: {json.dumps(algos)},
                        y: {json.dumps(colors_vals)},
                        name: 'Colors',
                        type: 'bar',
                        marker: {{ color: '#667eea' }}
                    }},
                    {{
                        x: {json.dumps(algos)},
                        y: {json.dumps(times_vals)},
                        name: 'Time (ms)',
                        type: 'bar',
                        yaxis: 'y2',
                        marker: {{ color: '#764ba2' }}
                    }}
                ];
                var ds{i}Layout = {{
                    title: '',
                    xaxis: {{ title: 'Algorithm' }},
                    yaxis: {{ title: 'Colors', side: 'left' }},
                    yaxis2: {{
                        title: 'Time (ms)',
                        overlaying: 'y',
                        side: 'right',
                        type: 'log'
                    }},
                    margin: {{ t: 20, b: 100, l: 60, r: 60 }},
                    showlegend: true,
                    legend: {{ orientation: 'h', y: -0.3 }}
                }};
                Plotly.newPlot('dataset-{i}-chart', ds{i}Data, ds{i}Layout, {{responsive: true}});
"""
    
    html += """
            </script>
"""
    
    return html


def generate_advanced_html(results_data):
    """Generate advanced HTML dashboard with tabs, 3D plots, animations."""
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Advanced Graph Coloring Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        
        .container {
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        
        h1 {
            font-size: 2.8em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .subtitle {
            font-size: 1.1em;
            opacity: 0.95;
        }
        
        .tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 3px solid #667eea;
            overflow-x: auto;
        }
        
        .tab-button {
            flex: 1;
            padding: 15px 20px;
            background: #f5f5f5;
            border: none;
            border-bottom: 4px solid transparent;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .tab-button:hover {
            background: #e8e8e8;
            color: #667eea;
        }
        
        .tab-button.active {
            background: white;
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        .tab-content {
            display: none;
            padding: 30px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .chart-container h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .chart-3d {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        
        .chart-3d h3 {
            color: #667eea;
            margin-bottom: 15px;
        }
        
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
            background: white;
        }
        
        .metrics-table th {
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }
        
        .metrics-table td {
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }
        
        .metrics-table tr:hover {
            background: #f5f5f5;
        }
        
        .edge-case-section {
            margin-bottom: 30px;
        }
        
        .edge-case-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }
        
        .edge-case-card {
            background: #f8f9fa;
            border: 2px solid #667eea;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
        }
        
        .edge-case-name {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .edge-case-result {
            font-size: 0.9em;
            color: #555;
            margin: 5px 0;
        }
        
        .result-good { color: #28a745; font-weight: 600; }
        .result-warning { color: #ff9800; font-weight: 600; }
        .result-error { color: #dc3545; font-weight: 600; }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }
        
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        footer {
            background: #f5f5f5;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }
        
        .legend-item {
            display: inline-block;
            margin-right: 20px;
            font-size: 0.9em;
        }
        
        .legend-color {
            display: inline-block;
            width: 15px;
            height: 15px;
            border-radius: 3px;
            margin-right: 5px;
            vertical-align: middle;
        }
        
        @media (max-width: 1200px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .edge-case-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            
            .stat-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        @media (max-width: 768px) {
            .tabs {
                flex-wrap: wrap;
            }
            
            .tab-button {
                flex: 0 0 50%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 Advanced Graph Coloring Analysis Dashboard</h1>
            <p class="subtitle">Interactive Visualizations with 3D Analysis, Animations & Edge Cases</p>
            <p class="subtitle">📊 Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </header>
        
        <div class="tabs">
            <button class="tab-button active" onclick="openTab(event, 'overview')">📊 Overview</button>
            <button class="tab-button" onclick="openTab(event, 'datasets')">🗂️ Your Datasets</button>
            <button class="tab-button" onclick="openTab(event, 'analysis')">📈 Analysis</button>
            <button class="tab-button" onclick="openTab(event, '3d')">🔮 3D Analysis</button>
            <button class="tab-button" onclick="openTab(event, 'edge-cases')">⚠️ Edge Cases</button>
            <button class="tab-button" onclick="openTab(event, 'metrics')">📋 Detailed Metrics</button>
        </div>
        
        <div id="overview" class="tab-content active">
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">4</div>
                    <div class="stat-label">Algorithms</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">12+</div>
                    <div class="stat-label">Edge Cases</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">20+</div>
                    <div class="stat-label">Metrics</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">15+</div>
                    <div class="stat-label">Charts</div>
                </div>
            </div>
            
            <div class="dashboard-grid">
                <div class="chart-container">
                    <h3>🎯 Colors Used - All Graphs</h3>
                    <div id="colorsChart"></div>
                    <div id="graphMeta" style="margin-top:12px; font-size:0.9em; color:#444;
                                display:flex; gap:12px; flex-wrap:wrap; align-items:flex-start;">
                        <!-- Populated by JavaScript: compact graph metadata (nodes / edges / density) -->
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3>⚡ Execution Time Comparison</h3>
                    <div id="timeChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Chromatic Efficiency</h3>
                    <div id="efficiencyChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>🎯 Solution Quality (Achromatic Power)</h3>
                    <div id="achroChart"></div>
                </div>
            </div>
        </div>
        
        <!-- DATASETS TAB -->
        <div id="datasets" class="tab-content">
            DATASETS_CONTENT_PLACEHOLDER
        </div>
        
        <div id="analysis" class="tab-content">
            <div class="dashboard-grid">
                <div class="chart-container">
                    <h3>📦 Color Distribution (Box Plot)</h3>
                    <div id="boxChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>🔥 Heatmap: Time vs Efficiency</h3>
                    <div id="heatmapChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>📊 Color Imbalance Analysis</h3>
                    <div id="imbalanceChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>⚙️ Algorithm Speed Ranking</h3>
                    <div id="speedRankChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>📈 Conflicts per Algorithm</h3>
                    <div id="conflictChart"></div>
                </div>
                
                <div class="chart-container">
                    <h3>🎨 Color Class Balance</h3>
                    <div id="classBalanceChart"></div>
                </div>
            </div>
        </div>
        
        <div id="3d" class="tab-content">
            <div class="chart-3d">
                <h3>🔮 3D Surface: How Colors Scale with Size & Density (Welsh-Powell)</h3>
                <div id="surface3d-wp"></div>
            </div>
            
            <div class="chart-3d">
                <h3>🔮 3D Surface: How Colors Scale with Size & Density (D-Satur)</h3>
                <div id="surface3d-ds"></div>
            </div>
            
            <div class="chart-3d">
                <h3>🔮 3D Scatter: Algorithm Comparison Space</h3>
                <div id="scatter3d"></div>
            </div>
        </div>
        
        <div id="edge-cases" class="tab-content">
            <h2 style="color: #667eea; margin-bottom: 20px;">⚠️ Edge Case Analysis</h2>
            <p style="margin-bottom: 20px; color: #666;">
                Testing algorithms on special graph structures: empty graphs, cliques, bipartite graphs, and more.
            </p>
            
            <div id="edgeCasesContainer" class="edge-case-grid">
                </div>
        </div>
        
        <div id="metrics" class="tab-content">
            <h2 style="color: #667eea; margin-bottom: 20px;">📋 Detailed Metrics Table</h2>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Graph</th>
                        <th>Description</th> <th>Algorithm</th>
                        <th>Colors</th>
                        <th>Conflicts</th>
                        <th>Valid</th>
                        <th>Time (ms)</th>
                        <th>Efficiency</th>
                        <th>Imbalance</th>
                        <th>Achromatic</th>
                        <th>Max Degree</th>
                    </tr>
                </thead>
                <tbody id="metricsBody">
                    </tbody>
            </table>
        </div>
        
        <footer>
            <p><strong>Graph Coloring Analysis | Algorithm Analysis & Design Final Project</strong></p>
            <p>Algorithms: Welsh-Powell | D-Satur | Simulated Annealing | Dynamic Programming</p>
            <p>This dashboard demonstrates advanced analysis, 3D visualization, and edge case handling.</p>
        </footer>
    </div>
    
    <script>
        // Tab switching functionality
        function openTab(evt, tabName) {
            const tabcontents = document.getElementsByClassName("tab-content");
            for (let i = 0; i < tabcontents.length; i++) {
                tabcontents[i].classList.remove("active");
            }
            
            const tabbuttons = document.getElementsByClassName("tab-button");
            for (let i = 0; i < tabbuttons.length; i++) {
                tabbuttons[i].classList.remove("active");
            }
            
            document.getElementById(tabName).classList.add("active");
            evt.currentTarget.classList.add("active");
        }
        
        const resultsData = """ + json.dumps(results_data['regular']) + """;
        const edgeCaseData = """ + json.dumps(results_data['edge_cases']) + """;
        const data3d = """ + json.dumps(results_data['3d']) + """;
        
        // Map for graph descriptions
        const graphDescMap = {};
        resultsData.forEach(r => graphDescMap[r.graph_name] = r.graph_description);

        // Helper: Extract by metric
        function getDataByMetric(metric) {
            const data = {};
            resultsData.forEach(result => {
                if (!data[result.algorithm]) data[result.algorithm] = [];
                data[result.algorithm].push(result[metric]);
            });
            return data;
        }
        
        // Helper: Get graph names
        function getGraphNames() {
            const graphs = new Set();
            resultsData.forEach(r => graphs.add(r.graph_name));
            return Array.from(graphs);
        }

        // Build a compact metadata map for each graph (nodes/edges/density/max degree)
        const graphMeta = {};
        resultsData.forEach(r => {
            if (!graphMeta[r.graph_name]) {
                graphMeta[r.graph_name] = {
                    nodes: r.graph_nodes,
                    edges: r.graph_edges,
                    density: r.graph_density,
                    max_degree: r.max_degree,
                    avg_degree: r.avg_degree
                };
            }
        });

        // Render compact metadata panel under the Colors chart
        function renderGraphMetaPanel() {
            const container = document.getElementById('graphMeta');
            if (!container) return;
            const items = Object.keys(graphMeta).map(name => {
                const m = graphMeta[name];
                return `<div style="background:#fff;border-radius:8px;padding:8px 10px;border:1px solid #eee;box-shadow:0 1px 3px rgba(0,0,0,0.05);min-width:160px;">
                            <div style="font-weight:700;color:#667eea;margin-bottom:6px;">${name}</div>
                            <div style="line-height:1.2;color:#333;"><strong>Nodes:</strong> ${m.nodes}</div>
                            <div style="line-height:1.2;color:#333;"><strong>Edges:</strong> ${m.edges}</div>
                            <div style="line-height:1.2;color:#333;"><strong>Density:</strong> ${m.density.toFixed(3)}</div>
                        </div>`;
            });
            container.innerHTML = items.join('');
        }
        
        const graphNames = getGraphNames();

        // ========== OVERVIEW TAB CHARTS ==========
        
        // Chart 1: Colors Used
        const colorsByAlgo = getDataByMetric('num_colors');
        const colorsTrace = [];
        Object.keys(colorsByAlgo).sort().forEach(algo => {
            colorsTrace.push({
                name: algo,
                x: graphNames,
                y: colorsByAlgo[algo],
                type: 'bar',
                marker: {color: ['#667eea', '#764ba2', '#f093fb', '#4facfe'][Object.keys(colorsByAlgo).sort().indexOf(algo)]},
                // include per-point text with graph metadata for hover (nodes/edges/density)
                text: graphNames.map(g => `Nodes: ${graphMeta[g] ? graphMeta[g].nodes : 'N/A'}<br>Edges: ${graphMeta[g] ? graphMeta[g].edges : 'N/A'}<br>Density: ${graphMeta[g] ? graphMeta[g].density.toFixed(3) : 'N/A'}`),
                hovertemplate: '<b>%{x}</b><br>%{text}<br>Colors: %{y}<extra></extra>'
            });
        });
        Plotly.newPlot('colorsChart', colorsTrace, {
            barmode: 'group',
            xaxis: {title: 'Graph Type'},
            yaxis: {title: 'Number of Colors'},
            hovermode: 'closest',
            height: 400
        }, {responsive: true});

        // Call function to render metadata panel
        renderGraphMetaPanel();
        
        // Chart 2: Execution Time - Enhanced with robust axis handling
        const timeByAlgo = getDataByMetric('execution_time_ms');
        const timeTrace = [];
        Object.keys(timeByAlgo).sort().forEach(algo => {
            timeTrace.push({
                name: algo,
                x: graphNames,
                y: timeByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers',
                line: {width: 3},
                // include metadata on hover for clarity
                text: graphNames.map(g => `Nodes: ${graphMeta[g] ? graphMeta[g].nodes : 'N/A'}<br>Edges: ${graphMeta[g] ? graphMeta[g].edges : 'N/A'}<br>Density: ${graphMeta[g] ? graphMeta[g].density.toFixed(3) : 'N/A'}`),
                hovertemplate: '<b>%{x}</b><br>%{text}<br>Time: %{y} ms<extra></extra>'
            });
        });

        // Choose appropriate y-axis scaling for execution time
        function renderTimeChart() {
            const allTimes = [].concat(...Object.values(timeByAlgo));
            const maxTime = allTimes.length ? Math.max(...allTimes) : 0;
            const nonZero = allTimes.filter(t => t > 0);
            const minNonZero = nonZero.length ? Math.min(...nonZero) : null;

            let yaxisConfig = {title: 'Time (ms)'};
            let annotations = [];

            if (maxTime === 0) {
                // All zeros -> show a small linear range so chart is visible and annotate
                yaxisConfig.type = 'linear';
                yaxisConfig.range = [0, 1];
                yaxisConfig.title = 'Time (ms) — all recorded as 0 (below timer resolution)';
                annotations.push({
                    xref: 'paper', yref: 'paper', x: 0.5, y: -0.18,
                    text: 'Note: All execution times recorded as 0 ms — likely below timing resolution.<br>This is equivalent to wall-clock time but measured in milliseconds.',
                    showarrow: false,
                    font: {size: 11, color: '#555'},
                    xanchor: 'center'
                });
            } else if (minNonZero !== null && maxTime / minNonZero > 1000) {
                // wide range -> use log scale
                yaxisConfig.type = 'log';
                yaxisConfig.title = 'Time (ms, log scale)';
            } else if (maxTime < 1) {
                // all very small values -> linear with small range and nice ticks
                yaxisConfig.type = 'linear';
                yaxisConfig.range = [0, Math.max(1, maxTime * 1.2)];
                yaxisConfig.tickformat = '.3f';
            } else {
                // reasonable values -> linear and small headroom
                yaxisConfig.type = 'linear';
                yaxisConfig.range = [0, maxTime * 1.2];
            }

            Plotly.newPlot('timeChart', timeTrace, {
                xaxis: {title: 'Graph Type'},
                yaxis: yaxisConfig,
                annotations: annotations,
                hovermode: 'closest',
                height: 400
            }, {responsive: true});
        }

        renderTimeChart();
        
        // Chart 3: Efficiency
        const effByAlgo = getDataByMetric('chromatic_efficiency');
        const effTrace = [];
        Object.keys(effByAlgo).sort().forEach(algo => {
            effTrace.push({
                name: algo,
                x: graphNames,
                y: effByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers',
                fill: 'tozeroy',
                // UPDATED: Add description to hover text
                text: graphNames.map(name => graphDescMap[name]), 
                hovertemplate: '<b>%{x}</b><br>%{text}<br>Efficiency: %{y:.1%}<extra></extra>'
            });
        });
        Plotly.newPlot('efficiencyChart', effTrace, {
            xaxis: {title: 'Graph Type'},
            yaxis: {title: 'Efficiency (0-1)', range: [0, 1.1]},
            hovermode: 'closest',
            height: 400
        }, {responsive: true});
        
        // Chart 4: Achromatic Power
        const achrByAlgo = getDataByMetric('achromatic_power');
        const achrTrace = [];
        Object.keys(achrByAlgo).sort().forEach(algo => {
            achrTrace.push({
                name: algo,
                x: graphNames,
                y: achrByAlgo[algo],
                type: 'scatter',
                mode: 'markers',
                marker: {size: 10},
                // UPDATED: Add description to hover text
                text: graphNames.map(name => graphDescMap[name]), 
                hovertemplate: '<b>%{x}</b><br>%{text}<br>Power: %{y:.2f}<extra></extra>'
            });
        });
        Plotly.newPlot('achroChart', achrTrace, {
            xaxis: {title: 'Graph Type'},
            yaxis: {title: 'Achromatic Power (0-1)', range: [-0.1, 1.1]},
            hovermode: 'closest',
            height: 400
        }, {responsive: true});
        
        // ========== ANALYSIS TAB CHARTS ==========
        
        // Chart 5: Box Plot of Colors
        const algos = Object.keys(colorsByAlgo).sort();
        const boxTraces = [];
        algos.forEach(algo => {
            boxTraces.push({
                y: colorsByAlgo[algo],
                name: algo,
                type: 'box'
            });
        });
        Plotly.newPlot('boxChart', boxTraces, {
            title: '',
            yaxis: {title: 'Number of Colors'},
            height: 350
        }, {responsive: true});
        
        // Chart 6: Heatmap - Time vs Efficiency
        const heatmapData = {};
        resultsData.forEach(r => {
            const key = r.algorithm + '|' + r.graph_name;
            heatmapData[key] = {time: r.execution_time_ms, eff: r.chromatic_efficiency};
        });
        
        const heatTrace = [{
            z: algos.map(algo => graphNames.map(graph => {
                const key = algo + '|' + graph;
                return heatmapData[key] ? heatmapData[key].time : 0;
            })),
            x: graphNames,
            y: algos,
            type: 'heatmap',
            colorscale: 'Viridis'
        }];
        
        Plotly.newPlot('heatmapChart', heatTrace, {
            title: '',
            xaxis: {title: 'Graph'},
            yaxis: {title: 'Algorithm'},
            height: 350
        }, {responsive: true});
        
        // Chart 7: Color Imbalance
        const imbalanceByAlgo = getDataByMetric('color_imbalance');
        const imbalanceTrace = [];
        Object.keys(imbalanceByAlgo).sort().forEach(algo => {
            imbalanceTrace.push({
                name: algo,
                x: graphNames,
                y: imbalanceByAlgo[algo],
                type: 'bar'
            });
        });
        Plotly.newPlot('imbalanceChart', imbalanceTrace, {
            barmode: 'group',
            xaxis: {title: 'Graph'},
            yaxis: {title: 'Imbalance Score'},
            height: 350
        }, {responsive: true});
        
        // Chart 8: Speed Ranking - Enhanced for zero times
        const avgTimeByAlgo = {};
        Object.keys(timeByAlgo).forEach(algo => {
            avgTimeByAlgo[algo] = timeByAlgo[algo].reduce((a, b) => a + b, 0) / timeByAlgo[algo].length;
        });
        
        const avgTimes = Object.values(avgTimeByAlgo);
        const maxAvgTime = Math.max(...avgTimes);
        
        const speedTrace = [{
            x: Object.keys(avgTimeByAlgo),
            y: Object.values(avgTimeByAlgo),
            type: 'bar',
            marker: {color: Object.values(avgTimeByAlgo), colorscale: 'Reds'},
            text: Object.values(avgTimeByAlgo).map(t => t.toFixed(4) + ' ms'),
            textposition: 'auto'
        }];
        
        let speedYaxis = {title: 'Average Time (ms)'};
        if (maxAvgTime === 0) {
            speedYaxis.range = [0, 1];
            speedYaxis.title = 'Average Time (ms) — all ≈0';
        } else if (maxAvgTime < 0.001) {
            speedYaxis.tickformat = '.4f';
        }
        
        Plotly.newPlot('speedRankChart', speedTrace, {
            xaxis: {title: 'Algorithm'},
            yaxis: speedYaxis,
            height: 350
        }, {responsive: true});
        
        // Chart 9: Conflicts
        const conflictByAlgo = getDataByMetric('conflicts');
        const conflictTrace = [];
        Object.keys(conflictByAlgo).sort().forEach(algo => {
            conflictTrace.push({
                name: algo,
                x: graphNames,
                y: conflictByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers'
            });
        });
        Plotly.newPlot('conflictChart', conflictTrace, {
            xaxis: {title: 'Graph'},
            yaxis: {title: 'Number of Conflicts'},
            height: 350
        }, {responsive: true});
        
        // Chart 10: Color Class Variance
        const varianceByAlgo = getDataByMetric('color_class_variance');
        const varianceTrace = [];
        Object.keys(varianceByAlgo).sort().forEach(algo => {
            varianceTrace.push({
                name: algo,
                x: graphNames,
                y: varianceByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers',
                fill: 'tonexty'
            });
        });
        Plotly.newPlot('classBalanceChart', varianceTrace, {
            xaxis: {title: 'Graph'},
            yaxis: {title: 'Color Class Variance'},
            height: 350
        }, {responsive: true});
        
        // ========== 3D TAB CHARTS ==========
        
        // 3D Surface Plot - Welsh-Powell
        if (data3d && data3d['Welsh-Powell']) {
            const wp3d = data3d['Welsh-Powell'];
            const wp3dTrace = [{
                x: wp3d.x,
                y: wp3d.y,
                z: wp3d.z,
                mode: 'markers',
                type: 'scatter3d',
                marker: {size: 5, color: wp3d.z, colorscale: 'Viridis', showscale: true}
            }];
            
            Plotly.newPlot('surface3d-wp', wp3dTrace, {
                scene: {
                    xaxis: {title: 'Graph Size (nodes)'},
                    yaxis: {title: 'Edge Density'},
                    zaxis: {title: 'Colors Used'}
                },
                height: 500
            }, {responsive: true});
        }
        
        // 3D Surface Plot - D-Satur
        if (data3d && data3d['D-Satur']) {
            const ds3d = data3d['D-Satur'];
            const ds3dTrace = [{
                x: ds3d.x,
                y: ds3d.y,
                z: ds3d.z,
                mode: 'markers',
                type: 'scatter3d',
                marker: {size: 5, color: ds3d.z, colorscale: 'Plasma', showscale: true}
            }];
            
            Plotly.newPlot('surface3d-ds', ds3dTrace, {
                scene: {
                    xaxis: {title: 'Graph Size (nodes)'},
                    yaxis: {title: 'Edge Density'},
                    zaxis: {title: 'Colors Used'}
                },
                height: 500
            }, {responsive: true});
        }
        
        // 3D Scatter: Algorithm Comparison
        const scatter3dTraces = [];
        algos.forEach((algo, idx) => {
            const subset = resultsData.filter(r => r.algorithm === algo);
            scatter3dTraces.push({
                x: subset.map(r => r.graph_nodes),
                y: subset.map(r => r.execution_time_ms),
                z: subset.map(r => r.num_colors),
                mode: 'markers',
                type: 'scatter3d',
                name: algo,
                marker: {size: 6}
            });
        });
        
        Plotly.newPlot('scatter3d', scatter3dTraces, {
            scene: {
                xaxis: {title: 'Nodes'},
                yaxis: {title: 'Time (ms)'},
                zaxis: {title: 'Colors'}
            },
            height: 500
        }, {responsive: true});
        
        // ========== EDGE CASES TAB ==========
        
        const edgeCaseContainer = document.getElementById('edgeCasesContainer');
        edgeCaseData.forEach(ec => {
            const card = document.createElement('div');
            card.className = 'edge-case-card';
            
            const statusClass = ec.error ? 'result-error' : (ec.has_errors ? 'result-warning' : 'result-good');
            const statusText = ec.error ? '❌ Error: ' + ec.error : (ec.has_errors ? '⚠️ Has Conflicts' : '✓ Valid');
            
            card.innerHTML = `
                <div class="edge-case-name">${ec.graph_name}</div>
                <div class="edge-case-result"><strong>Nodes:</strong> ${ec.graph_nodes}</div>
                <div class="edge-case-result"><strong>Edges:</strong> ${ec.graph_edges}</div>
                <div class="edge-case-result" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                    <strong>WP:</strong> ${ec.wp_colors} colors
                </div>
                <div class="edge-case-result"><strong>DS:</strong> ${ec.ds_colors} colors</div>
                <div class="edge-case-result"><strong>SA:</strong> ${ec.sa_colors} colors</div>
                <div class="edge-case-result"><strong>DP:</strong> ${ec.dp_colors} colors</div>
                <div class="edge-case-result" style="margin-top: 10px; padding-top: 10px; border-top: 1px solid #ddd;">
                    <span class="${statusClass}">${statusText}</span>
                </div>
            `;
            
            edgeCaseContainer.appendChild(card);
        });
        
        // ========== METRICS TABLE ==========
        
        const metricsBody = document.getElementById('metricsBody');
        resultsData.forEach(result => {
            const row = document.createElement('tr');
            const valid = result.is_valid ? 
                '<span class="result-good">✓ Valid</span>' : 
                '<span class="result-error">✗ Invalid</span>';
            
            row.innerHTML = `
                <td>${result.graph_name}</td>
                <td style="font-size: 0.85em; color: #666;">${result.graph_description}</td> <td><strong>${result.algorithm}</strong></td>
                <td style="text-align: center; font-weight: 600; color: #667eea;">${result.num_colors}</td>
                <td style="text-align: center;">${result.conflicts}</td>
                <td>${valid}</td>
                <td>${result.execution_time_ms.toFixed(2)}</td>
                <td>${(result.chromatic_efficiency * 100).toFixed(1)}%</td>
                <td>${result.color_imbalance.toFixed(3)}</td>
                <td>${result.achromatic_power.toFixed(3)}</td>
                <td>${result.max_degree}</td>
            `;
            metricsBody.appendChild(row);
        });
    </script>
</body>
</html>
"""
    
    # Load and inject dataset results if available
    dataset_results = load_dataset_results()
    if dataset_results:
        datasets_html = generate_datasets_tab_content(dataset_results)
        html = html.replace('DATASETS_CONTENT_PLACEHOLDER', datasets_html)
    else:
        html = html.replace('DATASETS_CONTENT_PLACEHOLDER', 
                           '<div style="padding: 40px; text-align: center;"><h2>No dataset results found</h2><p>Run <code>python3 run_on_your_data.py</code> to generate results.</p></div>')
    
    return html


def main():
    """Main dashboard generation function."""
    print("=" * 80)
    print("🎨 ADVANCED INTERACTIVE DASHBOARD GENERATOR")
    print("=" * 80)
    
    # Generate regular results
    print("\nGenerating results for standard graphs...")
    regular_results = []
    
    graphs_to_test = {
        # Small graphs where DP can run efficiently (≤10 nodes)
        'Tiny Random G(8,0.3)': generate_erdos_renyi_graph(8, 0.3),
        'Small Dense G(10,0.4)': generate_erdos_renyi_graph(10, 0.4),
        'Complete K(6)': generate_complete_graph(6),
        'Small Sparse G(9,0.2)': generate_erdos_renyi_graph(9, 0.2),
        
        # Medium/Large graphs for other algorithms (DP will be skipped)
        'Medium Random G(30,0.2)': generate_erdos_renyi_graph(30, 0.2),
        'Medium Dense G(40,0.3)': generate_erdos_renyi_graph(40, 0.3), 
        'Large Sparse G(60,0.1)': generate_erdos_renyi_graph(60, 0.1),
        'Dense Graph G(35,0.4)': generate_erdos_renyi_graph(35, 0.4),
        'Karate Club': load_karate_graph(),
        'Complete K(12)': generate_complete_graph(12),
    }

    # --- UPDATED: Define Graph Descriptions ---
    graph_descriptions = {
        'Tiny Random G(8,0.3)': "Random: 8 nodes, Medium density (30%) - DP Included",
        'Small Dense G(10,0.4)': "Random: 10 nodes, Dense (40%) - DP Included",
        'Complete K(6)': "Complete: 6 nodes, Fully Connected - DP Included",
        'Small Sparse G(9,0.2)': "Random: 9 nodes, Sparse (20%) - DP Included",
        
        'Medium Random G(30,0.2)': "Random: 30 nodes, Low density (20%)",
        'Medium Dense G(40,0.3)': "Random: 40 nodes, Medium density (30%)", 
        'Large Sparse G(60,0.1)': "Random: 60 nodes, Sparse (10%)",
        'Dense Graph G(35,0.4)': "Random: 35 nodes, Dense (40%)",
        'Karate Club': "Real-World: 34 nodes, Social Network",
        'Complete K(12)': "Complete: 12 nodes, Fully Connected",
    }
    # ------------------------------------------
    
    algorithms = ["Welsh-Powell", "D-Satur", "Simulated Annealing", "Dynamic Programming"]
    
    for graph_name, G in graphs_to_test.items():
        print(f"  Processing {graph_name}...")
        
        # Get description (fallback if missing)
        desc = graph_descriptions.get(graph_name, f"{G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

        for algo in algorithms:
            result = test_algorithm_on_graph(G, algo)
            if result['error'] is None:
                metrics = compute_all_metrics(
                    G, result['coloring'], algo, 
                    result.get('time', 0.0),
                    result.get('memory_mb', 0.0)
                )
                metrics['graph_name'] = graph_name
                metrics['graph_description'] = desc  # --- UPDATED: Add description to metrics ---
                regular_results.append(metrics)
            else:
                print(f"    Warning: {algo} failed on {graph_name}: {result['error']}")
    
    # Generate edge case results
    print("\nGenerating edge case results...")
    edge_case_results = []
    edge_cases = generate_edge_case_graphs()
    
    for ec_name, G in edge_cases.items():
        print(f"  Processing {ec_name}...")
        ec_data = {
            'graph_name': ec_name,
            'graph_nodes': G.number_of_nodes(),
            'graph_edges': G.number_of_edges(),
            'error': None,
            'has_errors': False,
            'wp_colors': 0,
            'ds_colors': 0,
            'sa_colors': 0,
            'dp_colors': 0,
        }
        
        try:
            wp_result = test_algorithm_on_graph(G, "Welsh-Powell")
            if wp_result['error']:
                ec_data['error'] = wp_result['error']
            else:
                ec_data['wp_colors'] = wp_result['num_colors']
                ec_data['has_errors'] = sum(1 for u, v in G.edges() if wp_result['coloring'].get(u) == wp_result['coloring'].get(v)) > 0
            
            ds_result = test_algorithm_on_graph(G, "D-Satur")
            if not ds_result['error']:
                ec_data['ds_colors'] = ds_result['num_colors']
            
            sa_result = test_algorithm_on_graph(G, "Simulated Annealing")
            if not sa_result['error']:
                ec_data['sa_colors'] = sa_result['num_colors']
            
            if G.number_of_nodes() <= 15:  # DP only for small graphs
                dp_result = test_algorithm_on_graph(G, "Dynamic Programming")
                if not dp_result['error']:
                    ec_data['dp_colors'] = dp_result['num_colors']
        
        except Exception as e:
            ec_data['error'] = str(e)
        
        edge_case_results.append(ec_data)
    
    # Generate 3D data
    print("\nGenerating 3D scalability data...")
    data_3d = generate_3d_data()
    
    # Generate HTML
    print("\nGenerating HTML dashboard...")
    results_data = {
        'regular': regular_results,
        'edge_cases': edge_case_results,
        '3d': data_3d
    }
    
    html_content = generate_advanced_html(results_data)
    
    # Save HTML
    os.makedirs('results', exist_ok=True)
    output_path = 'results/dashboard_advanced.html'
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print("\n" + "=" * 80)
    print(f"✓ Dashboard saved to: {os.path.abspath(output_path)}")
    print("=" * 80)
    print("\n📊 Features included:")
    print("  ✓ 15+ interactive visualizations")
    print("  ✓ 5 tabbed interface (Overview, Analysis, 3D, Edge Cases, Metrics)")
    print("  ✓ 3D scatter plots showing algorithm scalability")
    print("  ✓ 12+ edge case analysis with special graphs")
    print("  ✓ Heatmaps, box plots, distribution analysis")
    print("  ✓ Color imbalance, conflict, and efficiency tracking")
    print("  ✓ Responsive design (works on mobile, tablet, desktop)")
    print("  ✓ Detailed metrics table with 10 columns")
    print("\n🌐 Open in any browser:")
    print(f"  - Chrome/Edge: {os.path.abspath(output_path)}")
    print(f"  - Firefox: {os.path.abspath(output_path)}")
    print(f"  - Safari: {os.path.abspath(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()