"""
DEDAN Mine (Worldmine) - Conflict-Free Unified Architecture
Production-ready API with unified state management and priority logic
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn

# Import core unified state management
from core import unified_state_manager, UnifiedUserSession, sovereign_auth_system, conflict_prevention_system

# Import unified services
from services.unified import guardian_ai_vault, satellite_transaction_controller, micro_insurance_oracle
from services.sovereign import sovereign_onboarding_service
from services.regulatory import tax_oracle
from services.esg import esg_auditor

# Import existing services
from services.marketplace.listings import ListingService
from services.ai_agents.tradingAgent import AutonomousTradingAgent
from services.video_negotiation.videoStreaming import VideoNegotiationService
from services.traceability.iotSensors import IoTSensorService
from services.esg.scoring import ESGScoringService
from services.compliance.ecxIntegration import ECXComplianceService
from services.security.quantumEncryption import QuantumSecureData

# Import existing MarketNewsAgent and StateGraph
from main_simple import SimpleMarketNewsAgent
from main import MarketNewsAgent, StateGraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 DEDAN Mine Unified Architecture starting up...")
    
    # Initialize services
    listing_service = ListingService()
    esg_service = ESGScoringService()
    video_service = VideoNegotiationService()
    iot_service = IoTSensorService()
    ecx_service = ECXComplianceService()
    
    # Store in app state for access in endpoints
    app.state.listing_service = listing_service
    app.state.esg_service = esg_service
    app.state.video_service = video_service
    app.state.iot_service = iot_service
    app.state.ecx_service = ecx_service
    
    yield
    
    logger.info("🛑 DEDAN Mine Unified Architecture shutting down...")

# Create FastAPI application
app = FastAPI(
    title="DEDAN Mine - Conflict-Free Unified Architecture",
    description="World's most advanced AI-powered mining transaction marketplace with unified state management and priority logic",
    version="3.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dedan-mine.vercel.app",
        "https://worldmine.vercel.app",
        "*.vercel.app",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"]
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["dedan-mine.vercel.app", "*.vercel.app", "localhost", "127.0.0.1"]
)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Unified session middleware
@app.middleware("http")
async def unified_session_middleware(request: Request, call_next):
    """Unified session management middleware"""
    try:
        # Extract or create session ID
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Get or create unified session
        session = await unified_state_manager.get_session(session_id)
        if not session:
            # Create new session with mock user data
            user_id = request.headers.get("X-User-ID", str(uuid.uuid4()))
            session = await unified_state_manager.create_session(
                user_id=user_id,
                initial_data={
                    "profile": {"username": "demo_user"},
                    "verification": {"level": "basic"}
                }
            )
        
        # Add session to request state
        request.state.session_id = session_id
        request.state.unified_session = session
        
        response = await call_next(request)
        
        # Add session headers
        response.headers["X-Session-ID"] = session_id
        response.headers["X-Session-Updated"] = session.updated_at.isoformat()
        
        return response
        
    except Exception as e:
        logger.error(f"Unified session middleware error: {e}")
        return await call_next(request)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Safe logging without PII
    safe_log_data = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "time": f"{process_time:.3f}s",
        "session_id": getattr(request.state, 'session_id', 'unknown')
    }
    
    logger.info(f"📊 Unified Request: {safe_log_data}")
    
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Render keep-alive"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "service": "dedan-mine-api",
        "uptime": time.time(),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "features": {
            "marketplace": True,
            "ai_agents": True,
            "video_negotiations": True,
            "traceability": True,
            "esg_scoring": True,
            "ecx_compliance": True,
            "quantum_security": True
        }
    }

# API Health endpoint (alternative path)
@app.get("/api/health")
async def api_health_check():
    """API health check endpoint for frontend keep-alive"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0",
        "service": "dedan-mine-api",
        "message": "DEDAN Mine API is operational with all advanced features"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "status": "online", 
        "platform": "DEDAN Mine Unified Architecture",
        "version": "3.0.0",
        "features": [
            "Guardian AI Personal Vault",
            "Miner Legacy Chain", 
            "Behavioral Reputation Oracle",
            "Self-Healing Dispute Engine",
            "User Co-Ownership Nexus",
            "Zero-Knowledge User Shield",
            "Evolving Agent Marketplace",
            "Ethical Impact Credit Score",
            "Instant Micro-Insurance Oracle",
            "Community Oracle Network",
            "Satellite-Controlled Transactions"
        ],
        "architecture": "Conflict-Free Unified State Management",
        "priority_logic": "Critical Security > High Priority > Medium > Low > Standard"
    }

# ===== SOVEREIGN AUTHENTICATION ENDPOINTS =====

# Phase A: Invisible Handshake (Returning User)
@app.post("/api/v4/sovereign/invisible-handshake")
async def invisible_handshake(request: Request):
    """Phase A: The Invisible Handshake - Silent FIDO2 detection"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        user_request = data.get("user_request", {})
        
        result = await sovereign_onboarding_service.initiate_invisible_handshake(user_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in invisible handshake: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Phase B: Sovereign Forging (New User)
@app.post("/api/v4/sovereign/forge")
async def sovereign_forging(request: Request):
    """Phase B: The Sovereign Forging - New user onboarding"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        user_request = data.get("user_request", {})
        
        result = await sovereign_onboarding_service.initiate_sovereign_forging(user_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in sovereign forging: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/sovereign/step/digital-key")
async def forge_digital_key(request: Request):
    """Step 1: The Digital Key - Generate DID and PQC keypair"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        step_data = data.get("step_data", {})
        
        result = await sovereign_onboarding_service.execute_digital_key_forging(session_id, step_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in digital key forging: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/sovereign/step/behavioral-dna")
async def enroll_behavioral_dna(request: Request):
    """Step 2: The Behavioral DNA - Enroll biometrics"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        step_data = data.get("step_data", {})
        
        result = await sovereign_onboarding_service.execute_behavioral_dna(session_id, step_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in behavioral DNA enrollment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/sovereign/step/sovereign-shield")
async def activate_sovereign_shield(request: Request):
    """Step 3: The Sovereign Shield - Finalize SSI credentials"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        step_data = data.get("step_data", {})
        
        result = await sovereign_onboarding_service.execute_sovereign_shield(session_id, step_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in sovereign shield activation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/sovereign/dashboard/{user_id}")
async def get_bento_dashboard(user_id: str, request: Request):
    """Get Bento Dashboard configuration for authenticated user"""
    try:
        result = await sovereign_onboarding_service.get_bento_dashboard_config(user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting Bento dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 10-Layer Shield Authentication Endpoints
@app.post("/api/v4/auth/sovereign/initiate")
async def initiate_sovereign_auth(request: Request):
    """Initiate sovereign authentication with 10-layer shield"""
    try:
        data = await request.json()
        auth_request = data.get("auth_request", {})
        
        result = await sovereign_auth_system.initiate_sovereign_auth(auth_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error initiating sovereign auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/fido2/verify")
async def verify_fido2_passkey(request: Request):
    """Verify FIDO2 Passkey authentication"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        credential_data = data.get("credential_data", {})
        
        result = await sovereign_auth_system.verify_fido2_passkey(session_id, credential_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying FIDO2 passkey: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/ssi/did/verify")
async def verify_ssi_did(request: Request):
    """Verify Self-Sovereign Identity (DID) authentication"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        did_data = data.get("did_data", {})
        
        result = await sovereign_auth_system.verify_ssi_did(session_id, did_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying SSI DID: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/pqc/verify")
async def verify_post_quantum(request: Request):
    """Verify Post-Quantum Cryptography authentication"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        pqc_data = data.get("pqc_data", {})
        
        result = await sovereign_auth_system.verify_post_quantum(session_id, pqc_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying PQC: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/zk/verify")
async def verify_zero_knowledge(request: Request):
    """Verify Zero-Knowledge Proof authentication"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        zk_data = data.get("zk_data", {})
        
        result = await sovereign_auth_system.verify_zero_knowledge(session_id, zk_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying ZK proof: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/behavioral/verify")
async def verify_behavioral_biometrics(request: Request):
    """Verify Behavioral Biometrics authentication"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        behavioral_data = data.get("behavioral_data", {})
        
        result = await sovereign_auth_system.verify_behavioral_biometrics(session_id, behavioral_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying behavioral biometrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/liveness/verify")
async def verify_liveness(request: Request):
    """Verify Liveness Detection"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        liveness_data = data.get("liveness_data", {})
        
        result = await sovereign_auth_system.verify_liveness(session_id, liveness_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error verifying liveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/auth/complete")
async def complete_sovereign_auth(request: Request):
    """Complete sovereign authentication and issue tokens"""
    try:
        data = await request.json()
        session_id = data.get("session_id")
        
        result = await sovereign_auth_system.complete_sovereign_auth(session_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error completing sovereign auth: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Guardian AI Personal Vault
@app.post("/api/v3/guardian/monitor-behavior")
async def monitor_guardian_behavior(request: Request):
    """Guardian AI behavioral biometric monitoring"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        biometric_data = data.get("biometric_data", {})
        
        result = await guardian_ai_vault.monitor_user_behavior(
            session_id=session_id,
            biometric_data=biometric_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in Guardian AI monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Satellite Controlled Transactions
@app.post("/api/v3/satellite/verify-coordinates")
async def verify_satellite_coordinates(request: Request):
    """Satellite coordinate verification for transactions"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        transaction_data = data.get("transaction_data", {})
        
        result = await satellite_transaction_controller.verify_transaction_coordinates(
            session_id=session_id,
            transaction_data=transaction_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in satellite verification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/satellite/provenance/{transaction_id}")
async def get_transaction_provenance(transaction_id: str, request: Request):
    """Get satellite provenance for transaction"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        result = await satellite_transaction_controller.get_transaction_provenance(
            session_id=session_id,
            transaction_id=transaction_id
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting transaction provenance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Instant Micro-Insurance Oracle
@app.post("/api/v3/insurance/calculate-premium")
async def calculate_insurance_premium(request: Request):
    """Calculate micro-insurance premium with real-time risk assessment"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        coverage_request = data.get("coverage_request", {})
        
        result = await micro_insurance_oracle.calculate_insurance_premium(
            session_id=session_id,
            coverage_request=coverage_request
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating insurance premium: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/insurance/process-claim")
async def process_insurance_claim(request: Request):
    """Process insurance claim with automated verification"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        claim_data = data.get("claim_data", {})
        
        result = await micro_insurance_oracle.process_insurance_claim(
            session_id=session_id,
            claim_data=claim_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing insurance claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Unified State Management Endpoints
@app.get("/api/v3/session/status")
async def get_session_status(request: Request):
    """Get unified session status"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        session = await unified_state_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "success": True,
            "session_id": session_id,
            "user_id": session.user_id,
            "security_level": session.security_level,
            "risk_score": session.risk_score,
            "trust_score": session.trust_score,
            "space_verified": session.space_verified,
            "insurance_active": session.insurance_active,
            "pii_protected": session.pii_protected,
            "updated_at": session.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting session status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/feature/execute")
async def execute_unified_feature(request: Request):
    """Execute any unified feature with priority logic and dependency resolution"""
    try:
        session_id = getattr(request.state, 'session_id')
        if not session_id:
            raise HTTPException(status_code=401, detail="No session found")
        
        data = await request.json()
        feature_name = data.get("feature_name")
        request_data = data.get("request_data", {})
        
        session = await unified_state_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        result = await unified_state_manager.execute_feature_request(
            feature_name=feature_name,
            user_id=session.user_id,
            session_id=session_id,
            request_data=request_data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error executing unified feature: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/feature/registry")
async def get_feature_registry():
    """Get all available features and their priorities"""
    try:
        registry = unified_state_manager.feature_registry
        dependencies = unified_state_manager.dependency_graph
        
        # Format for response
        formatted_registry = {}
        for feature_name, config in registry.items():
            formatted_registry[feature_name] = {
                "priority": config["priority"].name,
                "requires_pii_access": config.get("requires_pii_access", False),
                "blocks_other_features": config.get("blocks_other_features", False),
                "description": config["description"],
                "dependencies": dependencies.get(feature_name, [])
            }
        
        return {
            "success": True,
            "features": formatted_registry,
            "total_features": len(formatted_registry),
            "dependency_graph": dependencies
        }
        
    except Exception as e:
        logger.error(f"Error getting feature registry: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== LEGACY COMPATIBILITY ENDPOINTS =====

# Keep existing endpoints for backward compatibility
@app.get("/api/v1/listings/browse")
async def legacy_browse_listings(request: Request):
    """Legacy marketplace browsing endpoint"""
    try:
        listing_service = request.app.state.listing_service
        
        result = await listing_service.get_listings(
            page=int(request.query_params.get("page", 1)),
            limit=int(request.query_params.get("limit", 20)),
            category=request.query_params.get("category"),
            gem_type=request.query_params.get("gem_type"),
            min_price=float(request.query_params.get("min_price")) if request.query_params.get("min_price") else None,
            max_price=float(request.query_params.get("max_price")) if request.query_params.get("max_price") else None,
            sort_by=request.query_params.get("sort_by", "created_at"),
            sort_order=request.query_params.get("sort_order", "desc")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in legacy listings browse: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analyze")
async def legacy_market_analysis(request: Request):
    """Legacy market analysis endpoint"""
    try:
        # Use SimpleMarketNewsAgent for lightweight analysis
        agent = SimpleMarketNewsAgent()
        
        # Get query parameters
        query = request.query_params.get("q", "mining market")
        limit = int(request.query_params.get("limit", 10))
        
        # Perform basic analysis
        analysis = await agent.get_basic_news(query, limit)
        
        return {
            "success": True,
            "analysis": analysis,
            "query": query,
            "limit": limit,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": "legacy_compatibility"
        }
        
    except Exception as e:
        logger.error(f"Error in legacy market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ESG AUDITOR ENDPOINTS =====

@app.post("/api/v4/esg/calculate-carbon-neutral-score")
async def calculate_carbon_neutral_score(request: Request):
    """Calculate carbon-neutral score for mineral listing"""
    try:
        data = await request.json()
        listing_data = data.get("listing_data", {})
        
        result = await esg_auditor.calculate_carbon_neutral_score(listing_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating carbon-neutral score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/esg/certificate/{listing_id}")
async def get_esg_certificate(listing_id: str):
    """Get ESG certificate for listing"""
    try:
        result = await esg_auditor.get_esg_certificate(listing_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting ESG certificate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/esg/update-score/{listing_id}")
async def update_esg_score(listing_id: str, request: Request):
    """Update ESG score with new data"""
    try:
        data = await request.json()
        update_data = data.get("update_data", {})
        
        result = await esg_auditor.update_esg_score(listing_id, update_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating ESG score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/esg/summary")
async def get_esg_summary():
    """Get ESG summary for all listings"""
    try:
        result = await esg_auditor.get_esg_summary()
        return result
        
    except Exception as e:
        logger.error(f"Error getting ESG summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== CONFLICT PREVENTION ENDPOINTS =====

@app.post("/api/v4/conflict/prevent")
async def prevent_conflicts(request: Request):
    """Prevent conflicts before execution"""
    try:
        data = await request.json()
        feature_request = data.get("feature_request", {})
        
        result = await conflict_prevention_system.prevent_conflicts(feature_request)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in conflict prevention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/conflict/statistics")
async def get_conflict_statistics():
    """Get conflict prevention statistics"""
    try:
        result = await conflict_prevention_system.get_conflict_statistics()
        return result
        
    except Exception as e:
        logger.error(f"Error getting conflict statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== REGULATORY AND TAX COMPLIANCE ENDPOINTS =====

@app.post("/api/v4/tax/calculate")
async def calculate_transaction_taxes(request: Request):
    """Calculate all applicable taxes for a transaction"""
    try:
        data = await request.json()
        transaction_data = data.get("transaction_data", {})
        
        result = await tax_oracle.calculate_transaction_taxes(transaction_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating taxes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/tax/rates")
async def get_tax_rates(jurisdiction: Optional[str] = None, mineral_type: Optional[str] = None):
    """Get current tax rates"""
    try:
        result = await tax_oracle.get_tax_rates(jurisdiction, mineral_type)
        return result
        
    except Exception as e:
        logger.error(f"Error getting tax rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v4/tax/rates/update")
async def update_tax_rate(request: Request):
    """Update tax rate (admin function)"""
    try:
        data = await request.json()
        rate_update = data.get("rate_update", {})
        
        result = await tax_oracle.update_tax_rate(rate_update)
        
        return result
        
    except Exception as e:
        logger.error(f"Error updating tax rate: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/tax/history/{transaction_id}")
async def get_tax_calculation_history(transaction_id: str):
    """Get tax calculation history for a transaction"""
    try:
        result = await tax_oracle.get_tax_calculation_history(transaction_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting tax history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== AI AGENTS ENDPOINTS =====

@app.post("/api/v1/ai-agents/create")
async def create_ai_agent(request: Request):
    """Create autonomous trading agent"""
    try:
        data = await request.json()
        
        agent = AutonomousTradingAgent(
            agent_id=str(uuid.uuid4()),
            owner_id=data.get("owner_id")
        )
        
        result = await agent.activate_agent()
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating AI agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/ai-agents/{agent_id}/analyze")
async def analyze_market(agent_id: str, request: Request):
    """AI market analysis"""
    try:
        data = await request.json()
        gem_types = data.get("gem_types")
        
        agent = AutonomousTradingAgent(agent_id, "")
        result = await agent.analyze_market(gem_types)
        
        return result
        
    except Exception as e:
        logger.error(f"Error in market analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ai-agents/{agent_id}/bid")
async def autonomous_bid(agent_id: str, request: Request):
    """Place autonomous bid"""
    try:
        data = await request.json()
        
        agent = AutonomousTradingAgent(agent_id, "")
        result = await agent.place_autonomous_bid(
            listing_id=data.get("listing_id"),
            max_bid=data.get("max_bid")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in autonomous bid: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== VIDEO NEGOTIATION ENDPOINTS =====

@app.post("/api/v1/video/schedule")
async def schedule_video_session(request: Request):
    """Schedule video negotiation or live auction"""
    try:
        data = await request.json()
        video_service = request.app.state.video_service
        
        result = await video_service.schedule_video_session(
            host_id=data.get("host_id"),
            listing_id=data.get("listing_id"),
            session_config=VideoSessionConfig(
                session_type=data.get("session_type"),
                max_participants=data.get("max_participants", 10),
                duration_minutes=data.get("duration_minutes", 60),
                enable_recording=data.get("enable_recording", True),
                enable_transcription=data.get("enable_transcription", True)
            )
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error scheduling video session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/video/join/{session_id}")
async def join_video_session(session_id: str, request: Request):
    """Join video session"""
    try:
        data = await request.json()
        video_service = request.app.state.video_service
        
        result = await video_service.join_video_session(
            session_id=session_id,
            participant_id=data.get("participant_id"),
            participant_type=data.get("participant_type", "participant")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error joining video session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/video/message")
async def send_video_message(request: Request):
    """Send message to video session"""
    try:
        data = await request.json()
        video_service = request.app.state.video_service
        
        result = await video_service.send_message_to_session(
            session_id=data.get("session_id"),
            sender_id=data.get("sender_id"),
            message=data.get("message"),
            message_type=data.get("message_type", "text"),
            metadata=data.get("metadata")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error sending video message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== TRACEABILITY ENDPOINTS =====

@app.post("/api/v1/traceability/register-sensors")
async def register_mine_sensors(request: Request):
    """Register IoT sensors for mine traceability"""
    try:
        data = await request.json()
        iot_service = request.app.state.iot_service
        
        result = await iot_service.register_mine_sensors(
            listing_id=data.get("listing_id"),
            sensor_config=data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error registering sensors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/traceability/record-sensors")
async def record_sensor_data(request: Request):
    """Record IoT sensor data"""
    try:
        data = await request.json()
        iot_service = request.app.state.iot_service
        
        result = await iot_service.record_sensor_data(
            traceability_id=data.get("traceability_id"),
            sensor_readings=data.get("sensor_readings")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error recording sensor data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/traceability/report/{listing_id}")
async def get_traceability_report(listing_id: str, request: Request):
    """Get comprehensive traceability report"""
    try:
        iot_service = request.app.state.iot_service
        
        result = await iot_service.get_traceability_report(listing_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting traceability report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== ESG ENDPOINTS =====

@app.post("/api/v1/esg/calculate-score")
async def calculate_esg_score(request: Request):
    """Calculate ESG score"""
    try:
        data = await request.json()
        esg_service = request.app.state.esg_service
        
        result = await esg_service.calculate_esg_score(
            user_id=data.get("user_id"),
            listing_id=data.get("listing_id"),
            environmental_data=data.get("environmental_data"),
            social_data=data.get("social_data"),
            governance_data=data.get("governance_data")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error calculating ESG score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/esg/dashboard/{user_id}")
async def get_esg_dashboard(user_id: str, request: Request):
    """Get ESG dashboard"""
    try:
        esg_service = request.app.state.esg_service
        
        result = await esg_service.get_esg_dashboard(user_id)
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting ESG dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== COMPLIANCE ENDPOINTS =====

@app.post("/api/v1/compliance/generate-export-form")
async def generate_export_form(request: Request):
    """Generate ECX export form"""
    try:
        data = await request.json()
        ecx_service = request.app.state.ecx_service
        
        result = await ecx_service.generate_ecx_export_form(
            listing_id=data.get("listing_id"),
            exporter_id=data.get("exporter_id"),
            form_data=data
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error generating export form: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/compliance/anti-smuggling-check")
async def anti_smuggling_check(request: Request):
    """Submit anti-smuggling verification"""
    try:
        data = await request.json()
        ecx_service = request.app.state.ecx_service
        
        result = await ecx_service.submit_anti_smuggling_check(
            listing_id=data.get("listing_id"),
            origin_data=data.get("origin_data"),
            certificate_data=data.get("certificate_data")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in anti-smuggling check: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "message": f"Endpoint {request.url.path} not found"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": "Something went wrong"}
    )

@app.exception_handler(429)
async def rate_limit_handler(request: Request, exc):
    return JSONResponse(
        status_code=429,
        content={"error": "Rate limit exceeded", "message": "Too many requests"}
    )

# Run the application
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "production")
    
    logger.info(f"🚀 Starting DEDAN Mine API on {host}:{port}")
    logger.info(f"🌍 Environment: {environment}")
    logger.info(f"🔧 Features: AI Agents, Video Negotiations, Traceability, ESG, ECX Compliance")
    
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=environment == "development",
        log_level="info",
        access_log=True
    )
