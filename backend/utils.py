"""
Utility Functions
Helper functions for the pipeline
"""
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from config import RESULTS_DIR


def visualize_results(results_csv_path):
    """
    Visualize model comparison results
    
    Args:
        results_csv_path: Path to model comparison CSV
    """
    df = pd.read_csv(results_csv_path)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Model Performance Comparison', fontsize=16, fontweight='bold')
    
    # SMAPE
    axes[0, 0].bar(df['model'], df['SMAPE'], color='skyblue')
    axes[0, 0].set_title('SMAPE (Lower is Better)')
    axes[0, 0].set_ylabel('SMAPE (%)')
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # RMSE
    axes[0, 1].bar(df['model'], df['RMSE'], color='lightcoral')
    axes[0, 1].set_title('RMSE (Lower is Better)')
    axes[0, 1].set_ylabel('RMSE')
    axes[0, 1].tick_params(axis='x', rotation=45)
    
    # MAE
    axes[1, 0].bar(df['model'], df['MAE'], color='lightgreen')
    axes[1, 0].set_title('MAE (Lower is Better)')
    axes[1, 0].set_ylabel('MAE')
    axes[1, 0].tick_params(axis='x', rotation=45)
    
    # Combined comparison
    metrics_normalized = df[['SMAPE', 'RMSE', 'MAE']].copy()
    for col in metrics_normalized.columns:
        metrics_normalized[col] = (metrics_normalized[col] - metrics_normalized[col].min()) / \
                                   (metrics_normalized[col].max() - metrics_normalized[col].min())
    
    x = range(len(df))
    width = 0.25
    axes[1, 1].bar([i - width for i in x], metrics_normalized['SMAPE'], 
                   width=width, label='SMAPE', color='skyblue')
    axes[1, 1].bar(x, metrics_normalized['RMSE'], 
                   width=width, label='RMSE', color='lightcoral')
    axes[1, 1].bar([i + width for i in x], metrics_normalized['MAE'], 
                   width=width, label='MAE', color='lightgreen')
    axes[1, 1].set_title('Normalized Metrics Comparison')
    axes[1, 1].set_ylabel('Normalized Score (0-1)')
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(df['model'], rotation=45)
    axes[1, 1].legend()
    
    plt.tight_layout()
    
    # Save figure
    output_path = os.path.join(RESULTS_DIR, 'model_comparison.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Visualization saved to {output_path}")
    
    plt.show()


def create_submission_file(predictions, test_ids, output_path):
    """
    Create submission file for competition
    
    Args:
        predictions: Array of predictions
        test_ids: Array of test IDs
        output_path: Path to save submission file
    """
    submission = pd.DataFrame({
        'id': test_ids,
        'sales': predictions
    })
    
    submission.to_csv(output_path, index=False)
    print(f"Submission file saved to {output_path}")


def get_data_summary(parquet_path):
    """
    Get summary statistics from a parquet file
    
    Args:
        parquet_path: Path to parquet file
    """
    df = pd.read_parquet(parquet_path)
    
    print("\n" + "="*60)
    print(f"DATA SUMMARY: {os.path.basename(parquet_path)}")
    print("="*60)
    print(f"\nShape: {df.shape}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
    print(f"\nColumns: {len(df.columns)}")
    print(df.columns.tolist())
    print(f"\nData types:\n{df.dtypes.value_counts()}")
    print(f"\nMissing values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"\nNumerical summary:\n{df.describe()}")
    print("="*60)


def plot_sales_trends(data_df, store_nbr=1, item_nbr=None):
    """
    Plot sales trends for a specific store/item
    
    Args:
        data_df: DataFrame with date and sales
        store_nbr: Store number to plot
        item_nbr: Item number to plot (optional)
    """
    df = data_df.copy()
    
    if item_nbr:
        df = df[(df['store_nbr'] == store_nbr) & (df['item_nbr'] == item_nbr)]
        title = f'Sales Trend - Store {store_nbr}, Item {item_nbr}'
    else:
        df = df[df['store_nbr'] == store_nbr]
        df = df.groupby('date')['sales'].sum().reset_index()
        title = f'Sales Trend - Store {store_nbr} (All Items)'
    
    plt.figure(figsize=(15, 6))
    plt.plot(df['date'], df['sales'])
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Sales')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    print("Utility functions loaded successfully!")
    print("\nAvailable functions:")
    print("- visualize_results(csv_path)")
    print("- create_submission_file(predictions, test_ids, output_path)")
    print("- get_data_summary(parquet_path)")
    print("- plot_sales_trends(data_df, store_nbr, item_nbr)")
