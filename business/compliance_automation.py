"""
Business Compliance Automation for DEDAN 2.0
Complete regulatory compliance with automated reporting
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import hashlib
import pandas as pd
import numpy as np
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiohttp
import asyncpg

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComplianceFramework(Enum):
    """Compliance frameworks"""
    GDPR = "gdpr"
    SOX = "sox"
    PCI_DSS = "pci_dss"
    KYC_AML = "kyc_aml"
    ISO_27001 = "iso_27001"
    HIPAA = "hipaa"
    FINRA = "finra"
    SEC = "sec"

class ComplianceStatus(Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPT = "exempt"

class RiskLevel(Enum):
    """Risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ComplianceRequirement:
    """Compliance requirement definition"""
    id: str
    framework: ComplianceFramework
    category: str
    description: str
    mandatory: bool
    controls: List[str]
    testing_procedures: List[str]
    evidence_requirements: List[str]
    review_frequency: str
    risk_level: RiskLevel
    automated_checks: List[str]

@dataclass
class ComplianceReport:
    """Compliance report data"""
    report_id: str
    framework: ComplianceFramework
    period_start: datetime
    period_end: datetime
    overall_status: ComplianceStatus
    risk_score: float
    requirements_assessed: int
    requirements_compliant: int
    requirements_non_compliant: int
    requirements_partial: int
    findings: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    next_review_date: datetime
    evidence_files: List[str]

@dataclass
class ComplianceAlert:
    """Compliance alert data"""
    alert_id: str
    requirement_id: str
    severity: RiskLevel
    description: str
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    assignee: Optional[str] = None
    status: str = "open"
    remediation_actions: List[str] = field(default_factory=list)

class ComplianceAutomationEngine:
    """Advanced compliance automation engine"""
    
    def __init__(self, db_connection: str, config_path: str):
        self.db_connection = db_connection
        self.config_path = config_path
        self.db = None
        self.compliance_requirements = {}
        self.compliance_reports = {}
        self.compliance_alerts = {}
        self.automated_checks = {}
        self.evidence_repository = Path("/home/kali/mini_business/compliance/evidence")
        self.report_templates = {}
        self.notification_settings = {}
        
        # Initialize
        self.evidence_repository.mkdir(exist_ok=True)
    
    async def initialize(self):
        """Initialize compliance automation engine"""
        self.db = await asyncpg.connect(self.db_connection)
        
        # Load compliance requirements
        await self._load_compliance_requirements()
        
        # Load configuration
        await self._load_configuration()
        
        # Initialize automated checks
        await self._initialize_automated_checks()
        
        logger.info("Compliance automation engine initialized")
    
    async def run_compliance_assessment(self, framework: ComplianceFramework, period_days: int = 30) -> ComplianceReport:
        """Run comprehensive compliance assessment"""
        logger.info(f"Starting compliance assessment for {framework.value}")
        
        period_start = datetime.utcnow() - timedelta(days=period_days)
        period_end = datetime.utcnow()
        
        # Get framework requirements
        requirements = await self._get_framework_requirements(framework)
        
        # Assess each requirement
        assessment_results = []
        total_risk_score = 0.0
        
        for requirement in requirements:
            result = await self._assess_requirement(requirement, period_start, period_end)
            assessment_results.append(result)
            total_risk_score += result.risk_score
        
        # Calculate overall status
        compliant_count = len([r for r in assessment_results if r.status == ComplianceStatus.COMPLIANT])
        non_compliant_count = len([r for r in assessment_results if r.status == ComplianceStatus.NON_COMPLIANT])
        partial_count = len([r for r in assessment_results if r.status == ComplianceStatus.PARTIALLY_COMPLIANT])
        
        # Determine overall status
        if non_compliant_count > 0:
            overall_status = ComplianceStatus.NON_COMPLIANT
        elif partial_count > 0:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            overall_status = ComplianceStatus.COMPLIANT
        
        # Calculate average risk score
        avg_risk_score = total_risk_score / len(requirements) if requirements else 0.0
        
        # Generate findings and recommendations
        findings = []
        recommendations = []
        
        for result in assessment_results:
            if result.status != ComplianceStatus.COMPLIANT:
                findings.append({
                    'requirement_id': requirement.id,
                    'status': result.status.value,
                    'risk_score': result.risk_score,
                    'details': result.details,
                    'evidence': result.evidence
                })
                
                recommendations.extend(result.recommendations)
        
        # Generate report
        report = ComplianceReport(
            report_id=f"comp_{framework.value}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            framework=framework,
            period_start=period_start,
            period_end=period_end,
            overall_status=overall_status,
            risk_score=avg_risk_score,
            requirements_assessed=len(requirements),
            requirements_compliant=compliant_count,
            requirements_non_compliant=non_compliant_count,
            requirements_partial=partial_count,
            findings=findings,
            recommendations=list(set(recommendations)),
            generated_at=datetime.utcnow(),
            next_review_date=datetime.utcnow() + timedelta(days=30),
            evidence_files=await self._collect_evidence(assessment_results)
        )
        
        # Store report
        await self._store_compliance_report(report)
        
        # Generate alerts for high-risk findings
        await self._generate_compliance_alerts(findings)
        
        # Send notifications
        await self._send_compliance_notifications(report)
        
        logger.info(f"Compliance assessment completed for {framework.value}: {overall_status.value}")
        
        return report
    
    async def _assess_requirement(self, requirement: ComplianceRequirement, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Assess individual compliance requirement"""
        assessment_result = {
            'requirement_id': requirement.id,
            'status': ComplianceStatus.COMPLIANT,
            'risk_score': 0.0,
            'details': {},
            'evidence': [],
            'recommendations': []
        }
        
        # Run automated checks
        for check_name in requirement.automated_checks:
            if check_name in self.automated_checks:
                check_result = await self.automated_checks[check_name](period_start, period_end)
                assessment_result['details'][check_name] = check_result
                
                # Update status based on check results
                if not check_result['compliant']:
                    assessment_result['status'] = ComplianceStatus.NON_COMPLIANT
                    assessment_result['risk_score'] += check_result['risk_score']
                    assessment_result['evidence'].extend(check_result['evidence'])
                    assessment_result['recommendations'].extend(check_result['recommendations'])
        
        # Determine final status and risk score
        if assessment_result['risk_score'] > 7.0:
            assessment_result['status'] = ComplianceStatus.NON_COMPLIANT
        elif assessment_result['risk_score'] > 3.0:
            assessment_result['status'] = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            assessment_result['status'] = ComplianceStatus.COMPLIANT
        
        return assessment_result
    
    async def _load_compliance_requirements(self):
        """Load compliance requirements from configuration"""
        requirements_config = {
            ComplianceFramework.GDPR: [
                ComplianceRequirement(
                    id="gdpr_001",
                    framework=ComplianceFramework.GDPR,
                    category="data_protection",
                    description="Lawful basis for processing",
                    mandatory=True,
                    controls=["consent_management", "data_minimization", "purpose_limitation"],
                    testing_procedures=["consent_review", "data_flow_analysis"],
                    evidence_requirements=["consent_records", "data_processing_register"],
                    review_frequency="quarterly",
                    risk_level=RiskLevel.HIGH,
                    automated_checks=["check_consent_records", "verify_data_minimization"]
                ),
                ComplianceRequirement(
                    id="gdpr_002",
                    framework=ComplianceFramework.GDPR,
                    category="data_subject_rights",
                    description="Right to access and rectification",
                    mandatory=True,
                    controls=["access_request_process", "rectification_procedure", "response_timeframe"],
                    testing_procedures=["access_request_test", "rectification_workflow_test"],
                    evidence_requirements=["access_request_logs", "rectification_records"],
                    review_frequency="monthly",
                    risk_level=RiskLevel.MEDIUM,
                    automated_checks=["check_access_response_times", "verify_rectification_procedures"]
                ),
                ComplianceRequirement(
                    id="gdpr_003",
                    framework=ComplianceFramework.GDPR,
                    category="data_breach_notification",
                    description="Breach notification within 72 hours",
                    mandatory=True,
                    controls=["breach_detection", "notification_procedure", "timeline_tracking"],
                    testing_procedures=["breach_simulation", "notification_workflow_test"],
                    evidence_requirements=["incident_logs", "notification_records"],
                    review_frequency="quarterly",
                    risk_level=RiskLevel.CRITICAL,
                    automated_checks=["check_breach_detection_system", "verify_notification_procedures"]
                )
            ],
            ComplianceFramework.PCI_DSS: [
                ComplianceRequirement(
                    id="pci_001",
                    framework=ComplianceFramework.PCI_DSS,
                    category="data_security",
                    description="Encryption of cardholder data",
                    mandatory=True,
                    controls=["encryption_at_rest", "encryption_in_transit", "key_management"],
                    testing_procedures=["encryption_audit", "key_rotation_test"],
                    evidence_requirements=["encryption_certificates", "key_management_logs"],
                    review_frequency="quarterly",
                    risk_level=RiskLevel.CRITICAL,
                    automated_checks=["check_encryption_status", "verify_key_rotation"]
                ),
                ComplianceRequirement(
                    id="pci_002",
                    framework=ComplianceFramework.PCI_DSS,
                    category="access_control",
                    description="Strong access control measures",
                    mandatory=True,
                    controls=["authentication", "authorization", "access_logging"],
                    testing_procedures=["access_control_test", "authentication_audit"],
                    evidence_requirements=["access_logs", "auth_policies"],
                    review_frequency="monthly",
                    risk_level=RiskLevel.HIGH,
                    automated_checks=["check_access_controls", "verify_authentication_systems"]
                )
            ],
            ComplianceFramework.KYC_AML: [
                ComplianceRequirement(
                    id="kyc_001",
                    framework=ComplianceFramework.KYC_AML,
                    category="customer_due_diligence",
                    description="Customer identification and verification",
                    mandatory=True,
                    controls=["identity_verification", "document_collection", "risk_assessment"],
                    testing_procedures=["kyc_process_test", "identity_verification_test"],
                    evidence_requirements=["kyc_records", "verification_documents"],
                    review_frequency="ongoing",
                    risk_level=RiskLevel.HIGH,
                    automated_checks=["check_kyc_completeness", "verify_identity_verification"]
                ),
                ComplianceRequirement(
                    id="aml_001",
                    framework=ComplianceFramework.KYC_AML,
                    category="transaction_monitoring",
                    description="Suspicious activity monitoring and reporting",
                    mandatory=True,
                    controls=["transaction_monitoring", "suspicious_activity_detection", "regulatory_reporting"],
                    testing_procedures=["aml_monitoring_test", "suspicious_activity_test"],
                    evidence_requirements=["transaction_logs", "suspicious_activity_reports"],
                    review_frequency="daily",
                    risk_level=RiskLevel.CRITICAL,
                    automated_checks=["check_transaction_monitoring", "verify_suspicious_activity_detection"]
                )
            ]
        }
        
        self.compliance_requirements = requirements_config
    
    async def _initialize_automated_checks(self):
        """Initialize automated compliance checks"""
        self.automated_checks = {
            # GDPR checks
            "check_consent_records": self._check_consent_records,
            "verify_data_minimization": self._verify_data_minimization,
            "check_access_response_times": self._check_access_response_times,
            "verify_rectification_procedures": self._verify_rectification_procedures,
            "check_breach_detection_system": self._check_breach_detection_system,
            "verify_notification_procedures": self._verify_notification_procedures,
            
            # PCI DSS checks
            "check_encryption_status": self._check_encryption_status,
            "verify_key_rotation": self._verify_key_rotation,
            "check_access_controls": self._check_access_controls,
            "verify_authentication_systems": self._verify_authentication_systems,
            
            # KYC/AML checks
            "check_kyc_completeness": self._check_kyc_completeness,
            "verify_identity_verification": self._verify_identity_verification,
            "check_transaction_monitoring": self._check_transaction_monitoring,
            "verify_suspicious_activity_detection": self._verify_suspicious_activity_detection,
            
            # General checks
            "check_data_retention": self._check_data_retention,
            "verify_backup_procedures": self._verify_backup_procedures,
            "check_incident_response": self._check_incident_response,
            "verify_vendor_management": self._verify_vendor_management
        }
    
    async def _check_consent_records(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Check GDPR consent records"""
        try:
            # Query consent records
            query = """
                SELECT COUNT(*) as total_consent,
                       COUNT(CASE WHEN consent_given = true THEN 1 END) as active_consent,
                       COUNT(CASE WHEN consent_withdrawn = true THEN 1 END) as withdrawn_consent,
                       MAX(consent_date) as latest_consent
                FROM user_consent
                WHERE created_at BETWEEN $1 AND $2
            """
            
            result = await self.db.fetchrow(query, period_start, period_end)
            
            compliant = True
            risk_score = 0.0
            evidence = []
            recommendations = []
            
            # Check if consent records are complete
            if result['total_consent'] == 0:
                compliant = False
                risk_score = 8.0
                evidence.append("No consent records found")
                recommendations.append("Implement consent management system")
            
            # Check withdrawal rate
            if result['total_consent'] > 0:
                withdrawal_rate = result['withdrawn_consent'] / result['total_consent']
                if withdrawal_rate > 0.1:  # 10% withdrawal rate
                    compliant = False
                    risk_score += 3.0
                    evidence.append(f"High withdrawal rate: {withdrawal_rate:.2%}")
                    recommendations.append("Review consent withdrawal process")
            
            return {
                'compliant': compliant,
                'risk_score': risk_score,
                'evidence': evidence,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking consent records: {e}")
            return {
                'compliant': False,
                'risk_score': 5.0,
                'evidence': [f"Error: {str(e)}"],
                'recommendations': ["Fix consent record checking system"]
            }
    
    async def _verify_data_minimization(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Verify data minimization principles"""
        try:
            # Check data collection practices
            query = """
                SELECT table_name, column_name, data_type, retention_period
                FROM data_inventory
                WHERE created_at BETWEEN $1 AND $2
            """
            
            inventory = await self.db.fetch(query, period_start, period_end)
            
            compliant = True
            risk_score = 0.0
            evidence = []
            recommendations = []
            
            for item in inventory:
                # Check if data collection is necessary
                if item['data_type'] == 'personal' and not item['retention_period']:
                    compliant = False
                    risk_score += 2.0
                    evidence.append(f"Unnecessary personal data in {item['table_name']}.{item['column_name']}")
                    recommendations.append("Review and minimize personal data collection")
                
                # Check retention periods
                if item['retention_period'] and item['retention_period'] > '365 days':
                    compliant = False
                    risk_score += 1.5
                    evidence.append(f"Excessive retention period for {item['table_name']}")
                    recommendations.append("Implement appropriate data retention policies")
            
            return {
                'compliant': compliant,
                'risk_score': risk_score,
                'evidence': evidence,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error verifying data minimization: {e}")
            return {
                'compliant': False,
                'risk_score': 4.0,
                'evidence': [f"Error: {str(e)}"],
                'recommendations': ["Fix data minimization verification system"]
            }
    
    async def _check_encryption_status(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Check encryption status for PCI DSS"""
        try:
            # Check encryption of sensitive data
            query = """
                SELECT table_name, encryption_status, key_rotation_date, last_audit_date
                FROM encryption_status
                WHERE created_at BETWEEN $1 AND $2
            """
            
            encryption_status = await self.db.fetch(query, period_start, period_end)
            
            compliant = True
            risk_score = 0.0
            evidence = []
            recommendations = []
            
            for item in encryption_status:
                if item['encryption_status'] != 'encrypted':
                    compliant = False
                    risk_score += 5.0
                    evidence.append(f"Unencrypted data in {item['table_name']}")
                    recommendations.append(f"Encrypt {item['table_name']} table")
                
                # Check key rotation
                if item['key_rotation_date']:
                    days_since_rotation = (datetime.utcnow() - item['key_rotation_date']).days
                    if days_since_rotation > 365:  # 1 year
                        compliant = False
                        risk_score += 2.0
                        evidence.append(f"Key rotation overdue for {item['table_name']}")
                        recommendations.append(f"Rotate encryption keys for {item['table_name']}")
                
                # Check audit frequency
                if item['last_audit_date']:
                    days_since_audit = (datetime.utcnow() - item['last_audit_date']).days
                    if days_since_audit > 90:  # 3 months
                        risk_score += 1.0
                        evidence.append(f"Encryption audit overdue for {item['table_name']}")
                        recommendations.append(f"Conduct encryption audit for {item['table_name']}")
            
            return {
                'compliant': compliant,
                'risk_score': risk_score,
                'evidence': evidence,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking encryption status: {e}")
            return {
                'compliant': False,
                'risk_score': 6.0,
                'evidence': [f"Error: {str(e)}"],
                'recommendations': ["Fix encryption status checking system"]
            }
    
    async def _check_kyc_completeness(self, period_start: datetime, period_end: datetime) -> Dict[str, Any]:
        """Check KYC completeness"""
        try:
            # Check KYC records
            query = """
                SELECT user_id, kyc_status, verification_level, documents_uploaded,
                       last_updated, risk_score
                FROM kyc_records
                WHERE created_at BETWEEN $1 AND $2
            """
            
            kyc_records = await self.db.fetch(query, period_start, period_end)
            
            compliant = True
            risk_score = 0.0
            evidence = []
            recommendations = []
            
            for record in kyc_records:
                # Check KYC completion
                if record['kyc_status'] != 'completed':
                    compliant = False
                    risk_score += 3.0
                    evidence.append(f"Incomplete KYC for user {record['user_id']}")
                    recommendations.append("Complete KYC process for all users")
                
                # Check verification level
                if record['verification_level'] < 2:  # Assuming 2 is minimum acceptable
                    compliant = False
                    risk_score += 2.0
                    evidence.append(f"Low verification level for user {record['user_id']}")
                    recommendations.append("Enhance verification procedures")
                
                # Check document completeness
                if record['documents_uploaded'] < 3:  # Assuming 3 documents minimum
                    compliant = False
                    risk_score += 2.0
                    evidence.append(f"Insufficient documents for user {record['user_id']}")
                    recommendations.append("Collect required KYC documents")
            
            return {
                'compliant': compliant,
                'risk_score': risk_score,
                'evidence': evidence,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Error checking KYC completeness: {e}")
            return {
                'compliant': False,
                'risk_score': 5.0,
                'evidence': [f"Error: {str(e)}"],
                'recommendations': ["Fix KYC completeness checking system"]
            }
    
    async def _get_framework_requirements(self, framework: ComplianceFramework) -> List[ComplianceRequirement]:
        """Get requirements for specific framework"""
        return self.compliance_requirements.get(framework, [])
    
    async def _store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in database"""
        try:
            query = """
                INSERT INTO compliance_reports (
                    id, framework, period_start, period_end, overall_status,
                    risk_score, requirements_assessed, requirements_compliant,
                    requirements_non_compliant, requirements_partial,
                    findings, recommendations, generated_at, next_review_date
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """
            
            await self.db.execute(
                query,
                report.report_id,
                report.framework.value,
                report.period_start,
                report.period_end,
                report.overall_status.value,
                report.risk_score,
                report.requirements_assessed,
                report.requirements_compliant,
                report.requirements_non_compliant,
                report.requirements_partial,
                json.dumps(report.findings),
                json.dumps(report.recommendations),
                report.generated_at,
                report.next_review_date
            )
            
            # Store evidence file references
            for evidence_file in report.evidence_files:
                await self.db.execute(
                    "INSERT INTO compliance_evidence (report_id, file_path, file_type) VALUES ($1, $2, $3)",
                    report.report_id,
                    evidence_file,
                    "supporting_document"
                )
            
            logger.info(f"Stored compliance report: {report.report_id}")
            
        except Exception as e:
            logger.error(f"Error storing compliance report: {e}")
    
    async def _generate_compliance_alerts(self, findings: List[Dict[str, Any]]):
        """Generate compliance alerts for high-risk findings"""
        for finding in findings:
            if finding['risk_score'] > 5.0:  # High risk threshold
                alert = ComplianceAlert(
                    alert_id=f"alert_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{finding['requirement_id']}",
                    requirement_id=finding['requirement_id'],
                    severity=RiskLevel.HIGH if finding['risk_score'] > 7.0 else RiskLevel.MEDIUM,
                    description=finding['details'],
                    detected_at=datetime.utcnow(),
                    status="open"
                )
                
                # Store alert
                await self._store_compliance_alert(alert)
                
                # Send notification
                await self._send_alert_notification(alert)
    
    async def _store_compliance_alert(self, alert: ComplianceAlert):
        """Store compliance alert"""
        try:
            query = """
                INSERT INTO compliance_alerts (
                    id, requirement_id, severity, description, detected_at, status
                ) VALUES ($1, $2, $3, $4, $5, $6)
            """
            
            await self.db.execute(
                query,
                alert.alert_id,
                alert.requirement_id,
                alert.severity.value,
                alert.description,
                alert.detected_at,
                alert.status
            )
            
            logger.info(f"Stored compliance alert: {alert.alert_id}")
            
        except Exception as e:
            logger.error(f"Error storing compliance alert: {e}")
    
    async def _send_alert_notification(self, alert: ComplianceAlert):
        """Send notification for compliance alert"""
        try:
            # Get notification settings
            settings = self.notification_settings.get('alerts', {})
            
            if not settings.get('enabled', True):
                return
            
            # Prepare email content
            subject = f"Compliance Alert: {alert.severity.value.upper()} - {alert.requirement_id}"
            body = f"""
            Compliance Alert Details:
            
            Alert ID: {alert.alert_id}
            Requirement: {alert.requirement_id}
            Severity: {alert.severity.value}
            Description: {alert.description}
            Detected At: {alert.detected_at.isoformat()}
            
            Please review and take appropriate action.
            """
            
            # Send email
            await self._send_email(
                to=settings.get('recipients', []),
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Error sending alert notification: {e}")
    
    async def _collect_evidence(self, assessment_results: List[Dict[str, Any]]) -> List[str]:
        """Collect evidence for compliance assessment"""
        evidence_files = []
        
        for i, result in enumerate(assessment_results):
            if result.get('evidence'):
                evidence_data = {
                    'requirement_id': result.get('requirement_id'),
                    'assessment_date': datetime.utcnow().isoformat(),
                    'evidence': result.get('evidence'),
                    'risk_score': result.get('risk_score'),
                    'status': result.get('status')
                }
                
                # Save evidence to file
                filename = f"evidence_{i}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = self.evidence_repository / filename
                
                with open(filepath, 'w') as f:
                    json.dump(evidence_data, f, indent=2)
                
                evidence_files.append(str(filepath))
        
        return evidence_files
    
    async def _send_compliance_notifications(self, report: ComplianceReport):
        """Send compliance notifications"""
        try:
            # Get notification settings
            settings = self.notification_settings.get('reports', {})
            
            if not settings.get('enabled', True):
                return
            
            # Prepare email content
            subject = f"Compliance Report: {report.framework.value.upper()} - {report.overall_status.value.upper()}"
            
            body = f"""
            Compliance Report Summary:
            
            Framework: {report.framework.value}
            Period: {report.period_start.strftime('%Y-%m-%d')} to {report.period_end.strftime('%Y-%m-%d')}
            Overall Status: {report.overall_status.value}
            Risk Score: {report.risk_score:.2f}
            
            Requirements Assessed: {report.requirements_assessed}
            Compliant: {report.requirements_compliant}
            Non-Compliant: {report.requirements_non_compliant}
            Partially Compliant: {report.requirements_partial}
            
            Key Findings: {len(report.findings)}
            Recommendations: {len(report.recommendations)}
            
            Next Review Date: {report.next_review_date.strftime('%Y-%m-%d')}
            
            Please review the full report for detailed findings and recommendations.
            """
            
            # Send email
            await self._send_email(
                to=settings.get('recipients', []),
                subject=subject,
                body=body
            )
            
        except Exception as e:
            logger.error(f"Error sending compliance notifications: {e}")
    
    async def _send_email(self, to: List[str], subject: str, body: str):
        """Send email notification"""
        try:
            # This would integrate with your email service
            # For now, just log the email
            logger.info(f"Email to {to}: {subject}")
            logger.info(f"Body: {body}")
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
    
    async def _load_configuration(self):
        """Load compliance configuration"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                self.notification_settings = config.get('notifications', {})
                self.report_templates = config.get('templates', {})
        else:
            # Default configuration
            self.notification_settings = {
                'alerts': {
                    'enabled': True,
                    'recipients': ['compliance@dedan.ai']
                },
                'reports': {
                    'enabled': True,
                    'recipients': ['compliance@dedan.ai', 'management@dedan.ai']
                }
            }
    
    async def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data"""
        try:
            # Get latest reports for each framework
            dashboard_data = {}
            
            for framework in ComplianceFramework:
                latest_report = await self.db.fetchrow(
                    """
                    SELECT * FROM compliance_reports
                    WHERE framework = $1
                    ORDER BY generated_at DESC
                    LIMIT 1
                    """,
                    framework.value
                )
                
                if latest_report:
                    # Get open alerts
                    open_alerts = await self.db.fetch(
                        """
                        SELECT COUNT(*) as count
                        FROM compliance_alerts
                        WHERE status = 'open'
                        AND detected_at >= $1
                        """,
                        datetime.utcnow() - timedelta(days=30)
                    )
                    
                    alert_count = open_alerts[0]['count'] if open_alerts else 0
                    
                    dashboard_data[framework.value] = {
                        'latest_report': {
                            'id': latest_report['id'],
                            'status': latest_report['overall_status'],
                            'risk_score': latest_report['risk_score'],
                            'generated_at': latest_report['generated_at']
                        },
                        'open_alerts': alert_count,
                        'trend': await self._get_compliance_trend(framework)
                    }
                else:
                    dashboard_data[framework.value] = {
                        'latest_report': None,
                        'open_alerts': 0,
                        'trend': 'no_data'
                    }
            
            # Overall compliance score
            overall_score = await self._calculate_overall_compliance_score()
            
            return {
                'frameworks': dashboard_data,
                'overall_score': overall_score,
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting compliance dashboard: {e}")
            return {'error': str(e)}
    
    async def _get_compliance_trend(self, framework: ComplianceFramework) -> str:
        """Get compliance trend for framework"""
        try:
            # Get last 6 months of reports
            reports = await self.db.fetch(
                """
                    SELECT overall_status, generated_at
                    FROM compliance_reports
                    WHERE framework = $1
                    ORDER BY generated_at DESC
                    LIMIT 6
                    """,
                framework.value
            )
            
            if len(reports) < 2:
                return 'insufficient_data'
            
            # Calculate trend
            recent_compliant = sum(1 for r in reports if r['overall_status'] == 'compliant')
            trend_score = recent_compliant / len(reports)
            
            if trend_score >= 0.8:
                return 'improving'
            elif trend_score >= 0.6:
                return 'stable'
            elif trend_score >= 0.4:
                return 'declining'
            else:
                return 'critical'
                
        except Exception as e:
            logger.error(f"Error getting compliance trend: {e}")
            return 'error'
    
    async def _calculate_overall_compliance_score(self) -> float:
        """Calculate overall compliance score"""
        try:
            # Get latest reports for all frameworks
            reports = await self.db.fetch(
                """
                    SELECT framework, risk_score, requirements_assessed, requirements_compliant
                    FROM compliance_reports
                    WHERE generated_at >= NOW() - INTERVAL '30 days'
                    ORDER BY generated_at DESC
                """
            )
            
            if not reports:
                return 0.0
            
            # Calculate weighted score
            total_weight = 0
            weighted_score = 0.0
            
            framework_weights = {
                'gdpr': 0.3,
                'pci_dss': 0.3,
                'kyc_aml': 0.25,
                'sox': 0.15
            }
            
            for report in reports:
                weight = framework_weights.get(report['framework'], 0.1)
                compliance_rate = report['requirements_compliant'] / report['requirements_assessed']
                
                # Convert risk score to compliance score (inverse)
                compliance_score = (10.0 - report['risk_score']) / 10.0
                
                weighted_score += (compliance_rate * compliance_score) * weight
                total_weight += weight
            
            return (weighted_score / total_weight) * 100 if total_weight > 0 else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating overall compliance score: {e}")
            return 0.0

# Main execution
async def main():
    """Main execution function"""
    compliance_engine = ComplianceAutomationEngine(
        db_connection="postgresql://dedan:password@localhost:5432/dedan",
        config_path="/home/kali/mini_business/compliance/config.json"
    )
    
    await compliance_engine.initialize()
    
    # Run compliance assessments
    gdpr_report = await compliance_engine.run_compliance_assessment(ComplianceFramework.GDPR)
    pci_report = await compliance_engine.run_compliance_assessment(ComplianceFramework.PCI_DSS)
    kyc_report = await compliance_engine.run_compliance_assessment(ComplianceFramework.KYC_AML)
    
    print(f"GDPR Report: {gdpr_report.overall_status.value} (Risk Score: {gdpr_report.risk_score:.2f})")
    print(f"PCI DSS Report: {pci_report.overall_status.value} (Risk Score: {pci_report.risk_score:.2f})")
    print(f"KYC/AML Report: {kyc_report.overall_status.value} (Risk Score: {kyc_report.risk_score:.2f})")
    
    # Get dashboard data
    dashboard = await compliance_engine.get_compliance_dashboard()
    print(f"Compliance Dashboard: {json.dumps(dashboard, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(main())
