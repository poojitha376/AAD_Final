#!/bin/bash

# Quick Start Guide for Graph Coloring Project
# Run this script to set up and test the project

set -e  # Exit on error

echo "============================================"
echo "Graph Coloring Project - Quick Start"
echo "============================================"
echo ""

# Check Python installation
echo "Checking Python version..."
python3 --version
echo ""

# Install dependencies
echo "Installing dependencies..."
pip3 install -r Requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"
echo ""

# Run correctness tests
echo "Running correctness tests..."
python3 -m benchmarking.test_correctness
echo ""

# Run a quick benchmark sample
echo ""
echo "Running benchmark sample (this may take a minute)..."
timeout 120 python3 benchmarking/run_experiments.py | head -60
echo ""
echo "✓ Project is working correctly!"
echo ""
echo "Next steps:"
echo "  1. Review results in results/data/benchmark_results.csv"
echo "  2. See Makefile for more commands: make help"
echo "  3. Read README.md for detailed documentation"
echo ""
