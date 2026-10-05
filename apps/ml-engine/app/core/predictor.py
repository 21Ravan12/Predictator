"""Core Predictator engine - XGBoost powered (Multi-Product Edition)"""

import pandas as pd
import numpy as np
from datetime import datetime
import pickle
import os
import logging
from pathlib import Path

import xgboost as xgb
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

logger = logging.getLogger(__name__)


class PredictatorEngine:
    """Main prediction engine using XGBoost (multi-product)"""
    
    def __init__(self):
        self.model = xgb.XGBRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            random_state=42,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_alpha=0.1,
            reg_lambda=1.0,
            verbosity=0,
            n_jobs=-1,
        )
        
        self.scaler = StandardScaler()
        self.is_trained = False
        self.last_training_date = None
        self.training_metrics = {}
        self.total_predictions = 0
        self.feature_columns = []
        
        # 🆕 Store product metadata for prediction context
        self.product_categories = {}  # {product_id: category}
        self.product_prices = {}      # {product_id: price}
        
        self._load_model()
    
    # ============================================
    # 🔧 FEATURE ENGINEERING
    # ============================================
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create features — handles MULTIPLE products correctly"""
        df = df.copy()
        df['date'] = pd.to_datetime(df['date'])
        
        # 🆕 Sort by product then date (CRITICAL for correct lags)
        df = df.sort_values(['product_id', 'date']).reset_index(drop=True)
        
        features = pd.DataFrame(index=df.index)
        
        # ============================================
        # ⏰ TIME FEATURES
        # ============================================
        features['day_of_week'] = df['date'].dt.dayofweek
        features['month'] = df['date'].dt.month
        features['quarter'] = df['date'].dt.quarter
        features['day_of_year'] = df['date'].dt.dayofyear
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        features['is_month_start'] = df['date'].dt.is_month_start.astype(int)
        features['is_month_end'] = df['date'].dt.is_month_end.astype(int)
        
        # Cyclical encoding
        features['day_of_week_sin'] = np.sin(2 * np.pi * features['day_of_week'] / 7)
        features['day_of_week_cos'] = np.cos(2 * np.pi * features['day_of_week'] / 7)
        features['month_sin'] = np.sin(2 * np.pi * features['month'] / 12)
        features['month_cos'] = np.cos(2 * np.pi * features['month'] / 12)
        
        # ============================================
        # 📊 LAG FEATURES (PER PRODUCT!) 🆕
        # ============================================
        lags = [1, 2, 3, 7, 14, 21, 28, 30]
        for lag in lags:
            features[f'lag_{lag}'] = df.groupby('product_id')['sales'].shift(lag)
        
        # Lag differences
        features['lag_diff_1'] = df.groupby('product_id')['sales'].diff(1)
        features['lag_diff_7'] = df.groupby('product_id')['sales'].diff(7)
        features['lag_diff_28'] = df.groupby('product_id')['sales'].diff(28)
        
        # ============================================
        # 📈 ROLLING FEATURES (PER PRODUCT!) 🆕
        # ============================================
        windows = [3, 7, 14, 30]
        for window in windows:
            features[f'rolling_mean_{window}'] = (
                df.groupby('product_id')['sales']
                .transform(lambda x: x.rolling(window, min_periods=1).mean())
            )
            features[f'rolling_std_{window}'] = (
                df.groupby('product_id')['sales']
                .transform(lambda x: x.rolling(window, min_periods=1).std())
            )
        
        # Rolling min/max
        features['rolling_min_7'] = (
            df.groupby('product_id')['sales']
            .transform(lambda x: x.rolling(7, min_periods=1).min())
        )
        features['rolling_max_7'] = (
            df.groupby('product_id')['sales']
            .transform(lambda x: x.rolling(7, min_periods=1).max())
        )
        
        # Trend indicators
        features['rolling_trend_7'] = features['rolling_mean_7'] - features['rolling_mean_14']
        features['rolling_trend_30'] = features['rolling_mean_30'] - features['rolling_mean_14']
        
        # Seasonal decomposition
        features['seasonal_dow'] = (
            df.groupby(['product_id', df['date'].dt.dayofweek])['sales']
            .transform('mean')
        )
        features['detrended'] = df['sales'] - features['rolling_mean_30']
        
        # ============================================
        # 🎉 HOLIDAY & EVENT FEATURES
        # ============================================
        if 'holiday_name' in df.columns:
            features['is_holiday'] = (
                df['holiday_name'].notna() & 
                (df['holiday_name'] != 'None')
            ).astype(int)
        else:
            features['is_holiday'] = 0
        
        if 'event_type' in df.columns:
            features['is_promotion'] = (df['event_type'] == 'Promotion').astype(int)
            features['is_ramadan'] = (df['event_type'] == 'Ramadan').astype(int)
        else:
            features['is_promotion'] = 0
            features['is_ramadan'] = 0
        
        if 'is_promo' in df.columns:
            features['is_promo'] = df['is_promo'].fillna(0).astype(int)
        else:
            features['is_promo'] = 0
        
        # ============================================
        # 💰 PRICE FEATURES
        # ============================================
        if 'price' in df.columns:
            features['price'] = df['price'].fillna(0)
            features['price_change'] = df.groupby('product_id')['price'].pct_change().fillna(0)
        
        if 'discount_percent' in df.columns:
            features['discount_percent'] = df['discount_percent'].fillna(0)
        
        # ============================================
        # 🌤️ WEATHER FEATURES (from dataset)
        # ============================================
        if 'temperature' in df.columns:
            features['temperature'] = df['temperature'].fillna(0)
            features['temp_rolling_7'] = (
                df.groupby('product_id')['temperature']
                .transform(lambda x: x.rolling(7, min_periods=1).mean())
            )
        
        if 'humidity' in df.columns:
            features['humidity'] = df['humidity'].fillna(0)
        
        if 'precipitation' in df.columns:
            features['precipitation'] = df['precipitation'].fillna(0)
            features['is_rainy'] = (df['precipitation'] > 1).astype(int)
            features['rain_rolling_7'] = (
                df.groupby('product_id')['precipitation']
                .transform(lambda x: x.rolling(7, min_periods=1).sum())
            )
        
        if 'wind_speed' in df.columns:
            features['wind_speed'] = df['wind_speed'].fillna(0)
        
        if 'weather_condition' in df.columns:
            features['is_sunny'] = (df['weather_condition'] == 'Sunny').astype(int)
            features['is_rainy_weather'] = (df['weather_condition'] == 'Rainy').astype(int)
        
        if 'pressure' in df.columns:
            features['pressure'] = df['pressure'].fillna(0)
        
        # ============================================
        # 🧹 CLEAN UP
        # ============================================
        features = features.bfill().ffill()
        features = features.fillna(0)
        
        return features
    
    # ============================================
    # 🎓 TRAIN
    # ============================================
    
    def train(self, df: pd.DataFrame) -> dict:
        """Train the XGBoost model on multi-product data"""
        logger.info(f"Training on {len(df):,} samples...")
        logger.info(f"📦 Products: {df['product_id'].nunique()}")
        
        # 🆕 Store product metadata
        for _, row in df.drop_duplicates('product_id').iterrows():
            self.product_categories[row['product_id']] = row.get('category', 'Unknown')
            self.product_prices[row['product_id']] = row.get('price', 0)
        
        # Create features
        features = self._create_features(df)
        target = df['sales'].values
        
        # Store feature columns
        self.feature_columns = features.columns.tolist()
        logger.info(f"📊 Features created: {len(self.feature_columns)}")
        
        # Prepare data
        X = features.values
        y = target
        
        # 🆕 Time-based split (last 20% of dates)
        df_sorted = df.sort_values('date').reset_index(drop=True)
        unique_dates = sorted(df['date'].unique())
        split_date = unique_dates[int(len(unique_dates) * 0.8)]
        
        train_mask = df['date'] < split_date
        test_mask = df['date'] >= split_date
        
        X_train, X_test = X[train_mask], X[test_mask]
        y_train, y_test = y[train_mask], y[test_mask]
        
        logger.info(f"📊 Train: {len(X_train):,} | Test: {len(X_test):,}")
        
        # Train XGBoost
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        y_pred = self.model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / np.clip(y_test, 1, None))) * 100
        
        self.training_metrics = {
            'r2': float(r2),
            'mae': float(mae),
            'rmse': float(rmse),
            'mape': float(mape),
            'n_features': len(self.feature_columns),
            'n_train': int(len(X_train)),
            'n_test': int(len(X_test)),
        }
        
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        logger.info(f"✅ Training complete!")
        logger.info(f"   R²: {r2:.3f}")
        logger.info(f"   MAE: {mae:.2f}")
        logger.info(f"   RMSE: {rmse:.2f}")
        logger.info(f"   MAPE: {mape:.2f}%")
        
        # 🆕 Feature importance
        importances = self.model.feature_importances_
        top_features = sorted(
            zip(self.feature_columns, importances),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        logger.info("📊 Top 10 features:")
        for name, imp in top_features:
            logger.info(f"   {name}: {imp:.4f}")
        
        return self.training_metrics
    
    # ============================================
    # 🔮 PREDICT
    # ============================================
    
    def predict(self, days_ahead: int, last_sales: pd.DataFrame, **kwargs) -> tuple:
        """Predict future sales using XGBoost"""
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() first")
        
        if not self.feature_columns:
            raise ValueError("Feature columns not set")
        
        predictions = []
        confidence_intervals = []
        
        current_data = last_sales.copy()
        current_data['date'] = pd.to_datetime(current_data['date'])
        current_data = current_data.sort_values('date').reset_index(drop=True)
        
        rmse = self.training_metrics.get('rmse', 15)
        
        # Get product context
        product_id = current_data['product_id'].iloc[-1]
        category = current_data['category'].iloc[-1] if 'category' in current_data.columns else 'Unknown'
        
        # 🆕 Use MEDIAN of last 30 days as placeholder (not 0!)
        placeholder_sale = float(current_data['sales'].tail(30).median())
        
        # 🆕 Get last-known weather
        last_weather = {
            'temperature': current_data['temperature'].iloc[-1] if 'temperature' in current_data.columns else 20,
            'humidity': current_data['humidity'].iloc[-1] if 'humidity' in current_data.columns else 60,
            'precipitation': current_data['precipitation'].iloc[-1] if 'precipitation' in current_data.columns else 0,
            'wind_speed': current_data['wind_speed'].iloc[-1] if 'wind_speed' in current_data.columns else 10,
            'pressure': current_data['pressure'].iloc[-1] if 'pressure' in current_data.columns else 1013,
            'weather_condition': current_data['weather_condition'].iloc[-1] if 'weather_condition' in current_data.columns else 'Sunny',
        }
        
        for i in range(days_ahead):
            future_date = current_data['date'].max() + pd.Timedelta(days=1)
            
            # 🆕 Use MEDIAN sale for placeholder
            new_row = pd.DataFrame({
                'date': [future_date],
                'store_id': [current_data['store_id'].iloc[-1] if 'store_id' in current_data.columns else 'ST001'],
                'product_id': [product_id],
                'category': [category],
                'sales': [placeholder_sale],  # ← Use median, not 0
                'price': [current_data['price'].iloc[-1] if 'price' in current_data.columns else 0],
                'promo_price': [current_data['promo_price'].iloc[-1] if 'promo_price' in current_data.columns else 0],
                'discount_percent': [0],
                'holiday_name': [None],
                'season_name': [current_data['season_name'].iloc[-1] if 'season_name' in current_data.columns else 'Winter'],
                'event_type': ['Normal'],
                'is_promo': [0],
                'temperature': [last_weather['temperature']],
                'humidity': [last_weather['humidity']],
                'precipitation': [last_weather['precipitation']],
                'wind_speed': [last_weather['wind_speed']],
                'weather_condition': [last_weather['weather_condition']],
                'pressure': [last_weather['pressure']],
            })
            
            temp_data = pd.concat([current_data, new_row], ignore_index=True)
            features = self._create_features(temp_data)
            
            if self.feature_columns:
                missing_cols = set(self.feature_columns) - set(features.columns)
                if missing_cols:
                    for col in missing_cols:
                        features[col] = 0
                features = features[self.feature_columns]
            
            last_features = features.iloc[-1:].values
            pred = float(self.model.predict(last_features)[0])
            pred = max(0, pred)
            predictions.append(pred)
            confidence_intervals.append((max(0, pred - rmse), pred + rmse))
            
            # Update the future row's sales with the prediction
            new_row['sales'] = pred
            current_data = pd.concat([current_data, new_row], ignore_index=True)
        
        return np.array(predictions), np.array(confidence_intervals), None
    
    # ============================================
    # 👑 DICTATOR
    # ============================================
    
    def enforce_floor_limit(self, predicted: float, floor_limit: int) -> tuple:
        if floor_limit > 0 and predicted < floor_limit:
            return float(floor_limit), f"⚠️ Enforced floor limit: {predicted:.0f} → {floor_limit}"
        return float(predicted), None
    
    # ============================================
    # 💾 SAVE / LOAD
    # ============================================
    
    def save_model(self, path: str = "model.pkl"):
        try:
            model_data = {
                'model': self.model,
                'scaler': self.scaler,
                'feature_columns': self.feature_columns,
                'training_metrics': self.training_metrics,
                'last_training_date': self.last_training_date,
                'is_trained': self.is_trained,
                'total_predictions': self.total_predictions,
                'product_categories': self.product_categories,
                'product_prices': self.product_prices,
                'version': '3.0',
            }
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            logger.info(f"💾 Model saved to {path}")
        except Exception as e:
            logger.error(f"❌ Failed to save model: {e}")
    
    def load_model(self, path: str = "model.pkl"):
        return self._load_model(path)
    
    def _load_model(self, path: str = "model.pkl"):
        if not os.path.exists(path):
            logger.info("⚠️ No existing model found")
            return False
        
        try:
            with open(path, 'rb') as f:
                data = pickle.load(f)
            
            version = data.get('version', '1.0')
            if version != '3.0':
                logger.warning(f"⚠️ Model version {version} vs current 3.0 — retrain recommended")
                return False
            
            self.model = data['model']
            self.scaler = data['scaler']
            self.feature_columns = data.get('feature_columns', [])
            self.training_metrics = data.get('training_metrics', {})
            self.last_training_date = data.get('last_training_date')
            self.is_trained = data.get('is_trained', False)
            self.total_predictions = data.get('total_predictions', 0)
            self.product_categories = data.get('product_categories', {})
            self.product_prices = data.get('product_prices', {})
            
            logger.info(f"✅ Model loaded from {path} (R²: {self.training_metrics.get('r2', 0):.3f})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    # ============================================
    # 🧪 SAMPLE DATA
    # ============================================
    
    def generate_sample_data(self) -> pd.DataFrame:
        """Fallback sample data generator"""
        dates = pd.date_range(start='2026-01-01', end='2026-12-31', freq='D')
        np.random.seed(42)
        
        sales = 100 + 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7) + np.random.normal(0, 15, len(dates))
        sales = np.maximum(sales, 10)
        
        return pd.DataFrame({
            'date': dates,
            'store_id': 'ST001',
            'product_id': 'sample_product',
            'category': 'Electronics',
            'sales': sales,
            'price': 299.99,
            'promo_price': 299.99,
            'discount_percent': 0,
            'holiday_name': None,
            'season_name': 'Winter',
            'event_type': 'Normal',
            'is_promo': 0,
            'temperature': 20,
            'humidity': 60,
            'precipitation': 0,
            'wind_speed': 10,
            'weather_condition': 'Sunny',
            'pressure': 1013,
        })


def get_predictator():
    """Dependency for FastAPI"""
    return PredictatorEngine()
