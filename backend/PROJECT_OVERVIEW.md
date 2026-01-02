# Project Overview - Store Sales Time Series Forecasting

## Executive Summary

This project implements a comprehensive **Big Data Analytics pipeline** for time series forecasting of retail store sales. The pipeline processes large-scale sales data using distributed computing (Apache Spark) and applies multiple machine learning and statistical models to predict future sales.

## 🎯 Objectives

1. **Process large-scale retail data** efficiently using distributed computing
2. **Engineer meaningful features** from time series and metadata
3. **Segment items and stores** through clustering analysis
4. **Build and compare multiple forecasting models** (SARIMAX, GBT, LSTM, ARIMA)
5. **Evaluate models** using industry-standard metrics (SMAPE, RMSE, MAE)

## Dataset Description

### Input Files
| File | Description | Key Columns |
|------|-------------|-------------|
| `train.csv` | Historical sales data | date, store_nbr, item_nbr, sales, onpromotion |
| `test.csv` | Future dates for forecasting | date, store_nbr, item_nbr, onpromotion |
| `items.csv` | Item metadata | item_nbr, family, class, perishable |
| `stores.csv` | Store metadata | store_nbr, city, state, type, cluster |
| `holidays_events.csv` | Holiday calendar | date, type, locale, transferred |
| `oil.csv` | Oil price (economic indicator) | date, dcoilwtico |
| `transactions.csv` | Store transactions | date, store_nbr, transactions |

## Architecture

```
┌─────────────────┐
│   CSV Files     │
│  (Raw Data)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Data Ingestion  │  ← Apache Spark
│ (Distributed)   │  ← Repartition by store_nbr
└────────┬────────┘  ← Convert to Parquet
         │
         ▼
┌─────────────────┐
│ Data Cleaning   │  ← Forward-fill oil prices
│ & Integration   │  ← Filter holidays
└────────┬────────┘  ← Join metadata
         │            ← Fill missing values
         ▼            ← Drop dead items
┌─────────────────┐
│    Feature      │  ← Lag features (1,7,14,28)
│  Engineering    │  ← Rolling stats (7,30)
└────────┬────────┘  ← Holiday flags
         │            ← Oil volatility
         ▼
┌─────────────────┐
│   Clustering    │  ← Item clusters (K=5)
│                 │  ← Store clusters (K=3)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Forecasting   │  ← SARIMAX
│     Models      │  ← Gradient Boosted Trees
└────────┬────────┘  ← LSTM Neural Network
         │            ← ARIMA
         ▼
┌─────────────────┐
│   Evaluation    │  ← SMAPE (zero-inflated)
│  & Comparison   │  ← RMSE
└─────────────────┘  ← MAE
```

## Methodology

### 1. Data Preprocessing
- **Distributed Loading**: Spark for parallel CSV processing
- **Partitioning**: By store_nbr for efficient computations
- **Format Conversion**: CSV → Parquet (columnar, compressed)

### 2. Data Cleaning
- **Missing Data Handling**: Forward-fill for oil prices
- **Holiday Filtering**: Keep only national/significant events
- **Integration**: Left-join all metadata to training data
- **Sales Imputation**: Fill missing sales with 0
- **Dead Item Removal**: Drop items never sold

### 3. Feature Engineering
- **Temporal Features**:
  - Lag features: t-1, t-7, t-14, t-28 days
  - Rolling statistics: 7-day and 30-day mean/std
  - Date components: day, week, month, year
  
- **External Features**:
  - Holiday impact flags (before, during, after)
  - Oil price volatility indicator
  - Weekend/month-start/month-end flags

### 4. Clustering Analysis
- **Item Clustering** (K=5):
  - Features: sales mean, variance, coefficient of variation
  - Purpose: Group similar items for targeted modeling
  
- **Store Clustering** (K=3):
  - Features: transaction volume, location, sales patterns
  - Purpose: Segment stores by characteristics

### 5. Forecasting Models

#### A. Gradient Boosted Trees (GBT)
- **Type**: Ensemble machine learning
- **Strengths**: Handles non-linear relationships, feature interactions
- **Hyperparameters**: 100 estimators, depth=10, lr=0.1

#### B. LSTM Neural Network
- **Type**: Deep learning, sequential model
- **Strengths**: Captures long-term dependencies, complex patterns
- **Architecture**: 2 LSTM layers (128, 64 units) + Dense layers

#### C. SARIMAX
- **Type**: Statistical time series
- **Strengths**: Handles seasonality, exogenous variables
- **Parameters**: (p,d,q) = (1,1,1), seasonal (P,D,Q,s) = (1,1,1,7)

#### D. ARIMA
- **Type**: Statistical time series
- **Strengths**: Simple, interpretable, baseline model
- **Parameters**: (p,d,q) = (5,1,2)

### 6. Evaluation Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| **SMAPE** | $\frac{2}{n}\sum\frac{|y-\hat{y}|}{|y|+|\hat{y}|} \times 100$ | Symmetric, handles zero sales |
| **RMSE** | $\sqrt{\frac{1}{n}\sum(y-\hat{y})^2}$ | Penalizes large errors |
| **MAE** | $\frac{1}{n}\sum|y-\hat{y}|$ | Average absolute error |

## Expected Outcomes

1. **Processed Dataset**: Clean, feature-rich data ready for modeling
2. **Cluster Insights**: Item and store segmentation for business strategy
3. **Model Comparison**: Performance metrics for each forecasting method
4. **Best Model**: Identified based on SMAPE (primary metric)
5. **Feature Importance**: Understanding of key predictive factors

## Technical Stack

| Component | Technology |
|-----------|-----------|
| **Distributed Computing** | Apache Spark (PySpark) |
| **Data Format** | Parquet (columnar storage) |
| **ML Framework** | scikit-learn, TensorFlow |
| **Time Series** | statsmodels (SARIMAX, ARIMA) |
| **Visualization** | matplotlib, seaborn |
| **Language** | Python 3.8+ |

## Running the Pipeline

### Quick Start
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Step-by-Step
```bash
# 1. Check environment
python check_environment.py

# 2. Run individual stages (optional)
python data_ingestion/ingest.py
python data_cleaning/clean.py
python feature_engineering/features.py
python clustering/cluster.py

# 3. Or run complete pipeline
python main.py
```

### Using Batch Script (Windows)
```bash
run_pipeline.bat
```

## Output Files

```
backend/
├── data/processed/
│   ├── train.parquet              # Ingested training data
│   ├── cleaned_data.parquet       # Cleaned & integrated data
│   ├── feature_data.parquet       # Feature-engineered data
│   └── clustered_data.parquet     # Final data with clusters
│
└── results/
    ├── model_comparison.csv       # Model performance metrics
    └── model_comparison.png        # Visualization (if generated)
```

## Learning Outcomes

1. **Big Data Processing**: Working with large-scale data using Spark
2. **Feature Engineering**: Creating predictive features from time series
3. **Clustering**: Unsupervised learning for segmentation
4. **Time Series Forecasting**: Multiple modeling approaches
5. **Model Evaluation**: Comparing models with appropriate metrics
6. **Pipeline Design**: Building end-to-end ML pipelines

## Business Impact

- **Inventory Optimization**: Better stock management based on forecasts
- **Demand Planning**: Improved supply chain efficiency
- **Promotional Strategy**: Data-driven promotion timing
- **Store Segmentation**: Targeted strategies for store clusters
- **Item Management**: Focused approach for item categories

## Future Enhancements

1. **Ensemble Methods**: Combine predictions from multiple models
2. **Prophet Model**: Add Facebook Prophet for trend detection
3. **Hierarchical Forecasting**: Forecast at different aggregation levels
4. **Real-time Pipeline**: Stream processing for live predictions
5. **AutoML**: Automated hyperparameter tuning
6. **Explainability**: SHAP values for model interpretation

## References

- Time Series Analysis: Box, Jenkins (1970)
- Gradient Boosting: Friedman (2001)
- LSTM Networks: Hochreiter & Schmidhuber (1997)
- SMAPE Metric: Makridakis (1993)

---

**Project Team**: BDA TSA - Amrita Vishwa Vidyapeetham
**Date**: January 2026
**Version**: 1.0.0
