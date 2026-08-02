"""Training service - handles model training and retraining"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime
import logging

from app.core.predictor import PredictatorEngine
from app.models import DatabaseManager
from app.core.features import FeatureEngineer
from app.core.ensemble import EnsembleModel

logger = logging.getLogger(__name__)


class TrainingService:
    """Service for model training and management"""
    
    def __init__(self):
        self.predictator = PredictatorEngine()
        self.db = DatabaseManager()
        self.feature_engineer = FeatureEngineer()
        self.ensemble = EnsembleModel()
    
    def train_model(
        self,
        csv_path: Optional[str] = None,
        force_retrain: bool = False,
        use_ensemble: bool = True
    ) -> Dict:
        """Train the prediction model"""
        
        if self.predictator.is_trained and not force_retrain:
            return {
                'success': True,
                'message': 'Model already trained. Use force_retrain=True to retrain',
                'metrics': self.predictator.training_metrics
            }
        
        try:
            # Load training data
            if csv_path:
                df = pd.read_csv(csv_path)
                logger.info(f"Loaded {len(df)} rows from {csv_path}")
            else:
                df = self.predictator.generate_sample_data()
                logger.info(f"Generated {len(df)} sample rows")
            
            # Validate and clean data
            df = self._validate_data(df)
            
            # Train model
            if use_ensemble:
                metrics = self._train_ensemble(df)
            else:
                metrics = self.predictator.train(df)
            
            # Save model
            self.predictator.save_model()
            
            # Log training
            self._log_training(metrics, len(df))
            
            return {
                'success': True,
                'message': 'Model trained successfully!',
                'samples_used': len(df),
                'model_type': 'ensemble' if use_ensemble else 'random_forest',
                'metrics': metrics,
                'training_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate and clean training data"""
        
        # Required columns
        required = ['date', 'sales']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Clean sales column
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
        df['sales'] = df['sales'].fillna(df['sales'].median())
        df['sales'] = df['sales'].fillna(100)
        df['sales'] = df['sales'].clip(lower=0)
        
        # Clean dates
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Add is_holiday if missing
        if 'is_holiday' not in df.columns:
            df['is_holiday'] = False
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['date'])
        
        return df
    
    def _train_ensemble(self, df: pd.DataFrame) -> Dict:
        """Train ensemble model"""
        
        # Create features
        features_df = self.feature_engineer.create_features(df)
        
        # Prepare data
        feature_cols = [c for c in features_df.columns if c != 'sales']
        X = features_df[feature_cols].values
        y = features_df['sales'].values
        
        # Split data
        split_idx = int(len(X) * 0.8)
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Train ensemble
        self.ensemble.train(X_train, y_train, X_val, y_val)
        
        # Evaluate
        y_pred = self.ensemble.predict(X_val)
        
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        import numpy as np
        
        metrics = {
            'mae': mean_absolute_error(y_val, y_pred),
            'mse': mean_squared_error(y_val, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_val, y_pred)),
            'r2': r2_score(y_val, y_pred),
            'ensemble_weights': self.ensemble.weights
        }
        
        # Store in predictor for compatibility
        self.predictator.training_metrics = metrics
        self.predictator.is_trained = True
        self.predictator.last_training_date = datetime.now()
        
        return metrics
    
    def _log_training(self, metrics: Dict, samples: int):
        """Log training event to database"""
        
        try:
            # Could store in a separate training_logs table
            logger.info(f"Training completed: R²={metrics.get('r2', 0):.3f}, Samples={samples}")
        except Exception as e:
            logger.warning(f"Failed to log training: {e}")
    
    def retrain_scheduled(self) -> Dict:
        """Scheduled retraining (for cron jobs)"""
        
        logger.info("🔄 Running scheduled retraining...")
        
        # Load latest data from database
        products = self.db.get_all_products()
        all_data = []
        
        for product in products:
            df = self.db.load_sales_history(product, days_back=180)
            if not df.empty:
                df['product_id'] = product
                all_data.append(df)
        
        if not all_data:
            return {'success': False, 'message': 'No data available for retraining'}
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        return self.train_model(force_retrain=True)
    
    def get_training_history(self, limit: int = 10) -> Dict:
        """Get training history"""
        
        # This would query a training_logs table
        # For now, return current metrics
        return {
            'success': True,
            'current_model': {
                'is_trained': self.predictator.is_trained,
                'last_training': self.predictator.last_training_date,
                'metrics': self.predictator.training_metrics
            },
            'history': []  # Would contain previous training runs
        }