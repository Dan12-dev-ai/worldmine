"""
Behavioral Reputation Oracle - DEDAN Mine
AI-powered trust scoring and dynamic platform fee calculation
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import asyncio
from dataclasses import dataclass

from database import get_db
from models import User, Transaction, TrustSignal

@dataclass
class ReputationMetrics:
    """Reputation calculation metrics"""
    successful_trades: int
    dispute_free_trades: int
    total_trades: int
    lab_certificates: int
    verification_level: str
    account_age_days: int
    reputation_score: float
    platform_fee_discount: float

class ReputationOracle:
    """AI-powered reputation scoring system"""
    
    def __init__(self):
        self.scoring_weights = {
            "trade_success_rate": 0.30,      # 30% weight
            "dispute_free_rate": 0.25,        # 25% weight
            "certification_level": 0.20,       # 20% weight
            "account_age": 0.15,              # 15% weight
            "verification_status": 0.10          # 10% weight
        }
        
        self.fee_tiers = {
            "excellent": {"min_score": 90, "discount": 0.50},    # 50% discount
            "very_good": {"min_score": 80, "discount": 0.30},   # 30% discount
            "good": {"min_score": 70, "discount": 0.15},       # 15% discount
            "average": {"min_score": 60, "discount": 0.05},     # 5% discount
            "standard": {"min_score": 0, "discount": 0.00}       # No discount
        }
    
    async def calculate_trust_score(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Calculate comprehensive trust score for user"""
        try:
            # Get user data
            user = await self._get_user_data(user_id)
            if not user:
                return {"success": False, "error": "User not found"}
            
            # Calculate individual components
            trade_success_rate = await self._calculate_trade_success_rate(user_id)
            dispute_free_rate = await self._calculate_dispute_free_rate(user_id)
            certification_score = await self._calculate_certification_score(user)
            account_age_score = await self._calculate_account_age_score(user)
            verification_score = await self._calculate_verification_score(user)
            
            # Calculate weighted overall score
            overall_score = (
                trade_success_rate * self.scoring_weights["trade_success_rate"] +
                dispute_free_rate * self.scoring_weights["dispute_free_rate"] +
                certification_score * self.scoring_weights["certification_level"] +
                account_age_score * self.scoring_weights["account_age"] +
                verification_score * self.scoring_weights["verification_status"]
            )
            
            # Determine fee discount
            fee_discount = self._calculate_fee_discount(overall_score)
            
            # Create reputation metrics
            metrics = ReputationMetrics(
                successful_trades=await self._get_successful_trades_count(user_id),
                dispute_free_trades=await self._get_dispute_free_trades_count(user_id),
                total_trades=await self._get_total_trades_count(user_id),
                lab_certificates=await self._get_lab_certificates_count(user_id),
                verification_level=user.verification_level,
                account_age_days=(datetime.now(timezone.utc) - user.created_at).days,
                reputation_score=overall_score,
                platform_fee_discount=fee_discount
            )
            
            # Update user's reputation score
            await self._update_user_reputation(user_id, overall_score, fee_discount)
            
            return {
                "success": True,
                "user_id": user_id,
                "reputation_score": round(overall_score, 2),
                "fee_discount_percent": round(fee_discount * 100, 1),
                "fee_tier": self._get_fee_tier(overall_score),
                "components": {
                    "trade_success_rate": round(trade_success_rate, 2),
                    "dispute_free_rate": round(dispute_free_rate, 2),
                    "certification_score": round(certification_score, 2),
                    "account_age_score": round(account_age_score, 2),
                    "verification_score": round(verification_score, 2)
                },
                "metrics": {
                    "successful_trades": metrics.successful_trades,
                    "dispute_free_trades": metrics.dispute_free_trades,
                    "total_trades": metrics.total_trades,
                    "lab_certificates": metrics.lab_certificates,
                    "verification_level": metrics.verification_level,
                    "account_age_days": metrics.account_age_days
                },
                "calculated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_platform_fee_rate(
        self,
        user_id: str,
        base_fee_rate: float = 0.05  # 5% base rate
    ) -> Dict[str, Any]:
        """Get dynamic platform fee rate for user"""
        try:
            # Get current reputation score
            reputation_result = await self.calculate_trust_score(user_id)
            
            if not reputation_result["success"]:
                return {
                    "success": False,
                    "error": reputation_result["error"]
                }
            
            fee_discount = reputation_result["fee_discount_percent"] / 100
            adjusted_fee_rate = base_fee_rate * (1 - fee_discount)
            
            return {
                "success": True,
                "user_id": user_id,
                "base_fee_rate": base_fee_rate,
                "fee_discount_percent": reputation_result["fee_discount_percent"],
                "adjusted_fee_rate": round(adjusted_fee_rate, 4),
                "savings_per_1000": round(1000 * (base_fee_rate - adjusted_fee_rate), 2),
                "reputation_score": reputation_result["reputation_score"],
                "fee_tier": reputation_result["fee_tier"]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_user_data(self, user_id: str) -> Optional[User]:
        """Get user data from database"""
        try:
            db = next(get_db())
            return db.query(User).filter(User.id == user_id).first()
        except Exception as e:
            print(f"Error getting user data: {e}")
            return None
    
    async def _calculate_trade_success_rate(self, user_id: str) -> float:
        """Calculate trade success rate (0-100)"""
        try:
            db = next(get_db())
            
            # Get user's transactions (this would be implemented based on actual transaction table)
            # For now, simulate with mock data
            successful_trades = await self._get_successful_trades_count(user_id)
            total_trades = await self._get_total_trades_count(user_id)
            
            if total_trades == 0:
                return 50.0  # Neutral score for new users
            
            success_rate = (successful_trades / total_trades) * 100
            return min(success_rate, 100.0)
            
        except Exception as e:
            print(f"Error calculating trade success rate: {e}")
            return 50.0
    
    async def _calculate_dispute_free_rate(self, user_id: str) -> float:
        """Calculate dispute-free trade rate (0-100)"""
        try:
            dispute_free_trades = await self._get_dispute_free_trades_count(user_id)
            total_trades = await self._get_total_trades_count(user_id)
            
            if total_trades == 0:
                return 50.0  # Neutral score for new users
            
            dispute_rate = (dispute_free_trades / total_trades) * 100
            return min(dispute_rate, 100.0)
            
        except Exception as e:
            print(f"Error calculating dispute-free rate: {e}")
            return 50.0
    
    async def _calculate_certification_score(self, user_id: str) -> float:
        """Calculate certification score based on lab-verified certificates"""
        try:
            lab_certificates = await self._get_lab_certificates_count(user_id)
            
            # Scoring based on number and quality of certificates
            if lab_certificates >= 5:
                return 100.0
            elif lab_certificates >= 3:
                return 80.0
            elif lab_certificates >= 1:
                return 60.0
            else:
                return 20.0  # Low score for no certificates
                
        except Exception as e:
            print(f"Error calculating certification score: {e}")
            return 20.0
    
    async def _calculate_account_age_score(self, user_id: str) -> float:
        """Calculate account age score (0-100)"""
        try:
            user = await self._get_user_data(user_id)
            if not user:
                return 0.0
            
            account_age_days = (datetime.now(timezone.utc) - user.created_at).days
            
            # Scoring based on account age
            if account_age_days >= 365:  # 1+ year
                return 100.0
            elif account_age_days >= 180:  # 6+ months
                return 80.0
            elif account_age_days >= 90:   # 3+ months
                return 60.0
            elif account_age_days >= 30:   # 1+ month
                return 40.0
            else:                           # < 1 month
                return 20.0
                
        except Exception as e:
            print(f"Error calculating account age score: {e}")
            return 20.0
    
    async def _calculate_verification_score(self, user_id: str) -> float:
        """Calculate verification score based on verification level"""
        try:
            user = await self._get_user_data(user_id)
            if not user:
                return 0.0
            
            verification_level = user.verification_level
            
            # Scoring based on verification level
            if verification_level == "enterprise":
                return 100.0
            elif verification_level == "professional":
                return 80.0
            elif verification_level == "basic":
                return 60.0
            elif verification_level == "none":
                return 20.0
            else:
                return 40.0  # Unknown level
                
        except Exception as e:
            print(f"Error calculating verification score: {e}")
            return 40.0
    
    def _calculate_fee_discount(self, reputation_score: float) -> float:
        """Calculate fee discount based on reputation score"""
        for tier_name, tier_config in self.fee_tiers.items():
            if reputation_score >= tier_config["min_score"]:
                return tier_config["discount"]
        
        return 0.0  # No discount for scores below minimum
    
    def _get_fee_tier(self, reputation_score: float) -> str:
        """Get fee tier name based on reputation score"""
        for tier_name, tier_config in self.fee_tiers.items():
            if reputation_score >= tier_config["min_score"]:
                return tier_name.replace("_", " ").title()
        
        return "Standard"
    
    async def _update_user_reputation(
        self,
        user_id: str,
        reputation_score: float,
        fee_discount: float
    ) -> None:
        """Update user's reputation score in database"""
        try:
            db = next(get_db())
            user = db.query(User).filter(User.id == user_id).first()
            
            if user:
                user.reputation_score = reputation_score
                user.updated_at = datetime.now(timezone.utc)
                db.commit()
                
        except Exception as e:
            print(f"Error updating user reputation: {e}")
    
    async def _get_successful_trades_count(self, user_id: str) -> int:
        """Get count of successful trades for user"""
        # This would query actual transaction data
        # For now, return mock data
        return 15  # Mock successful trades
    
    async def _get_dispute_free_trades_count(self, user_id: str) -> int:
        """Get count of dispute-free trades for user"""
        # This would query actual transaction data
        # For now, return mock data
        return 14  # Mock dispute-free trades
    
    async def _get_total_trades_count(self, user_id: str) -> int:
        """Get total count of trades for user"""
        # This would query actual transaction data
        # For now, return mock data
        return 16  # Mock total trades
    
    async def _get_lab_certificates_count(self, user_id: str) -> int:
        """Get count of lab-verified certificates for user"""
        # This would query certificate data
        # For now, return mock data
        return 3  # Mock certificates

# Singleton instance
reputation_oracle = ReputationOracle()
