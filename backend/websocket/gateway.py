"""
WebSocket Gateway
Real-time infrastructure with event bus and reconnection support
"""

from fastapi import WebSocket, WebSocketDisconnect, APIRouter, status
from typing import Dict, Set, Any, Optional
import json
import asyncio
from datetime import datetime
import uuid

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.room_subscriptions: Dict[str, Set[str]] = {}  # room -> connection_ids
        self.event_bus: Dict[str, Any] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        
        self.active_connections[connection_id] = websocket
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connected",
            "connection_id": connection_id,
            "timestamp": datetime.utcnow().isoformat()
        }, connection_id)
        
        return connection_id
    
    def disconnect(self, connection_id: str, user_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        # Remove from room subscriptions
        for room, connections in self.room_subscriptions.items():
            connections.discard(connection_id)
    
    async def send_personal_message(self, message: dict, connection_id: str):
        """Send a message to a specific connection"""
        if connection_id in self.active_connections:
            try:
                await self.active_connections[connection_id].send_json(message)
            except Exception:
                # Connection might be closed
                self.disconnect(connection_id, "")
    
    async def broadcast_to_user(self, message: dict, user_id: str):
        """Broadcast a message to all connections of a user"""
        if user_id in self.user_connections:
            for connection_id in self.user_connections[user_id]:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast_to_room(self, message: dict, room: str):
        """Broadcast a message to all subscribers of a room"""
        if room in self.room_subscriptions:
            for connection_id in self.room_subscriptions[room]:
                await self.send_personal_message(message, connection_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all active connections"""
        for connection_id in self.active_connections:
            await self.send_personal_message(message, connection_id)
    
    def subscribe_to_room(self, connection_id: str, room: str):
        """Subscribe a connection to a room"""
        if room not in self.room_subscriptions:
            self.room_subscriptions[room] = set()
        self.room_subscriptions[room].add(connection_id)
    
    def unsubscribe_from_room(self, connection_id: str, room: str):
        """Unsubscribe a connection from a room"""
        if room in self.room_subscriptions:
            self.room_subscriptions[room].discard(connection_id)
    
    def get_connection_stats(self) -> dict:
        """Get connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "total_users": len(self.user_connections),
            "total_rooms": len(self.room_subscriptions),
            "timestamp": datetime.utcnow().isoformat()
        }


manager = ConnectionManager()


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """Main WebSocket endpoint"""
    connection_id = await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            
            # Handle different message types
            message_type = data.get("type")
            
            if message_type == "ping":
                # Respond to ping with pong
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.utcnow().isoformat()
                }, connection_id)
            
            elif message_type == "subscribe":
                # Subscribe to a room
                room = data.get("room")
                if room:
                    manager.subscribe_to_room(connection_id, room)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "room": room,
                        "timestamp": datetime.utcnow().isoformat()
                    }, connection_id)
            
            elif message_type == "unsubscribe":
                # Unsubscribe from a room
                room = data.get("room")
                if room:
                    manager.unsubscribe_from_room(connection_id, room)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "room": room,
                        "timestamp": datetime.utcnow().isoformat()
                    }, connection_id)
            
            elif message_type == "message":
                # Broadcast message to room or user
                target_room = data.get("room")
                target_user = data.get("user_id")
                payload = data.get("payload")
                
                message = {
                    "type": "message",
                    "from_user_id": user_id,
                    "payload": payload,
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                if target_room:
                    await manager.broadcast_to_room(message, target_room)
                elif target_user:
                    await manager.broadcast_to_user(message, target_user)
            
            elif message_type == "event":
                # Emit event to event bus
                event_name = data.get("event")
                event_data = data.get("data")
                
                if event_name:
                    manager.event_bus[event_name] = {
                        "data": event_data,
                        "timestamp": datetime.utcnow().isoformat(),
                        "user_id": user_id
                    }
                    
                    # Broadcast event to subscribers
                    await manager.broadcast_to_room({
                        "type": "event",
                        "event": event_name,
                        "data": event_data,
                        "timestamp": datetime.utcnow().isoformat()
                    }, f"event:{event_name}")
    
    except WebSocketDisconnect:
        manager.disconnect(connection_id, user_id)
    except Exception as e:
        manager.disconnect(connection_id, user_id)


@router.get("/ws/stats")
@router.get("/stats")
@router.get("/api/ws/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    return manager.get_connection_stats()


@router.post("/ws/broadcast")
async def broadcast_message(message: dict):
    """Broadcast a message to all connected clients"""
    await manager.broadcast_to_all({
        "type": "broadcast",
        "payload": message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"message": "Broadcast sent"}


@router.post("/ws/broadcast/user/{user_id}")
async def broadcast_to_user(user_id: str, message: dict):
    """Broadcast a message to a specific user"""
    await manager.broadcast_to_user({
        "type": "broadcast",
        "payload": message,
        "timestamp": datetime.utcnow().isoformat()
    }, user_id)
    
    return {"message": f"Broadcast sent to user {user_id}"}


@router.post("/ws/broadcast/room/{room}")
async def broadcast_to_room(room: str, message: dict):
    """Broadcast a message to a specific room"""
    await manager.broadcast_to_room({
        "type": "broadcast",
        "payload": message,
        "timestamp": datetime.utcnow().isoformat()
    }, room)
    
    return {"message": f"Broadcast sent to room {room}"}


@router.get("/ws/event/{event_name}")
async def get_event(event_name: str):
    """Get event data from event bus"""
    if event_name in manager.event_bus:
        return manager.event_bus[event_name]
    
    return {"error": "Event not found"}


# Heartbeat task for connection health
async def heartbeat_task():
    """Send periodic heartbeat to all connections"""
    while True:
        await asyncio.sleep(30)
        await manager.broadcast_to_all({
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        })


# Reconnection helper
class ReconnectionHandler:
    """Handles WebSocket reconnection logic"""
    
    def __init__(self):
        self.reconnection_attempts: Dict[str, int] = {}
        self.max_attempts = 5
        self.backoff_base = 2
    
    def get_backoff_delay(self, connection_id: str) -> int:
        """Calculate exponential backoff delay"""
        attempts = self.reconnection_attempts.get(connection_id, 0)
        delay = min(self.backoff_base ** attempts, 30)
        return delay
    
    def record_attempt(self, connection_id: str):
        """Record a reconnection attempt"""
        self.reconnection_attempts[connection_id] = self.reconnection_attempts.get(connection_id, 0) + 1
    
    def reset_attempts(self, connection_id: str):
        """Reset reconnection attempts after successful connection"""
        if connection_id in self.reconnection_attempts:
            del self.reconnection_attempts[connection_id]
    
    def can_reconnect(self, connection_id: str) -> bool:
        """Check if reconnection is still possible"""
        return self.reconnection_attempts.get(connection_id, 0) < self.max_attempts


reconnection_handler = ReconnectionHandler()
