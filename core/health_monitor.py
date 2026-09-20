"""
World-Mine Health Monitoring System
Enterprise-grade health monitoring with startup/shutdown monitors
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class ServiceHealth:
    name: str
    status: HealthStatus
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""
    metrics: Dict[str, Any] = field(default_factory=dict)

class HealthMonitor:
    """Enterprise-grade health monitoring system"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self._monitoring = False
        self._lock = asyncio.Lock()
        
    async def startup_health_monitor(self):
        """Initialize health monitoring on startup"""
        logger.info("Starting health monitoring system...")
        self._monitoring = True
        
        # Initialize default services
        await self.register_service("database", HealthStatus.HEALTHY)
        await self.register_service("redis", HealthStatus.HEALTHY)
        await self.register_service("api", HealthStatus.HEALTHY)
        
        logger.info("Health monitoring system started")
        
    async def shutdown_health_monitor(self):
        """Shutdown health monitoring gracefully"""
        logger.info("Shutting down health monitoring system...")
        self._monitoring = False
        logger.info("Health monitoring system stopped")
        
    async def register_service(self, name: str, status: HealthStatus):
        """Register a service for monitoring"""
        async with self._lock:
            self.services[name] = ServiceHealth(name=name, status=status)
            logger.info(f"Registered service: {name}")
            
    async def update_service_health(self, name: str, status: HealthStatus, message: str = ""):
        """Update service health status"""
        async with self._lock:
            if name in self.services:
                self.services[name].status = status
                self.services[name].message = message
                self.services[name].last_check = datetime.now(timezone.utc)
                logger.info(f"Updated {name} health: {status.value}")
                
    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        async with self._lock:
            healthy_count = sum(1 for s in self.services.values() if s.status == HealthStatus.HEALTHY)
            total_count = len(self.services)
            
            overall_status = HealthStatus.HEALTHY
            if healthy_count < total_count:
                overall_status = HealthStatus.DEGRADED
            if healthy_count == 0:
                overall_status = HealthStatus.UNHEALTHY
                
            return {
                "status": overall_status.value,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "services": {
                    name: {
                        "status": s.status.value,
                        "message": s.message,
                        "last_check": s.last_check.isoformat()
                    }
                    for name, s in self.services.items()
                },
                "summary": f"{healthy_count}/{total_count} services healthy"
            }
            
    async def check_database(self) -> bool:
        """Check database connectivity"""
        # Placeholder for actual database check
        await self.update_service_health("database", HealthStatus.HEALTHY)
        return True
        
    async def check_redis(self) -> bool:
        """Check Redis connectivity"""
        # Placeholder for actual Redis check
        await self.update_service_health("redis", HealthStatus.HEALTHY)
        return True

# Global health monitor instance
health_monitor = HealthMonitor()

async def startup_health_monitor():
    """Startup health monitor"""
    await health_monitor.startup_health_monitor()

async def shutdown_health_monitor():
    """Shutdown health monitor"""
    await health_monitor.shutdown_health_monitor()
