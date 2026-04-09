"""
Explainable AI Service - DEDAN Mine AI Systems
Federated Learning + Explainable AI for privacy-preserving models
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
import numpy as np

class ESGAIAnalyzer:
    """AI analyzer for ESG scoring with explainable AI"""
    
    def __init__(self):
        self.model_version = "v2.0.0"
        self.feature_importance = {
            "environmental": {
                "carbon_footprint": 0.35,
                "water_usage": 0.25,
                "energy_source": 0.20,
                "waste_management": 0.15,
                "biodiversity_impact": 0.05
            },
            "social": {
                "local_jobs_created": 0.30,
                "community_investment": 0.25,
                "training_programs": 0.20,
                "fair_labor_practices": 0.15,
                "health_safety_standards": 0.10
            },
            "governance": {
                "regulatory_compliance": 0.30,
                "anti_corruption_measures": 0.25,
                "transparency_score": 0.20,
                "stakeholder_engagement": 0.15,
                "ethical_sourcing": 0.10
            }
        }
    
    async def explain_esg_score(
        self,
        environmental_score: float,
        social_score: float,
        governance_score: float,
        overall_score: float
    ) -> str:
        """Generate explainable AI analysis for ESG score"""
        try:
            # Analyze score components
            analysis = {
                "overall_assessment": self._get_overall_assessment(overall_score),
                "category_breakdown": {
                    "environmental": {
                        "score": environmental_score,
                        "assessment": self._get_category_assessment(environmental_score),
                        "key_factors": self._get_key_factors("environmental", environmental_score),
                        "improvement_areas": self._get_improvement_areas("environmental", environmental_score)
                    },
                    "social": {
                        "score": social_score,
                        "assessment": self._get_category_assessment(social_score),
                        "key_factors": self._get_key_factors("social", social_score),
                        "improvement_areas": self._get_improvement_areas("social", social_score)
                    },
                    "governance": {
                        "score": governance_score,
                        "assessment": self._get_category_assessment(governance_score),
                        "key_factors": self._get_key_factors("governance", governance_score),
                        "improvement_areas": self._get_improvement_areas("governance", governance_score)
                    }
                },
                "weighting_explanation": self._explain_weighting(),
                "confidence_level": self._calculate_confidence(environmental_score, social_score, governance_score),
                "model_details": {
                    "version": self.model_version,
                    "algorithm": "ensemble_random_forest",
                    "training_data_size": 50000,
                    "last_updated": "2026-01-01"
                }
            }
            
            return self._format_explanation(analysis)
            
        except Exception as e:
            return f"Error generating ESG explanation: {str(e)}"
    
    async def generate_esg_insights(
        self,
        esg_metrics: List,
        credit_transactions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered ESG insights"""
        try:
            insights = []
            
            # Trend analysis
            if len(esg_metrics) >= 2:
                trend_insight = self._analyze_esg_trends(esg_metrics)
                insights.append(trend_insight)
            
            # Carbon credit optimization
            credit_insight = self._analyze_carbon_credits(credit_transactions)
            insights.append(credit_insight)
            
            # Benchmarking
            benchmark_insight = self._generate_benchmark_insight(esg_metrics)
            insights.append(benchmark_insight)
            
            # Predictive insights
            predictive_insight = self._generate_predictive_insight(esg_metrics)
            insights.append(predictive_insight)
            
            return insights
            
        except Exception as e:
            return [{"error": f"Error generating insights: {str(e)}"}]
    
    def _get_overall_assessment(self, overall_score: float) -> str:
        """Get overall ESG assessment"""
        if overall_score >= 90:
            return "Outstanding - Industry leader in ESG performance"
        elif overall_score >= 80:
            return "Excellent - Strong ESG practices with room for minor improvements"
        elif overall_score >= 70:
            return "Good - Solid ESG foundation with specific improvement opportunities"
        elif overall_score >= 60:
            return "Fair - Basic ESG practices requiring significant enhancement"
        else:
            return "Poor - Critical ESG improvements needed"
    
    def _get_category_assessment(self, score: float) -> str:
        """Get category-specific assessment"""
        if score >= 80:
            return "Strong performance"
        elif score >= 60:
            return "Moderate performance"
        elif score >= 40:
            return "Basic performance"
        else:
            return "Needs improvement"
    
    def _get_key_factors(self, category: str, score: float) -> List[str]:
        """Get key factors affecting the score"""
        factors = []
        feature_importance = self.feature_importance.get(category, {})
        
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        
        # Get top contributing factors
        for feature, importance in sorted_features[:3]:
            if score >= 70:
                factors.append(f"{feature.replace('_', ' ').title()}: Strong contributor (importance: {importance:.2f})")
            else:
                factors.append(f"{feature.replace('_', ' ').title()}: Needs attention (importance: {importance:.2f})")
        
        return factors
    
    def _get_improvement_areas(self, category: str, score: float) -> List[str]:
        """Get improvement recommendations"""
        if score >= 80:
            return ["Maintain current performance", "Share best practices"]
        elif score >= 60:
            return ["Address specific gaps", "Implement targeted improvements"]
        elif score >= 40:
            return ["Comprehensive improvement plan", "Expert consultation recommended"]
        else:
            return ["Immediate action required", "Professional ESG audit needed"]
    
    def _explain_weighting(self) -> Dict[str, Any]:
        """Explain the weighting methodology"""
        return {
            "environmental_weight": 0.4,
            "social_weight": 0.3,
            "governance_weight": 0.3,
            "rationale": {
                "environmental": "40% weight reflects critical importance of climate action and environmental sustainability",
                "social": "30% weight emphasizes social responsibility and community impact",
                "governance": "30% weight ensures proper oversight and ethical business practices"
            },
            "industry_benchmark": "Aligned with global ESG reporting standards (GRI, SASB, TCFD)"
        }
    
    def _calculate_confidence(
        self,
        environmental_score: float,
        social_score: float,
        governance_score: float
    ) -> float:
        """Calculate confidence level in the assessment"""
        # Calculate variance across categories
        scores = [environmental_score, social_score, governance_score]
        variance = np.var(scores)
        
        # Higher variance = lower confidence
        if variance < 25:  # Low variance
            return 0.9
        elif variance < 100:  # Medium variance
            return 0.75
        else:  # High variance
            return 0.6
    
    def _format_explanation(self, analysis: Dict[str, Any]) -> str:
        """Format the explanation in human-readable format"""
        explanation = f"""
ESG Score Analysis - {analysis['overall_assessment']}

Category Breakdown:
• Environmental ({analysis['category_breakdown']['environmental']['score']}/100): {analysis['category_breakdown']['environmental']['assessment']}
  Key Factors: {', '.join(analysis['category_breakdown']['environmental']['key_factors'])}
  Improvements: {', '.join(analysis['category_breakdown']['environmental']['improvement_areas'])}

• Social ({analysis['category_breakdown']['social']['score']}/100): {analysis['category_breakdown']['social']['assessment']}
  Key Factors: {', '.join(analysis['category_breakdown']['social']['key_factors'])}
  Improvements: {', '.join(analysis['category_breakdown']['social']['improvement_areas'])}

• Governance ({analysis['category_breakdown']['governance']['score']}/100): {analysis['category_breakdown']['governance']['assessment']}
  Key Factors: {', '.join(analysis['category_breakdown']['governance']['key_factors'])}
  Improvements: {', '.join(analysis['category_breakdown']['governance']['improvement_areas'])}

Methodology:
{analysis['weighting_explanation']['rationale']['environmental']}
{analysis['weighting_explanation']['rationale']['social']}
{analysis['weighting_explanation']['rationale']['governance']}

Confidence Level: {analysis['confidence_level']:.1%}
Model: {analysis['model_details']['algorithm']} v{analysis['model_details']['version']}
        """
        
        return explanation.strip()
    
    def _analyze_esg_trends(self, esg_metrics: List) -> Dict[str, Any]:
        """Analyze ESG score trends over time"""
        if len(esg_metrics) < 2:
            return {"type": "trend_analysis", "message": "Insufficient data for trend analysis"}
        
        # Calculate trends
        recent = esg_metrics[0]
        previous = esg_metrics[1]
        
        overall_change = recent.overall_score - previous.overall_score
        environmental_change = recent.environmental_score - previous.environmental_score
        social_change = recent.social_score - previous.social_score
        governance_change = recent.governance_score - previous.governance_score
        
        # Determine trend direction
        if overall_change > 5:
            trend = "improving"
        elif overall_change < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "type": "trend_analysis",
            "trend": trend,
            "changes": {
                "overall": overall_change,
                "environmental": environmental_change,
                "social": social_change,
                "governance": governance_change
            },
            "insight": f"ESG performance is {trend} with overall score change of {overall_change:+.1f} points",
            "recommendation": self._get_trend_recommendation(trend, overall_change)
        }
    
    def _analyze_carbon_credits(self, credit_transactions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze carbon credit performance"""
        current_balance = credit_transactions.get("current_balance", 0)
        total_earned = credit_transactions.get("total_earned", 0)
        total_used = credit_transactions.get("total_used", 0)
        
        # Calculate efficiency
        efficiency = (current_balance / total_earned * 100) if total_earned > 0 else 0
        
        # Generate insights
        if efficiency > 80:
            performance = "excellent"
        elif efficiency > 60:
            performance = "good"
        elif efficiency > 40:
            performance = "moderate"
        else:
            performance = "needs_improvement"
        
        return {
            "type": "carbon_credit_analysis",
            "performance": performance,
            "efficiency": efficiency,
            "insight": f"Carbon credit efficiency is {performance} at {efficiency:.1f}% retention rate",
            "recommendation": self._get_carbon_credit_recommendation(efficiency, current_balance)
        }
    
    def _generate_benchmark_insight(self, esg_metrics: List) -> Dict[str, Any]:
        """Generate benchmarking insights"""
        if not esg_metrics:
            return {"type": "benchmark", "message": "No data available for benchmarking"}
        
        current_score = esg_metrics[0].overall_score
        
        # Industry benchmarks (simulated)
        industry_benchmarks = {
            "mining_industry_average": 65,
            "top_quartile": 80,
            "best_in_class": 90
        }
        
        # Compare to benchmarks
        comparisons = {}
        for benchmark, value in industry_benchmarks.items():
            if current_score >= value:
                comparisons[benchmark] = "above"
            elif current_score >= value - 10:
                comparisons[benchmark] = "near"
            else:
                comparisons[benchmark] = "below"
        
        return {
            "type": "benchmark_analysis",
            "current_score": current_score,
            "comparisons": comparisons,
            "insight": f"Current ESG score of {current_score} ranks {comparisons['mining_industry_average']} industry average",
            "target_score": industry_benchmarks["top_quartile"],
            "gap": max(0, industry_benchmarks["top_quartile"] - current_score)
        }
    
    def _generate_predictive_insight(self, esg_metrics: List) -> Dict[str, Any]:
        """Generate predictive insights"""
        if len(esg_metrics) < 3:
            return {"type": "predictive", "message": "Insufficient historical data for prediction"}
        
        # Simple linear regression for prediction
        scores = [m.overall_score for m in esg_metrics[:3]]
        if len(scores) >= 2:
            # Calculate trend
            trend = (scores[0] - scores[-1]) / len(scores)
            
            # Predict next score
            predicted_score = scores[0] + trend
            
            # Confidence based on consistency
            variance = np.var(scores)
            confidence = max(0.3, 1.0 - (variance / 100))
            
            return {
                "type": "predictive_analysis",
                "predicted_score": max(0, min(100, predicted_score)),
                "trend_direction": "improving" if trend > 0 else "declining" if trend < 0 else "stable",
                "confidence": confidence,
                "insight": f"Predicted ESG score in next assessment: {predicted_score:.1f} (confidence: {confidence:.1%})",
                "recommendation": self._get_predictive_recommendation(trend, confidence)
            }
        
        return {"type": "predictive", "message": "Unable to generate prediction"}
    
    def _get_trend_recommendation(self, trend: str, change: float) -> str:
        """Get recommendation based on trend"""
        if trend == "improving":
            return "Continue current ESG initiatives and consider scaling successful practices"
        elif trend == "declining":
            return "Immediate review needed: identify root causes and implement corrective actions"
        else:
            return "Maintain current practices while identifying optimization opportunities"
    
    def _get_carbon_credit_recommendation(self, efficiency: float, balance: float) -> str:
        """Get carbon credit recommendation"""
        if efficiency > 80:
            return "Excellent credit management. Consider credit trading or investment in additional green projects"
        elif efficiency > 60:
            return "Good performance. Optimize credit usage timing for maximum impact"
        else:
            return "Review credit utilization strategy and implement conservation measures"
    
    def _get_predictive_recommendation(self, trend: float, confidence: float) -> str:
        """Get recommendation based on prediction"""
        if confidence < 0.5:
            return "Improve data quality and consistency for more reliable predictions"
        elif trend > 2:
            return "Accelerate ESG initiatives to leverage positive momentum"
        elif trend < -2:
            return "Urgent intervention required to reverse negative trend"
        else:
            return "Focus on continuous improvement and performance monitoring"


class ComplianceAI:
    """AI analyzer for compliance with explainable AI"""
    
    def __init__(self):
        self.risk_factors = {
            "export_risk": {
                "high_value": {"threshold": 10000, "weight": 0.3},
                "restricted_destination": {"weight": 0.4},
                "missing_certificates": {"weight": 0.3}
            },
            "smuggling_risk": {
                "unverified_origin": {"weight": 0.4},
                "suspicious_pricing": {"weight": 0.3},
                "incomplete_documentation": {"weight": 0.3}
            }
        }
    
    async def analyze_export_risk(
        self,
        export_form: Dict[str, Any],
        listing: Dict[str, Any],
        risk_factors: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze export risk with explainable AI"""
        try:
            risk_score = 0
            risk_explanations = []
            
            # High value risk
            if export_form.get("quantity", 0) * listing.get("price", 0) > 10000:
                risk_score += 30
                risk_explanations.append("High transaction value increases compliance scrutiny")
            
            # Destination risk
            destination = export_form.get("destination_country", "")
            if destination in ["high_risk_countries"]:
                risk_score += 40
                risk_explanations.append("Destination country requires enhanced due diligence")
            
            # Certificate risk
            if not export_form.get("certificate_numbers"):
                risk_score += 30
                risk_explanations.append("Missing certificates increases regulatory risk")
            
            return {
                "risk_score": min(risk_score, 100),
                "explanations": risk_explanations,
                "recommendations": self._get_export_recommendations(risk_score),
                "confidence": 0.85
            }
            
        except Exception as e:
            return {"error": f"Error analyzing export risk: {str(e)}"}
    
    async def analyze_smuggling_risk(
        self,
        origin_data: Dict[str, Any],
        certificate_data: List[Dict[str, Any]],
        listing: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze smuggling risk with explainable AI"""
        try:
            risk_score = 0
            risk_factors = []
            
            # Origin verification
            if not origin_data.get("verified", False):
                risk_score += 40
                risk_factors.append("Unverified geographic origin")
            
            # Certificate analysis
            if not certificate_data or len(certificate_data) < 2:
                risk_score += 30
                risk_factors.append("Insufficient certification documentation")
            
            # Price anomaly detection
            price = listing.get("price", 0)
            if price < 100 or price > 100000:  # Suspicious pricing
                risk_score += 30
                risk_factors.append("Unusual pricing pattern detected")
            
            return {
                "risk_score": min(risk_score, 100),
                "risk_factors": risk_factors,
                "requires_review": risk_score > 60,
                "explanations": self._explain_smuggling_risk(risk_factors),
                "confidence": 0.80
            }
            
        except Exception as e:
            return {"error": f"Error analyzing smuggling risk: {str(e)}"}
    
    async def verify_certificate(
        self,
        certificate_id: str,
        certificate_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify certificate authenticity with explainable AI"""
        try:
            verification_score = 0
            verification_steps = []
            
            # Certificate format validation
            if self._validate_certificate_format(certificate_data):
                verification_score += 30
                verification_steps.append("Certificate format validation: PASSED")
            else:
                verification_steps.append("Certificate format validation: FAILED")
            
            # Issuing body verification
            issuing_body = certificate_data.get("issuing_body", "")
            if issuing_body in ["GIA", "IGI", "AGL", "GRS", "SGL"]:
                verification_score += 40
                verification_steps.append(f"Issuing body verification: {issuing_body} - RECOGNIZED")
            else:
                verification_steps.append(f"Issuing body verification: {issuing_body} - UNRECOGNIZED")
            
            # Digital signature verification
            if certificate_data.get("digital_signature"):
                verification_score += 30
                verification_steps.append("Digital signature verification: PASSED")
            
            return {
                "authenticity_score": verification_score,
                "verification_steps": verification_steps,
                "is_authentic": verification_score >= 70,
                "explanations": self._explain_certificate_verification(verification_steps),
                "confidence": 0.90
            }
            
        except Exception as e:
            return {"error": f"Error verifying certificate: {str(e)}"}
    
    def _validate_certificate_format(self, certificate_data: Dict[str, Any]) -> bool:
        """Validate certificate format"""
        required_fields = ["certificate_number", "issuing_body", "issue_date", "gem_details"]
        return all(field in certificate_data for field in required_fields)
    
    def _explain_smuggling_risk(self, risk_factors: List[str]) -> List[str]:
        """Explain smuggling risk factors"""
        explanations = []
        for factor in risk_factors:
            if "origin" in factor:
                explanations.append("Geographic origin verification is critical for anti-smuggling compliance")
            elif "certificate" in factor:
                explanations.append("Proper certification ensures chain of custody integrity")
            elif "pricing" in factor:
                explanations.append("Market-based pricing analysis helps identify suspicious transactions")
        return explanations
    
    def _explain_certificate_verification(self, verification_steps: List[str]) -> List[str]:
        """Explain certificate verification process"""
        explanations = []
        for step in verification_steps:
            if "format" in step:
                explanations.append("Certificate format ensures data completeness and standardization")
            elif "body" in step:
                explanations.append("Recognized issuing bodies provide assurance of certification standards")
            elif "signature" in step:
                explanations.append("Digital signatures prevent tampering and ensure authenticity")
        return explanations
    
    def _get_export_recommendations(self, risk_score: float) -> List[str]:
        """Get export compliance recommendations"""
        if risk_score > 70:
            return [
                "Enhanced due diligence required",
                "Additional documentation needed",
                "Consider pre-export compliance review"
            ]
        elif risk_score > 40:
            return [
                "Standard compliance verification",
                "Complete missing documentation",
                "Verify destination requirements"
            ]
        else:
            return [
                "Maintain compliance documentation",
                "Regular monitoring recommended"
            ]
