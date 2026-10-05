"""Training service - handles model training and retraining"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path
import logging

from app.core.predictor import PredictatorEngine
from app.models import DatabaseManager

logger = logging.getLogger(__name__)


class TrainingService:
    """Service for model training and management"""

    # 🆕 Default dataset path
    DEFAULT_DATASET = "data/raw/sales_data_large.csv"

    def __init__(self):
        self.predictator = PredictatorEngine()
        self.db = DatabaseManager()

    def train_model(
        self,
        csv_path: Optional[str] = None,
        force_retrain: bool = False,
    ) -> Dict:
        """Train the prediction model"""

        if self.predictator.is_trained and not force_retrain:
            return {
                'success': True,
                'message': 'Model already trained. Use force_retrain=True to retrain',
                'metrics': self.predictator.training_metrics,
            }

        try:
            # 🆕 Load data with priority order
            df = self._load_training_data(csv_path)
            logger.info(f"📊 Loaded {len(df):,} rows")

            # Validate
            df = self._validate_data(df)
            logger.info(f"✅ Validated: {len(df):,} rows, {df['product_id'].nunique()} products")

            # Train
            metrics = self.predictator.train(df)

            # Save model
            self.predictator.save_model()

            # Log training
            self._log_training(metrics, len(df))

            return {
                'success': True,
                'message': 'Model trained successfully!',
                'samples_used': len(df),
                'model_type': 'xgboost',
                'metrics': metrics,
                'training_time': datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ Training error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
            }

    def _load_training_data(self, csv_path: Optional[str] = None) -> pd.DataFrame:
        """🆕 Load training data with priority order"""

        # 1. Explicit path
        if csv_path and Path(csv_path).exists():
            logger.info(f"📥 Loading from explicit path: {csv_path}")
            return pd.read_csv(csv_path, parse_dates=['date'])

        # 2. New large dataset
        if Path(self.DEFAULT_DATASET).exists():
            logger.info(f"📥 Loading large dataset: {self.DEFAULT_DATASET}")
            return pd.read_csv(self.DEFAULT_DATASET, parse_dates=['date'])

        # 3. Legacy dataset
        legacy = Path("data/legacy/historical-sales.csv")
        if legacy.exists():
            logger.info(f"📥 Loading legacy dataset: {legacy}")
            return pd.read_csv(legacy, parse_dates=['date'])

        # 4. Fallback
        logger.warning("⚠️ No dataset found, using sample data")
        return self.predictator.generate_sample_data()

    def _validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """🆕 Validate and clean training data (multi-product safe)"""

        # Required columns
        required = ['date', 'sales']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # 🆕 If product_id missing, assume single product
        if 'product_id' not in df.columns:
            logger.warning("⚠️ No product_id column — assuming single product")
            df['product_id'] = 'default_product'

        # Clean sales
        df['sales'] = pd.to_numeric(df['sales'], errors='coerce')
        df['sales'] = df['sales'].fillna(df.groupby('product_id')['sales'].transform('median'))
        df['sales'] = df['sales'].fillna(0).clip(lower=0)

        # Clean dates
        df['date'] = pd.to_datetime(df['date'])

        # 🆕 Sort by product + date (not just date!)
        df = df.sort_values(['product_id', 'date']).reset_index(drop=True)

        # 🆕 Remove duplicates by (product_id, date) — NOT just date!
        before = len(df)
        df = df.drop_duplicates(subset=['product_id', 'date'], keep='first')
        if len(df) < before:
            logger.warning(f"⚠️ Removed {before - len(df)} duplicate (product, date) rows")

        # 🆕 Ensure minimal columns exist
        if 'is_holiday' not in df.columns and 'holiday_name' in df.columns:
            df['is_holiday'] = (
                df['holiday_name'].notna() & (df['holiday_name'] != 'None')
            ).astype(int)

        if 'is_promo' not in df.columns and 'event_type' in df.columns:
            df['is_promo'] = (df['event_type'] == 'Promotion').astype(int)

        return df

    def _log_training(self, metrics: Dict, samples: int):
        """Log training event to database"""
        try:
            self.db.save_training_log(
                samples=samples,
                model_type='xgboost',
                metrics=metrics,
            )
            logger.info(
                f"📝 Training logged: R²={metrics.get('r2', 0):.3f}, "
                f"MAE={metrics.get('mae', 0):.2f}, "
                f"Samples={samples:,}"
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to log training: {e}")

    def retrain_scheduled(self) -> Dict:
        """🆕 Scheduled retraining (for cron jobs)"""
        logger.info("🔄 Running scheduled retraining...")

        # Load latest data from the CSV (single source of truth for now)
        try:
            return self.train_model(force_retrain=True)
        except Exception as e:
            logger.error(f"❌ Scheduled retraining failed: {e}")
            return {'success': False, 'message': str(e)}

    def get_training_history(self, limit: int = 10) -> Dict:
        """Get training history"""
        return {
            'success': True,
            'current_model': {
                'is_trained': self.predictator.is_trained,
                'last_training': self.predictator.last_training_date,
                'metrics': self.predictator.training_metrics,
            },
            'history': [],
        }
    