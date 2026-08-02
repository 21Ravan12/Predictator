"""Metrics collection and tracking"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from collections import deque
import statistics


class MetricsCollector:
    """Collect and track performance metrics"""
    
    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.metrics = {
            'prediction_latency': deque(maxlen=max_history),
            'training_latency': deque(maxlen=max_history),
            'errors': deque(maxlen=max_history),
            'requests': deque(maxlen=max_history),
            'cache_hits': deque(maxlen=max_history),
            'cache_misses': deque(maxlen=max_history)
        }
        self.start_time = datetime.now()
    
    def record_latency(self, metric_type: str, duration_ms: float):
        """Record operation latency"""
        key = f"{metric_type}_latency"
        if key in self.metrics:
            self.metrics[key].append({
                'timestamp': datetime.now(),
                'value': duration_ms
            })
    
    def record_error(self, error_type: str, message: str):
        """Record error occurrence"""
        self.metrics['errors'].append({
            'timestamp': datetime.now(),
            'type': error_type,
            'message': message
        })
    
    def record_request(self, endpoint: str, method: str, status_code: int):
        """Record API request"""
        self.metrics['requests'].append({
            'timestamp': datetime.now(),
            'endpoint': endpoint,
            'method': method,
            'status_code': status_code
        })
    
    def record_cache_hit(self):
        """Record cache hit"""
        self.metrics['cache_hits'].append({'timestamp': datetime.now()})
    
    def record_cache_miss(self):
        """Record cache miss"""
        self.metrics['cache_misses'].append({'timestamp': datetime.now()})
    
    def get_average_latency(self, metric_type: str, minutes: int = 60) -> float:
        """Get average latency for last N minutes"""
        key = f"{metric_type}_latency"
        if key not in self.metrics:
            return 0.0
        
        cutoff = datetime.now() - timedelta(minutes=minutes)
        recent = [
            m['value'] for m in self.metrics[key]
            if m['timestamp'] > cutoff
        ]
        
        return statistics.mean(recent) if recent else 0.0
    
    def get_error_rate(self, minutes: int = 60) -> float:
        """Get error rate as percentage"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        recent_errors = [e for e in self.metrics['errors'] if e['timestamp'] > cutoff]
        recent_requests = [r for r in self.metrics['requests'] if r['timestamp'] > cutoff]
        
        if not recent_requests:
            return 0.0
        
        return len(recent_errors) / len(recent_requests) * 100
    
    def get_cache_hit_rate(self, minutes: int = 60) -> float:
        """Get cache hit rate percentage"""
        cutoff = datetime.now() - timedelta(minutes=minutes)
        
        hits = len([h for h in self.metrics['cache_hits'] if h['timestamp'] > cutoff])
        misses = len([m for m in self.metrics['cache_misses'] if m['timestamp'] > cutoff])
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0.0
    
    def get_uptime_seconds(self) -> float:
        """Get system uptime in seconds"""
        return (datetime.now() - self.start_time).total_seconds()
    
    def get_summary(self) -> Dict:
        """Get metrics summary"""
        return {
            'uptime_hours': round(self.get_uptime_seconds() / 3600, 2),
            'prediction_latency_avg_ms': round(self.get_average_latency('prediction'), 2),
            'training_latency_avg_ms': round(self.get_average_latency('training'), 2),
            'error_rate_pct': round(self.get_error_rate(), 2),
            'cache_hit_rate_pct': round(self.get_cache_hit_rate(), 2),
            'total_requests': len(self.metrics['requests']),
            'total_errors': len(self.metrics['errors']),
            'total_cache_hits': len(self.metrics['cache_hits'])
        }
    
    def reset(self):
        """Reset all metrics"""
        for key in self.metrics:
            self.metrics[key].clear()
        self.start_time = datetime.now()


class Timer:
    """Context manager for timing operations"""
    
    def __init__(self, metrics: MetricsCollector, operation: str):
        self.metrics = metrics
        self.operation = operation
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
    
    def __exit__(self, *args):
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        self.metrics.record_latency(self.operation, duration_ms)