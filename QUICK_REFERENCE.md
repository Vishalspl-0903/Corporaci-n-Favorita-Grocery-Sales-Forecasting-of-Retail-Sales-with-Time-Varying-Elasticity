# 🚀 QUICK REFERENCE CARD

## 📍 Your Current Setup

```
✅ Project Path:  E:\SEM-6\Projects\BDA_TSA
✅ Dataset Files: 8/8 files present (4.9 GB)
✅ Code Status:   Complete and ready
✅ Paths:         Correctly configured
```

## 🎯 Quick Commands

### Verify Everything
```bash
cd backend
python verify_paths.py
```

### Check Environment
```bash
cd backend
python check_environment.py
```

### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Run Pipeline
```bash
cd backend
python main.py
```

## 📁 Key Files & Locations

| What | Where | Description |
|------|-------|-------------|
| **Datasets** | `BDA_TSA/*.csv` | All 8 CSV files |
| **Main Pipeline** | `backend/main.py` | Run this! |
| **Configuration** | `backend/config.py` | All settings |
| **Documentation** | `backend/README.md` | Complete guide |
| **Quick Start** | `backend/QUICKSTART.md` | 5-min guide |

## 🔧 Path Configuration

**CSVs Location**: `E:\SEM-6\Projects\BDA_TSA\*.csv`
**Backend Code**: `E:\SEM-6\Projects\BDA_TSA\backend\`
**Run From**: Always run from `backend/` directory

```bash
# Always start here:
cd E:\SEM-6\Projects\BDA_TSA\backend
```

## 📊 Pipeline Stages

1. **Data Ingestion** → Spark loads CSVs to Parquet
2. **Data Cleaning** → Clean & integrate data
3. **Feature Engineering** → Create 30+ features
4. **Clustering** → Item & store segmentation
5. **Forecasting** → SARIMAX, GBT, LSTM, ARIMA
6. **Evaluation** → SMAPE, RMSE, MAE metrics

## 🎯 Expected Output

After running `python main.py`:

- **Processed Data**: `backend/data/processed/*.parquet`
- **Results**: `backend/results/model_comparison.csv`
- **Console**: Detailed logs and metrics
- **Runtime**: 10-30 minutes

## 🆘 Common Issues

### Java Not Found
```bash
# Install JDK 8 or 11
# Set JAVA_HOME environment variable
```

### Out of Memory
```python
# In config.py, change:
SPARK_MEMORY = "2g"  # Reduce from 4g
```

### Package Not Found
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 📚 Documentation Files

- `SETUP_COMPLETE.md` - Setup summary ⭐
- `README.md` - Complete documentation
- `QUICKSTART.md` - Quick start guide
- `PROJECT_OVERVIEW.md` - Detailed overview
- `PROJECT_STRUCTURE.md` - File structure
- `FILES_CREATED.md` - What was created

## ✅ Git Configuration

**.gitignore includes**:
- Python cache files
- Generated data (*.parquet)
- Model files (*.h5, *.pkl)
- Results (*.csv, *.png in results/)
- IDE settings

**Tracked in git**:
- All source code
- Documentation
- Configuration files
- Empty directory structure

## 🎉 You're All Set!

```bash
cd backend
python main.py
```

---

**Project**: Store Sales Forecasting with Big Data
**Status**: ✅ Ready to Run
**Date**: January 2, 2026
