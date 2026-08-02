"""Alert service - manages notifications and alerts"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

from app.models import DatabaseManager

logger = logging.getLogger(__name__)


class AlertService:
    """Service for generating and managing alerts"""
    
    ALERT_LEVELS = {
        'critical': 3,
        'warning': 2,
        'info': 1
    }
    
    def __init__(self):
        self.db = DatabaseManager()
        self.alerts = []
    
    def generate_alert(
        self,
        product_id: str,
        level: str,
        title: str,
        message: str,
        data: Optional[Dict] = None
    ) -> Dict:
        """Generate a new alert"""
        
        if level not in self.ALERT_LEVELS:
            level = 'info'
        
        alert = {
            'id': len(self.alerts) + 1,
            'timestamp': datetime.now().isoformat(),
            'product_id': product_id,
            'level': level,
            'priority': self.ALERT_LEVELS[level],
            'title': title,
            'message': message,
            'data': data or {},
            'read': False,
            'resolved': False
        }
        
        self.alerts.append(alert)
        
        # Log to database
        self._save_alert(alert)
        
        return alert
    
    def _save_alert(self, alert: Dict):
        """Save alert to database"""
        try:
            # Would save to alerts table
            logger.info(f"Alert saved: {alert['level']} - {alert['title']}")
        except Exception as e:
            logger.error(f"Failed to save alert: {e}")
    
    def get_alerts(
        self,
        product_id: Optional[str] = None,
        level: Optional[str] = None,
        unread_only: bool = False,
        limit: int = 50
    ) -> Dict:
        """Get alerts with filters"""
        
        filtered = self.alerts.copy()
        
        if product_id:
            filtered = [a for a in filtered if a['product_id'] == product_id]
        
        if level:
            filtered = [a for a in filtered if a['level'] == level]
        
        if unread_only:
            filtered = [a for a in filtered if not a['read']]
        
        # Sort by priority and timestamp
        filtered.sort(key=lambda x: (-x['priority'], x['timestamp']), reverse=True)
        
        return {
            'success': True,
            'total': len(filtered),
            'alerts': filtered[:limit]
        }
    
    def mark_as_read(self, alert_id: int) -> Dict:
        """Mark an alert as read"""
        
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['read'] = True
                return {'success': True, 'message': 'Alert marked as read'}
        
        return {'success': False, 'error': 'Alert not found'}
    
    def mark_as_resolved(self, alert_id: int) -> Dict:
        """Mark an alert as resolved"""
        
        for alert in self.alerts:
            if alert['id'] == alert_id:
                alert['resolved'] = True
                alert['read'] = True
                return {'success': True, 'message': 'Alert marked as resolved'}
        
        return {'success': False, 'error': 'Alert not found'}
    
    def check_stock_alerts(
        self,
        product_id: str,
        predicted_sales: float,
        current_stock: float,
        floor_limit: int
    ) -> List[Dict]:
        """Check and generate stock-related alerts"""
        
        alerts = []
        
        # Stockout alert
        if predicted_sales > current_stock:
            shortage = predicted_sales - current_stock
            alerts.append(
                self.generate_alert(
                    product_id=product_id,
                    level='critical',
                    title='Stockout Risk',
                    message=f'Predicted sales ({predicted_sales:.0f}) exceed current stock ({current_stock:.0f}). Shortage: {shortage:.0f} units',
                    data={'shortage': shortage, 'predicted': predicted_sales, 'current': current_stock}
                )
            )
        
        # Floor limit alert
        elif predicted_sales < floor_limit:
            deficit = floor_limit - predicted_sales
            alerts.append(
                self.generate_alert(
                    product_id=product_id,
                    level='warning',
                    title='Below Floor Limit',
                    message=f'Predicted sales ({predicted_sales:.0f}) below floor limit ({floor_limit}). Need +{deficit:.0f} units',
                    data={'deficit': deficit, 'predicted': predicted_sales, 'floor': floor_limit}
                )
            )
        
        # Overstock alert
        elif current_stock > predicted_sales * 2:
            excess = current_stock - predicted_sales
            alerts.append(
                self.generate_alert(
                    product_id=product_id,
                    level='info',
                    title='Overstock Detected',
                    message=f'Current stock ({current_stock:.0f}) is double predicted sales ({predicted_sales:.0f}). Excess: {excess:.0f} units',
                    data={'excess': excess, 'predicted': predicted_sales, 'current': current_stock}
                )
            )
        
        return alerts
    
    def cleanup_old_alerts(self, days_back: int = 30):
        """Remove old resolved alerts"""
        
        cutoff = datetime.now() - timedelta(days=days_back)
        original_count = len(self.alerts)
        
        self.alerts = [
            a for a in self.alerts
            if not (a['resolved'] and datetime.fromisoformat(a['timestamp']) < cutoff)
        ]
        
        return {
            'success': True,
            'removed': original_count - len(self.alerts),
            'remaining': len(self.alerts)
        }