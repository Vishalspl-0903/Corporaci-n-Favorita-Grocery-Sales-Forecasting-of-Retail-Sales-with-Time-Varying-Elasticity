"""
Configuration file for the Time Series Forecasting Pipeline
"""
import os

# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(ROOT_DIR)
PROCESSED_DATA_DIR = os.path.join(BASE_DIR, 'data', 'processed')

# Input data files
TRAIN_CSV = os.path.join(DATA_DIR, 'train.csv')
TEST_CSV = os.path.join(DATA_DIR, 'test.csv')
ITEMS_CSV = os.path.join(DATA_DIR, 'items.csv')
STORES_CSV = os.path.join(DATA_DIR, 'stores.csv')
HOLIDAYS_CSV = os.path.join(DATA_DIR, 'holidays_events.csv')
OIL_CSV = os.path.join(DATA_DIR, 'oil.csv')
TRANSACTIONS_CSV = os.path.join(DATA_DIR, 'transactions.csv')
SAMPLE_SUBMISSION_CSV = os.path.join(DATA_DIR, 'sample_submission.csv')

# Processed data files (Parquet)
TRAIN_PARQUET = os.path.join(PROCESSED_DATA_DIR, 'train.parquet')
TEST_PARQUET = os.path.join(PROCESSED_DATA_DIR, 'test.parquet')
CLEANED_DATA_PARQUET = os.path.join(PROCESSED_DATA_DIR, 'cleaned_data.parquet')
FEATURE_DATA_PARQUET = os.path.join(PROCESSED_DATA_DIR, 'feature_data.parquet')
CLUSTERED_DATA_PARQUET = os.path.join(PROCESSED_DATA_DIR, 'clustered_data.parquet')

# Spark configuration
SPARK_APP_NAME = "Store_Sales_Forecasting"
SPARK_MASTER = "local[*]"
SPARK_MEMORY = "4g"
REPARTITION_BY = "store_nbr"

# Feature engineering parameters
LAG_FEATURES = [1, 7, 14, 28]
ROLLING_WINDOWS = [7, 30]

# Clustering parameters
ITEM_CLUSTER_N = 5  # Number of item clusters
STORE_CLUSTER_N = 3  # Number of store clusters

# Model parameters
FORECAST_HORIZON = 16  # Days to forecast
VALIDATION_SPLIT = 0.2

# LSTM parameters
LSTM_UNITS = 128
LSTM_EPOCHS = 50
LSTM_BATCH_SIZE = 32
LSTM_LOOKBACK = 30

# GBT parameters
GBT_N_ESTIMATORS = 100
GBT_MAX_DEPTH = 10
GBT_LEARNING_RATE = 0.1

# Evaluation metrics
METRICS = ['SMAPE', 'RMSE', 'MAE']

# Model output paths
MODEL_DIR = os.path.join(BASE_DIR, 'models', 'saved_models')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')

# Create directories if they don't exist
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
