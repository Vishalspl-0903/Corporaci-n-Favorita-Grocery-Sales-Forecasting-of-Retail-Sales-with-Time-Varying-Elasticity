"""
Diagnostic Analytics Module
- Correlation between sales and external factors (oil prices, holidays)
- Identification of demand variability and volatility
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, corr, stddev, variance
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class DiagnosticAnalytics:
    """Performs diagnostic analytics to identify causes and relationships"""
    
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
        """Load feature-engineered data"""
        try:
            df = self.spark.read.parquet(FEATURE_DATA_PARQUET)
            print(f"Loaded feature data: {df.count()} rows")
        except:
            df = self.spark.read.parquet(CLEANED_DATA_PARQUET)
            print(f"Loaded cleaned data: {df.count()} rows")
        return df
    
    def correlation_with_oil_prices(self, df):
        """
        Analyze correlation between sales and oil prices
        """
        print("\n" + "="*70)
        print("1. CORRELATION: SALES vs OIL PRICES")
        print("="*70)
        
        # Convert to pandas for correlation analysis
        df_pd = df.select("sales", "dcoilwtico", "oil_price_change", 
                         "oil_volatility", "date").toPandas()
        
        # Calculate correlations
        corr_oil_sales = df_pd['sales'].corr(df_pd['dcoilwtico'])
        corr_oil_change_sales = df_pd['sales'].corr(df_pd['oil_price_change'])
        corr_oil_volatility_sales = df_pd['sales'].corr(df_pd['oil_volatility'])
        
        print(f"\n⛽ Oil Price Correlations:")
        print(f"   Sales vs Oil Price: {corr_oil_sales:.4f}")
        print(f"   Sales vs Oil Price Change: {corr_oil_change_sales:.4f}")
        print(f"   Sales vs Oil Volatility: {corr_oil_volatility_sales:.4f}")
        
        # Interpretation
        if abs(corr_oil_sales) > 0.5:
            strength = "strong"
        elif abs(corr_oil_sales) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"
        
        direction = "positive" if corr_oil_sales > 0 else "negative"
        
        print(f"\n💡 Interpretation:")
        print(f"   Oil prices show a {strength} {direction} correlation with sales")
        print(f"   When oil prices increase, sales tend to {'increase' if corr_oil_sales > 0 else 'decrease'}")
        
        # Statistical significance test
        statistic, p_value = stats.pearsonr(
            df_pd['sales'].dropna(), 
            df_pd['dcoilwtico'].dropna()
        )
        
        print(f"\n📊 Statistical Test:")
        print(f"   Pearson correlation: {statistic:.4f}")
        print(f"   P-value: {p_value:.4e}")
        print(f"   Significant: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")
        
        return {
            'oil_price_corr': corr_oil_sales,
            'oil_change_corr': corr_oil_change_sales,
            'oil_volatility_corr': corr_oil_volatility_sales,
            'p_value': p_value
        }
    
    def correlation_with_holidays(self, df):
        """
        Analyze correlation between sales and holidays
        """
        print("\n" + "="*70)
        print("2. CORRELATION: SALES vs HOLIDAYS")
        print("="*70)
        
        df_pd = df.select("sales", "is_holiday", "is_day_before_holiday", 
                         "is_day_after_holiday", "is_holiday_week").toPandas()
        
        # Calculate point-biserial correlation (for binary variables)
        corr_holiday = df_pd['sales'].corr(df_pd['is_holiday'])
        corr_before = df_pd['sales'].corr(df_pd['is_day_before_holiday'])
        corr_after = df_pd['sales'].corr(df_pd['is_day_after_holiday'])
        corr_week = df_pd['sales'].corr(df_pd['is_holiday_week'])
        
        print(f"\n🎉 Holiday Correlations:")
        print(f"   Sales vs Holiday: {corr_holiday:.4f}")
        print(f"   Sales vs Day Before Holiday: {corr_before:.4f}")
        print(f"   Sales vs Day After Holiday: {corr_after:.4f}")
        print(f"   Sales vs Holiday Week: {corr_week:.4f}")
        
        # Average sales comparison
        holiday_sales = df_pd[df_pd['is_holiday'] == 1]['sales'].mean()
        non_holiday_sales = df_pd[df_pd['is_holiday'] == 0]['sales'].mean()
        
        print(f"\n📊 Sales Impact:")
        print(f"   Average sales on holidays: ${holiday_sales:,.2f}")
        print(f"   Average sales on non-holidays: ${non_holiday_sales:,.2f}")
        
        if holiday_sales > non_holiday_sales:
            impact_pct = ((holiday_sales - non_holiday_sales) / non_holiday_sales) * 100
            print(f"   Holiday boost: +{impact_pct:.2f}%")
        else:
            impact_pct = ((non_holiday_sales - holiday_sales) / non_holiday_sales) * 100
            print(f"   Holiday impact: -{impact_pct:.2f}%")
        
        # T-test for significance
        holiday_group = df_pd[df_pd['is_holiday'] == 1]['sales'].dropna()
        non_holiday_group = df_pd[df_pd['is_holiday'] == 0]['sales'].dropna()
        
        t_stat, p_value = stats.ttest_ind(holiday_group, non_holiday_group)
        
        print(f"\n📊 Statistical Test:")
        print(f"   T-statistic: {t_stat:.4f}")
        print(f"   P-value: {p_value:.4e}")
        print(f"   Significant difference: {'Yes' if p_value < 0.05 else 'No'} (α=0.05)")
        
        return {
            'holiday_corr': corr_holiday,
            'before_holiday_corr': corr_before,
            'after_holiday_corr': corr_after,
            'holiday_week_corr': corr_week,
            'impact_pct': impact_pct,
            'p_value': p_value
        }
    
    def correlation_with_transactions(self, df):
        """
        Analyze correlation between sales and transaction volume
        """
        print("\n" + "="*70)
        print("3. CORRELATION: SALES vs TRANSACTIONS")
        print("="*70)
        
        df_pd = df.select("sales", "transactions", "date", "store_nbr").toPandas()
        df_pd = df_pd.dropna()
        
        # Calculate correlation
        corr_transactions = df_pd['sales'].corr(df_pd['transactions'])
        
        print(f"\n🛒 Transaction Correlation:")
        print(f"   Sales vs Transactions: {corr_transactions:.4f}")
        
        # Interpretation
        if abs(corr_transactions) > 0.7:
            strength = "very strong"
        elif abs(corr_transactions) > 0.5:
            strength = "strong"
        elif abs(corr_transactions) > 0.3:
            strength = "moderate"
        else:
            strength = "weak"
        
        print(f"\n💡 Interpretation:")
        print(f"   {strength.capitalize()} positive correlation")
        print(f"   Higher transaction volumes strongly associate with higher sales")
        
        # Calculate average basket size
        df_pd['basket_size'] = df_pd['sales'] / (df_pd['transactions'] + 1)  # +1 to avoid division by zero
        avg_basket = df_pd['basket_size'].mean()
        
        print(f"\n🛍️  Basket Analysis:")
        print(f"   Average basket size: ${avg_basket:.2f}")
        
        return {
            'transactions_corr': corr_transactions,
            'avg_basket_size': avg_basket
        }
    
    def demand_variability_analysis(self, df):
        """
        Identify demand variability and volatility
        """
        print("\n" + "="*70)
        print("4. DEMAND VARIABILITY & VOLATILITY ANALYSIS")
        print("="*70)
        
        # Store-level variability
        print("\n📊 Store-Level Variability:")
        store_var = df.groupBy("store_nbr").agg(
            stddev("sales").alias("sales_std"),
            variance("sales").alias("sales_var")
        ).toPandas()
        
        store_var = store_var.sort_values('sales_std', ascending=False)
        
        print(f"\n   Top 5 Most Volatile Stores:")
        for idx, row in store_var.head().iterrows():
            cv = (row['sales_std'] / np.sqrt(row['sales_var'])) * 100 if row['sales_var'] > 0 else 0
            print(f"   Store {row['store_nbr']}: Std=${row['sales_std']:.2f}, CV={cv:.2f}%")
        
        print(f"\n   Top 5 Most Stable Stores:")
        for idx, row in store_var.tail().iterrows():
            cv = (row['sales_std'] / np.sqrt(row['sales_var'])) * 100 if row['sales_var'] > 0 else 0
            print(f"   Store {row['store_nbr']}: Std=${row['sales_std']:.2f}, CV={cv:.2f}%")
        
        # Item-level variability
        print("\n📦 Item-Level Variability:")
        item_var = df.groupBy("item_nbr").agg(
            stddev("sales").alias("sales_std"),
            variance("sales").alias("sales_var")
        ).toPandas()
        
        item_var = item_var.sort_values('sales_std', ascending=False)
        
        print(f"\n   Top 5 Most Volatile Items:")
        for idx, row in item_var.head().iterrows():
            cv = (row['sales_std'] / np.sqrt(row['sales_var'])) * 100 if row['sales_var'] > 0 else 0
            print(f"   Item {row['item_nbr']}: Std=${row['sales_std']:.2f}, CV={cv:.2f}%")
        
        # Overall volatility metrics
        df_pd = df.select("sales", "date").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        
        # Calculate daily total sales
        daily_sales = df_pd.groupby('date')['sales'].sum().reset_index()
        daily_sales['returns'] = daily_sales['sales'].pct_change()
        daily_sales['volatility'] = daily_sales['returns'].rolling(window=7).std()
        
        avg_volatility = daily_sales['volatility'].mean()
        max_volatility = daily_sales['volatility'].max()
        
        print(f"\n📉 Overall Market Volatility:")
        print(f"   Average 7-day volatility: {avg_volatility*100:.2f}%")
        print(f"   Maximum 7-day volatility: {max_volatility*100:.2f}%")
        
        # Coefficient of variation
        overall_cv = (df_pd['sales'].std() / df_pd['sales'].mean()) * 100
        print(f"   Coefficient of Variation: {overall_cv:.2f}%")
        
        return {
            'store_variability': store_var,
            'item_variability': item_var,
            'avg_volatility': avg_volatility,
            'overall_cv': overall_cv
        }
    
    def correlation_matrix(self, df):
        """
        Generate correlation matrix for all key variables
        """
        print("\n" + "="*70)
        print("5. COMPREHENSIVE CORRELATION MATRIX")
        print("="*70)
        
        # Select numerical features
        feature_cols = [
            'sales', 'dcoilwtico', 'transactions', 'is_holiday',
            'day_of_week', 'month', 'oil_price_change', 'oil_volatility'
        ]
        
        # Check which columns exist
        existing_cols = [col for col in feature_cols if col in df.columns]
        
        df_pd = df.select(existing_cols).toPandas()
        
        # Calculate correlation matrix
        corr_matrix = df_pd.corr()
        
        print(f"\n📊 Correlation Matrix:")
        print(corr_matrix.to_string())
        
        # Find strongest correlations with sales
        sales_corr = corr_matrix['sales'].sort_values(ascending=False)
        
        print(f"\n🎯 Strongest Correlations with Sales:")
        for feature, corr_value in sales_corr.items():
            if feature != 'sales' and abs(corr_value) > 0.1:
                print(f"   {feature}: {corr_value:.4f}")
        
        return corr_matrix
    
    def generate_diagnostic_report(self):
        """Generate complete diagnostic analytics report"""
        print("\n" + "="*80)
        print("DIAGNOSTIC ANALYTICS REPORT")
        print("="*80)
        
        # Load data
        df = self.load_data()
        
        # Run all analyses
        oil_corr = self.correlation_with_oil_prices(df)
        holiday_corr = self.correlation_with_holidays(df)
        trans_corr = self.correlation_with_transactions(df)
        variability = self.demand_variability_analysis(df)
        corr_matrix = self.correlation_matrix(df)
        
        print("\n" + "="*80)
        print("DIAGNOSTIC ANALYTICS COMPLETE")
        print("="*80)
        
        return {
            'oil_correlation': oil_corr,
            'holiday_correlation': holiday_corr,
            'transaction_correlation': trans_corr,
            'variability': variability,
            'correlation_matrix': corr_matrix
        }


if __name__ == "__main__":
    analytics = DiagnosticAnalytics()
    try:
        results = analytics.generate_diagnostic_report()
        print("\n✅ Diagnostic analytics completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
