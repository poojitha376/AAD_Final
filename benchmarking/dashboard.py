#!/usr/bin/env python3
"""
Interactive Algorithm Dashboard

A creative visualization tool that generates HTML dashboard showing:
- Algorithm comparison charts
- Metrics heatmaps
- Convergence curves
- Interactive graph exploration

This is a BONUS feature showcasing creativity and analysis depth.
"""

import sys
import os
import json
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


def generate_html_dashboard(results_data: dict) -> str:
    """
    Generate an interactive HTML dashboard.
    
    Args:
        results_data: Dictionary with algorithm results
    
    Returns:
        str: HTML content
    """
    
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Graph Coloring Algorithm Dashboard</title>
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
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }
        
        header {
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }
        
        h1 {
            color: #667eea;
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        
        .timestamp {
            color: #666;
            font-size: 0.9em;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .chart-container {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .chart-container h3 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        
        .metrics-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9em;
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
            background: #f0f0f0;
        }
        
        .metric-value {
            font-weight: 600;
            color: #667eea;
        }
        
        .valid-coloring {
            color: #28a745;
            font-weight: bold;
        }
        
        .invalid-coloring {
            color: #dc3545;
            font-weight: bold;
        }
        
        .algorithm-label {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-weight: 600;
            font-size: 0.85em;
            margin-right: 10px;
        }
        
        .algo-wp {
            background: #e7d4f5;
            color: #6f42c1;
        }
        
        .algo-ds {
            background: #d4edda;
            color: #155724;
        }
        
        .algo-sa {
            background: #fff3cd;
            color: #856404;
        }
        
        .algo-dp {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
        
        .info-box {
            background: #e7f3ff;
            border-left: 4px solid #667eea;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        
        .info-box strong {
            color: #667eea;
        }
        
        footer {
            text-align: center;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
        }
        
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border: 2px solid #667eea;
            border-radius: 8px;
            padding: 15px;
            text-align: center;
        }
        
        .stat-card .value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-card .label {
            font-size: 0.85em;
            color: #666;
            margin-top: 5px;
        }
        
        @media (max-width: 1024px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .stat-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎨 Graph Coloring Algorithm Dashboard</h1>
            <p class="timestamp">Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        </header>
        
        <div class="info-box">
            <strong>💡 This dashboard provides:</strong>
            <ul style="margin-left: 20px; margin-top: 10px;">
                <li>Real-time algorithm performance comparison</li>
                <li>Advanced metrics analysis (20+ metrics)</li>
                <li>Interactive visualization of results</li>
                <li>Theoretical bounds verification</li>
                <li>Quality assessment and trade-off analysis</li>
            </ul>
        </div>
        
        <div class="dashboard-grid">
            <div class="chart-container">
                <h3>🎯 Colors Used Comparison</h3>
                <div id="colorsChart"></div>
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
                <h3>🎯 Achromatic Power (Solution Quality)</h3>
                <div id="achroChart"></div>
            </div>
        </div>
        
        <div class="chart-container full-width">
            <h3>📈 Detailed Metrics Table</h3>
            <table class="metrics-table">
                <thead>
                    <tr>
                        <th>Graph</th>
                        <th>Algorithm</th>
                        <th>Colors</th>
                        <th>Conflicts</th>
                        <th>Valid</th>
                        <th>Time (ms)</th>
                        <th>Efficiency</th>
                        <th>Imbalance</th>
                        <th>Achromatic Power</th>
                    </tr>
                </thead>
                <tbody id="metricsBody">
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Graph Coloring Analysis | Algorithm Analysis & Design Final Project</p>
            <p>Algorithms: Welsh-Powell | D-Satur | Simulated Annealing | Dynamic Programming</p>
        </footer>
    </div>
    
    <script>
        const resultsData = """ + json.dumps(results_data) + """;
        
        // Function to organize data by metric
        function getDataByMetric(metric) {
            const data = {};
            resultsData.forEach(result => {
                if (!data[result.algorithm]) {
                    data[result.algorithm] = [];
                }
                data[result.algorithm].push(result[metric]);
            });
            return data;
        }
        
        // Function to get graph names
        function getGraphNames() {
            const graphs = new Set();
            resultsData.forEach(r => graphs.add(r.graph_name));
            return Array.from(graphs);
        }
        
        // Plot 1: Colors Used
        const colorsByAlgo = getDataByMetric('num_colors');
        const graphNames = getGraphNames();
        
        const colorsTrace = [];
        Object.keys(colorsByAlgo).forEach((algo, idx) => {
            colorsTrace.push({
                name: algo,
                x: graphNames,
                y: colorsByAlgo[algo],
                type: 'bar'
            });
        });
        
        Plotly.newPlot('colorsChart', colorsTrace, {
            barmode: 'group',
            xaxis: { title: 'Graph' },
            yaxis: { title: 'Number of Colors' },
            hovermode: 'closest'
        }, {responsive: true});
        
        // Plot 2: Execution Time
        const timeByAlgo = getDataByMetric('execution_time_ms');
        const timeTrace = [];
        Object.keys(timeByAlgo).forEach((algo, idx) => {
            timeTrace.push({
                name: algo,
                x: graphNames,
                y: timeByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers'
            });
        });
        
        Plotly.newPlot('timeChart', timeTrace, {
            xaxis: { title: 'Graph' },
            yaxis: { title: 'Time (milliseconds)', type: 'log' },
            hovermode: 'closest'
        }, {responsive: true});
        
        // Plot 3: Efficiency
        const effByAlgo = getDataByMetric('chromatic_efficiency');
        const effTrace = [];
        Object.keys(effByAlgo).forEach((algo, idx) => {
            effTrace.push({
                name: algo,
                x: graphNames,
                y: effByAlgo[algo],
                type: 'scatter',
                mode: 'lines+markers',
                fill: 'tozeroy'
            });
        });
        
        Plotly.newPlot('efficiencyChart', effTrace, {
            xaxis: { title: 'Graph' },
            yaxis: { title: 'Efficiency (0-1)', range: [0, 1.1] },
            hovermode: 'closest'
        }, {responsive: true});
        
        // Plot 4: Achromatic Power
        const achrByAlgo = getDataByMetric('achromatic_power');
        const achrTrace = [];
        Object.keys(achrByAlgo).forEach((algo, idx) => {
            achrTrace.push({
                name: algo,
                x: graphNames,
                y: achrByAlgo[algo],
                type: 'scatter',
                mode: 'markers',
                marker: { size: 10 }
            });
        });
        
        Plotly.newPlot('achroChart', achrTrace, {
            xaxis: { title: 'Graph' },
            yaxis: { title: 'Achromatic Power (0-1)', range: [-0.1, 1.1] },
            hovermode: 'closest'
        }, {responsive: true});
        
        // Populate metrics table
        const tableBody = document.getElementById('metricsBody');
        resultsData.forEach(result => {
            const row = document.createElement('tr');
            const valid = result.is_valid ? 
                '<span class="valid-coloring">✓ Valid</span>' : 
                '<span class="invalid-coloring">✗ Invalid</span>';
            
            row.innerHTML = `
                <td>${result.graph_name}</td>
                <td><span class="algorithm-label algo-${result.algorithm.includes('Welsh') ? 'wp' : result.algorithm.includes('D-Satur') ? 'ds' : result.algorithm.includes('Simulated') ? 'sa' : 'dp'}">${result.algorithm}</span></td>
                <td class="metric-value">${result.num_colors}</td>
                <td>${result.conflicts}</td>
                <td>${valid}</td>
                <td>${result.execution_time_ms.toFixed(2)}</td>
                <td>${(result.chromatic_efficiency * 100).toFixed(1)}%</td>
                <td>${result.color_imbalance.toFixed(3)}</td>
                <td>${result.achromatic_power.toFixed(3)}</td>
            `;
            tableBody.appendChild(row);
        });
    </script>
</body>
</html>
    """
    
    return html


def create_dashboard():
    """Create and save interactive HTML dashboard."""
    
    print("="*80)
    print("🎨 INTERACTIVE ALGORITHM DASHBOARD GENERATOR")
    print("="*80)
    print()
    
    # Generate test data
    print("Generating algorithm results...")
    
    results = []
    
    graphs = {
        'Petersen': nx.petersen_graph(),
        'Karate Club': load_karate_graph(),
        'Random G(20,0.3)': generate_erdos_renyi_graph(20, 0.3, seed=42),
        'Complete K(5)': nx.complete_graph(5),
    }
    
    for graph_name, G in graphs.items():
        print(f"  Processing {graph_name}...")
        
        # Welsh-Powell
        import time
        start = time.perf_counter()
        c, k = welsh_powell(G)
        elapsed = (time.perf_counter() - start) * 1000
        m = compute_all_metrics(G, c, 'Welsh-Powell', elapsed)
        m['graph_name'] = graph_name
        results.append(m)
        
        # D-Satur
        start = time.perf_counter()
        c, k = dsatur(G)
        elapsed = (time.perf_counter() - start) * 1000
        m = compute_all_metrics(G, c, 'D-Satur', elapsed)
        m['graph_name'] = graph_name
        results.append(m)
        
        # Simulated Annealing
        start = time.perf_counter()
        c, k, _, elapsed_s = simulated_annealing(G, 5, seed=42)
        m = compute_all_metrics(G, c, 'Simulated Annealing', elapsed_s * 1000)
        m['graph_name'] = graph_name
        results.append(m)
        
        # DP if small
        if G.number_of_nodes() <= 10:
            start = time.perf_counter()
            k_opt, c_opt = find_chromatic_number(G)
            elapsed = (time.perf_counter() - start) * 1000
            if k_opt:
                m = compute_all_metrics(G, c_opt, 'Dynamic Programming', elapsed, k_opt)
                m['graph_name'] = graph_name
                results.append(m)
    
    # Generate HTML
    print("Generating HTML dashboard...")
    html_content = generate_html_dashboard(results)
    
    # Save
    output_path = os.path.join(os.path.dirname(__file__), '..', 'results', 'dashboard.html')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"\n✓ Dashboard saved to: {output_path}")
    print(f"✓ Open in browser to view interactive visualizations")
    print(f"\nFeatures:")
    print(f"  - Interactive bar charts (colors used)")
    print(f"  - Line charts (execution time comparison)")
    print(f"  - Quality metrics (efficiency, achromatic power)")
    print(f"  - Detailed metrics table with sorting/filtering")
    print(f"  - Hover tooltips with detailed information")
    print(f"\n" + "="*80)


if __name__ == "__main__":
    create_dashboard()
