"""
Legal Agent - Auto-handle legal compliance, auto-draft contracts
Replaces 1 Legal Counsel + 5 legal specialists
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
class LegalCompliance:
    """Legal compliance check"""
    compliance_id: str
    regulation: str
    status: str
    risk_level: str
    last_checked: datetime
    next_review: datetime

@dataclass
class LegalContract:
    """Legal contract"""
    contract_id: str
    contract_type: str
    parties: List[str]
    status: str
    created_at: datetime
    reviewed_at: Optional[datetime] = None
    clauses: List[Dict[str, Any]] = None

class LegalAgent(BaseAIAgent):
    """Legal Agent - Automated legal compliance and contracts"""
    
    def __init__(self):
        super().__init__(
            agent_id="legal_001",
            role=AgentRole.LEGAL,
            name="Legal Counsel",
            description="Auto-handle legal compliance, auto-draft contracts"
        )
        
        self.legal_compliance: List[LegalCompliance] = []
        self.legal_contracts: List[LegalContract] = []
        self.regulations: Dict[str, Any] = {}
        self.contract_templates: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize legal agent"""
        try:
            await self._load_regulations()
            await self._setup_contract_templates()
            asyncio.create_task(self._compliance_monitoring_loop())
            asyncio.create_task(self._contract_management_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Legal Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get legal agent capabilities"""
        return [
            AgentCapability(
                name="compliance_monitoring",
                description="Auto-monitor legal compliance",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.98, "response_time": 3.0},
                dependencies=["regulatory_databases", "compliance_rules"]
            ),
            AgentCapability(
                name="contract_automation",
                description="Auto-draft and review contracts",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 5.0},
                dependencies=["contract_templates", "legal_ai"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process legal tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle legal commands"""
        if subject == "check_compliance":
            return await self._check_compliance(content)
        elif subject == "draft_contract":
            return await self._draft_contract(content)
        elif subject == "review_contract":
            return await self._review_contract(content)
        elif subject == "update_regulations":
            return await self._update_regulations(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _check_compliance(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Check legal compliance"""
        regulation = content.get('regulation', 'GDPR')
        business_area = content.get('business_area', 'data_protection')
        
        # Create compliance check
        compliance = LegalCompliance(
            compliance_id=f"comp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            regulation=regulation,
            status='checking',
            risk_level='unknown',
            last_checked=datetime.utcnow(),
            next_review=datetime.utcnow() + timedelta(days=90)
        )
        
        # Perform compliance check
        check_result = await self._perform_compliance_check(regulation, business_area)
        
        compliance.status = check_result['status']
        compliance.risk_level = check_result['risk_level']
        
        self.legal_compliance.append(compliance)
        
        return {
            'compliance_id': compliance.compliance_id,
            'regulation': regulation,
            'business_area': business_area,
            'status': compliance.status,
            'risk_level': compliance.risk_level,
            'findings': check_result['findings'],
            'recommendations': check_result['recommendations'],
            'last_checked': compliance.last_checked.isoformat()
        }
    
    async def _draft_contract(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Draft legal contract automatically"""
        contract_type = content.get('contract_type', 'partnership')
        parties = content.get('parties', [])
        terms = content.get('terms', {})
        
        # Create contract
        contract = LegalContract(
            contract_id=f"contract_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            contract_type=contract_type,
            parties=parties,
            status='drafting',
            created_at=datetime.utcnow(),
            clauses=[]
        )
        
        # Generate contract clauses
        clauses = await self._generate_contract_clauses(contract_type, terms)
        contract.clauses = clauses
        
        # Validate contract
        validation_result = await self._validate_contract(contract)
        
        if validation_result['valid']:
            contract.status = 'drafted'
        else:
            contract.status = 'needs_revision'
        
        self.legal_contracts.append(contract)
        
        return {
            'contract_id': contract.contract_id,
            'contract_type': contract_type,
            'parties': parties,
            'status': contract.status,
            'clauses_count': len(clauses),
            'validation_result': validation_result,
            'created_at': contract.created_at.isoformat()
        }
    
    async def _review_contract(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Review existing contract"""
        contract_id = content.get('contract_id', 'unknown')
        
        # Find contract
        contract = next((c for c in self.legal_contracts if c.contract_id == contract_id), None)
        
        if not contract:
            return {'error': f'Contract not found: {contract_id}'}
        
        # Perform review
        review_result = await self._perform_contract_review(contract)
        
        contract.reviewed_at = datetime.utcnow()
        contract.status = 'reviewed'
        
        return {
            'contract_id': contract_id,
            'contract_type': contract.contract_type,
            'review_result': review_result,
            'risk_assessment': review_result['risk_assessment'],
            'recommendations': review_result['recommendations'],
            'reviewed_at': contract.reviewed_at.isoformat()
        }
    
    async def _update_regulations(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update regulatory information"""
        regulation_type = content.get('regulation_type', 'all')
        
        # Get latest regulations
        updated_regulations = await self._fetch_latest_regulations(regulation_type)
        
        # Update regulations database
        for reg in updated_regulations:
            self.regulations[reg['id']] = reg
        
        return {
            'regulations_updated': len(updated_regulations),
            'regulation_type': regulation_type,
            'updated_at': datetime.utcnow().isoformat(),
            'regulations': [reg['id'] for reg in updated_regulations]
        }
    
    async def _compliance_monitoring_loop(self):
        """Continuous compliance monitoring loop"""
        while self.is_active:
            try:
                # Check all compliance items
                for compliance in self.legal_compliance:
                    if datetime.utcnow() >= compliance.next_review:
                        await self._recheck_compliance(compliance)
                
                # Monitor regulatory changes
                await self._monitor_regulatory_changes()
                
                # Generate compliance reports
                await self._generate_compliance_reports()
                
                await asyncio.sleep(3600)  # Every hour
            except Exception as e:
                logger.error(f"Error in compliance monitoring loop: {e}")
                await asyncio.sleep(600)
    
    async def _contract_management_loop(self):
        """Continuous contract management loop"""
        while self.is_active:
            try:
                # Review pending contracts
                await self._review_pending_contracts()
                
                # Monitor contract expirations
                await self._monitor_contract_expirations()
                
                # Update contract templates
                await self._update_contract_templates()
                
                await asyncio.sleep(1800)  # Every 30 minutes
            except Exception as e:
                logger.error(f"Error in contract management loop: {e}")
                await asyncio.sleep(300)
    
    async def _perform_compliance_check(self, regulation: str, business_area: str) -> Dict[str, Any]:
        """Perform detailed compliance check"""
        # Mock compliance check
        findings = []
        recommendations = []
        
        if regulation == 'GDPR':
            findings.append("Data processing consent mechanisms verified")
            findings.append("Data retention policies reviewed")
            recommendations.append("Update privacy policy for new GDPR requirements")
            status = 'compliant'
            risk_level = 'low'
        elif regulation == 'KYC':
            findings.append("Customer verification procedures reviewed")
            findings.append("AML monitoring systems checked")
            recommendations.append("Enhance transaction monitoring for high-risk customers")
            status = 'mostly_compliant'
            risk_level = 'medium'
        else:
            findings.append("General compliance review completed")
            recommendations.append("Schedule detailed legal review")
            status = 'needs_review'
            risk_level = 'high'
        
        return {
            'status': status,
            'risk_level': risk_level,
            'findings': findings,
            'recommendations': recommendations
        }
    
    async def _generate_contract_clauses(self, contract_type: str, terms: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate contract clauses"""
        # Mock clause generation
        base_clauses = {
            'partnership': [
                {'type': 'definition', 'title': 'Definitions', 'content': 'This agreement defines the terms of partnership between parties.'},
                {'type': 'obligations', 'title': 'Obligations', 'content': 'Each party shall fulfill their obligations as outlined.'},
                {'type': 'termination', 'title': 'Termination', 'content': 'This agreement may be terminated by either party with 30 days notice.'}
            ],
            'service': [
                {'type': 'scope', 'title': 'Scope of Services', 'content': 'Provider shall deliver services as specified in Schedule A.'},
                {'type': 'payment', 'title': 'Payment Terms', 'content': 'Client shall pay fees as outlined in Schedule B.'},
                {'type': 'liability', 'title': 'Liability', 'content': 'Provider liability limited to fees paid in preceding 12 months.'}
            ],
            'nda': [
                {'type': 'confidentiality', 'title': 'Confidential Information', 'content': 'Both parties shall maintain confidentiality of disclosed information.'},
                {'type': 'duration', 'title': 'Duration', 'content': 'This agreement shall remain in effect for 3 years.'},
                {'type': 'return', 'title': 'Return of Information', 'content': 'All confidential information shall be returned upon termination.'}
            ]
        }
        
        return base_clauses.get(contract_type, base_clauses['partnership'])
    
    async def _validate_contract(self, contract: LegalContract) -> Dict[str, Any]:
        """Validate contract"""
        # Mock validation
        validation_issues = []
        
        if len(contract.parties) < 2:
            validation_issues.append("Contract requires at least 2 parties")
        
        if not contract.clauses:
            validation_issues.append("Contract must contain clauses")
        
        # Check for required clauses
        clause_types = [c['type'] for c in contract.clauses]
        required_types = ['definition', 'obligations', 'termination']
        
        for req_type in required_types:
            if req_type not in clause_types:
                validation_issues.append(f"Missing required clause type: {req_type}")
        
        return {
            'valid': len(validation_issues) == 0,
            'issues': validation_issues,
            'score': max(0, 100 - len(validation_issues) * 10)
        }
    
    async def _perform_contract_review(self, contract: LegalContract) -> Dict[str, Any]:
        """Perform contract review"""
        # Mock review
        risks = []
        recommendations = []
        
        # Analyze clauses
        for clause in contract.clauses:
            if 'liability' in clause['type'].lower():
                risks.append("Liability clause may need limitation")
                recommendations.append("Consider adding liability cap")
            
            if 'termination' in clause['type'].lower():
                if '30 days' in clause['content']:
                    risks.append("Short termination period")
                    recommendations.append("Consider extending to 60 days")
        
        risk_assessment = 'low' if len(risks) <= 1 else 'medium' if len(risks) <= 3 else 'high'
        
        return {
            'risk_assessment': risk_assessment,
            'risks_identified': risks,
            'recommendations': recommendations,
            'review_score': max(0, 100 - len(risks) * 15)
        }
    
    async def _fetch_latest_regulations(self, regulation_type: str) -> List[Dict[str, Any]]:
        """Fetch latest regulations"""
        # Mock regulation updates
        return [
            {
                'id': f"reg_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{i}",
                'type': regulation_type,
                'title': f"Updated Regulation {i}",
                'effective_date': (datetime.utcnow() + timedelta(days=30)).isoformat(),
                'summary': f"Summary of regulation changes {i}"
            }
            for i in range(np.random.randint(1, 5))
        ]
    
    async def _recheck_compliance(self, compliance: LegalCompliance):
        """Recheck existing compliance"""
        check_result = await self._perform_compliance_check(compliance.regulation, 'general')
        
        compliance.status = check_result['status']
        compliance.risk_level = check_result['risk_level']
        compliance.last_checked = datetime.utcnow()
        compliance.next_review = datetime.utcnow() + timedelta(days=90)
        
        # Alert if compliance status changed
        if check_result['status'] != 'compliant':
            await self.send_message(
                "ciso_001",
                MessageType.ALERT,
                f"Compliance Issue: {compliance.regulation}",
                {
                    'compliance_id': compliance.compliance_id,
                    'regulation': compliance.regulation,
                    'status': compliance.status,
                    'risk_level': compliance.risk_level,
                    'findings': check_result['findings']
                },
                priority=Priority.HIGH
            )
    
    async def _monitor_regulatory_changes(self):
        """Monitor for regulatory changes"""
        # Mock monitoring
        logger.info("Monitoring regulatory changes")
    
    async def _generate_compliance_reports(self):
        """Generate compliance reports"""
        # Mock report generation
        logger.info("Generating compliance reports")
    
    async def _review_pending_contracts(self):
        """Review pending contracts"""
        pending_contracts = [c for c in self.legal_contracts if c.status in ['drafting', 'needs_revision']]
        
        for contract in pending_contracts:
            await self._review_contract({'contract_id': contract.contract_id})
    
    async def _monitor_contract_expirations(self):
        """Monitor contract expirations"""
        # Mock expiration monitoring
        logger.info("Monitoring contract expirations")
    
    async def _update_contract_templates(self):
        """Update contract templates"""
        # Mock template updates
        logger.info("Updating contract templates")
    
    async def _load_regulations(self):
        """Load regulatory information"""
        self.regulations = {
            'GDPR': {
                'name': 'General Data Protection Regulation',
                'jurisdiction': 'EU',
                'effective_date': '2018-05-25',
                'requirements': ['data_protection', 'consent', 'breach_notification']
            },
            'KYC': {
                'name': 'Know Your Customer',
                'jurisdiction': 'Global',
                'effective_date': '2020-01-01',
                'requirements': ['customer_verification', 'aml_monitoring', 'record_keeping']
            },
            'AML': {
                'name': 'Anti-Money Laundering',
                'jurisdiction': 'Global',
                'effective_date': '2020-01-01',
                'requirements': ['transaction_monitoring', 'suspicious_activity_reporting', 'risk_assessment']
            }
        }
    
    async def _setup_contract_templates(self):
        """Setup contract templates"""
        self.contract_templates = {
            'partnership': {
                'name': 'Partnership Agreement',
                'required_clauses': ['definition', 'obligations', 'termination', 'liability'],
                'jurisdiction': 'Delaware'
            },
            'service': {
                'name': 'Service Agreement',
                'required_clauses': ['scope', 'payment', 'liability', 'termination'],
                'jurisdiction': 'Delaware'
            },
            'nda': {
                'name': 'Non-Disclosure Agreement',
                'required_clauses': ['confidentiality', 'duration', 'return', 'exceptions'],
                'jurisdiction': 'Delaware'
            }
        }

legal_agent = LegalAgent()
