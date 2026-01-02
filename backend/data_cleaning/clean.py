"""
Data Cleaning and Integration Module
- Forward-fill missing oil prices
- Filter irrelevant holidays
- Left-join all metadata to train.csv
- Fill missing sales with 0
- Drop dead items (never sold)
"""
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, when, isnan, isnull, sum as spark_sum, 
    coalesce, lit, count, to_date, lag, lead, avg
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class DataCleaner:
    """Handles data cleaning and integration"""
    
    def __init__(self, spark=None):
        """Initialize with existing Spark session or create new one"""
        if spark:
            self.spark = spark
        else:
            self.spark = SparkSession.builder \
                .appName(SPARK_APP_NAME) \
                .master(SPARK_MASTER) \
                .config("spark.driver.memory", SPARK_MEMORY) \
                .getOrCreate()
            self.spark.sparkContext.setLogLevel("WARN")
    
    def load_parquet_data(self):
        """Load all parquet files"""
        print("Loading parquet data...")
        
        train_df = self.spark.read.parquet(TRAIN_PARQUET)
        items_df = self.spark.read.parquet(os.path.join(PROCESSED_DATA_DIR, 'items.parquet'))
        stores_df = self.spark.read.parquet(os.path.join(PROCESSED_DATA_DIR, 'stores.parquet'))
        holidays_df = self.spark.read.parquet(os.path.join(PROCESSED_DATA_DIR, 'holidays.parquet'))
        oil_df = self.spark.read.parquet(os.path.join(PROCESSED_DATA_DIR, 'oil.parquet'))
        transactions_df = self.spark.read.parquet(os.path.join(PROCESSED_DATA_DIR, 'transactions.parquet'))
        
        return train_df, items_df, stores_df, holidays_df, oil_df, transactions_df
    
    def forward_fill_oil_prices(self, oil_df):
        """Forward-fill missing oil prices"""
        print("\n1. Forward-filling missing oil prices...")
        
        # Convert date column to date type
        oil_df = oil_df.withColumn("date", to_date(col("date")))
        
        # Check for null values
        null_count = oil_df.filter(col("dcoilwtico").isNull()).count()
        print(f"   Missing oil prices before filling: {null_count}")
        
        # Create window spec ordered by date
        window_spec = Window.orderBy("date").rowsBetween(Window.unboundedPreceding, 0)
        
        # Forward fill using last non-null value
        oil_df = oil_df.withColumn(
            "dcoilwtico",
            when(col("dcoilwtico").isNull(), 
                 last(col("dcoilwtico"), ignorenulls=True).over(window_spec))
            .otherwise(col("dcoilwtico"))
        )
        
        # Fill any remaining nulls with mean
        mean_oil = oil_df.select(avg("dcoilwtico")).collect()[0][0]
        oil_df = oil_df.fillna(mean_oil, subset=["dcoilwtico"])
        
        null_count_after = oil_df.filter(col("dcoilwtico").isNull()).count()
        print(f"   Missing oil prices after filling: {null_count_after}")
        
        return oil_df
    
    def filter_irrelevant_holidays(self, holidays_df):
        """Filter irrelevant holidays - keep only national holidays and important events"""
        print("\n2. Filtering irrelevant holidays...")
        
        print(f"   Total holidays before filtering: {holidays_df.count()}")
        
        # Keep national holidays and transferred holidays
        filtered_holidays = holidays_df.filter(
            (col("locale") == "National") | 
            (col("transferred") == True)
        )
        
        print(f"   Total holidays after filtering: {filtered_holidays.count()}")
        
        # Convert date to date type
        filtered_holidays = filtered_holidays.withColumn("date", to_date(col("date")))
        
        return filtered_holidays
    
    def join_metadata_to_train(self, train_df, items_df, stores_df, holidays_df, oil_df, transactions_df):
        """Left-join all metadata to train data"""
        print("\n3. Joining metadata to train data...")
        
        # Convert date columns
        train_df = train_df.withColumn("date", to_date(col("date")))
        transactions_df = transactions_df.withColumn("date", to_date(col("date")))
        
        print(f"   Train data rows: {train_df.count()}")
        
        # Join items metadata
        train_df = train_df.join(items_df, on="item_nbr", how="left")
        print(f"   After joining items: {train_df.count()}")
        
        # Join stores metadata
        train_df = train_df.join(stores_df, on="store_nbr", how="left")
        print(f"   After joining stores: {train_df.count()}")
        
        # Join oil prices
        train_df = train_df.join(oil_df, on="date", how="left")
        print(f"   After joining oil: {train_df.count()}")
        
        # Join transactions
        train_df = train_df.join(
            transactions_df.select("date", "store_nbr", "transactions"),
            on=["date", "store_nbr"],
            how="left"
        )
        print(f"   After joining transactions: {train_df.count()}")
        
        # Join holidays (create binary flag)
        holidays_df = holidays_df.select("date", "type").distinct()
        holidays_df = holidays_df.withColumn("is_holiday", lit(1))
        
        train_df = train_df.join(
            holidays_df.select("date", "is_holiday"),
            on="date",
            how="left"
        )
        train_df = train_df.fillna(0, subset=["is_holiday"])
        print(f"   After joining holidays: {train_df.count()}")
        
        return train_df
    
    def fill_missing_sales(self, df):
        """Fill missing sales with 0"""
        print("\n4. Filling missing sales with 0...")
        
        null_sales = df.filter(col("sales").isNull()).count()
        print(f"   Missing sales values: {null_sales}")
        
        df = df.fillna(0, subset=["sales"])
        
        print(f"   Missing sales after filling: {df.filter(col('sales').isNull()).count()}")
        
        return df
    
    def drop_dead_items(self, df):
        """Drop items that were never sold"""
        print("\n5. Dropping dead items (never sold)...")
        
        # Calculate total sales per item
        item_sales = df.groupBy("item_nbr").agg(
            spark_sum("sales").alias("total_sales")
        )
        
        # Find items with zero sales
        dead_items = item_sales.filter(col("total_sales") == 0)
        dead_item_count = dead_items.count()
        print(f"   Dead items found: {dead_item_count}")
        
        if dead_item_count > 0:
            # Get list of dead item numbers
            dead_item_list = [row.item_nbr for row in dead_items.collect()]
            
            # Remove dead items from dataframe
            df = df.filter(~col("item_nbr").isin(dead_item_list))
            print(f"   Rows after removing dead items: {df.count()}")
        
        return df
    
    def clean_and_integrate(self):
        """Execute complete data cleaning and integration pipeline"""
        print("="*80)
        print("DATA CLEANING & INTEGRATION - STEP 2")
        print("="*80)
        
        # Load data
        train_df, items_df, stores_df, holidays_df, oil_df, transactions_df = self.load_parquet_data()
        
        # Step 1: Forward-fill oil prices
        oil_df = self.forward_fill_oil_prices(oil_df)
        
        # Step 2: Filter holidays
        holidays_df = self.filter_irrelevant_holidays(holidays_df)
        
        # Step 3: Join all metadata
        train_df = self.join_metadata_to_train(
            train_df, items_df, stores_df, holidays_df, oil_df, transactions_df
        )
        
        # Step 4: Fill missing sales
        train_df = self.fill_missing_sales(train_df)
        
        # Step 5: Drop dead items
        train_df = self.drop_dead_items(train_df)
        
        # Save cleaned data
        print(f"\n6. Saving cleaned data to {CLEANED_DATA_PARQUET}...")
        train_df.write.mode('overwrite').parquet(CLEANED_DATA_PARQUET)
        
        print("\n" + "="*80)
        print("DATA CLEANING COMPLETE")
        print("="*80)
        print(f"Final row count: {train_df.count()}")
        print(f"Final column count: {len(train_df.columns)}")
        print("\nColumns:", train_df.columns)
        
        return train_df


# Import last function
from pyspark.sql.functions import last

if __name__ == "__main__":
    cleaner = DataCleaner()
    try:
        cleaned_df = cleaner.clean_and_integrate()
        print("\nData cleaning completed successfully!")
    except Exception as e:
        print(f"Error during data cleaning: {e}")
        import traceback
        traceback.print_exc()
