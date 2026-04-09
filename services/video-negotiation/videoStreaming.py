"""
Video Negotiation Service - DEDAN Mine Live Video & Auction System
Real-time live video negotiations + live auctions with WebRTC
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import json
import asyncio
from dataclasses import dataclass

from models import VideoSession, User, Listing
from database import get_db

@dataclass
class VideoSessionConfig:
    """Configuration for video sessions"""
    session_type: str  # 'negotiation', 'live_auction', 'verification_inspection'
    max_participants: int = 10
    duration_minutes: int = 60
    enable_recording: bool = True
    enable_transcription: bool = True
    bandwidth_requirements: Dict[str, Any] = None
    encryption_enabled: bool = True

@dataclass
class VideoMessage:
    """Message in video session"""
    user_id: str
    message: str
    message_type: str  # 'text', 'audio', 'video', 'screen_share'
    timestamp: datetime
    metadata: Dict[str, Any] = None

class VideoNegotiationService:
    """Live video negotiation and auction service"""
    
    def __init__(self):
        self.db = next(get_db())
        self.active_sessions = {}  # In-memory session tracking
        self.websocket_connections = {}  # WebSocket connection management
        
    async def schedule_video_session(
        self,
        host_id: str,
        listing_id: str,
        session_config: VideoSessionConfig
    ) -> Dict[str, Any]:
        """Schedule a video negotiation or live auction session"""
        try:
            # Validate listing
            listing = self.db.query(Listing).filter(Listing.id == listing_id).first()
            if not listing:
                return {"success": False, "error": "Listing not found"}
            
            # Check if listing supports video
            if not listing.video_negotiation_enabled:
                return {"success": False, "error": "Video negotiation not enabled for this listing"}
            
            # Create video session
            session = VideoSession(
                id=str(uuid.uuid4()),
                listing_id=listing_id,
                host_id=host_id,
                session_type=session_config.session_type,
                scheduled_time=session_config.scheduled_time if hasattr(session_config, 'scheduled_time') else datetime.now(timezone.utc) + timedelta(hours=1),
                duration_minutes=session_config.duration_minutes,
                max_participants=session_config.max_participants,
                session_status="scheduled",
                encryption_enabled=session_config.encryption_enabled,
                recording_enabled=session_config.enable_recording,
                auto_transcription=session_config.enable_transcription,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(session)
            self.db.commit()
            
            # Generate streaming keys
            stream_key = self._generate_stream_key(session.id)
            recording_url = f"https://stream.dedan-mine.com/recordings/{session.id}" if session_config.enable_recording else None
            
            return {
                "success": True,
                "session_id": session.id,
                "stream_key": stream_key,
                "recording_url": recording_url,
                "scheduled_time": session.scheduled_time.isoformat(),
                "duration_minutes": session.duration_minutes,
                "max_participants": session.max_participants
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def join_video_session(
        self,
        session_id: str,
        participant_id: str,
        participant_type: str = "participant"
    ) -> Dict[str, Any]:
        """Join a video session"""
        try:
            session = self.db.query(VideoSession).filter(VideoSession.id == session_id).first()
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Check session status
            if session.session_status not in ["scheduled", "waiting", "active"]:
                return {"success": False, "error": "Session not active"}
            
            # Check participant limit
            current_participants = json.loads(session.participant_ids or "[]")
            if len(current_participants) >= session.max_participants:
                return {"success": False, "error": "Session full"}
            
            # Add participant
            if participant_id not in current_participants:
                current_participants.append(participant_id)
                session.participant_ids = json.dumps(current_participants)
                
                # Update session status
                if session.session_status == "scheduled":
                    session.session_status = "waiting"
                    session.actual_start_time = datetime.now(timezone.utc)
                elif session.session_status == "waiting" and len(current_participants) >= 2:
                    session.session_status = "active"
                
                self.db.commit()
            
            # Generate WebRTC connection details
            webrtc_config = await self._generate_webrtc_config(session_id, participant_id)
            
            return {
                "success": True,
                "session_id": session_id,
                "participant_type": participant_type,
                "webrtc_config": webrtc_config,
                "session_status": session.session_status,
                "current_participants": len(current_participants),
                "max_participants": session.max_participants
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def send_message_to_session(
        self,
        session_id: str,
        sender_id: str,
        message: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Send message to video session"""
        try:
            session = self.db.query(VideoSession).filter(VideoSession.id == session_id).first()
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Create message object
            video_message = VideoMessage(
                user_id=sender_id,
                message=message,
                message_type=message_type,
                timestamp=datetime.now(timezone.utc),
                metadata=metadata or {}
            )
            
            # Add to session messages
            messages = json.loads(session.chat_messages or "[]")
            messages.append({
                "user_id": sender_id,
                "message": message,
                "message_type": message_type,
                "timestamp": video_message.timestamp.isoformat(),
                "metadata": metadata
            })
            session.chat_messages = json.dumps(messages)
            
            self.db.commit()
            
            # Broadcast to WebSocket connections
            await self._broadcast_message(session_id, video_message.__dict__)
            
            # Transcription if enabled
            if session.auto_transcription and message_type in ["text", "audio"]:
                await self._transcribe_message(session_id, video_message)
            
            return {
                "success": True,
                "message_id": str(uuid.uuid4()),
                "timestamp": video_message.timestamp.isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def start_live_auction(
        self,
        session_id: str,
        auction_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Start live auction within video session"""
        try:
            session = self.db.query(VideoSession).filter(VideoSession.id == session_id).first()
            if not session:
                return {"success": False, "error": "Session not found"}
            
            if session.session_type != "live_auction":
                return {"success": False, "error": "Session not configured for live auction"}
            
            # Update session to active
            session.session_status = "active"
            session.actual_start_time = datetime.now(timezone.utc)
            session.live_video_url = auction_config.get("stream_url")
            self.db.commit()
            
            # Initialize auction state
            auction_state = {
                "current_bid": auction_config.get("starting_price", 0),
                "current_bidder": None,
                "bid_count": 0,
                "auction_end_time": session.actual_start_time + timedelta(minutes=session.duration_minutes),
                "auto_extend": auction_config.get("auto_extend", True),
                "extend_time_minutes": auction_config.get("extend_time_minutes", 10)
            }
            
            # Store auction state
            self.active_sessions[session_id] = {
                "session": session.__dict__,
                "auction_state": auction_state,
                "participants": json.loads(session.participant_ids or "[]")
            }
            
            return {
                "success": True,
                "auction_state": auction_state,
                "stream_url": session.live_video_url,
                "session_active": True
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def place_live_bid(
        self,
        session_id: str,
        bidder_id: str,
        bid_amount: float
    ) -> Dict[str, Any]:
        """Place bid during live auction"""
        try:
            if session_id not in self.active_sessions:
                return {"success": False, "error": "Live auction not active"}
            
            session_data = self.active_sessions[session_id]
            auction_state = session_data["auction_state"]
            
            # Validate bid
            if bid_amount <= auction_state["current_bid"]:
                return {"success": False, "error": "Bid must be higher than current bid"}
            
            # Update auction state
            auction_state["current_bid"] = bid_amount
            auction_state["current_bidder"] = bidder_id
            auction_state["bid_count"] += 1
            
            # Check for auto-extension
            time_remaining = auction_state["auction_end_time"] - datetime.now(timezone.utc)
            if time_remaining.total_seconds() <= 600 and auction_state["auto_extend"]:  # 10 minutes
                auction_state["auction_end_time"] += timedelta(minutes=auction_state["extend_time_minutes"])
                auction_state["extend_count"] = auction_state.get("extend_count", 0) + 1
            
            # Broadcast bid update
            await self._broadcast_auction_update(session_id, {
                "type": "bid_update",
                "current_bid": bid_amount,
                "current_bidder": bidder_id,
                "bid_count": auction_state["bid_count"],
                "time_remaining": time_remaining.total_seconds(),
                "extended": auction_state.get("extend_count", 0) > 0
            })
            
            return {
                "success": True,
                "current_bid": bid_amount,
                "bid_count": auction_state["bid_count"],
                "time_remaining": time_remaining.total_seconds()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def end_video_session(
        self,
        session_id: str,
        end_reason: str = "completed"
    ) -> Dict[str, Any]:
        """End video session and save recording"""
        try:
            session = self.db.query(VideoSession).filter(VideoSession.id == session_id).first()
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Update session
            session.session_status = "ended"
            session.actual_end_time = datetime.now(timezone.utc)
            session.end_reason = end_reason
            self.db.commit()
            
            # Process recording
            recording_url = None
            if session.recording_enabled:
                recording_url = await self._process_session_recording(session_id)
            
            # Clean up active session
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
            
            # Disconnect WebSocket connections
            await self._disconnect_session_participants(session_id)
            
            return {
                "success": True,
                "session_duration": (session.actual_end_time - session.actual_start_time).total_seconds() / 60,
                "recording_url": recording_url,
                "end_reason": end_reason
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_webrtc_config(
        self,
        session_id: str,
        participant_id: str
    ) -> Dict[str, Any]:
        """Generate WebRTC configuration for participant"""
        return {
            "session_id": session_id,
            "participant_id": participant_id,
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"},
                {"urls": "stun:stun1.l.google.com:19302"}
            ],
            "signaling_server": f"wss://stream.dedan-mine.com/ws/{session_id}",
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256-GCM",
                "key_exchange": "ECDH"
            }
        }
    
    def _generate_stream_key(self, session_id: str) -> str:
        """Generate streaming key for session"""
        import secrets
        return secrets.token_urlsafe(32)
    
    async def _broadcast_message(self, session_id: str, message: Dict[str, Any]):
        """Broadcast message to all session participants"""
        if session_id in self.websocket_connections:
            connections = self.websocket_connections[session_id]
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"Error broadcasting message: {e}")
    
    async def _broadcast_auction_update(self, session_id: str, auction_update: Dict[str, Any]):
        """Broadcast auction update to all participants"""
        await self._broadcast_message(session_id, {
            "type": "auction_update",
            "data": auction_update
        })
    
    async def _transcribe_message(self, session_id: str, message: VideoMessage):
        """Transcribe audio/video message using AI"""
        # This would integrate with speech-to-text AI service
        # For now, simulate transcription
        if message.message_type == "audio":
            transcription = f"[Audio message: {message.message[:50]}...]"
            await self._broadcast_message(session_id, {
                "type": "transcription",
                "user_id": message.user_id,
                "transcription": transcription,
                "timestamp": message.timestamp.isoformat()
            })
    
    async def _process_session_recording(self, session_id: str) -> Optional[str]:
        """Process and store session recording"""
        try:
            # This would integrate with video processing service
            # For now, return mock URL
            return f"https://storage.dedan-mine.com/recordings/{session_id}.mp4"
        except Exception as e:
            print(f"Error processing recording: {e}")
            return None
    
    async def _disconnect_session_participants(self, session_id: str):
        """Disconnect all WebSocket participants"""
        if session_id in self.websocket_connections:
            connections = self.websocket_connections[session_id]
            for connection in connections:
                try:
                    await connection.close()
                except Exception as e:
                    print(f"Error disconnecting participant: {e}")
            del self.websocket_connections[session_id]
