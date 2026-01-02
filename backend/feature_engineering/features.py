"""
Feature Engineering Module
- Lag features: 1, 7, 14, 28
- Rolling mean & std: 7, 30
- Holiday impact flags
- Oil volatility indicator
"""
from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import (
    col, lag, avg, stddev, when, abs as spark_abs,
    row_number, lit, datediff, max as spark_max
)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class FeatureEngineer:
    """Handles feature engineering for time series forecasting"""
    
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
    
    def load_cleaned_data(self):
        """Load cleaned data from parquet"""
        print("Loading cleaned data...")
        df = self.spark.read.parquet(CLEANED_DATA_PARQUET)
        print(f"Loaded {df.count()} rows")
        return df
    
    def create_lag_features(self, df):
        """Create lag features for sales"""
        print("\n1. Creating lag features...")
        
        # Define window partitioned by store and item, ordered by date
        window_spec = Window.partitionBy("store_nbr", "item_nbr").orderBy("date")
        
        # Create lag features
        for lag_period in LAG_FEATURES:
            print(f"   Creating lag_{lag_period}...")
            df = df.withColumn(
                f"sales_lag_{lag_period}",
                lag("sales", lag_period).over(window_spec)
            )
        
        # Fill nulls with 0 for lag features
        lag_cols = [f"sales_lag_{lag}" for lag in LAG_FEATURES]
        df = df.fillna(0, subset=lag_cols)
        
        return df
    
    def create_rolling_features(self, df):
        """Create rolling mean and standard deviation features"""
        print("\n2. Creating rolling window features...")
        
        # Define window for rolling calculations
        for window_size in ROLLING_WINDOWS:
            print(f"   Creating rolling features for window {window_size}...")
            
            window_spec = Window.partitionBy("store_nbr", "item_nbr") \
                .orderBy("date") \
                .rowsBetween(-window_size, -1)
            
            # Rolling mean
            df = df.withColumn(
                f"sales_rolling_mean_{window_size}",
                avg("sales").over(window_spec)
            )
            
            # Rolling standard deviation
            df = df.withColumn(
                f"sales_rolling_std_{window_size}",
                stddev("sales").over(window_spec)
            )
        
        # Fill nulls with 0 for rolling features
        rolling_cols = []
        for window_size in ROLLING_WINDOWS:
            rolling_cols.extend([
                f"sales_rolling_mean_{window_size}",
                f"sales_rolling_std_{window_size}"
            ])
        df = df.fillna(0, subset=rolling_cols)
        
        return df
    
    def create_holiday_features(self, df):
        """Create holiday impact flags"""
        print("\n3. Creating holiday impact features...")
        
        # is_holiday already exists from data cleaning
        # Add day before and day after holiday flags
        
        window_spec = Window.partitionBy("store_nbr").orderBy("date")
        
        # Day before holiday
        df = df.withColumn(
            "is_day_before_holiday",
            lag("is_holiday", -1).over(window_spec)
        )
        
        # Day after holiday
        df = df.withColumn(
            "is_day_after_holiday",
            lag("is_holiday", 1).over(window_spec)
        )
        
        # Fill nulls
        df = df.fillna(0, subset=["is_day_before_holiday", "is_day_after_holiday"])
        
        # Holiday week flag (within 3 days of holiday)
        df = df.withColumn(
            "is_holiday_week",
            when(
                (col("is_holiday") == 1) | 
                (col("is_day_before_holiday") == 1) | 
                (col("is_day_after_holiday") == 1),
                1
            ).otherwise(0)
        )
        
        print(f"   Holiday features created")
        
        return df
    
    def create_oil_volatility(self, df):
        """Create oil price volatility indicator"""
        print("\n4. Creating oil volatility indicator...")
        
        # Calculate day-to-day oil price change
        window_spec = Window.orderBy("date")
        
        df = df.withColumn(
            "oil_price_prev",
            lag("dcoilwtico", 1).over(window_spec)
        )
        
        # Calculate absolute change
        df = df.withColumn(
            "oil_price_change",
            when(
                col("oil_price_prev").isNotNull(),
                col("dcoilwtico") - col("oil_price_prev")
            ).otherwise(0)
        )
        
        # Calculate volatility (7-day rolling std of price changes)
        window_7day = Window.orderBy("date").rowsBetween(-7, -1)
        
        df = df.withColumn(
            "oil_volatility",
            stddev("oil_price_change").over(window_7day)
        )
        
        # Fill nulls
        df = df.fillna(0, subset=["oil_volatility", "oil_price_change"])
        
        # Drop temporary column
        df = df.drop("oil_price_prev")
        
        print(f"   Oil volatility features created")
        
        return df
    
    def create_date_features(self, df):
        """Create date-based features"""
        print("\n5. Creating date features...")
        
        from pyspark.sql.functions import dayofweek, dayofmonth, month, year, weekofyear
        
        # Day of week (1 = Sunday, 7 = Saturday)
        df = df.withColumn("day_of_week", dayofweek("date"))
        
        # Day of month
        df = df.withColumn("day_of_month", dayofmonth("date"))
        
        # Month
        df = df.withColumn("month", month("date"))
        
        # Year
        df = df.withColumn("year", year("date"))
        
        # Week of year
        df = df.withColumn("week_of_year", weekofyear("date"))
        
        # Weekend flag
        df = df.withColumn(
            "is_weekend",
            when((col("day_of_week") == 1) | (col("day_of_week") == 7), 1).otherwise(0)
        )
        
        # Month start/end flags
        df = df.withColumn(
            "is_month_start",
            when(col("day_of_month") <= 7, 1).otherwise(0)
        )
        
        df = df.withColumn(
            "is_month_end",
            when(col("day_of_month") >= 24, 1).otherwise(0)
        )
        
        print(f"   Date features created")
        
        return df
    
    def engineer_features(self):
        """Execute complete feature engineering pipeline"""
        print("="*80)
        print("FEATURE ENGINEERING - STEP 3")
        print("="*80)
        
        # Load cleaned data
        df = self.load_cleaned_data()
        
        # Create lag features
        df = self.create_lag_features(df)
        
        # Create rolling features
        df = self.create_rolling_features(df)
        
        # Create holiday features
        df = self.create_holiday_features(df)
        
        # Create oil volatility
        df = self.create_oil_volatility(df)
        
        # Create date features
        df = self.create_date_features(df)
        
        # Save feature-engineered data
        print(f"\n6. Saving feature data to {FEATURE_DATA_PARQUET}...")
        df.write.mode('overwrite').parquet(FEATURE_DATA_PARQUET)
        
        print("\n" + "="*80)
        print("FEATURE ENGINEERING COMPLETE")
        print("="*80)
        print(f"Final row count: {df.count()}")
        print(f"Final column count: {len(df.columns)}")
        print("\nFeature columns:", df.columns)
        
        return df


if __name__ == "__main__":
    engineer = FeatureEngineer()
    try:
        feature_df = engineer.engineer_features()
        print("\nFeature engineering completed successfully!")
    except Exception as e:
        print(f"Error during feature engineering: {e}")
        import traceback
        traceback.print_exc()
