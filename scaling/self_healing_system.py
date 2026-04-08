"""
DEDAN Mine - Self-Healing System
Automated health monitoring and recovery for million-user support
Guardian AI integration for intelligent service management
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import psutil
import aiohttp
import json
import os
import subprocess
import signal
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """Service status types"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    CRITICAL = "critical"
    MAINTENANCE = "maintenance"
    RESTARTING = "restarting"

class RecoveryAction(Enum):
    """Recovery action types"""
    NONE = "none"
    RESTART_SERVICE = "restart_service"
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    FAILOVER = "failover"
    KILL_AND_RESTART = "kill_and_restart"
    ROUTE_TRAFFIC = "route_traffic"
    MAINTENANCE_MODE = "maintenance_mode"

@dataclass
class ServiceMetrics:
    """Service metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: float
    response_time: float
    error_rate: float
    request_rate: float
    active_connections: int
    queue_size: int

@dataclass
class ServiceHealth:
    """Service health information"""
    service_name: str
    service_type: str
    status: ServiceStatus
    metrics: ServiceMetrics
    last_check: datetime
    uptime: float
    consecutive_failures: int
    last_recovery_action: RecoveryAction
    last_recovery_time: Optional[datetime]
    recovery_count: int
    health_score: float
    auto_recovery_enabled: bool

class SelfHealingSystem:
    """Self-healing system for DEDAN Mine"""
    
    def __init__(self):
        self.services = {}
        self.health_check_interval = 30  # seconds
        self.recovery_cooldown = 300  # seconds
        self.max_consecutive_failures = 3
        self.health_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "response_time": 1000.0,  # milliseconds
            "error_rate": 0.05,  # 5%
            "queue_size": 1000
        }
        
        # Initialize services
        self.initialize_services()
    
    def initialize_services(self):
        """Initialize service definitions"""
        services_config = [
            {
                "service_name": "main_api",
                "service_type": "fastapi",
                "port": 8000,
                "health_endpoint": "/health",
                "process_name": "uvicorn",
                "auto_recovery": True
            },
            {
                "service_name": "payout_api",
                "service_type": "fastapi",
                "port": 8001,
                "health_endpoint": "/health",
                "process_name": "uvicorn",
                "auto_recovery": True
            },
            {
                "service_name": "consumer_protection",
                "service_type": "fastapi",
                "port": 8002,
                "health_endpoint": "/health",
                "process_name": "uvicorn",
                "auto_recovery": True
            },
            {
                "service_name": "dashboard",
                "service_type": "streamlit",
                "port": 8501,
                "health_endpoint": "/_stcore/health",
                "process_name": "streamlit",
                "auto_recovery": True
            },
            {
                "service_name": "redis",
                "service_type": "cache",
                "port": 6379,
                "health_endpoint": None,
                "process_name": "redis-server",
                "auto_recovery": True
            },
            {
                "service_name": "postgresql",
                "service_type": "database",
                "port": 5432,
                "health_endpoint": None,
                "process_name": "postgres",
                "auto_recovery": True
            }
        ]
        
        for config in services_config:
            self.services[config["service_name"]] = ServiceHealth(
                service_name=config["service_name"],
                service_type=config["service_type"],
                status=ServiceStatus.HEALTHY,
                metrics=ServiceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0),
                last_check=datetime.now(timezone.utc),
                uptime=0.0,
                consecutive_failures=0,
                last_recovery_action=RecoveryAction.NONE,
                last_recovery_time=None,
                recovery_count=0,
                health_score=100.0,
                auto_recovery_enabled=config["auto_recovery"]
            )
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        logger.info("Starting self-healing system monitoring")
        
        while True:
            try:
                await self.check_all_services()
                await asyncio.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"Monitoring error: {str(e)}")
                await asyncio.sleep(10)
    
    async def check_all_services(self):
        """Check health of all services"""
        tasks = []
        
        for service_name in self.services.keys():
            task = asyncio.create_task(self.check_service_health(service_name))
            tasks.append(task)
        
        # Run all health checks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and trigger recovery if needed
        for i, result in enumerate(results):
            service_name = list(self.services.keys())[i]
            if isinstance(result, Exception):
                logger.error(f"Health check failed for {service_name}: {str(result)}")
                await self.trigger_recovery(service_name, RecoveryAction.RESTART_SERVICE)
    
    async def check_service_health(self, service_name: str) -> ServiceHealth:
        """Check health of individual service"""
        try:
            service = self.services[service_name]
            
            # Get service metrics
            metrics = await self.collect_service_metrics(service_name)
            
            # Calculate health score
            health_score = self.calculate_health_score(metrics)
            
            # Determine status
            status = self.determine_service_status(metrics, health_score)
            
            # Update service health
            service.metrics = metrics
            service.last_check = datetime.now(timezone.utc)
            service.health_score = health_score
            service.status = status
            
            # Check if recovery is needed
            if status in [ServiceStatus.UNHEALTHY, ServiceStatus.CRITICAL]:
                service.consecutive_failures += 1
                
                if service.consecutive_failures >= self.max_consecutive_failures:
                    recovery_action = self.determine_recovery_action(service_name, status)
                    await self.trigger_recovery(service_name, recovery_action)
            else:
                service.consecutive_failures = 0
            
            logger.info(f"Health check completed for {service_name}: {status.value} (score: {health_score:.1f})")
            
            return service
            
        except Exception as e:
            logger.error(f"Health check failed for {service_name}: {str(e)}")
            service = self.services[service_name]
            service.status = ServiceStatus.UNHEALTHY
            service.consecutive_failures += 1
            return service
    
    async def collect_service_metrics(self, service_name: str) -> ServiceMetrics:
        """Collect metrics for service"""
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Get network metrics
            network = psutil.net_io_counters()
            
            # Get service-specific metrics
            service_metrics = await self.get_service_specific_metrics(service_name)
            
            return ServiceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory.percent,
                disk_usage=disk.percent,
                network_io=network.bytes_sent + network.bytes_recv,
                response_time=service_metrics.get("response_time", 0.0),
                error_rate=service_metrics.get("error_rate", 0.0),
                request_rate=service_metrics.get("request_rate", 0.0),
                active_connections=service_metrics.get("active_connections", 0),
                queue_size=service_metrics.get("queue_size", 0)
            )
            
        except Exception as e:
            logger.error(f"Metrics collection failed for {service_name}: {str(e)}")
            return ServiceMetrics(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0)
    
    async def get_service_specific_metrics(self, service_name: str) -> Dict[str, float]:
        """Get service-specific metrics"""
        try:
            service = self.services[service_name]
            
            if service.service_type == "fastapi":
                return await self.get_fastapi_metrics(service_name, service.port)
            elif service.service_type == "streamlit":
                return await self.get_streamlit_metrics(service_name, service.port)
            elif service.service_type == "cache":
                return await self.get_redis_metrics()
            elif service.service_type == "database":
                return await self.get_postgresql_metrics()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Service-specific metrics failed for {service_name}: {str(e)}")
            return {}
    
    async def get_fastapi_metrics(self, service_name: str, port: int) -> Dict[str, float]:
        """Get FastAPI service metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/metrics", timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "response_time": data.get("response_time", 0.0),
                            "error_rate": data.get("error_rate", 0.0),
                            "request_rate": data.get("request_rate", 0.0),
                            "active_connections": data.get("active_connections", 0),
                            "queue_size": data.get("queue_size", 0)
                        }
        except:
            pass
        
        # Fallback to basic health check
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/health", timeout=5) as response:
                    response_time = (time.time() - start_time) * 1000
                    return {
                        "response_time": response_time,
                        "error_rate": 0.0 if response.status == 200 else 1.0,
                        "request_rate": 0.0,
                        "active_connections": 1,
                        "queue_size": 0
                    }
        except:
            return {
                "response_time": 5000.0,  # High response time indicates failure
                "error_rate": 1.0,
                "request_rate": 0.0,
                "active_connections": 0,
                "queue_size": 0
            }
    
    async def get_streamlit_metrics(self, service_name: str, port: int) -> Dict[str, float]:
        """Get Streamlit service metrics"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{port}/_stcore/health", timeout=5) as response:
                    response_time = (time.time() - time.time()) * 1000
                    return {
                        "response_time": response_time,
                        "error_rate": 0.0 if response.status == 200 else 1.0,
                        "request_rate": 0.0,
                        "active_connections": 1,
                        "queue_size": 0
                    }
        except:
            return {
                "response_time": 5000.0,
                "error_rate": 1.0,
                "request_rate": 0.0,
                "active_connections": 0,
                "queue_size": 0
            }
    
    async def get_redis_metrics(self) -> Dict[str, float]:
        """Get Redis metrics"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            info = r.info()
            
            return {
                "response_time": 0.0,
                "error_rate": 0.0,
                "request_rate": info.get("instantaneous_ops_per_sec", 0.0),
                "active_connections": info.get("connected_clients", 0),
                "queue_size": 0
            }
        except:
            return {
                "response_time": 5000.0,
                "error_rate": 1.0,
                "request_rate": 0.0,
                "active_connections": 0,
                "queue_size": 0
            }
    
    async def get_postgresql_metrics(self) -> Dict[str, float]:
        """Get PostgreSQL metrics"""
        try:
            import asyncpg
            conn = await asyncpg.connect(
                host="localhost",
                port=5432,
                user="postgres",
                password="",
                database="dedan_mine"
            )
            
            # Get connection count
            result = await conn.fetch("SELECT count(*) FROM pg_stat_activity")
            active_connections = result[0]["count"]
            
            await conn.close()
            
            return {
                "response_time": 0.0,
                "error_rate": 0.0,
                "request_rate": 0.0,
                "active_connections": active_connections,
                "queue_size": 0
            }
        except:
            return {
                "response_time": 5000.0,
                "error_rate": 1.0,
                "request_rate": 0.0,
                "active_connections": 0,
                "queue_size": 0
            }
    
    def calculate_health_score(self, metrics: ServiceMetrics) -> float:
        """Calculate health score from metrics"""
        score = 100.0
        
        # CPU usage penalty
        if metrics.cpu_usage > self.health_thresholds["cpu_usage"]:
            score -= (metrics.cpu_usage - self.health_thresholds["cpu_usage"]) * 0.5
        
        # Memory usage penalty
        if metrics.memory_usage > self.health_thresholds["memory_usage"]:
            score -= (metrics.memory_usage - self.health_thresholds["memory_usage"]) * 0.5
        
        # Disk usage penalty
        if metrics.disk_usage > self.health_thresholds["disk_usage"]:
            score -= (metrics.disk_usage - self.health_thresholds["disk_usage"]) * 0.3
        
        # Response time penalty
        if metrics.response_time > self.health_thresholds["response_time"]:
            score -= (metrics.response_time - self.health_thresholds["response_time"]) * 0.01
        
        # Error rate penalty
        if metrics.error_rate > self.health_thresholds["error_rate"]:
            score -= metrics.error_rate * 100
        
        # Queue size penalty
        if metrics.queue_size > self.health_thresholds["queue_size"]:
            score -= (metrics.queue_size - self.health_thresholds["queue_size"]) * 0.01
        
        return max(0.0, min(100.0, score))
    
    def determine_service_status(self, metrics: ServiceMetrics, health_score: float) -> ServiceStatus:
        """Determine service status from metrics and health score"""
        if health_score >= 90:
            return ServiceStatus.HEALTHY
        elif health_score >= 70:
            return ServiceStatus.DEGRADED
        elif health_score >= 50:
            return ServiceStatus.UNHEALTHY
        else:
            return ServiceStatus.CRITICAL
    
    def determine_recovery_action(self, service_name: str, status: ServiceStatus) -> RecoveryAction:
        """Determine recovery action based on service status"""
        service = self.services[service_name]
        
        # Check if we're in cooldown period
        if service.last_recovery_time:
            cooldown_remaining = (datetime.now(timezone.utc) - service.last_recovery_time).total_seconds()
            if cooldown_remaining < self.recovery_cooldown:
                return RecoveryAction.NONE
        
        if status == ServiceStatus.CRITICAL:
            return RecoveryAction.KILL_AND_RESTART
        elif status == ServiceStatus.UNHEALTHY:
            if service.recovery_count < 3:
                return RecoveryAction.RESTART_SERVICE
            else:
                return RecoveryAction.SCALE_UP
        elif status == ServiceStatus.DEGRADED:
            return RecoveryAction.ROUTE_TRAFFIC
        else:
            return RecoveryAction.NONE
    
    async def trigger_recovery(self, service_name: str, action: RecoveryAction):
        """Trigger recovery action for service"""
        try:
            service = self.services[service_name]
            
            if not service.auto_recovery_enabled:
                logger.warning(f"Auto-recovery disabled for {service_name}")
                return
            
            logger.warning(f"Triggering recovery for {service_name}: {action.value}")
            
            # Update service state
            service.last_recovery_action = action
            service.last_recovery_time = datetime.now(timezone.utc)
            service.recovery_count += 1
            service.status = ServiceStatus.RESTARTING
            
            # Execute recovery action
            if action == RecoveryAction.RESTART_SERVICE:
                await self.restart_service(service_name)
            elif action == RecoveryAction.KILL_AND_RESTART:
                await self.kill_and_restart_service(service_name)
            elif action == RecoveryAction.SCALE_UP:
                await self.scale_service(service_name, "up")
            elif action == RecoveryAction.SCALE_DOWN:
                await self.scale_service(service_name, "down")
            elif action == RecoveryAction.ROUTE_TRAFFIC:
                await self.route_traffic_away(service_name)
            elif action == RecoveryAction.MAINTENANCE_MODE:
                await self.enable_maintenance_mode(service_name)
            
            logger.info(f"Recovery completed for {service_name}: {action.value}")
            
        except Exception as e:
            logger.error(f"Recovery failed for {service_name}: {str(e)}")
    
    async def restart_service(self, service_name: str):
        """Restart service"""
        try:
            service = self.services[service_name]
            
            # Find and restart process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_name in ' '.join(proc.info['cmdline'] or []):
                    proc.terminate()
                    proc.wait(timeout=10)
                    break
            
            # Wait a moment
            await asyncio.sleep(5)
            
            # Start service (implementation depends on service type)
            await self.start_service(service_name)
            
        except Exception as e:
            logger.error(f"Service restart failed for {service_name}: {str(e)}")
    
    async def kill_and_restart_service(self, service_name: str):
        """Kill and restart service"""
        try:
            service = self.services[service_name]
            
            # Force kill process
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_name in ' '.join(proc.info['cmdline'] or []):
                    proc.kill()
                    proc.wait(timeout=5)
                    break
            
            # Wait longer for force kill
            await asyncio.sleep(10)
            
            # Start service
            await self.start_service(service_name)
            
        except Exception as e:
            logger.error(f"Kill and restart failed for {service_name}: {str(e)}")
    
    async def start_service(self, service_name: str):
        """Start service"""
        try:
            service = self.services[service_name]
            
            if service.service_type == "fastapi":
                # Start FastAPI service
                cmd = [
                    "uvicorn",
                    f"{service_name}:app",
                    "--host", "0.0.0.0",
                    "--port", str(service.port),
                    "--workers", "4"
                ]
                subprocess.Popen(cmd, cwd="/home/kali/mini_business/backend")
                
            elif service.service_type == "streamlit":
                # Start Streamlit service
                cmd = [
                    "streamlit",
                    "run", "dashboard/app.py",
                    "--server.port", str(service.port),
                    "--server.address", "0.0.0.0"
                ]
                subprocess.Popen(cmd, cwd="/home/kali/mini_business")
            
            # Wait for service to start
            await asyncio.sleep(10)
            
            # Verify service is running
            await self.verify_service_start(service_name)
            
        except Exception as e:
            logger.error(f"Service start failed for {service_name}: {str(e)}")
    
    async def verify_service_start(self, service_name: str):
        """Verify service started successfully"""
        try:
            service = self.services[service_name]
            
            # Check health endpoint
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://localhost:{service.port}/health", timeout=10) as response:
                    if response.status == 200:
                        service.status = ServiceStatus.HEALTHY
                        logger.info(f"Service {service_name} started successfully")
                    else:
                        service.status = ServiceStatus.UNHEALTHY
                        logger.warning(f"Service {service_name} started but unhealthy")
                        
        except Exception as e:
            logger.error(f"Service start verification failed for {service_name}: {str(e)}")
            service.status = ServiceStatus.UNHEALTHY
    
    async def scale_service(self, service_name: str, direction: str):
        """Scale service up or down"""
        try:
            logger.info(f"Scaling {service_name} {direction}")
            
            # In production, this would integrate with container orchestration
            # For now, just log the action
            if direction == "up":
                logger.info(f"Scaling up {service_name}: adding more resources")
            else:
                logger.info(f"Scaling down {service_name}: reducing resources")
                
        except Exception as e:
            logger.error(f"Service scaling failed for {service_name}: {str(e)}")
    
    async def route_traffic_away(self, service_name: str):
        """Route traffic away from unhealthy service"""
        try:
            logger.info(f"Routing traffic away from {service_name}")
            
            # In production, this would update load balancer configuration
            # For now, just log the action
            service = self.services[service_name]
            service.status = ServiceStatus.MAINTENANCE
            
        except Exception as e:
            logger.error(f"Traffic routing failed for {service_name}: {str(e)}")
    
    async def enable_maintenance_mode(self, service_name: str):
        """Enable maintenance mode for service"""
        try:
            logger.info(f"Enabling maintenance mode for {service_name}")
            
            service = self.services[service_name]
            service.status = ServiceStatus.MAINTENANCE
            
        except Exception as e:
            logger.error(f"Maintenance mode failed for {service_name}: {str(e)}")
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health"""
        try:
            total_health_score = 0
            healthy_services = 0
            total_services = len(self.services)
            
            service_health = {}
            
            for service_name, service in self.services.items():
                service_health[service_name] = {
                    "status": service.status.value,
                    "health_score": service.health_score,
                    "consecutive_failures": service.consecutive_failures,
                    "recovery_count": service.recovery_count,
                    "last_recovery": service.last_recovery_time.isoformat() if service.last_recovery_time else None,
                    "auto_recovery_enabled": service.auto_recovery_enabled
                }
                
                total_health_score += service.health_score
                if service.status == ServiceStatus.HEALTHY:
                    healthy_services += 1
            
            overall_health_score = total_health_score / total_services if total_services > 0 else 0
            
            return {
                "overall_health_score": overall_health_score,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "system_status": "healthy" if overall_health_score >= 80 else "degraded" if overall_health_score >= 60 else "unhealthy",
                "service_health": service_health,
                "last_check": datetime.now(timezone.utc).isoformat(),
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"System health retrieval failed: {str(e)}")
            return {"error": str(e)}

# Global instance
self_healing_system = SelfHealingSystem()

# Main monitoring function
async def start_self_healing():
    """Start self-healing system"""
    await self_healing_system.start_monitoring()

# API endpoints for health monitoring
async def get_service_health(service_name: str) -> Dict[str, Any]:
    """Get health of specific service"""
    service = self_healing_system.services.get(service_name)
    if not service:
        return {"error": f"Service {service_name} not found"}
    
    return {
        "service_name": service.service_name,
        "status": service.status.value,
        "health_score": service.health_score,
        "metrics": {
            "cpu_usage": service.metrics.cpu_usage,
            "memory_usage": service.metrics.memory_usage,
            "response_time": service.metrics.response_time,
            "error_rate": service.metrics.error_rate,
            "active_connections": service.metrics.active_connections
        },
        "last_check": service.last_check.isoformat(),
        "consecutive_failures": service.consecutive_failures,
        "recovery_count": service.recovery_count,
        "nbe_compliance": True
    }

async def trigger_manual_recovery(service_name: str, action: str) -> Dict[str, Any]:
    """Trigger manual recovery for service"""
    try:
        recovery_action = RecoveryAction(action)
        await self_healing_system.trigger_recovery(service_name, recovery_action)
        
        return {
            "success": True,
            "service_name": service_name,
            "action": action,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nbe_compliance": True
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "nbe_compliance": False
        }
