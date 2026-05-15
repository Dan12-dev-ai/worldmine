# COMMUNICATION + NEGOTIATION SYSTEM
# DEDAN Mine - Global Mineral Marketplace Platform
# Real-time communication system for buyer-seller negotiations

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timezone
import uuid
import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
import json

from core.production_foundation import audit_log
from core.event_driven_architecture import event_bus, EventType, Event
from core.governance_orchestrator import governance_orchestrator
from core.ai_intelligence_system import communication_agent

logger = logging.getLogger(__name__)

class NegotiationStatus(Enum):
    """Negotiation room status"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTED = "disputed"

class MessageType(Enum):
    """Message types in negotiation"""
    TEXT = "text"
    FILE = "file"
    CONTRACT = "contract"
    OFFER = "offer"
    COUNTER_OFFER = "counter_offer"
    ACCEPTANCE = "acceptance"
    REJECTION = "rejection"

@dataclass
class NegotiationParticipant:
    """Participant in negotiation room"""
    user_id: str
    role: str  # buyer, seller, mediator, observer
    joined_at: datetime
    permissions: List[str]  # send_messages, share_files, make_offers, etc.
    identity_verified: bool = False
    language_preference: str = "en"

@dataclass
class NegotiationMessage:
    """Message in negotiation room"""
    message_id: str
    room_id: str
    sender_id: str
    message_type: MessageType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    edited: bool = False
    deleted: bool = False

@dataclass
class NegotiationRoom:
    """Negotiation room for buyer-seller discussions"""
    room_id: str
    listing_id: str
    title: str
    participants: List[NegotiationParticipant] = field(default_factory=list)
    status: NegotiationStatus = NegotiationStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[NegotiationMessage] = field(default_factory=list)
    webRTC_room_id: Optional[str] = None
    recording_enabled: bool = False
    ai_moderation_enabled: bool = True

@dataclass
class VideoSession:
    """WebRTC video session"""
    session_id: str
    room_id: str
    participants: List[str]
    start_time: datetime
    end_time: Optional[datetime] = None
    recording_path: Optional[str] = None
    status: str = "active"

class CommunicationEngine:
    """
    Communication and negotiation engine
    Handles real-time messaging, video calls, and AI-assisted negotiations
    """

    def __init__(self):
        self.negotiation_rooms: Dict[str, NegotiationRoom] = {}
        self.active_video_sessions: Dict[str, VideoSession] = {}
        self.message_history: Dict[str, List[NegotiationMessage]] = {}

    async def create_negotiation_room(self, listing_id: str, creator_id: str, room_data: Dict[str, Any]) -> Tuple[bool, str, Optional[NegotiationRoom]]:
        """
        Create a new negotiation room for listing
        """
        logger.info(f"Creating negotiation room for listing {listing_id}")

        # Step 1: Validate creator permissions
        if not await self._validate_room_creation_permissions(creator_id, listing_id):
            return False, "Insufficient permissions to create negotiation room", None

        # Step 2: Create room
        room = NegotiationRoom(
            room_id=str(uuid.uuid4()),
            listing_id=listing_id,
            title=room_data.get('title', f"Negotiation for {listing_id}"),
            participants=[NegotiationParticipant(
                user_id=creator_id,
                role="creator",
                joined_at=datetime.now(timezone.utc),
                permissions=["send_messages", "share_files", "make_offers", "invite_participants"]
            )]
        )

        # Step 3: Initialize WebRTC room
        webrtc_id = await self._initialize_webrtc_room(room.room_id)
        room.webRTC_room_id = webrtc_id

        # Step 4: Register room
        self.negotiation_rooms[room.room_id] = room
        self.message_history[room.room_id] = []

        # Step 5: Publish room creation event
        event = Event(
            event_type=EventType.NEGOTIATION_ROOM_CREATED,
            payload={"room": room.__dict__},
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        # Step 6: Log room creation
        await audit_log.log_negotiation_room_creation(room)

        logger.info(f"Negotiation room created: {room.room_id}")
        return True, "Negotiation room created successfully", room

    async def join_negotiation_room(self, room_id: str, user_id: str, join_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Join an existing negotiation room
        """
        logger.info(f"User {user_id} joining room {room_id}")

        room = self.negotiation_rooms.get(room_id)
        if not room:
            return False, "Room not found"

        if room.status != NegotiationStatus.ACTIVE:
            return False, "Room is not active"

        # Check if user is already a participant
        if any(p.user_id == user_id for p in room.participants):
            return False, "User already in room"

        # Validate join permissions
        if not await self._validate_join_permissions(user_id, room):
            return False, "Insufficient permissions to join room"

        # Add participant
        participant = NegotiationParticipant(
            user_id=user_id,
            role=join_data.get('role', 'participant'),
            joined_at=datetime.now(timezone.utc),
            permissions=join_data.get('permissions', ["send_messages", "share_files"]),
            language_preference=join_data.get('language_preference', 'en')
        )

        room.participants.append(participant)
        room.last_activity = datetime.now(timezone.utc)

        # Publish join event
        event = Event(
            event_type=EventType.NEGOTIATION_PARTICIPANT_JOINED,
            payload={
                "room_id": room_id,
                "participant": participant.__dict__
            },
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        # Log participant join
        await audit_log.log_participant_join(room_id, participant)

        logger.info(f"User {user_id} joined room {room_id}")
        return True, "Successfully joined negotiation room"

    async def send_message(self, room_id: str, sender_id: str, message_data: Dict[str, Any]) -> Tuple[bool, str, Optional[NegotiationMessage]]:
        """
        Send message to negotiation room
        """
        room = self.negotiation_rooms.get(room_id)
        if not room:
            return False, "Room not found", None

        # Validate sender is participant
        if not any(p.user_id == sender_id for p in room.participants):
            return False, "Sender not in room", None

        # Validate message permissions
        participant = next(p for p in room.participants if p.user_id == sender_id)
        if "send_messages" not in participant.permissions:
            return False, "Insufficient permissions to send messages", None

        # Create message
        message = NegotiationMessage(
            message_id=str(uuid.uuid4()),
            room_id=room_id,
            sender_id=sender_id,
            message_type=MessageType(message_data.get('type', 'text')),
            content=message_data['content'],
            metadata=message_data.get('metadata', {})
        )

        # AI moderation if enabled
        if room.ai_moderation_enabled:
            moderation_result = await self._moderate_message(message)
            if not moderation_result['approved']:
                return False, f"Message rejected: {moderation_result['reason']}", None

        # Add to room and history
        room.messages.append(message)
        self.message_history[room_id].append(message)
        room.last_activity = datetime.now(timezone.utc)

        # Publish message event
        event = Event(
            event_type=EventType.NEGOTIATION_MESSAGE_SENT,
            payload={"message": message.__dict__},
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        # Log message
        await audit_log.log_negotiation_message(message)

        logger.info(f"Message sent in room {room_id} by {sender_id}")
        return True, "Message sent successfully", message

    async def start_video_session(self, room_id: str, initiator_id: str) -> Tuple[bool, str, Optional[VideoSession]]:
        """
        Start video session in negotiation room
        """
        room = self.negotiation_rooms.get(room_id)
        if not room:
            return False, "Room not found", None

        # Check if video session already active
        if room_id in self.active_video_sessions:
            return False, "Video session already active", None

        # Validate initiator permissions
        if not any(p.user_id == initiator_id and "start_video" in p.permissions for p in room.participants):
            return False, "Insufficient permissions to start video", None

        # Create video session
        session = VideoSession(
            session_id=str(uuid.uuid4()),
            room_id=room_id,
            participants=[p.user_id for p in room.participants],
            start_time=datetime.now(timezone.utc)
        )

        self.active_video_sessions[room_id] = session

        # Publish video session event
        event = Event(
            event_type=EventType.VIDEO_SESSION_STARTED,
            payload={"session": session.__dict__},
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        # Log video session start
        await audit_log.log_video_session_start(session)

        logger.info(f"Video session started in room {room_id}")
        return True, "Video session started", session

    async def end_video_session(self, room_id: str, user_id: str) -> Tuple[bool, str]:
        """
        End video session
        """
        session = self.active_video_sessions.get(room_id)
        if not session:
            return False, "No active video session", None

        # Validate permissions
        if user_id not in session.participants:
            return False, "User not in video session"

        # End session
        session.end_time = datetime.now(timezone.utc)
        session.status = "ended"

        # Clean up
        del self.active_video_sessions[room_id]

        # Publish end event
        event = Event(
            event_type=EventType.VIDEO_SESSION_ENDED,
            payload={"session": session.__dict__},
            correlation_id=str(uuid.uuid4())
        )
        await event_bus.publish(event)

        # Log session end
        await audit_log.log_video_session_end(session)

        logger.info(f"Video session ended in room {room_id}")
        return True, "Video session ended"

    async def get_ai_negotiation_assistance(self, room_id: str, user_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get AI assistance for negotiation
        """
        room = self.negotiation_rooms.get(room_id)
        if not room:
            return {"error": "Room not found"}

        # Get recent messages for context
        recent_messages = self.message_history.get(room_id, [])[-10:]  # Last 10 messages

        # Create AI signal for assistance
        assistance_signal = await communication_agent.assist_negotiation({
            "room_id": room_id,
            "user_id": user_id,
            "recent_messages": [msg.__dict__ for msg in recent_messages],
            "context": context
        })

        # Governance validation
        decision = await governance_orchestrator.validate_agent_signal(assistance_signal)

        if decision.approved:
            return {
                "assistance": assistance_signal.data,
                "confidence": assistance_signal.confidence,
                "governance_approved": True
            }
        else:
            return {
                "error": "AI assistance not approved",
                "reason": decision.reason
            }

    async def _validate_room_creation_permissions(self, creator_id: str, listing_id: str) -> bool:
        """Validate user can create negotiation room for listing"""
        # Placeholder - check if user owns listing or has negotiation permissions
        return True

    async def _validate_join_permissions(self, user_id: str, room: NegotiationRoom) -> bool:
        """Validate user can join negotiation room"""
        # Placeholder - check invitation, permissions, etc.
        return True

    async def _initialize_webrtc_room(self, room_id: str) -> str:
        """Initialize WebRTC room for video calls"""
        # Placeholder - integrate with WebRTC service
        return f"webrtc_{room_id}"

    async def _moderate_message(self, message: NegotiationMessage) -> Dict[str, Any]:
        """AI moderation of messages"""
        # Placeholder - integrate with content moderation AI
        return {"approved": True, "reason": "clean"}

# Global communication engine instance
communication_engine = CommunicationEngine()