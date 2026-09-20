"""
World-Mine GPS Retry Logic
Enterprise-grade GPS tracking with offline buffering and reconnect sync
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RECONNECTING = "reconnecting"

@dataclass
class GPSDataPoint:
    timestamp: datetime
    latitude: float
    longitude: float
    altitude: float
    accuracy: float
    device_id: str

@dataclass
class BufferedData:
    data_points: List[GPSDataPoint] = field(default_factory=list)
    max_buffer_size: int = 1000
    sync_status: str = "pending"

class GPSRetryManager:
    """Enterprise-grade GPS retry manager with offline buffering"""
    
    def __init__(self):
        self.connection_status = ConnectionStatus.DISCONNECTED
        self.buffered_data: Dict[str, BufferedData] = {}
        self.retry_attempts = 0
        self.max_retry_attempts = 5
        self.retry_delay = 5  # seconds
        self._sync_task = None
        
    async def start_tracking(self, device_id: str):
        """Start GPS tracking for device"""
        logger.info(f"Starting GPS tracking for device {device_id}")
        self.buffered_data[device_id] = BufferedData()
        await self._connect_with_retry()
        
    async def stop_tracking(self, device_id: str):
        """Stop GPS tracking for device"""
        logger.info(f"Stopping GPS tracking for device {device_id}")
        if device_id in self.buffered_data:
            await self.sync_buffered_data(device_id)
            del self.buffered_data[device_id]
            
    async def record_gps_point(self, device_id: str, data: Dict[str, Any]) -> bool:
        """
        Record GPS data point with offline buffering
        
        Args:
            device_id: Device identifier
            data: GPS data including lat, lon, alt, accuracy
            
        Returns:
            bool: Success status
        """
        if self.connection_status == ConnectionStatus.CONNECTED:
            # Direct upload when connected
            return await self._upload_gps_data(device_id, data)
        else:
            # Buffer when disconnected
            return await self._buffer_gps_data(device_id, data)
            
    async def _buffer_gps_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Buffer GPS data when offline"""
        if device_id not in self.buffered_data:
            self.buffered_data[device_id] = BufferedData()
            
        buffer = self.buffered_data[device_id]
        
        if len(buffer.data_points) >= buffer.max_buffer_size:
            logger.warning(f"Buffer full for device {device_id}, discarding oldest")
            buffer.data_points.pop(0)
            
        data_point = GPSDataPoint(
            timestamp=datetime.now(timezone.utc),
            latitude=data["latitude"],
            longitude=data["longitude"],
            altitude=data.get("altitude", 0),
            accuracy=data.get("accuracy", 0),
            device_id=device_id
        )
        
        buffer.data_points.append(data_point)
        buffer.sync_status = "pending"
        logger.info(f"Buffered GPS data for device {device_id}")
        return True
        
    async def _upload_gps_data(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Upload GPS data directly when connected"""
        try:
            # Placeholder for actual upload logic
            logger.info(f"Uploaded GPS data for device {device_id}")
            return True
        except Exception as e:
            logger.error(f"Upload failed, buffering: {e}")
            return await self._buffer_gps_data(device_id, data)
            
    async def _connect_with_retry(self):
        """Connect with exponential backoff retry"""
        self.connection_status = ConnectionStatus.RECONNECTING
        
        for attempt in range(self.max_retry_attempts):
            try:
                # Placeholder for actual connection logic
                logger.info(f"Connection attempt {attempt + 1}")
                
                # Simulate connection success
                self.connection_status = ConnectionStatus.CONNECTED
                self.retry_attempts = 0
                
                # Start sync task
                if self._sync_task is None or self._sync_task.done():
                    self._sync_task = asyncio.create_task(self._periodic_sync())
                    
                logger.info("GPS connection established")
                return
                
            except Exception as e:
                logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                self.retry_attempts += 1
                
                # Exponential backoff
                delay = self.retry_delay * (2 ** attempt)
                await asyncio.sleep(delay)
        
        self.connection_status = ConnectionStatus.DISCONNECTED
        logger.error("Max retry attempts reached, staying offline")
        
    async def _periodic_sync(self):
        """Periodically sync buffered data"""
        while self.connection_status == ConnectionStatus.CONNECTED:
            for device_id in list(self.buffered_data.keys()):
                await self.sync_buffered_data(device_id)
            await asyncio.sleep(30)  # Sync every 30 seconds
            
    async def sync_buffered_data(self, device_id: str) -> int:
        """
        Sync buffered GPS data for device
        
        Returns:
            int: Number of data points synced
        """
        if device_id not in self.buffered_data:
            return 0
            
        buffer = self.buffered_data[device_id]
        
        if not buffer.data_points:
            return 0
            
        if self.connection_status != ConnectionStatus.CONNECTED:
            logger.warning(f"Cannot sync, device {device_id} not connected")
            return 0
            
        synced_count = 0
        
        for data_point in buffer.data_points:
            try:
                data = {
                    "latitude": data_point.latitude,
                    "longitude": data_point.longitude,
                    "altitude": data_point.altitude,
                    "accuracy": data_point.accuracy,
                    "timestamp": data_point.timestamp.isoformat()
                }
                
                if await self._upload_gps_data(device_id, data):
                    synced_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to sync data point: {e}")
                break
                
        # Clear synced data
        if synced_count > 0:
            buffer.data_points = buffer.data_points[synced_count:]
            buffer.sync_status = "synced"
            logger.info(f"Synced {synced_count} data points for device {device_id}")
            
        return synced_count
        
    async def get_buffer_status(self, device_id: str) -> Dict[str, Any]:
        """Get buffer status for device"""
        if device_id not in self.buffered_data:
            return {"device_id": device_id, "buffered_count": 0, "status": "not_tracking"}
            
        buffer = self.buffered_data[device_id]
        
        return {
            "device_id": device_id,
            "buffered_count": len(buffer.data_points),
            "max_buffer_size": buffer.max_buffer_size,
            "sync_status": buffer.sync_status,
            "connection_status": self.connection_status.value
        }

# Global GPS retry manager instance
gps_retry_manager = GPSRetryManager()
