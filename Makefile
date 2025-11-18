.PHONY: help install test benchmark clean all

# Python interpreter
PYTHON := python3
PIP := pip3

# Project directories
SRC_DIR := src
BENCH_DIR := benchmarking
RESULTS_DIR := results

help:
	@echo "Graph Coloring Project - Available Commands"
	@echo "============================================"
	@echo ""
	@echo "make install      - Install project dependencies"
	@echo "make test         - Run correctness tests on known graphs"
	@echo "make benchmark    - Run full benchmarking suite"
	@echo "make metrics      - Run advanced metrics analysis"
	@echo "make dashboard    - Generate interactive dashboard (BONUS)"
	@echo "make clean        - Remove generated files and cache"
	@echo "make all          - Install, test, benchmark, metrics, dashboard"
	@echo ""

install:
	@echo "Installing dependencies..."
	$(PIP) install -r Requirements.txt
	@echo "✓ Installation complete"

test:
	@echo "Running correctness tests..."
	@echo "===================================="
	$(PYTHON) -m $(BENCH_DIR).test_correctness
	@echo "===================================="
	@echo "✓ Tests complete"

benchmark:
	@echo "Running benchmarking suite..."
	@echo "===================================="
	@mkdir -p $(RESULTS_DIR)/data
	@mkdir -p $(RESULTS_DIR)/plots
	$(PYTHON) $(BENCH_DIR)/run_experiments.py
	@echo "===================================="
	@echo "✓ Benchmarks complete"
	@echo "Results saved to: $(RESULTS_DIR)/"

metrics:
	@echo "Running advanced metrics analysis..."
	@echo "===================================="
	@mkdir -p $(RESULTS_DIR)/data
	$(PYTHON) $(BENCH_DIR)/metrics_analysis.py
	@echo "===================================="
	@echo "✓ Metrics analysis complete"
	@echo "Results saved to: $(RESULTS_DIR)/data/detailed_metrics.csv"

dashboard:
	@echo "Generating interactive dashboard..."
	@echo "===================================="
	@mkdir -p $(RESULTS_DIR)
	$(PYTHON) $(BENCH_DIR)/dashboard.py
	@echo "✓ Dashboard created: $(RESULTS_DIR)/dashboard.html"
	@echo "Open in browser to view interactive visualizations"

# Clean up generated files
clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	@echo "✓ Cache cleaned"

# Run all: install -> test -> benchmark -> metrics -> dashboard
all: install test benchmark metrics dashboard
	@echo ""
	@echo "========================================"
	@echo "All tasks completed successfully!"
	@echo "========================================"
	@echo ""
	@echo "Results available at:"
	@echo "  - Benchmark data: $(RESULTS_DIR)/data/benchmark_results.csv"
	@echo "  - Metrics data: $(RESULTS_DIR)/data/detailed_metrics.csv"
	@echo "  - Dashboard: $(RESULTS_DIR)/dashboard.html"
	@echo "  - Plots: $(RESULTS_DIR)/plots/"

# Development helper targets
format:
	@echo "Formatting code..."
	$(PYTHON) -m black $(SRC_DIR) $(BENCH_DIR) || true

lint:
	@echo "Running linting checks..."
	$(PYTHON) -m pylint $(SRC_DIR) || true

# Run specific tests
test-triangle:
	@echo "Testing triangle (K3)..."
	$(PYTHON) -c "from $(BENCH_DIR).test_correctness import test_triangle; test_triangle()"

test-karate:
	@echo "Testing Karate Club..."
	$(PYTHON) -c "from $(BENCH_DIR).test_correctness import test_karate_club; test_karate_club()"

# Algorithm-specific tests
test-welsh-powell:
	@$(PYTHON) -c "import sys; sys.path.insert(0, '.'); from src.algorithms.welshpowell import welsh_powell; from src.utils.graph_generator import generate_erdos_renyi_graph; G = generate_erdos_renyi_graph(20, 0.3); coloring, k = welsh_powell(G); print(f'Welsh-Powell: {k} colors')"

test-dsatur:
	@$(PYTHON) -c "import sys; sys.path.insert(0, '.'); from src.algorithms.dsatur import dsatur; from src.utils.graph_generator import generate_erdos_renyi_graph; G = generate_erdos_renyi_graph(20, 0.3); coloring, k = dsatur(G); print(f'D-Satur: {k} colors')"

test-sa:
	@$(PYTHON) -c "import sys; sys.path.insert(0, '.'); from src.algorithms.simulated_annealing import simulated_annealing; from src.utils.graph_generator import generate_erdos_renyi_graph; G = generate_erdos_renyi_graph(20, 0.3); coloring, k, _, t = simulated_annealing(G, 5); print(f'SA: {k} colors in {t:.3f}s')"

test-dp:
	@$(PYTHON) -c "import sys; sys.path.insert(0, '.'); from src.algorithms.dynamic_programming import find_chromatic_number; from src.utils.graph_generator import generate_erdos_renyi_graph; G = generate_erdos_renyi_graph(10, 0.3); k, _ = find_chromatic_number(G); print(f'DP: chromatic number = {k}')"
