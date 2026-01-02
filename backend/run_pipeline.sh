#!/bin/bash
# Run Store Sales Forecasting Pipeline
# This script runs the complete time series forecasting pipeline

echo "================================================================================"
echo "STORE SALES TIME SERIES FORECASTING PIPELINE"
echo "================================================================================"
echo ""

# Check if in backend directory
if [ ! -f "main.py" ]; then
    echo "Error: main.py not found. Make sure you're in the backend directory."
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

echo "Step 1: Checking environment..."
echo ""
python3 check_environment.py
echo ""

echo "================================================================================"
echo "Ready to run the pipeline?"
echo "================================================================================"
echo "This will:"
echo "  1. Load and process all CSV files"
echo "  2. Clean and integrate data"
echo "  3. Engineer features"
echo "  4. Perform clustering"
echo "  5. Train forecasting models"
echo "  6. Evaluate and compare results"
echo ""
echo "This may take 10-30 minutes depending on your system."
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

echo ""
echo "================================================================================"
echo "STARTING PIPELINE..."
echo "================================================================================"
echo ""

# Run the main pipeline
python3 main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "================================================================================"
    echo "SUCCESS: Pipeline completed!"
    echo "================================================================================"
    echo ""
    echo "Results saved to:"
    echo "  - results/model_comparison.csv"
    echo "  - data/processed/ (processed data files)"
    echo ""
else
    echo ""
    echo "================================================================================"
    echo "ERROR: Pipeline failed!"
    echo "================================================================================"
    exit 1
fi
