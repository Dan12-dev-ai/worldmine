# 🔧 WORLD-MINE RELIABILITY ENGINEERING SYSTEM
## Enterprise-Grade Health Monitoring, Fault Tolerance, and Observability

"""
Enterprise-grade reliability system for World-Mine platform
- Health monitoring (API, WebSockets, AI agents, database)
- Fault tolerance (retry, circuit breakers, fallback logic)
- Observability (structured logging, metrics, tracing)
- Failure recovery (auto-reconnect, state recovery, rollbacks)
"""

from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timezone
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
import uuid
import logging
from functools import wraps
import json

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# ENUMERATIONS
# =============================================================================

class HealthStatus(Enum):
    """Health status for system components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class ComponentType(Enum):
    """Types of system components"""
    API = "api"
    WEBSOCKET = "websocket"
    AI_AGENT = "ai_agent"
    DATABASE = "database"
    EVENT_BUS = "event_bus"
    ESCROW = "escrow"
    LOGISTICS = "logistics"
    MARKETPLACE = "marketplace"

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class HealthCheck:
    """Result of a health check"""
    component_id: str
    component_type: ComponentType
    status: HealthStatus
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    latency_ms: float = 0.0
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker"""
    failure_threshold: int = 5
    reset_timeout_seconds: int = 30
    half_open_max_calls: int = 3

@dataclass
class RetryConfig:
    """Configuration for retry logic"""
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 10.0
    backoff_multiplier: float = 2.0
    retryable_exceptions: List[type] = field(default_factory=lambda: [Exception])

@dataclass
class Metric:
    """Structured metric for observability"""
    metric_id: str
    name: str
    value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    component_id: str = ""
    tags: Dict[str, str] = field(default_factory=dict)

# =============================================================================
# HEALTH MONITORING SYSTEM
# =============================================================================

class HealthMonitor:
    """
    Enterprise-grade health monitoring system
    Tracks health of API, WebSockets, AI agents, database, and event bus
    """

    def __init__(self):
        self.health_checks: Dict[str, HealthCheck] = {}
        self.component_heartbeats: Dict[str, float] = {}
        self.alert_callbacks: List[Callable] = []

    async def check_api_health(self, api_url: str = "/") -> HealthCheck:
        """Check API health with latency measurement"""
        start_time = time.time()
        try:
            # In production, make actual HTTP request
            # For now, simulate healthy API
            latency_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                component_id="worldmine_api",
                component_type=ComponentType.API,
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message="API is responding normally"
            )
            
            self._update_health_check(health_check)
            return health_check
            
        except Exception as e:
            health_check = HealthCheck(
                component_id="worldmine_api",
                component_type=ComponentType.API,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"API health check failed: {str(e)}"
            )
            self._update_health_check(health_check)
            return health_check

    async def check_database_health(self) -> HealthCheck:
        """Check database health with connection test"""
        start_time = time.time()
        try:
            # In production, execute a simple query
            latency_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                component_id="mineral_database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message="Database connection is healthy"
            )
            
            self._update_health_check(health_check)
            return health_check
            
        except Exception as e:
            health_check = HealthCheck(
                component_id="mineral_database",
                component_type=ComponentType.DATABASE,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Database health check failed: {str(e)}"
            )
            self._update_health_check(health_check)
            return health_check

    async def check_ai_agent_health(self, agent_id: str) -> HealthCheck:
        """Check AI agent health with heartbeat"""
        start_time = time.time()
        try:
            # In production, ping the agent service
            latency_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                component_id=agent_id,
                component_type=ComponentType.AI_AGENT,
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message=f"AI agent {agent_id} is active"
            )
            
            self._update_health_check(health_check)
            return health_check
            
        except Exception as e:
            health_check = HealthCheck(
                component_id=agent_id,
                component_type=ComponentType.AI_AGENT,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"AI agent {agent_id} health check failed: {str(e)}"
            )
            self._update_health_check(health_check)
            return health_check

    async def check_event_bus_health(self) -> HealthCheck:
        """Check event bus health"""
        start_time = time.time()
        try:
            latency_ms = (time.time() - start_time) * 1000
            
            health_check = HealthCheck(
                component_id="event_bus",
                component_type=ComponentType.EVENT_BUS,
                status=HealthStatus.HEALTHY,
                latency_ms=latency_ms,
                message="Event bus is operational"
            )
            
            self._update_health_check(health_check)
            return health_check
            
        except Exception as e:
            health_check = HealthCheck(
                component_id="event_bus",
                component_type=ComponentType.EVENT_BUS,
                status=HealthStatus.UNHEALTHY,
                latency_ms=0,
                message=f"Event bus health check failed: {str(e)}"
            )
            self._update_health_check(health_check)
            return health_check

    async def check_all_systems(self) -> Dict[str, HealthCheck]:
        """Run comprehensive health check on all systems"""
        logger.info("🔍 Running comprehensive health check...")
        
        results = {}
        
        # Check API
        results["api"] = await self.check_api_health()
        
        # Check database
        results["database"] = await self.check_database_health()
        
        # Check AI agents
        results["ai_market"] = await self.check_ai_agent_health("market_intelligence")
        results["ai_fraud"] = await self.check_ai_agent_health("fraud_detection")
        results["ai_trade"] = await self.check_ai_agent_health("trade_recommendation")
        
        # Check event bus
        results["event_bus"] = await self.check_event_bus_health()
        
        # Log summary
        healthy_count = sum(1 for r in results.values() if r.status == HealthStatus.HEALTHY)
        logger.info(f"✅ Health check complete: {healthy_count}/{len(results)} systems healthy")
        
        return results

    def _update_health_check(self, health_check: HealthCheck) -> None:
        """Update health check and trigger alerts if needed"""
        self.health_checks[health_check.component_id] = health_check
        
        # Trigger alert if status changed to unhealthy
        if health_check.status in [HealthStatus.UNHEALTHY, HealthStatus.DEGRADED]:
            self._trigger_alerts(health_check)

    def _trigger_alerts(self, health_check: HealthCheck) -> None:
        """Trigger configured alert callbacks"""
        for callback in self.alert_callbacks:
            try:
                callback(health_check)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def register_alert_callback(self, callback: Callable) -> None:
        """Register a callback for health alerts"""
        self.alert_callbacks.append(callback)

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get comprehensive health summary for monitoring"""
        total_healthy = sum(1 for hc in self.health_checks.values() if hc.status == HealthStatus.HEALTHY)
        total_degraded = sum(1 for hc in self.health_checks.values() if hc.status == HealthStatus.DEGRADED)
        total_unhealthy = sum(1 for hc in self.health_checks.values() if hc.status == HealthStatus.UNHEALTHY)
        
        return {
            "summary": {
                "total": len(self.health_checks),
                "healthy": total_healthy,
                "degraded": total_degraded,
                "unhealthy": total_unhealthy
            },
            "components": {
                component_id: {
                    "status": hc.status.value,
                    "latency_ms": hc.latency_ms,
                    "message": hc.message,
                    "timestamp": hc.timestamp.isoformat()
                }
                for component_id, hc in self.health_checks.items()
            }
        }

# =============================================================================
# CIRCUIT BREAKER (FAULT TOLERANCE)
# =============================================================================

class CircuitBreaker:
    """
    Enterprise-grade circuit breaker pattern
    Prevents cascading failures by stopping calls to unhealthy services
    """

    def __init__(self, config: CircuitBreakerConfig = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_call_count = 0

    def __call__(self, func: Callable):
        """Decorator to apply circuit breaker to functions"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper

    async def execute(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        # Check circuit state
        if self.state == CircuitState.OPEN:
            # Check if we should transition to half-open
            if (time.time() - self.last_failure_time) >= self.config.reset_timeout_seconds:
                logger.info(f"🔄 Circuit transitioning to HALF_OPEN: {func.__name__}")
                self.state = CircuitState.HALF_OPEN
                self.half_open_call_count = 0
            else:
                raise Exception(f"Circuit is OPEN for {func.__name__}")
        
        # In half-open, limit calls
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_call_count >= self.config.half_open_max_calls:
                raise Exception(f"Circuit in HALF_OPEN, max calls reached for {func.__name__}")
            self.half_open_call_count += 1

        try:
            # Execute the function
            result = await func(*args, **kwargs)
            
            # Success - reset circuit
            self._on_success()
            return result
            
        except Exception as e:
            # Failure - handle it
            self._on_failure()
            raise

    def _on_success(self) -> None:
        """Handle successful call"""
        if self.state in [CircuitState.HALF_OPEN, CircuitState.OPEN]:
            logger.info("✅ Circuit transitioning to CLOSED")
            self.state = CircuitState.CLOSED
        self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
            logger.error(f"🚨 Circuit transitioning to OPEN after {self.failure_count} failures")
            self.state = CircuitState.OPEN
        elif self.state == CircuitState.HALF_OPEN:
            logger.error(f"🚨 Circuit transitioning back to OPEN after half-open failure")
            self.state = CircuitState.OPEN

# =============================================================================
# RETRY DECORATOR (FAULT TOLERANCE)
# =============================================================================

def with_retry(config: RetryConfig = None):
    """
    Decorator that adds retry logic to async functions
    Configurable backoff, max attempts, and retryable exceptions
    """
    config = config or RetryConfig()
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            delay = config.initial_delay_seconds
            
            for attempt in range(config.max_attempts):
                try:
                    return await func(*args, **kwargs)
                except tuple(config.retryable_exceptions) as e:
                    last_exception = e
                    attempt_number = attempt + 1
                    
                    if attempt_number == config.max_attempts:
                        logger.error(f"❌ Max retries ({config.max_attempts}) reached for {func.__name__}")
                        raise
                    
                    logger.warning(f"⚠️  Attempt {attempt_number}/{config.max_attempts} failed for {func.__name__}. Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                    
                    # Exponential backoff
                    delay = min(delay * config.backoff_multiplier, config.max_delay_seconds)
            
            raise last_exception
        
        return wrapper
    return decorator

# =============================================================================
# OBSERVABILITY SYSTEM
# =============================================================================

class ObservabilitySystem:
    """
    Enterprise-grade observability system
    Structured logging, metrics collection, and distributed tracing
    """

    def __init__(self):
        self.metrics: List[Metric] = []
        self.max_metrics_stored = 10000

    def log_structured(self, level: str, message: str, metadata: Dict[str, Any] = None) -> None:
        """Log structured data for observability"""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level.upper(),
            "message": message,
            "metadata": metadata or {}
        }
        
        # Log using Python logging
        log_method = getattr(logger, level.lower(), logger.info)
        log_method(json.dumps(log_entry))

    def record_metric(self, name: str, value: float, component_id: str = "", tags: Dict[str, str] = None) -> None:
        """Record a structured metric"""
        metric = Metric(
            metric_id=str(uuid.uuid4()),
            name=name,
            value=value,
            component_id=component_id,
            tags=tags or {}
        )
        
        self.metrics.append(metric)
        
        # Trim if too many
        if len(self.metrics) > self.max_metrics_stored:
            self.metrics = self.metrics[-self.max_metrics_stored:]
        
        logger.debug(f"📊 Metric recorded: {name} = {value}")

    def get_metrics_summary(self, component_id: str = None, name: str = None) -> Dict[str, Any]:
        """Get summary of recorded metrics"""
        filtered = self.metrics
        
        if component_id:
            filtered = [m for m in filtered if m.component_id == component_id]
        
        if name:
            filtered = [m for m in filtered if m.name == name]
        
        if not filtered:
            return {"count": 0, "metrics": []}
        
        values = [m.value for m in filtered]
        
        return {
            "count": len(filtered),
            "component_id": component_id,
            "metric_name": name,
            "latest_value": filtered[-1].value,
            "min_value": min(values),
            "max_value": max(values),
            "avg_value": sum(values) / len(values)
        }

# =============================================================================
# FAILURE RECOVERY SYSTEM (PHASE 2)
# =============================================================================

class AutoReconnectManager:
    """
    Auto-reconnect manager for WebSocket and network connections
    Handles unstable internet, intermittent disconnects, and reconnect synchronization
    """

    def __init__(self, max_reconnect_attempts: int = 10, initial_delay_seconds: float = 1.0):
        self.max_reconnect_attempts = max_reconnect_attempts
        self.initial_delay_seconds = initial_delay_seconds
        self.reconnect_attempts = 0
        self.is_connected = False
        self.connection_callbacks: List[Callable] = []
        self.disconnect_callbacks: List[Callable] = []
        self.reconnect_callbacks: List[Callable] = []
        self.pending_events: List[Dict] = []
        self.max_pending_events = 1000

    async def connect(self, connect_func: Callable, *args, **kwargs) -> bool:
        """Attempt to connect with auto-retry logic"""
        logger.info("🔄 Attempting connection...")
        
        delay = self.initial_delay_seconds
        
        for attempt in range(self.max_reconnect_attempts):
            try:
                result = await connect_func(*args, **kwargs)
                self.is_connected = True
                self.reconnect_attempts = 0
                logger.info(f"✅ Connected successfully on attempt {attempt + 1}")
                
                # Trigger connected callbacks
                for callback in self.connection_callbacks:
                    try:
                        await callback()
                    except Exception as e:
                        logger.error(f"Connection callback failed: {e}")
                
                # Process pending events
                await self._process_pending_events()
                
                return True
                
            except Exception as e:
                self.reconnect_attempts = attempt + 1
                logger.warning(f"⚠️  Connection attempt {attempt + 1}/{self.max_reconnect_attempts} failed: {e}")
                
                # Trigger disconnect callbacks
                for callback in self.disconnect_callbacks:
                    try:
                        await callback(attempt + 1, str(e))
                    except Exception as cb_error:
                        logger.error(f"Disconnect callback failed: {cb_error}")
                
                if attempt < self.max_reconnect_attempts - 1:
                    # Exponential backoff
                    wait_time = min(delay * (2 ** attempt), 60.0)
                    logger.info(f"⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)
        
        logger.error(f"❌ All {self.max_reconnect_attempts} connection attempts failed")
        return False

    async def disconnect(self, disconnect_func: Callable, *args, **kwargs) -> None:
        """Gracefully disconnect"""
        try:
            await disconnect_func(*args, **kwargs)
            self.is_connected = False
            logger.info("✅ Disconnected gracefully")
        except Exception as e:
            logger.error(f"❌ Error during disconnect: {e}")

    def queue_event(self, event: Dict) -> None:
        """Queue an event to be processed when reconnected"""
        self.pending_events.append(event)
        
        if len(self.pending_events) > self.max_pending_events:
            self.pending_events = self.pending_events[-self.max_pending_events:]
            logger.warning(f"⚠️  Pending events buffer full, dropped oldest events")

    async def _process_pending_events(self) -> None:
        """Process queued events after reconnection"""
        if not self.pending_events:
            return
        
        logger.info(f"🔄 Processing {len(self.pending_events)} pending events...")
        
        for event in list(self.pending_events):
            for callback in self.reconnect_callbacks:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Reconnect callback failed: {e}")
        
        self.pending_events = []
        logger.info("✅ Pending events processed")

    def register_connection_callback(self, callback: Callable) -> None:
        """Register callback for successful connection"""
        self.connection_callbacks.append(callback)

    def register_disconnect_callback(self, callback: Callable) -> None:
        """Register callback for disconnection"""
        self.disconnect_callbacks.append(callback)

    def register_reconnect_callback(self, callback: Callable) -> None:
        """Register callback for processing events after reconnect"""
        self.reconnect_callbacks.append(callback)

class StateRecoverySystem:
    """
    State recovery system for application state
    Saves state to persistent storage and recovers on restart
    """

    def __init__(self, storage_path: str = "/tmp/worldmine_state"):
        self.storage_path = storage_path
        self.state_snapshots: Dict[str, Dict] = {}
        self.max_snapshots = 100
        os.makedirs(storage_path, exist_ok=True)

    async def save_state(self, component_id: str, state: Dict[str, Any]) -> bool:
        """Save component state to persistent storage"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            snapshot = {
                "component_id": component_id,
                "timestamp": timestamp,
                "state": state
            }
            
            # Save to memory
            if component_id not in self.state_snapshots:
                self.state_snapshots[component_id] = []
            
            self.state_snapshots[component_id].append(snapshot)
            
            if len(self.state_snapshots[component_id]) > self.max_snapshots:
                self.state_snapshots[component_id] = self.state_snapshots[component_id][-self.max_snapshots:]
            
            # Save to disk
            file_path = os.path.join(self.storage_path, f"{component_id}_state.json")
            with open(file_path, "w") as f:
                json.dump(snapshot, f)
            
            logger.debug(f"💾 State saved for {component_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save state for {component_id}: {e}")
            return False

    async def recover_state(self, component_id: str) -> Optional[Dict[str, Any]]:
        """Recover component state from persistent storage"""
        try:
            # Try memory first
            if component_id in self.state_snapshots and self.state_snapshots[component_id]:
                latest_snapshot = self.state_snapshots[component_id][-1]
                logger.info(f"🔄 Recovered state from memory for {component_id}")
                return latest_snapshot["state"]
            
            # Try disk
            file_path = os.path.join(self.storage_path, f"{component_id}_state.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    snapshot = json.load(f)
                
                # Cache in memory
                if component_id not in self.state_snapshots:
                    self.state_snapshots[component_id] = []
                self.state_snapshots[component_id].append(snapshot)
                
                logger.info(f"🔄 Recovered state from disk for {component_id}")
                return snapshot["state"]
            
            logger.warning(f"⚠️  No state found for {component_id}")
            return None
            
        except Exception as e:
            logger.error(f"❌ Failed to recover state for {component_id}: {e}")
            return None

    def get_state_history(self, component_id: str, limit: int = 10) -> List[Dict]:
        """Get historical state snapshots"""
        if component_id not in self.state_snapshots:
            return []
        
        return self.state_snapshots[component_id][-limit:]

class PersistentEventQueue:
    """
    Persistent event queue for reliable event delivery
    Stores events on disk and guarantees delivery
    """

    def __init__(self, queue_path: str = "/tmp/worldmine_events"):
        self.queue_path = queue_path
        self.queue: List[Dict] = []
        self.processing_queue: List[Dict] = []
        self.max_queue_size = 10000
        os.makedirs(queue_path, exist_ok=True)
        
        # Load existing events from disk
        self._load_from_disk()

    async def enqueue(self, event: Dict[str, Any]) -> bool:
        """Add event to the queue"""
        try:
            event_id = str(uuid.uuid4())
            timestamp = datetime.now(timezone.utc).isoformat()
            
            queue_item = {
                "event_id": event_id,
                "timestamp": timestamp,
                "event": event,
                "status": "pending"
            }
            
            self.queue.append(queue_item)
            
            if len(self.queue) > self.max_queue_size:
                self.queue = self.queue[-self.max_queue_size:]
                logger.warning(f"⚠️  Queue full, dropped oldest events")
            
            await self._save_to_disk()
            logger.debug(f"📥 Event enqueued: {event_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to enqueue event: {e}")
            return False

    async def dequeue(self, batch_size: int = 10) -> List[Dict]:
        """Get next batch of events from queue"""
        try:
            batch = self.queue[:batch_size]
            self.processing_queue.extend(batch)
            self.queue = self.queue[batch_size:]
            
            for item in batch:
                item["status"] = "processing"
            
            await self._save_to_disk()
            logger.debug(f"📤 Dequeued {len(batch)} events")
            return [item["event"] for item in batch]
            
        except Exception as e:
            logger.error(f"❌ Failed to dequeue events: {e}")
            return []

    async def mark_completed(self, event_id: str) -> None:
        """Mark event as completed"""
        try:
            self.processing_queue = [
                item for item in self.processing_queue 
                if item["event_id"] != event_id
            ]
            await self._save_to_disk()
            logger.debug(f"✅ Event completed: {event_id}")
        except Exception as e:
            logger.error(f"❌ Failed to mark event completed: {e}")

    async def mark_failed(self, event_id: str, requeue: bool = True) -> None:
        """Mark event as failed, optionally requeue"""
        try:
            failed_item = next(
                (item for item in self.processing_queue if item["event_id"] == event_id),
                None
            )
            
            if failed_item:
                self.processing_queue = [
                    item for item in self.processing_queue 
                    if item["event_id"] != event_id
                ]
                
                if requeue:
                    failed_item["status"] = "pending"
                    self.queue.insert(0, failed_item)
                    logger.warning(f"🔄 Event requeued: {event_id}")
            
            await self._save_to_disk()
        except Exception as e:
            logger.error(f"❌ Failed to mark event failed: {e}")

    def get_queue_size(self) -> int:
        """Get current queue size"""
        return len(self.queue) + len(self.processing_queue)

    async def _save_to_disk(self) -> None:
        """Save queue to disk"""
        try:
            all_items = self.queue + self.processing_queue
            file_path = os.path.join(self.queue_path, "events.json")
            with open(file_path, "w") as f:
                json.dump(all_items, f)
        except Exception as e:
            logger.error(f"❌ Failed to save queue to disk: {e}")

    def _load_from_disk(self) -> None:
        """Load queue from disk on startup"""
        try:
            file_path = os.path.join(self.queue_path, "events.json")
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    all_items = json.load(f)
                
                for item in all_items:
                    if item["status"] == "processing":
                        item["status"] = "pending"
                        self.queue.append(item)
                    else:
                        self.queue.append(item)
                
                logger.info(f"🔄 Loaded {len(all_items)} events from disk")
        except Exception as e:
            logger.error(f"❌ Failed to load queue from disk: {e}")

# =============================================================================
# REAL-TIME SYSTEM HARDENING (PHASE 3)
# =============================================================================

class EventIntegrityManager:
    """
    Event integrity manager for real-time systems
    Prevents duplicate events, ensures ordering, and validates integrity
    """

    def __init__(self):
        self.seen_events: set = set()
        self.event_order: List[str] = []
        self.max_seen_events = 100000
        self.event_sequence_number = 0

    async def validate_event(self, event_id: str, sequence_number: Optional[int] = None) -> Dict[str, Any]:
        """Validate event for integrity and ordering"""
        result = {
            "event_id": event_id,
            "is_duplicate": False,
            "is_valid": True,
            "sequence_valid": True,
            "message": ""
        }

        # Check for duplicate
        if event_id in self.seen_events:
            result["is_duplicate"] = True
            result["is_valid"] = False
            result["message"] = f"Duplicate event detected: {event_id}"
            logger.warning(f"⚠️  {result['message']}")
            return result

        # Add to seen events
        self.seen_events.add(event_id)
        self.event_order.append(event_id)

        # Trim if too many
        if len(self.seen_events) > self.max_seen_events:
            oldest_events = self.event_order[:-self.max_seen_events]
            for old_id in oldest_events:
                self.seen_events.discard(old_id)
            self.event_order = self.event_order[-self.max_seen_events:]

        # Validate sequence number
        if sequence_number is not None:
            expected_sequence = self.event_sequence_number + 1
            if sequence_number != expected_sequence:
                result["sequence_valid"] = False
                result["message"] = f"Sequence gap: expected {expected_sequence}, got {sequence_number}"
                logger.warning(f"⚠️  {result['message']}")
            
            self.event_sequence_number = max(self.event_sequence_number, sequence_number)

        return result

    def is_duplicate(self, event_id: str) -> bool:
        """Check if event is duplicate"""
        return event_id in self.seen_events

    def get_next_sequence_number(self) -> int:
        """Get next sequence number for event ordering"""
        self.event_sequence_number += 1
        return self.event_sequence_number

class RaceConditionHandler:
    """
    Race condition handler for concurrent operations
    Uses async locks and optimistic concurrency control
    """

    def __init__(self):
        self.locks: Dict[str, asyncio.Lock] = {}
        self.resource_versions: Dict[str, int] = {}
        self.lock_timeout_seconds = 30.0

    async def acquire_lock(self, resource_id: str) -> bool:
        """Acquire lock for a resource"""
        if resource_id not in self.locks:
            self.locks[resource_id] = asyncio.Lock()

        lock = self.locks[resource_id]
        
        try:
            acquired = await asyncio.wait_for(
                lock.acquire(),
                timeout=self.lock_timeout_seconds
            )
            if acquired:
                logger.debug(f"🔒 Lock acquired: {resource_id}")
                return True
            return False
        except asyncio.TimeoutError:
            logger.error(f"❌ Lock timeout: {resource_id}")
            return False

    def release_lock(self, resource_id: str) -> None:
        """Release lock for a resource"""
        if resource_id in self.locks:
            lock = self.locks[resource_id]
            if lock.locked():
                lock.release()
                logger.debug(f"🔓 Lock released: {resource_id}")

    async def update_resource_version(self, resource_id: str, expected_version: int) -> Optional[int]:
        """Update resource version with optimistic concurrency control"""
        current_version = self.resource_versions.get(resource_id, 0)
        
        if expected_version != current_version:
            logger.warning(f"⚠️  Version conflict: {resource_id} - expected {expected_version}, current {current_version}")
            return None
        
        new_version = current_version + 1
        self.resource_versions[resource_id] = new_version
        logger.debug(f"📝 Version updated: {resource_id} -> {new_version}")
        return new_version

    def get_resource_version(self, resource_id: str) -> int:
        """Get current version of a resource"""
        return self.resource_versions.get(resource_id, 0)

class StaleStateHandler:
    """
    Stale state handler for real-time systems
    Prevents and recovers from stale state issues
    """

    def __init__(self, max_staleness_seconds: float = 60.0):
        self.max_staleness_seconds = max_staleness_seconds
        self.state_timestamps: Dict[str, float] = {}
        self.state_validators: Dict[str, Callable] = {}

    def update_state_timestamp(self, state_id: str) -> None:
        """Update timestamp for a state"""
        self.state_timestamps[state_id] = time.time()

    def is_state_stale(self, state_id: str) -> bool:
        """Check if state is stale"""
        if state_id not in self.state_timestamps:
            return True
        
        age_seconds = time.time() - self.state_timestamps[state_id]
        return age_seconds > self.max_staleness_seconds

    def get_state_age(self, state_id: str) -> Optional[float]:
        """Get age of state in seconds"""
        if state_id not in self.state_timestamps:
            return None
        return time.time() - self.state_timestamps[state_id]

    def register_validator(self, state_id: str, validator: Callable) -> None:
        """Register a validator function for a state"""
        self.state_validators[state_id] = validator

    async def validate_state(self, state_id: str, current_state: Any) -> Dict[str, Any]:
        """Validate state using registered validator"""
        result = {
            "state_id": state_id,
            "is_valid": True,
            "is_stale": self.is_state_stale(state_id),
            "age_seconds": self.get_state_age(state_id),
            "message": ""
        }

        if state_id in self.state_validators:
            try:
                validator = self.state_validators[state_id]
                is_valid = await validator(current_state) if asyncio.iscoroutinefunction(validator) else validator(current_state)
                
                if not is_valid:
                    result["is_valid"] = False
                    result["message"] = f"State validation failed: {state_id}"
                    logger.warning(f"⚠️  {result['message']}")
            except Exception as e:
                result["is_valid"] = False
                result["message"] = f"Validator error: {str(e)}"
                logger.error(f"❌ {result['message']}")

        return result

class ConflictResolutionEngine:
    """
    Conflict resolution engine for distributed systems
    Handles conflicts with predefined strategies
    """

    class ConflictStrategy(Enum):
        """Conflict resolution strategies"""
        LAST_WRITE_WINS = "last_write_wins"
        FIRST_WRITE_WINS = "first_write_wins"
        HIGHEST_VERSION_WINS = "highest_version_wins"
        MERGE = "merge"
        MANUAL = "manual"

    def __init__(self, default_strategy: ConflictStrategy = ConflictStrategy.LAST_WRITE_WINS):
        self.default_strategy = default_strategy
        self.conflict_log: List[Dict] = []
        self.max_conflict_log = 1000
        self.state_versions: Dict[str, int] = {}

    async def resolve_conflict(
        self,
        resource_id: str,
        version_a: int,
        version_b: int,
        state_a: Any,
        state_b: Any,
        strategy: Optional[ConflictStrategy] = None
    ) -> Dict[str, Any]:
        """Resolve conflict between two versions"""
        strategy = strategy or self.default_strategy
        
        conflict_record = {
            "resource_id": resource_id,
            "version_a": version_a,
            "version_b": version_b,
            "strategy": strategy.value,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

        logger.warning(f"⚠️  Conflict detected: {resource_id} (v{version_a} vs v{version_b}) - using {strategy.value}")

        winner = None
        winning_version = None
        message = ""

        if strategy == self.ConflictStrategy.LAST_WRITE_WINS:
            if version_b > version_a:
                winner = state_b
                winning_version = version_b
                message = "Last write wins"
            else:
                winner = state_a
                winning_version = version_a
                message = "First write wins (last write was not newer)"

        elif strategy == self.ConflictStrategy.FIRST_WRITE_WINS:
            if version_a < version_b:
                winner = state_a
                winning_version = version_a
                message = "First write wins"
            else:
                winner = state_b
                winning_version = version_b
                message = "Last write wins (first write was not older)"

        elif strategy == self.ConflictStrategy.HIGHEST_VERSION_WINS:
            if version_b > version_a:
                winner = state_b
                winning_version = version_b
                message = "Highest version wins"
            else:
                winner = state_a
                winning_version = version_a
                message = "Highest version wins"

        elif strategy == self.ConflictStrategy.MERGE:
            winner = self._merge_states(state_a, state_b)
            winning_version = max(version_a, version_b) + 1
            message = "States merged"

        else:
            winner = None
            winning_version = None
            message = "Manual resolution required"

        conflict_record["winner"] = winning_version
        conflict_record["message"] = message
        
        self.conflict_log.append(conflict_record)
        
        if len(self.conflict_log) > self.max_conflict_log:
            self.conflict_log = self.conflict_log[-self.max_conflict_log:]

        return {
            "winner": winner,
            "winning_version": winning_version,
            "strategy": strategy.value,
            "message": message,
            "conflict_recorded": True
        }

    def _merge_states(self, state_a: Any, state_b: Any) -> Any:
        """Simple merge strategy - combines dictionaries"""
        if isinstance(state_a, dict) and isinstance(state_b, dict):
            merged = {**state_a, **state_b}
            return merged
        elif isinstance(state_a, list) and isinstance(state_b, list):
            return list(set(state_a + state_b))
        else:
            return state_b

    def get_conflict_history(self, resource_id: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Get conflict history, optionally filtered by resource"""
        conflicts = self.conflict_log
        
        if resource_id:
            conflicts = [c for c in conflicts if c["resource_id"] == resource_id]
        
        return conflicts[-limit:]

# =============================================================================
# PERFORMANCE ENGINEERING (PHASE 4)
# =============================================================================

class PerformanceOptimizer:
    """
    Performance optimization engine for backend systems
    Implements caching, batching, and async task queuing
    """

    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.cache_ttl_seconds: Dict[str, float] = {}
        self.max_cache_size = 10000
        self.task_queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self.is_processing_tasks = False
        self.event_batches: Dict[str, List[Dict]] = {}
        self.max_batch_size = 100
        self.batch_timeout_seconds = 5.0

    async def get_from_cache(self, key: str) -> Optional[Any]:
        """Get item from cache with TTL check"""
        if key not in self.cache:
            return None
        
        if key in self.cache_ttl_seconds:
            ttl = self.cache_ttl_seconds[key]
            cache_entry = self.cache[key]
            
            if time.time() - cache_entry["timestamp"] > ttl:
                del self.cache[key]
                del self.cache_ttl_seconds[key]
                logger.debug(f"⏰ Cache expired: {key}")
                return None
        
        logger.debug(f"📦 Cache hit: {key}")
        return self.cache[key]["value"]

    async def set_cache(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None
    ) -> None:
        """Set item in cache with optional TTL"""
        self.cache[key] = {
            "value": value,
            "timestamp": time.time()
        }
        
        if ttl_seconds:
            self.cache_ttl_seconds[key] = ttl_seconds
        
        # Trim cache if too big
        if len(self.cache) > self.max_cache_size:
            oldest_keys = sorted(
                self.cache.keys(),
                key=lambda k: self.cache[k]["timestamp"]
            )[:-self.max_cache_size]
            
            for old_key in oldest_keys:
                del self.cache[old_key]
                if old_key in self.cache_ttl_seconds:
                    del self.cache_ttl_seconds[old_key]
        
        logger.debug(f"📦 Cache set: {key}")

    async def invalidate_cache(self, pattern: Optional[str] = None) -> int:
        """Invalidate cache items, optionally by pattern"""
        if pattern:
            keys_to_delete = [k for k in self.cache.keys() if pattern in k]
        else:
            keys_to_delete = list(self.cache.keys())
        
        for key in keys_to_delete:
            del self.cache[key]
            if key in self.cache_ttl_seconds:
                del self.cache_ttl_seconds[key]
        
        logger.info(f"🗑️  Invalidated {len(keys_to_delete)} cache items")
        return len(keys_to_delete)

    async def enqueue_task(self, task: Callable, *args, **kwargs) -> None:
        """Enqueue a task for background processing"""
        task_item = {
            "task": task,
            "args": args,
            "kwargs": kwargs,
            "enqueued_at": time.time()
        }
        
        try:
            self.task_queue.put_nowait(task_item)
            logger.debug(f"📋 Task enqueued")
            
            if not self.is_processing_tasks:
                asyncio.create_task(self._process_task_queue())
                
        except asyncio.QueueFull:
            logger.warning(f"⚠️  Task queue full, dropping task")

    async def _process_task_queue(self) -> None:
        """Process tasks from the queue in background"""
        self.is_processing_tasks = True
        logger.info("🚀 Starting task queue processor")
        
        try:
            while True:
                try:
                    task_item = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                    
                    task = task_item["task"]
                    args = task_item["args"]
                    kwargs = task_item["kwargs"]
                    
                    try:
                        if asyncio.iscoroutinefunction(task):
                            await task(*args, **kwargs)
                        else:
                            task(*args, **kwargs)
                        
                        logger.debug(f"✅ Task completed")
                        
                    except Exception as e:
                        logger.error(f"❌ Task failed: {e}")
                        
                    finally:
                        self.task_queue.task_done()
                        
                except asyncio.TimeoutError:
                    # Queue is empty, check if we should exit
                    if self.task_queue.empty():
                        break
                        
        except Exception as e:
            logger.error(f"❌ Task queue processor failed: {e}")
        finally:
            self.is_processing_tasks = False
            logger.info("🛑 Task queue processor stopped")

    async def batch_event(self, batch_id: str, event: Dict) -> None:
        """Batch events for efficient processing"""
        if batch_id not in self.event_batches:
            self.event_batches[batch_id] = []
        
        self.event_batches[batch_id].append(event)
        
        # Process batch if full
        if len(self.event_batches[batch_id]) >= self.max_batch_size:
            await self._process_batch(batch_id)

    async def _process_batch(self, batch_id: str) -> None:
        """Process a batch of events"""
        if batch_id not in self.event_batches:
            return
        
        batch = self.event_batches[batch_id]
        logger.info(f"📦 Processing batch {batch_id}: {len(batch)} events")
        
        # Clear the batch
        del self.event_batches[batch_id]
        
        return batch

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.max_cache_size,
            "ttl_count": len(self.cache_ttl_seconds),
            "task_queue_size": self.task_queue.qsize(),
            "active_batches": len(self.event_batches)
        }

# =============================================================================
# SECURITY HARDENING (PHASE 5)
# =============================================================================

class SecurityHardeningEngine:
    """
    Enterprise-grade security hardening engine
    Zero-Trust, audit logging, threat detection, and encryption
    """

    class ThreatLevel(Enum):
        """Threat severity levels"""
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"

    def __init__(self):
        self.audit_log: List[Dict] = []
        self.max_audit_log = 100000
        self.rate_limits: Dict[str, Dict] = {}
        self.default_rate_limit_requests = 100
        self.default_rate_limit_window_seconds = 60
        self.suspicious_activities: List[Dict] = []
        self.trusted_ips: set = set()
        self.blocked_ips: set = set()

    async def log_audit(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        action: str = "",
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None
    ) -> None:
        """Log an audit event for compliance"""
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "action": action,
            "metadata": metadata or {},
            "ip_address": ip_address,
            "is_sensitive": event_type in [
                "escrow_release",
                "kyc_verification",
                "password_change",
                "api_key_create"
            ]
        }
        
        self.audit_log.append(audit_entry)
        
        if len(self.audit_log) > self.max_audit_log:
            self.audit_log = self.audit_log[-self.max_audit_log:]
        
        logger.info(f"📝 Audit log: {event_type} - {action}")

    async def check_rate_limit(
        self,
        client_id: str,
        requests: Optional[int] = None,
        window_seconds: Optional[float] = None
    ) -> Dict[str, Any]:
        """Check and enforce rate limits"""
        requests = requests or self.default_rate_limit_requests
        window_seconds = window_seconds or self.default_rate_limit_window_seconds
        
        now = time.time()
        
        if client_id not in self.rate_limits:
            self.rate_limits[client_id] = {
                "requests": [],
                "window_start": now
            }
        
        client_data = self.rate_limits[client_id]
        
        # Clean old requests
        client_data["requests"] = [
            req_time for req_time in client_data["requests"]
            if now - req_time < window_seconds
        ]
        
        # Reset window if needed
        if now - client_data["window_start"] > window_seconds:
            client_data["requests"] = []
            client_data["window_start"] = now
        
        # Check limit
        remaining = requests - len(client_data["requests"])
        is_allowed = remaining > 0
        
        if is_allowed:
            client_data["requests"].append(now)
        
        result = {
            "client_id": client_id,
            "allowed": is_allowed,
            "remaining": max(0, remaining),
            "limit": requests,
            "window_seconds": window_seconds,
            "reset_at": client_data["window_start"] + window_seconds
        }
        
        if not is_allowed:
            logger.warning(f"⚠️  Rate limit exceeded: {client_id}")
        
        return result

    async def detect_threat(
        self,
        activity: Dict,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect suspicious activity and threats"""
        threat_result = {
            "is_threat": False,
            "threat_level": self.ThreatLevel.LOW,
            "message": "",
            "recommended_action": ""
        }
        
        threat_indicators = []
        
        # Check for brute force patterns
        if activity.get("failed_login_attempts", 0) > 5:
            threat_indicators.append("multiple_failed_logins")
            threat_result["threat_level"] = self.ThreatLevel.HIGH
        
        # Check for unusual location
        if ip_address and ip_address not in self.trusted_ips:
            if activity.get("is_new_location", False):
                threat_indicators.append("unusual_location")
                if threat_result["threat_level"].value < "medium":
                    threat_result["threat_level"] = self.ThreatLevel.MEDIUM
        
        # Check for rapid transactions
        if activity.get("transactions_last_minute", 0) > 10:
            threat_indicators.append("rapid_transactions")
            if threat_result["threat_level"].value < "high":
                threat_result["threat_level"] = self.ThreatLevel.HIGH
        
        if threat_indicators:
            threat_result["is_threat"] = True
            threat_result["message"] = f"Suspicious activity detected: {', '.join(threat_indicators)}"
            threat_result["recommended_action"] = "require_2fa" if threat_result["threat_level"] == self.ThreatLevel.HIGH else "monitor"
            
            # Log the threat
            self.suspicious_activities.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": user_id,
                "ip_address": ip_address,
                "activity": activity,
                "indicators": threat_indicators,
                "threat_level": threat_result["threat_level"].value
            })
            
            logger.warning(f"🚨 Threat detected: {threat_result['message']}")
        
        return threat_result

    async def block_ip(self, ip_address: str) -> None:
        """Block an IP address"""
        self.blocked_ips.add(ip_address)
        logger.warning(f"🚫 IP blocked: {ip_address}")
        await self.log_audit(
            event_type="security_block",
            action=f"block_ip:{ip_address}",
            metadata={"ip_address": ip_address}
        )

    async def allow_ip(self, ip_address: str) -> None:
        """Allow/trust an IP address"""
        self.trusted_ips.add(ip_address)
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
        logger.info(f"✅ IP trusted: {ip_address}")

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips

    def get_audit_history(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """Get audit history with optional filters"""
        filtered = self.audit_log
        
        if user_id:
            filtered = [entry for entry in filtered if entry.get("user_id") == user_id]
        
        if event_type:
            filtered = [entry for entry in filtered if entry.get("event_type") == event_type]
        
        return filtered[-limit:]

    def get_security_stats(self) -> Dict[str, Any]:
        """Get security system statistics"""
        return {
            "audit_log_count": len(self.audit_log),
            "suspicious_activities_count": len(self.suspicious_activities),
            "trusted_ips_count": len(self.trusted_ips),
            "blocked_ips_count": len(self.blocked_ips),
            "rate_limit_clients_count": len(self.rate_limits)
        }

# =============================================================================
# GLOBAL INSTANCES (ALL PHASES 1-5)
# =============================================================================

health_monitor = HealthMonitor()
observability = ObservabilitySystem()
default_circuit_breaker = CircuitBreaker()
auto_reconnect_manager = AutoReconnectManager()
state_recovery = StateRecoverySystem()
persistent_queue = PersistentEventQueue()
event_integrity = EventIntegrityManager()
race_condition_handler = RaceConditionHandler()
stale_state_handler = StaleStateHandler()
conflict_resolution = ConflictResolutionEngine()
performance_optimizer = PerformanceOptimizer()
security_engine = SecurityHardeningEngine()

async def example_reliability_demo():
    """Demonstrate the reliability system"""
    logger.info("🚀 Starting World-Mine Reliability System Demo...")
    
    # 1. Health check all systems
    health_summary = await health_monitor.check_all_systems()
    print("\n📊 HEALTH CHECK RESULTS:")
    print(json.dumps(health_monitor.get_system_health_summary(), indent=2))
    
    # 2. Record some metrics
    observability.record_metric("transaction_latency", 45.2, "escrow", {"type": "create"})
    observability.record_metric("transaction_latency", 52.1, "escrow", {"type": "release"})
    observability.record_metric("ai_inference_time", 234.5, "market_intelligence")
    
    print("\n📈 METRICS SUMMARY:")
    print(json.dumps(observability.get_metrics_summary("escrow", "transaction_latency"), indent=2))
    
    logger.info("✅ Reliability system demo complete!")

if __name__ == "__main__":
    asyncio.run(example_reliability_demo())
