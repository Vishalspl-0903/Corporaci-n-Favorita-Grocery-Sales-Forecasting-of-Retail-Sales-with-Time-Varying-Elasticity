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
- **Comprehensive Analytics** (Descriptive, Diagnostic, Predictive, Advanced)

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
BDA_TSA/
├── Dataset Files (CSV)           # Root directory
│   ├── train.csv
│   ├── test.csv
│   ├── items.csv
│   ├── stores.csv
│   ├── holidays_events.csv
│   ├── oil.csv
│   ├── transactions.csv
│   └── sample_submission.csv
│
└── backend/                      # Main codebase
    ├── config.py                 # Configuration settings
    ├── requirements.txt          # Python dependencies
    ├── main.py                   # Main pipeline orchestrator
    ├── utils.py                  # Utility functions
    ├── check_environment.py      # Environment checker
    │
    ├── data/                     # Data storage
    │   └── processed/            # Processed parquet files
    │
    ├── data_ingestion/          # Step 1: Load CSVs with Spark
    │   ├── __init__.py
    │   └── ingest.py
    │
    ├── data_cleaning/           # Step 2: Clean & integrate data
    │   ├── __init__.py
    │   └── clean.py
    │
    ├── feature_engineering/     # Step 3: Create features
    │   ├── __init__.py
    │   └── features.py
    │
    ├── clustering/              # Step 4: Item & store clustering
    │   ├── __init__.py
    │   └── cluster.py
    │
    ├── analytics/               # Step 5: Comprehensive analytics
    │   ├── __init__.py
    │   ├── descriptive_analytics.py
    │   ├── diagnostic_analytics.py
    │   └── advanced_analytics.py
    │
    ├── models/                  # Step 6: Forecasting models
    │   ├── __init__.py
    │   ├── forecasters.py
    │   └── saved_models/
    │
    ├── evaluation/              # Step 7: Model evaluation
    │   ├── __init__.py
    │   └── metrics.py
    │
    └── results/                 # Output results
```

## Pipeline Stages

### Stage 1: Distributed Data Ingestion
- Load all CSV files using Apache Spark
- Repartition by `store_nbr` for efficient processing
- Convert to Parquet format for optimized storage

### Stage 2: Data Cleaning & Integration
- Forward-fill missing oil prices
- Filter irrelevant holidays (keep only national events)
- Left-join all metadata to training data
- Fill missing sales with 0
- Drop dead items (never sold)

### Stage 3: Feature Engineering
- **Lag Features**: 1, 7, 14, 28 days
- **Rolling Statistics**: 7-day and 30-day mean & std
- **Holiday Impact Flags**: Before, during, after holidays
- **Oil Volatility Indicator**: Price change patterns
- **Date Features**: Day of week, month, year, weekend flags

### Stage 4: Clustering
- **Item Clustering**: Based on sales mean, variance, and seasonality (K=5)
- **Store Clustering**: Based on transaction volume and location (K=3)

### Stage 5: Comprehensive Analytics

#### 5.1 Descriptive Analytics
- Sales trend analysis (daily, weekly, monthly)
- Store-level demand patterns
- Item-level demand patterns by family
- Seasonal and holiday impact analysis

#### 5.2 Diagnostic Analytics
- Correlation analysis with oil prices
- Correlation with holidays and transactions
- Demand variability analysis
- Statistical significance testing

#### 5.3 Advanced Analytics
- Time-varying oil price elasticity (90-day rolling windows)
- Holiday elasticity analysis (60-day windows)
- Transaction elasticity patterns
- Multivariate elasticity using Ridge regression

### Stage 6: Predictive Modeling (Forecasting)

#### SARIMAX
- Seasonal ARIMA with exogenous variables
- Handles seasonality and external factors
- Parameters: order=(1,1,1), seasonal_order=(1,1,1,7)

#### GBT (Gradient Boosted Trees)
- Ensemble machine learning model
- Captures non-linear relationships
- Parameters: 100 estimators, max_depth=10

#### LSTM (Deep Learning)
- Long Short-Term Memory neural network
- Captures temporal dependencies
- Architecture: LSTM(128) → LSTM(64) → Dense(32) → Output

#### ARIMA
- Traditional time series statistical model
- Simple baseline for comparison
- Parameters: order=(5,1,2)

### Stage 7: Evaluation
- **SMAPE**: Symmetric Mean Absolute Percentage Error (primary metric)
- **RMSE**: Root Mean Squared Error
- **MAE**: Mean Absolute Error
- **Model Comparison**: Side-by-side performance analysis

## Installation

### Prerequisites
1. **Python 3.8+** (Python 3.8, 3.9, 3.10, or 3.11 recommended)

2. **Java JDK 8 or 11** (required for PySpark)
   - Download from [Oracle](https://www.oracle.com/java/technologies/downloads/) or [OpenJDK](https://openjdk.org/)
   - Set `JAVA_HOME` environment variable

### Setup

1. **Clone or download the repository**
   ```bash
   cd BDA_TSA
   ```

2. **Navigate to backend directory**
   ```bash
   cd backend
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify environment** (optional but recommended)
   ```bash
   python check_environment.py
   ```

## Usage

### Quick Start - Run Complete Pipeline

```bash
cd backend
python main.py
```

This executes all 8 pipeline stages:
1. Data Ingestion (Spark)
2. Data Cleaning & Integration
3. Feature Engineering
4. Clustering
5. Analytics (Descriptive, Diagnostic, Advanced)
6. Predictive Modeling (4 models)
7. Model Evaluation & Comparison
8. Results Generation

### Run Individual Modules

```bash
cd backend

# Data Ingestion
python data_ingestion/ingest.py

# Data Cleaning
python data_cleaning/clean.py

# Feature Engineering
python feature_engineering/features.py

# Clustering
python clustering/cluster.py
```

### Windows Batch Script
```bash
cd backend
run_pipeline.bat
```

### Linux/Mac Shell Script
```bash
cd backend
chmod +x run_pipeline.sh
./run_pipeline.sh
```

## Output Files

### Processed Data (Parquet format)
Located in `backend/data/processed/`:
- `train.parquet` - Ingested training data
- `cleaned_data.parquet` - Cleaned and integrated data
- `feature_data.parquet` - Feature-engineered data
- `clustered_data.parquet` - Data with cluster assignments

### Results
Located in `backend/results/`:
- `model_comparison.csv` - Performance metrics for all models
- `analytics_reports/` - Analytics output files

### Console Output
- Detailed logs for each pipeline stage
- Model training progress
- Evaluation metrics
- Processing statistics

## Configuration

Edit `backend/config.py` to customize:

### Spark Settings
```python
SPARK_MEMORY = "4g"
SPARK_PARTITIONS = 8
```

### Feature Engineering
```python
LAG_FEATURES = [1, 7, 14, 28]
ROLLING_WINDOWS = [7, 30]
```

### Clustering
```python
ITEM_CLUSTERS = 5
STORE_CLUSTERS = 3
```

### Model Parameters
```python
GBT_ESTIMATORS = 100
LSTM_UNITS = [128, 64]
FORECAST_HORIZON = 16
```

## Expected Results

After running the pipeline, you'll see:

### Model Comparison Table
```
Model                          SMAPE      RMSE       MAE
----------------------------------------------------
Gradient Boosted Trees         45.23      12.45      8.67
LSTM Neural Network            48.12      13.21      9.12
SARIMAX                        46.89      12.98      8.95
ARIMA                          52.34      15.67     10.45
```

### Analytics Insights
- Sales patterns and trends
- Correlation analysis results
- Elasticity measurements
- Cluster characteristics

### Processing Time
- First run: 10-20 minutes (dataset dependent)
- Subsequent runs: Faster due to cached Parquet files

## Troubleshooting

### Memory Issues
**Problem**: Out of memory errors during Spark operations

**Solution**:
```python
# In config.py, reduce memory allocation
SPARK_MEMORY = "2g"  # Reduce from 4g
```

### Java Not Found
**Problem**: `JAVA_HOME not set` or Java errors

**Solution**:
```bash
# Windows (PowerShell)
$env:JAVA_HOME = "C:\Program Files\Java\jdk-11"

# Windows (CMD)
set JAVA_HOME=C:\Program Files\Java\jdk-11

# Linux/Mac
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

### Package Installation Errors
**Problem**: pip install fails for some packages

**Solution**:
```bash
# Upgrade pip first
pip install --upgrade pip

# Install packages individually
pip install pyspark pandas numpy scikit-learn
pip install tensorflow statsmodels matplotlib seaborn
pip install pyarrow fastparquet
```

### Missing CSV Files
**Problem**: FileNotFoundError for CSV files

**Solution**:
- Ensure all CSV files are in the root directory (BDA_TSA/)
- Check paths in `config.py`
- Files should be at same level as `backend/` folder

### Slow Processing
**Problem**: Pipeline takes too long

**Solutions**:
- Reduce dataset size for testing
- Increase `SPARK_MEMORY` if you have more RAM
- Use SSD for faster I/O
- Skip model training temporarily

## Technical Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| **Language** | Python | 3.8+ |
| **Distributed Computing** | Apache Spark (PySpark) | 3.5.0 |
| **Data Processing** | Pandas, NumPy | 2.1.4, 1.26.2 |
| **Machine Learning** | scikit-learn | 1.3.2 |
| **Deep Learning** | TensorFlow | 2.15.0 |
| **Time Series** | statsmodels | 0.14.1 |
| **Visualization** | Matplotlib, Seaborn, Plotly | Latest |
| **Storage** | Parquet (PyArrow) | 14.0.1 |

## Key Features

- **Distributed Processing**: Handle datasets of any size with Apache Spark
- **Modular Design**: Each pipeline stage is independent and reusable
- **Multiple Models**: Compare 4 different forecasting approaches
- **Comprehensive Analytics**: Understand data patterns before modeling
- **Rich Features**: 30+ engineered features from raw data
- **Professional Metrics**: Industry-standard evaluation (SMAPE for retail)
- **Reproducible**: Consistent results with fixed random seeds
- **Well-Documented**: Extensive inline comments and documentation

## Performance Notes

- **First Run**: 10-20 minutes (includes Spark initialization)
- **Data Ingestion**: 2-3 minutes for large CSV files
- **Feature Engineering**: 3-5 minutes with lag and rolling features
- **Model Training**: 
  - GBT: 1-2 minutes
  - LSTM: 3-5 minutes (GPU recommended)
  - SARIMAX: 2-3 minutes
  - ARIMA: 1 minute
- **Total Pipeline**: 15-30 minutes (dataset and hardware dependent)

## Project Status

- **Version**: 1.0.0
- **Status**: Production Ready
- **Last Updated**: January 2, 2026
- **Maintainer**: BDA TSA Team

## Academic Context

**Institution**: Amrita Vishwa Vidyapeetham  
**Course**: Big Data Analytics (BDA)  
**Semester**: 6  
**Project Type**: Time Series Analysis (TSA)  
**License**: Educational Project

## Contributors

Big Data Analytics - Time Series Analysis Project Team

## Next Steps

After running the pipeline successfully:

1. **Tune Hyperparameters**: Optimize model parameters in `config.py`
2. **Add Features**: Experiment with additional features in `feature_engineering/`
3. **Try Ensemble**: Combine predictions from multiple models
4. **Deploy Model**: Use best model for production forecasting
5. **Visualization**: Create interactive dashboards with results
6. **Documentation**: Add project-specific insights

## Support

For issues or questions:
1. Check `QUICKSTART.md` for common solutions
2. Review `PROJECT_OVERVIEW.md` for detailed methodology
3. Check console logs for error messages
4. Verify environment with `check_environment.py`

## Acknowledgments

- Apache Spark community for distributed computing framework
- scikit-learn team for machine learning tools
- TensorFlow team for deep learning capabilities
- statsmodels contributors for time series models

---

**Note**: Ensure all CSV files (`train.csv`, `test.csv`, `items.csv`, `stores.csv`, `holidays_events.csv`, `oil.csv`, `transactions.csv`) are in the root directory before running the pipeline.

For detailed documentation, see:
- `backend/QUICKSTART.md` - Quick start guide
- `backend/PROJECT_OVERVIEW.md` - Detailed overview
- `backend/PROJECT_STRUCTURE.md` - File structure
- `backend/FILES_CREATED.md` - Complete file listing
