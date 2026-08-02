import numpy as np
from typing import Dict, List, Any
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
try:
    import xgboost as xgb
    XGB_AVAILABLE = True
except ImportError:
    xgb = None
    XGB_AVAILABLE = False
import joblib

class EnsembleModel:
    """Ensemble of multiple models for better predictions"""
    
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=200, max_depth=15, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=150, learning_rate=0.1, random_state=42),
            'linear': LinearRegression()
        }
        if XGB_AVAILABLE:
            self.models['xgboost'] = xgb.XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)
        self.weights = {'random_forest': 0.4, 'gradient_boosting': 0.3, 'xgboost': 0.2, 'linear': 0.1}
        self.feature_importance = {}
        
    def train(self, X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray = None, y_val: np.ndarray = None):
        """Train all models"""
        print(f"🤖 Training ensemble with {len(self.models)} models...")
        
        for name, model in self.models.items():
            print(f"   Training {name}...")
            model.fit(X_train, y_train)
            
            # Update weights if validation data is provided
            if X_val is not None:
                val_pred = model.predict(X_val)
                mse = np.mean((y_val - val_pred) ** 2)
                self.weights[name] = 1 / (mse + 1e-6)
            
            # Store feature importance if available
            if hasattr(model, 'feature_importances_'):
                self.feature_importance[name] = model.feature_importances_
        
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
        
        print(f"✅ Ensemble trained with weights: {self.weights}")
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict with weighted ensemble"""
        predictions = []
        
        for name, model in self.models.items():
            pred = model.predict(X)
            predictions.append(pred * self.weights[name])
        
        return np.sum(predictions, axis=0)
    
    def predict_with_confidence(self, X: np.ndarray, n_iterations: int = 10) -> Dict:
        """Predict with confidence intervals"""
        all_predictions = []
        
        for _ in range(n_iterations):
            # Bootstrap the ensemble
            bootstrapped = self._bootstrap_predict(X)
            all_predictions.append(bootstrapped)
        
        all_predictions = np.array(all_predictions)
        
        return {
            'mean': np.mean(all_predictions, axis=0),
            'std': np.std(all_predictions, axis=0),
            'lower_95': np.percentile(all_predictions, 2.5, axis=0),
            'upper_95': np.percentile(all_predictions, 97.5, axis=0),
            'lower_80': np.percentile(all_predictions, 10, axis=0),
            'upper_80': np.percentile(all_predictions, 90, axis=0)
        }
    
    def _bootstrap_predict(self, X: np.ndarray) -> np.ndarray:
        """Single bootstrap prediction"""
        predictions = []
        for name, model in self.models.items():
            # Add random noise to weights
            weight_noise = np.random.normal(1, 0.1)
            pred = model.predict(X) * self.weights[name] * weight_noise
            predictions.append(pred)
        return np.sum(predictions, axis=0)
    
    def save(self, path: str):
        """Save ensemble model"""
        joblib.dump({'models': self.models, 'weights': self.weights}, path)
    
    def load(self, path: str):
        """Load ensemble model"""
        data = joblib.load(path)
        self.models = data['models']
        self.weights = data['weights']