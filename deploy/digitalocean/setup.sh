#!/bin/bash
#
# Setup script for Digital Ocean deployment
# Run this once after copying files to server
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "MIZRAHI COMPLIANCE - SETUP"
echo "=========================================="
echo ""

# Create directories
echo "Creating directories..."
mkdir -p "$SCRIPT_DIR/output/hook1"
mkdir -p "$SCRIPT_DIR/output/hook2"
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/config"

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
fi

# Activate and install dependencies
echo "Installing Python dependencies..."
source "$SCRIPT_DIR/venv/bin/activate"
pip install --upgrade pip
pip install pandas openpyxl requests

# Make scripts executable
echo "Making scripts executable..."
chmod +x "$SCRIPT_DIR"/*.sh
chmod +x "$SCRIPT_DIR/scripts"/*.py

# Create credentials file if it doesn't exist
if [ ! -f "$SCRIPT_DIR/config/credentials.env" ]; then
    echo "Creating credentials template..."
    cp "$SCRIPT_DIR/config/credentials.env.example" "$SCRIPT_DIR/config/credentials.env"
    echo ""
    echo "IMPORTANT: Edit config/credentials.env with your API keys!"
    echo "  nano $SCRIPT_DIR/config/credentials.env"
fi

echo ""
echo "=========================================="
echo "SETUP COMPLETE"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit config/credentials.env with your API keys"
echo "2. Test Hook 1: ./run_hook1.sh --fund-name 'סיגמא'"
echo "3. Test Hook 2: ./run_hook2.sh --managers 'סיגמא'"
echo ""
