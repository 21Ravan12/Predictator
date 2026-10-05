"""Prediction service - handles all forecasting logic"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

from app.core.predictor import PredictatorEngine
from app.models import DatabaseManager

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for generating and managing predictions"""

    def __init__(self):
        self.predictator = PredictatorEngine()
        self.db = DatabaseManager()

    def get_predictions(
        self,
        product_id: str,
        days_ahead: int = 7,
        floor_limit: int = 0,
        current_stock: Optional[float] = None,
        include_contributions: bool = False,
    ) -> Dict:
        """Get predictions for a product"""

        # 🆕 Load ALL available history for this product
        history_df = self.db.load_sales_history(product_id, days_back=None)

        if history_df is None or len(history_df) < 30:
            return {
                'success': False,
                'error': f'Need at least 30 days of history. Only have {len(history_df) if history_df is not None else 0}',
                'product_id': product_id,
            }

        logger.info(f"🔮 Predicting {days_ahead} days for {product_id} (using {len(history_df)} history rows)")

        # Generate predictions
        predictions, confidence_intervals, contributions = self.predictator.predict(
            days_ahead=days_ahead,
            last_sales=history_df,
        )

        # 🆕 Apply floor limit inline (simpler than full DictatorEngine)
        final_predictions = []
        alerts = []
        floor_violations = 0

        for i, (pred, conf) in enumerate(zip(predictions, confidence_intervals)):
            final, alert = self.predictator.enforce_floor_limit(pred, floor_limit)
            final_predictions.append(final)
            if alert:
                alerts.append({'day': i + 1, 'message': alert})
                floor_violations += 1

        # Format response
        future_dates = [
            (datetime.now() + timedelta(days=i + 1)).strftime("%Y-%m-%d")
            for i in range(days_ahead)
        ]

        predictions_list = []
        for i, (date, pred, conf, orig) in enumerate(
            zip(future_dates, final_predictions, confidence_intervals, predictions)
        ):
            predictions_list.append({
                'date': date,
                'predicted_sales': round(float(pred), 2),
                'confidence_lower': round(float(conf[0]), 2),
                'confidence_upper': round(float(conf[1]), 2),
                'original_prediction': round(float(orig), 2) if orig != pred else None,
            })

        # Log predictions
        try:
            self.db.log_prediction(product_id, predictions_list, floor_limit)
        except Exception as e:
            logger.warning(f"⚠️ Failed to log predictions: {e}")

        return {
            'success': True,
            'product_id': product_id,
            'predictions': predictions_list,
            'summary': {
                'total_predicted': round(sum(p['predicted_sales'] for p in predictions_list), 2),
                'average_daily': round(sum(p['predicted_sales'] for p in predictions_list) / len(predictions_list), 2),
                'peak_day': round(max(p['predicted_sales'] for p in predictions_list), 2),
                'floor_violations': floor_violations,
            },
            'dictator_actions': alerts,
            'dictator_active': floor_limit > 0,
        }

    def get_bulk_predictions(
        self,
        product_ids: List[str],
        days_ahead: int = 7,
        floor_limit: int = 0,
    ) -> Dict:
        """Get predictions for multiple products"""
        results = {}
        for product_id in product_ids:
            result = self.get_predictions(product_id, days_ahead, floor_limit)
            results[product_id] = result

        return {
            'success': True,
            'products': results,
            'total_products': len(results),
            'total_units': sum(
                r.get('summary', {}).get('total_predicted', 0)
                for r in results.values()
                if r.get('success')
            ),
        }

    def get_prediction_history(self, product_id: str, days_back: int = 180) -> Dict:
        """Get historical prediction accuracy"""
        predictions = self.db.get_prediction_history(product_id, days_back)
        if not predictions:
            return {'success': False, 'message': 'No prediction history found'}

        actuals = self.db.load_sales_history(product_id, days_back=days_back)

        accuracy_metrics = []
        for pred in predictions:
            actual = actuals[actuals['date'] == pred['date']]
            if not actual.empty:
                error = abs(pred['predicted_sales'] - actual.iloc[0]['sales'])
                accuracy_metrics.append({
                    'date': pred['date'],
                    'predicted': pred['predicted_sales'],
                    'actual': actual.iloc[0]['sales'],
                    'error': error,
                    'accuracy_pct': max(0, (1 - error / actual.iloc[0]['sales']) * 100),
                })

        return {
            'success': True,
            'product_id': product_id,
            'predictions': accuracy_metrics,
            'average_accuracy': (
                float(np.mean([m['accuracy_pct'] for m in accuracy_metrics]))
                if accuracy_metrics else 0
            ),
        }
    