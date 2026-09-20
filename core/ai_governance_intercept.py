"""
World-Mine AI Governance Intercept Layer
Enterprise-grade AI validation for fraud, compliance, and risk
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GovernanceDecision(Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"

@dataclass
class GovernanceResult:
    decision: GovernanceDecision
    confidence: float
    reasons: List[str]
    risk_score: float
    timestamp: datetime

class AIGovernanceInterceptLayer:
    """Enterprise-grade AI governance intercept layer"""
    
    def __init__(self):
        self.fraud_threshold = 0.7
        self.compliance_threshold = 0.8
        self.risk_threshold = 0.6
        
    async def validate_ai_recommendation(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> GovernanceResult:
        """
        Validate AI recommendation before execution
        
        Args:
            recommendation: AI-generated recommendation
            context: Transaction/user context
            
        Returns:
            GovernanceResult with decision and details
        """
        logger.info("Validating AI recommendation...")
        
        # Run all validation checks
        fraud_result = await self._check_fraud(recommendation, context)
        compliance_result = await self._check_compliance(recommendation, context)
        risk_result = await self._assess_risk(recommendation, context)
        
        # Aggregate results
        overall_decision = self._aggregate_decisions(
            fraud_result, compliance_result, risk_result
        )
        
        logger.info(f"Governance decision: {overall_decision.decision.value}")
        
        return overall_decision
        
    async def _check_fraud(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check for fraud indicators"""
        fraud_score = 0.0
        reasons = []
        
        # Check transaction amount
        amount = recommendation.get("amount", 0)
        if amount > 1000000:
            fraud_score += 0.3
            reasons.append("High transaction amount")
            
        # Check user reputation
        reputation = context.get("user_reputation", 0)
        if reputation < 50:
            fraud_score += 0.4
            reasons.append("Low user reputation")
            
        # Check for rapid transactions
        tx_count = context.get("recent_tx_count", 0)
        if tx_count > 10:
            fraud_score += 0.2
            reasons.append("High transaction frequency")
            
        return {
            "score": fraud_score,
            "flagged": fraud_score > self.fraud_threshold,
            "reasons": reasons
        }
        
    async def _check_compliance(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check regulatory compliance"""
        compliance_score = 1.0
        reasons = []
        
        # Check KYC status
        kyc_verified = context.get("kyc_verified", False)
        if not kyc_verified:
            compliance_score -= 0.5
            reasons.append("KYC not verified")
            
        # Check sanctions
        sanctioned = context.get("sanctioned", False)
        if sanctioned:
            compliance_score -= 1.0
            reasons.append("Sanctioned entity")
            
        # Check jurisdiction
        jurisdiction = context.get("jurisdiction", "")
        if jurisdiction in ["restricted_jurisdiction_1", "restricted_jurisdiction_2"]:
            compliance_score -= 0.3
            reasons.append("Restricted jurisdiction")
            
        return {
            "score": compliance_score,
            "compliant": compliance_score > self.compliance_threshold,
            "reasons": reasons
        }
        
    async def _assess_risk(
        self,
        recommendation: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess overall risk level"""
        risk_score = 0.0
        reasons = []
        
        # Market volatility risk
        volatility = context.get("market_volatility", 0)
        risk_score += volatility * 0.3
        
        # Counterparty risk
        counterparty_risk = context.get("counterparty_risk", 0)
        risk_score += counterparty_risk * 0.4
        
        # Operational risk
        operational_risk = context.get("operational_risk", 0)
        risk_score += operational_risk * 0.3
        
        if risk_score > 0.5:
            reasons.append("High risk score")
            
        return {
            "score": risk_score,
            "acceptable": risk_score < self.risk_threshold,
            "reasons": reasons
        }
        
    def _aggregate_decisions(
        self,
        fraud_result: Dict[str, Any],
        compliance_result: Dict[str, Any],
        risk_result: Dict[str, Any]
    ) -> GovernanceResult:
        """Aggregate individual validation results"""
        reasons = []
        overall_risk = (fraud_result["score"] + risk_result["score"]) / 2
        
        # Critical failures
        if fraud_result["flagged"]:
            reasons.extend(fraud_result["reasons"])
            
        if not compliance_result["compliant"]:
            reasons.extend(compliance_result["reasons"])
            
        if not risk_result["acceptable"]:
            reasons.extend(risk_result["reasons"])
            
        # Make decision
        if not compliance_result["compliant"] or fraud_result["flagged"]:
            decision = GovernanceDecision.REJECTED
            confidence = 0.9
        elif overall_risk > self.risk_threshold:
            decision = GovernanceDecision.REQUIRES_REVIEW
            confidence = 0.7
        else:
            decision = GovernanceDecision.APPROVED
            confidence = 0.95
            
        return GovernanceResult(
            decision=decision,
            confidence=confidence,
            reasons=reasons,
            risk_score=overall_risk,
            timestamp=datetime.now(timezone.utc)
        )

# Global governance intercept instance
governance_intercept = AIGovernanceInterceptLayer()
