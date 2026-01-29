from typing import Any, Optional, Dict
import asyncio
import hashlib
import time
from datetime import datetime, timedelta
from ..utils.logger import get_logger


class CacheEntry:
    """Represents a cached value with expiration"""
    def __init__(self, value: Any, ttl: float, created_at: float = None):
        self.value = value
        self.ttl = ttl  # Time-to-live in seconds
        self.created_at = created_at or time.time()
    
    def is_expired(self) -> bool:
        """Check if the cache entry has expired"""
        return time.time() - self.created_at > self.ttl
    
    def time_remaining(self) -> float:
        """Get the time remaining before expiration"""
        return max(0, self.ttl - (time.time() - self.created_at))


class LRUCache:
    """Simple LRU (Least Recently Used) cache implementation"""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache: Dict[str, CacheEntry] = {}
        self.access_order: Dict[str, float] = {}  # Track access times
        self._lock = asyncio.Lock()
        self._logger = get_logger(__name__)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from the cache"""
        async with self._lock:
            if key in self.cache:
                entry = self.cache[key]
                if entry.is_expired():
                    # Remove expired entry
                    del self.cache[key]
                    if key in self.access_order:
                        del self.access_order[key]
                    self._logger.debug(f"Cache miss: expired entry for key {key}")
                    return None
                
                # Update access time
                self.access_order[key] = time.time()
                self._logger.debug(f"Cache hit for key {key}")
                return entry.value
            
            self._logger.debug(f"Cache miss for key {key}")
            return None
    
    async def set(self, key: str, value: Any, ttl: float = 300.0):  # 5 minutes default
        """Set a value in the cache"""
        async with self._lock:
            # Check if we need to evict entries due to size limit
            if len(self.cache) >= self.max_size:
                # Remove least recently used entries
                sorted_keys = sorted(self.access_order.items(), key=lambda x: x[1])
                keys_to_remove = []
                
                # Remove enough entries to make room for the new one
                excess = len(self.cache) - self.max_size + 1
                for i in range(min(excess, len(sorted_keys))):
                    key_to_remove = sorted_keys[i][0]
                    keys_to_remove.append(key_to_remove)
                
                for key_to_remove in keys_to_remove:
                    del self.cache[key_to_remove]
                    del self.access_order[key_to_remove]
                
                self._logger.info(f"Evicted {len(keys_to_remove)} entries from cache due to size limit")
            
            # Add the new entry
            self.cache[key] = CacheEntry(value, ttl)
            self.access_order[key] = time.time()
            self._logger.debug(f"Cache set for key {key}")
    
    async def delete(self, key: str) -> bool:
        """Delete a value from the cache"""
        async with self._lock:
            if key in self.cache:
                del self.cache[key]
                if key in self.access_order:
                    del self.access_order[key]
                self._logger.debug(f"Cache deleted for key {key}")
                return True
            return False
    
    async def clear(self):
        """Clear all entries from the cache"""
        async with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self._logger.info("Cache cleared")
    
    def size(self) -> int:
        """Get the current size of the cache"""
        return len(self.cache)
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "size": self.size(),
            "max_size": self.max_size,
            "hit_rate": getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1),
            "keys": list(self.cache.keys())
        }


class DomainCache:
    """Cache specifically designed for domain operations"""
    
    def __init__(self, lru_cache: LRUCache = None, enabled: bool = True):
        self.lru_cache = lru_cache or LRUCache()
        self.enabled = enabled
        self._logger = get_logger(__name__)
        self._hit_count = 0
        self._total_requests = 0
    
    def _generate_key(self, domain_name: str, operation: str, input_data) -> str:
        """Generate a cache key based on domain, operation, and input"""
        # Create a hash of the input data to make a unique key
        input_str = f"{domain_name}:{operation}:{str(input_data.query)}:{str(input_data.context)}:{str(input_data.parameters)}"
        return hashlib.sha256(input_str.encode()).hexdigest()
    
    async def get_cached_result(self, domain_name: str, operation: str, input_data) -> Optional[Any]:
        """Get a cached result for a domain operation"""
        if not self.enabled:
            return None
        
        key = self._generate_key(domain_name, operation, input_data)
        self._total_requests += 1
        
        result = await self.lru_cache.get(key)
        if result is not None:
            self._hit_count += 1
            self._logger.debug(f"Cache hit for domain {domain_name}, operation {operation}")
        
        return result
    
    async def cache_result(self, domain_name: str, operation: str, input_data, result: Any, ttl: float = 300.0):
        """Cache a result for a domain operation"""
        if not self.enabled:
            return
        
        key = self._generate_key(domain_name, operation, input_data)
        await self.lru_cache.set(key, result, ttl)
        self._logger.debug(f"Cached result for domain {domain_name}, operation {operation}")
    
    async def invalidate(self, domain_name: str = None, operation: str = None):
        """Invalidate cache entries"""
        # For simplicity, we'll clear the entire cache
        # In a more advanced implementation, we could selectively invalidate
        await self.lru_cache.clear()
        self._logger.info(f"Cache invalidated for domain {domain_name}, operation {operation}")


# Global cache instance
domain_cache = DomainCache()


def get_domain_cache() -> DomainCache:
    """Get the global domain cache"""
    return domain_cache