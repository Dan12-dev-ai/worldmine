"""
Guardian AI Security Layer - DEDAN Mine
Monitors user activity and flags anomalous behavior using LangGraph
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import json
import asyncio
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI

from database import get_db
from models import User, GuardianPattern

@dataclass
class GuardianState:
    """State for Guardian AI Agent"""
    user_id: str
    activity_data: Dict[str, Any]
    behavior_patterns: Dict[str, Any]
    risk_score: float
    alerts: List[str]
    recommendations: List[str]

class GuardianAgent:
    """AI-powered security monitoring agent using LangGraph"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            max_tokens=1000
        )
        self.graph = self._create_guardian_graph()
        
    def _create_guardian_graph(self) -> StateGraph:
        """Create LangGraph for Guardian AI analysis"""
        workflow = StateGraph(GuardianState)
        
        # Add nodes
        workflow.add_node("analyze_activity", self._analyze_activity)
        workflow.add_node("compare_patterns", self._compare_patterns)
        workflow.add_node("calculate_risk", self._calculate_risk)
        workflow.add_node("generate_alerts", self._generate_alerts)
        workflow.add_node("recommend_actions", self._recommend_actions)
        
        # Add edges
        workflow.set_entry_point("analyze_activity")
        workflow.add_edge("analyze_activity", "compare_patterns")
        workflow.add_edge("compare_patterns", "calculate_risk")
        workflow.add_edge("calculate_risk", "generate_alerts")
        workflow.add_edge("generate_alerts", "recommend_actions")
        workflow.add_edge("recommend_actions", END)
        
        return workflow.compile()
    
    async def monitor_user_activity(
        self,
        user_id: str,
        activity_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor user activity and detect anomalies"""
        try:
            # Get stored behavior patterns
            behavior_patterns = await self._get_behavior_patterns(user_id)
            
            # Create initial state
            initial_state = GuardianState(
                user_id=user_id,
                activity_data=activity_data,
                behavior_patterns=behavior_patterns,
                risk_score=0.0,
                alerts=[],
                recommendations=[]
            )
            
            # Run Guardian analysis
            result = await self.graph.ainvoke(initial_state)
            
            # Store updated patterns if needed
            await self._update_behavior_patterns(user_id, activity_data, result)
            
            return {
                "success": True,
                "user_id": user_id,
                "risk_score": result["risk_score"],
                "alerts": result["alerts"],
                "recommendations": result["recommendations"],
                "monitoring_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _get_behavior_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get stored behavior patterns for user"""
        try:
            db = next(get_db())
            
            # Get latest guardian pattern
            pattern = db.query(GuardianPattern).filter(
                GuardianPattern.user_id == user_id
            ).order_by(GuardianPattern.updated_at.desc()).first()
            
            if pattern:
                return json.loads(pattern.behavior_patterns or "{}")
            else:
                # Return default patterns for new users
                return {
                    "login_times": [],
                    "typical_trade_sizes": [],
                    "preferred_categories": [],
                    "activity_frequency": {},
                    "risk_history": []
                }
                
        except Exception as e:
            print(f"Error getting behavior patterns: {e}")
            return {}
    
    async def _analyze_activity(self, state: GuardianState) -> GuardianState:
        """Analyze current activity using AI"""
        try:
            activity_type = state.activity_data.get("activity_type", "unknown")
            
            # Create analysis prompt
            prompt = f"""
            Analyze this user activity for security risks:
            
            User ID: {state.user_id}
            Activity Type: {activity_type}
            Activity Data: {json.dumps(state.activity_data, indent=2)}
            Historical Patterns: {json.dumps(state.behavior_patterns, indent=2)}
            
            Focus on:
            1. Unusual transaction amounts
            2. Strange login times/locations
            3. Atypical behavior patterns
            4. Potential security risks
            
            Provide analysis as JSON with keys: risk_indicators, severity_level, anomalies_detected
            """
            
            # Get AI analysis
            response = await self.llm.ainvoke([
                HumanMessage(content=prompt)
            ])
            
            # Parse AI response
            try:
                ai_analysis = json.loads(response.content)
                state.activity_data["ai_analysis"] = ai_analysis
            except:
                state.activity_data["ai_analysis"] = {"risk_indicators": [], "severity_level": "low"}
            
            return state
            
        except Exception as e:
            print(f"Error in activity analysis: {e}")
            state.activity_data["ai_analysis"] = {"risk_indicators": [], "severity_level": "low"}
            return state
    
    async def _compare_patterns(self, state: GuardianState) -> GuardianState:
        """Compare current activity with historical patterns"""
        try:
            activity_type = state.activity_data.get("activity_type")
            current_patterns = state.behavior_patterns
            
            # Pattern comparison logic
            anomalies = []
            
            if activity_type == "login":
                anomalies = self._check_login_patterns(
                    state.activity_data, current_patterns
                )
            elif activity_type == "transaction":
                anomalies = self._check_transaction_patterns(
                    state.activity_data, current_patterns
                )
            elif activity_type == "listing":
                anomalies = self._check_listing_patterns(
                    state.activity_data, current_patterns
                )
            
            state.activity_data["pattern_anomalies"] = anomalies
            return state
            
        except Exception as e:
            print(f"Error in pattern comparison: {e}")
            state.activity_data["pattern_anomalies"] = []
            return state
    
    async def _calculate_risk(self, state: GuardianState) -> GuardianState:
        """Calculate overall risk score"""
        try:
            risk_score = 0.0
            
            # AI analysis risk
            ai_analysis = state.activity_data.get("ai_analysis", {})
            severity = ai_analysis.get("severity_level", "low")
            if severity == "high":
                risk_score += 40
            elif severity == "medium":
                risk_score += 25
            elif severity == "low":
                risk_score += 10
            
            # Pattern anomaly risk
            anomalies = state.activity_data.get("pattern_anomalies", [])
            risk_score += len(anomalies) * 15
            
            # Historical risk
            risk_history = state.behavior_patterns.get("risk_history", [])
            if risk_history:
                avg_risk = sum(risk_history[-5:]) / min(len(risk_history), 5)
                if avg_risk > 30:
                    risk_score += 20
            
            # Cap at 100
            state.risk_score = min(risk_score, 100.0)
            return state
            
        except Exception as e:
            print(f"Error calculating risk: {e}")
            state.risk_score = 0.0
            return state
    
    async def _generate_alerts(self, state: GuardianState) -> GuardianState:
        """Generate security alerts based on risk score"""
        try:
            alerts = []
            risk_score = state.risk_score
            
            if risk_score >= 80:
                alerts.append("🚨 HIGH RISK: Immediate security review required")
            elif risk_score >= 60:
                alerts.append("⚠️ MEDIUM RISK: Unusual activity detected")
            elif risk_score >= 40:
                alerts.append("🔍 LOW RISK: Monitor user activity")
            
            # Specific anomaly alerts
            anomalies = state.activity_data.get("pattern_anomalies", [])
            for anomaly in anomalies:
                alerts.append(f"🔔 Anomaly: {anomaly}")
            
            # AI analysis alerts
            ai_analysis = state.activity_data.get("ai_analysis", {})
            risk_indicators = ai_analysis.get("risk_indicators", [])
            for indicator in risk_indicators:
                alerts.append(f"🤖 AI Alert: {indicator}")
            
            state.alerts = alerts
            return state
            
        except Exception as e:
            print(f"Error generating alerts: {e}")
            state.alerts = ["Error generating alerts"]
            return state
    
    async def _recommend_actions(self, state: GuardianState) -> GuardianState:
        """Recommend security actions"""
        try:
            recommendations = []
            risk_score = state.risk_score
            activity_type = state.activity_data.get("activity_type")
            
            if risk_score >= 80:
                recommendations.extend([
                    "Require additional authentication",
                    "Temporarily restrict high-value transactions",
                    "Manual review by security team"
                ])
            elif risk_score >= 60:
                recommendations.extend([
                    "Enhanced monitoring for next 24 hours",
                    "Verify user identity via additional factors",
                    "Consider temporary transaction limits"
                ])
            elif risk_score >= 40:
                recommendations.extend([
                    "Continue monitoring",
                    "Update user behavior patterns"
                ])
            
            # Activity-specific recommendations
            if activity_type == "transaction" and risk_score >= 50:
                recommendations.append("Implement transaction delay for verification")
            
            if activity_type == "login" and risk_score >= 60:
                recommendations.append("Send security notification to user")
            
            state.recommendations = recommendations
            return state
            
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            state.recommendations = ["Error generating recommendations"]
            return state
    
    def _check_login_patterns(
        self,
        activity_data: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Check login patterns for anomalies"""
        anomalies = []
        
        current_time = datetime.now(timezone.utc)
        login_hour = current_time.hour
        
        # Check login time patterns
        login_times = patterns.get("login_times", [])
        if login_times:
            typical_hours = [t.hour for t in login_times[-10:]]  # Last 10 logins
            if typical_hours and login_hour not in typical_hours:
                anomalies.append(f"Unusual login time: {login_hour}:00")
        
        # Check location patterns
        current_location = activity_data.get("location", {})
        if current_location:
            # Location anomaly detection logic would go here
            pass
        
        return anomalies
    
    def _check_transaction_patterns(
        self,
        activity_data: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Check transaction patterns for anomalies"""
        anomalies = []
        
        transaction_amount = activity_data.get("amount", 0)
        typical_sizes = patterns.get("typical_trade_sizes", [])
        
        if typical_sizes and transaction_amount > 0:
            avg_size = sum(typical_sizes[-10:]) / min(len(typical_sizes), 10)
            
            # Flag unusually large transactions
            if transaction_amount > avg_size * 3:
                anomalies.append(f"Unusually large transaction: ${transaction_amount:,.2f}")
            
            # Flag unusually small transactions
            if transaction_amount < avg_size * 0.1 and transaction_amount > 0:
                anomalies.append(f"Unusually small transaction: ${transaction_amount:,.2f}")
        
        return anomalies
    
    def _check_listing_patterns(
        self,
        activity_data: Dict[str, Any],
        patterns: Dict[str, Any]
    ) -> List[str]:
        """Check listing patterns for anomalies"""
        anomalies = []
        
        category = activity_data.get("category", "")
        preferred_categories = patterns.get("preferred_categories", [])
        
        # Check if user is listing in unusual category
        if preferred_categories and category not in preferred_categories:
            anomalies.append(f"New category listing: {category}")
        
        return anomalies
    
    async def _update_behavior_patterns(
        self,
        user_id: str,
        activity_data: Dict[str, Any],
        analysis_result: GuardianState
    ) -> None:
        """Update stored behavior patterns"""
        try:
            db = next(get_db())
            
            # Get current patterns
            current_patterns = await self._get_behavior_patterns(user_id)
            
            # Update patterns based on activity
            activity_type = activity_data.get("activity_type")
            
            if activity_type == "login":
                login_times = current_patterns.get("login_times", [])
                login_times.append(datetime.now(timezone.utc))
                current_patterns["login_times"] = login_times[-50:]  # Keep last 50
                
            elif activity_type == "transaction":
                trade_sizes = current_patterns.get("typical_trade_sizes", [])
                amount = activity_data.get("amount", 0)
                if amount > 0:
                    trade_sizes.append(amount)
                    current_patterns["typical_trade_sizes"] = trade_sizes[-50:]  # Keep last 50
                
            elif activity_type == "listing":
                categories = current_patterns.get("preferred_categories", [])
                category = activity_data.get("category", "")
                if category and category not in categories:
                    categories.append(category)
                    current_patterns["preferred_categories"] = categories[-20:]  # Keep last 20
            
            # Update risk history
            risk_history = current_patterns.get("risk_history", [])
            risk_history.append(analysis_result["risk_score"])
            current_patterns["risk_history"] = risk_history[-100:]  # Keep last 100
            
            # Save to database
            guardian_pattern = db.query(GuardianPattern).filter(
                GuardianPattern.user_id == user_id
            ).first()
            
            if guardian_pattern:
                guardian_pattern.behavior_patterns = json.dumps(current_patterns)
                guardian_pattern.updated_at = datetime.now(timezone.utc)
            else:
                guardian_pattern = GuardianPattern(
                    user_id=user_id,
                    behavior_patterns=json.dumps(current_patterns),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc)
                )
                db.add(guardian_pattern)
            
            db.commit()
            
        except Exception as e:
            print(f"Error updating behavior patterns: {e}")

# Singleton instance
guardian_agent = GuardianAgent()
