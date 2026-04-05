"""
Instant Micro-Insurance Oracle - DEDAN Mine Unified Architecture
Real-time risk-assessed premium calculation with unified state management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import json
import asyncio
import math
from dataclasses import dataclass

from ..core import unified_state_manager, FeaturePriority

@dataclass
class InsurancePolicy:
    """Micro-insurance policy structure"""
    policy_id: str
    user_id: str
    coverage_amount: float
    premium_rate: float
    risk_factors: Dict[str, float]
    satellite_verified: bool
    location_risk: float
    active: bool
    created_at: datetime
    expires_at: datetime

class MicroInsuranceOracle:
    """Instant Micro-Insurance Oracle with unified state integration"""
    
    def __init__(self):
        self.base_premium_rate = 0.05  # 5% base rate
        self.max_coverage = 100000  # $100,000 max coverage
        self.min_coverage = 1000    # $1,000 min coverage
        
        # Risk factor weights
        self.risk_weights = {
            "satellite_verification": 0.25,
            "location_risk": 0.20,
            "user_reputation": 0.20,
            "transaction_history": 0.15,
            "market_volatility": 0.10,
            "environmental_factors": 0.10
        }
        
        # Location risk factors (mock data)
        self.location_risk_map = {
            "high_risk": {"premium_multiplier": 1.5, "regions": ["conflict_zones", "high_theft_areas"]},
            "medium_risk": {"premium_multiplier": 1.2, "regions": ["urban_centers", "border_regions"]},
            "low_risk": {"premium_multiplier": 1.0, "regions": ["stable_areas", "secured_mines"]}
        }
    
    async def calculate_insurance_premium(
        self,
        session_id: str,
        coverage_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate real-time insurance premium based on risk assessment"""
        try:
            # Get unified session
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Validate coverage request
            validation_result = await self._validate_coverage_request(coverage_request)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Calculate risk factors
            risk_assessment = await self._calculate_risk_factors(session, coverage_request)
            
            # Calculate premium rate
            premium_rate = await self._calculate_premium_rate(risk_assessment)
            
            # Calculate total premium
            coverage_amount = coverage_request["coverage_amount"]
            total_premium = coverage_amount * premium_rate
            
            # Create insurance policy
            policy = await self._create_insurance_policy(session, coverage_request, risk_assessment, premium_rate)
            
            # Execute micro-insurance feature through unified state
            result = await unified_state_manager.execute_feature_request(
                feature_name="instant_micro_insurance_oracle",
                user_id=session.user_id,
                session_id=session_id,
                request_data={
                    "policy": policy.__dict__,
                    "risk_assessment": risk_assessment,
                    "premium_rate": premium_rate,
                    "total_premium": total_premium,
                    "coverage_request": coverage_request
                }
            )
            
            if result["success"]:
                return {
                    "success": True,
                    "policy_id": policy.policy_id,
                    "coverage_amount": coverage_amount,
                    "premium_rate": premium_rate,
                    "total_premium": total_premium,
                    "risk_assessment": risk_assessment,
                    "policy_active": True,
                    "expires_at": policy.expires_at.isoformat(),
                    "payment_required": True,
                    "coverage_details": {
                        "base_premium": self.base_premium_rate,
                        "risk_adjustment": premium_rate / self.base_premium_rate,
                        "discounts_applied": risk_assessment.get("discounts", []),
                        "coverage_limits": {
                            "min": self.min_coverage,
                            "max": self.max_coverage
                        }
                    }
                }
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_coverage_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Validate insurance coverage request"""
        try:
            coverage_amount = request.get("coverage_amount")
            policy_type = request.get("policy_type", "standard")
            
            # Check coverage amount
            if not coverage_amount or not isinstance(coverage_amount, (int, float)):
                return {"valid": False, "error": "Invalid coverage amount"}
            
            if coverage_amount < self.min_coverage:
                return {"valid": False, "error": f"Coverage amount must be at least ${self.min_coverage:,}"}
            
            if coverage_amount > self.max_coverage:
                return {"valid": False, "error": f"Coverage amount cannot exceed ${self.max_coverage:,}"}
            
            # Check policy type
            valid_policy_types = ["standard", "premium", "comprehensive"]
            if policy_type not in valid_policy_types:
                return {"valid": False, "error": f"Invalid policy type. Must be one of: {valid_policy_types}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _calculate_risk_factors(
        self,
        session: UnifiedUserSession,
        coverage_request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate comprehensive risk factors"""
        try:
            risk_factors = {}
            total_risk = 0.0
            
            # 1. Satellite verification risk (25% weight)
            satellite_risk = await self._calculate_satellite_risk(session)
            risk_factors["satellite_verification"] = satellite_risk
            total_risk += satellite_risk * self.risk_weights["satellite_verification"]
            
            # 2. Location risk (20% weight)
            location_risk = await self._calculate_location_risk(session)
            risk_factors["location_risk"] = location_risk
            total_risk += location_risk * self.risk_weights["location_risk"]
            
            # 3. User reputation risk (20% weight)
            reputation_risk = await self._calculate_reputation_risk(session)
            risk_factors["user_reputation"] = reputation_risk
            total_risk += reputation_risk * self.risk_weights["user_reputation"]
            
            # 4. Transaction history risk (15% weight)
            transaction_risk = await self._calculate_transaction_risk(session)
            risk_factors["transaction_history"] = transaction_risk
            total_risk += transaction_risk * self.risk_weights["transaction_history"]
            
            # 5. Market volatility risk (10% weight)
            market_risk = await self._calculate_market_risk(coverage_request)
            risk_factors["market_volatility"] = market_risk
            total_risk += market_risk * self.risk_weights["market_volatility"]
            
            # 6. Environmental factors risk (10% weight)
            environmental_risk = await self._calculate_environmental_risk(session, coverage_request)
            risk_factors["environmental_factors"] = environmental_risk
            total_risk += environmental_risk * self.risk_weights["environmental_factors"]
            
            # Calculate discounts
            discounts = await self._calculate_discounts(session, risk_factors)
            
            return {
                "risk_factors": risk_factors,
                "total_risk_score": total_risk,
                "risk_level": await self._determine_risk_level(total_risk),
                "discounts": discounts,
                "final_risk_score": max(0.1, total_risk - sum(discounts.values()))
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    async def _calculate_satellite_risk(self, session: UnifiedUserSession) -> float:
        """Calculate satellite verification risk factor"""
        try:
            if session.space_verified and session.location_verified:
                return 0.1  # Low risk if verified
            elif session.location_verified:
                return 0.3  # Medium risk if only location verified
            else:
                return 0.8  # High risk if not verified
                
        except Exception as e:
            return 0.5  # Default medium risk
    
    async def _calculate_location_risk(self, session: UnifiedUserSession) -> float:
        """Calculate location-based risk factor"""
        try:
            if not session.satellite_coordinates:
                return 0.7  # High risk if no coordinates
            
            lat = session.satellite_coordinates.get("latitude", 0)
            lng = session.satellite_coordinates.get("longitude", 0)
            
            # Mock location risk assessment
            # In production, use actual geographic risk data
            if self._is_high_risk_region(lat, lng):
                return 0.8  # High risk
            elif self._is_medium_risk_region(lat, lng):
                return 0.4  # Medium risk
            else:
                return 0.2  # Low risk
                
        except Exception as e:
            return 0.5  # Default medium risk
    
    async def _calculate_reputation_risk(self, session: UnifiedUserSession) -> float:
        """Calculate user reputation-based risk factor"""
        try:
            trust_score = session.trust_score
            
            if trust_score >= 90:
                return 0.1  # Very low risk for excellent reputation
            elif trust_score >= 80:
                return 0.2  # Low risk for good reputation
            elif trust_score >= 70:
                return 0.3  # Medium-low risk
            elif trust_score >= 60:
                return 0.5  # Medium risk
            elif trust_score >= 50:
                return 0.7  # Medium-high risk
            else:
                return 0.9  # High risk for poor reputation
                
        except Exception as e:
            return 0.5  # Default medium risk
    
    async def _calculate_transaction_risk(self, session: UnifiedUserSession) -> float:
        """Calculate transaction history-based risk factor"""
        try:
            trade_history = session.trade_history
            
            if len(trade_history) == 0:
                return 0.6  # Medium risk for no history
            
            # Calculate success rate
            successful_trades = len([t for t in trade_history if t.get("status") == "completed"])
            total_trades = len(trade_history)
            success_rate = successful_trades / total_trades if total_trades > 0 else 0
            
            # Calculate frequency
            recent_trades = [t for t in trade_history if 
                           datetime.fromisoformat(t["timestamp"]) > datetime.now(timezone.utc) - timedelta(days=30)]
            trade_frequency = len(recent_trades)
            
            # Risk calculation
            if success_rate >= 0.95 and trade_frequency >= 10:
                return 0.1  # Very low risk
            elif success_rate >= 0.90 and trade_frequency >= 5:
                return 0.2  # Low risk
            elif success_rate >= 0.80:
                return 0.4  # Medium risk
            elif success_rate >= 0.70:
                return 0.6  # Medium-high risk
            else:
                return 0.8  # High risk
                
        except Exception as e:
            return 0.5  # Default medium risk
    
    async def _calculate_market_risk(self, coverage_request: Dict[str, Any]) -> float:
        """Calculate market volatility risk factor"""
        try:
            policy_type = coverage_request.get("policy_type", "standard")
            coverage_amount = coverage_request["coverage_amount"]
            
            # Mock market volatility calculation
            # In production, use actual market data
            base_market_risk = 0.3  # Base market risk
            
            # Adjust for coverage amount
            if coverage_amount > 50000:
                base_market_risk += 0.2  # Higher risk for large coverage
            elif coverage_amount > 20000:
                base_market_risk += 0.1  # Slightly higher risk for medium coverage
            
            # Adjust for policy type
            if policy_type == "comprehensive":
                base_market_risk += 0.1  # Higher risk for comprehensive coverage
            elif policy_type == "premium":
                base_market_risk += 0.05  # Slightly higher risk for premium
            
            return min(1.0, base_market_risk)
            
        except Exception as e:
            return 0.3  # Default market risk
    
    async def _calculate_environmental_risk(
        self,
        session: UnifiedUserSession,
        coverage_request: Dict[str, Any]
    ) -> float:
        """Calculate environmental factors risk"""
        try:
            # Get ESG metrics from session
            esg_score = session.esg_score
            
            if esg_score >= 80:
                return 0.1  # Low risk for high ESG score
            elif esg_score >= 60:
                return 0.3  # Medium risk for moderate ESG score
            elif esg_score >= 40:
                return 0.5  # Medium-high risk for low ESG score
            else:
                return 0.7  # High risk for very low ESG score
                
        except Exception as e:
            return 0.4  # Default environmental risk
    
    async def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score <= 0.2:
            return "very_low"
        elif risk_score <= 0.4:
            return "low"
        elif risk_score <= 0.6:
            return "medium"
        elif risk_score <= 0.8:
            return "high"
        else:
            return "very_high"
    
    async def _calculate_discounts(
        self,
        session: UnifiedUserSession,
        risk_factors: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate applicable discounts"""
        discounts = {}
        
        # Reputation discount
        if session.trust_score >= 90:
            discounts["reputation_bonus"] = 0.05  # 5% discount
        elif session.trust_score >= 80:
            discounts["reputation_bonus"] = 0.02  # 2% discount
        
        # Satellite verification discount
        if session.space_verified:
            discounts["satellite_verified"] = 0.03  # 3% discount
        
        # ESG discount
        if session.esg_score >= 80:
            discounts["esg_excellent"] = 0.02  # 2% discount
        elif session.esg_score >= 60:
            discounts["esg_good"] = 0.01  # 1% discount
        
        # Multi-policy discount (if user has multiple policies)
        existing_policies = len(session.insurance_claims)
        if existing_policies >= 2:
            discounts["multi_policy"] = 0.05  # 5% discount
        elif existing_policies >= 1:
            discounts["multi_policy"] = 0.02  # 2% discount
        
        return discounts
    
    async def _calculate_premium_rate(self, risk_assessment: Dict[str, Any]) -> float:
        """Calculate final premium rate"""
        try:
            final_risk_score = risk_assessment.get("final_risk_score", 0.5)
            
            # Premium rate calculation
            premium_rate = self.base_premium_rate * (1 + final_risk_score)
            
            # Ensure premium rate is within reasonable bounds
            premium_rate = max(0.01, min(0.20, premium_rate))  # 1% to 20%
            
            return premium_rate
            
        except Exception as e:
            return self.base_premium_rate  # Default to base rate
    
    async def _create_insurance_policy(
        self,
        session: UnifiedUserSession,
        coverage_request: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        premium_rate: float
    ) -> InsurancePolicy:
        """Create insurance policy"""
        try:
            import uuid
            
            policy = InsurancePolicy(
                policy_id=str(uuid.uuid4()),
                user_id=session.user_id,
                coverage_amount=coverage_request["coverage_amount"],
                premium_rate=premium_rate,
                risk_factors=risk_assessment["risk_factors"],
                satellite_verified=session.space_verified,
                location_risk=risk_assessment["risk_factors"].get("location_risk", 0.5),
                active=True,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(days=30)  # 30-day policy
            )
            
            return policy
            
        except Exception as e:
            raise Exception(f"Error creating policy: {str(e)}")
    
    def _is_high_risk_region(self, lat: float, lng: float) -> bool:
        """Check if coordinates are in high-risk region"""
        # Mock implementation - use actual geographic risk data in production
        high_risk_regions = [
            {"lat_min": 0, "lat_max": 5, "lng_min": 30, "lng_max": 40},  # Example region
            {"lat_min": -5, "lat_max": 0, "lng_min": 20, "lng_max": 30}   # Example region
        ]
        
        for region in high_risk_regions:
            if (region["lat_min"] <= lat <= region["lat_max"] and 
                region["lng_min"] <= lng <= region["lng_max"]):
                return True
        
        return False
    
    def _is_medium_risk_region(self, lat: float, lng: float) -> bool:
        """Check if coordinates are in medium-risk region"""
        # Mock implementation
        medium_risk_regions = [
            {"lat_min": 5, "lat_max": 10, "lng_min": 35, "lng_max": 45},
            {"lat_min": -10, "lat_max": -5, "lng_min": 25, "lng_max": 35}
        ]
        
        for region in medium_risk_regions:
            if (region["lat_min"] <= lat <= region["lat_max"] and 
                region["lng_min"] <= lng <= region["lng_max"]):
                return True
        
        return False
    
    async def process_insurance_claim(
        self,
        session_id: str,
        claim_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process insurance claim with automated verification"""
        try:
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Validate claim
            validation_result = await self._validate_claim(session, claim_data)
            if not validation_result["valid"]:
                return {"success": False, "error": validation_result["error"]}
            
            # Automated claim review
            claim_review = await self._automated_claim_review(session, claim_data)
            
            # Process claim payment if approved
            if claim_review["approved"]:
                payment_result = await self._process_claim_payment(session, claim_data, claim_review)
            else:
                payment_result = {"status": "rejected", "reason": claim_review["rejection_reason"]}
            
            # Update session with claim
            claim_record = {
                "claim_id": claim_data.get("claim_id"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "amount": claim_data.get("claim_amount"),
                "status": payment_result["status"],
                "review_result": claim_review
            }
            
            session.insurance_claims.append(claim_record)
            
            return {
                "success": True,
                "claim_processed": True,
                "claim_status": payment_result["status"],
                "payout_amount": payment_result.get("payout_amount", 0),
                "processing_time": claim_review["processing_time"],
                "automated_review": claim_review
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _validate_claim(self, session: UnifiedUserSession, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate insurance claim"""
        try:
            # Check required fields
            required_fields = ["claim_id", "claim_amount", "incident_date", "incident_type"]
            for field in required_fields:
                if field not in claim_data:
                    return {"valid": False, "error": f"Missing required field: {field}"}
            
            # Check claim amount
            claim_amount = claim_data["claim_amount"]
            coverage_amount = session.coverage_amount if hasattr(session, 'coverage_amount') else 0
            
            if claim_amount > coverage_amount:
                return {"valid": False, "error": f"Claim amount ${claim_amount:,} exceeds coverage ${coverage_amount:,}"}
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def _automated_claim_review(self, session: UnifiedUserSession, claim_data: Dict[str, Any]) -> Dict[str, Any]:
        """Automated claim review using AI"""
        try:
            start_time = datetime.now(timezone.utc)
            
            # Simulate AI review process
            await asyncio.sleep(0.5)  # Simulate processing time
            
            # Mock approval logic (90% approval rate for demonstration)
            import random
            approved = random.random() < 0.9
            
            processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()
            
            if approved:
                return {
                    "approved": True,
                    "confidence": 0.95,
                    "processing_time": processing_time,
                    "review_factors": {
                        "claim_history": "clean",
                        "incident_verification": "passed",
                        "coverage_validation": "confirmed"
                    }
                }
            else:
                return {
                    "approved": False,
                    "confidence": 0.85,
                    "processing_time": processing_time,
                    "rejection_reason": "Insufficient evidence for incident verification"
                }
                
        except Exception as e:
            return {"approved": False, "error": str(e)}
    
    async def _process_claim_payment(
        self,
        session: UnifiedUserSession,
        claim_data: Dict[str, Any],
        claim_review: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process claim payment"""
        try:
            claim_amount = claim_data["claim_amount"]
            
            # Mock payment processing
            await asyncio.sleep(0.2)
            
            return {
                "status": "paid",
                "payout_amount": claim_amount,
                "payment_method": "blockchain",
                "transaction_id": f"CLAIM_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "processed_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    
    async def calculate_esg_adjusted_premium(self, premium_request: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate insurance premium with ESG adjustments including satellite-verified reforestation"""
        try:
            user_id = premium_request["user_id"]
            mineral_type = premium_request["mineral_type"]
            coverage_amount = premium_request["coverage_amount"]
            
            # Get base premium
            base_premium_result = await self.calculate_premium(premium_request)
            base_premium = base_premium_result["premium_amount"]
            
            # Get ESG data
            esg_data = await self._get_user_esg_data(user_id)
            
            # Satellite-verified reforestation multiplier (mandatory)
            reforestation_multiplier = await self._calculate_reforestation_multiplier(esg_data)
            
            # Other ESG factors
            ethical_score_multiplier = esg_data.get("ethical_impact_score", 1.0)
            sustainability_multiplier = esg_data.get("sustainability_score", 1.0)
            governance_multiplier = esg_data.get("governance_score", 1.0)
            
            # Calculate ESG-adjusted premium
            combined_esg_multiplier = (
                reforestation_multiplier *  # Mandatory satellite-verified reforestation
                ethical_score_multiplier *
                sustainability_multiplier *
                governance_multiplier
            )
            
            esg_adjusted_premium = base_premium * combined_esg_multiplier
            
            # Generate ESG report
            esg_report = {
                "base_premium": base_premium,
                "esg_adjusted_premium": esg_adjusted_premium,
                "esg_discount_percentage": ((base_premium - esg_adjusted_premium) / base_premium) * 100,
                "multipliers": {
                    "reforestation": reforestation_multiplier,
                    "ethical_score": ethical_score_multiplier,
                    "sustainability": sustainability_multiplier,
                    "governance": governance_multiplier
                },
                "satellite_verified": esg_data.get("satellite_verified", False),
                "reforestation_acres": esg_data.get("reforestation_acres", 0),
                "tree_count": esg_data.get("tree_count", 0)
            }
            
            return {
                "success": True,
                "premium_amount": esg_adjusted_premium,
                "base_premium": base_premium,
                "esg_adjustment": esg_report,
                "currency": "USD",
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_user_esg_data(self, user_id: str) -> Dict[str, Any]:
        """Get user's ESG data including satellite-verified reforestation"""
        # Mock ESG data - in production, integrate with actual ESG systems
        return {
            "ethical_impact_score": 0.85,  # 15% discount
            "sustainability_score": 0.90,  # 10% discount
            "governance_score": 0.95,     # 5% discount
            "satellite_verified": True,
            "reforestation_acres": 100.5,
            "tree_count": 50000,
            "carbon_sequestered_tons": 250.0,
            "reforestation_survival_rate": 0.85,
            "last_verification_date": datetime.now(timezone.utc).isoformat()
        }
    
    async def _calculate_reforestation_multiplier(self, esg_data: Dict[str, Any]) -> float:
        """Calculate satellite-verified reforestation multiplier"""
        if not esg_data.get("satellite_verified", False):
            return 1.0  # No discount if not satellite verified
        
        reforestation_acres = esg_data.get("reforestation_acres", 0)
        tree_count = esg_data.get("tree_count", 0)
        survival_rate = esg_data.get("reforestation_survival_rate", 0.8)
        
        # Base reforestation discount: up to 20% based on scale and survival
        if reforestation_acres >= 1000 and survival_rate >= 0.9:
            base_discount = 0.20  # 20% discount
        elif reforestation_acres >= 500 and survival_rate >= 0.85:
            base_discount = 0.15  # 15% discount
        elif reforestation_acres >= 100 and survival_rate >= 0.8:
            base_discount = 0.10  # 10% discount
        elif reforestation_acres >= 50 and survival_rate >= 0.75:
            base_discount = 0.05  # 5% discount
        else:
            base_discount = 0.0  # No discount
        
        # Apply survival rate adjustment
        survival_adjustment = min(1.0, survival_rate / 0.8)  # Normalize to 80% baseline
        
        final_multiplier = 1.0 - (base_discount * survival_adjustment)
        
        return max(0.5, final_multiplier)  # Minimum 50% of base premium

# Singleton instance
micro_insurance_oracle = MicroInsuranceOracle()
