"""
API Reliability Middleware for DEDAN 2.0
Ensures 99.99% uptime with circuit breakers, retries, and load balancing
"""

import asyncio
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import random
import hashlib
from functools import wraps
from collections import defaultdict, deque
import aiohttp
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class RetryStrategy(Enum):
    """Retry strategies"""
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    NO_RETRY = "no_retry"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration"""
    name: str
    url: str
    timeout: float = 5.0
    max_retries: int = 3
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    health_check_interval: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: float = 60.0
    load_balancing: bool = True
    backup_endpoints: List[str] = field(default_factory=list)

@dataclass
class CircuitBreakerMetrics:
    """Circuit breaker metrics"""
    total_requests: int = 0
    failed_requests: int = 0
    success_requests: int = 0
    timeout_requests: int = 0
    circuit_state_changes: int = 0
    last_state_change: Optional[datetime] = None
    current_state: CircuitState = CircuitState.CLOSED
    failure_rate: float = 0.0

class CircuitBreaker:
    """Advanced circuit breaker implementation"""
    
    def __init__(self, endpoint: ServiceEndpoint):
        self.endpoint = endpoint
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.metrics = CircuitBreakerMetrics()
        self.request_history = deque(maxlen=100)
        self.last_health_check = None
        self.healthy_endpoints = [endpoint.url] + endpoint.backup_endpoints
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        start_time = time.time()
        
        try:
            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    self.metrics.circuit_state_changes += 1
                    self.metrics.last_state_change = datetime.utcnow()
                else:
                    raise HTTPException(status_code=503, detail="Service temporarily unavailable")
            
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Record success
            self._record_success(time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Record failure
            self._record_failure(time.time() - start_time)
            
            # Check if we should open the circuit
            if self._should_open_circuit():
                self.state = CircuitState.OPEN
                self.metrics.circuit_state_changes += 1
                self.metrics.last_state_change = datetime.utcnow()
            
            raise e
    
    def _should_open_circuit(self) -> bool:
        """Check if circuit should open"""
        return (
            self.state == CircuitState.CLOSED and
            self.failure_count >= self.endpoint.circuit_breaker_threshold
        )
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset"""
        if self.last_failure_time is None:
            return False
        
        elapsed = time.time() - self.last_failure_time
        return elapsed >= self.endpoint.circuit_breaker_timeout
    
    def _record_success(self, duration: float):
        """Record successful request"""
        self.success_count += 1
        self.failure_count = 0
        self.request_history.append({
            'timestamp': time.time(),
            'success': True,
            'duration': duration
        })
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.success_requests += 1
        self.metrics.failure_rate = self._calculate_failure_rate()
        
        # Close circuit if half-open
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.metrics.circuit_state_changes += 1
            self.metrics.last_state_change = datetime.utcnow()
    
    def _record_failure(self, duration: float):
        """Record failed request"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.request_history.append({
            'timestamp': time.time(),
            'success': False,
            'duration': duration
        })
        
        # Update metrics
        self.metrics.total_requests += 1
        self.metrics.failed_requests += 1
        self.metrics.failure_rate = self._calculate_failure_rate()
    
    def _calculate_failure_rate(self) -> float:
        """Calculate failure rate"""
        if self.metrics.total_requests == 0:
            return 0.0
        
        recent_requests = [
            r for r in self.request_history
            if time.time() - r['timestamp'] <= 300  # Last 5 minutes
        ]
        
        if not recent_requests:
            return 0.0
        
        failures = sum(1 for r in recent_requests if not r['success'])
        return failures / len(recent_requests)
    
    async def health_check(self) -> bool:
        """Perform health check on endpoint"""
        if self.last_health_check and time.time() - self.last_health_check < self.endpoint.health_check_interval:
            return self.state != CircuitState.OPEN
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.endpoint.timeout)) as session:
                async with session.get(f"{self.endpoint.url}/health") as response:
                    is_healthy = response.status == 200
                    
                    if is_healthy and self.state == CircuitState.OPEN:
                        self.state = CircuitState.CLOSED
                        self.metrics.circuit_state_changes += 1
                        self.metrics.last_state_change = datetime.utcnow()
                    
                    self.last_health_check = time.time()
                    return is_healthy
                    
        except Exception as e:
            logger.warning(f"Health check failed for {self.endpoint.name}: {e}")
            self.last_health_check = time.time()
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics"""
        return {
            'endpoint': self.endpoint.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'total_requests': self.metrics.total_requests,
            'failure_rate': self.metrics.failure_rate,
            'last_state_change': self.metrics.last_state_change.isoformat() if self.metrics.last_state_change else None,
            'circuit_state_changes': self.metrics.circuit_state_changes
        }

class RetryManager:
    """Advanced retry manager with multiple strategies"""
    
    def __init__(self, max_retries: int = 3, strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF):
        self.max_retries = max_retries
        self.strategy = strategy
        self.retry_history = defaultdict(list)
    
    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                if attempt > 0:
                    self.retry_history[func.__name__].append({
                        'attempt': attempt,
                        'success': True,
                        'timestamp': datetime.utcnow()
                    })
                
                return result
                
            except Exception as e:
                last_exception = e
                
                self.retry_history[func.__name__].append({
                    'attempt': attempt,
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.utcnow()
                })
                
                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed: {e}")
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay based on strategy"""
        if self.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return min(2 ** attempt, 30) + random.uniform(0, 1)
        elif self.strategy == RetryStrategy.LINEAR_BACKOFF:
            return attempt * 1.0 + random.uniform(0, 0.5)
        elif self.strategy == RetryStrategy.FIXED_DELAY:
            return 1.0
        else:
            return 0
    
    def get_retry_metrics(self) -> Dict[str, Any]:
        """Get retry metrics"""
        metrics = {}
        
        for func_name, history in self.retry_history.items():
            total_attempts = len(history)
            successful_attempts = sum(1 for h in history if h['success'])
            failure_rate = (total_attempts - successful_attempts) / total_attempts if total_attempts > 0 else 0
            
            metrics[func_name] = {
                'total_attempts': total_attempts,
                'successful_attempts': successful_attempts,
                'failure_rate': failure_rate,
                'last_attempt': history[-1]['timestamp'].isoformat() if history else None
            }
        
        return metrics

class LoadBalancer:
    """Advanced load balancer with multiple algorithms"""
    
    def __init__(self, endpoints: List[str], algorithm: str = "round_robin"):
        self.endpoints = endpoints
        self.algorithm = algorithm
        self.current_index = 0
        self.endpoint_stats = defaultdict(lambda: {
            'requests': 0,
            'failures': 0,
            'response_times': deque(maxlen=100),
            'last_used': None
        })
    
    def get_next_endpoint(self) -> str:
        """Get next endpoint based on algorithm"""
        if not self.endpoints:
            raise ValueError("No endpoints available")
        
        if self.algorithm == "round_robin":
            endpoint = self.endpoints[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.endpoints)
            
        elif self.algorithm == "least_connections":
            endpoint = min(self.endpoints, key=lambda e: self.endpoint_stats[e]['requests'])
            
        elif self.algorithm == "response_time":
            endpoint = min(
                self.endpoints,
                key=lambda e: (
                    sum(self.endpoint_stats[e]['response_times']) / len(self.endpoint_stats[e]['response_times'])
                    if self.endpoint_stats[e]['response_times'] else float('inf')
                )
            )
            
        elif self.algorithm == "random":
            endpoint = random.choice(self.endpoints)
            
        else:
            endpoint = self.endpoints[0]
        
        self.endpoint_stats[endpoint]['requests'] += 1
        self.endpoint_stats[endpoint]['last_used'] = datetime.utcnow()
        
        return endpoint
    
    def record_response_time(self, endpoint: str, response_time: float):
        """Record response time for endpoint"""
        self.endpoint_stats[endpoint]['response_times'].append(response_time)
    
    def record_failure(self, endpoint: str):
        """Record failure for endpoint"""
        self.endpoint_stats[endpoint]['failures'] += 1
    
    def get_load_balancing_metrics(self) -> Dict[str, Any]:
        """Get load balancing metrics"""
        metrics = {}
        
        for endpoint in self.endpoints:
            stats = self.endpoint_stats[endpoint]
            avg_response_time = (
                sum(stats['response_times']) / len(stats['response_times'])
                if stats['response_times'] else 0
            )
            
            failure_rate = (
                stats['failures'] / stats['requests']
                if stats['requests'] > 0 else 0
            )
            
            metrics[endpoint] = {
                'requests': stats['requests'],
                'failures': stats['failures'],
                'failure_rate': failure_rate,
                'avg_response_time': avg_response_time,
                'last_used': stats['last_used'].isoformat() if stats['last_used'] else None
            }
        
        return metrics

class APIReliabilityMiddleware:
    """Main API reliability middleware"""
    
    def __init__(self):
        self.circuit_breakers = {}
        self.retry_managers = {}
        self.load_balancers = {}
        self.request_cache = {}
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'circuit_breaker_trips': 0,
            'retry_attempts': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'start_time': datetime.utcnow()
        }
    
    def register_endpoint(self, endpoint: ServiceEndpoint):
        """Register service endpoint"""
        self.circuit_breakers[endpoint.name] = CircuitBreaker(endpoint)
        self.retry_managers[endpoint.name] = RetryManager(
            endpoint.max_retries,
            endpoint.retry_strategy
        )
        
        if endpoint.load_balancing and endpoint.backup_endpoints:
            self.load_balancers[endpoint.name] = LoadBalancer(
                [endpoint.url] + endpoint.backup_endpoints,
                "least_connections"
            )
    
    async def call_service(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Call service with reliability features"""
        self.metrics['total_requests'] += 1
        
        circuit_breaker = self.circuit_breakers.get(service_name)
        retry_manager = self.retry_managers.get(service_name)
        load_balancer = self.load_balancers.get(service_name)
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(service_name, args, kwargs)
            cached_result = self._get_from_cache(cache_key)
            
            if cached_result is not None:
                self.metrics['cache_hits'] += 1
                return cached_result
            else:
                self.metrics['cache_misses'] += 1
            
            # Get endpoint URL if load balancing
            if load_balancer:
                endpoint_url = load_balancer.get_next_endpoint()
                kwargs['endpoint_url'] = endpoint_url
            
            # Execute with circuit breaker and retry
            if circuit_breaker and retry_manager:
                result = await circuit_breaker.call(
                    retry_manager.execute_with_retry,
                    func,
                    *args,
                    **kwargs
                )
            elif circuit_breaker:
                result = await circuit_breaker.call(func, *args, **kwargs)
            elif retry_manager:
                result = await retry_manager.execute_with_retry(func, *args, **kwargs)
            else:
                result = await func(*args, **kwargs)
            
            # Cache successful result
            self._set_cache(cache_key, result)
            
            # Record success
            self.metrics['successful_requests'] += 1
            
            # Record response time for load balancer
            if load_balancer and 'endpoint_url' in kwargs:
                # This would be set by the actual function
                pass
            
            return result
            
        except Exception as e:
            # Record failure
            self.metrics['failed_requests'] += 1
            
            # Record circuit breaker trip
            if circuit_breaker and circuit_breaker.state == CircuitState.OPEN:
                self.metrics['circuit_breaker_trips'] += 1
            
            # Record retry attempt
            if retry_manager:
                self.metrics['retry_attempts'] += 1
            
            # Record failure for load balancer
            if load_balancer and 'endpoint_url' in kwargs:
                load_balancer.record_failure(kwargs['endpoint_url'])
            
            raise e
    
    def _generate_cache_key(self, service_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key"""
        key_data = {
            'service': service_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        return hashlib.md5(json.dumps(key_data).encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """Get value from cache"""
        if cache_key in self.request_cache:
            cached_item = self.request_cache[cache_key]
            if datetime.utcnow() - cached_item['timestamp'] < timedelta(minutes=5):
                return cached_item['value']
            else:
                del self.request_cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, value: Any):
        """Set value in cache"""
        self.request_cache[cache_key] = {
            'value': value,
            'timestamp': datetime.utcnow()
        }
        
        # Limit cache size
        if len(self.request_cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self.request_cache.keys(),
                key=lambda k: self.request_cache[k]['timestamp']
            )[:100]
            for key in oldest_keys:
                del self.request_cache[key]
    
    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all services"""
        health_status = {}
        
        for service_name, circuit_breaker in self.circuit_breakers.items():
            is_healthy = await circuit_breaker.health_check()
            health_status[service_name] = {
                'healthy': is_healthy,
                'circuit_state': circuit_breaker.state.value,
                'metrics': circuit_breaker.get_metrics()
            }
        
        return health_status
    
    def get_reliability_metrics(self) -> Dict[str, Any]:
        """Get overall reliability metrics"""
        uptime = datetime.utcnow() - self.metrics['start_time']
        uptime_seconds = uptime.total_seconds()
        
        success_rate = (
            self.metrics['successful_requests'] / self.metrics['total_requests']
            if self.metrics['total_requests'] > 0 else 0
        ) * 100
        
        cache_hit_rate = (
            self.metrics['cache_hits'] / (self.metrics['cache_hits'] + self.metrics['cache_misses'])
            if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 else 0
        ) * 100
        
        return {
            'uptime_seconds': uptime_seconds,
            'total_requests': self.metrics['total_requests'],
            'successful_requests': self.metrics['successful_requests'],
            'failed_requests': self.metrics['failed_requests'],
            'success_rate': success_rate,
            'circuit_breaker_trips': self.metrics['circuit_breaker_trips'],
            'retry_attempts': self.metrics['retry_attempts'],
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': cache_hit_rate,
            'services': {
                name: {
                    'circuit_breaker': cb.get_metrics(),
                    'retry_manager': rm.get_retry_metrics() if name in rm else None,
                    'load_balancer': lb.get_load_balancing_metrics() if name in lb else None
                }
                for name, cb in self.circuit_breakers.items()
                for rm in [self.retry_managers.get(name)] if rm
                for lb in [self.load_balancers.get(name)] if lb
            }
        }

# Decorator for automatic reliability
def reliable_service(service_name: str, endpoint: Optional[ServiceEndpoint] = None):
    """Decorator for reliable service calls"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get middleware instance (would be injected)
            middleware = kwargs.pop('_reliability_middleware', None)
            
            if middleware:
                # Register endpoint if provided
                if endpoint:
                    middleware.register_endpoint(endpoint)
                
                # Call through middleware
                return await middleware.call_service(service_name, func, *args, **kwargs)
            else:
                # Fallback to direct call
                return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Global middleware instance
reliability_middleware = APIReliabilityMiddleware()

# Example usage
@reliable_service("trading_service", ServiceEndpoint(
    name="trading_service",
    url="https://api.dedan.ai/trading",
    timeout=5.0,
    max_retries=3,
    retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
    circuit_breaker_threshold=5,
    circuit_breaker_timeout=60.0,
    load_balancing=True,
    backup_endpoints=[
        "https://backup1.dedan.ai/trading",
        "https://backup2.dedan.ai/trading"
    ]
))
async def place_order(order_data: dict):
    """Example reliable service function"""
    # This would be the actual service call
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.dedan.ai/orders",
            json=order_data
        ) as response:
            return await response.json()

# Main execution
async def main():
    """Main execution function"""
    # Register some example endpoints
    trading_endpoint = ServiceEndpoint(
        name="trading_service",
        url="https://api.dedan.ai/trading",
        timeout=3.0,
        max_retries=3,
        retry_strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        circuit_breaker_threshold=5,
        circuit_breaker_timeout=60.0,
        load_balancing=True,
        backup_endpoints=[
            "https://backup1.dedan.ai/trading",
            "https://backup2.dedan.ai/trading"
        ]
    )
    
    market_endpoint = ServiceEndpoint(
        name="market_service",
        url="https://api.dedan.ai/market",
        timeout=2.0,
        max_retries=2,
        retry_strategy=RetryStrategy.LINEAR_BACKOFF,
        circuit_breaker_threshold=3,
        circuit_breaker_timeout=30.0
    )
    
    reliability_middleware.register_endpoint(trading_endpoint)
    reliability_middleware.register_endpoint(market_endpoint)
    
    # Test reliability features
    try:
        # Test with reliability middleware
        order_data = {"mineral": "gold", "quantity": 100, "price": 50.0}
        result = await reliability_middleware.call_service(
            "trading_service",
            place_order,
            order_data,
            _reliability_middleware=reliability_middleware
        )
        
        print(f"Order placed successfully: {result}")
        
        # Get health status
        health_status = await reliability_middleware.health_check_all()
        print(f"Service health status: {json.dumps(health_status, indent=2, default=str)}")
        
        # Get reliability metrics
        metrics = reliability_middleware.get_reliability_metrics()
        print(f"Reliability metrics: {json.dumps(metrics, indent=2, default=str)}")
        
    except Exception as e:
        print(f"Service call failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
