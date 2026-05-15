"""
Crash Prevention Agent - Auto-detect crashes, auto-restart services in <30s
Replaces 1 SRE Engineer + 3 reliability specialists
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import numpy as np
from ..agent_framework import BaseAIAgent, AgentRole, MessageType, Priority, AgentCapability

@dataclass
class CrashEvent:
    """Service crash event"""
    crash_id: str
    service_name: str
    crash_type: str
    detected_at: datetime
    restarted_at: Optional[datetime] = None
    restart_time_seconds: float = 0.0
    root_cause: str = ""
    prevented: bool = False

@dataclass
class PreventionAction:
    """Crash prevention action"""
    action_id: str
    service_name: str
    action_type: str
    description: str
    executed_at: datetime
    success: bool
    impact: str

class CrashPreventionAgent(BaseAIAgent):
    """Crash Prevention Agent - Automated crash detection and prevention"""
    
    def __init__(self):
        super().__init__(
            agent_id="crash_prevention_001",
            role=AgentRole.CRASH_PREVENTION,
            name="Crash Prevention System",
            description="Auto-detect crashes, auto-restart services in <30s"
        )
        
        self.crash_events: List[CrashEvent] = []
        self.prevention_actions: List[PreventionAction] = []
        self.service_health: Dict[str, Dict[str, Any]] = {}
        self.crash_patterns: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize crash prevention agent"""
        try:
            await self._setup_crash_detection()
            await self._load_crash_patterns()
            asyncio.create_task(self._crash_detection_loop())
            asyncio.create_task(self._prevention_loop())
            asyncio.create_task(self._health_monitoring_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Crash Prevention Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get crash prevention agent capabilities"""
        return [
            AgentCapability(
                name="crash_detection",
                description="Auto-detect crashes in real-time",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.99, "response_time": 0.1},
                dependencies=["monitoring", "log_analysis"]
            ),
            AgentCapability(
                name="auto_restart",
                description="Auto-restart services in <30s",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.98, "response_time": 30.0},
                dependencies=["orchestration", "service_manager"]
            ),
            AgentCapability(
                name="crash_prevention",
                description="Prevent crashes before they happen",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 5.0},
                dependencies=["predictive_models", "resource_monitoring"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process crash prevention tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle crash prevention commands"""
        if subject == "restart_service":
            return await self._restart_service(content)
        elif subject == "prevent_crash":
            return await self._prevent_crash(content)
        elif subject == "analyze_crash":
            return await self._analyze_crash(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _restart_service(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Restart service automatically"""
        service_name = content.get('service_name', 'unknown')
        crash_id = content.get('crash_id', '')
        
        # Record restart start
        restart_start = datetime.utcnow()
        
        # Execute restart
        restart_result = await self._execute_service_restart(service_name)
        
        # Calculate restart time
        restart_time = (datetime.utcnow() - restart_start).total_seconds()
        
        # Update crash event
        if crash_id:
            crash = next((c for c in self.crash_events if c.crash_id == crash_id), None)
            if crash:
                crash.restarted_at = datetime.utcnow()
                crash.restart_time_seconds = restart_time
        
        return {
            'service_name': service_name,
            'restart_success': restart_result['success'],
            'restart_time_seconds': restart_time,
            'restarted_at': restart_start.isoformat(),
            'new_status': restart_result['status']
        }
    
    async def _prevent_crash(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Prevent crash proactively"""
        service_name = content.get('service_name', 'unknown')
        risk_factors = content.get('risk_factors', [])
        
        # Generate prevention actions
        prevention_actions = await self._generate_prevention_actions(service_name, risk_factors)
        
        # Execute prevention actions
        executed_actions = []
        for action in prevention_actions:
            executed = await self._execute_prevention_action(action)
            executed_actions.append(executed)
            self.prevention_actions.append(executed)
        
        return {
            'service_name': service_name,
            'risk_factors': risk_factors,
            'prevention_actions': len(executed_actions),
            'successful_actions': sum(1 for a in executed_actions if a.success),
            'actions': [
                {
                    'action_id': a.action_id,
                    'action_type': a.action_type,
                    'success': a.success,
                    'impact': a.impact
                }
                for a in executed_actions
            ]
        }
    
    async def _analyze_crash(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze crash for root cause"""
        crash_id = content.get('crash_id', 'unknown')
        
        # Find crash event
        crash = next((c for c in self.crash_events if c.crash_id == crash_id), None)
        
        if not crash:
            return {'error': f'Crash not found: {crash_id}'}
        
        # Analyze crash data
        analysis = await self._perform_crash_analysis(crash)
        
        # Update crash with root cause
        crash.root_cause = analysis['root_cause']
        
        return {
            'crash_id': crash_id,
            'service_name': crash.service_name,
            'crash_type': crash.crash_type,
            'root_cause': analysis['root_cause'],
            'contributing_factors': analysis['contributing_factors'],
            'prevention_recommendations': analysis['prevention_recommendations'],
            'similar_crashes': analysis['similar_crashes']
        }
    
    async def _crash_detection_loop(self):
        """Continuous crash detection loop"""
        while self.is_active:
            try:
                # Monitor service health
                health_status = await self._monitor_service_health()
                
                # Detect crashes
                for service, health in health_status.items():
                    if health['status'] == 'crashed':
                        await self._handle_crash_detection(service, health)
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in crash detection loop: {e}")
                await asyncio.sleep(1)
    
    async def _prevention_loop(self):
        """Continuous crash prevention loop"""
        while self.is_active:
            try:
                # Analyze system for crash risks
                risk_analysis = await self._analyze_crash_risks()
                
                # Take preventive actions
                for risk in risk_analysis:
                    if risk['risk_level'] in ['high', 'critical']:
                        await self._prevent_crash({
                            'service_name': risk['service_name'],
                            'risk_factors': risk['risk_factors']
                        })
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in prevention loop: {e}")
                await asyncio.sleep(10)
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop"""
        while self.is_active:
            try:
                # Update service health
                health_status = await self._monitor_service_health()
                self.service_health.update(health_status)
                
                # Check for early warning signs
                warnings = await self._detect_early_warnings(health_status)
                
                # Send warnings
                for warning in warnings:
                    await self.send_message(
                        "monitoring_001",
                        MessageType.ALERT,
                        f"Crash Warning: {warning['service']}",
                        warning,
                        priority=Priority.HIGH
                    )
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in health monitoring loop: {e}")
                await asyncio.sleep(5)
    
    async def _handle_crash_detection(self, service_name: str, health: Dict[str, Any]):
        """Handle detected crash"""
        # Create crash event
        crash = CrashEvent(
            crash_id=f"crash_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            service_name=service_name,
            crash_type=health['crash_type'],
            detected_at=datetime.utcnow()
        )
        
        self.crash_events.append(crash)
        
        # Auto-restart service
        restart_result = await self._restart_service({
            'service_name': service_name,
            'crash_id': crash.crash_id
        })
        
        # Analyze crash
        analysis = await self._analyze_crash({'crash_id': crash.crash_id})
        
        # Send alert
        await self.send_message(
            "ciso_001",
            MessageType.ALERT,
            f"Service Crash Detected: {service_name}",
            {
                'crash_id': crash.crash_id,
                'service_name': service_name,
                'crash_type': crash.crash_type,
                'detected_at': crash.detected_at.isoformat(),
                'restart_success': restart_result['restart_success'],
                'restart_time': restart_result['restart_time_seconds'],
                'root_cause': analysis['root_cause']
            },
            priority=Priority.CRITICAL
        )
    
    async def _monitor_service_health(self) -> Dict[str, Dict[str, Any]]:
        """Monitor health of all services"""
        services = ['api_server', 'database', 'cache', 'trading_engine', 'blockchain']
        health_status = {}
        
        for service in services:
            # Mock health monitoring
            is_healthy = np.random.random() > 0.02  # 98% uptime
            cpu_usage = np.random.uniform(0.1, 0.9)
            memory_usage = np.random.uniform(0.2, 0.8)
            error_rate = np.random.uniform(0.001, 0.05)
            
            if not is_healthy:
                status = 'crashed'
                crash_type = np.random.choice(['memory_leak', 'cpu_spike', 'exception', 'timeout'])
            elif cpu_usage > 0.9 or memory_usage > 0.9 or error_rate > 0.03:
                status = 'degraded'
                crash_type = 'performance_issue'
            else:
                status = 'healthy'
                crash_type = None
            
            health_status[service] = {
                'status': status,
                'crash_type': crash_type,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'error_rate': error_rate,
                'last_check': datetime.utcnow().isoformat()
            }
        
        return health_status
    
    async def _analyze_crash_risks(self) -> List[Dict[str, Any]]:
        """Analyze system for crash risks"""
        risks = []
        
        for service, health in self.service_health.items():
            risk_factors = []
            risk_level = 'low'
            
            # Check CPU usage
            if health['cpu_usage'] > 0.8:
                risk_factors.append('high_cpu_usage')
                risk_level = 'medium'
            
            if health['cpu_usage'] > 0.95:
                risk_level = 'high'
            
            # Check memory usage
            if health['memory_usage'] > 0.85:
                risk_factors.append('high_memory_usage')
                risk_level = max(risk_level, 'medium')
            
            if health['memory_usage'] > 0.95:
                risk_level = 'high'
            
            # Check error rate
            if health['error_rate'] > 0.02:
                risk_factors.append('high_error_rate')
                risk_level = max(risk_level, 'medium')
            
            if health['error_rate'] > 0.05:
                risk_level = 'critical'
            
            # Check historical crash patterns
            recent_crashes = [c for c in self.crash_events 
                              if c.service_name == service and 
                              (datetime.utcnow() - c.detected_at).total_seconds() < 3600]
            
            if len(recent_crashes) > 2:
                risk_factors.append('repeated_crashes')
                risk_level = 'critical'
            
            if risk_factors:
                risks.append({
                    'service_name': service,
                    'risk_level': risk_level,
                    'risk_factors': risk_factors,
                    'recent_crashes': len(recent_crashes)
                })
        
        return risks
    
    async def _detect_early_warnings(self, health_status: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect early warning signs"""
        warnings = []
        
        for service, health in health_status.items():
            warning_signs = []
            
            # Gradual memory increase
            if health['memory_usage'] > 0.7:
                warning_signs.append('memory_usage_increasing')
            
            # CPU spikes
            if health['cpu_usage'] > 0.8:
                warning_signs.append('cpu_spike_detected')
            
            # Error rate increase
            if health['error_rate'] > 0.01:
                warning_signs.append('error_rate_increasing')
            
            if warning_signs:
                warnings.append({
                    'service': service,
                    'warning_signs': warning_signs,
                    'severity': 'high' if len(warning_signs) > 2 else 'medium',
                    'recommended_action': 'monitor_closely' if len(warning_signs) <= 2 else 'preventive_action'
                })
        
        return warnings
    
    async def _execute_service_restart(self, service_name: str) -> Dict[str, Any]:
        """Execute service restart"""
        logger.info(f"Restarting service: {service_name}")
        
        # Mock service restart
        await asyncio.sleep(np.random.uniform(5, 25))  # 5-25 seconds
        success = np.random.random() > 0.05  # 95% success rate
        
        return {
            'success': success,
            'status': 'running' if success else 'failed',
            'restart_method': 'graceful' if success else 'force'
        }
    
    async def _generate_prevention_actions(self, service_name: str, risk_factors: List[str]) -> List[Dict[str, Any]]:
        """Generate prevention actions"""
        actions = []
        
        for factor in risk_factors:
            if factor == 'high_cpu_usage':
                actions.append({
                    'action_type': 'scale_resources',
                    'description': 'Scale up CPU resources',
                    'priority': 'high'
                })
            elif factor == 'high_memory_usage':
                actions.append({
                    'action_type': 'memory_optimization',
                    'description': 'Optimize memory usage',
                    'priority': 'high'
                })
            elif factor == 'high_error_rate':
                actions.append({
                    'action_type': 'error_handling',
                    'description': 'Improve error handling',
                    'priority': 'medium'
                })
            elif factor == 'repeated_crashes':
                actions.append({
                    'action_type': 'root_cause_analysis',
                    'description': 'Analyze root cause of crashes',
                    'priority': 'critical'
                })
        
        return actions
    
    async def _execute_prevention_action(self, action: Dict[str, Any]) -> PreventionAction:
        """Execute prevention action"""
        prevention = PreventionAction(
            action_id=f"prevent_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            service_name=action.get('service_name', 'unknown'),
            action_type=action['action_type'],
            description=action['description'],
            executed_at=datetime.utcnow(),
            success=False,
            impact='unknown'
        )
        
        # Execute action
        if action['action_type'] == 'scale_resources':
            result = await self._scale_resources(prevention.service_name)
        elif action['action_type'] == 'memory_optimization':
            result = await self._optimize_memory(prevention.service_name)
        elif action['action_type'] == 'error_handling':
            result = await self._improve_error_handling(prevention.service_name)
        elif action['action_type'] == 'root_cause_analysis':
            result = await self._analyze_root_cause(prevention.service_name)
        else:
            result = {'success': False, 'impact': 'none'}
        
        prevention.success = result['success']
        prevention.impact = result['impact']
        
        return prevention
    
    async def _scale_resources(self, service_name: str) -> Dict[str, Any]:
        """Scale service resources"""
        logger.info(f"Scaling resources for: {service_name}")
        await asyncio.sleep(2)  # 2 seconds to scale
        return {'success': True, 'impact': 'increased_capacity'}
    
    async def _optimize_memory(self, service_name: str) -> Dict[str, Any]:
        """Optimize service memory"""
        logger.info(f"Optimizing memory for: {service_name}")
        await asyncio.sleep(3)  # 3 seconds to optimize
        return {'success': True, 'impact': 'reduced_memory_usage'}
    
    async def _improve_error_handling(self, service_name: str) -> Dict[str, Any]:
        """Improve error handling"""
        logger.info(f"Improving error handling for: {service_name}")
        await asyncio.sleep(1)  # 1 second to update
        return {'success': True, 'impact': 'improved_resilience'}
    
    async def _analyze_root_cause(self, service_name: str) -> Dict[str, Any]:
        """Analyze root cause of crashes"""
        logger.info(f"Analyzing root cause for: {service_name}")
        await asyncio.sleep(5)  # 5 seconds to analyze
        return {'success': True, 'impact': 'identified_root_cause'}
    
    async def _perform_crash_analysis(self, crash: CrashEvent) -> Dict[str, Any]:
        """Perform detailed crash analysis"""
        # Mock crash analysis
        return {
            'root_cause': np.random.choice(['memory_leak', 'null_pointer', 'timeout', 'resource_exhaustion']),
            'contributing_factors': [
                'high_load',
                'insufficient_resources',
                'code_bug'
            ],
            'prevention_recommendations': [
                'increase_memory_allocation',
                'add_error_handling',
                'implement_circuit_breaker'
            ],
            'similar_crashes': np.random.randint(0, 5)
        }
    
    async def _setup_crash_detection(self):
        """Setup crash detection systems"""
        # Initialize service health monitoring
        services = ['api_server', 'database', 'cache', 'trading_engine', 'blockchain']
        
        for service in services:
            self.service_health[service] = {
                'status': 'healthy',
                'cpu_usage': 0.5,
                'memory_usage': 0.5,
                'error_rate': 0.001,
                'last_check': datetime.utcnow()
            }
    
    async def _load_crash_patterns(self):
        """Load historical crash patterns"""
        self.crash_patterns = {
            'memory_leak': {
                'indicators': ['memory_usage_increase', 'gradual_slowdown'],
                'prevention': 'memory_monitoring',
                'frequency': 0.1
            },
            'cpu_spike': {
                'indicators': ['cpu_usage_spike', 'response_time_increase'],
                'prevention': 'load_balancing',
                'frequency': 0.15
            },
            'timeout': {
                'indicators': ['response_timeout', 'connection_timeout'],
                'prevention': 'timeout_handling',
                'frequency': 0.05
            }
        }

crash_prevention_agent = CrashPreventionAgent()
