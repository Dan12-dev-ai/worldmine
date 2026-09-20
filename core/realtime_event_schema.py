# 🚀 WORLD-MINE REAL-TIME EVENT SCHEMA
## Standardized WebSocket Event Interface & Logistics Retry Logic

from typing import Dict, Any, Optional, Generic, TypeVar
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
import uuid
import json
import logging
import asyncio

logger = logging.getLogger(__name__)

T = TypeVar('T')

# =============================================================================
# EVENT TYPE ENUMERATION
# =============================================================================

class EventType(Enum):
    """Standardized event types"""
    # Logistics Events
    LOGISTICS_UPDATE = "logistics.update"
    SHIPMENT_TRACKING = "logistics.shipment_tracking"
    GPS_POSITION = "logistics.gps_position"
    CUSTOMS_UPDATE = "logistics.customs"
    WAREHOUSE_STATUS = "logistics.warehouse"
    
    # Market Events
    MARKET_SIGNAL = "market.signal"
    PRICE_UPDATE = "market.price_update"
    ORDER_BOOK = "market.order_book"
    TRADE_EXECUTED = "market.trade_executed"
    
    # Chat & Communication
    CHAT_MESSAGE = "chat.message"
    NEGOTIATION_UPDATE = "chat.negotiation"
    DOCUMENT_SHARED = "chat.document_shared"
    
    # System Events
    AI_RECOMMENDATION = "system.ai_recommendation"
    HEALTH_CHECK = "system.health_check"
    ALERT = "system.alert"
    
    # Transaction Events
    ESCROW_UPDATE = "transaction.escrow"
    CONTRACT_SIGNED = "transaction.contract_signed"
    PAYMENT_RECEIVED = "transaction.payment_received"

# =============================================================================
# STANDARDIZED EVENT INTERFACE
# =============================================================================

@dataclass
class WorldMineEvent(Generic[T]):
    """
    Standardized event schema for ALL WebSocket messages
    Every event MUST follow this strict TypeScript/TypeScript interface
    """
    event_type: str
    payload: T
    timestamp: str
    trace_id: str
    correlation_id: Optional[str] = None
    version: str = "1.0.0"
    source: str = "worldmine-api"

    @classmethod
    def create(
        cls,
        event_type: EventType,
        payload: T,
        correlation_id: Optional[str] = None
    ) -> 'WorldMineEvent[T]':
        """Factory method to create a standardized event"""
        return cls(
            event_type=event_type.value,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            trace_id=str(uuid.uuid4()),
            correlation_id=correlation_id,
            version="1.0.0",
            source="worldmine-api"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return asdict(self)

    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorldMineEvent[T]':
        """Create event from dictionary"""
        return cls(**data)

    @classmethod
    def from_json(cls, json_str: str) -> 'WorldMineEvent[T]':
        """Create event from JSON string"""
        return cls.from_dict(json.loads(json_str))

# =============================================================================
# PAYLOAD TYPES
# =============================================================================

@dataclass
class LogisticsTrackingPayload:
    """Payload for logistics tracking updates"""
    shipment_id: str
    status: str
    location: Dict[str, float]
    timestamp: str
    carrier: str
    estimated_arrival: Optional[str] = None
    waypoints: Optional[List[Dict[str, Any]]] = None

@dataclass
class GPSPositionPayload:
    """Payload for GPS position updates"""
    asset_id: str
    latitude: float
    longitude: float
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    speed: Optional[float] = None
    heading: Optional[float] = None

@dataclass
class MarketPricePayload:
    """Payload for market price updates"""
    commodity: str
    price: float
    currency: str
    change_24h: float
    volume: float
    source: str

@dataclass
class ChatMessagePayload:
    """Payload for chat messages"""
    message_id: str
    room_id: str
    user_id: str
    user_name: str
    content: str
    is_ai: bool = False
    attachments: Optional[List[Dict[str, Any]]] = None

# =============================================================================
# LOGISTICS GPS TRACKING - RETRY LOGIC
# =============================================================================

class LogisticsRetryManager:
    """
    Retry-Logic mechanism for Logistics GPS tracking
    Handles intermittent connectivity in remote mining areas
    """

    def __init__(self, max_retries: int = 10, initial_delay: float = 2.0):
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.pending_updates: List[WorldMineEvent[GPSPositionPayload]] = []
        self.max_pending = 1000
        self.is_retrying = False

    async def send_gps_update(
        self,
        event: WorldMineEvent[GPSPositionPayload]
    ) -> bool:
        """
        Send GPS update with automatic retry
        """
        attempt = 0
        delay = self.initial_delay

        while attempt < self.max_retries:
            try:
                # In production, this would send to WebSocket
                # For now, we'll simulate
                success = await self._attempt_send(event)
                
                if success:
                    logger.info(f"✅ GPS update sent successfully (attempt {attempt + 1})")
                    return True
                
                attempt += 1
                logger.warning(f"⚠️  GPS update failed (attempt {attempt + 1}/{self.max_retries})")
                
                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = min(delay * (2 ** (attempt - 1)), 60.0)
                    logger.info(f"⏳ Waiting {wait_time:.1f}s before retry...")
                    await asyncio.sleep(wait_time)

            except Exception as e:
                attempt += 1
                logger.error(f"❌ GPS update error (attempt {attempt + 1}): {e}")
                
                if attempt < self.max_retries:
                    wait_time = min(delay * (2 ** (attempt - 1)), 60.0)
                    await asyncio.sleep(wait_time)

        # All retries failed - queue for later
        logger.warning(f"📥 Queueing GPS update for later: {event.trace_id}")
        self._queue_update(event)
        return False

    async def _attempt_send(self, event: WorldMineEvent[GPSPositionPayload]) -> bool:
        """
        Attempt to send a single update
        Replace this with actual WebSocket send in production
        """
        # Simulate occasional failures (90% success rate)
        import random
        return random.random() > 0.1

    def _queue_update(self, event: WorldMineEvent[GPSPositionPayload]) -> None:
        """Queue an update for later transmission"""
        self.pending_updates.append(event)
        
        if len(self.pending_updates) > self.max_pending:
            # Keep most recent
            self.pending_updates = self.pending_updates[-self.max_pending:]
        
        logger.info(f"📦 Pending GPS updates: {len(self.pending_updates)}")

    async def flush_pending_updates(self) -> int:
        """Flush all pending updates"""
        if not self.pending_updates:
            return 0
        
        logger.info(f"🚀 Flushing {len(self.pending_updates)} pending GPS updates...")
        
        success_count = 0
        updates_to_send = list(self.pending_updates)
        self.pending_updates = []
        
        for event in updates_to_send:
            if await self.send_gps_update(event):
                success_count += 1
        
        logger.info(f"✅ Flushed {success_count}/{len(updates_to_send)} updates")
        return success_count

    def get_stats(self) -> Dict[str, Any]:
        """Get retry manager statistics"""
        return {
            "pending_updates": len(self.pending_updates),
            "max_pending": self.max_pending,
            "max_retries": self.max_retries
        }

# =============================================================================
# EVENT VALIDATOR
# =============================================================================

class EventValidator:
    """
    Validates that events follow the strict schema
    """

    @staticmethod
    def validate_event(event: WorldMineEvent[Any]) -> bool:
        """Validate an event against the schema"""
        try:
            # Required fields
            if not event.event_type:
                logger.warning("❌ Event missing event_type")
                return False
            
            if not event.payload:
                logger.warning("❌ Event missing payload")
                return False
            
            if not event.timestamp:
                logger.warning("❌ Event missing timestamp")
                return False
            
            if not event.trace_id:
                logger.warning("❌ Event missing trace_id")
                return False
            
            # Validate timestamp format
            datetime.fromisoformat(event.timestamp)
            
            # Validate trace_id is UUID
            uuid.UUID(event.trace_id)
            
            return True
            
        except Exception as e:
            logger.warning(f"❌ Event validation failed: {e}")
            return False

# =============================================================================
# GLOBAL INSTANCES
# =============================================================================

logistics_retry_manager = LogisticsRetryManager()
event_validator = EventValidator()
