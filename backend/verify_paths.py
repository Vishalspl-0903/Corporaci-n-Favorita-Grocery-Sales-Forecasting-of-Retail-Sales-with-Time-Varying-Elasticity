"""
Path Verification Script
Verifies that all dataset files are accessible and paths are configured correctly
"""
import os
import sys

# Add backend to path if running from backend directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import *


def check_file(filepath, file_description):
    """Check if a file exists and print status"""
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) / (1024**2) if exists else 0  # Size in MB
    
    status = "✓" if exists else "✗"
    size_str = f"({size:.2f} MB)" if exists else "(NOT FOUND)"
    
    print(f"{status} {file_description:30s} {size_str}")
    return exists


def check_directory(dirpath, dir_description):
    """Check if a directory exists and print status"""
    exists = os.path.exists(dirpath)
    is_dir = os.path.isdir(dirpath) if exists else False
    
    status = "✓" if (exists and is_dir) else "✗"
    print(f"{status} {dir_description:30s} {'(exists)' if exists else '(NOT FOUND)'}")
    return exists and is_dir


def main():
    """Run all path verification checks"""
    print("="*70)
    print("PATH VERIFICATION - Dataset and Configuration Check")
    print("="*70)
    
    print(f"\nBase Directories:")
    print(f"  BASE_DIR (backend):  {BASE_DIR}")
    print(f"  ROOT_DIR (project):  {ROOT_DIR}")
    print(f"  DATA_DIR (CSVs):     {DATA_DIR}")
    
    # Check input CSV files
    print("\n" + "="*70)
    print("INPUT DATASET FILES (CSV)")
    print("="*70)
    
    csv_checks = []
    csv_checks.append(check_file(TRAIN_CSV, "train.csv"))
    csv_checks.append(check_file(TEST_CSV, "test.csv"))
    csv_checks.append(check_file(ITEMS_CSV, "items.csv"))
    csv_checks.append(check_file(STORES_CSV, "stores.csv"))
    csv_checks.append(check_file(HOLIDAYS_CSV, "holidays_events.csv"))
    csv_checks.append(check_file(OIL_CSV, "oil.csv"))
    csv_checks.append(check_file(TRANSACTIONS_CSV, "transactions.csv"))
    csv_checks.append(check_file(SAMPLE_SUBMISSION_CSV, "sample_submission.csv"))
    
    # Check processed data directory
    print("\n" + "="*70)
    print("PROCESSED DATA DIRECTORIES")
    print("="*70)
    
    dir_checks = []
    dir_checks.append(check_directory(PROCESSED_DATA_DIR, "data/processed/"))
    dir_checks.append(check_directory(MODEL_DIR, "models/saved_models/"))
    dir_checks.append(check_directory(RESULTS_DIR, "results/"))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    csv_passed = sum(csv_checks)
    csv_total = len(csv_checks)
    dir_passed = sum(dir_checks)
    dir_total = len(dir_checks)
    
    print(f"\nDataset Files:  {csv_passed}/{csv_total} found")
    print(f"Directories:    {dir_passed}/{dir_total} ready")
    
    if csv_passed == csv_total and dir_passed == dir_total:
        print("\n✅ All paths are correctly configured!")
        print("✅ All required files are present!")
        print("\n🚀 You're ready to run the pipeline:")
        print("   python main.py")
    else:
        print("\n⚠️  Some files or directories are missing!")
        
        if csv_passed < csv_total:
            print("\n❌ Missing CSV files:")
            print("   Please ensure all CSV files are in the project root directory:")
            print(f"   {ROOT_DIR}")
        
        if dir_passed < dir_total:
            print("\n❌ Missing directories:")
            print("   These will be created automatically when you run the pipeline.")
    
    print("="*70)
    
    return csv_passed == csv_total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
