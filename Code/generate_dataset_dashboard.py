#!/usr/bin/env python3
"""
Generate Interactive Dashboard from Your Dataset Results
Reads results/data/your_datasets_results.csv and creates comprehensive visualizations
"""

import csv
import json
from datetime import datetime

def load_dataset_results(csv_path):
    """Load results from CSV file."""
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
    return results

def organize_data(results):
    """Organize data by dataset and algorithm."""
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
    
    return datasets, sorted(list(algorithms))

def generate_html(results, datasets, algorithms):
    """Generate comprehensive HTML dashboard."""
    
    # Prepare data for charts
    dataset_names = list(datasets.keys())
    
    # Colors comparison data
    colors_data = []
    for algo in algorithms:
        colors_data.append({
            'x': dataset_names,
            'y': [datasets[ds].get(algo, {}).get('colors', 0) for ds in dataset_names],
            'name': algo,
            'type': 'bar'
        })
    
    # Time comparison data
    time_data = []
    for algo in algorithms:
        time_data.append({
            'x': dataset_names,
            'y': [datasets[ds].get(algo, {}).get('time', 0) * 1000 for ds in dataset_names],  # Convert to ms
            'name': algo,
            'type': 'bar'
        })
    
    # Per-dataset comparison
    dataset_comparisons = {}
    for ds_name in dataset_names:
        ds_data = datasets[ds_name]
        dataset_comparisons[ds_name] = {
            'algorithms': list(ds_data.keys()),
            'colors': [ds_data[algo]['colors'] for algo in ds_data.keys()],
            'times': [ds_data[algo]['time'] * 1000 for algo in ds_data.keys()]
        }
    
    # Algorithm performance summary
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
                'max_colors': max(colors_list),
                'datasets_tested': len(colors_list)
            }
    
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 Dataset Results Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        h1 {{
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .subtitle {{
            font-size: 1.2em;
            opacity: 0.95;
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section-title {{
            color: #667eea;
            font-size: 1.8em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 8px;
        }}
        
        .stat-label {{
            font-size: 1em;
            opacity: 0.95;
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .chart-container {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .chart-container h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .chart-full {{
            grid-column: 1 / -1;
        }}
        
        .dataset-cards {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .dataset-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .dataset-card h3 {{
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }}
        
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 0.95em;
        }}
        
        .metrics-table th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .metrics-table td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
        }}
        
        .metrics-table tr:hover {{
            background: #f5f5f5;
        }}
        
        .best {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .worst {{
            color: #dc3545;
        }}
        
        footer {{
            background: #f5f5f5;
            padding: 25px;
            text-align: center;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        
        @media (max-width: 1200px) {{
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
            
            .dataset-cards {{
                grid-template-columns: 1fr;
            }}
            
            .stat-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📊 Graph Coloring Algorithms - Dataset Results</h1>
            <p class="subtitle">Comprehensive Analysis of {len(algorithms)} Algorithms on {len(dataset_names)} Real-World Datasets</p>
            <p class="subtitle" style="font-size: 0.9em; margin-top: 10px;">Generated on {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}</p>
        </header>
        
        <div class="content">
            <!-- Summary Statistics -->
            <div class="section">
                <h2 class="section-title">📈 Summary Statistics</h2>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-value">{len(algorithms)}</div>
                        <div class="stat-label">Algorithms Tested</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(dataset_names)}</div>
                        <div class="stat-label">Datasets Analyzed</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{len(results)}</div>
                        <div class="stat-label">Total Experiments</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">{sum(1 for r in results if r['valid'])}/{len(results)}</div>
                        <div class="stat-label">Valid Colorings</div>
                    </div>
                </div>
            </div>
            
            <!-- Overall Comparisons -->
            <div class="section">
                <h2 class="section-title">🎯 Algorithm Comparison Across All Datasets</h2>
                <div class="chart-grid">
                    <div class="chart-container">
                        <h3>Colors Used by Algorithm</h3>
                        <div id="colors-comparison"></div>
                    </div>
                    <div class="chart-container">
                        <h3>Execution Time by Algorithm (ms)</h3>
                        <div id="time-comparison"></div>
                    </div>
                </div>
            </div>
            
            <!-- Per-Dataset Analysis -->
            <div class="section">
                <h2 class="section-title">📊 Individual Dataset Analysis</h2>
                <div class="dataset-cards">
"""
    
    # Add individual dataset cards
    for ds_name in dataset_names:
        ds_data = datasets[ds_name]
        best_colors = min(ds_data[algo]['colors'] for algo in ds_data.keys())
        fastest_time = min(ds_data[algo]['time'] for algo in ds_data.keys())
        
        html += f"""
                    <div class="dataset-card">
                        <h3>🗂️ {ds_name}</h3>
                        <div id="dataset-{dataset_names.index(ds_name)}-colors"></div>
                        <div id="dataset-{dataset_names.index(ds_name)}-time" style="margin-top: 20px;"></div>
                    </div>
"""
    
    html += """
                </div>
            </div>
            
            <!-- Algorithm Performance Summary -->
            <div class="section">
                <h2 class="section-title">📋 Algorithm Performance Summary</h2>
                <div class="chart-container">
                    <table class="metrics-table">
                        <thead>
                            <tr>
                                <th>Algorithm</th>
                                <th>Avg Colors</th>
                                <th>Min Colors</th>
                                <th>Max Colors</th>
                                <th>Avg Time (ms)</th>
                                <th>Datasets</th>
                            </tr>
                        </thead>
                        <tbody>
"""
    
    # Add algorithm stats rows
    for algo in sorted(algorithms):
        if algo in algo_stats:
            stats = algo_stats[algo]
            avg_colors = stats['avg_colors']
            best_avg = min(algo_stats[a]['avg_colors'] for a in algo_stats.keys())
            color_class = 'best' if avg_colors == best_avg else ''
            
            html += f"""
                            <tr>
                                <td><strong>{algo}</strong></td>
                                <td class="{color_class}">{avg_colors:.2f}</td>
                                <td>{stats['min_colors']}</td>
                                <td>{stats['max_colors']}</td>
                                <td>{stats['avg_time']*1000:.4f}</td>
                                <td>{stats['datasets_tested']}</td>
                            </tr>
"""
    
    html += """
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- Detailed Results Table -->
            <div class="section">
                <h2 class="section-title">📝 Complete Results Table</h2>
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
    
    # Add all results
    for r in results:
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
            </div>
        </div>
        
        <footer>
            <p><strong>Graph Coloring Algorithms Dashboard</strong></p>
            <p>Generated from: results/data/your_datasets_results.csv</p>
            <p>Total Algorithms: {len(algorithms)} | Total Datasets: {len(dataset_names)} | Total Tests: {len(results)}</p>
        </footer>
    </div>
    
    <script>
        // Overall Colors Comparison
        var colorsData = {json.dumps(colors_data)};
        var colorsLayout = {{
            barmode: 'group',
            xaxis: {{ title: 'Dataset' }},
            yaxis: {{ title: 'Number of Colors' }},
            legend: {{ orientation: 'h', y: -0.2 }},
            margin: {{ t: 20, b: 100 }}
        }};
        Plotly.newPlot('colors-comparison', colorsData, colorsLayout, {{responsive: true}});
        
        // Overall Time Comparison
        var timeData = {json.dumps(time_data)};
        var timeLayout = {{
            barmode: 'group',
            xaxis: {{ title: 'Dataset' }},
            yaxis: {{ title: 'Time (ms)', type: 'log' }},
            legend: {{ orientation: 'h', y: -0.2 }},
            margin: {{ t: 20, b: 100 }}
        }};
        Plotly.newPlot('time-comparison', timeData, timeLayout, {{responsive: true}});
"""
    
    # Add individual dataset charts
    for i, ds_name in enumerate(dataset_names):
        ds_comp = dataset_comparisons[ds_name]
        
        html += f"""
        
        // {ds_name} - Colors
        var ds{i}ColorsData = [{{
            x: {json.dumps(ds_comp['algorithms'])},
            y: {json.dumps(ds_comp['colors'])},
            type: 'bar',
            marker: {{ color: '#667eea' }}
        }}];
        var ds{i}ColorsLayout = {{
            xaxis: {{ title: 'Algorithm' }},
            yaxis: {{ title: 'Colors' }},
            margin: {{ t: 20, b: 80, l: 50, r: 20 }}
        }};
        Plotly.newPlot('dataset-{i}-colors', ds{i}ColorsData, ds{i}ColorsLayout, {{responsive: true}});
        
        // {ds_name} - Time
        var ds{i}TimeData = [{{
            x: {json.dumps(ds_comp['algorithms'])},
            y: {json.dumps(ds_comp['times'])},
            type: 'bar',
            marker: {{ color: '#764ba2' }}
        }}];
        var ds{i}TimeLayout = {{
            xaxis: {{ title: 'Algorithm' }},
            yaxis: {{ title: 'Time (ms)', type: 'log' }},
            margin: {{ t: 20, b: 80, l: 50, r: 20 }}
        }};
        Plotly.newPlot('dataset-{i}-time', ds{i}TimeData, ds{i}TimeLayout, {{responsive: true}});
"""
    
    html += """
    </script>
</body>
</html>
"""
    
    return html

def main():
    print("\n" + "="*80)
    print("📊 GENERATING DATASET RESULTS DASHBOARD")
    print("="*80)
    
    csv_path = 'results/data/your_datasets_results.csv'
    output_path = 'results/dataset_dashboard.html'
    
    print(f"\n📂 Loading data from: {csv_path}")
    results = load_dataset_results(csv_path)
    print(f"   ✓ Loaded {len(results)} results")
    
    print(f"\n🔄 Organizing data...")
    datasets, algorithms = organize_data(results)
    print(f"   ✓ Found {len(datasets)} datasets")
    print(f"   ✓ Found {len(algorithms)} algorithms")
    
    print(f"\n🎨 Generating HTML dashboard...")
    html = generate_html(results, datasets, algorithms)
    
    print(f"\n💾 Saving to: {output_path}")
    with open(output_path, 'w') as f:
        f.write(html)
    
    print("\n" + "="*80)
    print("✅ DASHBOARD GENERATED SUCCESSFULLY!")
    print("="*80)
    print(f"\n📍 Open this file in your browser:")
    print(f"   {output_path}")
    print()

if __name__ == '__main__':
    main()
