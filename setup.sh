#!/bin/bash

# Setup script for MCP Unstructured Server

set -e

echo "Setting up MCP Unstructured Server..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV not found. Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "Please restart your shell or run: source ~/.bashrc"
    echo "Then run this script again."
    exit 1
fi

echo "UV is installed. Creating virtual environment..."

# Create virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate

echo "Installing dependencies..."

# Install the package in development mode
uv pip install -e .

echo "Installation complete!"
echo ""
echo "To activate the virtual environment, run:"
echo "source .venv/bin/activate"
echo ""
echo "To run the server, use:"
echo "python -m mcp_unstructured.server"
echo ""
echo "To run tests, use:"
echo "pytest"
echo ""
echo "To run the example, use:"
echo "python examples/basic_usage.py" 