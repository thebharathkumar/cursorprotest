#!/bin/bash

# ATS Resume Scoring Agent - Startup Script

echo "=============================================="
echo "  ATS Resume Scoring Agent"
echo "=============================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if dependencies are installed
if ! python3 -c "import fastapi" &> /dev/null; then
    echo ""
    echo "Installing dependencies..."
    pip install -q -r requirements.txt
    echo "✓ Dependencies installed"
fi

echo ""
echo "Starting ATS Resume Scoring Agent..."
echo ""
echo "Access the application at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=============================================="
echo ""

# Start the application
python3 main.py
