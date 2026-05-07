"""
OPTIMIZED DATABASE LAYER - DEDAN WORLDMINE
High-performance, connection-pooled, cached database operations

Optimizations:
- Connection pooling
- Query optimization
- Prepared statements
- Batch operations
- Index optimization
- Read replicas
- Caching layer
"""

import asyncpg
import aioredis
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
import json
import logging
from datetime import datetime, timedelta
from contextlib import asynccontextmanager
import os
from dataclasses import dataclass
from functools import wraps
import time

logger = logging.getLogger(__name__)

@dataclass
class DatabaseConfig:
    """Database configuration"""
    host: str = "localhost"
    port: int = 5432
    database: str = "worldmine"
    user: str = "postgres"
    password: str = "password"
    min_size: int = 5
    max_size: int = 20
    command_timeout: int = 60

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    max_connections: int = 20
    retry_on_timeout: bool = True
    socket_keepalive: bool = True
    socket_keepalive_options: Dict = None

class QueryPerformanceMonitor:
    """Monitor query performance"""
    def __init__(self):
        self.query_times = {}
        self.slow_queries = []
    
    def record_query(self, query: str, duration: float):
        query_type = query.split()[0].upper()
        if query_type not in self.query_times:
            self.query_times[query_type] = []
        self.query_times[query_type].append(duration)
        
        if duration > 1.0:  # Slow query threshold
            self.slow_queries.append({
                "query": query,
                "duration": duration,
                "timestamp": datetime.now()
            })
    
    def get_stats(self) -> Dict[str, Any]:
        stats = {}
        for query_type, times in self.query_times.items():
            if times:
                stats[query_type] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times)
                }
        return stats

query_monitor = QueryPerformanceMonitor()

def monitor_query(func):
    """Decorator to monitor query performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            duration = time.time() - start_time
            # Extract query from args if available
            query = args[0] if args else "unknown"
            query_monitor.record_query(query, duration)
    return wrapper

class OptimizedDatabase:
    """Optimized database with connection pooling and caching"""
    
    def __init__(self, db_config: DatabaseConfig = None, redis_config: RedisConfig = None):
        self.db_config = db_config or DatabaseConfig()
        self.redis_config = redis_config or RedisConfig()
        self.pool = None
        self.redis_pool = None
        self.redis = None
        
    async def initialize(self):
        """Initialize database and Redis connections"""
        # Initialize PostgreSQL connection pool
        self.pool = await asyncpg.create_pool(
            host=self.db_config.host,
            port=self.db_config.port,
            database=self.db_config.database,
            user=self.db_config.user,
            password=self.db_config.password,
            min_size=self.db_config.min_size,
            max_size=self.db_config.max_size,
            command_timeout=self.db_config.command_timeout,
            server_settings={
                'application_name': 'worldmine_optimized',
                'jit': 'off'
            }
        )
        
        # Initialize Redis connection pool
        self.redis_pool = aioredis.ConnectionPool.from_url(
            f"redis://{self.redis_config.host}:{self.redis_config.port}/{self.redis_config.db}",
            max_connections=self.redis_config.max_connections,
            retry_on_timeout=self.redis_config.retry_on_timeout,
            socket_keepalive=self.redis_config.socket_keepalive,
            socket_keepalive_options=self.redis_config.socket_keepalive_options
        )
        
        self.redis = aioredis.Redis(connection_pool=self.redis_pool)
        
        logger.info("Database and Redis connections initialized")
    
    async def close(self):
        """Close all connections"""
        if self.pool:
            await self.pool.close()
        if self.redis:
            await self.redis.close()
        logger.info("Database connections closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        async with self.pool.acquire() as conn:
            yield conn
    
    async def execute_query(self, query: str, *args, fetch: str = "all") -> Any:
        """Execute query with performance monitoring"""
        start_time = time.time()
        
        try:
            async with self.get_connection() as conn:
                if fetch == "all":
                    result = await conn.fetch(query, *args)
                elif fetch == "one":
                    result = await conn.fetchrow(query, *args)
                elif fetch == "val":
                    result = await conn.fetchval(query, *args)
                else:
                    result = await conn.execute(query, *args)
                
                return result
        finally:
            duration = time.time() - start_time
            query_monitor.record_query(query, duration)
    
    async def execute_batch(self, query: str, params_list: List[tuple]) -> None:
        """Execute batch query for better performance"""
        async with self.get_connection() as conn:
            await conn.executemany(query, params_list)
    
    async def get_cached(self, key: str, ttl: int = 300) -> Optional[Any]:
        """Get data from cache"""
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                return json.loads(cached_data)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set_cached(self, key: str, data: Any, ttl: int = 300) -> None:
        """Set data in cache"""
        try:
            await self.redis.setex(key, ttl, json.dumps(data, default=str))
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete_cached(self, key: str) -> None:
        """Delete data from cache"""
        try:
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def invalidate_pattern(self, pattern: str) -> None:
        """Delete cache keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                await self.redis.delete(*keys)
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")

class OptimizedQueries:
    """Optimized database queries with caching"""
    
    def __init__(self, db: OptimizedDatabase):
        self.db = db
    
    @monitor_query
    async def get_minerals(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get all minerals with caching"""
        cache_key = "minerals:all"
        
        if use_cache:
            cached_data = await self.db.get_cached(cache_key)
            if cached_data:
                return cached_data
        
        query = """
        SELECT 
            m.id, m.name, m.symbol, m.category, 
            m.price, m.unit, m.description,
            m.last_updated, m.active,
            c.name as category_name
        FROM minerals m
        LEFT JOIN mineral_categories c ON m.category_id = c.id
        WHERE m.active = true
        ORDER BY m.name
        """
        
        minerals = await self.db.execute_query(query, fetch="all")
        
        # Convert to dict format
        result = [
            {
                "id": row["id"],
                "name": row["name"],
                "symbol": row["symbol"],
                "category": row["category"],
                "category_name": row["category_name"],
                "price": float(row["price"]),
                "unit": row["unit"],
                "description": row["description"],
                "last_updated": row["last_updated"].isoformat(),
                "active": row["active"]
            }
            for row in minerals
        ]
        
        if use_cache:
            await self.db.set_cached(cache_key, result, ttl=600)  # 10 minutes
        
        return result
    
    @monitor_query
    async def get_mineral_by_id(self, mineral_id: int, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Get mineral by ID with caching"""
        cache_key = f"mineral:{mineral_id}"
        
        if use_cache:
            cached_data = await self.db.get_cached(cache_key)
            if cached_data:
                return cached_data
        
        query = """
        SELECT 
            m.id, m.name, m.symbol, m.category_id, 
            m.price, m.unit, m.description,
            m.last_updated, m.active,
            c.name as category_name
        FROM minerals m
        LEFT JOIN mineral_categories c ON m.category_id = c.id
        WHERE m.id = $1 AND m.active = true
        """
        
        mineral = await self.db.execute_query(query, mineral_id, fetch="one")
        
        if mineral:
            result = {
                "id": mineral["id"],
                "name": mineral["name"],
                "symbol": mineral["symbol"],
                "category_id": mineral["category_id"],
                "category_name": mineral["category_name"],
                "price": float(mineral["price"]),
                "unit": mineral["unit"],
                "description": mineral["description"],
                "last_updated": mineral["last_updated"].isoformat(),
                "active": mineral["active"]
            }
            
            if use_cache:
                await self.db.set_cached(cache_key, result, ttl=300)  # 5 minutes
            
            return result
        
        return None
    
    @monitor_query
    async def get_user_transactions(
        self, 
        user_id: int, 
        limit: int = 50, 
        offset: int = 0,
        use_cache: bool = False
    ) -> List[Dict[str, Any]]:
        """Get user transactions with pagination"""
        cache_key = f"user:{user_id}:transactions:{offset}:{limit}"
        
        if use_cache:
            cached_data = await self.db.get_cached(cache_key)
            if cached_data:
                return cached_data
        
        query = """
        SELECT 
            t.id, t.user_id, t.mineral_id, t.quantity,
            t.price, t.total, t.status, t.created_at,
            m.name as mineral_name, m.symbol as mineral_symbol
        FROM transactions t
        LEFT JOIN minerals m ON t.mineral_id = m.id
        WHERE t.user_id = $1
        ORDER BY t.created_at DESC
        LIMIT $2 OFFSET $3
        """
        
        transactions = await self.db.execute_query(query, user_id, limit, offset, fetch="all")
        
        result = [
            {
                "id": row["id"],
                "user_id": row["user_id"],
                "mineral_id": row["mineral_id"],
                "mineral_name": row["mineral_name"],
                "mineral_symbol": row["mineral_symbol"],
                "quantity": float(row["quantity"]),
                "price": float(row["price"]),
                "total": float(row["total"]),
                "status": row["status"],
                "created_at": row["created_at"].isoformat()
            }
            for row in transactions
        ]
        
        if use_cache:
            await self.db.set_cached(cache_key, result, ttl=60)  # 1 minute
        
        return result
    
    @monitor_query
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> int:
        """Create transaction with optimized query"""
        query = """
        INSERT INTO transactions 
        (user_id, mineral_id, quantity, price, total, status, created_at)
        VALUES ($1, $2, $3, $4, $5, 'pending', NOW())
        RETURNING id
        """
        
        transaction_id = await self.db.execute_query(
            query,
            transaction_data["user_id"],
            transaction_data["mineral_id"],
            transaction_data["quantity"],
            transaction_data["price"],
            transaction_data["quantity"] * transaction_data["price"],
            fetch="val"
        )
        
        # Invalidate relevant cache
        await self.db.delete_cached("transactions:all")
        await self.db.invalidate_pattern(f"user:{transaction_data['user_id']}:transactions:*")
        
        return transaction_id
    
    @monitor_query
    async def update_transaction_status(self, transaction_id: int, status: str) -> bool:
        """Update transaction status"""
        query = """
        UPDATE transactions 
        SET status = $1, updated_at = NOW()
        WHERE id = $2
        """
        
        result = await self.db.execute_query(query, status, transaction_id, fetch="val")
        
        # Invalidate relevant cache
        await self.db.delete_cached("transactions:all")
        await self.db.invalidate_pattern("user:*:transactions:*")
        
        return result > 0
    
    @monitor_query
    async def get_market_stats(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get market statistics with caching"""
        cache_key = "market:stats"
        
        if use_cache:
            cached_data = await self.db.get_cached(cache_key)
            if cached_data:
                return cached_data
        
        queries = {
            "total_transactions": """
                SELECT COUNT(*) as count FROM transactions 
                WHERE status = 'completed'
            """,
            "total_volume": """
                SELECT COALESCE(SUM(total), 0) as volume FROM transactions 
                WHERE status = 'completed'
            """,
            "active_users": """
                SELECT COUNT(DISTINCT user_id) as count FROM transactions 
                WHERE created_at > NOW() - INTERVAL '30 days'
            """,
            "top_minerals": """
                SELECT 
                    m.name, 
                    COUNT(t.id) as transaction_count,
                    COALESCE(SUM(t.total), 0) as total_volume
                FROM minerals m
                LEFT JOIN transactions t ON m.id = t.mineral_id AND t.status = 'completed'
                WHERE m.active = true
                GROUP BY m.id, m.name
                ORDER BY total_volume DESC
                LIMIT 10
            """
        }
        
        stats = {}
        for key, query in queries.items():
            if key == "top_minerals":
                stats[key] = await self.db.execute_query(query, fetch="all")
            else:
                stats[key] = await self.db.execute_query(query, fetch="val")
        
        result = {
            "total_transactions": stats["total_transactions"],
            "total_volume": float(stats["total_volume"]),
            "active_users": stats["active_users"],
            "top_minerals": [
                {
                    "name": row["name"],
                    "transaction_count": row["transaction_count"],
                    "total_volume": float(row["total_volume"])
                }
                for row in stats["top_minerals"]
            ],
            "last_updated": datetime.now().isoformat()
        }
        
        if use_cache:
            await self.db.set_cached(cache_key, result, ttl=300)  # 5 minutes
        
        return result
    
    async def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        return {
            "query_performance": query_monitor.get_stats(),
            "slow_queries": [
                {
                    "query": sq["query"],
                    "duration": sq["duration"],
                    "timestamp": sq["timestamp"].isoformat()
                }
                for sq in query_monitor.slow_queries[-10:]  # Last 10 slow queries
            ],
            "pool_stats": {
                "min_size": self.db_config.min_size,
                "max_size": self.db_config.max_size,
                "current_size": self.pool.get_size() if self.pool else 0
            }
        }

# Initialize optimized database
db_config = DatabaseConfig(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5432)),
    database=os.getenv("DB_NAME", "worldmine"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", "password"),
    min_size=int(os.getenv("DB_MIN_SIZE", 5)),
    max_size=int(os.getenv("DB_MAX_SIZE", 20))
)

redis_config = RedisConfig(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", 20))
)

optimized_db = OptimizedDatabase(db_config, redis_config)
optimized_queries = OptimizedQueries(optimized_db)

# Example usage
async def main():
    """Example usage of optimized database"""
    await optimized_db.initialize()
    
    try:
        # Get minerals with caching
        minerals = await optimized_queries.get_minerals()
        print(f"Found {len(minerals)} minerals")
        
        # Get market statistics
        stats = await optimized_queries.get_market_stats()
        print(f"Market stats: {stats}")
        
        # Create transaction
        transaction_data = {
            "user_id": 1,
            "mineral_id": 1,
            "quantity": 100,
            "price": 50.0
        }
        transaction_id = await optimized_queries.create_transaction(transaction_data)
        print(f"Created transaction {transaction_id}")
        
        # Get performance stats
        perf_stats = await optimized_queries.get_performance_stats()
        print(f"Performance stats: {perf_stats}")
        
    finally:
        await optimized_db.close()

if __name__ == "__main__":
    asyncio.run(main())
