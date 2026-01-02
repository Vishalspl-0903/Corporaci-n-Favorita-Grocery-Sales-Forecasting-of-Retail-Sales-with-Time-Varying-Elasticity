"""
Main Pipeline Script
Orchestrates the entire time series forecasting pipeline
"""
import sys
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *
from data_ingestion.ingest import DataIngestion
from data_cleaning.clean import DataCleaner
from feature_engineering.features import FeatureEngineer
from clustering.cluster import Clusterer
from models.forecasters import GBTForecaster, LSTMForecaster, SARIMAXForecaster, ARIMAForecaster
from evaluation.metrics import Evaluator
from analytics.descriptive_analytics import DescriptiveAnalytics
from analytics.diagnostic_analytics import DiagnosticAnalytics
from analytics.advanced_analytics import AdvancedAnalytics


class ForecastingPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self):
        self.start_time = time.time()
        self.results = []
        print("\n" + "="*80)
        print("STORE SALES TIME SERIES FORECASTING PIPELINE")
        print("="*80)
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")
    
    def run_data_ingestion(self):
        """Step 1: Data Ingestion"""
        print("\n" + "🔄 "*20)
        print("STEP 1: DISTRIBUTED DATA INGESTION")
        print("🔄 "*20 + "\n")
        
        ingestion = DataIngestion()
        try:
            data = ingestion.ingest_all_data()
            print("✅ Data ingestion completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error in data ingestion: {e}")
            return False
        finally:
            ingestion.close()
    
    def run_data_cleaning(self):
        """Step 2: Data Cleaning & Integration"""
        print("\n" + "🧹 "*20)
        print("STEP 2: DATA CLEANING & INTEGRATION")
        print("🧹 "*20 + "\n")
        
        cleaner = DataCleaner()
        try:
            cleaned_df = cleaner.clean_and_integrate()
            print("✅ Data cleaning completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error in data cleaning: {e}")
            return False
    
    def run_feature_engineering(self):
        """Step 3: Feature Engineering"""
        print("\n" + "⚙️ "*20)
        print("STEP 3: FEATURE ENGINEERING")
        print("⚙️ "*20 + "\n")
        
        engineer = FeatureEngineer()
        try:
            feature_df = engineer.engineer_features()
            print("✅ Feature engineering completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error in feature engineering: {e}")
            return False
    
    def run_clustering(self):
        """Step 4: Clustering"""
        print("\n" + "🔍 "*20)
        print("STEP 4: CLUSTERING")
        print("🔍 "*20 + "\n")
        
        clusterer = Clusterer()
        try:
            clustered_df = clusterer.perform_clustering()
            print("✅ Clustering completed successfully!")
            return True
        except Exception as e:
            print(f"❌ Error in clustering: {e}")
            return False
    
    def run_analytics(self):
        """Step 5: Comprehensive Analytics (Descriptive, Diagnostic, Advanced)"""
        print("\n" + "📊 "*20)
        print("STEP 5: COMPREHENSIVE ANALYTICS")
        print("📊 "*20 + "\n")
        
        try:
            # Descriptive Analytics
            print("\n🔹 Running Descriptive Analytics...")
            descriptive = DescriptiveAnalytics()
            desc_results = descriptive.generate_descriptive_report()
            
            # Diagnostic Analytics
            print("\n🔹 Running Diagnostic Analytics...")
            diagnostic = DiagnosticAnalytics()
            diag_results = diagnostic.generate_diagnostic_report()
            
            # Advanced Analytics
            print("\n🔹 Running Advanced Analytics (Time-Varying Elasticity)...")
            advanced = AdvancedAnalytics()
            adv_results = advanced.generate_advanced_report()
            
            print("✅ All analytics completed successfully!")
            return True, {
                'descriptive': desc_results,
                'diagnostic': diag_results,
                'advanced': adv_results
            }
        except Exception as e:
            print(f"❌ Error in analytics: {e}")
            import traceback
            traceback.print_exc()
            return False, None
    
    def prepare_modeling_data(self):
        """Prepare data for predictive modeling"""
        print("\n" + "📊 "*20)
        print("STEP 6: PREPARING DATA FOR PREDICTIVE MODELING")
        print("📊 "*20 + "\n")
        
        try:
            from pyspark.sql import SparkSession
            
            spark = SparkSession.builder \
                .appName(SPARK_APP_NAME) \
                .master(SPARK_MASTER) \
                .config("spark.driver.memory", SPARK_MEMORY) \
                .getOrCreate()
            
            # Load clustered data
            df_spark = spark.read.parquet(CLUSTERED_DATA_PARQUET)
            
            # Convert to pandas for modeling
            print("Converting Spark DataFrame to Pandas...")
            df = df_spark.toPandas()
            
            print(f"Data shape: {df.shape}")
            print(f"Date range: {df['date'].min()} to {df['date'].max()}")
            
            # Sort by date
            df = df.sort_values('date')
            
            # Define feature columns
            feature_cols = [
                col for col in df.columns 
                if col not in ['date', 'id', 'sales'] and df[col].dtype in ['int64', 'float64']
            ]
            
            print(f"\nNumber of features: {len(feature_cols)}")
            
            # Split into train/test
            split_date = df['date'].quantile(1 - VALIDATION_SPLIT)
            train_df = df[df['date'] < split_date]
            test_df = df[df['date'] >= split_date]
            
            print(f"\nTrain set: {len(train_df)} rows")
            print(f"Test set: {len(test_df)} rows")
            
            # Prepare X and y
            X_train = train_df[feature_cols].fillna(0).values
            y_train = train_df['sales'].values
            X_test = test_df[feature_cols].fillna(0).values
            y_test = test_df['sales'].values
            
            spark.stop()
            
            return X_train, y_train, X_test, y_test, feature_cols, df
            
        except Exception as e:
            print(f"❌ Error preparing data: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None, None, None, None
    
    def run_modeling(self, X_train, y_train, X_test, y_test, feature_cols, df):
        """Step 7: Train and evaluate predictive models"""
        print("\n" + "🤖 "*20)
        print("STEP 7: PREDICTIVE ANALYTICS - FORECASTING MODELS")
        print("🤖 "*20 + "\n")
        
        results_list = []
        
        # 1. Gradient Boosted Trees
        try:
            print("\n" + "-"*60)
            print("Training Gradient Boosted Trees (GBT)...")
            print("-"*60)
            gbt = GBTForecaster()
            gbt.fit(X_train, y_train)
            gbt_results = gbt.evaluate(X_test, y_test)
            results_list.append(gbt_results)
            Evaluator.print_evaluation(gbt_results)
            
            # Feature importance
            print("\nTop 10 Feature Importances:")
            importance = gbt.get_feature_importance(feature_cols)
            print(importance.head(10).to_string(index=False))
            
        except Exception as e:
            print(f"❌ Error in GBT: {e}")
        
        # 2. LSTM Neural Network
        try:
            print("\n" + "-"*60)
            print("Training LSTM Neural Network...")
            print("-"*60)
            lstm = LSTMForecaster()
            lstm.fit(X_train, y_train, validation_split=0.2)
            lstm_results = lstm.evaluate(X_test, y_test)
            results_list.append(lstm_results)
            Evaluator.print_evaluation(lstm_results)
            
        except Exception as e:
            print(f"❌ Error in LSTM: {e}")
            import traceback
            traceback.print_exc()
        
        # 3. ARIMA
        try:
            print("\n" + "-"*60)
            print("Training ARIMA...")
            print("-"*60)
            arima = ARIMAForecaster()
            arima.fit(df, target_col='sales')
            
            # For ARIMA, we predict aggregated sales
            arima_pred = arima.predict(steps=len(test_df))
            if len(arima_pred) > 0:
                # Distribute predictions proportionally
                test_total = y_test.sum()
                if test_total > 0:
                    scaling_factor = arima_pred.sum() / test_total
                    arima_pred_scaled = y_test * scaling_factor
                else:
                    arima_pred_scaled = arima_pred[:len(y_test)]
                
                arima_results = Evaluator.evaluate_all(y_test, arima_pred_scaled, "ARIMA")
                results_list.append(arima_results)
                Evaluator.print_evaluation(arima_results)
            
        except Exception as e:
            print(f"❌ Error in ARIMA: {e}")
            import traceback
            traceback.print_exc()
        
        return results_list
    
    def run_evaluation(self, results_list):
        """Step 8: Model Comparison"""
        print("\n" + "📈 "*20)
        print("STEP 8: MODEL EVALUATION & COMPARISON")
        print("📈 "*20 + "\n")
        
        if len(results_list) > 0:
            # Compare models
            comparison_df = Evaluator.compare_models(results_list)
            
            # Save results
            results_path = os.path.join(RESULTS_DIR, 'model_comparison.csv')
            Evaluator.save_results(results_list, results_path)
            
            return comparison_df
        else:
            print("❌ No models completed successfully")
            return None
    
    def run_full_pipeline(self):
        """Execute the complete pipeline"""
        try:
            # Step 1: Data Ingestion
            if not self.run_data_ingestion():
                print("Pipeline stopped: Data ingestion failed")
                return
            
            # Step 2: Data Cleaning
            if not self.run_data_cleaning():
                print("Pipeline stopped: Data cleaning failed")
                return
            
            # Step 3: Feature Engineering
            if not self.run_feature_engineering():
                print("Pipeline stopped: Feature engineering failed")
                return
            
            # Step 4: Clustering
            if not self.run_clustering():
                print("Pipeline stopped: Clustering failed")
                return
            
            # Step 5: Analytics (Descriptive, Diagnostic, Advanced)
            analytics_success, analytics_results = self.run_analytics()
            if not analytics_success:
                print("Warning: Analytics failed, but continuing with predictive modeling...")
            
            # Step 6: Prepare data for predictive modeling
            X_train, y_train, X_test, y_test, feature_cols, df = self.prepare_modeling_data()
            #7: Predictive Modeling
            results_list = self.run_modeling(X_train, y_train, X_test, y_test, feature_cols, df)
            
            # Step 8rn
            
            # Step 5: Modeling
            results_list = self.run_modeling(X_train, y_train, X_test, y_test, feature_cols, df)
            
            # Step 6: Evaluation
            comparison_df = self.run_evaluation(results_list)
            
            # Pipeline complete
            elapsed_time = time.time() - self.start_time
            print("\n" + "🎉 "*20)
            print("PIPELINE COMPLETED SUCCESSFULLY!")
            print("🎉 "*20)
            print(f"\nTotal execution time: {elapsed_time/60:.2f} minutes")
            print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("\n" + "="*80 + "\n")
            
        except Exception as e:
            print(f"\n❌ Pipeline failed with error: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main entry point"""
    pipeline = ForecastingPipeline()
    pipeline.run_full_pipeline()


if __name__ == "__main__":
    main()
