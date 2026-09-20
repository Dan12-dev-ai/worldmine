# 🔐 WORLD-MINE AI ORCHESTRATION LAYER
## Agent Intercept Layer - Governance & Fraud Detection Integration

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone
import uuid
import json
import logging

logger = logging.getLogger(__name__)

# =============================================================================
# ENUMERATIONS
# =============================================================================

class AgentType(Enum):
    """Types of AI agents in the system"""
    GOVERNANCE = "governance"
    FRAUD_DETECTION = "fraud_detection"
    MARKET_INTELLIGENCE = "market_intelligence"
    TRADE_RECOMMENDATION = "trade_recommendation"
    LOGISTICS_OPTIMIZATION = "logistics_optimization"
    COMMUNICATION_ASSISTANT = "communication_assistant"

class ComplianceStatus(Enum):
    """Compliance check result"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    NEEDS_REVIEW = "needs_review"
    WARNING = "warning"

class TrustLevel(Enum):
    """Trust level from fraud detection"""
    EXCELLENT = "excellent"
    GOOD = "good"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class AIRecommendation:
    """Standardized AI recommendation format"""
    recommendation_id: str
    agent_type: AgentType
    timestamp: datetime
    content: str
    confidence: float
    metadata: Dict[str, Any]
    source_agent: str

@dataclass
class GovernanceCheck:
    """Result from Governance Agent"""
    check_id: str
    compliance_status: ComplianceStatus
    risk_score: float
    issues_found: List[str]
    recommendations: List[str]
    timestamp: datetime

@dataclass
class FraudCheck:
    """Result from Fraud Detection Agent"""
    check_id: str
    trust_level: TrustLevel
    fraud_score: float
    red_flags: List[str]
    trust_indicators: List[str]
    timestamp: datetime

@dataclass
class InterceptedRecommendation:
    """Final recommendation after intercept layer"""
    original: AIRecommendation
    governance_check: GovernanceCheck
    fraud_check: FraudCheck
    approved: bool
    display_content: str
    warnings: List[str]
    final_timestamp: datetime

# =============================================================================
# GOVERNANCE AGENT
# =============================================================================

class GovernanceAgent:
    """
    Governance Agent - ensures compliance and regulatory adherence
    Cross-references AI recommendations against compliance rules
    """

    def __init__(self):
        self.compliance_rules = self._load_compliance_rules()
        self.check_history: List[GovernanceCheck] = []

    async def check_recommendation(
        self,
        recommendation: AIRecommendation
    ) -> GovernanceCheck:
        """
        Check an AI recommendation for compliance
        """
        check_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        issues_found = []
        recommendations = []
        risk_score = 0.0

        # Check 1: KYC/AML compliance
        if recommendation.metadata.get("requires_kyc", False):
            user_verified = recommendation.metadata.get("user_verified", False)
            if not user_verified:
                issues_found.append("KYC verification required for this transaction")
                risk_score += 0.4
                recommendations.append("Complete KYC verification before proceeding")

        # Check 2: Escrow requirement
        if recommendation.metadata.get("transaction_amount", 0) > 10000:
            escrow_enabled = recommendation.metadata.get("escrow_enabled", False)
            if not escrow_enabled:
                issues_found.append("Escrow required for transactions > $10,000")
                risk_score += 0.3
                recommendations.append("Enable escrow for this high-value transaction")

        # Check 3: Contract terms
        if "contract" in recommendation.content.lower():
            contract_verified = recommendation.metadata.get("contract_verified", False)
            if not contract_verified:
                issues_found.append("Contract terms need legal review")
                risk_score += 0.2
                recommendations.append("Request legal review of contract")

        # Determine compliance status
        if risk_score == 0:
            status = ComplianceStatus.COMPLIANT
        elif risk_score < 0.3:
            status = ComplianceStatus.WARNING
        elif risk_score < 0.6:
            status = ComplianceStatus.NEEDS_REVIEW
        else:
            status = ComplianceStatus.NON_COMPLIANT

        check = GovernanceCheck(
            check_id=check_id,
            compliance_status=status,
            risk_score=min(risk_score, 1.0),
            issues_found=issues_found,
            recommendations=recommendations,
            timestamp=timestamp
        )

        self.check_history.append(check)
        logger.info(f"📋 Governance check complete: {status.value} (risk: {risk_score:.2f})")
        
        return check

    def _load_compliance_rules(self) -> Dict[str, Any]:
        """Load compliance rules from configuration"""
        return {
            "max_transaction_without_escrow": 10000,
            "required_kyc_level": 2,
            "contract_review_threshold": 50000,
            "sanctioned_countries": ["NK", "IR", "SY", "CU"],
            "restricted_commodities": ["uranium", "diamonds_conflict"]
        }

# =============================================================================
# FRAUD DETECTION AGENT
# =============================================================================

class FraudDetectionAgent:
    """
    Fraud Detection Agent - analyzes trustworthiness
    Scores users, listings, and transactions for fraud risk
    """

    def __init__(self):
        self.fraud_rules = self._load_fraud_rules()
        self.check_history: List[FraudCheck] = []

    async def check_recommendation(
        self,
        recommendation: AIRecommendation
    ) -> FraudCheck:
        """
        Check an AI recommendation for fraud risk
        """
        check_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        red_flags = []
        trust_indicators = []
        fraud_score = 0.0

        # Check 1: Seller reputation
        seller_reputation = recommendation.metadata.get("seller_reputation", 5.0)
        if seller_reputation < 3.0:
            red_flags.append(f"Low seller reputation: {seller_reputation}/5.0")
            fraud_score += 0.3
        elif seller_reputation >= 4.5:
            trust_indicators.append(f"Excellent seller reputation: {seller_reputation}/5.0")

        # Check 2: Transaction history
        transaction_count = recommendation.metadata.get("seller_transaction_count", 0)
        if transaction_count < 5:
            red_flags.append(f"New seller: only {transaction_count} transactions")
            fraud_score += 0.2
        elif transaction_count > 100:
            trust_indicators.append(f"Experienced seller: {transaction_count}+ transactions")

        # Check 3: Price anomaly
        market_price = recommendation.metadata.get("market_price", 0)
        listing_price = recommendation.metadata.get("listing_price", 0)
        
        if market_price > 0 and listing_price > 0:
            price_ratio = listing_price / market_price
            if price_ratio < 0.7:
                red_flags.append(f"Price significantly below market: {price_ratio:.0%}")
                fraud_score += 0.25
            elif price_ratio > 1.5:
                red_flags.append(f"Price significantly above market: {price_ratio:.0%}")
                fraud_score += 0.15

        # Check 4: Verification status
        identity_verified = recommendation.metadata.get("identity_verified", False)
        business_verified = recommendation.metadata.get("business_verified", False)
        
        if not identity_verified:
            red_flags.append("Identity not verified")
            fraud_score += 0.2
        else:
            trust_indicators.append("Identity verified")
            
        if business_verified:
            trust_indicators.append("Business verified")

        # Determine trust level
        if fraud_score < 0.1:
            trust_level = TrustLevel.EXCELLENT
        elif fraud_score < 0.25:
            trust_level = TrustLevel.GOOD
        elif fraud_score < 0.5:
            trust_level = TrustLevel.MEDIUM
        elif fraud_score < 0.75:
            trust_level = TrustLevel.LOW
        else:
            trust_level = TrustLevel.CRITICAL

        check = FraudCheck(
            check_id=check_id,
            trust_level=trust_level,
            fraud_score=min(fraud_score, 1.0),
            red_flags=red_flags,
            trust_indicators=trust_indicators,
            timestamp=timestamp
        )

        self.check_history.append(check)
        logger.info(f"🕵️  Fraud check complete: {trust_level.value} (score: {fraud_score:.2f})")
        
        return check

    def _load_fraud_rules(self) -> Dict[str, Any]:
        """Load fraud detection rules"""
        return {
            "min_reputation_threshold": 3.0,
            "min_transaction_count": 5,
            "price_anomaly_low": 0.7,
            "price_anomaly_high": 1.5,
            "suspicious_activity_threshold": 3
        }

# =============================================================================
# AGENT INTERCEPT LAYER
# =============================================================================

class AgentInterceptLayer:
    """
    Agent Intercept Layer - sits between AI agents and UI
    Cross-references every recommendation with Governance and Fraud Detection
    """

    def __init__(self):
        self.governance_agent = GovernanceAgent()
        self.fraud_agent = FraudDetectionAgent()
        self.interception_history: List[InterceptedRecommendation] = []

    async def intercept_recommendation(
        self,
        recommendation: AIRecommendation
    ) -> InterceptedRecommendation:
        """
        Intercept and validate an AI recommendation before display
        """
        logger.info(f"🔍 Intercepting recommendation from {recommendation.agent_type.value}")

        # Step 1: Run Governance check
        governance_check = await self.governance_agent.check_recommendation(recommendation)

        # Step 2: Run Fraud Detection check
        fraud_check = await self.fraud_agent.check_recommendation(recommendation)

        # Step 3: Determine if approved
        approved = self._determine_approval(governance_check, fraud_check)

        # Step 4: Prepare display content
        display_content = self._prepare_display_content(
            recommendation,
            governance_check,
            fraud_check,
            approved
        )

        # Step 5: Collect warnings
        warnings = self._collect_warnings(governance_check, fraud_check)

        # Create final intercepted recommendation
        final = InterceptedRecommendation(
            original=recommendation,
            governance_check=governance_check,
            fraud_check=fraud_check,
            approved=approved,
            display_content=display_content,
            warnings=warnings,
            final_timestamp=datetime.now(timezone.utc)
        )

        self.interception_history.append(final)

        if approved:
            logger.info(f"✅ Recommendation approved: {recommendation.recommendation_id}")
        else:
            logger.warning(f"⚠️  Recommendation NOT approved: {recommendation.recommendation_id}")

        return final

    def _determine_approval(
        self,
        governance_check: GovernanceCheck,
        fraud_check: FraudCheck
    ) -> bool:
        """Determine if recommendation should be approved"""
        # Block if non-compliant
        if governance_check.compliance_status == ComplianceStatus.NON_COMPLIANT:
            return False

        # Block if critical trust level
        if fraud_check.trust_level == TrustLevel.CRITICAL:
            return False

        # Block if high risk combined
        total_risk = governance_check.risk_score + fraud_check.fraud_score
        if total_risk > 1.0:
            return False

        return True

    def _prepare_display_content(
        self,
        recommendation: AIRecommendation,
        governance_check: GovernanceCheck,
        fraud_check: FraudCheck,
        approved: bool
    ) -> str:
        """Prepare content for UI display"""
        content = recommendation.content

        # Add governance information
        if governance_check.issues_found:
            content += "\n\n⚠️ Compliance Notes:\n"
            for issue in governance_check.issues_found:
                content += f"  • {issue}\n"

        # Add trust information
        if fraud_check.red_flags:
            content += "\n\n🚩 Trust Warnings:\n"
            for flag in fraud_check.red_flags:
                content += f"  • {flag}\n"

        if fraud_check.trust_indicators:
            content += "\n\n✅ Trust Indicators:\n"
            for indicator in fraud_check.trust_indicators:
                content += f"  • {indicator}\n"

        # Add badge
        trust_badge = f"[TRUST: {fraud_check.trust_level.value.upper()}]"
        compliance_badge = f"[COMPLIANCE: {governance_check.compliance_status.value.upper()}]"
        
        content = f"{trust_badge} {compliance_badge}\n\n{content}"

        return content

    def _collect_warnings(
        self,
        governance_check: GovernanceCheck,
        fraud_check: FraudCheck
    ) -> List[str]:
        """Collect all warnings from both agents"""
        warnings = []
        warnings.extend(governance_check.issues_found)
        warnings.extend(fraud_check.red_flags)
        return warnings

    def get_interception_stats(self) -> Dict[str, Any]:
        """Get statistics about interceptions"""
        total = len(self.interception_history)
        approved = sum(1 for r in self.interception_history if r.approved)
        blocked = total - approved

        return {
            "total_interceptions": total,
            "approved": approved,
            "blocked": blocked,
            "approval_rate": approved / total if total > 0 else 0
        }

# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

agent_intercept_layer = AgentInterceptLayer()
