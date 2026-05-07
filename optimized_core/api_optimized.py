"""
OPTIMIZED API LAYER - DEDAN WORLDMINE
High-performance, cached, rate-limited API endpoints

Optimizations:
- Connection pooling
- Request caching
- Rate limiting
- Response compression
- Background processing
- Error handling
- Performance monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import asyncio
import aioredis
import asyncpg
from typing import Dict, List, Any, Optional
import logging
import time
import json
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import gzip
import pickle
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# Performance monitoring
class APIPerformanceMonitor:
    def __init__(self):
        self.request_stats = {}
        self.error_rates = {}
        self.response_times = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0
        }
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        if endpoint not in self.request_stats:
            self.request_stats[endpoint] = {
                "count": 0,
                "total_time": 0,
                "errors": 0,
                "avg_time": 0
            }
        
        stats = self.request_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        
        if status_code >= 400:
            stats["errors"] += 1
        
        # Keep only last 1000 requests per endpoint
        if stats["count"] > 1000:
            stats["count"] = 1000
    
    def record_cache_hit(self):
        self.cache_stats["hits"] += 1
    
    def record_cache_miss(self):
        self.cache_stats["misses"] += 1
    
    def record_cache_set(self):
        self.cache_stats["sets"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        total_requests = sum(stats["count"] for stats in self.request_stats.values())
        total_errors = sum(stats["errors"] for stats in self.request_stats.values())
        
        return {
            "total_requests": total_requests,
            "total_errors": total_errors,
            "error_rate": total_errors / total_requests if total_requests > 0 else 0,
            "cache_hit_rate": (
                self.cache_stats["hits"] / 
                (self.cache_stats["hits"] + self.cache_stats["misses"])
                if (self.cache_stats["hits"] + self.cache_stats["misses"]) > 0 else 0
            ),
            "endpoints": self.request_stats,
            "cache_stats": self.cache_stats
        }

api_monitor = APIPerformanceMonitor()

# Advanced caching
class AdvancedCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_pool = None
        self.redis = None
        self.default_ttl = 300  # 5 minutes
    
    async def initialize(self):
        """Initialize Redis connection pool"""
        self.redis_pool = aioredis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=20,
            retry_on_timeout=True
        )
        self.redis = aioredis.Redis(connection_pool=self.redis_pool)
    
    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached data"""
        try:
            cached = await self.redis.get(key)
            if cached:
                api_monitor.record_cache_hit()
                return pickle.loads(cached)
            api_monitor.record_cache_miss()
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, data: Any, ttl: int = None) -> bool:
        """Set cached data"""
        try:
            serialized = pickle.dumps(data)
            await self.redis.setex(key, ttl or self.default_ttl, serialized)
            api_monitor.record_cache_set()
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached data"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache pattern delete error: {e}")
            return 0

# Initialize cache
cache = AdvancedCache()

# Performance decorator
def monitor_performance(func):
    """Monitor API endpoint performance"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = func.__name__
        
        try:
            result = await func(*args, **kwargs)
            status_code = getattr(result, 'status_code', 200)
            return result
        except HTTPException as e:
            status_code = e.status_code
            raise
        except Exception as e:
            status_code = 500
            logger.error(f"API error in {endpoint}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
        finally:
            response_time = time.time() - start_time
            api_monitor.record_request(endpoint, status_code, response_time)
    
    return wrapper

# Cache decorator
def cached(ttl: int = 300, key_prefix: str = None):
    """Cache API response"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_cache_key(
                key_prefix or func.__name__,
                args,
                kwargs
            )
            
            # Try cache first
            cached_result = await cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result (only for successful responses)
            if hasattr(result, 'status_code') and result.status_code == 200:
                await cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Background task processor
class BackgroundTaskProcessor:
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.processing = False
    
    async def add_task(self, task_func: callable, *args, **kwargs):
        """Add task to background queue"""
        await self.task_queue.put((task_func, args, kwargs))
    
    async def process_tasks(self):
        """Process background tasks"""
        if self.processing:
            return
        
        self.processing = True
        while True:
            try:
                task_func, args, kwargs = await asyncio.wait_for(
                    self.task_queue.get(), 
                    timeout=1.0
                )
                
                # Execute task in background
                asyncio.create_task(task_func(*args, **kwargs))
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Background task error: {e}")

background_processor = BackgroundTaskProcessor()

# Optimized FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup
    await cache.initialize()
    asyncio.create_task(background_processor.process_tasks())
    logger.info("Optimized API started")
    
    yield
    
    # Shutdown
    logger.info("Optimized API shutting down")

app = FastAPI(
    title="DEDAN WORLDMINE - Optimized API",
    description="High-performance mining and mineral transaction API",
    version="2035.0.0-optimized",
    lifespan=lifespan
)

# Optimized middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Rate limiting
app.state.limiter = FastAPILimiter(redis=cache.redis)

# Error handlers
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Optimized endpoints
@app.get("/api/v1/minerals")
@monitor_performance
@cached(ttl=600, key_prefix="minerals")
@limiter.limit("100/minute")
async def get_minerals():
    """Get all minerals with caching and rate limiting"""
    # This would normally query the database
    # For now, return mock data
    minerals = [
        {
            "id": 1,
            "name": "Gold",
            "symbol": "AU",
            "category": "Precious Metals",
            "price": 1950.50,
            "unit": "oz",
            "last_updated": datetime.now().isoformat()
        },
        {
            "id": 2,
            "name": "Silver",
            "symbol": "AG",
            "category": "Precious Metals",
            "price": 24.75,
            "unit": "oz",
            "last_updated": datetime.now().isoformat()
        }
    ]
    
    return JSONResponse(
        status_code=200,
        content={"minerals": minerals}
    )

@app.get("/api/v1/minerals/{mineral_id}")
@monitor_performance
@cached(ttl=300, key_prefix="mineral")
@limiter.limit("200/minute")
async def get_mineral(mineral_id: int):
    """Get mineral by ID with caching"""
    # Mock data - would normally query database
    mineral = {
        "id": mineral_id,
        "name": f"Mineral {mineral_id}",
        "symbol": f"M{mineral_id}",
        "category": "Industrial",
        "price": 100.0 + mineral_id * 10,
        "unit": "kg",
        "last_updated": datetime.now().isoformat()
    }
    
    return JSONResponse(
        status_code=200,
        content={"mineral": mineral}
    )

@app.post("/api/v1/transactions")
@monitor_performance
@limiter.limit("50/minute")
async def create_transaction(
    transaction_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Create transaction with background processing"""
    # Validate transaction data
    required_fields = ["user_id", "mineral_id", "quantity", "price"]
    for field in required_fields:
        if field not in transaction_data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required field: {field}"
            )
    
    # Calculate total
    total = transaction_data["quantity"] * transaction_data["price"]
    
    # Create transaction record
    transaction = {
        "id": int(time.time() * 1000),  # Mock ID
        "user_id": transaction_data["user_id"],
        "mineral_id": transaction_data["mineral_id"],
        "quantity": transaction_data["quantity"],
        "price": transaction_data["price"],
        "total": total,
        "status": "pending",
        "created_at": datetime.now().isoformat()
    }
    
    # Add background processing
    background_tasks.add_task(
        process_transaction_background,
        transaction["id"]
    )
    
    # Invalidate relevant cache
    await cache.delete_pattern("minerals:*")
    await cache.delete_pattern("transactions:*")
    
    return JSONResponse(
        status_code=201,
        content={"transaction": transaction}
    )

@app.get("/api/v1/transactions")
@monitor_performance
@cached(ttl=60, key_prefix="transactions")
@limiter.limit("100/minute")
async def get_transactions(
    user_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get transactions with pagination and caching"""
    # Mock data - would normally query database
    transactions = [
        {
            "id": i,
            "user_id": user_id or 1,
            "mineral_id": 1,
            "quantity": 100.0,
            "price": 1950.50,
            "total": 195050.0,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }
        for i in range(1, min(limit + 1, 11))
    ]
    
    return JSONResponse(
        status_code=200,
        content={
            "transactions": transactions,
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(transactions)
            }
        }
    )

@app.get("/api/v1/market/stats")
@monitor_performance
@cached(ttl=300, key_prefix="market_stats")
@limiter.limit("30/minute")
async def get_market_stats():
    """Get market statistics with caching"""
    # Mock data - would normally aggregate from database
    stats = {
        "total_transactions": 1000000,
        "total_volume": 5000000000.0,
        "active_users": 50000,
        "top_minerals": [
            {
                "name": "Gold",
                "volume": 2000000000.0,
                "transactions": 500000
            },
            {
                "name": "Silver",
                "volume": 1500000000.0,
                "transactions": 300000
            }
        ],
        "last_updated": datetime.now().isoformat()
    }
    
    return JSONResponse(
        status_code=200,
        content={"stats": stats}
    )

@app.get("/api/v1/performance")
@monitor_performance
@limiter.limit("10/minute")
async def get_performance_stats():
    """Get API performance statistics"""
    return JSONResponse(
        status_code=200,
        content={"performance": api_monitor.get_stats()}
    )

# Background processing function
async def process_transaction_background(transaction_id: int):
    """Process transaction in background"""
    try:
        # Simulate processing
        await asyncio.sleep(2)
        
        # Update transaction status
        logger.info(f"Transaction {transaction_id} processed successfully")
        
        # Invalidate cache
        await cache.delete_pattern("transactions:*")
        
    except Exception as e:
        logger.error(f"Background processing error: {e}")

# Health check
@app.get("/health")
@monitor_performance
async def health_check():
    """Health check with performance metrics"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "performance": api_monitor.get_stats()
        }
    )

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api_optimized:app",
        host="0.0.0.0",
        port=8000,
        workers=4,
        loop="uvloop",
        http="httptools"
    )
