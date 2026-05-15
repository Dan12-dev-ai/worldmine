"""
Advanced Multi-Tier Caching System for DEDAN 2.0
L1: In-memory cache, L2: Redis, L3: Database
Cache-aside + Write-through + LRU eviction
"""

import asyncio
import json
import logging
import time
import hashlib
import pickle
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
import aioredis
import asyncpg
import zlib
from collections import OrderedDict
import weakref
import gc
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Cache levels"""
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_DATABASE = "l3_database"

class CacheStrategy(Enum):
    """Caching strategies"""
    CACHE_ASIDE = "cache_aside"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"

class EvictionPolicy(Enum):
    """Eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    RANDOM = "random"

@dataclass
class CacheConfig:
    """Cache configuration"""
    l1_max_size: int = 1000
    l1_ttl_seconds: int = 300  # 5 minutes
    l2_ttl_seconds: int = 3600  # 1 hour
    l3_ttl_seconds: int = 86400  # 24 hours
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    compression_enabled: bool = True
    serialization_method: str = "pickle"  # pickle, json, msgpack
    cache_stats_enabled: bool = True
    auto_cleanup_interval: int = 300  # 5 minutes
    max_memory_usage_mb: int = 512
    redis_cluster_nodes: List[str] = field(default_factory=list)
    connection_pool_size: int = 20

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    level: CacheLevel
    ttl: datetime
    access_count: int = 0
    last_access: datetime = field(default_factory=datetime.utcnow)
    size_bytes: int = 0
    checksum: str = ""
    version: int = 1
    tags: List[str] = field(default_factory=list)

class LRUCache:
    """Thread-safe LRU cache implementation"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                value = self.cache.pop(key)
                self.cache[key] = value
                self.hits += 1
                return value
            else:
                self.misses += 1
                return None
    
    def put(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.pop(key)
            elif len(self.cache) >= self.max_size:
                # Remove least recently used
                self.cache.popitem(last=False)
            
            self.cache[key] = value
    
    def remove(self, key: str) -> bool:
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self) -> None:
        with self.lock:
            self.cache.clear()
            self.hits = 0
            self.misses = 0
    
    def size(self) -> int:
        with self.lock:
            return len(self.cache)
    
    def get_stats(self) -> Dict[str, Any]:
        with self.lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'hit_rate': hit_rate,
                'size': len(self.cache),
                'max_size': self.max_size
            }

class AdvancedCacheManager:
    """Advanced multi-tier caching system"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.l1_cache = LRUCache(config.l1_max_size)
        self.l2_redis = None
        self.l3_database = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache_stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'l3_hits': 0,
            'l3_misses': 0,
            'total_operations': 0,
            'evictions': 0,
            'memory_usage_bytes': 0,
            'cache_size': 0
        }
        self.running = False
        self.cleanup_task = None
        
        # Initialize connections
        self.initialize_connections()
    
    def initialize_connections(self):
        """Initialize Redis and database connections"""
        try:
            # Initialize Redis connection pool
            if self.config.redis_cluster_nodes:
                self.l2_redis = aioredis.Redis(
                    host=self.config.redis_cluster_nodes[0],
                    port=6379,
                    db=0,
                    max_connections=self.config.connection_pool_size,
                    retry_on_timeout=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    decode_responses=True
                )
            else:
                self.l2_redis = aioredis.from_url("redis://localhost:6379")
            
            logger.info("Redis connection pool initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            raise
    
    async def get(self, key: str, default: Any = None, 
                 tags: List[str] = None) -> Any:
        """Get value from cache (L1 -> L2 -> L3)"""
        start_time = time.time()
        self.cache_stats['total_operations'] += 1
        
        try:
            # Try L1 cache first
            value = await self._get_from_l1(key)
            if value is not None:
                self.cache_stats['l1_hits'] += 1
                logger.debug(f"L1 cache hit for key: {key}")
                return value
            
            self.cache_stats['l1_misses'] += 1
            
            # Try L2 cache (Redis)
            value = await self._get_from_l2(key)
            if value is not None:
                self.cache_stats['l2_hits'] += 1
                # Store in L1 for faster access
                await self._put_to_l1(key, value)
                logger.debug(f"L2 cache hit for key: {key}")
                return value
            
            self.cache_stats['l2_misses'] += 1
            
            # Try L3 cache (Database)
            value = await self._get_from_l3(key)
            if value is not None:
                self.cache_stats['l3_hits'] += 1
                # Store in L1 and L2 for faster access
                await self._put_to_l1(key, value)
                await self._put_to_l2(key, value)
                logger.debug(f"L3 cache hit for key: {key}")
                return value
            
            self.cache_stats['l3_misses'] += 1
            logger.debug(f"Cache miss for key: {key}")
            return default
            
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return default
        finally:
            execution_time = time.time() - start_time
            if execution_time > 0.1:  # Log slow operations
                logger.warning(f"Slow cache get for key {key}: {execution_time:.3f}s")
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None,
                 tags: List[str] = None, level: Optional[CacheLevel] = None) -> bool:
        """Set value in cache based on strategy"""
        start_time = time.time()
        
        try:
            if self.config.strategy == CacheStrategy.CACHE_ASIDE:
                return await self._set_cache_aside(key, value, ttl, tags, level)
            elif self.config.strategy == CacheStrategy.WRITE_THROUGH:
                return await self._set_write_through(key, value, ttl, tags, level)
            elif self.config.strategy == CacheStrategy.WRITE_BEHIND:
                return await self._set_write_behind(key, value, ttl, tags, level)
            elif self.config.strategy == CacheStrategy.WRITE_AROUND:
                return await self._set_write_around(key, value, ttl, tags, level)
            else:
                logger.error(f"Unknown cache strategy: {self.config.strategy}")
                return False
                
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            return False
        finally:
            execution_time = time.time() - start_time
            if execution_time > 0.5:  # Log slow operations
                logger.warning(f"Slow cache set for key {key}: {execution_time:.3f}s")
    
    async def _set_cache_aside(self, key: str, value: Any, ttl: Optional[int],
                               tags: List[str], level: Optional[CacheLevel]) -> bool:
        """Set value using cache-aside strategy"""
        success = True
        
        # Store in L1
        l1_success = await self._put_to_l1(key, value, ttl, tags)
        
        # Store in L2
        l2_success = await self._put_to_l2(key, value, ttl, tags)
        
        # Store in L3 if specified or if L1/L2 failed
        if level == CacheLevel.L3_DATABASE or (not l1_success and not l2_success):
            l3_success = await self._put_to_l3(key, value, ttl, tags)
            success = l3_success
        
        return success
    
    async def _set_write_through(self, key: str, value: Any, ttl: Optional[int],
                              tags: List[str], level: Optional[CacheLevel]) -> bool:
        """Set value using write-through strategy"""
        # Always store in L3 (database) first
        l3_success = await self._put_to_l3(key, value, ttl, tags)
        
        if l3_success:
            # Then store in L1 and L2
            await self._put_to_l1(key, value, ttl, tags)
            await self._put_to_l2(key, value, ttl, tags)
            return True
        
        return False
    
    async def _set_write_behind(self, key: str, value: Any, ttl: Optional[int],
                               tags: List[str], level: Optional[CacheLevel]) -> bool:
        """Set value using write-behind strategy"""
        # Store in L1 and L2 immediately
        await self._put_to_l1(key, value, ttl, tags)
        await self._put_to_l2(key, value, ttl, tags)
        
        # Asynchronously store in L3
        asyncio.create_task(self._put_to_l3(key, value, ttl, tags))
        return True
    
    async def _set_write_around(self, key: str, value: Any, ttl: Optional[int],
                             tags: List[str], level: Optional[CacheLevel]) -> bool:
        """Set value using write-around strategy"""
        # Store in L1 and L2, but not in L3
        await self._put_to_l1(key, value, ttl, tags)
        await self._put_to_l2(key, value, ttl, tags)
        return True
    
    async def _get_from_l1(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        try:
            entry = self.l1_cache.get(key)
            if entry is not None:
                # Check TTL
                if datetime.utcnow() > entry.ttl:
                    self.l1_cache.remove(key)
                    return None
                
                # Update access info
                entry.access_count += 1
                entry.last_access = datetime.utcnow()
                
                # Update checksum
                if self.config.serialization_method == "pickle":
                    serialized = pickle.dumps(entry.value)
                    entry.checksum = hashlib.sha256(serialized).hexdigest()
                
                return entry.value
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting from L1 cache: {e}")
            return None
    
    async def _get_from_l2(self, key: str) -> Optional[Any]:
        """Get value from L2 cache (Redis)"""
        try:
            if not self.l2_redis:
                return None
            
            # Get cache entry
            data = await self.l2_redis.get(f"cache:{key}")
            if data is None:
                return None
            
            # Deserialize and check TTL
            entry = self._deserialize_data(data)
            if entry is None or datetime.utcnow() > entry.ttl:
                await self.l2_redis.delete(f"cache:{key}")
                return None
            
            # Update access info
            entry.access_count += 1
            entry.last_access = datetime.utcnow()
            
            # Update in Redis
            serialized_entry = self._serialize_data(entry)
            await self.l2_redis.setex(f"cache:{key}", entry.ttl, serialized_entry)
            
            return entry.value
            
        except Exception as e:
            logger.error(f"Error getting from L2 cache: {e}")
            return None
    
    async def _get_from_l3(self, key: str) -> Optional[Any]:
        """Get value from L3 cache (Database)"""
        try:
            # This would connect to your database
            # For now, return None to simulate cache miss
            return None
            
        except Exception as e:
            logger.error(f"Error getting from L3 cache: {e}")
            return None
    
    async def _put_to_l1(self, key: str, value: Any, ttl: Optional[int] = None,
                         tags: List[str] = None) -> bool:
        """Put value in L1 cache"""
        try:
            if ttl is None:
                ttl = self.config.l1_ttl_seconds
            
            entry = CacheEntry(
                key=key,
                value=value,
                level=CacheLevel.L1_MEMORY,
                ttl=datetime.utcnow() + timedelta(seconds=ttl),
                tags=tags or []
            )
            
            # Calculate size
            if self.config.serialization_method == "pickle":
                serialized = pickle.dumps(value)
                entry.size_bytes = len(serialized)
                entry.checksum = hashlib.sha256(serialized).hexdigest()
            
            # Check memory usage
            if self._should_evict_for_memory(entry.size_bytes):
                self._evict_l1_items()
            
            self.l1_cache.put(key, entry)
            return True
            
        except Exception as e:
            logger.error(f"Error putting to L1 cache: {e}")
            return False
    
    async def _put_to_l2(self, key: str, value: Any, ttl: Optional[int] = None,
                         tags: List[str] = None) -> bool:
        """Put value in L2 cache (Redis)"""
        try:
            if not self.l2_redis:
                return False
            
            if ttl is None:
                ttl = self.config.l2_ttl_seconds
            
            entry = CacheEntry(
                key=key,
                value=value,
                level=CacheLevel.L2_REDIS,
                ttl=datetime.utcnow() + timedelta(seconds=ttl),
                tags=tags or []
            )
            
            # Calculate size and checksum
            if self.config.serialization_method == "pickle":
                serialized = pickle.dumps(value)
                entry.size_bytes = len(serialized)
                entry.checksum = hashlib.sha256(serialized).hexdigest()
            
            # Compress if enabled
            serialized_entry = self._serialize_data(entry)
            if self.config.compression_enabled:
                serialized_entry = zlib.compress(serialized_entry)
            
            # Store in Redis
            await self.l2_redis.setex(f"cache:{key}", ttl, serialized_entry)
            return True
            
        except Exception as e:
            logger.error(f"Error putting to L2 cache: {e}")
            return False
    
    async def _put_to_l3(self, key: str, value: Any, ttl: Optional[int] = None,
                         tags: List[str] = None) -> bool:
        """Put value in L3 cache (Database)"""
        try:
            if ttl is None:
                ttl = self.config.l3_ttl_seconds
            
            # This would store in your database
            # For now, just log the operation
            entry = CacheEntry(
                key=key,
                value=value,
                level=CacheLevel.L3_DATABASE,
                ttl=datetime.utcnow() + timedelta(seconds=ttl),
                tags=tags or []
            )
            
            logger.info(f"Would store in L3 cache: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Error putting to L3 cache: {e}")
            return False
    
    def _should_evict_for_memory(self, entry_size: int) -> bool:
        """Check if eviction is needed for memory constraints"""
        current_usage = self._get_memory_usage()
        return (current_usage + entry_size) > (self.config.max_memory_usage_mb * 1024 * 1024)
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage of L1 cache"""
        total_size = 0
        for key in self.l1_cache.cache:
            entry = self.l1_cache.cache[key]
            total_size += entry.size_bytes
        return total_size
    
    def _evict_l1_items(self) -> None:
        """Evict items from L1 cache based on policy"""
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # LRU is already implemented in LRUCache
            pass
        elif self.config.eviction_policy == EvictionPolicy.LFU:
            self._evict_lfu_items()
        elif self.config.eviction_policy == EvictionPolicy.TTL:
            self._evict_ttl_items()
        elif self.config.eviction_policy == EvictionPolicy.RANDOM:
            self._evict_random_items()
    
    def _evict_lfu_items(self) -> None:
        """Evict least frequently used items"""
        with self.l1_cache.lock:
            if len(self.l1_cache.cache) == 0:
                return
            
            # Find least frequently used items
            items_by_frequency = []
            for key, entry in self.l1_cache.cache.items():
                items_by_frequency.append((entry.access_count, key, entry))
            
            items_by_frequency.sort(key=lambda x: x[0])
            
            # Evict 10% of items
            evict_count = max(1, len(items_by_frequency) // 10)
            
            for i in range(evict_count):
                _, key, _ = items_by_frequency[i]
                del self.l1_cache.cache[key]
                self.cache_stats['evictions'] += 1
    
    def _evict_ttl_items(self) -> None:
        """Evict expired items"""
        with self.l1_cache.lock:
            current_time = datetime.utcnow()
            expired_keys = []
            
            for key, entry in self.l1_cache.cache.items():
                if current_time > entry.ttl:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.l1_cache.cache[key]
                self.cache_stats['evictions'] += 1
    
    def _evict_random_items(self) -> None:
        """Evict random items"""
        with self.l1_cache.lock:
            if len(self.l1_cache.cache) == 0:
                return
            
            import random
            keys = list(self.l1_cache.cache.keys())
            evict_count = max(1, len(keys) // 10)
            
            for _ in range(evict_count):
                if keys:
                    key = random.choice(keys)
                    if key in self.l1_cache.cache:
                        del self.l1_cache.cache[key]
                        keys.remove(key)
                        self.cache_stats['evictions'] += 1
    
    def _serialize_data(self, data: Any) -> bytes:
        """Serialize data for storage"""
        if self.config.serialization_method == "pickle":
            return pickle.dumps(data)
        elif self.config.serialization_method == "json":
            return json.dumps(data).encode()
        elif self.config.serialization_method == "msgpack":
            import msgpack
            return msgpack.packb(data)
        else:
            return pickle.dumps(data)
    
    def _deserialize_data(self, data: bytes) -> Any:
        """Deserialize data from storage"""
        try:
            # Try to decompress first
            if self.config.compression_enabled:
                try:
                    data = zlib.decompress(data)
                except:
                    pass  # Data might not be compressed
            
            if self.config.serialization_method == "pickle":
                return pickle.loads(data)
            elif self.config.serialization_method == "json":
                return json.loads(data.decode())
            elif self.config.serialization_method == "msgpack":
                import msgpack
                return msgpack.unpackb(data)
            else:
                return pickle.loads(data)
                
        except Exception as e:
            logger.error(f"Error deserializing data: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        success = True
        
        # Delete from L1
        self.l1_cache.remove(key)
        
        # Delete from L2
        try:
            if self.l2_redis:
                await self.l2_redis.delete(f"cache:{key}")
        except Exception as e:
            logger.error(f"Error deleting from L2 cache: {e}")
            success = False
        
        # Delete from L3
        try:
            await self._delete_from_l3(key)
        except Exception as e:
            logger.error(f"Error deleting from L3 cache: {e}")
            success = False
        
        return success
    
    async def _delete_from_l3(self, key: str) -> bool:
        """Delete key from L3 cache (Database)"""
        # This would delete from your database
        logger.info(f"Would delete from L3 cache: {key}")
        return True
    
    async def clear(self, level: Optional[CacheLevel] = None) -> None:
        """Clear cache by level"""
        if level is None or level == CacheLevel.L1_MEMORY:
            self.l1_cache.clear()
        
        if level is None or level == CacheLevel.L2_REDIS:
            try:
                if self.l2_redis:
                    # Clear all cache keys
                    pattern = "cache:*"
                    keys = await self.l2_redis.keys(pattern)
                    if keys:
                        await self.l2_redis.delete(*keys)
            except Exception as e:
                logger.error(f"Error clearing L2 cache: {e}")
        
        if level is None or level == CacheLevel.L3_DATABASE:
            await self._clear_l3_cache()
    
    async def _clear_l3_cache(self) -> None:
        """Clear L3 cache (Database)"""
        # This would clear from your database
        logger.info("Would clear L3 cache")
    
    async def cleanup_expired(self) -> None:
        """Clean up expired entries"""
        # Clean L1
        self._evict_ttl_items()
        
        # Clean L2 (Redis handles TTL automatically)
        # Clean L3
        await self._cleanup_l3_expired()
    
    async def _cleanup_l3_expired(self) -> None:
        """Clean up expired entries in L3 cache"""
        # This would clean expired entries from your database
        logger.info("Would clean up L3 expired entries")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics"""
        l1_stats = self.l1_cache.get_stats()
        
        # Calculate memory usage
        memory_usage = self._get_memory_usage()
        
        # Update cache stats
        self.cache_stats.update({
            'memory_usage_bytes': memory_usage,
            'cache_size': self.l1_cache.size(),
            'l1_hit_rate': l1_stats['hit_rate'],
            'l2_hit_rate': (self.cache_stats['l2_hits'] / (self.cache_stats['l2_hits'] + self.cache_stats['l2_misses']) * 100) if (self.cache_stats['l2_hits'] + self.cache_stats['l2_misses']) > 0 else 0,
            'l3_hit_rate': (self.cache_stats['l3_hits'] / (self.cache_stats['l3_hits'] + self.cache_stats['l3_misses']) * 100) if (self.cache_stats['l3_hits'] + self.cache_stats['l3_misses']) > 0 else 0,
            'overall_hit_rate': ((self.cache_stats['l1_hits'] + self.cache_stats['l2_hits'] + self.cache_stats['l3_hits']) / self.cache_stats['total_operations'] * 100) if self.cache_stats['total_operations'] > 0 else 0
        })
        
        return {
            'l1_cache': l1_stats,
            'l2_cache': {
                'hits': self.cache_stats['l2_hits'],
                'misses': self.cache_stats['l2_misses'],
                'hit_rate': self.cache_stats['l2_hit_rate']
            },
            'l3_cache': {
                'hits': self.cache_stats['l3_hits'],
                'misses': self.cache_stats['l3_misses'],
                'hit_rate': self.cache_stats['l3_hit_rate']
            },
            'overall': {
                'total_operations': self.cache_stats['total_operations'],
                'total_hits': self.cache_stats['l1_hits'] + self.cache_stats['l2_hits'] + self.cache_stats['l3_hits'],
                'total_misses': self.cache_stats['l1_misses'] + self.cache_stats['l2_misses'] + self.cache_stats['l3_misses'],
                'overall_hit_rate': self.cache_stats['overall_hit_rate'],
                'evictions': self.cache_stats['evictions'],
                'memory_usage_bytes': memory_usage,
                'memory_usage_mb': memory_usage / (1024 * 1024),
                'cache_size': self.cache_stats['cache_size'],
                'max_memory_usage_mb': self.config.max_memory_usage_mb
            },
            'config': {
                'strategy': self.config.strategy.value,
                'eviction_policy': self.config.eviction_policy.value,
                'l1_max_size': self.config.l1_max_size,
                'l1_ttl_seconds': self.config.l1_ttl_seconds,
                'l2_ttl_seconds': self.config.l2_ttl_seconds,
                'l3_ttl_seconds': self.config.l3_ttl_seconds,
                'compression_enabled': self.config.compression_enabled,
                'serialization_method': self.config.serialization_method
            }
        }
    
    async def warmup_cache(self, keys: List[str], data_source: Callable = None) -> None:
        """Warm up cache with data"""
        logger.info(f"Warming up cache with {len(keys)} keys")
        
        if data_source is None:
            return
        
        for key in keys:
            try:
                value = await data_source(key)
                if value is not None:
                    await self.set(key, value)
                    logger.debug(f"Warmed up key: {key}")
            except Exception as e:
                logger.error(f"Error warming up key {key}: {e}")
    
    async def start_background_tasks(self) -> None:
        """Start background cleanup and monitoring tasks"""
        self.running = True
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info("Background tasks started")
    
    async def stop_background_tasks(self) -> None:
        """Stop background tasks"""
        self.running = False
        
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Background tasks stopped")
    
    async def _cleanup_loop(self) -> None:
        """Background cleanup loop"""
        while self.running:
            try:
                await self.cleanup_expired()
                await asyncio.sleep(self.config.auto_cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(60)
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on cache system"""
        health_status = {
            'l1_cache': 'healthy',
            'l2_cache': 'healthy',
            'l3_cache': 'healthy',
            'overall': 'healthy',
            'issues': []
        }
        
        # Check L1 cache
        try:
            l1_stats = self.l1_cache.get_stats()
            if l1_stats['hit_rate'] < 50:  # Hit rate below 50%
                health_status['l1_cache'] = 'degraded'
                health_status['issues'].append('L1 cache hit rate too low')
        except Exception as e:
            health_status['l1_cache'] = 'unhealthy'
            health_status['issues'].append(f'L1 cache error: {e}')
        
        # Check L2 cache (Redis)
        try:
            if self.l2_redis:
                await self.l2_redis.ping()
            else:
                health_status['l2_cache'] = 'unhealthy'
                health_status['issues'].append('L2 Redis not connected')
        except Exception as e:
            health_status['l2_cache'] = 'unhealthy'
            health_status['issues'].append(f'L2 Redis error: {e}')
        
        # Check memory usage
        memory_usage_mb = self._get_memory_usage() / (1024 * 1024)
        if memory_usage_mb > self.config.max_memory_usage_mb * 0.9:
            health_status['overall'] = 'warning'
            health_status['issues'].append(f'Memory usage high: {memory_usage_mb:.1f}MB')
        
        # Determine overall health
        if any(status in ['unhealthy'] for status in [health_status['l1_cache'], health_status['l2_cache']]):
            health_status['overall'] = 'unhealthy'
        elif any(status in ['degraded'] for status in [health_status['l1_cache'], health_status['l2_cache']]):
            health_status['overall'] = 'degraded'
        
        return health_status

# Factory function for cache manager
def create_cache_manager(config: CacheConfig) -> AdvancedCacheManager:
    """Create cache manager instance"""
    return AdvancedCacheManager(config)

# Example usage
async def example_usage():
    """Example usage of advanced caching system"""
    
    # Configure cache
    config = CacheConfig(
        l1_max_size=1000,
        l1_ttl_seconds=300,
        l2_ttl_seconds=3600,
        l3_ttl_seconds=86400,
        strategy=CacheStrategy.CACHE_ASIDE,
        eviction_policy=EvictionPolicy.LRU,
        compression_enabled=True,
        serialization_method="pickle",
        cache_stats_enabled=True,
        auto_cleanup_interval=300,
        max_memory_usage_mb=512
    )
    
    # Create cache manager
    cache_manager = create_cache_manager(config)
    
    # Start background tasks
    await cache_manager.start_background_tasks()
    
    # Example operations
    await cache_manager.set("user:123", {"name": "John", "email": "john@example.com"})
    user_data = await cache_manager.get("user:123")
    
    # Get cache statistics
    stats = await cache_manager.get_cache_stats()
    print(f"Cache hit rate: {stats['overall']['overall_hit_rate']:.1f}%")
    
    # Health check
    health = await cache_manager.health_check()
    print(f"Cache health: {health['overall']}")
    
    # Cleanup
    await cache_manager.stop_background_tasks()

if __name__ == "__main__":
    asyncio.run(example_usage())
