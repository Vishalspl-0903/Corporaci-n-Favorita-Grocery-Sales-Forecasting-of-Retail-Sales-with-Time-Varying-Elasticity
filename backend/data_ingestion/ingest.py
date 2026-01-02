"""
Distributed Data Ingestion Module
Loads all CSVs using Spark, repartitions by store_nbr, and converts to Parquet
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class DataIngestion:
    """Handles distributed data ingestion using Spark"""
    
    def __init__(self):
        """Initialize Spark session"""
        self.spark = SparkSession.builder \
            .appName(SPARK_APP_NAME) \
            .master(SPARK_MASTER) \
            .config("spark.driver.memory", SPARK_MEMORY) \
            .config("spark.sql.shuffle.partitions", "200") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        print(f"Spark session initialized: {SPARK_APP_NAME}")
    
    def load_csv_to_parquet(self, csv_path, parquet_path, repartition_col=None):
        """
        Load CSV file and save as Parquet with optional repartitioning
        
        Args:
            csv_path: Path to input CSV file
            parquet_path: Path to output Parquet file
            repartition_col: Column to repartition by (default: None)
        """
        print(f"Loading {csv_path}...")
        df = self.spark.read.csv(csv_path, header=True, inferSchema=True)
        
        # Display schema and row count
        print(f"Schema for {os.path.basename(csv_path)}:")
        df.printSchema()
        print(f"Row count: {df.count()}")
        
        # Repartition if specified
        if repartition_col and repartition_col in df.columns:
            print(f"Repartitioning by {repartition_col}...")
            df = df.repartition(col(repartition_col))
        
        # Save as Parquet
        print(f"Saving to {parquet_path}...")
        df.write.mode('overwrite').parquet(parquet_path)
        print(f"Successfully saved {os.path.basename(parquet_path)}\n")
        
        return df
    
    def ingest_all_data(self):
        """Load all CSV files and convert to Parquet format"""
        print("="*80)
        print("DISTRIBUTED DATA INGESTION - STEP 1")
        print("="*80)
        
        # Load train data (repartition by store_nbr for efficient processing)
        train_df = self.load_csv_to_parquet(
            TRAIN_CSV, 
            TRAIN_PARQUET, 
            repartition_col=REPARTITION_BY
        )
        
        # Load test data (repartition by store_nbr)
        test_df = self.load_csv_to_parquet(
            TEST_CSV, 
            TEST_PARQUET, 
            repartition_col=REPARTITION_BY
        )
        
        # Load metadata files (no repartitioning needed)
        items_path = os.path.join(PROCESSED_DATA_DIR, 'items.parquet')
        items_df = self.load_csv_to_parquet(ITEMS_CSV, items_path)
        
        stores_path = os.path.join(PROCESSED_DATA_DIR, 'stores.parquet')
        stores_df = self.load_csv_to_parquet(STORES_CSV, stores_path)
        
        holidays_path = os.path.join(PROCESSED_DATA_DIR, 'holidays.parquet')
        holidays_df = self.load_csv_to_parquet(HOLIDAYS_CSV, holidays_path)
        
        oil_path = os.path.join(PROCESSED_DATA_DIR, 'oil.parquet')
        oil_df = self.load_csv_to_parquet(OIL_CSV, oil_path)
        
        transactions_path = os.path.join(PROCESSED_DATA_DIR, 'transactions.parquet')
        transactions_df = self.load_csv_to_parquet(TRANSACTIONS_CSV, transactions_path)
        
        print("="*80)
        print("DATA INGESTION COMPLETE")
        print("="*80)
        
        return {
            'train': train_df,
            'test': test_df,
            'items': items_df,
            'stores': stores_df,
            'holidays': holidays_df,
            'oil': oil_df,
            'transactions': transactions_df
        }
    
    def close(self):
        """Stop Spark session"""
        self.spark.stop()
        print("Spark session closed")


if __name__ == "__main__":
    # Run data ingestion
    ingestion = DataIngestion()
    try:
        data = ingestion.ingest_all_data()
        print("\nData ingestion completed successfully!")
    except Exception as e:
        print(f"Error during data ingestion: {e}")
    finally:
        ingestion.close()
