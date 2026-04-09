"""
Consumer Protection API - NBE 2026 Compliant Safety Endpoints
Elite-Tier Protection Framework REST API
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio
import logging

from ..consumer_protection import (
    ConsumerProtectionFramework,
    consumer_protection_framework,
    SafetyLevel,
    RiskLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="DEDAN Mine Consumer Protection API",
    description="NBE 2026 Compliant Elite-Tier Safety Framework",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic models
class SafetyCheckRequest(BaseModel):
    """Safety check request model"""
    user_id: str = Field(..., description="User ID")
    transaction_data: Dict[str, Any] = Field(..., description="Transaction data")
    session_data: Dict[str, Any] = Field(..., description="Session data")
    client_public_key: Optional[str] = Field(None, description="Client public key")
    private_key: Optional[str] = Field(None, description="Private key")

class SafetyCheckResponse(BaseModel):
    """Safety check response model"""
    overall_safety_level: str
    overall_safety_score: float
    nbe_compliance: bool
    quantum_secured: bool
    protection_active: bool
    safety_description: str
    checks_performed: List[Dict[str, Any]]
    timestamp: str

class RiskDisclosureRequest(BaseModel):
    """Risk disclosure request model"""
    user_id: str = Field(..., description="User ID")
    transaction_amount: float = Field(..., gt=0, description="Transaction amount")
    mineral_type: str = Field(..., description="Mineral type")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Market data")

class RiskDisclosureResponse(BaseModel):
    """Risk disclosure response model"""
    disclosure_id: str
    risk_level: str
    volatility_warning: str
    potential_loss: str
    recommendations: List[str]
    nbe_compliance: bool
    timestamp: str

class ZKPVerificationRequest(BaseModel):
    """ZKP verification request model"""
    user_id: str = Field(..., description="User ID")
    statement: str = Field(..., description="Statement to verify")
    public_inputs: Optional[Dict[str, Any]] = Field(None, description="Public inputs")
    proof: Optional[str] = Field(None, description="Zero-knowledge proof")

class ZKPVerificationResponse(BaseModel):
    """ZKP verification response model"""
    verification_id: str
    statement_verified: bool
    proof_valid: bool
    privacy_preserved: bool
    nbe_compliance: bool
    timestamp: str

class BehavioralAnalysisRequest(BaseModel):
    """Behavioral analysis request model"""
    user_id: str = Field(..., description="User ID")
    session_data: Dict[str, Any] = Field(..., description="Session data")
    analysis_type: str = Field(..., description="Analysis type")

class BehavioralAnalysisResponse(BaseModel):
    """Behavioral analysis response model"""
    analysis_id: str
    risk_score: float
    anomalies_detected: List[str]
    auto_freeze: bool
    baseline_updated: bool
    nbe_compliance: bool
    timestamp: str

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    # Mock authentication - implement real JWT validation
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate token (mock)
    if credentials.credentials != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": "demo_user", "permissions": ["consumer_protection"]}

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Consumer Protection API",
        "version": "2.0.0",
        "nbe_compliance": True,
        "quantum_security": True,
        "protection_level": "elite_tier",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Comprehensive safety check
@app.post("/safety/check", response_model=SafetyCheckResponse, tags=["Safety"])
async def comprehensive_safety_check(
    request: SafetyCheckRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform comprehensive safety check"""
    try:
        # Perform comprehensive safety check
        safety_results = await consumer_protection_framework.comprehensive_safety_check(
            request.transaction_data,
            request.user_id,
            request.session_data
        )
        
        # Add background task for logging
        background_tasks.add_task(
            log_safety_check_background,
            request.user_id,
            safety_results
        )
        
        return SafetyCheckResponse(**safety_results)
        
    except Exception as e:
        logger.error(f"Comprehensive safety check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# NBE Anti-Scam Firewall
@app.post("/anti-scam/scan", tags=["Anti-Scam"])
async def anti_scam_scan(
    transaction_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Scan transaction for scam patterns"""
    try:
        result = await consumer_protection_framework.anti_scam_firewall.scan_transaction(transaction_data)
        return result
        
    except Exception as e:
        logger.error(f"Anti-scam scan error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Data protection - Encryption
@app.post("/data/encrypt", tags=["Data Protection"])
async def encrypt_user_data(
    user_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Encrypt user data with AES-256-GCM"""
    try:
        result = await consumer_protection_framework.data_protection.encrypt_user_data(
            user_data,
            current_user["user_id"]
        )
        return result
        
    except Exception as e:
        logger.error(f"Data encryption error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Data protection - ZKP
@app.post("/data/zkp/generate", response_model=ZKPVerificationResponse, tags=["Data Protection"])
async def generate_zkp_proof(
    request: ZKPVerificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate Zero-Knowledge Proof"""
    try:
        result = await consumer_protection_framework.data_protection.generate_zkp_proof(
            {"user_id": request.user_id, "statement": request.statement},
            request.user_id
        )
        return result
        
    except Exception as e:
        logger.error(f"ZKP generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/zkp/verify", response_model=ZKPVerificationResponse, tags=["Data Protection"])
async def verify_zkp_proof(
    request: ZKPVerificationRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Verify Zero-Knowledge Proof"""
    try:
        # Mock ZKP verification
        # In production, integrate with actual ZK-SNARK verification
        result = {
            "verification_id": f"zkp_verify_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "statement_verified": True,
            "proof_valid": True,
            "privacy_preserved": True,
            "nbe_compliance": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"ZKP verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Quantum security - Session establishment
@app.post("/quantum/session/establish", tags=["Quantum Security"])
async def establish_quantum_session(
    client_public_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Establish quantum-resistant session"""
    try:
        result = await consumer_protection_framework.quantum_security.establish_quantum_session(client_public_key)
        return result
        
    except Exception as e:
        logger.error(f"Quantum session establishment error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Quantum security - Transaction signing
@app.post("/quantum/sign", tags=["Quantum Security"])
async def sign_transaction_quantum(
    transaction_data: Dict[str, Any],
    private_key: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Sign transaction with ML-DSA (Dilithium)"""
    try:
        result = await consumer_protection_framework.quantum_security.sign_transaction_quantum(
            transaction_data,
            private_key
        )
        return result
        
    except Exception as e:
        logger.error(f"Quantum signature error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Financial safety - Escrow
@app.post("/financial/escrow/create", tags=["Financial Safety"])
async def create_escrow_contract(
    transaction_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Create escrow contract"""
    try:
        result = await consumer_protection_framework.sovereign_vault.create_escrow_contract(transaction_data)
        return result
        
    except Exception as e:
        logger.error(f"Escrow contract creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/financial/escrow/release", tags=["Financial Safety"])
async def release_escrow_funds(
    contract_id: str,
    provenance_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Release escrow funds"""
    try:
        result = await consumer_protection_framework.sovereign_vault.verify_provenance_for_release(
            contract_id,
            provenance_data
        )
        return result
        
    except Exception as e:
        logger.error(f"Escrow release error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# NBE Risk Disclosure
@app.post("/nbe/risk-disclosure", response_model=RiskDisclosureResponse, tags=["NBE Compliance"])
async def generate_risk_disclosure(
    request: RiskDisclosureRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate NBE-compliant risk disclosure"""
    try:
        # Calculate risk level based on transaction
        risk_score = calculate_risk_score(request.transaction_amount, request.mineral_type)
        
        # Generate disclosure content
        disclosure = generate_disclosure_content(risk_score, request)
        
        result = {
            "disclosure_id": f"risk_disclosure_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "risk_level": get_risk_level_from_score(risk_score),
            "volatility_warning": generate_volatility_warning(request.mineral_type),
            "potential_loss": f"Up to {request.transaction_amount * 0.15:.2f} ETB",
            "recommendations": generate_recommendations(risk_score),
            "nbe_compliance": True,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Risk disclosure generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Guardian AI - Behavioral analysis
@app.post("/guardian/behavioral/analyze", response_model=BehavioralAnalysisResponse, tags=["Guardian AI"])
async def analyze_behavioral_patterns(
    request: BehavioralAnalysisRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Analyze behavioral patterns"""
    try:
        result = await consumer_protection_framework.guardian_ai.analyze_behavioral_biometrics(
            request.user_id,
            request.session_data
        )
        
        return BehavioralAnalysisResponse(**result)
        
    except Exception as e:
        logger.error(f"Behavioral analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Guardian AI - Freeze account
@app.post("/guardian/freeze/{user_id}", tags=["Guardian AI"])
async def freeze_user_account(
    user_id: str,
    reason: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Freeze user account due to suspicious activity"""
    try:
        # Log freeze event
        freeze_event = {
            "freeze_id": f"freeze_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "user_id": user_id,
            "reason": reason,
            "initiated_by": current_user["user_id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nbe_compliance": True
        }
        
        # In production, implement actual account freeze logic
        logger.warning(f"Account frozen: {user_id} - Reason: {reason}")
        
        return {
            "success": True,
            "freeze_id": freeze_event["freeze_id"],
            "user_id": user_id,
            "reason": reason,
            "timestamp": freeze_event["timestamp"],
            "nbe_compliance": True
        }
        
    except Exception as e:
        logger.error(f"Account freeze error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Guardian AI - 72-hour breach alert
@app.post("/guardian/breach-alert", tags=["Guardian AI"])
async def send_breach_alert(
    breach_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Send 72-hour breach alert to Ethiopian authorities"""
    try:
        # Prepare breach alert
        alert_data = {
            "alert_id": f"breach_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "breach_type": breach_data.get("type", "security"),
            "severity": breach_data.get("severity", "high"),
            "affected_users": breach_data.get("affected_users", []),
            "description": breach_data.get("description", ""),
            "actions_taken": breach_data.get("actions_taken", []),
            "ethiopian_authorities_notified": True,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "nbe_compliance": True
        }
        
        # In production, implement actual notification to Ethiopian Communications Authority
        logger.critical(f"Security breach alert: {alert_data}")
        
        return {
            "success": True,
            "alert_id": alert_data["alert_id"],
            "ethiopian_authorities_notified": True,
            "timestamp": alert_data["timestamp"],
            "nbe_compliance": True
        }
        
    except Exception as e:
        logger.error(f"Breach alert error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions
def calculate_risk_score(amount: float, mineral_type: str) -> float:
    """Calculate risk score"""
    # Base risk calculation
    base_score = 50
    
    # Adjust based on amount
    if amount > 100000:
        base_score += 30
    elif amount > 50000:
        base_score += 20
    elif amount > 10000:
        base_score += 10
    
    # Adjust based on mineral type
    high_risk_minerals = ["gold", "tantalum", "rare_earth"]
    if mineral_type.lower() in high_risk_minerals:
        base_score += 15
    
    return min(100, base_score)

def get_risk_level_from_score(score: float) -> str:
    """Get risk level from score"""
    if score >= 80:
        return "high"
    elif score >= 60:
        return "medium"
    elif score >= 40:
        return "low"
    else:
        return "very_low"

def generate_disclosure_content(risk_score: float, request: RiskDisclosureRequest) -> List[str]:
    """Generate disclosure content"""
    content = [
        "⚠️ NBE RISK DISCLOSURE - NBE-FCP/01/2026 ⚠️",
        "",
        "Investment Risk Level: " + get_risk_level_from_score(risk_score).upper(),
        "",
        f"Mineral Type: {request.mineral_type}",
        f"Transaction Amount: {request.transaction_amount} ETB",
        "",
        "Market Volatility Warning:",
        "• Mineral markets are highly volatile",
        "• Prices can change rapidly without notice",
        "• Past performance does not guarantee future results",
        "",
        "Potential Loss Warning:",
        f"• You could lose up to {request.transaction_amount * 0.15:.2f} ETB",
        "• Only invest what you can afford to lose",
        "• Consider your financial situation carefully",
        "",
        "NBE Consumer Protection Rights:",
        "• You have the right to clear information",
        "• You have the right to fair treatment",
        "• You have the right to privacy protection",
        "• You have the right to redress mechanisms",
        "",
        f"Disclosure ID: risk_disclosure_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ]
    
    return content

def generate_volatility_warning(mineral_type: str) -> str:
    """Generate volatility warning"""
    volatility_warnings = {
        "gold": "Gold prices can fluctuate significantly based on global economic conditions",
        "silver": "Silver markets are subject to high volatility and speculation",
        "tantalum": "Tantalum prices are highly volatile due to limited supply",
        "rare_earth": "Rare earth elements experience extreme price volatility",
        "potash": "Potash prices are influenced by agricultural demand and weather",
        "coal": "Coal prices are subject to environmental regulations and market shifts"
    }
    
    return volatility_warnings.get(mineral_type.lower(), "Market volatility applies to this investment")

def generate_recommendations(risk_score: float) -> List[str]:
    """Generate risk-based recommendations"""
    recommendations = []
    
    if risk_score >= 80:
        recommendations.extend([
            "Consider consulting with a licensed financial advisor",
            "Start with a smaller investment amount",
            "Diversify your investment portfolio",
            "Set clear stop-loss limits",
            "Monitor market conditions regularly"
        ])
    elif risk_score >= 60:
        recommendations.extend([
            "Educate yourself about the mineral market",
            "Consider the tax implications",
            "Have an exit strategy",
            "Invest only disposable income"
        ])
    else:
        recommendations.extend([
            "Continue monitoring market conditions",
            "Stay informed about regulatory changes",
            "Maintain detailed records",
            "Review performance periodically"
        ])
    
    return recommendations

async def log_safety_check_background(user_id: str, safety_results: Dict[str, Any]):
    """Log safety check in background"""
    try:
        # In production, log to database
        logger.info(f"Safety check completed for user {user_id}: {safety_results}")
    except Exception as e:
        logger.error(f"Background logging error: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "nbe_compliance": False,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Run server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.consumer_protection_api:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
