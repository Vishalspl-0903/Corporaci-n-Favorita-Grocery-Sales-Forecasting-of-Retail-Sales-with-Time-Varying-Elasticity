@echo off
REM Run Store Sales Forecasting Pipeline
REM This script runs the complete time series forecasting pipeline

echo ================================================================================
echo STORE SALES TIME SERIES FORECASTING PIPELINE
echo ================================================================================
echo.

REM Check if in backend directory
if not exist "main.py" (
    echo Error: main.py not found. Make sure you're in the backend directory.
    pause
    exit /b 1
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher.
    pause
    exit /b 1
)

echo Step 1: Checking environment...
echo.
python check_environment.py
echo.

echo ================================================================================
echo Ready to run the pipeline?
echo ================================================================================
echo This will:
echo   1. Load and process all CSV files
echo   2. Clean and integrate data
echo   3. Engineer features
echo   4. Perform clustering
echo   5. Train forecasting models
echo   6. Evaluate and compare results
echo.
echo This may take 10-30 minutes depending on your system.
echo.
pause

echo.
echo ================================================================================
echo STARTING PIPELINE...
echo ================================================================================
echo.

REM Run the main pipeline
python main.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo ERROR: Pipeline failed!
    echo ================================================================================
    pause
    exit /b 1
) else (
    echo.
    echo ================================================================================
    echo SUCCESS: Pipeline completed!
    echo ================================================================================
    echo.
    echo Results saved to:
    echo   - results/model_comparison.csv
    echo   - data/processed/ (processed data files)
    echo.
    pause
)
