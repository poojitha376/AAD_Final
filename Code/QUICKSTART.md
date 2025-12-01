# Quick Start Guide

## Installation (1 minute)

```bash
# Clone repository
git clone https://github.com/poojitha376/AAD_Final.git
cd AAD_Final

# Install dependencies (Ubuntu/Debian)
sudo apt-get install -y python3-networkx python3-matplotlib python3-numpy

# Verify
python3 -c "import networkx, matplotlib; print('✓ Ready!')"
```

## Run Everything (3 commands)

```bash
# 1. Run benchmarks on all datasets
python3 run_on_your_data.py

# 2. Generate interactive dashboard
python3 generate_dataset_dashboard.py

# 3. Open dashboard in browser
xdg-open results/dataset_dashboard.html
```

## Use Individual Algorithms

```python
import networkx as nx
from src.algorithms import welsh_powell, dsatur, hybrid_dsatur_sa

# Create a graph
G = nx.karate_club_graph()

# Run algorithms
coloring_wp, colors_wp = welsh_powell(G)
coloring_ds, colors_ds = dsatur(G)
coloring_hy, colors_hy, stats = hybrid_dsatur_sa(G)

print(f"Welsh-Powell: {colors_wp} colors")
print(f"DSatur: {colors_ds} colors")
print(f"Hybrid: {colors_hy} colors (saved {stats['reduction']})")
```

## File Locations

| What | Where |
|------|-------|
| Algorithms | `src/algorithms/*.py` |
| Datasets | `data/dimacs/` and `data/real-world/` |
| Results | `results/data/your_datasets_results.csv` |
| Dashboard | `results/dataset_dashboard.html` |
| Tests | `benchmarking/test_*.py` |

## Quick Commands

```bash
# Test algorithms
python3 benchmarking/test_correctness.py

# Run map visualizations
cd results/maps
python3 dsatur.py
python3 welsh_powell.py
python3 simulated_annealing.py

# Advanced dashboard
python3 benchmarking/dashboard_advanced.py
```

## Help

- Full documentation: `README.md`
- Compliance checklist: `REPOSITORY_COMPLIANCE.md`
- Hybrid algorithms guide: `HYBRID_README.md`
