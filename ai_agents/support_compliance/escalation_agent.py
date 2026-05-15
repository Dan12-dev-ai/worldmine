"""
Escalation Agent - Auto-escalate complex issues to human experts
Replaces 1 Escalation Manager + 5 escalation specialists
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
class Escalation:
    """Escalation case"""
    escalation_id: str
    original_ticket_id: str
    customer_id: str
    issue_type: str
    severity: str
    assigned_to: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_time: float = 0.0

@dataclass
class EscalationRule:
    """Escalation rule"""
    rule_id: str
    condition: str
    threshold: float
    action: str
    created_at: datetime

class EscalationAgent(BaseAIAgent):
    """Escalation Agent - Automated issue escalation"""
    
    def __init__(self):
        super().__init__(
            agent_id="escalation_001",
            role=AgentRole.ESCALATION,
            name="Escalation Manager",
            description="Auto-escalate complex issues to human experts"
        )
        
        self.escalations: List[Escalation] = []
        self.escalation_rules: List[EscalationRule] = []
        self.expert_pool: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize escalation agent"""
        try:
            await self._setup_escalation_rules()
            await self._load_expert_pool()
            asyncio.create_task(self._escalation_monitoring_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Escalation Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get escalation agent capabilities"""
        return [
            AgentCapability(
                name="automatic_escalation",
                description="Auto-escalate complex issues",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.98, "response_time": 2.0},
                dependencies=["ticket_system", "expert_pool", "routing"]
            ),
            AgentCapability(
                name="expert_matching",
                description="Auto-match issues to right experts",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 1.0},
                dependencies=["expert_skills", "availability", "workload"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process escalation tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle escalation commands"""
        if subject == "escalate_issue":
            return await self._escalate_issue(content)
        elif subject == "assign_expert":
            return await self._assign_expert(content)
        elif subject == "update_escalation":
            return await self._update_escalation(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _escalate_issue(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Escalate issue automatically"""
        ticket_id = content.get('ticket_id', 'unknown')
        customer_id = content.get('customer_id', 'unknown')
        issue_type = content.get('issue_type', 'technical')
        severity = content.get('severity', 'medium')
        escalation_reason = content.get('reason', 'complex_issue')
        
        # Check escalation rules
        should_escalate = await self._check_escalation_rules(ticket_id, issue_type, severity)
        
        if should_escalate:
            # Find appropriate expert
            expert = await self._find_best_expert(issue_type, severity)
            
            # Create escalation
            escalation = Escalation(
                escalation_id=f"escal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                original_ticket_id=ticket_id,
                customer_id=customer_id,
                issue_type=issue_type,
                severity=severity,
                assigned_to=expert['id'],
                status='assigned',
                created_at=datetime.utcnow()
            )
            
            self.escalations.append(escalation)
            
            # Notify expert
            await self._notify_expert(expert, escalation)
            
            # Update original ticket status
            await self._update_ticket_status(ticket_id, 'escalated')
            
            return {
                'escalation_id': escalation.escalation_id,
                'ticket_id': ticket_id,
                'expert_assigned': expert['name'],
                'expert_specialization': expert['specialization'],
                'severity': severity,
                'escalated_at': escalation.created_at.isoformat(),
                'estimated_resolution': await self._estimate_resolution_time(issue_type, severity)
            }
        
        return {
            'ticket_id': ticket_id,
            'escalation_required': False,
            'reason': 'Issue does not meet escalation criteria'
        }
    
    async def _assign_expert(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Assign expert to escalation"""
        escalation_id = content.get('escalation_id', 'unknown')
        expert_id = content.get('expert_id', 'unknown')
        
        # Find escalation
        escalation = next((e for e in self.escalations if e.escalation_id == escalation_id), None)
        
        if escalation:
            # Find expert
            expert = self.expert_pool.get(expert_id)
            
            if expert:
                escalation.assigned_to = expert_id
                escalation.status = 'assigned'
                
                # Notify expert
                await self._notify_expert(expert, escalation)
                
                return {
                    'escalation_id': escalation_id,
                    'expert_id': expert_id,
                    'expert_name': expert['name'],
                    'specialization': expert['specialization'],
                    'assigned_at': datetime.utcnow().isoformat()
                }
        
        return {'error': f'Escalation not found: {escalation_id}'}
    
    async def _update_escalation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update escalation status"""
        escalation_id = content.get('escalation_id', 'unknown')
        status = content.get('status', 'in_progress')
        resolution_notes = content.get('resolution_notes', '')
        
        # Find escalation
        escalation = next((e for e in self.escalations if e.escalation_id == escalation_id), None)
        
        if escalation:
            escalation.status = status
            
            if status == 'resolved':
                escalation.resolved_at = datetime.utcnow()
                escalation.resolution_time = (escalation.resolved_at - escalation.created_at).total_seconds()
                
                # Notify customer
                await self._notify_resolution(escalation, resolution_notes)
                
                # Update original ticket
                await self._update_ticket_status(escalation.original_ticket_id, 'resolved')
            
            return {
                'escalation_id': escalation_id,
                'status': escalation.status,
                'resolved_at': escalation.resolved_at.isoformat() if escalation.resolved_at else None,
                'resolution_time': escalation.resolution_time
            }
        
        return {'error': f'Escalation not found: {escalation_id}'}
    
    async def _escalation_monitoring_loop(self):
        """Continuous escalation monitoring loop"""
        while self.is_active:
            try:
                # Monitor for issues needing escalation
                await self._monitor_tickets_for_escalation()
                
                # Monitor escalation progress
                await self._monitor_escalation_progress()
                
                # Follow up on overdue escalations
                await self._follow_up_overdue_escalations()
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in escalation monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _check_escalation_rules(self, ticket_id: str, issue_type: str, severity: str) -> bool:
        """Check if issue meets escalation criteria"""
        # Check severity-based rules
        if severity in ['critical', 'high']:
            return True
        
        # Check issue type rules
        critical_issues = ['security_breach', 'data_loss', 'system_outage', 'legal_issue']
        if issue_type in critical_issues:
            return True
        
        # Check response time rules
        response_time = await self._get_ticket_response_time(ticket_id)
        if response_time > 3600:  # 1 hour
            return True
        
        # Check customer tier rules
        customer_tier = await self._get_customer_tier(ticket_id)
        if customer_tier in ['enterprise', 'premium'] and severity in ['medium', 'high']:
            return True
        
        # Check retry rules
        retry_count = await self._get_ticket_retry_count(ticket_id)
        if retry_count > 3:
            return True
        
        return False
    
    async def _find_best_expert(self, issue_type: str, severity: str) -> Dict[str, Any]:
        """Find best expert for issue"""
        # Filter experts by specialization
        qualified_experts = [
            expert for expert in self.expert_pool.values()
            if issue_type in expert['specializations']
        ]
        
        if not qualified_experts:
            # Fallback to general experts
            qualified_experts = [e for e in self.expert_pool.values() if 'general' in e['specializations']]
        
        if not qualified_experts:
            # Return first available expert
            return list(self.expert_pool.values())[0] if self.expert_pool else {'id': 'unknown', 'name': 'Unknown'}
        
        # Score experts based on availability, workload, and expertise
        best_expert = None
        best_score = -1
        
        for expert in qualified_experts:
            score = 0
            
            # Availability score
            if expert['availability'] == 'available':
                score += 3
            elif expert['availability'] == 'busy':
                score += 1
            
            # Workload score (lower is better)
            score += max(0, 3 - expert['current_workload'])
            
            # Expertise score
            if severity == 'critical' and expert['experience'] > 5:
                score += 2
            elif severity == 'high' and expert['experience'] > 3:
                score += 1
            
            if score > best_score:
                best_score = score
                best_expert = expert
        
        return best_expert or qualified_experts[0]
    
    async def _notify_expert(self, expert: Dict[str, Any], escalation: Escalation):
        """Notify expert of escalation"""
        await self.send_message(
            expert['id'],
            MessageType.ALERT,
            f"New Escalation: {escalation.escalation_id}",
            {
                'escalation_id': escalation.escalation_id,
                'ticket_id': escalation.original_ticket_id,
                'customer_id': escalation.customer_id,
                'issue_type': escalation.issue_type,
                'severity': escalation.severity,
                'assigned_at': escalation.created_at.isoformat()
            },
            priority=Priority.HIGH
        )
    
    async def _update_ticket_status(self, ticket_id: str, status: str):
        """Update original ticket status"""
        # This would integrate with ticket system
        logger.info(f"Updating ticket {ticket_id} status to {status}")
    
    async def _notify_resolution(self, escalation: Escalation, resolution_notes: str):
        """Notify customer of resolution"""
        # This would integrate with notification system
        logger.info(f"Notifying customer {escalation.customer_id} of resolution for escalation {escalation.escalation_id}")
    
    async def _monitor_tickets_for_escalation(self):
        """Monitor tickets for escalation needs"""
        # Get tickets that might need escalation
        tickets_needing_escalation = await self._get_tickets_needing_escalation()
        
        for ticket in tickets_needing_escalation:
            await self._escalate_issue({
                'ticket_id': ticket['id'],
                'customer_id': ticket['customer_id'],
                'issue_type': ticket['issue_type'],
                'severity': ticket['severity'],
                'reason': 'automatic_escalation'
            })
    
    async def _monitor_escalation_progress(self):
        """Monitor escalation progress"""
        # Check for escalations taking too long
        overdue_escalations = [
            e for e in self.escalations
            if e.status in ['assigned', 'in_progress'] and
               (datetime.utcnow() - e.created_at).total_seconds() > 14400  # 4 hours
        ]
        
        for escalation in overdue_escalations:
            await self.send_message(
                escalation.assigned_to,
                MessageType.ALERT,
                f"Escalation Overdue: {escalation.escalation_id}",
                {
                    'escalation_id': escalation.escalation_id,
                    'hours_open': (datetime.utcnow() - escalation.created_at).total_seconds() / 3600
                },
                priority=Priority.CRITICAL
            )
    
    async def _follow_up_overdue_escalations(self):
        """Follow up on overdue escalations"""
        # Get escalations overdue by more than 8 hours
        critical_overdue = [
            e for e in self.escalations
            if e.status in ['assigned', 'in_progress'] and
               (datetime.utcnow() - e.created_at).total_seconds() > 28800  # 8 hours
        ]
        
        for escalation in critical_overdue:
            # Escalate to manager
            await self.send_message(
                "escalation_manager_001",
                MessageType.ALERT,
                f"Critical Escalation Overdue: {escalation.escalation_id}",
                {
                    'escalation_id': escalation.escalation_id,
                    'expert_assigned': escalation.assigned_to,
                    'hours_open': (datetime.utcnow() - escalation.created_at).total_seconds() / 3600,
                    'severity': escalation.severity
                },
                priority=Priority.CRITICAL
            )
    
    async def _get_ticket_response_time(self, ticket_id: str) -> float:
        """Get ticket response time"""
        # Mock response time
        return np.random.uniform(100, 7200)  # 1 minute to 2 hours
    
    async def _get_customer_tier(self, ticket_id: str) -> str:
        """Get customer tier"""
        # Mock customer tier
        return np.random.choice(['basic', 'premium', 'enterprise'], p=[0.7, 0.2, 0.1])
    
    async def _get_ticket_retry_count(self, ticket_id: str) -> int:
        """Get ticket retry count"""
        # Mock retry count
        return np.random.randint(0, 5)
    
    async def _estimate_resolution_time(self, issue_type: str, severity: str) -> str:
        """Estimate resolution time"""
        # Mock estimation
        if severity == 'critical':
            return "1-2 hours"
        elif severity == 'high':
            return "2-4 hours"
        elif severity == 'medium':
            return "4-8 hours"
        else:
            return "8-24 hours"
    
    async def _get_tickets_needing_escalation(self) -> List[Dict[str, Any]]:
        """Get tickets needing escalation"""
        # Mock tickets needing escalation
        return [
            {
                'id': f"ticket_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'customer_id': f"customer_{np.random.randint(1, 10000)}",
                'issue_type': np.random.choice(['technical', 'billing', 'security']),
                'severity': np.random.choice(['high', 'critical']),
                'response_time': np.random.uniform(4000, 7200)
            }
            for _ in range(np.random.randint(1, 5))
        ]
    
    async def _setup_escalation_rules(self):
        """Setup escalation rules"""
        self.escalation_rules = [
            EscalationRule(
                rule_id="severity_critical",
                condition="severity == 'critical'",
                threshold=0.0,
                action="immediate_escalation",
                created_at=datetime.utcnow()
            ),
            EscalationRule(
                rule_id="response_time_1hour",
                condition="response_time > 3600",
                threshold=3600.0,
                action="auto_escalation",
                created_at=datetime.utcnow()
            ),
            EscalationRule(
                rule_id="retry_count_3",
                condition="retry_count > 3",
                threshold=3.0,
                action="auto_escalation",
                created_at=datetime.utcnow()
            )
        ]
    
    async def _load_expert_pool(self):
        """Load expert pool"""
        self.expert_pool = {
            'expert_001': {
                'id': 'expert_001',
                'name': 'John Smith',
                'specializations': ['technical', 'security', 'billing'],
                'availability': 'available',
                'current_workload': 2,
                'experience': 7
            },
            'expert_002': {
                'id': 'expert_002',
                'name': 'Sarah Johnson',
                'specializations': ['trading', 'market', 'compliance'],
                'availability': 'busy',
                'current_workload': 4,
                'experience': 5
            },
            'expert_003': {
                'id': 'expert_003',
                'name': 'Mike Chen',
                'specializations': ['general', 'account', 'payment'],
                'availability': 'available',
                'current_workload': 1,
                'experience': 3
            }
        }

escalation_agent = EscalationAgent()
