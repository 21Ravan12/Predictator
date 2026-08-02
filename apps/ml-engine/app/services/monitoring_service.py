"""Monitoring service - tracks metrics and performance"""

import time
try:
    import psutil
except ImportError:
    psutil = None
import platform
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from collections import deque

logger = logging.getLogger(__name__)


class MonitoringService:
    """Service for monitoring system performance"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.prediction_times = deque(maxlen=max_history)
        self.training_times = deque(maxlen=max_history)
        self.errors = deque(maxlen=max_history)
        self.requests = deque(maxlen=max_history)
        self.start_time = datetime.now()
    
    def record_prediction_time(self, duration_ms: float):
        """Record prediction latency"""
        self.prediction_times.append({
            'timestamp': datetime.now(),
            'duration_ms': duration_ms
        })
    
    def record_training_time(self, duration_ms: float, samples: int):
        """Record training time"""
        self.training_times.append({
            'timestamp': datetime.now(),
            'duration_ms': duration_ms,
            'samples': samples
        })
    
    def record_error(self, error_type: str, message: str):
        """Record an error"""
        self.errors.append({
            'timestamp': datetime.now(),
            'type': error_type,
            'message': message
        })
    
    def record_request(self, endpoint: str, method: str, status_code: int):
        """Record an API request"""
        self.requests.append({
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code
        })
    
    def get_system_metrics(self) -> Dict:
        """Get system health metrics"""
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Uptime
        uptime = datetime.now() - self.start_time
        
        return {
            'success': True,
            'system': {
                'platform': platform.platform(),
                'python_version': platform.python_version(),
                'uptime_seconds': uptime.total_seconds(),
                'uptime_human': str(uptime).split('.')[0]
            },
            'resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': memory.used / (1024**3),
                'memory_total_gb': memory.total / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3)
            }
        }
    
    def get_performance_metrics(self) -> Dict:
        """Get model performance metrics"""
        
        # Prediction latency
        recent_preds = list(self.prediction_times)[-100:]
        if recent_preds:
            avg_pred_time = sum(p['duration_ms'] for p in recent_preds) / len(recent_preds)
            max_pred_time = max(p['duration_ms'] for p in recent_preds)
        else:
            avg_pred_time = 0
            max_pred_time = 0
        
        # Error rate
        recent_errors = list(self.errors)[-1000:]
        recent_requests = list(self.requests)[-1000:]
        error_rate = len(recent_errors) / len(recent_requests) if recent_requests else 0
        
        # Request rate
        last_hour = datetime.now() - timedelta(hours=1)
        hourly_requests = len([r for r in self.requests if r['timestamp'] > last_hour])
        
        return {
            'success': True,
            'prediction': {
                'avg_latency_ms': round(avg_pred_time, 2),
                'max_latency_ms': round(max_pred_time, 2),
                'total_predictions': len(self.prediction_times)
            },
            'reliability': {
                'error_rate': round(error_rate * 100, 2),
                'total_errors': len(self.errors),
                'total_requests': len(self.requests)
            },
            'throughput': {
                'requests_per_hour': hourly_requests,
                'requests_per_minute': round(hourly_requests / 60, 1)
            }
        }
    
    def get_model_metrics(self, predictator) -> Dict:
        """Get model-specific metrics"""
        
        if not predictator.is_trained:
            return {
                'success': False,
                'message': 'Model not trained yet'
            }
        
        return {
            'success': True,
            'model': {
                'is_trained': predictator.is_trained,
                'last_training': predictator.last_training_date.isoformat() if predictator.last_training_date else None,
                'metrics': predictator.training_metrics,
                'total_predictions': predictator.total_predictions
            }
        }
    
    def get_dashboard_data(self, predictator) -> Dict:
        """Get all metrics for dashboard"""
        
        return {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'system': self.get_system_metrics(),
            'performance': self.get_performance_metrics(),
            'model': self.get_model_metrics(predictator),
            'health_score': self._calculate_health_score()
        }
    
    def _calculate_health_score(self) -> int:
        """Calculate overall health score (0-100)"""
        
        score = 100
        
        # CPU penalty
        cpu = psutil.cpu_percent()
        if cpu > 80:
            score -= 20
        elif cpu > 60:
            score -= 10
        
        # Memory penalty
        memory = psutil.virtual_memory().percent
        if memory > 90:
            score -= 30
        elif memory > 75:
            score -= 15
        
        # Error rate penalty
        recent_errors = list(self.errors)[-100:]
        recent_requests = list(self.requests)[-100:]
        if recent_requests:
            error_rate = len(recent_errors) / len(recent_requests)
            score -= min(30, error_rate * 100)
        
        return max(0, score)
    
    def clear_metrics(self) -> Dict:
        """Clear all metrics (for testing)"""
        
        self.prediction_times.clear()
        self.training_times.clear()
        self.errors.clear()
        self.requests.clear()
        
        return {
            'success': True,
            'message': 'All metrics cleared'
        }