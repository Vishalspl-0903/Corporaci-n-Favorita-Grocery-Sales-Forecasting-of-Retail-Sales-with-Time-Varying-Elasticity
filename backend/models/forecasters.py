"""
Forecasting Models Module
- SARIMAX (Seasonal AutoRegressive Integrated Moving Average with eXogenous factors)
- GBT (Gradient Boosted Trees)
- LSTM (Long Short-Term Memory)
- ARIMA (AutoRegressive Integrated Moving Average)
"""
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *
from evaluation.metrics import Evaluator


class BaseForecaster:
    """Base class for all forecasting models"""
    
    def __init__(self, model_name="BaseModel"):
        self.model_name = model_name
        self.model = None
        self.is_fitted = False
    
    def fit(self, X_train, y_train):
        """Fit the model"""
        raise NotImplementedError
    
    def predict(self, X_test):
        """Make predictions"""
        raise NotImplementedError
    
    def evaluate(self, X_test, y_test):
        """Evaluate the model"""
        predictions = self.predict(X_test)
        results = Evaluator.evaluate_all(y_test, predictions, self.model_name)
        return results


class GBTForecaster(BaseForecaster):
    """Gradient Boosted Trees Forecaster"""
    
    def __init__(self):
        super().__init__("Gradient Boosted Trees")
        self.model = GradientBoostingRegressor(
            n_estimators=GBT_N_ESTIMATORS,
            max_depth=GBT_MAX_DEPTH,
            learning_rate=GBT_LEARNING_RATE,
            random_state=42,
            verbose=0
        )
    
    def fit(self, X_train, y_train):
        """Fit GBT model"""
        print(f"\nTraining {self.model_name}...")
        self.model.fit(X_train, y_train)
        self.is_fitted = True
        print(f"{self.model_name} training complete!")
        return self
    
    def predict(self, X_test):
        """Make predictions with GBT"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        predictions = self.model.predict(X_test)
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        return predictions
    
    def get_feature_importance(self, feature_names):
        """Get feature importance"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted first")
        
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        return importance_df


class LSTMForecaster(BaseForecaster):
    """LSTM Neural Network Forecaster"""
    
    def __init__(self):
        super().__init__("LSTM Neural Network")
        self.model = None
        self.scaler_X = None
        self.scaler_y = None
    
    def build_model(self, input_shape):
        """Build LSTM model"""
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import LSTM, Dense, Dropout
        from tensorflow.keras.optimizers import Adam
        
        model = Sequential([
            LSTM(LSTM_UNITS, activation='relu', return_sequences=True, 
                 input_shape=input_shape),
            Dropout(0.2),
            LSTM(LSTM_UNITS // 2, activation='relu'),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dense(1)
        ])
        
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
        return model
    
    def fit(self, X_train, y_train, validation_split=0.2):
        """Fit LSTM model"""
        from sklearn.preprocessing import StandardScaler
        from tensorflow.keras.callbacks import EarlyStopping
        
        print(f"\nTraining {self.model_name}...")
        
        # Scale the data
        self.scaler_X = StandardScaler()
        self.scaler_y = StandardScaler()
        
        X_train_scaled = self.scaler_X.fit_transform(X_train)
        y_train_scaled = self.scaler_y.fit_transform(y_train.reshape(-1, 1))
        
        # Reshape for LSTM [samples, timesteps, features]
        X_train_reshaped = X_train_scaled.reshape(
            (X_train_scaled.shape[0], 1, X_train_scaled.shape[1])
        )
        
        # Build model
        self.model = self.build_model((1, X_train_scaled.shape[1]))
        
        # Early stopping
        early_stop = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
        
        # Train
        self.model.fit(
            X_train_reshaped, y_train_scaled,
            epochs=LSTM_EPOCHS,
            batch_size=LSTM_BATCH_SIZE,
            validation_split=validation_split,
            callbacks=[early_stop],
            verbose=1
        )
        
        self.is_fitted = True
        print(f"{self.model_name} training complete!")
        return self
    
    def predict(self, X_test):
        """Make predictions with LSTM"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        # Scale input
        X_test_scaled = self.scaler_X.transform(X_test)
        
        # Reshape for LSTM
        X_test_reshaped = X_test_scaled.reshape(
            (X_test_scaled.shape[0], 1, X_test_scaled.shape[1])
        )
        
        # Predict and inverse transform
        predictions_scaled = self.model.predict(X_test_reshaped, verbose=0)
        predictions = self.scaler_y.inverse_transform(predictions_scaled).flatten()
        
        # Ensure non-negative predictions
        predictions = np.maximum(predictions, 0)
        return predictions


class SARIMAXForecaster(BaseForecaster):
    """SARIMAX Time Series Forecaster"""
    
    def __init__(self):
        super().__init__("SARIMAX")
        self.models = {}  # Store models for each series
    
    def fit(self, data_df, target_col='sales', exog_cols=None):
        """
        Fit SARIMAX model
        Note: This is simplified - in practice, you'd fit separate models per store-item
        """
        from statsmodels.tsa.statespace.sarimax import SARIMAX
        
        print(f"\nTraining {self.model_name}...")
        print("Note: SARIMAX requires fitting individual models per time series")
        print("This is a simplified implementation")
        
        # For demonstration, fit a single aggregated model
        ts_data = data_df.groupby('date')[target_col].sum().sort_index()
        
        try:
            # Fit SARIMAX model with seasonal component
            model = SARIMAX(
                ts_data,
                order=(1, 1, 1),  # (p, d, q)
                seasonal_order=(1, 1, 1, 7),  # (P, D, Q, s) - weekly seasonality
                enforce_stationarity=False,
                enforce_invertibility=False
            )
            
            self.models['aggregate'] = model.fit(disp=False, maxiter=100)
            self.is_fitted = True
            print(f"{self.model_name} training complete!")
        except Exception as e:
            print(f"Error fitting SARIMAX: {e}")
            print("Using fallback prediction method")
        
        return self
    
    def predict(self, steps=FORECAST_HORIZON):
        """Make predictions with SARIMAX"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            forecast = self.models['aggregate'].forecast(steps=steps)
            predictions = np.maximum(forecast.values, 0)
            return predictions
        except Exception as e:
            print(f"Error in prediction: {e}")
            return np.zeros(steps)


class ARIMAForecaster(BaseForecaster):
    """ARIMA Time Series Forecaster (simpler than SARIMAX)"""
    
    def __init__(self):
        super().__init__("ARIMA")
        self.model_fit = None
    
    def fit(self, data_df, target_col='sales'):
        """Fit ARIMA model"""
        from statsmodels.tsa.arima.model import ARIMA
        
        print(f"\nTraining {self.model_name}...")
        
        # Aggregate time series
        ts_data = data_df.groupby('date')[target_col].sum().sort_index()
        
        try:
            # Fit ARIMA model
            model = ARIMA(ts_data, order=(5, 1, 2))
            self.model_fit = model.fit()
            self.is_fitted = True
            print(f"{self.model_name} training complete!")
        except Exception as e:
            print(f"Error fitting ARIMA: {e}")
        
        return self
    
    def predict(self, steps=FORECAST_HORIZON):
        """Make predictions with ARIMA"""
        if not self.is_fitted:
            raise ValueError("Model must be fitted before prediction")
        
        try:
            forecast = self.model_fit.forecast(steps=steps)
            predictions = np.maximum(forecast, 0)
            return predictions
        except Exception as e:
            print(f"Error in prediction: {e}")
            return np.zeros(steps)


if __name__ == "__main__":
    print("Forecasting models module loaded successfully!")
    print("Available models:")
    print("- GBTForecaster (Gradient Boosted Trees)")
    print("- LSTMForecaster (Long Short-Term Memory)")
    print("- SARIMAXForecaster (Seasonal ARIMA with exogenous variables)")
    print("- ARIMAForecaster (AutoRegressive Integrated Moving Average)")
