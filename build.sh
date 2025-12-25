#!/bin/bash
"""
Simple shell script to build Stock Allocation Tool executable.
"""

set -e  # Exit on any error

echo "Stock Allocation Tool - Build Script"
echo "===================================="

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Please run this script from the project root."
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: Virtual environment not detected."
    echo "Please activate your virtual environment first:"
    echo "  source venv/bin/activate"
    exit 1
fi

# Clean previous builds
echo "Cleaning previous build artifacts..."
rm -rf build/ dist/ *.spec

# Install PyInstaller if not present
echo "Checking PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    pip install pyinstaller
fi

# Build the executable
echo "Building executable..."
pyinstaller \
    --onefile \
    --windowed \
    --name "Stock Allocation Tool" \
    --add-data "src:src" \
    --hidden-import yfinance \
    --hidden-import tkinter \
    --clean \
    main.py

# Check if build was successful
if [ -f "dist/Stock Allocation Tool" ] || [ -f "dist/Stock Allocation Tool.exe" ]; then
    echo "✓ Build completed successfully!"
    echo "Executable location: dist/"
    ls -la dist/
else
    echo "✗ Build failed - executable not found"
    exit 1
fi

echo ""
echo "Your executable is ready in the dist/ directory."
echo "Double-click to run, no Python installation required!"