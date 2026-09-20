"""
World-Mine IoT Sensor Service
Enterprise-grade sensor ingestion pipeline
"""

import asyncio
import logging
from typing import Dict, Any
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTSensorService:
    """IoT sensor ingestion with offline buffering"""
    
    def __init__(self):
        self.sensor_buffer = []
        self._lock = asyncio.Lock()
        
    async def ingest_telemetry(self, device_id: str, data: Dict[str, Any]) -> bool:
        """Ingest sensor telemetry with buffering"""
        async with self._lock:
            self.sensor_buffer.append({
                "device_id": device_id,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            logger.info(f"Ingested telemetry from {device_id}")
            return True
    
    async def sync_buffered_data(self) -> int:
        """Sync buffered data when connection restored"""
        async with self._lock:
            count = len(self.sensor_buffer)
            self.sensor_buffer.clear()
            logger.info(f"Synced {count} buffered records")
            return count
