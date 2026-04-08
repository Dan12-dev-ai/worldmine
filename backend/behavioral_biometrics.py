"""
DEDAN Mine - Behavioral Biometrics Security (v4.5.0)
Invisible Security with Haptic Feedback + Animations
Liveness Detection for high-value transactions
Strategic Friction for $10,000+ transactions
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import base64
import numpy as np
from collections import defaultdict, deque
import time
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiometricType(Enum):
    """Biometric verification types"""
    FINGERPRINT = "fingerprint"
    FACE_ID = "face_id"
    VOICE = "voice"
    IRIS_SCAN = "iris_scan"
    BEHAVIORAL = "behavioral"

class SecurityLevel(Enum):
    """Security levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class BiometricStatus(Enum):
    """Biometric status"""
    NOT_VERIFIED = "not_verified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"
    LOCKED = "locked"

@dataclass
class BiometricProfile:
    """User biometric profile"""
    user_id: str
    biometric_type: BiometricType
    baseline_patterns: Dict[str, Any]
    risk_threshold: float
    verification_count: int
    last_verified: Optional[datetime]
    failure_count: int
    lock_until: Optional[datetime]
    created_at: datetime
    updated_at: datetime

@dataclass
class BiometricSession:
    """Biometric verification session"""
    session_id: str
    user_id: str
    biometric_type: BiometricType
    security_level: SecurityLevel
    challenge_data: Dict[str, Any]
    response_data: Optional[Dict[str, Any]]
    status: BiometricStatus
    confidence_score: float
    risk_score: float
    created_at: datetime
    expires_at: datetime
    haptic_feedback: bool
    animation_type: str

@dataclass
class BehavioralMetrics:
    """Behavioral metrics for analysis"""
    user_id: str
    session_id: str
    mouse_patterns: List[Dict[str, Any]]
    touch_patterns: List[Dict[str, Any]]
    typing_patterns: List[Dict[str, Any]]
    device_orientation: List[Dict[str, Any]]
    pressure_patterns: List[Dict[str, Any]]
    timing_patterns: List[Dict[str, Any]]
    location_consistency: List[Dict[str, Any]]
    session_duration: float
    interaction_frequency: float
    anomaly_indicators: List[str]
    risk_factors: List[str]
    timestamp: datetime

class BehavioralBiometrics:
    """Behavioral biometrics security system"""
    
    def __init__(self):
        self.profiles = {}
        self.sessions = {}
        self.behavioral_data = defaultdict(list)
        
        # Security thresholds
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.5,
            "high": 0.7,
            "critical": 0.9
        }
        
        # Behavioral patterns
        self.pattern_weights = {
            "mouse_velocity": 0.2,
            "touch_pressure": 0.15,
            "typing_rhythm": 0.2,
            "session_duration": 0.1,
            "interaction_frequency": 0.1,
            "device_orientation": 0.1,
            "location_consistency": 0.15
        }
        
        # Haptic feedback patterns
        self.haptic_patterns = {
            "success": [50, 30, 50],
            "warning": [100, 50, 100],
            "error": [200, 100, 200],
            "verification": [30, 20, 30, 50, 30]
        }
        
        # Animation patterns
        self.animation_types = {
            "scan": "biometric_scan",
            "pulse": "security_pulse",
            "success": "verification_success",
            "warning": "security_warning",
            "error": "verification_error"
        }
        
        # Lockout policies
        self.lockout_policies = {
            "max_failures": 3,
            "lock_duration": 300,  # 5 minutes
            "escalation_threshold": 0.8
        }
        
        logger.info("Behavioral Biometrics system initialized")
    
    async def create_biometric_profile(self, user_id: str, biometric_type: BiometricType, 
                                     baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create biometric profile for user"""
        try:
            # Generate baseline patterns
            baseline_patterns = self._analyze_baseline_patterns(baseline_data)
            
            # Calculate risk threshold based on biometric type
            risk_threshold = self._calculate_risk_threshold(biometric_type)
            
            profile = BiometricProfile(
                user_id=user_id,
                biometric_type=biometric_type,
                baseline_patterns=baseline_patterns,
                risk_threshold=risk_threshold,
                verification_count=0,
                last_verified=None,
                failure_count=0,
                lock_until=None,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.profiles[user_id] = profile
            
            return {
                "success": True,
                "user_id": user_id,
                "biometric_type": biometric_type.value,
                "risk_threshold": risk_threshold,
                "profile_created": True
            }
            
        except Exception as e:
            logger.error(f"Biometric profile creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def initiate_verification(self, user_id: str, security_level: SecurityLevel, 
                                   transaction_amount: float = 0) -> Dict[str, Any]:
        """Initiate biometric verification session"""
        try:
            # Check if user is locked out
            profile = self.profiles.get(user_id)
            if profile and profile.lock_until and profile.lock_until > datetime.now(timezone.utc):
                return {
                    "success": False,
                    "error": "User is locked out",
                    "lock_until": profile.lock_until.isoformat()
                }
            
            # Determine if strategic friction is needed
            strategic_friction = transaction_amount > 10000
            
            # Generate session
            session_id = f"BIOMETRIC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(user_id.encode()).hexdigest()[:8]}"
            
            # Generate challenge data
            challenge_data = self._generate_challenge_data(user_id, security_level, strategic_friction)
            
            # Create session
            session = BiometricSession(
                session_id=session_id,
                user_id=user_id,
                biometric_type=profile.biometric_type if profile else BiometricType.FINGERPRINT,
                security_level=security_level,
                challenge_data=challenge_data,
                response_data=None,
                status=BiometricStatus.PENDING,
                confidence_score=0.0,
                risk_score=0.0,
                created_at=datetime.now(timezone.utc),
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
                haptic_feedback=True,
                animation_type=self.animation_types["scan"]
            )
            
            self.sessions[session_id] = session
            
            return {
                "success": True,
                "session_id": session_id,
                "user_id": user_id,
                "biometric_type": session.biometric_type.value,
                "security_level": security_level.value,
                "challenge_data": challenge_data,
                "strategic_friction": strategic_friction,
                "haptic_feedback": session.haptic_feedback,
                "animation_type": session.animation_type,
                "expires_at": session.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Verification initiation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_biometric(self, session_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify biometric response"""
        try:
            session = self.sessions.get(session_id)
            
            if not session:
                return {
                    "success": False,
                    "error": "Invalid session"
                }
            
            if session.status != BiometricStatus.PENDING:
                return {
                    "success": False,
                    "error": f"Session already {session.status.value}"
                }
            
            if datetime.now(timezone.utc) > session.expires_at:
                session.status = BiometricStatus.FAILED
                return {
                    "success": False,
                    "error": "Session expired"
                }
            
            # Get user profile
            profile = self.profiles.get(session.user_id)
            
            # Perform verification
            verification_result = await self._perform_verification(session, response_data, profile)
            
            # Update session
            session.response_data = response_data
            session.confidence_score = verification_result["confidence_score"]
            session.risk_score = verification_result["risk_score"]
            session.status = verification_result["status"]
            
            # Update profile if verified
            if profile and verification_result["status"] == BiometricStatus.VERIFIED:
                profile.last_verified = datetime.now(timezone.utc)
                profile.verification_count += 1
                profile.updated_at = datetime.now(timezone.utc)
                
                # Trigger success haptic feedback
                session.haptic_feedback = True
                session.animation_type = self.animation_types["success"]
                
            elif verification_result["status"] == BiometricStatus.FAILED:
                if profile:
                    profile.failure_count += 1
                    profile.updated_at = datetime.now(timezone.utc)
                    
                    # Check if user should be locked out
                    if profile.failure_count >= self.lockout_policies["max_failures"]:
                        profile.lock_until = datetime.now(timezone.utc) + timedelta(seconds=self.lockout_policies["lock_duration"])
                    
                    # Trigger error haptic feedback
                    session.haptic_feedback = True
                    session.animation_type = self.animation_types["error"]
            
            return {
                "success": verification_result["status"] == BiometricStatus.VERIFIED,
                "session_id": session_id,
                "status": verification_result["status"].value,
                "confidence_score": verification_result["confidence_score"],
                "risk_score": verification_result["risk_score"],
                "haptic_feedback": session.haptic_feedback,
                "animation_type": session.animation_type,
                "verified_at": datetime.now(timezone.utc).isoformat() if verification_result["status"] == BiometricStatus.VERIFIED else None
            }
            
        except Exception as e:
            logger.error(f"Biometric verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def collect_behavioral_data(self, user_id: str, session_id: str, 
                                     behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
        """Collect behavioral data for analysis"""
        try:
            # Create behavioral metrics
            metrics = BehavioralMetrics(
                user_id=user_id,
                session_id=session_id,
                mouse_patterns=behavioral_data.get("mouse_patterns", []),
                touch_patterns=behavioral_data.get("touch_patterns", []),
                typing_patterns=behavioral_data.get("typing_patterns", []),
                device_orientation=behavioral_data.get("device_orientation", []),
                pressure_patterns=behavioral_data.get("pressure_patterns", []),
                timing_patterns=behavioral_data.get("timing_patterns", []),
                location_consistency=behavioral_data.get("location_consistency", []),
                session_duration=behavioral_data.get("session_duration", 0),
                interaction_frequency=behavioral_data.get("interaction_frequency", 0),
                anomaly_indicators=[],
                risk_factors=[],
                timestamp=datetime.now(timezone.utc)
            )
            
            # Analyze behavioral patterns
            analysis_result = await self._analyze_behavioral_patterns(metrics)
            
            # Store behavioral data
            self.behavioral_data[user_id].append(metrics)
            
            # Keep only last 100 sessions per user
            if len(self.behavioral_data[user_id]) > 100:
                self.behavioral_data[user_id] = self.behavioral_data[user_id][-100:]
            
            return {
                "success": True,
                "user_id": user_id,
                "session_id": session_id,
                "risk_score": analysis_result["risk_score"],
                "anomaly_indicators": analysis_result["anomaly_indicators"],
                "risk_factors": analysis_result["risk_factors"],
                "recommendations": analysis_result["recommendations"]
            }
            
        except Exception as e:
            logger.error(f"Behavioral data collection failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _perform_verification(self, session: BiometricSession, response_data: Dict[str, Any], 
                                    profile: Optional[BiometricProfile]) -> Dict[str, Any]:
        """Perform biometric verification"""
        try:
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(response_data, profile)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(session, response_data, profile)
            
            # Determine status
            threshold = self.risk_thresholds[session.security_level.value]
            
            if confidence_score >= (1 - risk_score) and risk_score <= threshold:
                return {
                    "status": BiometricStatus.VERIFIED,
                    "confidence_score": confidence_score,
                    "risk_score": risk_score
                }
            else:
                return {
                    "status": BiometricStatus.FAILED,
                    "confidence_score": confidence_score,
                    "risk_score": risk_score
                }
                
        except Exception as e:
            logger.error(f"Verification performance failed: {str(e)}")
            return {
                "status": BiometricStatus.FAILED,
                "confidence_score": 0.0,
                "risk_score": 1.0
            }
    
    def _calculate_confidence_score(self, response_data: Dict[str, Any], profile: Optional[BiometricProfile]) -> float:
        """Calculate confidence score for biometric response"""
        try:
            if not profile:
                return 0.5  # Default confidence for new users
            
            # Base confidence from response quality
            base_confidence = 0.7
            
            # Adjust based on pattern similarity
            pattern_similarity = self._calculate_pattern_similarity(response_data, profile.baseline_patterns)
            
            # Adjust based on response time
            response_time = response_data.get("response_time", 1.0)
            time_confidence = max(0, 1.0 - (response_time / 5.0))  # 5 seconds max
            
            # Adjust based on data completeness
            completeness = len(response_data.get("biometric_data", {})) / 10.0
            completeness_confidence = min(1.0, completeness)
            
            # Calculate final confidence
            confidence = (base_confidence * 0.4 + 
                        pattern_similarity * 0.4 + 
                        time_confidence * 0.1 + 
                        completeness_confidence * 0.1)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            logger.error(f"Confidence score calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_risk_score(self, session: BiometricSession, response_data: Dict[str, Any], 
                            profile: Optional[BiometricProfile]) -> float:
        """Calculate risk score for verification attempt"""
        try:
            base_risk = 0.1
            
            # Adjust based on security level
            security_risk = {
                SecurityLevel.LOW: 0.0,
                SecurityLevel.MEDIUM: 0.1,
                SecurityLevel.HIGH: 0.2,
                SecurityLevel.CRITICAL: 0.3
            }
            
            # Adjust based on session age
            session_age = (datetime.now(timezone.utc) - session.created_at).total_seconds()
            age_risk = min(0.2, session_age / 300)  # 5 minutes max
            
            # Adjust based on response anomalies
            anomalies = response_data.get("anomalies", [])
            anomaly_risk = min(0.3, len(anomalies) * 0.1)
            
            # Adjust based on user history
            history_risk = 0.0
            if profile:
                if profile.failure_count > 0:
                    history_risk = min(0.2, profile.failure_count * 0.05)
                if profile.failure_count >= 3:
                    history_risk = 0.5
            
            # Calculate final risk
            risk = (base_risk + 
                    security_risk[session.security_level] + 
                    age_risk + 
                    anomaly_risk + 
                    history_risk)
            
            return min(1.0, max(0.0, risk))
            
        except Exception as e:
            logger.error(f"Risk score calculation failed: {str(e)}")
            return 0.5
    
    def _calculate_pattern_similarity(self, response_data: Dict[str, Any], baseline_patterns: Dict[str, Any]) -> float:
        """Calculate pattern similarity score"""
        try:
            # Mock pattern similarity calculation
            # In production, use actual biometric matching algorithms
            
            similarity = 0.8  # Default similarity
            
            # Adjust based on data quality
            data_quality = len(response_data.get("biometric_data", {}))
            if data_quality > 5:
                similarity += 0.1
            
            return min(1.0, similarity)
            
        except Exception as e:
            logger.error(f"Pattern similarity calculation failed: {str(e)}")
            return 0.5
    
    def _analyze_behavioral_patterns(self, metrics: BehavioralMetrics) -> Dict[str, Any]:
        """Analyze behavioral patterns for anomalies"""
        try:
            risk_score = 0.0
            anomaly_indicators = []
            risk_factors = []
            recommendations = []
            
            # Analyze mouse patterns
            if metrics.mouse_patterns:
                mouse_risk = self._analyze_mouse_patterns(metrics.mouse_patterns)
                risk_score += mouse_risk["risk"]
                anomaly_indicators.extend(mouse_risk["anomalies"])
                risk_factors.extend(mouse_risk["risk_factors"])
            
            # Analyze touch patterns
            if metrics.touch_patterns:
                touch_risk = self._analyze_touch_patterns(metrics.touch_patterns)
                risk_score += touch_risk["risk"]
                anomaly_indicators.extend(touch_risk["anomalies"])
                risk_factors.extend(touch_risk["risk_factors"])
            
            # Analyze typing patterns
            if metrics.typing_patterns:
                typing_risk = self._analyze_typing_patterns(metrics.typing_patterns)
                risk_score += typing_risk["risk"]
                anomaly_indicators.extend(typing_risk["anomalies"])
                risk_factors.extend(typing_risk["risk_factors"])
            
            # Analyze session patterns
            session_risk = self._analyze_session_patterns(metrics)
            risk_score += session_risk["risk"]
            anomaly_indicators.extend(session_risk["anomalies"])
            risk_factors.extend(session_risk["risk_factors"])
            
            # Generate recommendations
            if risk_score > 0.7:
                recommendations.append("High risk detected - additional verification required")
            elif risk_score > 0.5:
                recommendations.append("Medium risk detected - monitor closely")
            elif risk_score > 0.3:
                recommendations.append("Low risk detected - normal monitoring")
            
            return {
                "risk_score": risk_score,
                "anomaly_indicators": anomaly_indicators,
                "risk_factors": risk_factors,
                "recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Behavioral pattern analysis failed: {str(e)}")
            return {
                "risk_score": 0.5,
                "anomaly_indicators": ["analysis_error"],
                "risk_factors": ["system_error"],
                "recommendations": ["Retry verification"]
            }
    
    def _analyze_mouse_patterns(self, mouse_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze mouse movement patterns"""
        try:
            risk = 0.0
            anomalies = []
            risk_factors = []
            
            for pattern in mouse_patterns:
                # Check for unusual velocity
                velocity = pattern.get("velocity", 0)
                if velocity > 1000 or velocity < 10:
                    risk += 0.1
                    anomalies.append("unusual_mouse_velocity")
                    risk_factors.append("high_mouse_velocity" if velocity > 1000 else "low_mouse_velocity")
                
                # Check for erratic movement
                acceleration = pattern.get("acceleration", 0)
                if abs(acceleration) > 500:
                    risk += 0.1
                    anomalies.append("erratic_mouse_movement")
                    risk_factors.append("high_mouse_acceleration")
            
            return {
                "risk": risk,
                "anomalies": anomalies,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"Mouse pattern analysis failed: {str(e)}")
            return {"risk": 0.0, "anomalies": [], "risk_factors": []}
    
    def _analyze_touch_patterns(self, touch_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze touch pressure patterns"""
        try:
            risk = 0.0
            anomalies = []
            risk_factors = []
            
            for pattern in touch_patterns:
                # Check for unusual pressure
                pressure = pattern.get("pressure", 0.5)
                if pressure > 0.9 or pressure < 0.1:
                    risk += 0.1
                    anomalies.append("unusual_touch_pressure")
                    risk_factors.append("high_touch_pressure" if pressure > 0.9 else "low_touch_pressure")
                
                # Check for unusual duration
                duration = pattern.get("duration", 0)
                if duration > 5000 or duration < 50:
                    risk += 0.05
                    anomalies.append("unusual_touch_duration")
                    risk_factors.append("long_touch_duration" if duration > 5000 else "short_touch_duration")
            
            return {
                "risk": risk,
                "anomalies": anomalies,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"Touch pattern analysis failed: {str(e)}")
            return {"risk": 0.0, "anomalies": [], "risk_factors": []}
    
    def _analyze_typing_patterns(self, typing_patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze typing rhythm patterns"""
        try:
            risk = 0.0
            anomalies = []
            risk_factors = []
            
            for pattern in typing_patterns:
                # Check for unusual typing speed
                speed = pattern.get("speed", 60)  # WPM
                if speed > 200 or speed < 10:
                    risk += 0.1
                    anomalies.append("unusual_typing_speed")
                    risk_factors.append("high_typing_speed" if speed > 200 else "low_typing_speed")
                
                # Check for unusual rhythm
                rhythm = pattern.get("rhythm", 0.5)
                if rhythm < 0.2 or rhythm > 0.8:
                    risk += 0.05
                    anomalies.append("unusual_typing_rhythm")
                    risk_factors.append("inconsistent_typing_rhythm")
            
            return {
                "risk": risk,
                "anomalies": anomalies,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"Typing pattern analysis failed: {str(e)}")
            return {"risk": 0.0, "anomalies": [], "risk_factors": []}
    
    def _analyze_session_patterns(self, metrics: BehavioralMetrics) -> Dict[str, Any]:
        """Analyze session patterns"""
        try:
            risk = 0.0
            anomalies = []
            risk_factors = []
            
            # Check session duration
            if metrics.session_duration > 7200:  # 2 hours
                risk += 0.1
                anomalies.append("long_session_duration")
                risk_factors.append("extended_session")
            
            # Check interaction frequency
            if metrics.interaction_frequency > 10:  # 10 interactions per minute
                risk += 0.05
                anomalies.append("high_interaction_frequency")
                risk_factors.append("rapid_interactions")
            
            # Check location consistency
            if metrics.location_consistency:
                location_changes = len(set(loc.get("location") for loc in metrics.location_consistency))
                if location_changes > 2:
                    risk += 0.15
                    anomalies.append("inconsistent_location")
                    risk_factors.append("multiple_locations")
            
            return {
                "risk": risk,
                "anomalies": anomalies,
                "risk_factors": risk_factors
            }
            
        except Exception as e:
            logger.error(f"Session pattern analysis failed: {str(e)}")
            return {"risk": 0.0, "anomalies": [], "risk_factors": []}
    
    def _analyze_baseline_patterns(self, baseline_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze baseline patterns from initial data"""
        try:
            patterns = {
                "mouse_velocity": np.mean(baseline_data.get("mouse_velocities", [50])),
                "touch_pressure": np.mean(baseline_data.get("touch_pressures", [0.5])),
                "typing_speed": np.mean(baseline_data.get("typing_speeds", [60])),
                "session_duration": np.mean(baseline_data.get("session_durations", [1800])),
                "interaction_frequency": np.mean(baseline_data.get("interaction_frequencies", [2]))
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"Baseline pattern analysis failed: {str(e)}")
            return {}
    
    def _calculate_risk_threshold(self, biometric_type: BiometricType) -> float:
        """Calculate risk threshold based on biometric type"""
        thresholds = {
            BiometricType.FINGERPRINT: 0.3,
            BiometricType.FACE_ID: 0.4,
            BiometricType.VOICE: 0.5,
            BiometricType.IRIS_SCAN: 0.2,
            BiometricType.BEHAVIORAL: 0.6
        }
        
        return thresholds.get(biometric_type, 0.3)
    
    def _generate_challenge_data(self, user_id: str, security_level: SecurityLevel, 
                              strategic_friction: bool) -> Dict[str, Any]:
        """Generate challenge data for verification"""
        try:
            challenge_data = {
                "challenge_id": hashlib.sha256(f"{user_id}_{datetime.now().isoformat()}".encode()).hexdigest(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "security_level": security_level.value,
                "strategic_friction": strategic_friction,
                "liveness_detection": strategic_friction,
                "haptic_feedback": True,
                "animation_type": self.animation_types["scan"]
            }
            
            # Add liveness detection for strategic friction
            if strategic_friction:
                challenge_data["liveness_challenge"] = {
                    "type": "face_id",
                    "challenge": "blink_and_smile",
                    "timeout": 10
                }
            
            return challenge_data
            
        except Exception as e:
            logger.error(f"Challenge data generation failed: {str(e)}")
            return {}
    
    def get_haptic_pattern(self, pattern_type: str) -> List[int]:
        """Get haptic feedback pattern"""
        return self.haptic_patterns.get(pattern_type, [50, 30, 50])
    
    def get_animation_type(self, status: str) -> str:
        """Get animation type for status"""
        return self.animation_types.get(status, self.animation_types["pulse"])
    
    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user biometric profile"""
        try:
            profile = self.profiles.get(user_id)
            
            if not profile:
                return {
                    "success": False,
                    "error": "Profile not found"
                }
            
            return {
                "success": True,
                "user_id": user_id,
                "biometric_type": profile.biometric_type.value,
                "risk_threshold": profile.risk_threshold,
                "verification_count": profile.verification_count,
                "last_verified": profile.last_verified.isoformat() if profile.last_verified else None,
                "failure_count": profile.failure_count,
                "lock_until": profile.lock_until.isoformat() if profile.lock_until else None,
                "created_at": profile.created_at.isoformat(),
                "updated_at": profile.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Profile retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_behavioral_summary(self, user_id: str) -> Dict[str, Any]:
        """Get behavioral summary for user"""
        try:
            user_data = self.behavioral_data.get(user_id, [])
            
            if not user_data:
                return {
                    "success": False,
                    "error": "No behavioral data found"
                }
            
            # Calculate summary statistics
            total_sessions = len(user_data)
            avg_session_duration = np.mean([m.session_duration for m in user_data])
            avg_risk_score = np.mean([self._analyze_behavioral_patterns(m)["risk_score"] for m in user_data])
            
            return {
                "success": True,
                "user_id": user_id,
                "total_sessions": total_sessions,
                "average_session_duration": avg_session_duration,
                "average_risk_score": avg_risk_score,
                "last_session": user_data[-1].timestamp.isoformat() if user_data else None
            }
            
        except Exception as e:
            logger.error(f"Behavioral summary retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
behavioral_biometrics = BehavioralBiometrics()

# API endpoints
async def create_biometric_profile_api(user_id: str, biometric_type: str, 
                                        baseline_data: Dict[str, Any]) -> Dict[str, Any]:
    """API endpoint for creating biometric profile"""
    return await behavioral_biometrics.create_biometric_profile(
        user_id, BiometricType(biometric_type), baseline_data
    )

async def initiate_verification_api(user_id: str, security_level: str, 
                                   transaction_amount: float = 0) -> Dict[str, Any]:
    """API endpoint for initiating verification"""
    return await behavioral_biometrics.initiate_verification(
        user_id, SecurityLevel(security_level), transaction_amount
    )

async def verify_biometric_api(session_id: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
    """API endpoint for verifying biometric"""
    return await behavioral_biometrics.verify_biometric(session_id, response_data)

async def collect_behavioral_data_api(user_id: str, session_id: str, 
                                     behavioral_data: Dict[str, Any]) -> Dict[str, Any]:
    """API endpoint for collecting behavioral data"""
    return await behavioral_biometrics.collect_behavioral_data(user_id, session_id, behavioral_data)

async def get_user_profile_api(user_id: str) -> Dict[str, Any]:
    """API endpoint for getting user profile"""
    return await behavioral_biometrics.get_user_profile(user_id)

async def get_behavioral_summary_api(user_id: str) -> Dict[str, Any]:
    """API endpoint for getting behavioral summary"""
    return await behavioral_biometrics.get_behavioral_summary(user_id)
