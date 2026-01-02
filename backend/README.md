# Store Sales Time Series Forecasting Pipeline

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PySpark](https://img.shields.io/badge/PySpark-3.5.0-orange.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15.0-FF6F00.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3.2-F7931E.svg)

A complete Big Data Analytics pipeline for time series forecasting of store sales using distributed computing (Apache Spark) and machine learning.

## Project Overview

This project implements an end-to-end pipeline for forecasting retail store sales using:
- **Distributed Data Processing** with Apache Spark
- **Advanced Feature Engineering** (lag features, rolling statistics, holiday impacts)
- **Clustering Analysis** (item and store segmentation)
- **Multiple Forecasting Models** (SARIMAX, GBT, LSTM, ARIMA)
- **Comprehensive Evaluation** (SMAPE, RMSE, MAE)

## Dataset

The project uses the following datasets:
- `train.csv` - Daily sales for thousands of stores & items
- `test.csv` - Data for forecasting horizon
- `items.csv` - Item metadata
- `stores.csv` - Store metadata (cluster, family, city)
- `holidays_events.csv` - National holidays, type of event
- `oil.csv` - Economic indicator (Ecuador oil price)
- `transactions.csv` - Store-level transactions

## Project Structure

```
backend/
├── config.py                      # Configuration settings
├── requirements.txt               # Python dependencies
├── main.py                        # Main pipeline orchestrator
├── data/                          # Data storage
│   └── processed/                 # Processed parquet files
├── data_ingestion/               # Step 1: Load CSVs with Spark
│   ├── __init__.py
│   └── ingest.py
├── data_cleaning/                # Step 2: Clean & integrate data
│   ├── __init__.py
│   └── clean.py
├── feature_engineering/          # Step 3: Create features
│   ├── __init__.py
│   └── features.py
├── clustering/                   # Step 4: Item & store clustering
│   ├── __init__.py
│   └── cluster.py
├── models/                       # Step 5: Forecasting models
│   ├── __init__.py
│   ├── forecasters.py
│   └── saved_models/
├── evaluation/                   # Step 6: Model evaluation
│   ├── __init__.py
│   └── metrics.py
└── results/                      # Output results
```

## Pipeline Stages

### 1. Distributed Data Ingestion
- Load all CSV files using Apache Spark
- Repartition by `store_nbr` for efficient processing
- Convert to Parquet format for optimized storage

### 2. Data Cleaning & Integration
- Forward-fill missing oil prices
- Filter irrelevant holidays (keep only national events)
- Left-join all metadata to training data
- Fill missing sales with 0
- Drop dead items (never sold)

### 3. Feature Engineering
- **Lag Features**: 1, 7, 14, 28 days
- **Rolling Statistics**: 7-day and 30-day mean & std
- **Holiday Impact Flags**: Before, during, after holidays
- **Oil Volatility Indicator**: Price change patterns
- **Date Features**: Day of week, month, year, weekend flags

### 4. Clustering
- **Item Clustering**: Based on sales mean, variance, and seasonality
- **Store Clustering**: Based on transaction volume and location

### 5. Forecasting Models
- **SARIMAX**: Seasonal ARIMA with exogenous variables
- **GBT**: Gradient Boosted Trees
- **LSTM**: Deep learning neural network
- **ARIMA**: Traditional time series model

### 6. Evaluation
- **SMAPE**: Symmetric Mean Absolute Percentage Error (for zero-inflated sales)
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error

## Installation

1. **Install Python 3.8+** (if not already installed)

2. **Install Java** (required for PySpark):
   - Download and install JDK 8 or 11
   - Set `JAVA_HOME` environment variable

3. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

## Usage

### Run the Complete Pipeline

```bash
cd backend
python main.py
```

This will execute all pipeline stages sequentially:
1. Data Ingestion
2. Data Cleaning
3. Feature Engineering
4. Clustering
5. Model Training
6. Evaluation

### Run Individual Stages

```python
# Data Ingestion
python data_ingestion/ingest.py

# Data Cleaning
python data_cleaning/clean.py

# Feature Engineering
python feature_engineering/features.py

# Clustering
python clustering/cluster.py
```

## Output

The pipeline generates:

1. **Processed Data**: Parquet files in `data/processed/`
   - `train.parquet`
   - `cleaned_data.parquet`
   - `feature_data.parquet`
   - `clustered_data.parquet`

2. **Model Results**: CSV files in `results/`
   - `model_comparison.csv` - Performance metrics for all models

3. **Console Output**: Detailed logs of each pipeline stage

## Configuration

Edit `config.py` to customize:
- Spark settings (memory, partitions)
- Feature engineering parameters
- Clustering parameters
- Model hyperparameters
- File paths

## Expected Results

The pipeline will output:
- Model comparison showing SMAPE, RMSE, and MAE for each model
- Feature importance analysis
- Cluster distributions
- Processing statistics at each stage

## Troubleshooting

### Memory Issues
- Reduce `SPARK_MEMORY` in config.py
- Process data in smaller batches

### Java Not Found
- Install JDK and set JAVA_HOME environment variable
- Restart your terminal/IDE

### Package Installation Errors
- Upgrade pip: `pip install --upgrade pip`
- Install packages one by one if batch install fails

## Notes

- The pipeline is designed for large datasets and uses distributed processing
- First run will take longer as Spark initializes
- Processed data is cached in Parquet format for faster subsequent runs
- Models are trained on a validation split of the data

## Contributors

Big Data Analytics - Time Series Analysis Project

## License

Educational Project - Amrita Vishwa Vidyapeetham

---

**Note**: Ensure all CSV files are in the parent directory before running the pipeline.
