"""Core Predictator engine - simplified but powerful"""

import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
import logging

logger = logging.getLogger(__name__)


class PredictatorEngine:
    """Main prediction engine"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        self.last_training_date = None
        self.training_metrics = {}
        self.total_predictions = 0
    
    def _create_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create time-series features"""
        features = pd.DataFrame()
        
        # Time features
        features['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek
        features['month'] = pd.to_datetime(df['date']).dt.month
        features['is_weekend'] = (features['day_of_week'] >= 5).astype(int)
        
        # Lag features
        features['lag_1'] = df['sales'].shift(1)
        features['lag_2'] = df['sales'].shift(2)
        features['lag_3'] = df['sales'].shift(3)
        features['lag_7'] = df['sales'].shift(7)
        
        # Rolling averages
        features['rolling_mean_3'] = df['sales'].rolling(3).mean()
        features['rolling_mean_7'] = df['sales'].rolling(7).mean()
        
        # Holiday
        features['is_holiday'] = df.get('is_holiday', pd.Series([0]*len(df))).fillna(0).astype(int)
        
        # Clean NaN
        features = features.bfill().ffill().fillna(0)
        
        return features
    
    def train(self, df: pd.DataFrame) -> dict:
        """Train the model"""
        logger.info(f"Training on {len(df)} samples...")
        
        # Create features
        features = self._create_features(df)
        target = df['sales'].values
        
        # Prepare data
        X = features.values
        y = target
        
        # Split for validation
        split = int(len(X) * 0.8)
        X_train, X_test = X[:split], X[split:]
        y_train, y_test = y[:split], y[split:]
        
        # Scale
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
        y_pred = self.model.predict(X_test_scaled)
        
        self.training_metrics = {
            'r2': r2_score(y_test, y_pred),
            'mae': mean_absolute_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
        }
        
        self.is_trained = True
        self.last_training_date = datetime.now()
        
        logger.info(f"✅ Training complete! R²: {self.training_metrics['r2']:.3f}")
        return self.training_metrics
    
    def predict(self, days_ahead: int, last_sales: pd.DataFrame, **kwargs) -> tuple:
        """Predict future sales"""
        if not self.is_trained:
            raise ValueError("Model not trained")
        
        predictions = []
        confidence_intervals = []
        
        current_data = last_sales.copy()
        
        for i in range(days_ahead):
            # Create features for next day
            future_date = pd.date_range(start=current_data['date'].max(), periods=2, freq='D')[1]
            new_row = pd.DataFrame({'date': [future_date], 'sales': [0]})
            temp_data = pd.concat([current_data, new_row], ignore_index=True)
            
            features = self._create_features(temp_data)
            last_features = features.iloc[-1:].values
            last_features_scaled = self.scaler.transform(last_features)
            
            pred = self.model.predict(last_features_scaled)[0]
            predictions.append(max(0, pred))
            
            # Simple confidence interval
            std = self.training_metrics.get('rmse', pred * 0.15)
            confidence_intervals.append((pred - std, pred + std))
            
            # Update for next iteration
            new_sale = pd.DataFrame({'date': [future_date], 'sales': [pred]})
            current_data = pd.concat([current_data, new_sale], ignore_index=True)
        
        return np.array(predictions), np.array(confidence_intervals), None
    
    def enforce_floor_limit(self, predicted: float, floor_limit: int) -> tuple:
        """Dictator rule - enforce minimum stock"""
        if floor_limit > 0 and predicted < floor_limit:
            return float(floor_limit), f"⚠️ Enforced floor limit: {predicted:.0f} → {floor_limit}"
        return predicted, None
    
    def save_model(self, path: str = "model.pkl"):
        """Save model to disk"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'metrics': self.training_metrics,
                'last_training': self.last_training_date
            }, f)
        logger.info(f"💾 Model saved to {path}")
    
    def load_model(self, path: str = "model.pkl") -> bool:
        """Load model from disk"""
        if os.path.exists(path):
            with open(path, 'rb') as f:
                data = pickle.load(f)
                self.model = data['model']
                self.scaler = data['scaler']
                self.training_metrics = data['metrics']
                self.last_training_date = data['last_training']
                self.is_trained = True
            logger.info(f"✅ Model loaded from {path}")
            return True
        return False
    
    def generate_sample_data(self) -> pd.DataFrame:
        """Generate sample data for testing"""
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        np.random.seed(42)
        
        # Realistic pattern
        trend = 100 + np.arange(len(dates)) * 0.1
        weekly = 30 * np.sin(np.arange(len(dates)) * 2 * np.pi / 7)
        monthly = 20 * np.sin(np.arange(len(dates)) * 2 * np.pi / 30.4)
        noise = np.random.normal(0, 15, len(dates))
        
        sales = trend + weekly + monthly + noise
        sales = np.maximum(sales, 10)
        
        return pd.DataFrame({
            'date': dates,
            'sales': sales,
            'is_holiday': (dates.dayofweek >= 5)
        })