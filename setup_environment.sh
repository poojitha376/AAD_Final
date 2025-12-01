#!/bin/bash
# Setup script for hybrid algorithms benchmarking

echo "╔══════════════════════════════════════════════════════════════════════╗"
echo "║         Hybrid Algorithms - Environment Setup                       ║"
echo "╚══════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Try to install NetworkX
echo ""
echo "Installing required packages..."
echo "Attempting: pip3 install networkx matplotlib numpy"
echo ""

# Try different installation methods
if pip3 install networkx matplotlib numpy 2>/dev/null; then
    echo "✓ Packages installed successfully with pip3"
elif pip3 install --user networkx matplotlib numpy 2>/dev/null; then
    echo "✓ Packages installed successfully with pip3 --user"
elif python3 -m pip install --user networkx matplotlib numpy 2>/dev/null; then
    echo "✓ Packages installed successfully with python3 -m pip --user"
else
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "⚠️  Automatic installation failed. Please try one of these manually:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Option 1: Using pip with --break-system-packages (if you understand the risks)"
    echo "  pip3 install --break-system-packages networkx matplotlib numpy"
    echo ""
    echo "Option 2: Create a virtual environment (recommended)"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo "  pip install networkx matplotlib numpy"
    echo ""
    echo "Option 3: Install system packages (Ubuntu/Debian)"
    echo "  sudo apt-get install python3-networkx python3-matplotlib python3-numpy"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    exit 1
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Verifying installation..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if python3 -c "import networkx; print('✓ NetworkX version:', networkx.__version__)" 2>/dev/null; then
    echo "✓ Installation successful!"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Setup Complete! You can now run:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  python3 quick_test_hybrid.py        # Quick test (~1 min)"
    echo "  python3 run_hybrid_benchmarks.py    # Full benchmark (~10 min)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
else
    echo "✗ Installation verification failed"
    exit 1
fi
