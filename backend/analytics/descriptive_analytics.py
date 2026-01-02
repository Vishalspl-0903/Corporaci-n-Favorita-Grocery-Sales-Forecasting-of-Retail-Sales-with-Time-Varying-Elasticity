"""
Descriptive Analytics Module
- Sales trend analysis
- Store and item-level demand patterns
- Seasonal and holiday impact analysis
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as spark_sum, avg, count, month, year, dayofweek
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class DescriptiveAnalytics:
    """Performs descriptive analytics on sales data"""
    
    def __init__(self, spark=None):
        """Initialize with Spark session"""
        if spark:
            self.spark = spark
        else:
            self.spark = SparkSession.builder \
                .appName(SPARK_APP_NAME) \
                .master(SPARK_MASTER) \
                .config("spark.driver.memory", SPARK_MEMORY) \
                .getOrCreate()
            self.spark.sparkContext.setLogLevel("WARN")
    
    def load_data(self):
        """Load cleaned or feature data"""
        try:
            df = self.spark.read.parquet(FEATURE_DATA_PARQUET)
            print(f"Loaded feature data: {df.count()} rows")
        except:
            df = self.spark.read.parquet(CLEANED_DATA_PARQUET)
            print(f"Loaded cleaned data: {df.count()} rows")
        return df
    
    def sales_trend_analysis(self, df):
        """
        Analyze overall sales trends over time
        Returns: DataFrame with daily, weekly, monthly trends
        """
        print("\n" + "="*70)
        print("1. SALES TREND ANALYSIS")
        print("="*70)
        
        # Convert to pandas for easier analysis
        df_pd = df.select("date", "sales").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        
        # Daily trends
        daily_sales = df_pd.groupby('date')['sales'].agg(['sum', 'mean', 'std', 'count']).reset_index()
        daily_sales.columns = ['date', 'total_sales', 'avg_sales', 'std_sales', 'num_transactions']
        
        print(f"\n📊 Daily Sales Summary:")
        print(f"   Average daily total sales: ${daily_sales['total_sales'].mean():,.2f}")
        print(f"   Median daily total sales: ${daily_sales['total_sales'].median():,.2f}")
        print(f"   Std deviation: ${daily_sales['total_sales'].std():,.2f}")
        print(f"   Date range: {daily_sales['date'].min()} to {daily_sales['date'].max()}")
        
        # Weekly trends
        df_pd['week'] = df_pd['date'].dt.isocalendar().week
        df_pd['year'] = df_pd['date'].dt.year
        weekly_sales = df_pd.groupby(['year', 'week'])['sales'].sum().reset_index()
        
        print(f"\n📈 Weekly Trends:")
        print(f"   Average weekly sales: ${weekly_sales['sales'].mean():,.2f}")
        print(f"   Peak week sales: ${weekly_sales['sales'].max():,.2f}")
        print(f"   Lowest week sales: ${weekly_sales['sales'].min():,.2f}")
        
        # Monthly trends
        df_pd['month'] = df_pd['date'].dt.month
        monthly_sales = df_pd.groupby(['year', 'month'])['sales'].sum().reset_index()
        
        print(f"\n📅 Monthly Trends:")
        print(f"   Average monthly sales: ${monthly_sales['sales'].mean():,.2f}")
        print(f"   Peak month sales: ${monthly_sales['sales'].max():,.2f}")
        print(f"   Lowest month sales: ${monthly_sales['sales'].min():,.2f}")
        
        # Growth analysis
        daily_sales['growth_rate'] = daily_sales['total_sales'].pct_change() * 100
        avg_growth = daily_sales['growth_rate'].mean()
        print(f"\n📊 Growth Rate:")
        print(f"   Average daily growth: {avg_growth:.2f}%")
        
        return {
            'daily': daily_sales,
            'weekly': weekly_sales,
            'monthly': monthly_sales
        }
    
    def store_level_demand_patterns(self, df):
        """
        Analyze demand patterns at store level
        Returns: DataFrame with store-level statistics
        """
        print("\n" + "="*70)
        print("2. STORE-LEVEL DEMAND PATTERNS")
        print("="*70)
        
        # Store-level aggregation
        store_stats = df.groupBy("store_nbr", "city", "state", "type").agg(
            spark_sum("sales").alias("total_sales"),
            avg("sales").alias("avg_sales"),
            count("sales").alias("num_records")
        ).toPandas()
        
        store_stats = store_stats.sort_values('total_sales', ascending=False)
        
        print(f"\n🏪 Store Performance Summary:")
        print(f"   Total stores: {len(store_stats)}")
        print(f"   Average sales per store: ${store_stats['total_sales'].mean():,.2f}")
        
        print(f"\n🏆 Top 5 Stores by Total Sales:")
        for idx, row in store_stats.head().iterrows():
            print(f"   Store {row['store_nbr']} ({row['city']}, {row['state']}): ${row['total_sales']:,.2f}")
        
        print(f"\n📉 Bottom 5 Stores by Total Sales:")
        for idx, row in store_stats.tail().iterrows():
            print(f"   Store {row['store_nbr']} ({row['city']}, {row['state']}): ${row['total_sales']:,.2f}")
        
        # Store type analysis
        type_stats = store_stats.groupby('type')['total_sales'].agg(['sum', 'mean', 'count'])
        print(f"\n🏬 Performance by Store Type:")
        print(type_stats.to_string())
        
        return store_stats
    
    def item_level_demand_patterns(self, df):
        """
        Analyze demand patterns at item level
        Returns: DataFrame with item-level statistics
        """
        print("\n" + "="*70)
        print("3. ITEM-LEVEL DEMAND PATTERNS")
        print("="*70)
        
        # Item-level aggregation
        item_stats = df.groupBy("item_nbr", "family", "class").agg(
            spark_sum("sales").alias("total_sales"),
            avg("sales").alias("avg_sales"),
            count("sales").alias("num_records")
        ).toPandas()
        
        item_stats = item_stats.sort_values('total_sales', ascending=False)
        
        print(f"\n📦 Item Performance Summary:")
        print(f"   Total items: {len(item_stats)}")
        print(f"   Average sales per item: ${item_stats['total_sales'].mean():,.2f}")
        
        print(f"\n🌟 Top 10 Items by Total Sales:")
        for idx, row in item_stats.head(10).iterrows():
            print(f"   Item {row['item_nbr']} ({row['family']}): ${row['total_sales']:,.2f}")
        
        # Family-level analysis
        family_stats = item_stats.groupby('family')['total_sales'].agg(['sum', 'mean', 'count'])
        family_stats = family_stats.sort_values('sum', ascending=False)
        
        print(f"\n🏷️  Top 10 Product Families:")
        print(family_stats.head(10).to_string())
        
        return item_stats
    
    def seasonal_holiday_impact_analysis(self, df):
        """
        Analyze seasonal patterns and holiday impact on sales
        Returns: Dictionary with seasonal and holiday insights
        """
        print("\n" + "="*70)
        print("4. SEASONAL & HOLIDAY IMPACT ANALYSIS")
        print("="*70)
        
        # Convert to pandas for analysis
        df_pd = df.select("date", "sales", "is_holiday", "day_of_week", "month").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        
        # Day of week analysis
        dow_sales = df_pd.groupby('day_of_week')['sales'].mean().reset_index()
        dow_sales.columns = ['day_of_week', 'avg_sales']
        
        print(f"\n📅 Average Sales by Day of Week:")
        dow_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday', 
                     5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
        for _, row in dow_sales.iterrows():
            print(f"   {dow_names[row['day_of_week']]}: ${row['avg_sales']:,.2f}")
        
        # Monthly seasonality
        monthly_avg = df_pd.groupby('month')['sales'].mean().reset_index()
        monthly_avg.columns = ['month', 'avg_sales']
        
        print(f"\n🗓️  Average Sales by Month:")
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        for _, row in monthly_avg.iterrows():
            print(f"   {month_names[row['month']]}: ${row['avg_sales']:,.2f}")
        
        peak_month = monthly_avg.loc[monthly_avg['avg_sales'].idxmax(), 'month']
        low_month = monthly_avg.loc[monthly_avg['avg_sales'].idxmin(), 'month']
        print(f"\n   📈 Peak sales month: {month_names[peak_month]}")
        print(f"   📉 Lowest sales month: {month_names[low_month]}")
        
        # Holiday impact
        holiday_sales = df_pd[df_pd['is_holiday'] == 1]['sales'].mean()
        non_holiday_sales = df_pd[df_pd['is_holiday'] == 0]['sales'].mean()
        
        print(f"\n🎉 Holiday Impact Analysis:")
        print(f"   Average sales on holidays: ${holiday_sales:,.2f}")
        print(f"   Average sales on non-holidays: ${non_holiday_sales:,.2f}")
        
        if holiday_sales > non_holiday_sales:
            impact = ((holiday_sales - non_holiday_sales) / non_holiday_sales) * 100
            print(f"   Holiday boost: +{impact:.2f}%")
        else:
            impact = ((non_holiday_sales - holiday_sales) / non_holiday_sales) * 100
            print(f"   Holiday impact: -{impact:.2f}%")
        
        return {
            'day_of_week': dow_sales,
            'monthly': monthly_avg,
            'holiday_impact': {
                'holiday_avg': holiday_sales,
                'non_holiday_avg': non_holiday_sales,
                'impact_pct': impact
            }
        }
    
    def generate_descriptive_report(self):
        """Generate complete descriptive analytics report"""
        print("\n" + "="*80)
        print("DESCRIPTIVE ANALYTICS REPORT")
        print("="*80)
        
        # Load data
        df = self.load_data()
        
        # Run all analyses
        trends = self.sales_trend_analysis(df)
        store_patterns = self.store_level_demand_patterns(df)
        item_patterns = self.item_level_demand_patterns(df)
        seasonal = self.seasonal_holiday_impact_analysis(df)
        
        print("\n" + "="*80)
        print("DESCRIPTIVE ANALYTICS COMPLETE")
        print("="*80)
        
        return {
            'trends': trends,
            'store_patterns': store_patterns,
            'item_patterns': item_patterns,
            'seasonal': seasonal
        }


if __name__ == "__main__":
    analytics = DescriptiveAnalytics()
    try:
        results = analytics.generate_descriptive_report()
        print("\n✅ Descriptive analytics completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
