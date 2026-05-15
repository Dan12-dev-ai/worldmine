"""
Monitoring Agent - 24/7 alerts, auto-detect anomalies before users notice
Replaces 1 Monitoring lead + 5 monitoring engineers
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import numpy as np
from ..agent_framework import BaseAIAgent, AgentRole, MessageType, Priority, AgentCapability

@dataclass
class MonitoringAlert:
    """Monitoring alert"""
    alert_id: str
    severity: str
    source: str
    metric: str
    current_value: float
    threshold: float
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    false_positive: bool = False

@dataclass
class AnomalyDetection:
    """Anomaly detection result"""
    anomaly_id: str
    service: str
    anomaly_type: str
    confidence: float
    impact_level: str
    predicted_failure: bool
    detected_at: datetime

class MonitoringAgent(BaseAIAgent):
    """Monitoring Agent - 24/7 alerts and anomaly detection"""
    
    def __init__(self):
        super().__init__(
            agent_id="monitoring_001",
            role=AgentRole.MONITORING,
            name="Monitoring Alert System",
            description="24/7 alerts, auto-detect anomalies before users notice"
        )
        
        self.monitoring_alerts: List[MonitoringAlert] = []
        self.anomaly_detections: List[AnomalyDetection] = []
        self.metrics_thresholds: Dict[str, Dict[str, float]] = {}
        self.service_health: Dict[str, Dict[str, Any]] = {}
        
    async def initialize(self) -> bool:
        """Initialize monitoring agent"""
        try:
            await self._setup_monitoring_systems()
            await self._configure_thresholds()
            asyncio.create_task(self._alert_monitoring_loop())
            asyncio.create_task(self._anomaly_detection_loop())
            asyncio.create_task(self._health_check_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Monitoring Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get monitoring agent capabilities"""
        return [
            AgentCapability(
                name="24_7_monitoring",
                description="24/7 monitoring with instant alerts",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.99, "response_time": 0.001},
                dependencies=["metrics_collector", "alert_engine"]
            ),
            AgentCapability(
                name="anomaly_detection",
                description="Auto-detect anomalies before users notice",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 0.5},
                dependencies=["ml_models", "pattern_recognition"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process monitoring tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        elif task_type == 'request':
            return await self._handle_request(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle monitoring commands"""
        if subject == "update_thresholds":
            return await self._update_thresholds(content)
        elif subject == "configure_alerts":
            return await self._configure_alerts(content)
        elif subject == "check_service_health":
            return await self._check_service_health(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _update_thresholds(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update monitoring thresholds"""
        service = content.get('service', 'global')
        thresholds = content.get('thresholds', {})
        
        if service not in self.metrics_thresholds:
            self.metrics_thresholds[service] = {}
        
        self.metrics_thresholds[service].update(thresholds)
        
        return {
            'service': service,
            'thresholds_updated': list(thresholds.keys()),
            'new_thresholds': thresholds,
            'status': 'updated'
        }
    
    async def _configure_alerts(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Configure alert settings"""
        alert_config = content.get('alert_config', {})
        
        # Update alert configuration
        # This would integrate with alert systems
        
        return {
            'alert_config': alert_config,
            'channels_configured': alert_config.get('channels', []),
            'escalation_rules': alert_config.get('escalation_rules', []),
            'status': 'configured'
        }
    
    async def _check_service_health(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check service health status"""
        service = content.get('service', 'all')
        
        if service == 'all':
            health_status = await self._get_all_service_health()
        else:
            health_status = await self._get_service_health(service)
        
        return {
            'service': service,
            'health_status': health_status,
            'checked_at': datetime.utcnow().isoformat()
        }
    
    async def _alert_monitoring_loop(self):
        """Continuous alert monitoring loop"""
        while self.is_active:
            try:
                # Collect metrics from all services
                metrics = await self._collect_metrics()
                
                # Check threshold violations
                threshold_violations = await self._check_threshold_violations(metrics)
                
                # Process violations
                for violation in threshold_violations:
                    alert = MonitoringAlert(
                        alert_id=f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        severity=violation['severity'],
                        source=violation['source'],
                        metric=violation['metric'],
                        current_value=violation['current_value'],
                        threshold=violation['threshold'],
                        detected_at=datetime.utcnow()
                    )
                    
                    self.monitoring_alerts.append(alert)
                    
                    # Send alert to relevant agents
                    await self._send_alert(alert)
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in alert monitoring loop: {e}")
                await asyncio.sleep(10)
    
    async def _anomaly_detection_loop(self):
        """Continuous anomaly detection loop"""
        while self.is_active:
            try:
                # Get historical metrics
                historical_metrics = await self._get_historical_metrics()
                
                # Detect anomalies
                anomalies = await self._detect_anomalies(historical_metrics)
                
                # Process anomalies
                for anomaly in anomalies:
                    detection = AnomalyDetection(
                        anomaly_id=f"anomaly_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        service=anomaly['service'],
                        anomaly_type=anomaly['type'],
                        confidence=anomaly['confidence'],
                        impact_level=anomaly['impact_level'],
                        predicted_failure=anomaly['predicted_failure'],
                        detected_at=datetime.utcnow()
                    )
                    
                    self.anomaly_detections.append(detection)
                    
                    # Send anomaly alert
                    await self._send_anomaly_alert(detection)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in anomaly detection loop: {e}")
                await asyncio.sleep(20)
    
    async def _health_check_loop(self):
        """Continuous health check loop"""
        while self.is_active:
            try:
                # Check health of all services
                health_status = await self._get_all_service_health()
                
                # Update service health
                self.service_health.update(health_status)
                
                # Alert on unhealthy services
                for service, health in health_status.items():
                    if not health['healthy']:
                        await self._send_health_alert(service, health)
                
                await asyncio.sleep(120)  # Check every 2 minutes
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(30)
    
    async def _collect_metrics(self) -> Dict[str, Dict[str, float]]:
        """Collect metrics from all services"""
        # Mock metrics collection
        return {
            'api_server': {
                'response_time': np.random.uniform(0.01, 0.1),  # 10-100ms
                'error_rate': np.random.uniform(0.001, 0.01),  # 0.1-1%
                'throughput': np.random.uniform(1000, 10000),  # requests/second
                'cpu_usage': np.random.uniform(0.2, 0.8),  # 20-80%
                'memory_usage': np.random.uniform(0.3, 0.7)  # 30-70%
            },
            'database': {
                'query_time': np.random.uniform(0.001, 0.05),  # 1-50ms
                'connection_count': np.random.randint(50, 500),
                'disk_usage': np.random.uniform(0.4, 0.8),  # 40-80%
                'cache_hit_ratio': np.random.uniform(0.8, 0.95)  # 80-95%
            },
            'trading_engine': {
                'orders_per_second': np.random.uniform(10, 100),
                'settlement_time': np.random.uniform(0.001, 0.01),  # 1-10ms
                'liquidity_ratio': np.random.uniform(0.8, 0.99),
                'error_rate': np.random.uniform(0.0001, 0.001)  # 0.01-0.1%
            },
            'blockchain': {
                'transaction_time': np.random.uniform(0.5, 5.0),  # 0.5-5s
                'gas_price': np.random.uniform(10, 100),  # 10-100 Gwei
                'confirmation_time': np.random.uniform(10, 60),  # 10-60s
                'success_rate': np.random.uniform(0.95, 0.99)  # 95-99%
            }
        }
    
    async def _check_threshold_violations(self, metrics: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Check for threshold violations"""
        violations = []
        
        for service, service_metrics in metrics.items():
            service_thresholds = self.metrics_thresholds.get(service, {})
            
            for metric, value in service_metrics.items():
                if metric in service_thresholds:
                    threshold = service_thresholds[metric]
                    
                    # Check if threshold violated
                    if metric in ['response_time', 'query_time', 'transaction_time']:
                        if value > threshold:  # Higher is worse
                            violations.append({
                                'source': service,
                                'metric': metric,
                                'current_value': value,
                                'threshold': threshold,
                                'severity': 'high' if value > threshold * 2 else 'medium'
                            })
                    
                    elif metric in ['error_rate', 'cpu_usage', 'memory_usage', 'disk_usage']:
                        if value > threshold:  # Higher is worse
                            violations.append({
                                'source': service,
                                'metric': metric,
                                'current_value': value,
                                'threshold': threshold,
                                'severity': 'critical' if value > threshold * 1.5 else 'high'
                            })
                    
                    elif metric in ['throughput', 'cache_hit_ratio', 'liquidity_ratio', 'success_rate']:
                        if value < threshold:  # Lower is worse
                            violations.append({
                                'source': service,
                                'metric': metric,
                                'current_value': value,
                                'threshold': threshold,
                                'severity': 'high' if value < threshold * 0.5 else 'medium'
                            })
        
        return violations
    
    async def _detect_anomalies(self, historical_metrics: Dict[str, List[float]]) -> List[Dict[str, Any]]:
        """Detect anomalies in metrics"""
        anomalies = []
        
        for service, metric_history in historical_metrics.items():
            if len(metric_history) < 10:
                continue
            
            # Simple anomaly detection using statistical methods
            mean = np.mean(metric_history)
            std = np.std(metric_history)
            current_value = metric_history[-1]
            
            # Z-score anomaly detection
            z_score = abs((current_value - mean) / std) if std > 0 else 0
            
            if z_score > 3:  # 3 sigma threshold
                anomalies.append({
                    'service': service,
                    'type': 'statistical_outlier',
                    'confidence': min(z_score / 3, 1.0),
                    'impact_level': 'high' if z_score > 5 else 'medium',
                    'predicted_failure': z_score > 4,
                    'current_value': current_value,
                    'expected_range': [mean - 2*std, mean + 2*std]
                })
            
            # Trend anomaly detection
            if len(metric_history) >= 20:
                recent_trend = np.polyfit(range(10), metric_history[-10:], 1)[0]
                if abs(recent_trend) > std * 0.5:
                    anomalies.append({
                        'service': service,
                        'type': 'trend_anomaly',
                        'confidence': min(abs(recent_trend) / (std * 0.5), 1.0),
                        'impact_level': 'medium' if abs(recent_trend) > std else 'low',
                        'predicted_failure': False,
                        'trend': 'increasing' if recent_trend > 0 else 'decreasing',
                        'trend_strength': abs(recent_trend)
                    })
        
        return anomalies
    
    async def _get_historical_metrics(self) -> Dict[str, List[float]]:
        """Get historical metrics for anomaly detection"""
        # Mock historical data
        return {
            'api_server_response_time': [np.random.uniform(0.01, 0.1) for _ in range(100)],
            'database_query_time': [np.random.uniform(0.001, 0.05) for _ in range(100)],
            'trading_engine_orders_per_second': [np.random.uniform(10, 100) for _ in range(100)],
            'blockchain_transaction_time': [np.random.uniform(0.5, 5.0) for _ in range(100)]
        }
    
    async def _get_all_service_health(self) -> Dict[str, Dict[str, Any]]:
        """Get health status of all services"""
        services = ['api_server', 'database', 'trading_engine', 'blockchain', 'cache']
        health_status = {}
        
        for service in services:
            health_status[service] = await self._get_service_health(service)
        
        return health_status
    
    async def _get_service_health(self, service: str) -> Dict[str, Any]:
        """Get health status of specific service"""
        # Mock health check
        is_healthy = np.random.random() > 0.02  # 98% uptime
        
        return {
            'healthy': is_healthy,
            'response_time': np.random.uniform(0.01, 0.2),
            'last_check': datetime.utcnow().isoformat(),
            'uptime_percentage': 99.8 if is_healthy else 95.0,
            'issues': [] if is_healthy else ['high_response_time']
        }
    
    async def _send_alert(self, alert: MonitoringAlert):
        """Send monitoring alert to relevant agents"""
        # Determine alert recipients
        if alert.source == 'api_server':
            recipients = ['api_001', 'infrastructure_001']
        elif alert.source == 'database':
            recipients = ['database_001', 'infrastructure_001']
        elif alert.source == 'trading_engine':
            recipients = ['trading_001', 'performance_001']
        elif alert.source == 'blockchain':
            recipients = ['blockchain_001', 'security_001']
        else:
            recipients = ['ceo_001', 'ciso_001']
        
        # Send alert to all recipients
        for recipient in recipients:
            await self.send_message(
                recipient,
                MessageType.ALERT,
                f"Monitoring Alert: {alert.source}",
                {
                    'alert_id': alert.alert_id,
                    'severity': alert.severity,
                    'source': alert.source,
                    'metric': alert.metric,
                    'current_value': alert.current_value,
                    'threshold': alert.threshold,
                    'detected_at': alert.detected_at.isoformat()
                },
                priority=Priority.HIGH if alert.severity in ['critical', 'high'] else Priority.NORMAL
            )
    
    async def _send_anomaly_alert(self, detection: AnomalyDetection):
        """Send anomaly detection alert"""
        recipients = ['ceo_001', 'cto_001', 'ciso_001']
        
        await self.send_message(
            'ceo_001',
            MessageType.ALERT,
            f"Anomaly Detected: {detection.service}",
            {
                'anomaly_id': detection.anomaly_id,
                'service': detection.service,
                'anomaly_type': detection.anomaly_type,
                'confidence': detection.confidence,
                'impact_level': detection.impact_level,
                'predicted_failure': detection.predicted_failure,
                'detected_at': detection.detected_at.isoformat()
            },
            priority=Priority.HIGH if detection.impact_level == 'high' else Priority.NORMAL
        )
    
    async def _send_health_alert(self, service: str, health: Dict[str, Any]):
        """Send health alert for unhealthy service"""
        recipients = ['infrastructure_001', 'devops_001']
        
        await self.send_message(
            'infrastructure_001',
            MessageType.ALERT,
            f"Service Unhealthy: {service}",
            {
                'service': service,
                'health_status': health,
                'alert_time': datetime.utcnow().isoformat()
            },
            priority=Priority.HIGH
        )
    
    async def _setup_monitoring_systems(self):
        """Setup monitoring systems"""
        # Initialize monitoring for all services
        services = ['api_server', 'database', 'trading_engine', 'blockchain', 'cache']
        
        for service in services:
            self.service_health[service] = {
                'healthy': True,
                'last_check': datetime.utcnow(),
                'uptime_percentage': 100.0
            }
    
    async def _configure_thresholds(self):
        """Configure default monitoring thresholds"""
        default_thresholds = {
            'api_server': {
                'response_time': 0.1,  # 100ms
                'error_rate': 0.01,  # 1%
                'cpu_usage': 0.8,  # 80%
                'memory_usage': 0.8,  # 80%
                'throughput': 1000  # minimum 1000 RPS
            },
            'database': {
                'query_time': 0.05,  # 50ms
                'connection_count': 400,  # max connections
                'disk_usage': 0.8,  # 80%
                'cache_hit_ratio': 0.8  # minimum 80%
            },
            'trading_engine': {
                'orders_per_second': 50,  # minimum 50 ops/sec
                'settlement_time': 0.01,  # 10ms
                'liquidity_ratio': 0.8,  # minimum 80%
                'error_rate': 0.001  # maximum 0.1%
            },
            'blockchain': {
                'transaction_time': 3.0,  # 3 seconds
                'gas_price': 50,  # 50 Gwei
                'confirmation_time': 30,  # 30 seconds
                'success_rate': 0.95  # minimum 95%
            }
        }
        
        self.metrics_thresholds = default_thresholds

monitoring_agent = MonitoringAgent()
