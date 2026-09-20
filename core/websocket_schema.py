"""
World-Mine WebSocket Schema Standardization
Unified event schema with validation
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Standardized WebSocket event types"""
    # Connection events
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    RECONNECT = "reconnect"
    
    # Transaction events
    BID_PLACED = "bid_placed"
    BID_ACCEPTED = "bid_accepted"
    TRANSACTION_COMPLETED = "transaction_completed"
    
    # Listing events
    LISTING_CREATED = "listing_created"
    LISTING_UPDATED = "listing_updated"
    LISTING_CLOSED = "listing_closed"
    
    # AI events
    AI_RECOMMENDATION = "ai_recommendation"
    AI_VALIDATION = "ai_validation"
    
    # System events
    HEALTH_UPDATE = "health_update"
    ERROR = "error"

class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class WebSocketEvent:
    """Standardized WebSocket event schema"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    user_id: str
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "priority": self.priority.value,
            "data": self.data,
            "metadata": self.metadata,
            "correlation_id": self.correlation_id
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WebSocketEvent":
        """Create event from dictionary"""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            user_id=data["user_id"],
            priority=EventPriority(data.get("priority", "normal")),
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            correlation_id=data.get("correlation_id")
        )

class WebSocketEventValidator:
    """Validator for WebSocket events"""
    
    REQUIRED_FIELDS = ["event_id", "event_type", "timestamp", "user_id"]
    
    @staticmethod
    def validate(event_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate WebSocket event data
        
        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []
        
        # Check required fields
        for field in WebSocketEventValidator.REQUIRED_FIELDS:
            if field not in event_data:
                errors.append(f"Missing required field: {field}")
        
        # Validate event_type
        if "event_type" in event_data:
            try:
                EventType(event_data["event_type"])
            except ValueError:
                errors.append(f"Invalid event_type: {event_data['event_type']}")
        
        # Validate timestamp format
        if "timestamp" in event_data:
            try:
                datetime.fromisoformat(event_data["timestamp"])
            except ValueError:
                errors.append(f"Invalid timestamp format: {event_data['timestamp']}")
        
        # Validate priority if present
        if "priority" in event_data:
            try:
                EventPriority(event_data["priority"])
            except ValueError:
                errors.append(f"Invalid priority: {event_data['priority']}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize(event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize event data by removing sensitive fields"""
        sensitive_fields = ["password", "api_key", "secret", "token"]
        sanitized = event_data.copy()
        
        for field in sensitive_fields:
            if field in sanitized:
                sanitized[field] = "***REDACTED***"
        
        return sanitized

class WebSocketEventBus:
    """Centralized event bus for WebSocket events"""
    
    def __init__(self):
        self.subscribers: Dict[EventType, List[callable]] = {}
        self.event_history: List[WebSocketEvent] = []
        self._max_history = 1000
        
    def subscribe(self, event_type: EventType, callback: callable):
        """Subscribe to specific event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
        logger.info(f"Subscribed to {event_type.value}")
    
    async def publish(self, event: WebSocketEvent):
        """Publish event to subscribers"""
        # Validate event
        event_dict = event.to_dict()
        is_valid, errors = WebSocketEventValidator.validate(event_dict)
        if not is_valid:
            logger.error(f"Invalid event: {errors}")
            return False
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self._max_history:
            self.event_history.pop(0)
        
        # Notify subscribers
        if event.event_type in self.subscribers:
            for callback in self.subscribers[event.event_type]:
                try:
                    await callback(event)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
        
        logger.info(f"Published event: {event.event_type.value}")
        return True
    
    def get_history(self, event_type: Optional[EventType] = None, limit: int = 100) -> List[WebSocketEvent]:
        """Get event history"""
        if event_type:
            filtered = [e for e in self.event_history if e.event_type == event_type]
            return filtered[-limit:]
        return self.event_history[-limit:]

# Global event bus instance
websocket_event_bus = WebSocketEventBus()
