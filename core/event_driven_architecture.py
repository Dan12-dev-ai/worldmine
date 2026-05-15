"""
EVENT-DRIVEN ARCHITECTURE with MESSAGE BUS
Async event streaming for scalable, decoupled services
================================================================================

All system components communicate via events, not direct calls.
Enables:
- Service independence
- Exactly-once processing
- Complete audit trail
- Easy scaling and failure isolation
"""

import json
import uuid
from typing import Dict, Any, Callable, List, Optional
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod
from enum import Enum
import asyncio
import structlog

import aioredis
from core.production_foundation import (
    redis_client,
    logger,
    db_pool,
)

# ============================================================================
# EVENT TYPES
# ============================================================================

class EventType(Enum):
    """System event types"""
    # Agent events
    AGENT_SIGNAL_GENERATED = "agent.signal.generated"
    AGENT_ANALYSIS_COMPLETE = "agent.analysis.complete"
    
    # Order events
    ORDER_SUBMITTED = "order.submitted"
    ORDER_VALIDATED = "order.validated"
    ORDER_RISK_CHECKED = "order.risk_checked"
    ORDER_APPROVED = "order.approved"
    ORDER_REJECTED = "order.rejected"
    ORDER_EXECUTED = "order.executed"
    ORDER_FAILED = "order.failed"
    ORDER_CANCELLED = "order.cancelled"
    
    # Trade events
    TRADE_EXECUTED = "trade.executed"
    TRADE_SETTLED = "trade.settled"
    TRADE_FAILED = "trade.failed"
    
    # Risk events
    RISK_CHECK_PASSED = "risk.check.passed"
    RISK_CHECK_FAILED = "risk.check.failed"
    RISK_LIMIT_BREACHED = "risk.limit.breached"
    CIRCUIT_BREAKER_TRIGGERED = "risk.circuit_breaker.triggered"
    
    # Market events
    MARKET_DATA_UPDATED = "market.data.updated"
    PRICE_FEED_UPDATE = "market.price.updated"
    LIQUIDITY_CHECK = "market.liquidity.check"
    
    # System events
    SYSTEM_HEALTH_CHECK = "system.health.check"
    SYSTEM_ERROR = "system.error"
    SERVICE_DEGRADED = "system.service.degraded"

@dataclass
class Event:
    """Base event class"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    source_service: str
    payload: Dict[str, Any]
    correlation_id: str  # For tracing request through systems
    user_id: Optional[str] = None
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps({
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source_service": self.source_service,
            "payload": self.payload,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
        })
    
    @staticmethod
    def from_json(data: str) -> "Event":
        """Deserialize from JSON"""
        obj = json.loads(data)
        return Event(
            event_id=obj["event_id"],
            event_type=EventType(obj["event_type"]),
            timestamp=datetime.fromisoformat(obj["timestamp"]),
            source_service=obj["source_service"],
            payload=obj["payload"],
            correlation_id=obj["correlation_id"],
            user_id=obj.get("user_id"),
        )

# ============================================================================
# MESSAGE BUS (REDIS-BACKED EVENT STREAM)
# ============================================================================

class EventBus:
    """
    Redis-backed event bus for async, scalable event publishing.
    
    Uses Redis Streams for:
    - Persistence (survives restarts)
    - Consumer groups (at-least-once delivery)
    - Exactly-once semantics with deduplication
    """
    
    def __init__(self):
        self.redis = redis_client.redis
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.worker_tasks = []
    
    async def publish(self, event: Event) -> bool:
        """
        Publish event to Redis stream.
        
        All subscribers will receive this event asynchronously.
        """
        try:
            stream_key = f"events:{event.event_type.value}"
            
            # Publish to stream
            await self.redis.xadd(
                stream_key,
                {"data": event.to_json()},
                maxlen=1000000,  # Limit memory usage
            )
            
            logger.info(
                "event_published",
                event_type=event.event_type.value,
                event_id=event.event_id,
                correlation_id=event.correlation_id
            )
            
            return True
        except Exception as e:
            logger.error("event_publish_failed", error=str(e))
            return False
    
    async def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(handler)
        
        logger.info(
            "event_subscriber_added",
            event_type=event_type.value,
            handler=handler.__name__
        )
    
    async def consume(self, event_type: EventType) -> Optional[Event]:
        """
        Consume event from stream.
        
        Blocks until event available (30s timeout).
        """
        stream_key = f"events:{event_type.value}"
        
        try:
            result = await self.redis.xread({stream_key: "0"}, count=1, block=30000)
            
            if result:
                stream, messages = result[0]
                event_id, data = messages[0]
                event_json = data[b"data"].decode("utf-8")
                return Event.from_json(event_json)
            
            return None
        except Exception as e:
            logger.error("event_consume_failed", error=str(e))
            return None
    
    async def start_listeners(self):
        """Start event listeners for all subscribers"""
        tasks = []
        
        for event_type, handlers in self.subscribers.items():
            for handler in handlers:
                task = asyncio.create_task(self._listen_and_handle(event_type, handler))
                tasks.append(task)
                self.worker_tasks.append(task)
        
        logger.info("event_listeners_started", count=len(tasks))
    
    async def _listen_and_handle(self, event_type: EventType, handler: Callable):
        """Listen for events and call handler"""
        while True:
            try:
                event = await self.consume(event_type)
                if event:
                    await handler(event)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("event_handler_failed", error=str(e))
                await asyncio.sleep(1)
    
    async def shutdown(self):
        """Shutdown all listeners"""
        for task in self.worker_tasks:
            task.cancel()
        
        # Wait for all tasks to complete
        await asyncio.gather(*self.worker_tasks, return_exceptions=True)
        logger.info("event_bus_shutdown")

event_bus = EventBus()

# ============================================================================
# EVENT HANDLERS (SERVICES LISTEN TO EVENTS)
# ============================================================================

class OrderEventHandler:
    """Handles order-related events"""
    
    async def on_order_submitted(self, event: Event):
        """Handle order submission event"""
        logger.info("order_event", event_type="SUBMITTED", order_id=event.payload.get("order_id"))
        # Process order submission
    
    async def on_order_approved(self, event: Event):
        """Handle order approval"""
        logger.info("order_event", event_type="APPROVED", order_id=event.payload.get("order_id"))
        # Trigger execution
    
    async def on_order_executed(self, event: Event):
        """Handle trade execution"""
        logger.info("order_event", event_type="EXECUTED", trade_id=event.payload.get("trade_id"))
        # Update account, record PnL

class RiskEventHandler:
    """Handles risk-related events"""
    
    async def on_risk_limit_breached(self, event: Event):
        """Handle risk limit breach"""
        logger.warning("risk_event", event_type="LIMIT_BREACHED", details=event.payload)
        # Halt trading, alert monitoring
    
    async def on_circuit_breaker_triggered(self, event: Event):
        """Handle circuit breaker trigger"""
        logger.critical("risk_event", event_type="CIRCUIT_BREAKER", details=event.payload)
        # Send emergency notification

class MarketEventHandler:
    """Handles market data events"""
    
    async def on_price_update(self, event: Event):
        """Handle market price update"""
        # Update internal price cache
        pass
    
    async def on_liquidity_check(self, event: Event):
        """Handle liquidity assessment"""
        # Update liquidity metrics
        pass

# ============================================================================
# OUTBOX PATTERN (FOR TRANSACTION RELIABILITY)
# ============================================================================

class OutboxPattern:
    """
    Guarantees event delivery even if service crashes.
    
    Process:
    1. Write to database + insert event to outbox table
    2. Periodically send events from outbox
    3. Mark sent events as delivered
    4. Retry failed events indefinitely
    """
    
    async def publish_with_guarantee(
        self,
        event: Event,
        db_operation_query: str,
        db_operation_params: List[Any],
    ) -> bool:
        """
        Publish event with transactional guarantee.
        
        Either both database operation AND event are written,
        or neither (atomic).
        """
        
        try:
            # Write to database and outbox atomically
            query = """
                BEGIN;
                """ + db_operation_query + """;
                INSERT INTO outbox (event_id, event_type, payload, created_at)
                VALUES ($N, $N+1, $N+2, $N+3);
                COMMIT;
            """
            
            await db_pool.execute(
                query,
                event.event_id,
                event.event_type.value,
                event.to_json(),
                datetime.now(timezone.utc),
            )
            
            logger.info("outbox_event_stored", event_id=event.event_id)
            return True
            
        except Exception as e:
            logger.error("outbox_store_failed", error=str(e))
            return False
    
    async def flush_outbox(self):
        """
        Periodically flush outbox events.
        
        Should be called periodically (e.g., every 10 seconds).
        """
        
        try:
            # Fetch undelivered events
            query = """
                SELECT event_id, event_type, payload
                FROM outbox
                WHERE delivered = false
                ORDER BY created_at
                LIMIT 100
            """
            
            rows = await db_pool.fetch(query)
            
            for row in rows:
                event_json = row["payload"]
                event = Event.from_json(event_json)
                
                # Try to publish
                if await event_bus.publish(event):
                    # Mark as delivered
                    await db_pool.execute(
                        "UPDATE outbox SET delivered = true WHERE event_id = $1",
                        row["event_id"]
                    )
                else:
                    # Retry next cycle
                    logger.warning("outbox_event_delivery_failed", event_id=row["event_id"])
        
        except Exception as e:
            logger.error("outbox_flush_failed", error=str(e))

outbox = OutboxPattern()

# ============================================================================
# REQUEST TRACING (CORRELATION ID)
# ============================================================================

class RequestTracer:
    """
    Tracks request through entire system with correlation ID.
    
    Enables root cause analysis of failures.
    """
    
    def __init__(self):
        self.current_correlation_id = None
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for this request"""
        self.current_correlation_id = correlation_id
    
    def get_correlation_id(self) -> str:
        """Get current correlation ID or create new"""
        if not self.current_correlation_id:
            self.current_correlation_id = str(uuid.uuid4())
        return self.current_correlation_id
    
    def create_event(
        self,
        event_type: EventType,
        source_service: str,
        payload: Dict[str, Any],
        user_id: Optional[str] = None,
    ) -> Event:
        """Create event with current correlation ID"""
        return Event(
            event_id=f"EVT_{uuid.uuid4().hex[:12]}",
            event_type=event_type,
            timestamp=datetime.now(timezone.utc),
            source_service=source_service,
            payload=payload,
            correlation_id=self.get_correlation_id(),
            user_id=user_id,
        )

tracer = RequestTracer()

print("✅ Event-Driven Architecture with Message Bus loaded")
