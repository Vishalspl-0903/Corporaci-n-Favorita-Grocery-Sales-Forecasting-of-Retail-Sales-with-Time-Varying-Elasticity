"""
Evaluation Metrics Module
- SMAPE (Symmetric Mean Absolute Percentage Error) - for zero-inflated sales
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
"""
import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error


class Evaluator:
    """Handles model evaluation with multiple metrics"""
    
    @staticmethod
    def smape(y_true, y_pred):
        """
        Calculate Symmetric Mean Absolute Percentage Error (SMAPE)
        Suitable for zero-inflated sales data
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            SMAPE score (0-100)
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Avoid division by zero
        denominator = (np.abs(y_true) + np.abs(y_pred))
        
        # Calculate SMAPE
        smape_value = np.mean(
            2.0 * np.abs(y_pred - y_true) / np.where(denominator == 0, 1, denominator)
        ) * 100
        
        return smape_value
    
    @staticmethod
    def rmse(y_true, y_pred):
        """
        Calculate Root Mean Squared Error (RMSE)
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            RMSE score
        """
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    @staticmethod
    def mae(y_true, y_pred):
        """
        Calculate Mean Absolute Error (MAE)
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            MAE score
        """
        return mean_absolute_error(y_true, y_pred)
    
    @staticmethod
    def mape(y_true, y_pred):
        """
        Calculate Mean Absolute Percentage Error (MAPE)
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            
        Returns:
            MAPE score (0-100)
        """
        y_true = np.array(y_true)
        y_pred = np.array(y_pred)
        
        # Avoid division by zero - only calculate for non-zero actual values
        mask = y_true != 0
        
        if mask.sum() == 0:
            return 0.0
        
        mape_value = np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100
        
        return mape_value
    
    @staticmethod
    def evaluate_all(y_true, y_pred, model_name="Model"):
        """
        Evaluate using all metrics
        
        Args:
            y_true: Actual values
            y_pred: Predicted values
            model_name: Name of the model being evaluated
            
        Returns:
            Dictionary with all metrics
        """
        results = {
            'model': model_name,
            'SMAPE': Evaluator.smape(y_true, y_pred),
            'RMSE': Evaluator.rmse(y_true, y_pred),
            'MAE': Evaluator.mae(y_true, y_pred),
            'MAPE': Evaluator.mape(y_true, y_pred)
        }
        
        return results
    
    @staticmethod
    def print_evaluation(results):
        """
        Print evaluation results in a formatted way
        
        Args:
            results: Dictionary with evaluation metrics
        """
        print("\n" + "="*60)
        print(f"EVALUATION RESULTS: {results['model']}")
        print("="*60)
        print(f"SMAPE (Symmetric Mean Absolute Percentage Error): {results['SMAPE']:.4f}%")
        print(f"RMSE  (Root Mean Squared Error):                  {results['RMSE']:.4f}")
        print(f"MAE   (Mean Absolute Error):                      {results['MAE']:.4f}")
        print(f"MAPE  (Mean Absolute Percentage Error):           {results['MAPE']:.4f}%")
        print("="*60)
    
    @staticmethod
    def compare_models(results_list):
        """
        Compare multiple models
        
        Args:
            results_list: List of result dictionaries
            
        Returns:
            DataFrame with comparison
        """
        df = pd.DataFrame(results_list)
        df = df.sort_values('SMAPE')
        
        print("\n" + "="*80)
        print("MODEL COMPARISON")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80)
        print(f"\nBest Model (by SMAPE): {df.iloc[0]['model']} with SMAPE = {df.iloc[0]['SMAPE']:.4f}%")
        
        return df
    
    @staticmethod
    def save_results(results_list, filepath):
        """
        Save evaluation results to CSV
        
        Args:
            results_list: List of result dictionaries
            filepath: Path to save CSV file
        """
        df = pd.DataFrame(results_list)
        df.to_csv(filepath, index=False)
        print(f"\nResults saved to {filepath}")


if __name__ == "__main__":
    # Test the evaluator
    print("Testing Evaluator...")
    
    # Sample data
    y_true = np.array([100, 150, 200, 50, 0, 300])
    y_pred = np.array([95, 160, 190, 55, 5, 290])
    
    # Evaluate
    results = Evaluator.evaluate_all(y_true, y_pred, "Test Model")
    Evaluator.print_evaluation(results)
    
    print("\nEvaluator test completed!")
