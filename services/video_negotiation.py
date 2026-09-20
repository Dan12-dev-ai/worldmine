"""
World-Mine Video Negotiation Service
Enterprise-grade WebRTC-based video negotiation
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional, Any
from enum import Enum
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoomStatus(Enum):
    CREATED = "created"
    ACTIVE = "active"
    ENDED = "ended"

@dataclass
class VideoRoom:
    id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    status: RoomStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    participants: Dict[str, Any] = field(default_factory=dict)

class VideoNegotiationService:
    """Enterprise-grade video negotiation service"""
    
    def __init__(self):
        self.rooms: Dict[str, VideoRoom] = {}
        self._lock = asyncio.Lock()
        
    async def create_room(self, listing_id: str, buyer_id: str, seller_id: str) -> VideoRoom:
        """Create video negotiation room"""
        async with self._lock:
            room_id = str(uuid.uuid4())
            room = VideoRoom(
                id=room_id,
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=seller_id,
                status=RoomStatus.CREATED
            )
            self.rooms[room_id] = room
            logger.info(f"Created video room {room_id}")
            return room
    
    async def join_room(self, room_id: str, user_id: str) -> Dict[str, Any]:
        """Join video room"""
        async with self._lock:
            if room_id not in self.rooms:
                raise ValueError(f"Room {room_id} not found")
            room = self.rooms[room_id]
            if room.status == RoomStatus.CREATED:
                room.status = RoomStatus.ACTIVE
            return {"room_id": room_id, "status": room.status.value}
    
    async def end_room(self, room_id: str) -> bool:
        """End video room"""
        async with self._lock:
            if room_id not in self.rooms:
                return False
            self.rooms[room_id].status = RoomStatus.ENDED
            return True
