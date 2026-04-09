"""
ESG Scoring Service - DEDAN Mine Environmental & Social Impact
Built-in ESG + Carbon Credit + Social Impact Dashboard with automatic scoring
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid
import json
import asyncio
from dataclasses import dataclass, asdict

from ..models import ESGMetrics, User, Listing
from ..database import get_db
from ..ai.explainableAI import ESGAIAnalyzer

@dataclass
class EnvironmentalMetrics:
    """Environmental impact metrics"""
    carbon_footprint: float  # kg CO2e
    water_usage: float  # liters
    energy_consumption: float  # kWh
    waste_generated: float  # kg
    biodiversity_impact: int  # 0-100 scale
    land_rehabilitation: bool  # Land restored after mining

@dataclass
class SocialMetrics:
    """Social impact metrics"""
    local_jobs_created: int
    community_investment: float  # USD
    training_programs_supported: int
    fair_labor_practices: bool
    health_safety_standards: bool
    community_engagement: int  # 0-100 scale

@dataclass
class GovernanceMetrics:
    """Governance and compliance metrics"""
    regulatory_compliance: bool
    anti_corruption_measures: bool
    transparency_score: int  # 0-100
    stakeholder_engagement: int  # 0-100
    ethical_sourcing: bool

class ESGScoringService:
    """ESG scoring and carbon credit management"""
    
    def __init__(self):
        self.db = next(get_db())
        self.ai_analyzer = ESGAIAnalyzer()
        self.carbon_credit_rates = {
            "solar_renewable": 2.0,  # $2 per ton CO2 avoided
            "reforestation": 5.0,  # $5 per ton CO2 sequestered
            "water_conservation": 1.5,  # $1.5 per 1000 liters saved
            "biodiversity_protection": 3.0  # $3 per hectare protected
        }
    
    async def calculate_esg_score(
        self,
        user_id: str,
        listing_id: str = None,
        environmental_data: Dict[str, Any] = None,
        social_data: Dict[str, Any] = None,
        governance_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Calculate comprehensive ESG score"""
        try:
            # Get existing ESG metrics if available
            existing_metrics = self.db.query(ESGMetrics).filter(
                ESGMetrics.user_id == user_id
            ).first()
            
            # Process environmental data
            env_metrics = await self._process_environmental_data(environment_data or {})
            
            # Process social data
            social_metrics = await self._process_social_data(social_data or {})
            
            # Process governance data
            gov_metrics = await self._process_governance_data(governance_data or {})
            
            # Calculate category scores (0-100)
            environmental_score = await self._calculate_environmental_score(env_metrics)
            social_score = await self._calculate_social_score(social_metrics)
            governance_score = await self._calculate_governance_score(gov_metrics)
            
            # Calculate overall ESG score
            overall_score = (environmental_score * 0.4) + (social_score * 0.3) + (governance_score * 0.3)
            
            # Generate AI explanation
            ai_explanation = await self.ai_analyzer.explain_esg_score(
                environmental_score, social_score, governance_score, overall_score
            )
            
            # Calculate carbon credits
            carbon_credits = await self._calculate_carbon_credits(env_metrics)
            
            # Save or update ESG metrics
            if existing_metrics:
                existing_metrics.overall_score = overall_score
                existing_metrics.environmental_score = environmental_score
                existing_metrics.social_score = social_score
                existing_metrics.governance_score = governance_score
                existing_metrics.carbon_credits_earned = carbon_credits
                existing_metrics.ai_explanation = ai_explanation
                existing_metrics.assessment_date = datetime.now(timezone.utc).date()
                existing_metrics.updated_at = datetime.now(timezone.utc)
            else:
                esg_metrics = ESGMetrics(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    listing_id=listing_id,
                    overall_score=int(overall_score),
                    environmental_score=int(environmental_score),
                    social_score=int(social_score),
                    governance_score=int(governance_score),
                    carbon_credits_earned=carbon_credits,
                    ai_explanation=ai_explanation,
                    assessment_date=datetime.now(timezone.utc).date(),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                self.db.add(esg_metrics)
            
            self.db.commit()
            
            return {
                "success": True,
                "esg_scores": {
                    "overall": int(overall_score),
                    "environmental": int(environmental_score),
                    "social": int(social_score),
                    "governance": int(governance_score)
                },
                "carbon_credits_earned": carbon_credits,
                "ai_explanation": ai_explanation,
                "rating": self._get_esg_rating(overall_score),
                "recommendations": await self._generate_esg_recommendations(overall_score)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def record_esg_impact(
        self,
        user_id: str,
        impact_type: str,  # 'carbon_reduction', 'community_investment', 'training_program', 'biodiversity'
        impact_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Record specific ESG impact activities"""
        try:
            credits_earned = 0
            
            # Calculate credits based on impact type
            if impact_type == "carbon_reduction":
                reduction_tons = impact_data.get("carbon_reduction_tons", 0)
                credits_earned = reduction_tons * self.carbon_credit_rates.get("solar_renewable", 2.0)
            
            elif impact_type == "community_investment":
                investment_amount = impact_data.get("investment_amount", 0)
                credits_earned = investment_amount * 0.01  # 1% of investment as credits
            
            elif impact_type == "training_program":
                participants = impact_data.get("participants", 0)
                credits_earned = participants * self.carbon_credit_rates.get("training_program", 0.5)
            
            elif impact_type == "biodiversity_protection":
                hectares_protected = impact_data.get("hectares_protected", 0)
                credits_earned = hectares_protected * self.carbon_credit_rates.get("biodiversity_protection", 3.0)
            
            # Update user's carbon credits
            user = self.db.query(User).filter(User.id == user_id).first()
            if user:
                user.carbon_credits += credits_earned
                self.db.commit()
            
            # Record impact activity
            impact_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "impact_type": impact_type,
                "impact_data": impact_data,
                "credits_earned": credits_earned,
                "recorded_at": datetime.now(timezone.utc)
            }
            
            return {
                "success": True,
                "credits_earned": credits_earned,
                "total_credits": user.carbon_credits if user else 0,
                "impact_record": impact_record
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_esg_dashboard(
        self,
        user_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive ESG dashboard data"""
        try:
            # Get ESG metrics
            esg_metrics = self.db.query(ESGMetrics).filter(
                ESGMetrics.user_id == user_id
            ).order_by(ESGMetrics.assessment_date.desc()).all()
            
            if not esg_metrics:
                return {"success": False, "error": "No ESG data found"}
            
            # Get user's carbon credit transactions
            credit_transactions = await self._get_carbon_credit_transactions(user_id)
            
            # Calculate trends
            score_trend = self._calculate_score_trend(esg_metrics)
            
            # Generate insights
            insights = await self.ai_analyzer.generate_esg_insights(esg_metrics, credit_transactions)
            
            # Dashboard data
            dashboard = {
                "current_scores": {
                    "overall": esg_metrics[0].overall_score,
                    "environmental": esg_metrics[0].environmental_score,
                    "social": esg_metrics[0].social_score,
                    "governance": esg_metrics[0].governance_score,
                    "rating": self._get_esg_rating(esg_metrics[0].overall_score)
                },
                "score_history": [
                    {
                        "date": metric.assessment_date.isoformat(),
                        "overall": metric.overall_score,
                        "environmental": metric.environmental_score,
                        "social": metric.social_score,
                        "governance": metric.governance_score
                    }
                    for metric in esg_metrics[:12]  # Last 12 assessments
                ],
                "carbon_credits": {
                    "current_balance": credit_transactions["current_balance"],
                    "total_earned": credit_transactions["total_earned"],
                    "total_used": credit_transactions["total_used"],
                    "recent_transactions": credit_transactions["recent"]
                },
                "impact_activities": await self._get_impact_activities(user_id),
                "trends": score_trend,
                "ai_insights": insights,
                "recommendations": await self._generate_dashboard_recommendations(esg_metrics[0])
            }
            
            return {
                "success": True,
                "dashboard": dashboard
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _process_environmental_data(self, env_data: Dict[str, Any]) -> EnvironmentalMetrics:
        """Process environmental impact data"""
        return EnvironmentalMetrics(
            carbon_footprint=env_data.get("carbon_footprint", 0),
            water_usage=env_data.get("water_usage", 0),
            energy_consumption=env_data.get("energy_consumption", 0),
            waste_generated=env_data.get("waste_generated", 0),
            biodiversity_impact=env_data.get("biodiversity_impact", 50),
            land_rehabilitation=env_data.get("land_rehabilitated", False)
        )
    
    async def _process_social_data(self, social_data: Dict[str, Any]) -> SocialMetrics:
        """Process social impact data"""
        return SocialMetrics(
            local_jobs_created=social_data.get("local_jobs_created", 0),
            community_investment=social_data.get("community_investment", 0),
            training_programs_supported=social_data.get("training_programs_supported", 0),
            fair_labor_practices=social_data.get("fair_labor_practices", True),
            health_safety_standards=social_data.get("health_safety_standards", True),
            community_engagement=social_data.get("community_engagement", 70)
        )
    
    async def _process_governance_data(self, gov_data: Dict[str, Any]) -> GovernanceMetrics:
        """Process governance and compliance data"""
        return GovernanceMetrics(
            regulatory_compliance=gov_data.get("regulatory_compliance", True),
            anti_corruption_measures=gov_data.get("anti_corruption_measures", True),
            transparency_score=gov_data.get("transparency_score", 80),
            stakeholder_engagement=gov_data.get("stakeholder_engagement", 75),
            ethical_sourcing=gov_data.get("ethical_sourcing", True)
        )
    
    async def _calculate_environmental_score(self, env_metrics: EnvironmentalMetrics) -> float:
        """Calculate environmental score (0-100)"""
        score = 0
        
        # Carbon footprint (40 points)
        if env_metrics.carbon_footprint <= 10:
            score += 40
        elif env_metrics.carbon_footprint <= 50:
            score += 30
        elif env_metrics.carbon_footprint <= 100:
            score += 20
        
        # Water usage (25 points)
        if env_metrics.water_usage <= 100:
            score += 25
        elif env_metrics.water_usage <= 500:
            score += 15
        elif env_metrics.water_usage <= 1000:
            score += 5
        
        # Energy source (20 points)
        renewable_sources = ['solar', 'wind', 'hydro', 'geothermal']
        if env_metrics.energy_source in renewable_sources:
            score += 20
        
        # Waste management (15 points)
        if env_metrics.waste_generated <= 1:
            score += 15
        elif env_metrics.waste_generated <= 5:
            score += 10
        
        return min(score, 100)
    
    async def _calculate_social_score(self, social_metrics: SocialMetrics) -> float:
        """Calculate social score (0-100)"""
        score = 0
        
        # Local jobs (30 points)
        if social_metrics.local_jobs_created >= 10:
            score += 30
        elif social_metrics.local_jobs_created >= 5:
            score += 20
        elif social_metrics.local_jobs_created >= 1:
            score += 10
        
        # Community investment (25 points)
        if social_metrics.community_investment >= 10000:
            score += 25
        elif social_metrics.community_investment >= 5000:
            score += 15
        elif social_metrics.community_investment >= 1000:
            score += 5
        
        # Training programs (20 points)
        if social_metrics.training_programs_supported >= 5:
            score += 20
        elif social_metrics.training_programs_supported >= 2:
            score += 10
        
        # Fair labor (15 points)
        if social_metrics.fair_labor_practices:
            score += 15
        
        # Health & safety (10 points)
        if social_metrics.health_safety_standards:
            score += 10
        
        return min(score, 100)
    
    async def _calculate_governance_score(self, gov_metrics: GovernanceMetrics) -> float:
        """Calculate governance score (0-100)"""
        score = 0
        
        # Regulatory compliance (30 points)
        if gov_metrics.regulatory_compliance:
            score += 30
        
        # Anti-corruption (25 points)
        if gov_metrics.anti_corruption_measures:
            score += 25
        
        # Transparency (20 points)
        score += gov_metrics.transparency_score * 0.2
        
        # Stakeholder engagement (15 points)
        score += gov_metrics.stakeholder_engagement * 0.15
        
        # Ethical sourcing (10 points)
        if gov_metrics.ethical_sourcing:
            score += 10
        
        return min(score, 100)
    
    async def _calculate_carbon_credits(self, env_metrics: EnvironmentalMetrics) -> float:
        """Calculate carbon credits from environmental metrics"""
        credits = 0
        
        # Credits for carbon reduction
        if env_metrics.carbon_footprint < 50:  # Below average
            credits += (50 - env_metrics.carbon_footprint) * self.carbon_credit_rates.get("solar_renewable", 2.0)
        
        # Credits for water conservation
        if env_metrics.water_usage < 500:
            credits += (500 - env_metrics.water_usage) / 1000 * self.carbon_credit_rates.get("water_conservation", 1.5)
        
        # Credits for biodiversity
        if env_metrics.biodiversity_impact > 80:  # High biodiversity protection
            credits += 10 * self.carbon_credit_rates.get("biodiversity_protection", 3.0)
        
        # Credits for land rehabilitation
        if env_metrics.land_rehabilitation:
            credits += 5
        
        return credits
    
    def _get_esg_rating(self, overall_score: float) -> str:
        """Get ESG rating based on score"""
        if overall_score >= 90:
            return "AAA+"
        elif overall_score >= 85:
            return "AAA"
        elif overall_score >= 80:
            return "AA+"
        elif overall_score >= 75:
            return "AA"
        elif overall_score >= 70:
            return "A+"
        elif overall_score >= 65:
            return "A"
        elif overall_score >= 55:
            return "BBB"
        elif overall_score >= 45:
            return "BB"
        elif overall_score >= 35:
            return "B"
        else:
            return "CCC"
    
    async def _generate_esg_recommendations(self, current_metrics: ESGMetrics) -> List[str]:
        """Generate ESG improvement recommendations"""
        recommendations = []
        
        if current_metrics.environmental_score < 70:
            recommendations.append("Reduce carbon footprint by implementing renewable energy sources")
            recommendations.append("Implement water recycling and conservation measures")
        
        if current_metrics.social_score < 70:
            recommendations.append("Increase local community investment programs")
            recommendations.append("Expand training and skill development programs")
        
        if current_metrics.governance_score < 70:
            recommendations.append("Enhance transparency in reporting and operations")
            recommendations.append("Strengthen stakeholder engagement mechanisms")
        
        return recommendations
    
    async def _get_carbon_credit_transactions(self, user_id: str) -> Dict[str, Any]:
        """Get carbon credit transaction history"""
        # This would query carbon credit transaction table
        # For now, return mock data
        return {
            "current_balance": 150.5,
            "total_earned": 500.0,
            "total_used": 349.5,
            "recent": [
                {
                    "date": "2026-01-15",
                    "type": "earned",
                    "amount": 25.0,
                    "source": "carbon_reduction"
                },
                {
                    "date": "2026-01-10",
                    "type": "used",
                    "amount": 10.0,
                    "purpose": "offset_shipping"
                }
            ]
        }
    
    async def _get_impact_activities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's ESG impact activities"""
        # This would query impact activities table
        # For now, return mock data
        return [
            {
                "date": "2026-01-15",
                "type": "carbon_reduction",
                "description": "Installed solar panels at mining operation",
                "impact": "Reduced carbon footprint by 15 tons CO2",
                "credits_earned": 30.0
            },
            {
                "date": "2026-01-10",
                "type": "community_investment",
                "description": "Funded local school renovation",
                "impact": "Supported 50 students with improved facilities",
                "credits_earned": 25.0
            }
        ]
    
    def _calculate_score_trend(self, esg_metrics: List[ESGMetrics]) -> Dict[str, Any]:
        """Calculate ESG score trends"""
        if len(esg_metrics) < 2:
            return {"trend": "insufficient_data", "change": 0}
        
        recent = esg_metrics[0].overall_score
        previous = esg_metrics[1].overall_score if len(esg_metrics) > 1 else recent
        
        change = recent - previous
        trend = "improving" if change > 2 else "declining" if change < -2 else "stable"
        
        return {
            "trend": trend,
            "change": change,
            "period_days": 30
        }
    
    async def _generate_dashboard_recommendations(self, current_metrics: ESGMetrics) -> List[str]:
        """Generate dashboard-specific recommendations"""
        recommendations = []
        
        # Priority recommendations based on lowest scores
        scores = {
            "environmental": current_metrics.environmental_score,
            "social": current_metrics.social_score,
            "governance": current_metrics.governance_score
        }
        
        lowest_category = min(scores, key=scores.get)
        
        if lowest_category == "environmental":
            recommendations.extend([
                "Conduct environmental impact assessment",
                "Set carbon reduction targets",
                "Invest in renewable energy"
            ])
        elif lowest_category == "social":
            recommendations.extend([
                "Launch community engagement programs",
                "Increase local hiring and training",
                "Implement fair labor certification"
            ])
        elif lowest_category == "governance":
            recommendations.extend([
                "Enhance transparency reporting",
                "Implement stakeholder feedback systems",
                "Obtain ethical sourcing certifications"
            ])
        
        return recommendations
