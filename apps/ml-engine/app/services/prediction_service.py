"""Prediction service - handles all forecasting logic"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

from app.core.predictor import PredictatorEngine
from app.core.dictator import DictatorEngine
from app.models import DatabaseManager

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for generating and managing predictions"""
    
    def __init__(self):
        self.predictator = PredictatorEngine()
        self.dictator = DictatorEngine()
        self.db = DatabaseManager()
    
    def get_predictions(
        self,
        product_id: str,
        days_ahead: int = 7,
        floor_limit: int = 0,
        current_stock: Optional[float] = None,
        include_contributions: bool = False
    ) -> Dict:
        """Get predictions for a product with dictator enforcement"""
        
        # Load historical data
        history_df = self.db.load_sales_history(product_id, days_back=90)
        
        if len(history_df) < 30:
            return {
                'success': False,
                'error': f'Need at least 30 days of history. Only have {len(history_df)}',
                'product_id': product_id
            }
        
        # Generate base predictions
        predictions, confidence_intervals, contributions = self.predictator.predict(
            days_ahead=days_ahead,
            last_sales=history_df,
            include_contributions=include_contributions
        )
        
        # Apply dictator rules
        context = {
            'floor_limit': floor_limit,
            'current_stock': current_stock or history_df['sales'].tail(7).mean(),
            'safety_stock': floor_limit or 100,
            'is_ramadan': self._is_ramadan_season()
        }
        
        dictator_result = self.dictator.enforce_rules(predictions, context)
        
        # Format response
        future_dates = [
            (datetime.now() + timedelta(days=i+1)).strftime("%Y-%m-%d")
            for i in range(days_ahead)
        ]
        
        predictions_list = []
        for i, (date, pred, conf) in enumerate(zip(future_dates, dictator_result['modified'], confidence_intervals)):
            predictions_list.append({
                'date': date,
                'predicted_sales': round(pred, 2),
                'confidence_lower': round(conf[0], 2),
                'confidence_upper': round(conf[1], 2),
                'original_prediction': round(dictator_result['original'][i], 2) if dictator_result['modified'][i] != dictator_result['original'][i] else None
            })
        
        # Log predictions
        self.db.log_prediction(product_id, predictions_list, floor_limit)
        
        return {
            'success': True,
            'product_id': product_id,
            'predictions': predictions_list,
            'summary': {
                'total_predicted': sum(p['predicted_sales'] for p in predictions_list),
                'average_daily': sum(p['predicted_sales'] for p in predictions_list) / len(predictions_list),
                'peak_day': max(p['predicted_sales'] for p in predictions_list),
                'floor_violations': len([a for a in dictator_result['actions'] if 'floor' in a['rule']])
            },
            'dictator_actions': dictator_result['actions'],
            'dictator_active': dictator_result['dictator_mode']
        }
    
    def get_bulk_predictions(
        self,
        product_ids: List[str],
        days_ahead: int = 7,
        floor_limit: int = 0
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
            'total_units': sum(r.get('summary', {}).get('total_predicted', 0) for r in results.values())
        }
    
    def _is_ramadan_season(self) -> bool:
        """Check if current date is near Ramadan"""
        # Simplified - can be replaced with actual calendar API
        current_month = datetime.now().month
        return current_month in [3, 4]  # March-April approximation
    
    def get_prediction_history(self, product_id: str, days_back: int = 30) -> Dict:
        """Get historical prediction accuracy"""
        
        # Load past predictions from database
        predictions = self.db.get_prediction_history(product_id, days_back)
        
        if not predictions:
            return {'success': False, 'message': 'No prediction history found'}
        
        # Calculate accuracy
        actuals = self.db.load_sales_history(product_id, days_back)
        
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
                    'accuracy_pct': max(0, (1 - error / actual.iloc[0]['sales']) * 100)
                })
        
        return {
            'success': True,
            'product_id': product_id,
            'predictions': accuracy_metrics,
            'average_accuracy': np.mean([m['accuracy_pct'] for m in accuracy_metrics]) if accuracy_metrics else 0
        }