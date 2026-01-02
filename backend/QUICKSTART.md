# Quick Start Guide

## Getting Started in 5 Minutes

### Step 1: Install Dependencies

```bash
# Navigate to backend folder
cd backend

# Install required packages
pip install -r requirements.txt
```

### Step 2: Check Environment

```bash
# Verify all dependencies are installed
python check_environment.py
```

### Step 3: Run the Pipeline

```bash
# Execute the complete pipeline
python main.py
```

That's it! The pipeline will:
1. Load and process all data files
2. Clean and integrate datasets
3. Engineer features
4. Perform clustering
5. Train multiple models
6. Evaluate and compare results

### Expected Output

```
================================================================================
STORE SALES TIME SERIES FORECASTING PIPELINE
================================================================================
Start time: 2026-01-02 10:30:00
================================================================================

STEP 1: DISTRIBUTED DATA INGESTION
...
Data ingestion completed successfully!

STEP 2: DATA CLEANING & INTEGRATION
...
Data cleaning completed successfully!

STEP 3: FEATURE ENGINEERING
...
Feature engineering completed successfully!

STEP 4: CLUSTERING
...
Clustering completed successfully!

STEP 5: FORECASTING MODELS
...
MODEL COMPARISON
model                        SMAPE       RMSE       MAE
Gradient Boosted Trees      45.23      12.45      8.67
LSTM Neural Network         48.12      13.21      9.12
ARIMA                       52.34      15.67     10.45

PIPELINE COMPLETED SUCCESSFULLY!
Total execution time: 15.32 minutes
```

## View Results

After the pipeline completes:

1. **Model Comparison**
   - Check `results/model_comparison.csv`

2. **Processed Data**
   - All processed data in `data/processed/` folder

3. **Visualize Results**
   ```python
   from utils import visualize_results
   visualize_results('results/model_comparison.csv')
   ```

## Troubleshooting

### Issue: Java not found
**Solution**: Install JDK 8 or 11 and set JAVA_HOME
```bash
# Windows
setx JAVA_HOME "C:\Program Files\Java\jdk-11"

# Mac/Linux
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

### Issue: Out of memory
**Solution**: Reduce Spark memory in config.py
```python
SPARK_MEMORY = "2g"  # Reduce from 4g to 2g
```

### Issue: Package installation fails
**Solution**: Install packages individually
```bash
pip install pyspark pandas numpy scikit-learn
pip install tensorflow statsmodels matplotlib seaborn
pip install pyarrow fastparquet
```

## Tips

1. **First run takes longer** - Spark initialization and data processing
2. **Subsequent runs are faster** - Processed data is cached in Parquet
3. **Monitor memory usage** - Reduce SPARK_MEMORY if needed
4. **Check logs** - Detailed information printed during execution

## Next Steps

- Tune model hyperparameters in `config.py`
- Add more features in `feature_engineering/features.py`
- Try different clustering algorithms in `clustering/cluster.py`
- Experiment with ensemble methods

## Key Files

- `main.py` - Main pipeline orchestrator
- `config.py` - All configuration settings
- `requirements.txt` - Python dependencies
- `README.md` - Complete documentation

Happy Forecasting!
