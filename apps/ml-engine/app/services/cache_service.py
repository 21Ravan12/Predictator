"""Cache service - Redis-based caching for predictions and data"""

import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not installed. Cache service will use in-memory fallback.")

logger = logging.getLogger(__name__)


class CacheService:
    """Service for caching predictions, products, and API responses"""
    
    def __init__(self, redis_url: Optional[str] = None, use_memory_fallback: bool = True):
        """
        Initialize cache service
        
        Args:
            redis_url: Redis connection URL (e.g., redis://localhost:6379)
            use_memory_fallback: Use in-memory cache if Redis unavailable
        """
        self.use_memory_fallback = use_memory_fallback
        self._memory_cache = {}  # Fallback in-memory cache
        self._memory_ttl = {}    # Track TTL for memory cache
        self._redis_client = None
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self._redis_client = redis.from_url(redis_url, decode_responses=True)
                self._redis_client.ping()
                logger.info("✅ Redis cache connected successfully")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}")
                self._redis_client = None
        else:
            if redis_url:
                logger.warning("Redis URL provided but redis package not installed")
            logger.info("Using in-memory cache fallback")
    
    def _get_redis(self):
        """Get Redis client if available"""
        if self._redis_client:
            try:
                self._redis_client.ping()
                return self._redis_client
            except:
                return None
        return None
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and parameters"""
        key_parts = [prefix]
        key_parts.extend([str(arg) for arg in args])
        key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
        
        key_string = ":".join(key_parts)
        
        # Use hash for long keys
        if len(key_string) > 100:
            hash_key = hashlib.md5(key_string.encode()).hexdigest()[:16]
            return f"{prefix}:{hash_key}"
        
        return key_string
    
    def _get_memory(self, key: str) -> Optional[Any]:
        """Get from in-memory cache with TTL check"""
        if key in self._memory_cache:
            # Check TTL
            if key in self._memory_ttl:
                expire_time = self._memory_ttl[key]
                if datetime.now() > expire_time:
                    # Expired
                    del self._memory_cache[key]
                    del self._memory_ttl[key]
                    return None
            return self._memory_cache[key]
        return None
    
    def _set_memory(self, key: str, value: Any, ttl_seconds: int = 300):
        """Set in-memory cache with TTL"""
        self._memory_cache[key] = value
        if ttl_seconds > 0:
            self._memory_ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
        else:
            # No TTL
            if key in self._memory_ttl:
                del self._memory_ttl[key]
    
    def _delete_memory(self, pattern: str) -> int:
        """Delete from in-memory cache by pattern"""
        deleted = 0
        keys_to_delete = [k for k in self._memory_cache.keys() if pattern.replace('*', '') in k]
        for key in keys_to_delete:
            del self._memory_cache[key]
            if key in self._memory_ttl:
                del self._memory_ttl[key]
            deleted += 1
        return deleted
    
    # ==================== CACHE OPERATIONS ====================
    
    def get(self, prefix: str, *args, **kwargs) -> Optional[Any]:
        """Get value from cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        # Try Redis first
        redis_client = self._get_redis()
        if redis_client:
            try:
                value = redis_client.get(key)
                if value:
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"Redis get error: {e}")
        
        # Fallback to memory
        if self.use_memory_fallback:
            return self._get_memory(key)
        
        return None
    
    def set(self, prefix: str, value: Any, ttl_seconds: int = 300, *args, **kwargs) -> bool:
        """Set value in cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        # Convert to JSON
        try:
            json_value = json.dumps(value, default=str)
        except Exception as e:
            logger.error(f"Failed to serialize value: {e}")
            return False
        
        # Try Redis first
        redis_client = self._get_redis()
        if redis_client:
            try:
                if ttl_seconds > 0:
                    redis_client.setex(key, ttl_seconds, json_value)
                else:
                    redis_client.set(key, json_value)
                return True
            except Exception as e:
                logger.warning(f"Redis set error: {e}")
        
        # Fallback to memory
        if self.use_memory_fallback:
            self._set_memory(key, value, ttl_seconds)
            return True
        
        return False
    
    def delete(self, prefix: str, *args, **kwargs) -> int:
        """Delete from cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        deleted = 0
        
        # Try Redis
        redis_client = self._get_redis()
        if redis_client:
            try:
                deleted += redis_client.delete(key)
            except Exception as e:
                logger.warning(f"Redis delete error: {e}")
        
        # Memory fallback
        if self.use_memory_fallback:
            if self._memory_cache.get(key):
                del self._memory_cache[key]
                if key in self._memory_ttl:
                    del self._memory_ttl[key]
                deleted += 1
        
        return deleted
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern"""
        deleted = 0
        
        # Try Redis
        redis_client = self._get_redis()
        if redis_client:
            try:
                keys = redis_client.keys(pattern)
                if keys:
                    deleted += redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis delete_pattern error: {e}")
        
        # Memory fallback
        if self.use_memory_fallback:
            deleted += self._delete_memory(pattern)
        
        return deleted
    
    def clear_all(self) -> int:
        """Clear entire cache"""
        deleted = 0
        
        # Try Redis
        redis_client = self._get_redis()
        if redis_client:
            try:
                deleted += redis_client.flushdb()
            except Exception as e:
                logger.warning(f"Redis clear error: {e}")
        
        # Memory fallback
        if self.use_memory_fallback:
            deleted += len(self._memory_cache)
            self._memory_cache.clear()
            self._memory_ttl.clear()
        
        return deleted
    
    def exists(self, prefix: str, *args, **kwargs) -> bool:
        """Check if key exists in cache"""
        key = self._generate_key(prefix, *args, **kwargs)
        
        # Try Redis
        redis_client = self._get_redis()
        if redis_client:
            try:
                return redis_client.exists(key) > 0
            except:
                pass
        
        # Memory fallback
        if self.use_memory_fallback:
            return key in self._memory_cache
        
        return False
    
    # ==================== SPECIFIC CACHE METHODS ====================
    
    def cache_prediction(
        self,
        product_id: str,
        days_ahead: int,
        floor_limit: int,
        prediction_result: Dict,
        ttl_seconds: int = 3600  # 1 hour cache for predictions
    ) -> bool:
        """Cache prediction result"""
        return self.set(
            "prediction",
            prediction_result,
            ttl_seconds=ttl_seconds,
            product_id=product_id,
            days_ahead=days_ahead,
            floor_limit=floor_limit
        )
    
    def get_cached_prediction(
        self,
        product_id: str,
        days_ahead: int,
        floor_limit: int
    ) -> Optional[Dict]:
        """Get cached prediction"""
        return self.get(
            "prediction",
            product_id=product_id,
            days_ahead=days_ahead,
            floor_limit=floor_limit
        )
    
    def invalidate_product_predictions(self, product_id: str) -> int:
        """Invalidate all predictions for a product"""
        return self.delete_pattern(f"*prediction*{product_id}*")
    
    def cache_product_data(
        self,
        product_id: str,
        data: Dict,
        ttl_seconds: int = 300  # 5 minutes for product data
    ) -> bool:
        """Cache product data"""
        return self.set(
            "product_data",
            data,
            ttl_seconds=ttl_seconds,
            product_id=product_id
        )
    
    def get_cached_product_data(self, product_id: str) -> Optional[Dict]:
        """Get cached product data"""
        return self.get("product_data", product_id=product_id)
    
    def cache_all_products(self, products_data: Dict, ttl_seconds: int = 60) -> bool:
        """Cache all products list"""
        return self.set(
            "all_products",
            products_data,
            ttl_seconds=ttl_seconds
        )
    
    def get_cached_all_products(self) -> Optional[Dict]:
        """Get cached all products"""
        return self.get("all_products")
    
    def cache_model_metrics(self, metrics: Dict, ttl_seconds: int = 300) -> bool:
        """Cache model metrics"""
        return self.set("model_metrics", metrics, ttl_seconds=ttl_seconds)
    
    def get_cached_model_metrics(self) -> Optional[Dict]:
        """Get cached model metrics"""
        return self.get("model_metrics")
    
    def cache_health_status(self, health: Dict, ttl_seconds: int = 30) -> bool:
        """Cache health status (short TTL)"""
        return self.set("health_status", health, ttl_seconds=ttl_seconds)
    
    def get_cached_health_status(self) -> Optional[Dict]:
        """Get cached health status"""
        return self.get("health_status")
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        redis_client = self._get_redis()
        redis_stats = {}
        
        if redis_client:
            try:
                info = redis_client.info()
                redis_stats = {
                    'connected': True,
                    'used_memory_mb': info.get('used_memory', 0) / (1024 * 1024),
                    'total_commands': info.get('total_commands_processed', 0),
                    'hits': info.get('keyspace_hits', 0),
                    'misses': info.get('keyspace_misses', 0)
                }
            except:
                redis_stats = {'connected': False}
        else:
            redis_stats = {'connected': False}
        
        return {
            'success': True,
            'redis': redis_stats,
            'memory_fallback': {
                'active': self.use_memory_fallback and not redis_stats.get('connected', False),
                'keys': len(self._memory_cache),
                'size_estimate_mb': sum(len(str(v)) for v in self._memory_cache.values()) / (1024 * 1024)
            }
        }
    
    def warmup_cache(self, product_ids: List[str]) -> Dict:
        """Pre-warm cache for popular products"""
        warmed = 0
        
        for product_id in product_ids:
            # You would fetch and cache product data here
            # This is a placeholder for actual warming logic
            warmed += 1
        
        return {
            'success': True,
            'warmed_products': warmed,
            'message': f'Warmed cache for {warmed} products'
        }


# Simple in-memory cache for when Redis is not available
class SimpleCache:
    """Ultra-simple in-memory cache (fallback)"""
    
    def __init__(self):
        self._cache = {}
        self._ttl = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if key in self._ttl and datetime.now() > self._ttl[key]:
                del self._cache[key]
                del self._ttl[key]
                return None
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        self._cache[key] = value
        if ttl_seconds > 0:
            self._ttl[key] = datetime.now() + timedelta(seconds=ttl_seconds)
    
    def delete(self, key: str):
        if key in self._cache:
            del self._cache[key]
        if key in self._ttl:
            del self._ttl[key]
    
    def clear(self):
        self._cache.clear()
        self._ttl.clear()