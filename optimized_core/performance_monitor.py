"""
PERFORMANCE MONITORING SYSTEM - DEDAN WORLDMINE
Real-time performance monitoring, alerting, and optimization

Features:
- Real-time metrics collection
- Performance alerting
- Resource monitoring
- API performance tracking
- Database performance monitoring
- Cache performance tracking
- System resource monitoring
- Automated optimization suggestions
"""

import asyncio
import psutil
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque
import aioredis
import aiofiles
from pathlib import Path
import numpy as np
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics data structure"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    memory_used_gb: float
    memory_available_gb: float
    disk_usage_percent: float
    disk_read_mb_s: float
    disk_write_mb_s: float
    network_sent_mb_s: float
    network_recv_mb_s: float
    active_connections: int
    process_count: int
    load_average: List[float]
    temperature: Optional[float] = None

@dataclass
class APIMetrics:
    """API performance metrics"""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    request_size: int
    response_size: int
    user_agent: str
    ip_address: str
    timestamp: datetime

@dataclass
class DatabaseMetrics:
    """Database performance metrics"""
    query_type: str
    query_time: float
    rows_affected: int
    connections_active: int
    connections_idle: int
    cache_hit_rate: float
    index_usage: Dict[str, float]
    timestamp: datetime

@dataclass
class CacheMetrics:
    """Cache performance metrics"""
    cache_type: str
    operation: str  # get, set, delete
    key: str
    hit: bool
    size: int
    ttl: int
    response_time: float
    timestamp: datetime

class PerformanceMonitor:
    """Advanced performance monitoring system"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        self.monitoring = False
        
        # Metrics storage
        self.system_metrics = deque(maxlen=1000)
        self.api_metrics = deque(maxlen=10000)
        self.db_metrics = deque(maxlen=5000)
        self.cache_metrics = deque(maxlen=10000)
        
        # Prometheus metrics
        self.prometheus_metrics = {
            'cpu_usage': Gauge('worldmine_cpu_usage_percent', 'CPU usage percentage'),
            'memory_usage': Gauge('worldmine_memory_usage_percent', 'Memory usage percentage'),
            'disk_usage': Gauge('worldmine_disk_usage_percent', 'Disk usage percentage'),
            'api_requests_total': Counter('worldmine_api_requests_total', 'Total API requests', ['method', 'endpoint', 'status']),
            'api_request_duration': Histogram('worldmine_api_request_duration_seconds', 'API request duration', ['method', 'endpoint']),
            'db_query_duration': Histogram('worldmine_db_query_duration_seconds', 'Database query duration', ['query_type']),
            'cache_operations_total': Counter('worldmine_cache_operations_total', 'Total cache operations', ['operation', 'cache_type', 'hit']),
            'active_connections': Gauge('worldmine_active_connections', 'Active connections'),
            'system_load': Gauge('worldmine_system_load', 'System load average')
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'disk_warning': 85.0,
            'disk_critical': 95.0,
            'api_response_time_warning': 1.0,
            'api_response_time_critical': 2.0,
            'db_query_time_warning': 0.5,
            'db_query_time_critical': 1.0,
            'cache_hit_rate_warning': 70.0,
            'cache_hit_rate_critical': 50.0
        }
        
        # Performance history for trend analysis
        self.performance_history = {
            'hourly': deque(maxlen=24),
            'daily': deque(maxlen=30),
            'weekly': deque(maxlen=12)
        }
        
        logger.info("Performance monitor initialized")
    
    async def initialize(self):
        """Initialize performance monitoring"""
        try:
            # Initialize Redis
            self.redis = aioredis.from_url(self.redis_url)
            
            # Start Prometheus metrics server
            start_http_server(9090, '/metrics')
            
            # Start monitoring
            self.monitoring = True
            
            logger.info("Performance monitoring started")
            
        except Exception as e:
            logger.error(f"Failed to initialize performance monitor: {e}")
            raise
    
    async def start_monitoring(self):
        """Start continuous performance monitoring"""
        if not self.monitoring:
            await self.initialize()
        
        # Start monitoring tasks
        tasks = [
            asyncio.create_task(self._monitor_system_metrics()),
            asyncio.create_task(self._monitor_api_metrics()),
            asyncio.create_task(self._monitor_database_metrics()),
            asyncio.create_task(self._monitor_cache_metrics()),
            asyncio.create_task(self._analyze_performance_trends()),
            asyncio.create_task(self._check_alerts()),
            asyncio.create_task(self._generate_optimization_suggestions())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _monitor_system_metrics(self):
        """Monitor system performance metrics"""
        while self.monitoring:
            try:
                # Collect system metrics
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=psutil.cpu_percent(interval=1),
                    memory_percent=psutil.virtual_memory().percent,
                    memory_used_gb=psutil.virtual_memory().used / (1024**3),
                    memory_available_gb=psutil.virtual_memory().available / (1024**3),
                    disk_usage_percent=psutil.disk_usage('/').percent,
                    disk_read_mb_s=psutil.disk_io_counters().read_bytes / (1024**2) if hasattr(psutil.disk_io_counters(), 'read_bytes') else 0,
                    disk_write_mb_s=psutil.disk_io_counters().write_bytes / (1024**2) if hasattr(psutil.disk_io_counters(), 'write_bytes') else 0,
                    network_sent_mb_s=psutil.net_io_counters().bytes_sent / (1024**2) if hasattr(psutil.net_io_counters(), 'bytes_sent') else 0,
                    network_recv_mb_s=psutil.net_io_counters().bytes_recv / (1024**2) if hasattr(psutil.net_io_counters(), 'bytes_recv') else 0,
                    active_connections=len(psutil.net_connections()),
                    process_count=len(psutil.pids()),
                    load_average=list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else [0, 0, 0]
                )
                
                # Store metrics
                self.system_metrics.append(metrics)
                
                # Update Prometheus metrics
                self.prometheus_metrics['cpu_usage'].set(metrics.cpu_percent)
                self.prometheus_metrics['memory_usage'].set(metrics.memory_percent)
                self.prometheus_metrics['disk_usage'].set(metrics.disk_usage_percent)
                self.prometheus_metrics['active_connections'].set(metrics.active_connections)
                if metrics.load_average:
                    self.prometheus_metrics['system_load'].set(metrics.load_average[0])
                
                # Store in Redis for external monitoring
                await self._store_metrics('system', asdict(metrics))
                
                # Check for alerts
                await self._check_system_alerts(metrics)
                
            except Exception as e:
                logger.error(f"System monitoring error: {e}")
            
            await asyncio.sleep(30)  # Monitor every 30 seconds
    
    async def _monitor_api_metrics(self):
        """Monitor API performance metrics"""
        # This would be called by API endpoints
        # For now, we'll simulate some metrics
        while self.monitoring:
            try:
                # Simulate API metrics collection
                # In real implementation, this would collect from API middleware
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"API monitoring error: {e}")
    
    async def _monitor_database_metrics(self):
        """Monitor database performance metrics"""
        while self.monitoring:
            try:
                # Simulate database metrics collection
                # In real implementation, this would connect to database stats
                metrics = DatabaseMetrics(
                    timestamp=datetime.now(),
                    query_type="SELECT",
                    query_time=0.05,
                    rows_affected=100,
                    connections_active=15,
                    connections_idle=5,
                    cache_hit_rate=85.5,
                    index_usage={"primary": 95.0, "secondary": 87.0}
                )
                
                self.db_metrics.append(metrics)
                
                # Update Prometheus metrics
                self.prometheus_metrics['db_query_duration'].labels(query_type=metrics.query_type).observe(metrics.query_time)
                
                # Store in Redis
                await self._store_metrics('database', asdict(metrics))
                
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Database monitoring error: {e}")
    
    async def _monitor_cache_metrics(self):
        """Monitor cache performance metrics"""
        while self.monitoring:
            try:
                # Simulate cache metrics collection
                # In real implementation, this would connect to cache stats
                metrics = CacheMetrics(
                    timestamp=datetime.now(),
                    cache_type="redis",
                    operation="get",
                    key="minerals:all",
                    hit=True,
                    size=1024,
                    ttl=300,
                    response_time=0.001
                )
                
                self.cache_metrics.append(metrics)
                
                # Update Prometheus metrics
                self.prometheus_metrics['cache_operations_total'].labels(
                    operation=metrics.operation,
                    cache_type=metrics.cache_type,
                    hit=str(metrics.hit)
                ).inc()
                
                # Store in Redis
                await self._store_metrics('cache', asdict(metrics))
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Cache monitoring error: {e}")
    
    async def _store_metrics(self, metric_type: str, metrics: Dict[str, Any]):
        """Store metrics in Redis"""
        try:
            key = f"metrics:{metric_type}:{int(time.time())}"
            await self.redis.setex(key, 3600, json.dumps(metrics, default=str))
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    async def _check_system_alerts(self, metrics: PerformanceMetrics):
        """Check for system performance alerts"""
        alerts = []
        
        # CPU alerts
        if metrics.cpu_percent >= self.alert_thresholds['cpu_critical']:
            alerts.append({
                'type': 'cpu_critical',
                'message': f"CPU usage critical: {metrics.cpu_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'critical'
            })
        elif metrics.cpu_percent >= self.alert_thresholds['cpu_warning']:
            alerts.append({
                'type': 'cpu_warning',
                'message': f"CPU usage warning: {metrics.cpu_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'warning'
            })
        
        # Memory alerts
        if metrics.memory_percent >= self.alert_thresholds['memory_critical']:
            alerts.append({
                'type': 'memory_critical',
                'message': f"Memory usage critical: {metrics.memory_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'critical'
            })
        elif metrics.memory_percent >= self.alert_thresholds['memory_warning']:
            alerts.append({
                'type': 'memory_warning',
                'message': f"Memory usage warning: {metrics.memory_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'warning'
            })
        
        # Disk alerts
        if metrics.disk_usage_percent >= self.alert_thresholds['disk_critical']:
            alerts.append({
                'type': 'disk_critical',
                'message': f"Disk usage critical: {metrics.disk_usage_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'critical'
            })
        elif metrics.disk_usage_percent >= self.alert_thresholds['disk_warning']:
            alerts.append({
                'type': 'disk_warning',
                'message': f"Disk usage warning: {metrics.disk_usage_percent:.1f}%",
                'timestamp': metrics.timestamp,
                'severity': 'warning'
            })
        
        # Send alerts if any
        if alerts:
            await self._send_alerts(alerts)
    
    async def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send performance alerts"""
        for alert in alerts:
            logger.warning(f"PERFORMANCE ALERT: {alert['message']}")
            
            # Store alert in Redis
            alert_key = f"alerts:{alert['type']}:{int(time.time())}"
            await self.redis.setex(alert_key, 86400, json.dumps(alert))
            
            # In real implementation, send to alerting system
            # e.g., Slack, email, PagerDuty, etc.
    
    async def _analyze_performance_trends(self):
        """Analyze performance trends over time"""
        while self.monitoring:
            try:
                current_time = datetime.now()
                
                # Hourly aggregation
                if len(self.system_metrics) > 0:
                    recent_metrics = [m for m in self.system_metrics 
                                   if m.timestamp > current_time - timedelta(hours=1)]
                    
                    if recent_metrics:
                        hourly_avg = {
                            'timestamp': current_time,
                            'cpu_avg': np.mean([m.cpu_percent for m in recent_metrics]),
                            'memory_avg': np.mean([m.memory_percent for m in recent_metrics]),
                            'disk_avg': np.mean([m.disk_usage_percent for m in recent_metrics])
                        }
                        
                        self.performance_history['hourly'].append(hourly_avg)
                
                # Daily aggregation
                if len(self.performance_history['hourly']) >= 24:
                    daily_avg = {
                        'timestamp': current_time,
                        'cpu_avg': np.mean([h['cpu_avg'] for h in list(self.performance_history['hourly'])[-24:]]),
                        'memory_avg': np.mean([h['memory_avg'] for h in list(self.performance_history['hourly'])[-24:]]),
                        'disk_avg': np.mean([h['disk_avg'] for h in list(self.performance_history['hourly'])[-24:]])
                    }
                    
                    self.performance_history['daily'].append(daily_avg)
                
                # Store trends in Redis
                await self._store_trends()
                
                await asyncio.sleep(3600)  # Analyze every hour
                
            except Exception as e:
                logger.error(f"Trend analysis error: {e}")
    
    async def _store_trends(self):
        """Store performance trends in Redis"""
        try:
            trends = {
                'hourly': [asdict(t) for t in list(self.performance_history['hourly'])[-24:]],
                'daily': [asdict(t) for t in list(self.performance_history['daily'])[-30:]],
                'weekly': [asdict(t) for t in list(self.performance_history['weekly'])[-12:]]
            }
            
            await self.redis.setex('performance_trends', 86400, json.dumps(trends, default=str))
        except Exception as e:
            logger.error(f"Failed to store trends: {e}")
    
    async def _check_alerts(self):
        """Check for performance alerts"""
        while self.monitoring:
            try:
                # Check various performance conditions
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Alert checking error: {e}")
    
    async def _generate_optimization_suggestions(self):
        """Generate optimization suggestions based on performance data"""
        while self.monitoring:
            try:
                suggestions = []
                
                # Analyze recent metrics
                if len(self.system_metrics) > 10:
                    recent_metrics = list(self.system_metrics)[-10:]
                    
                    # CPU optimization suggestions
                    avg_cpu = np.mean([m.cpu_percent for m in recent_metrics])
                    if avg_cpu > 80:
                        suggestions.append({
                            'type': 'cpu_optimization',
                            'message': 'High CPU usage detected. Consider scaling up or optimizing CPU-intensive operations.',
                            'priority': 'high',
                            'timestamp': datetime.now()
                        })
                    
                    # Memory optimization suggestions
                    avg_memory = np.mean([m.memory_percent for m in recent_metrics])
                    if avg_memory > 85:
                        suggestions.append({
                            'type': 'memory_optimization',
                            'message': 'High memory usage detected. Consider increasing memory or optimizing memory usage.',
                            'priority': 'high',
                            'timestamp': datetime.now()
                        })
                    
                    # Disk optimization suggestions
                    avg_disk = np.mean([m.disk_usage_percent for m in recent_metrics])
                    if avg_disk > 85:
                        suggestions.append({
                            'type': 'disk_optimization',
                            'message': 'High disk usage detected. Consider cleaning up disk or expanding storage.',
                            'priority': 'medium',
                            'timestamp': datetime.now()
                        })
                
                # Store suggestions
                if suggestions:
                    await self._store_suggestions(suggestions)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Optimization suggestion error: {e}")
    
    async def _store_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Store optimization suggestions"""
        try:
            for suggestion in suggestions:
                suggestion_key = f"suggestions:{suggestion['type']}:{int(time.time())}"
                await self.redis.setex(suggestion_key, 3600, json.dumps(suggestion, default=str))
                
                logger.info(f"OPTIMIZATION SUGGESTION: {suggestion['message']}")
        except Exception as e:
            logger.error(f"Failed to store suggestions: {e}")
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        if not self.system_metrics:
            return {}
        
        latest = self.system_metrics[-1]
        return asdict(latest)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.system_metrics:
            return {}
        
        recent_metrics = list(self.system_metrics)[-100:]  # Last 100 measurements
        
        return {
            'current': asdict(self.system_metrics[-1]),
            'averages': {
                'cpu_percent': np.mean([m.cpu_percent for m in recent_metrics]),
                'memory_percent': np.mean([m.memory_percent for m in recent_metrics]),
                'disk_usage_percent': np.mean([m.disk_usage_percent for m in recent_metrics])
            },
            'maximums': {
                'cpu_percent': np.max([m.cpu_percent for m in recent_metrics]),
                'memory_percent': np.max([m.memory_percent for m in recent_metrics]),
                'disk_usage_percent': np.max([m.disk_usage_percent for m in recent_metrics])
            },
            'minimums': {
                'cpu_percent': np.min([m.cpu_percent for m in recent_metrics]),
                'memory_percent': np.min([m.memory_percent for m in recent_metrics]),
                'disk_usage_percent': np.min([m.disk_usage_percent for m in recent_metrics])
            },
            'trends': {
                'hourly': [asdict(t) for t in list(self.performance_history['hourly'])[-24:]],
                'daily': [asdict(t) for t in list(self.performance_history['daily'])[-7:]]
            },
            'alerts_count': len(await self._get_recent_alerts()),
            'suggestions_count': len(await self._get_recent_suggestions())
        }
    
    async def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            alert_keys = await self.redis.keys('alerts:*')
            alerts = []
            
            for key in alert_keys[-10:]:  # Last 10 alerts
                alert_data = await self.redis.get(key)
                if alert_data:
                    alerts.append(json.loads(alert_data))
            
            return alerts
        except Exception as e:
            logger.error(f"Failed to get recent alerts: {e}")
            return []
    
    async def _get_recent_suggestions(self) -> List[Dict[str, Any]]:
        """Get recent optimization suggestions"""
        try:
            suggestion_keys = await self.redis.keys('suggestions:*')
            suggestions = []
            
            for key in suggestion_keys[-10:]:  # Last 10 suggestions
                suggestion_data = await self.redis.get(key)
                if suggestion_data:
                    suggestions.append(json.loads(suggestion_data))
            
            return suggestions
        except Exception as e:
            logger.error(f"Failed to get recent suggestions: {e}")
            return []
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring = False
        logger.info("Performance monitoring stopped")

# Initialize performance monitor
performance_monitor = PerformanceMonitor()

# Example usage
async def main():
    """Example usage of performance monitoring"""
    try:
        # Start monitoring
        await performance_monitor.start_monitoring()
        
        # Get current metrics
        current_metrics = performance_monitor.get_current_metrics()
        print(f"Current metrics: {current_metrics}")
        
        # Get performance summary
        summary = performance_monitor.get_performance_summary()
        print(f"Performance summary: {summary}")
        
    except KeyboardInterrupt:
        await performance_monitor.stop_monitoring()
        logger.info("Performance monitoring stopped by user")

if __name__ == "__main__":
    asyncio.run(main())
