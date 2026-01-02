"""
Clustering Module
- Item clustering based on sales mean, variance, seasonality
- Store clustering based on transaction volume & location
"""
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, stddev, sum as spark_sum, 
    count, max as spark_max, min as spark_min
)
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class Clusterer:
    """Handles item and store clustering"""
    
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
    
    def load_feature_data(self):
        """Load feature-engineered data"""
        print("Loading feature-engineered data...")
        df = self.spark.read.parquet(FEATURE_DATA_PARQUET)
        print(f"Loaded {df.count()} rows")
        return df
    
    def create_item_clusters(self, df):
        """
        Cluster items based on:
        - Sales mean
        - Sales variance
        - Seasonality patterns
        """
        print("\n1. Creating item clusters...")
        
        # Calculate item-level statistics
        item_stats = df.groupBy("item_nbr").agg(
            avg("sales").alias("sales_mean"),
            stddev("sales").alias("sales_std"),
            spark_sum("sales").alias("total_sales"),
            count("sales").alias("sales_count"),
            spark_max("sales").alias("max_sales"),
            spark_min("sales").alias("min_sales")
        )
        
        # Calculate coefficient of variation as seasonality indicator
        item_stats = item_stats.withColumn(
            "sales_cv",
            col("sales_std") / (col("sales_mean") + 1)  # Add 1 to avoid division by zero
        )
        
        # Convert to pandas for sklearn
        item_stats_pd = item_stats.toPandas()
        print(f"   Items to cluster: {len(item_stats_pd)}")
        
        # Prepare features for clustering
        features = item_stats_pd[['sales_mean', 'sales_std', 'sales_cv']].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform KMeans clustering
        kmeans_items = KMeans(n_clusters=ITEM_CLUSTER_N, random_state=42, n_init=10)
        item_stats_pd['item_cluster'] = kmeans_items.fit_predict(features_scaled)
        
        print(f"   Item cluster distribution:")
        print(item_stats_pd['item_cluster'].value_counts().sort_index())
        
        # Convert back to Spark DataFrame
        item_clusters_spark = self.spark.createDataFrame(
            item_stats_pd[['item_nbr', 'item_cluster']]
        )
        
        return item_clusters_spark
    
    def create_store_clusters(self, df):
        """
        Cluster stores based on:
        - Transaction volume
        - Location (city, state)
        """
        print("\n2. Creating store clusters...")
        
        # Calculate store-level statistics
        store_stats = df.groupBy("store_nbr", "city", "state", "type", "cluster").agg(
            avg("transactions").alias("avg_transactions"),
            spark_sum("sales").alias("total_sales"),
            avg("sales").alias("avg_sales"),
            count("*").alias("record_count")
        )
        
        # Convert to pandas
        store_stats_pd = store_stats.toPandas()
        print(f"   Stores to cluster: {len(store_stats_pd)}")
        
        # One-hot encode categorical features (city, state, type)
        store_features = pd.get_dummies(
            store_stats_pd,
            columns=['city', 'state', 'type'],
            drop_first=True
        )
        
        # Select numerical features for clustering
        feature_cols = ['avg_transactions', 'total_sales', 'avg_sales', 'cluster']
        feature_cols.extend([col for col in store_features.columns if col.startswith(('city_', 'state_', 'type_'))])
        
        features = store_features[feature_cols].fillna(0)
        
        # Standardize features
        scaler = StandardScaler()
        features_scaled = scaler.fit_transform(features)
        
        # Perform KMeans clustering
        kmeans_stores = KMeans(n_clusters=STORE_CLUSTER_N, random_state=42, n_init=10)
        store_stats_pd['store_cluster'] = kmeans_stores.fit_predict(features_scaled)
        
        print(f"   Store cluster distribution:")
        print(store_stats_pd['store_cluster'].value_counts().sort_index())
        
        # Convert back to Spark DataFrame
        store_clusters_spark = self.spark.createDataFrame(
            store_stats_pd[['store_nbr', 'store_cluster']]
        )
        
        return store_clusters_spark
    
    def apply_clusters(self, df, item_clusters, store_clusters):
        """Join cluster assignments back to main dataframe"""
        print("\n3. Applying cluster assignments to data...")
        
        # Join item clusters
        df = df.join(item_clusters, on="item_nbr", how="left")
        print(f"   After joining item clusters: {df.count()}")
        
        # Join store clusters
        df = df.join(store_clusters, on="store_nbr", how="left")
        print(f"   After joining store clusters: {df.count()}")
        
        # Fill any null clusters with 0
        df = df.fillna(0, subset=["item_cluster", "store_cluster"])
        
        return df
    
    def perform_clustering(self):
        """Execute complete clustering pipeline"""
        print("="*80)
        print("CLUSTERING - STEP 4")
        print("="*80)
        
        # Load feature data
        df = self.load_feature_data()
        
        # Create item clusters
        item_clusters = self.create_item_clusters(df)
        
        # Create store clusters
        store_clusters = self.create_store_clusters(df)
        
        # Apply clusters to data
        df = self.apply_clusters(df, item_clusters, store_clusters)
        
        # Save clustered data
        print(f"\n4. Saving clustered data to {CLUSTERED_DATA_PARQUET}...")
        df.write.mode('overwrite').parquet(CLUSTERED_DATA_PARQUET)
        
        print("\n" + "="*80)
        print("CLUSTERING COMPLETE")
        print("="*80)
        print(f"Final row count: {df.count()}")
        print(f"Total columns: {len(df.columns)}")
        
        return df


if __name__ == "__main__":
    clusterer = Clusterer()
    try:
        clustered_df = clusterer.perform_clustering()
        print("\nClustering completed successfully!")
    except Exception as e:
        print(f"Error during clustering: {e}")
        import traceback
        traceback.print_exc()
