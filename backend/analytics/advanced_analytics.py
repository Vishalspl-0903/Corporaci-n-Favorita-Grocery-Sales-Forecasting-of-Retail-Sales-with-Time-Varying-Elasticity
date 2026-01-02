"""
Advanced/Novel Analytics Module
- Time-varying contextual elasticity
- Measuring how external factors impact sales differently across time
- Dynamic elasticity estimation using rolling windows
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *


class AdvancedAnalytics:
    """
    Performs advanced analytics including time-varying elasticity
    """
    
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
    
    def calculate_oil_price_elasticity(self, df, window_size=90):
        """
        Calculate time-varying oil price elasticity
        Elasticity = % change in sales / % change in oil price
        """
        print("\n" + "="*70)
        print("1. TIME-VARYING OIL PRICE ELASTICITY")
        print("="*70)
        
        # Convert to pandas
        df_pd = df.select("date", "sales", "dcoilwtico", "store_nbr", "item_nbr").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        
        # Aggregate to daily level
        daily_data = df_pd.groupby('date').agg({
            'sales': 'sum',
            'dcoilwtico': 'mean'
        }).reset_index()
        
        # Calculate percentage changes
        daily_data['sales_pct_change'] = daily_data['sales'].pct_change() * 100
        daily_data['oil_pct_change'] = daily_data['dcoilwtico'].pct_change() * 100
        
        # Calculate rolling elasticity
        elasticity_results = []
        
        for i in range(window_size, len(daily_data)):
            window_data = daily_data.iloc[i-window_size:i]
            
            # Avoid division by zero
            valid_data = window_data[
                (window_data['oil_pct_change'] != 0) & 
                (window_data['oil_pct_change'].notna()) &
                (window_data['sales_pct_change'].notna())
            ]
            
            if len(valid_data) > 10:
                # Simple elasticity: average % change in sales / average % change in oil
                elasticity = valid_data['sales_pct_change'].mean() / valid_data['oil_pct_change'].mean()
                
                # Regression-based elasticity (more robust)
                X = valid_data['oil_pct_change'].values.reshape(-1, 1)
                y = valid_data['sales_pct_change'].values
                
                model = LinearRegression()
                model.fit(X, y)
                regression_elasticity = model.coef_[0]
                
                elasticity_results.append({
                    'date': daily_data.iloc[i]['date'],
                    'simple_elasticity': elasticity,
                    'regression_elasticity': regression_elasticity,
                    'r_squared': model.score(X, y)
                })
        
        elasticity_df = pd.DataFrame(elasticity_results)
        
        print(f"\n⛽ Oil Price Elasticity Over Time ({window_size}-day window):")
        print(f"   Average elasticity: {elasticity_df['regression_elasticity'].mean():.4f}")
        print(f"   Median elasticity: {elasticity_df['regression_elasticity'].median():.4f}")
        print(f"   Std deviation: {elasticity_df['regression_elasticity'].std():.4f}")
        print(f"   Min elasticity: {elasticity_df['regression_elasticity'].min():.4f}")
        print(f"   Max elasticity: {elasticity_df['regression_elasticity'].max():.4f}")
        
        # Identify periods of high/low elasticity
        high_elasticity = elasticity_df.nlargest(5, 'regression_elasticity')
        low_elasticity = elasticity_df.nsmallest(5, 'regression_elasticity')
        
        print(f"\n📈 Periods of Highest Elasticity (most sensitive to oil):")
        for _, row in high_elasticity.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['regression_elasticity']:.4f}")
        
        print(f"\n📉 Periods of Lowest Elasticity (least sensitive to oil):")
        for _, row in low_elasticity.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['regression_elasticity']:.4f}")
        
        # Interpretation
        avg_elasticity = elasticity_df['regression_elasticity'].mean()
        
        print(f"\n💡 Interpretation:")
        if abs(avg_elasticity) < 0.1:
            print(f"   Inelastic: Sales are relatively insensitive to oil price changes")
        elif abs(avg_elasticity) < 0.5:
            print(f"   Moderately elastic: Sales show some sensitivity to oil prices")
        else:
            print(f"   Highly elastic: Sales are very sensitive to oil price changes")
        
        if avg_elasticity < 0:
            print(f"   Negative elasticity: Higher oil prices → Lower sales")
        else:
            print(f"   Positive elasticity: Higher oil prices → Higher sales")
        
        return elasticity_df
    
    def calculate_holiday_elasticity(self, df, window_size=60):
        """
        Calculate time-varying holiday impact elasticity
        """
        print("\n" + "="*70)
        print("2. TIME-VARYING HOLIDAY ELASTICITY")
        print("="*70)
        
        df_pd = df.select("date", "sales", "is_holiday").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        
        # Aggregate to daily level
        daily_data = df_pd.groupby('date').agg({
            'sales': 'sum',
            'is_holiday': 'max'
        }).reset_index()
        
        # Calculate rolling holiday impact
        elasticity_results = []
        
        for i in range(window_size, len(daily_data)):
            window_data = daily_data.iloc[i-window_size:i]
            
            holiday_sales = window_data[window_data['is_holiday'] == 1]['sales'].mean()
            non_holiday_sales = window_data[window_data['is_holiday'] == 0]['sales'].mean()
            
            if non_holiday_sales > 0 and not pd.isna(holiday_sales):
                # Holiday lift percentage
                holiday_lift = ((holiday_sales - non_holiday_sales) / non_holiday_sales) * 100
                
                elasticity_results.append({
                    'date': daily_data.iloc[i]['date'],
                    'holiday_lift': holiday_lift,
                    'holiday_sales_avg': holiday_sales,
                    'non_holiday_sales_avg': non_holiday_sales
                })
        
        elasticity_df = pd.DataFrame(elasticity_results)
        
        print(f"\n🎉 Holiday Impact Over Time ({window_size}-day window):")
        print(f"   Average holiday lift: {elasticity_df['holiday_lift'].mean():.2f}%")
        print(f"   Median holiday lift: {elasticity_df['holiday_lift'].median():.2f}%")
        print(f"   Std deviation: {elasticity_df['holiday_lift'].std():.2f}%")
        print(f"   Max lift: {elasticity_df['holiday_lift'].max():.2f}%")
        print(f"   Min lift: {elasticity_df['holiday_lift'].min():.2f}%")
        
        # Identify best and worst holiday periods
        best_holidays = elasticity_df.nlargest(5, 'holiday_lift')
        worst_holidays = elasticity_df.nsmallest(5, 'holiday_lift')
        
        print(f"\n📈 Periods with Strongest Holiday Impact:")
        for _, row in best_holidays.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: +{row['holiday_lift']:.2f}%")
        
        print(f"\n📉 Periods with Weakest Holiday Impact:")
        for _, row in worst_holidays.iterrows():
            print(f"   {row['date'].strftime('%Y-%m-%d')}: {row['holiday_lift']:.2f}%")
        
        return elasticity_df
    
    def calculate_transaction_elasticity(self, df, window_size=90):
        """
        Calculate time-varying transaction volume elasticity
        """
        print("\n" + "="*70)
        print("3. TIME-VARYING TRANSACTION ELASTICITY")
        print("="*70)
        
        df_pd = df.select("date", "sales", "transactions").toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        df_pd = df_pd.dropna()
        
        # Aggregate to daily level
        daily_data = df_pd.groupby('date').agg({
            'sales': 'sum',
            'transactions': 'sum'
        }).reset_index()
        
        # Calculate percentage changes
        daily_data['sales_pct_change'] = daily_data['sales'].pct_change() * 100
        daily_data['trans_pct_change'] = daily_data['transactions'].pct_change() * 100
        
        # Calculate rolling elasticity
        elasticity_results = []
        
        for i in range(window_size, len(daily_data)):
            window_data = daily_data.iloc[i-window_size:i]
            
            valid_data = window_data[
                (window_data['trans_pct_change'] != 0) & 
                (window_data['trans_pct_change'].notna()) &
                (window_data['sales_pct_change'].notna())
            ]
            
            if len(valid_data) > 10:
                # Regression-based elasticity
                X = valid_data['trans_pct_change'].values.reshape(-1, 1)
                y = valid_data['sales_pct_change'].values
                
                model = LinearRegression()
                model.fit(X, y)
                elasticity = model.coef_[0]
                
                elasticity_results.append({
                    'date': daily_data.iloc[i]['date'],
                    'transaction_elasticity': elasticity,
                    'r_squared': model.score(X, y)
                })
        
        elasticity_df = pd.DataFrame(elasticity_results)
        
        print(f"\n🛒 Transaction Volume Elasticity ({window_size}-day window):")
        print(f"   Average elasticity: {elasticity_df['transaction_elasticity'].mean():.4f}")
        print(f"   Median elasticity: {elasticity_df['transaction_elasticity'].median():.4f}")
        print(f"   Std deviation: {elasticity_df['transaction_elasticity'].std():.4f}")
        
        print(f"\n💡 Interpretation:")
        avg_elasticity = elasticity_df['transaction_elasticity'].mean()
        print(f"   On average, a 1% increase in transactions → {avg_elasticity:.2f}% change in sales")
        
        return elasticity_df
    
    def multivariate_elasticity_analysis(self, df, window_size=90):
        """
        Multivariate analysis: How multiple factors jointly impact sales over time
        """
        print("\n" + "="*70)
        print("4. MULTIVARIATE TIME-VARYING ELASTICITY")
        print("="*70)
        
        # Select features
        feature_cols = ['date', 'sales', 'dcoilwtico', 'transactions', 'is_holiday', 
                       'day_of_week', 'month']
        
        df_pd = df.select([c for c in feature_cols if c in df.columns]).toPandas()
        df_pd['date'] = pd.to_datetime(df_pd['date'])
        df_pd = df_pd.sort_values('date')
        df_pd = df_pd.dropna()
        
        # Aggregate to daily level
        daily_data = df_pd.groupby('date').agg({
            'sales': 'sum',
            'dcoilwtico': 'mean',
            'transactions': 'sum',
            'is_holiday': 'max'
        }).reset_index()
        
        # Calculate rolling multivariate elasticity
        elasticity_results = []
        
        for i in range(window_size, len(daily_data)):
            window_data = daily_data.iloc[i-window_size:i]
            
            # Prepare features
            X = window_data[['dcoilwtico', 'transactions', 'is_holiday']].values
            y = window_data['sales'].values
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Ridge regression (handles multicollinearity)
            model = Ridge(alpha=1.0)
            model.fit(X_scaled, y)
            
            elasticity_results.append({
                'date': daily_data.iloc[i]['date'],
                'oil_coefficient': model.coef_[0],
                'transaction_coefficient': model.coef_[1],
                'holiday_coefficient': model.coef_[2],
                'r_squared': model.score(X_scaled, y)
            })
        
        elasticity_df = pd.DataFrame(elasticity_results)
        
        print(f"\n📊 Multivariate Elasticity Analysis ({window_size}-day window):")
        print(f"\n   Oil Price Impact:")
        print(f"      Average coefficient: {elasticity_df['oil_coefficient'].mean():.2f}")
        print(f"      Std deviation: {elasticity_df['oil_coefficient'].std():.2f}")
        
        print(f"\n   Transaction Impact:")
        print(f"      Average coefficient: {elasticity_df['transaction_coefficient'].mean():.2f}")
        print(f"      Std deviation: {elasticity_df['transaction_coefficient'].std():.2f}")
        
        print(f"\n   Holiday Impact:")
        print(f"      Average coefficient: {elasticity_df['holiday_coefficient'].mean():.2f}")
        print(f"      Std deviation: {elasticity_df['holiday_coefficient'].std():.2f}")
        
        print(f"\n   Model Fit (R²):")
        print(f"      Average R²: {elasticity_df['r_squared'].mean():.4f}")
        
        print(f"\n💡 Key Insights:")
        # Identify which factor is most important
        importance = {
            'Oil Prices': abs(elasticity_df['oil_coefficient'].mean()),
            'Transactions': abs(elasticity_df['transaction_coefficient'].mean()),
            'Holidays': abs(elasticity_df['holiday_coefficient'].mean())
        }
        
        most_important = max(importance, key=importance.get)
        print(f"   Most influential factor: {most_important}")
        print(f"   Relative importance: Oil={importance['Oil Prices']:.2f}, "
              f"Trans={importance['Transactions']:.2f}, Holiday={importance['Holidays']:.2f}")
        
        return elasticity_df
    
    def temporal_elasticity_patterns(self, elasticity_df, factor_name):
        """
        Analyze temporal patterns in elasticity (seasonality, trends)
        """
        print(f"\n📅 Temporal Patterns in {factor_name} Elasticity:")
        
        elasticity_df['month'] = elasticity_df['date'].dt.month
        elasticity_df['quarter'] = elasticity_df['date'].dt.quarter
        elasticity_df['year'] = elasticity_df['date'].dt.year
        
        # Monthly patterns
        monthly_elasticity = elasticity_df.groupby('month').agg({
            list(elasticity_df.columns)[1]: 'mean'
        }).reset_index()
        
        elasticity_col = list(elasticity_df.columns)[1]
        
        print(f"\n   Monthly Variation:")
        month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                      7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        
        for _, row in monthly_elasticity.iterrows():
            print(f"      {month_names[row['month']]}: {row[elasticity_col]:.4f}")
        
        return monthly_elasticity
    
    def generate_advanced_report(self):
        """Generate complete advanced analytics report"""
        print("\n" + "="*80)
        print("ADVANCED/NOVEL ANALYTICS REPORT")
        print("Time-Varying Contextual Elasticity Analysis")
        print("="*80)
        
        # Load data
        df = self.load_data()
        
        # Run all analyses
        oil_elasticity = self.calculate_oil_price_elasticity(df, window_size=90)
        holiday_elasticity = self.calculate_holiday_elasticity(df, window_size=60)
        trans_elasticity = self.calculate_transaction_elasticity(df, window_size=90)
        multivariate = self.multivariate_elasticity_analysis(df, window_size=90)
        
        # Temporal patterns
        self.temporal_elasticity_patterns(oil_elasticity, "Oil Price")
        self.temporal_elasticity_patterns(holiday_elasticity, "Holiday")
        
        print("\n" + "="*80)
        print("ADVANCED ANALYTICS COMPLETE")
        print("="*80)
        
        return {
            'oil_elasticity': oil_elasticity,
            'holiday_elasticity': holiday_elasticity,
            'transaction_elasticity': trans_elasticity,
            'multivariate_elasticity': multivariate
        }


if __name__ == "__main__":
    analytics = AdvancedAnalytics()
    try:
        results = analytics.generate_advanced_report()
        print("\n✅ Advanced analytics completed successfully!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
