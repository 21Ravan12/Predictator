"""Core Predictator engine - XGBoost powered"""

import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os
import logging
from pathlib import Path

# 🆕 XGBoost
import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


class PredictatorEngine:
    """Main prediction engine using XGBoost"""
    
    def __init__(self):
        # 🆕 XGBoost Model with optimized settings for your potato
        self.model = xgb.XGBRegressor(
            n_estimators=150,           # Number of trees
            learning_rate=0.05,         # How fast to learn
            max_depth=5,                # Tree depth (keep shallow = fast)
            random_state=42,            # Reproducibility
            subsample=0.8,              # Use 80% of data per tree
            colsample_bytree=0.8,       # Use 80% of features per tree
            reg_alpha=0.1,              # L1 regularization (prevents overfitting)
            reg_lambda=1.0,             # L2 regularization (prevents overfitting)
            verbosity=0,                # Quiet training
            n_jobs=-1,                  # Use all CPU cores 🚀
        )
        
        self.scaler = StandardScaler()  # XGBoost doesn't need this, but keeping for safety
        self.is_trained = False
        self.last_training_date = None
        self.training_metrics = {}
        self.total_predictions = 0
        self.feature_columns = []  # 🆕 Store feature names
        
        # 🆕 Try to load existing model
        self._load_model()
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-series features"""
        features = pd.DataFrame()
        df = df.copy()
        
        # Ensure date is datetime
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        
        # Time features
        features['day_of_week'] = df['date'].dt.dayofweek
        features['month'] = df['date'].dt.month
        features['quarter'] = df['date'].dt.quarter
        features['day_of_year'] = df['date'].dt.dayofyear
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        features['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # 🆕 Cyclical encoding
        features['day_of_week_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['day_of_week_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        
        # Lag features (more lags!)
        lags = [1, 2, 3, 7, 14, 21, 28, 30]
        for lag in lags:
            features[f'lag_{lag}'] = df['sales'].shift(lag)
        
        # Lag differences (trend indicators)
        features['lag_diff_1'] = df['sales'].diff(1)
        features['lag_diff_7'] = df['sales'].diff(7)
        features['lag_diff_28'] = df['sales'].diff(28)
        
        # Rolling averages
        windows = [3, 7, 14, 30]
        for window in windows:
            features[f'rolling_mean_{window}'] = df['sales'].rolling(window).mean()
            features[f'rolling_std_{window}'] = df['sales'].rolling(window).std()
        
        # 🆕 Rolling min/max
        features['rolling_min_7'] = df['sales'].rolling(7).min()
        features['rolling_max_7'] = df['sales'].rolling(7).max()
        
        # 🆕 Trend indicators
        features['rolling_trend_7'] = features['rolling_mean_7'] - features['rolling_mean_14']
        features['rolling_trend_30'] = features['rolling_mean_30'] - features['rolling_mean_14']
        
        # 🆕 Seasonal decomposition (simple)
        dow_avg = df.groupby(df['date'].dt.dayofweek)['sales'].transform('mean')
        features['seasonal_dow'] = dow_avg
        features['detrended'] = df['sales'] - features['rolling_mean_30']
        
        # Holiday features (if exists)
        if 'is_holiday' in df.columns:
            features['is_holiday'] = df['is_holiday'].fillna(0).astype(int)
        else:
            features['is_holiday'] = 0
        
        # 🆕 Price features (if exists)
        if 'price' in df.columns:
            features['price'] = df['price'].fillna(0)
            features['price_change'] = df['price'].pct_change().fillna(0)
        
        # 🆕 Promotion (if exists)
        if 'promotion' in df.columns:
            features['promotion'] = df['promotion'].fillna(0).astype(int)
        
        # 🆕 Temperature (if exists)
        if 'temperature' in df.columns:
            features['temperature'] = df['temperature'].fillna(0)
        
        # Clean NaN - forward fill then backward fill
        features = features.bfill().ffill()
        features = features.fillna(0)
        
        return features
    
    def train(self, df: pd.DataFrame) -> dict:
        """Train the XGBoost model"""
        logger.info(f"Training on {len(df)} samples...")
        
        # Create features
        features = self._create_features(df)
        target = df['sales'].values
        
        # 🆕 Store feature columns for later use in predict()
        self.feature_columns = features.columns.tolist()
        
        # Prepare data
        X = features.values
        y = target
        
        # Split for validation
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # 🆕 Train XGBoost
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        # Calculate metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        self.training_metrics = {
            'r2': r2,
            'mae': mae,
            'rmse': rmse,
            'n_features': len(self.feature_columns),
        }
        
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        logger.info(f"✅ Training complete! R²: {r2:.3f}")
        logger.info(f"📊 Features: {len(self.feature_columns)}")
        
        return self.training_metrics
    
    def predict(self, days_ahead: int, last_sales: pd.DataFrame, **kwargs) -> tuple:
        """Predict future sales using XGBoost"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first")
        
        if not self.feature_columns:
            raise ValueError("Feature columns not set. Train the model first!")
        
        predictions = []
        confidence_intervals = []
        
        current_data = last_sales.copy()
        
        # Get RMSE for confidence intervals
        rmse = self.training_metrics.get('rmse', 15)
        
        for i in range(days_ahead):
            # Create features for next day
            future_date = pd.date_range(
                start=current_data['date'].max(), 
                periods=2, 
                freq='D'
            )[1]
            
            # Get product_id and category from current_data
            product_id = current_data['product_id'].iloc[-1] if 'product_id' in current_data.columns else 'P001'
            category = current_data['category'].iloc[-1] if 'category' in current_data.columns else 'Electronics'
            season = current_data['season_name'].iloc[-1] if 'season_name' in current_data.columns else 'Summer'
            
            # Create a row with ALL required columns
            new_row = pd.DataFrame({
                'date': [future_date],
                'product_id': [product_id],
                'category': [category],
                'sales': [0],
                'price': [current_data['price'].iloc[-1] if 'price' in current_data.columns else 0],
                'holiday_name': ['None'],
                'season_name': [season],
                'event_type': ['Normal'],
                'is_holiday': [0],
                'promotion': [0],
                'temperature': [current_data['temperature'].iloc[-1] if 'temperature' in current_data.columns else 20],
            })
            
            # Combine with historical data
            temp_data = pd.concat([current_data, new_row], ignore_index=True)
            
            # Create features
            features = self._create_features(temp_data)
            
            # 🆕 CRITICAL: Use ONLY the columns the model was trained on!
            # This ensures the shape matches exactly
            if self.feature_columns:
                # Check if we have all required columns
                missing_cols = set(self.feature_columns) - set(features.columns)
                if missing_cols:
                    print(f"⚠️ Missing columns: {missing_cols}")
                    for col in missing_cols:
                        features[col] = 0
                
                # Select only the columns the model knows
                features = features[self.feature_columns]
            
            last_features = features.iloc[-1:].values
            
            # Predict with XGBoost
            pred = float(self.model.predict(last_features)[0])  
            pred = max(0, pred)  # No negative sales
            predictions.append(pred)
            
            # Confidence interval based on RMSE
            confidence_intervals.append((max(0, pred - rmse), pred + rmse))
            
            # Update for next iteration - keep ALL columns
            new_sale = pd.DataFrame({
                'date': [future_date],
                'product_id': [product_id],
                'category': [category],
                'sales': [pred],
                'price': [current_data['price'].iloc[-1] if 'price' in current_data.columns else 0],
                'holiday_name': ['None'],
                'season_name': [season],
                'event_type': ['Normal'],
                'is_holiday': [0],
                'promotion': [0],
                'temperature': [current_data['temperature'].iloc[-1] if 'temperature' in current_data.columns else 20],
            })
            current_data = pd.concat([current_data, new_sale], ignore_index=True)
        
        return np.array(predictions), np.array(confidence_intervals), None
    
    def enforce_floor_limit(self, predicted: float, floor_limit: int) -> tuple:
        """Dictator rule - enforce minimum sales"""
        if floor_limit > 0 and predicted < floor_limit:
            return float(floor_limit), f"⚠️ Enforced floor limit: {predicted:.0f} → {floor_limit}"
        return float(predicted), None
    
    def save_model(self, path: str = "model.pkl"):
        """Save model to disk"""
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'training_metrics': self.training_metrics,
                'last_training_date': self.last_training_date,
                'is_trained': self.is_trained,
                'total_predictions': self.total_predictions,
                'version': '2.0',
            }
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"💾 Model saved to {path}")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    def load_model(self, path: str = "model.pkl"):
        """Load model from disk and return whether a saved model was found."""
        return self._load_model(path)

    def _load_model(self, path: str = "model.pkl"):
        """Load model from disk"""
        if not os.path.exists(path):
            logger.info("⚠️ No existing model found")
            return False
        
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data.get('feature_columns', [])
            self.training_metrics = data.get('training_metrics', {})
            self.last_training_date = data.get('last_training_date')
            self.is_trained = data.get('is_trained', False)
            self.total_predictions = data.get('total_predictions', 0)
            
            version = data.get('version', '1.0')
            if version != '2.0':
                logger.warning(f"⚠️ Model version {version} vs current 2.0")
            
            logger.info(f"✅ Model loaded from {path} (R²: {self.training_metrics.get('r2', 0):.3f})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def generate_sample_data(self) -> pd.DataFrame:
        """Generate sample data for testing"""
        dates = pd.date_range(start='2026-01-01', end='2026-12-31', freq='D')
        np.random.seed(42)
        
        # Realistic pattern
        trend = 100 + np.arange(len(dates)) * 0.1
        weekly = 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
        monthly = 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / 30.4)
        noise = np.random.normal(0, 15, len(dates))
        
        sales = trend + weekly + monthly + noise
        sales = np.maximum(sales, 10)
        
        # More realistic data
        df = pd.DataFrame({
            'date': dates,
            'product_id': 'sample_product',
            'category': 'Electronics',
            'sales': sales,
            'price': 299.99 + np.random.normal(0, 5, len(dates)),
            'temperature': 20 + 10 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365),
            'is_holiday': (dates.dayofweek >= 5).astype(int),
            'promotion': np.random.choice([0, 1], size=len(dates), p=[0.9, 0.1]),
        })
        
        # Add some holiday spikes
        holiday_dates = ['2026-01-01', '2026-03-20', '2026-03-21', '2026-05-09']
        for h_date in holiday_dates:
            df.loc[df['date'] == pd.to_datetime(h_date), 'sales'] *= 1.5
            df.loc[df['date'] == pd.to_datetime(h_date), 'is_holiday'] = 1
        
        return df


# For backward compatibility
def get_predictator():
    """Dependency for FastAPI"""
    return PredictatorEngine()