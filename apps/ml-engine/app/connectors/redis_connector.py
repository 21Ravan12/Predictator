"""Redis connector - for production caching and queues"""

import json
from typing import Optional, Any, Dict, List
from datetime import datetime, timedelta
import logging
from ..config import settings

logger = logging.getLogger(__name__)

# Try to import redis, but don't fail if not installed
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("Redis not installed. Install with: pip install redis")


class RedisConnector:
    """Connector for Redis caching and message queue"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or settings.REDIS_URL
        self.client = None
        self.enabled = False
        
        if REDIS_AVAILABLE and self.redis_url:
            self._connect()
    
    def _connect(self):
        """Establish Redis connection"""
        
        try:
            self.client = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            self.client.ping()
            self.enabled = True
            logger.info("✅ Redis connected")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Running without Redis.")
            self.enabled = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set value in cache with expiration"""
        
        if not self.enabled:
            return False
        
        try:
            self.client.setex(
                key,
                expire_seconds,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache"""
        
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        
        if not self.enabled:
            return False
        
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis exists error: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter"""
        
        if not self.enabled:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Redis increment error: {e}")
            return None
    
    def push_to_queue(self, queue_name: str, data: Any) -> bool:
        """Push message to queue"""
        
        if not self.enabled:
            return False
        
        try:
            self.client.lpush(
                queue_name,
                json.dumps(data, default=str)
            )
            return True
        except Exception as e:
            logger.error(f"Redis queue push error: {e}")
            return False
    
    def pop_from_queue(self, queue_name: str, timeout: int = 0) -> Optional[Any]:
        """Pop message from queue"""
        
        if not self.enabled:
            return None
        
        try:
            if timeout > 0:
                result = self.client.brpop(queue_name, timeout=timeout)
                if result:
                    return json.loads(result[1])
            else:
                result = self.client.rpop(queue_name)
                if result:
                    return json.loads(result)
            return None
        except Exception as e:
            logger.error(f"Redis queue pop error: {e}")
            return None
    
    def get_queue_length(self, queue_name: str) -> int:
        """Get queue length"""
        
        if not self.enabled:
            return 0
        
        try:
            return self.client.llen(queue_name)
        except Exception as e:
            logger.error(f"Redis queue length error: {e}")
            return 0
    
    def cache_prediction(self, product_id: str, prediction: Dict, ttl: int = 3600) -> bool:
        """Cache a prediction result"""
        
        key = f"prediction:{product_id}"
        return self.set(key, prediction, ttl)
    
    def get_cached_prediction(self, product_id: str) -> Optional[Dict]:
        """Get cached prediction"""
        
        key = f"prediction:{product_id}"
        return self.get(key)
    
    def cache_training_data(self, product_id: str, data: List[Dict], ttl: int = 86400) -> bool:
        """Cache training data"""
        
        key = f"training:{product_id}"
        return self.set(key, data, ttl)
    
    def get_stats(self) -> Dict:
        """Get Redis statistics"""
        
        if not self.enabled:
            return {'enabled': False}
        
        try:
            info = self.client.info()
            return {
                'enabled': True,
                'connected': True,
                'version': info.get('redis_version'),
                'used_memory_mb': info.get('used_memory_rss', 0) / 1024 / 1024,
                'total_connections': info.get('total_connections_received', 0),
                'total_commands': info.get('total_commands_processed', 0)
            }
        except Exception as e:
            return {
                'enabled': True,
                'connected': False,
                'error': str(e)
            }


class CacheService:
    """High-level cache service for Predictator"""
    
    def __init__(self):
        self.redis = RedisConnector()
        self.memory_cache = {}
    
    def get_or_compute(self, key: str, compute_func, ttl: int = 3600):
        """Get from cache or compute and store"""
        
        # Try Redis first
        if self.redis.enabled:
            cached = self.redis.get(key)
            if cached:
                return cached
        
        # Try memory cache
        if key in self.memory_cache:
            value, timestamp = self.memory_cache[key]
            if datetime.now() - timestamp < timedelta(seconds=ttl):
                return value
        
        # Compute value
        value = compute_func()
        
        # Store in both caches
        if self.redis.enabled:
            self.redis.set(key, value, ttl)
        
        self.memory_cache[key] = (value, datetime.now())
        
        return value
    
    def invalidate(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        
        # Clear memory cache
        keys_to_delete = [k for k in self.memory_cache if pattern in k]
        for k in keys_to_delete:
            del self.memory_cache[k]
        
        # Clear Redis if enabled
        if self.redis.enabled:
            keys = self.redis.client.keys(f"*{pattern}*")
            for key in keys:
                self.redis.delete(key)
    
    def clear_all(self):
        """Clear all caches"""
        
        self.memory_cache.clear()
        
        if self.redis.enabled:
            self.redis.client.flushdb()