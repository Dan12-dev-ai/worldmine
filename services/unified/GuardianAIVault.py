"""
Guardian AI Personal Vault - DEDAN Mine Unified Architecture
Behavioral biometric monitor + automated freeze with unified state management
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone, timedelta
import json
import asyncio
from dataclasses import dataclass

from core import unified_state_manager, FeaturePriority, FeatureStatus, UnifiedUserSession

@dataclass
class BiometricData:
    """User biometric data for behavioral analysis"""
    login_patterns: List[datetime]
    transaction_patterns: List[Dict[str, Any]]
    device_fingerprints: List[str]
    location_patterns: List[Dict[str, float]]
    typing_rhythms: List[float]
    mouse_movements: List[Dict[str, float]]
    
class GuardianAIVault:
    """Guardian AI Personal Vault with unified state integration"""
    
    def __init__(self):
        self.biometric_thresholds = {
            "unusual_login_time": 0.7,
            "unusual_transaction_amount": 0.8,
            "unusual_location": 0.9,
            "unusual_device": 0.6,
            "typing_rhythm_deviation": 0.5
        }
        
        self.freeze_conditions = {
            "high_risk_score": 85,
            "multiple_anomalies": 3,
            "failed_attempts": 5,
            "suspicious_location": True
        }
    
    async def monitor_user_behavior(
        self,
        session_id: str,
        biometric_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Monitor user behavior and detect anomalies"""
        try:
            # Get unified session
            session = await unified_state_manager.get_session(session_id)
            if not session:
                return {"success": False, "error": "Session not found"}
            
            # Analyze biometric data
            anomaly_analysis = await self._analyze_biometric_patterns(session, biometric_data)
            
            # Calculate comprehensive risk score
            risk_score = await self._calculate_behavioral_risk(session, anomaly_analysis)
            
            # Check for freeze conditions
            should_freeze = await self._should_freeze_account(session, risk_score, anomaly_analysis)
            
            # Execute Guardian AI feature through unified state
            result = await unified_state_manager.execute_feature_request(
                feature_name="guardian_ai_personal_vault",
                user_id=session.user_id,
                session_id=session_id,
                request_data={
                    "biometric_analysis": anomaly_analysis,
                    "risk_score": risk_score,
                    "should_freeze": should_freeze,
                    "biometric_data": biometric_data
                }
            )
            
            if result["success"]:
                # Update session with behavioral patterns
                await self._update_behavioral_patterns(session, biometric_data, anomaly_analysis)
                
                return {
                    "success": True,
                    "risk_score": risk_score,
                    "anomalies_detected": anomaly_analysis["anomalies"],
                    "security_level": result["result"]["security_level"],
                    "account_frozen": result["result"]["is_frozen"],
                    "freeze_reason": result["result"]["freeze_reason"],
                    "recommendations": await self._generate_security_recommendations(risk_score, anomaly_analysis)
                }
            else:
                return result
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _analyze_biometric_patterns(
        self,
        session: UnifiedUserSession,
        biometric_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze biometric patterns for anomalies"""
        try:
            anomalies = []
            anomaly_scores = {}
            
            # Analyze login patterns
            if "login_time" in biometric_data:
                login_anomaly = await self._analyze_login_pattern(session, biometric_data["login_time"])
                if login_anomaly["is_anomaly"]:
                    anomalies.append(f"Unusual login time: {login_anomaly['description']}")
                    anomaly_scores["login_time"] = login_anomaly["score"]
            
            # Analyze transaction patterns
            if "transaction_amount" in biometric_data:
                transaction_anomaly = await self._analyze_transaction_pattern(session, biometric_data["transaction_amount"])
                if transaction_anomaly["is_anomaly"]:
                    anomalies.append(f"Unusual transaction amount: {transaction_anomaly['description']}")
                    anomaly_scores["transaction_amount"] = transaction_anomaly["score"]
            
            # Analyze location patterns
            if "location" in biometric_data:
                location_anomaly = await self._analyze_location_pattern(session, biometric_data["location"])
                if location_anomaly["is_anomaly"]:
                    anomalies.append(f"Unusual location: {location_anomaly['description']}")
                    anomaly_scores["location"] = location_anomaly["score"]
            
            # Analyze device patterns
            if "device_fingerprint" in biometric_data:
                device_anomaly = await self._analyze_device_pattern(session, biometric_data["device_fingerprint"])
                if device_anomaly["is_anomaly"]:
                    anomalies.append(f"Unusual device: {device_anomaly['description']}")
                    anomaly_scores["device"] = device_anomaly["score"]
            
            # Analyze typing patterns
            if "typing_rhythm" in biometric_data:
                typing_anomaly = await self._analyze_typing_pattern(session, biometric_data["typing_rhythm"])
                if typing_anomaly["is_anomaly"]:
                    anomalies.append(f"Unusual typing pattern: {typing_anomaly['description']}")
                    anomaly_scores["typing_rhythm"] = typing_anomaly["score"]
            
            return {
                "anomalies": anomalies,
                "anomaly_scores": anomaly_scores,
                "total_anomalies": len(anomalies),
                "highest_anomaly_score": max(anomaly_scores.values()) if anomaly_scores else 0.0,
                "analysis_timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {"anomalies": [], "error": str(e)}
    
    async def _analyze_login_pattern(self, session: UnifiedUserSession, login_time: datetime) -> Dict[str, Any]:
        """Analyze login time patterns"""
        try:
            current_hour = login_time.hour
            
            # Get historical login patterns from session
            historical_logins = session.behavior_patterns.get("login_times", [])
            
            if len(historical_logins) < 5:
                return {"is_anomaly": False, "score": 0.0, "description": "Insufficient historical data"}
            
            # Calculate typical login hours
            historical_hours = [log.hour for log in historical_logins[-20:]]  # Last 20 logins
            
            # Check if current hour is unusual
            hour_frequency = historical_hours.count(current_hour)
            total_logins = len(historical_hours)
            hour_probability = hour_frequency / total_logins
            
            # Calculate anomaly score
            if hour_probability == 0:
                anomaly_score = 1.0
                description = f"Never logged in at {current_hour}:00 before"
            elif hour_probability < 0.1:
                anomaly_score = 0.8
                description = f"Rarely logged in at {current_hour}:00 ({hour_probability:.1%} of logins)"
            elif hour_probability < 0.2:
                anomaly_score = 0.5
                description = f"Occasionally logged in at {current_hour}:00 ({hour_probability:.1%} of logins)"
            else:
                anomaly_score = 0.0
                description = f"Normal login time at {current_hour}:00"
            
            is_anomaly = anomaly_score > self.biometric_thresholds["unusual_login_time"]
            
            return {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "description": description,
                "historical_frequency": hour_probability
            }
            
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}
    
    async def _analyze_transaction_pattern(self, session: UnifiedUserSession, amount: float) -> Dict[str, Any]:
        """Analyze transaction amount patterns"""
        try:
            # Get historical transaction patterns
            historical_transactions = session.behavior_patterns.get("transaction_amounts", [])
            
            if len(historical_transactions) < 3:
                return {"is_anomaly": False, "score": 0.0, "description": "Insufficient transaction history"}
            
            # Calculate statistics
            avg_amount = sum(historical_transactions[-20:]) / min(len(historical_transactions), 20)
            max_amount = max(historical_transactions[-20:])
            
            # Check for unusual amounts
            if amount > max_amount * 3:
                anomaly_score = 1.0
                description = f"Transaction amount ${amount:,.2f} is 3x higher than previous maximum ${max_amount:,.2f}"
            elif amount > avg_amount * 2:
                anomaly_score = 0.8
                description = f"Transaction amount ${amount:,.2f} is 2x higher than average ${avg_amount:,.2f}"
            elif amount < avg_amount * 0.1 and amount > 0:
                anomaly_score = 0.6
                description = f"Transaction amount ${amount:,.2f} is much lower than average ${avg_amount:,.2f}"
            else:
                anomaly_score = 0.0
                description = f"Normal transaction amount ${amount:,.2f}"
            
            is_anomaly = anomaly_score > self.biometric_thresholds["unusual_transaction_amount"]
            
            return {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "description": description,
                "historical_average": avg_amount,
                "historical_maximum": max_amount
            }
            
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}
    
    async def _analyze_location_pattern(self, session: UnifiedUserSession, location: Dict[str, float]) -> Dict[str, Any]:
        """Analyze location patterns"""
        try:
            current_lat = location.get("latitude")
            current_lng = location.get("longitude")
            
            if not current_lat or not current_lng:
                return {"is_anomaly": False, "score": 0.0, "description": "Invalid location data"}
            
            # Get historical locations
            historical_locations = session.behavior_patterns.get("locations", [])
            
            if len(historical_locations) < 2:
                return {"is_anomaly": False, "score": 0.0, "description": "Insufficient location history"}
            
            # Calculate distance from most common locations
            min_distance = float('inf')
            for hist_loc in historical_locations[-10:]:  # Last 10 locations
                hist_lat = hist_loc.get("latitude")
                hist_lng = hist_loc.get("longitude")
                
                if hist_lat and hist_lng:
                    # Simple distance calculation (haversine would be more accurate)
                    distance = ((current_lat - hist_lat) ** 2 + (current_lng - hist_lng) ** 2) ** 0.5
                    min_distance = min(min_distance, distance)
            
            # Check for unusual location
            if min_distance > 10:  # More than 10 degrees difference
                anomaly_score = 0.9
                description = f"Location is {min_distance:.1f} degrees from usual locations"
            elif min_distance > 5:
                anomaly_score = 0.6
                description = f"Location is {min_distance:.1f} degrees from usual locations"
            else:
                anomaly_score = 0.0
                description = f"Normal location within {min_distance:.1f} degrees of usual areas"
            
            is_anomaly = anomaly_score > self.biometric_thresholds["unusual_location"]
            
            return {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "description": description,
                "minimum_distance": min_distance
            }
            
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}
    
    async def _analyze_device_pattern(self, session: UnifiedUserSession, device_fingerprint: str) -> Dict[str, Any]:
        """Analyze device fingerprint patterns"""
        try:
            # Get historical device fingerprints
            historical_devices = session.behavior_patterns.get("device_fingerprints", [])
            
            if len(historical_devices) < 1:
                return {"is_anomaly": False, "score": 0.0, "description": "First device login"}
            
            # Check if device is recognized
            device_recognized = device_fingerprint in historical_devices
            
            if device_recognized:
                anomaly_score = 0.0
                description = "Recognized device fingerprint"
            else:
                # Check how many different devices have been used
                unique_devices = len(set(historical_devices))
                
                if unique_devices == 1:
                    anomaly_score = 0.8
                    description = "First time using a new device"
                elif unique_devices <= 3:
                    anomaly_score = 0.4
                    description = f"New device (have used {unique_devices} devices before)"
                else:
                    anomaly_score = 0.2
                    description = f"New device (frequently switch between {unique_devices} devices)"
            
            is_anomaly = anomaly_score > self.biometric_thresholds["unusual_device"]
            
            return {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "description": description,
                "device_recognized": device_recognized,
                "historical_device_count": len(set(historical_devices))
            }
            
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}
    
    async def _analyze_typing_pattern(self, session: UnifiedUserSession, typing_rhythm: float) -> Dict[str, Any]:
        """Analyze typing rhythm patterns"""
        try:
            # Get historical typing rhythms
            historical_rhythms = session.behavior_patterns.get("typing_rhythms", [])
            
            if len(historical_rhythms) < 5:
                return {"is_anomaly": False, "score": 0.0, "description": "Insufficient typing pattern data"}
            
            # Calculate average and standard deviation
            avg_rhythm = sum(historical_rhythms[-20:]) / min(len(historical_rhythms), 20)
            
            # Calculate deviation
            deviation = abs(typing_rhythm - avg_rhythm) / avg_rhythm if avg_rhythm > 0 else 0
            
            # Check for unusual typing rhythm
            if deviation > 0.5:
                anomaly_score = 0.8
                description = f"Typing rhythm deviation of {deviation:.1%} from normal"
            elif deviation > 0.3:
                anomaly_score = 0.5
                description = f"Typing rhythm deviation of {deviation:.1%} from normal"
            else:
                anomaly_score = 0.0
                description = f"Normal typing rhythm (deviation: {deviation:.1%})"
            
            is_anomaly = anomaly_score > self.biometric_thresholds["typing_rhythm_deviation"]
            
            return {
                "is_anomaly": is_anomaly,
                "score": anomaly_score,
                "description": description,
                "deviation_percentage": deviation,
                "historical_average": avg_rhythm
            }
            
        except Exception as e:
            return {"is_anomaly": False, "score": 0.0, "error": str(e)}
    
    async def _calculate_behavioral_risk(
        self,
        session: UnifiedUserSession,
        anomaly_analysis: Dict[str, Any]
    ) -> float:
        """Calculate comprehensive behavioral risk score"""
        try:
            base_risk = 0.0
            
            # Add anomaly scores
            anomaly_scores = anomaly_analysis.get("anomaly_scores", {})
            for anomaly_type, score in anomaly_scores.items():
                base_risk += score * 20  # Each anomaly contributes up to 20 points
            
            # Add multiple anomaly penalty
            total_anomalies = anomaly_analysis.get("total_anomalies", 0)
            if total_anomalies >= 3:
                base_risk += 30  # Multiple anomalies penalty
            elif total_anomalies >= 2:
                base_risk += 15
            
            # Add historical risk factor
            historical_risk = session.risk_score
            base_risk += historical_risk * 0.3  # Weight historical risk
            
            # Cap at 100
            return min(base_risk, 100.0)
            
        except Exception as e:
            return 0.0
    
    async def _should_freeze_account(
        self,
        session: UnifiedUserSession,
        risk_score: float,
        anomaly_analysis: Dict[str, Any]
    ) -> bool:
        """Determine if account should be frozen"""
        try:
            # Check high risk score
            if risk_score >= self.freeze_conditions["high_risk_score"]:
                return True
            
            # Check multiple anomalies
            total_anomalies = anomaly_analysis.get("total_anomalies", 0)
            if total_anomalies >= self.freeze_conditions["multiple_anomalies"]:
                return True
            
            # Check suspicious location
            anomaly_scores = anomaly_analysis.get("anomaly_scores", {})
            location_score = anomaly_scores.get("location", 0.0)
            if location_score >= 0.9:
                return True
            
            return False
            
        except Exception as e:
            return False
    
    async def _update_behavioral_patterns(
        self,
        session: UnifiedUserSession,
        biometric_data: Dict[str, Any],
        anomaly_analysis: Dict[str, Any]
    ):
        """Update behavioral patterns in session"""
        try:
            # Update login patterns
            if "login_time" in biometric_data:
                login_times = session.behavior_patterns.get("login_times", [])
                login_times.append(biometric_data["login_time"])
                session.behavior_patterns["login_times"] = login_times[-50:]  # Keep last 50
            
            # Update transaction patterns
            if "transaction_amount" in biometric_data:
                transaction_amounts = session.behavior_patterns.get("transaction_amounts", [])
                transaction_amounts.append(biometric_data["transaction_amount"])
                session.behavior_patterns["transaction_amounts"] = transaction_amounts[-50:]  # Keep last 50
            
            # Update location patterns
            if "location" in biometric_data:
                locations = session.behavior_patterns.get("locations", [])
                locations.append(biometric_data["location"])
                session.behavior_patterns["locations"] = locations[-20:]  # Keep last 20
            
            # Update device patterns
            if "device_fingerprint" in biometric_data:
                device_fingerprints = session.behavior_patterns.get("device_fingerprints", [])
                device_fingerprints.append(biometric_data["device_fingerprint"])
                session.behavior_patterns["device_fingerprints"] = list(set(device_fingerprints))[-10:]  # Keep last 10 unique
            
            # Update typing patterns
            if "typing_rhythm" in biometric_data:
                typing_rhythms = session.behavior_patterns.get("typing_rhythms", [])
                typing_rhythms.append(biometric_data["typing_rhythm"])
                session.behavior_patterns["typing_rhythms"] = typing_rhythms[-30:]  # Keep last 30
            
        except Exception as e:
            print(f"Error updating behavioral patterns: {e}")
    
    async def _generate_security_recommendations(
        self,
        risk_score: float,
        anomaly_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate security recommendations based on risk analysis"""
        recommendations = []
        
        if risk_score >= 80:
            recommendations.append("🚨 IMMEDIATE ACTION REQUIRED: Account temporarily frozen for security")
            recommendations.append("Contact support immediately for manual verification")
        elif risk_score >= 60:
            recommendations.append("⚠️ ENHANCED MONITORING: Enable two-factor authentication")
            recommendations.append("Verify recent activities and update security settings")
        elif risk_score >= 40:
            recommendations.append("🔍 REVIEW: Check recent login locations and devices")
            recommendations.append("Consider updating password and security questions")
        
        # Specific anomaly recommendations
        anomalies = anomaly_analysis.get("anomalies", [])
        for anomaly in anomalies:
            if "login time" in anomaly.lower():
                recommendations.append("Login time anomaly detected - verify if this was you")
            elif "transaction amount" in anomaly.lower():
                recommendations.append("Unusual transaction amount - confirm transaction details")
            elif "location" in anomaly.lower():
                recommendations.append("Unusual location - verify account security")
            elif "device" in anomaly.lower():
                recommendations.append("New device detected - ensure device security")
        
        if not recommendations:
            recommendations.append("✅ No security concerns detected")
        
        return recommendations

# Singleton instance
guardian_ai_vault = GuardianAIVault()
