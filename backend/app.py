"""
DEDAN Mine (Worldmine) - Enhanced FastAPI Application
Production-ready API with core marketplace + future-tech features + Guardian AI
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

# Import core services
from services.marketplace.listings import ListingService
from services.ai_agents.tradingAgent import AutonomousTradingAgent
from services.video_negotiation.videoStreaming import VideoNegotiationService
from services.traceability.iotSensors import IoTSensorService
from services.esg.scoring import ESGScoringService
from services.compliance.ecxIntegration import ECXComplianceService
from services.security.quantumEncryption import QuantumSecureData

# NEW: Import DEDAN Mine core features
from services.guardian import guardian_agent
from services.reputation import reputation_oracle
from services.agents import agent_marketplace
from middleware.GuardianMiddleware import GuardianMiddleware
from schemas import SecureUserRegistration, SecureUserLogin, SecureTransaction, ZeroKnowledgeShield

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
    logger.info("🚀 DEDAN Mine API starting up...")
    
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
    
    logger.info("🛑 DEDAN Mine API shutting down...")

# Create FastAPI application
app = FastAPI(
    title="DEDAN Mine - AI-Powered Global Mining Marketplace",
    description="World's most advanced AI-powered mining transaction marketplace with autonomous agents, video negotiations, Guardian AI security, and agent marketplace",
    version="2.1.0",
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

# Add Guardian AI security middleware
app.add_middleware(GuardianMiddleware)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware with PII protection
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing and PII protection"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    
    # Safe logging without PII
    safe_log_data = {
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "time": f"{process_time:.3f}s",
        "origin": request.headers.get("origin", "unknown")
    }
    
    logger.info(f"📊 Request: {ZeroKnowledgeShield.safe_log(safe_log_data, 'request_data')}")
    
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
        "platform": "DEDAN Mine AI",
        "version": "2.1.0",
        "features": [
            "Autonomous AI Trading Agents",
            "Live Video Negotiations",
            "Mine-to-Market Traceability",
            "ESG & Carbon Credits",
            "ECX Compliance",
            "Quantum-Resistant Security",
            "Guardian AI Security Layer",
            "Behavioral Reputation Oracle",
            "Evolving Agent Marketplace",
            "Zero-Knowledge User Shield"
        ]
    }

# ===== CORE MARKETPLACE ENDPOINTS =====

@app.post("/api/v1/listings/create")
async def create_listing(request: Request):
    """Create listing with progressive feature support"""
    try:
        data = await request.json()
        listing_service = request.app.state.listing_service
        
        result = await listing_service.create_listing(
            seller_id=data.get("seller_id"),
            title=data.get("title"),
            description=data.get("description"),
            category=data.get("category"),
            gem_type=data.get("gem_type"),
            weight=data.get("weight"),
            unit=data.get("unit"),
            price=data.get("price"),
            listing_type=data.get("listing_type"),
            images=data.get("images"),
            buy_it_now_price=data.get("buy_it_now_price"),
            reserve_price=data.get("reserve_price"),
            auction_end_time=datetime.fromisoformat(data["auction_end_time"]) if data.get("auction_end_time") else None,
            # Future features
            enable_traceability=data.get("enable_traceability", False),
            enable_video_negotiation=data.get("enable_video_negotiation", False),
            ai_agent_managed=data.get("ai_agent_managed", False),
            esg_monitored=data.get("esg_monitored", False),
            mine_location=data.get("mine_location")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creating listing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/listings/browse")
async def browse_listings(request: Request):
    """Browse listings with advanced filtering"""
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
        logger.error(f"Error browsing listings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/listings/{listing_id}")
async def get_listing_details(listing_id: str, request: Request):
    """Get detailed listing information"""
    try:
        listing_service = request.app.state.listing_service
        result = await listing_service.get_listing_details(listing_id)
        return result
        
    except Exception as e:
        logger.error(f"Error getting listing details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auctions/{listing_id}/bid")
async def place_bid(listing_id: str, request: Request):
    """Place bid with quantum-resistant security"""
    try:
        data = await request.json()
        listing_service = request.app.state.listing_service
        
        result = await listing_service.place_bid(
            auction_id=listing_id,
            bidder_id=data.get("bidder_id"),
            amount=data.get("amount"),
            max_proxy_amount=data.get("max_proxy_amount"),
            quantum_signature=data.get("quantum_signature")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error placing bid: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/listings/{listing_id}/buy-now")
async def buy_it_now(listing_id: str, request: Request):
    """Execute Buy-It-Now transaction with dynamic fee"""
    try:
        data = await request.json()
        listing_service = request.app.state.listing_service
        
        # Get dynamic fee rate based on reputation
        buyer_id = data.get("buyer_id")
        fee_result = await reputation_oracle.get_platform_fee_rate(buyer_id)
        
        if not fee_result["success"]:
            raise HTTPException(status_code=400, detail=fee_result["error"])
        
        result = await listing_service.buy_it_now(
            listing_id=listing_id,
            buyer_id=buyer_id,
            payment_method=data.get("payment_method", "stripe"),
            fee_rate=fee_result["adjusted_fee_rate"]
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in Buy-It-Now: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ===== NEW: DEDAN MINE CORE FEATURES =====

# Guardian AI Security Layer
@app.post("/api/v1/guardian/monitor")
async def monitor_activity(request: Request):
    """Manual Guardian AI monitoring endpoint"""
    try:
        data = await request.json()
        
        result = await guardian_agent.monitor_user_activity(
            user_id=data.get("user_id"),
            activity_data=data.get("activity_data")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error in Guardian monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Behavioral Reputation Oracle
@app.get("/api/v1/reputation/trust-score/{user_id}")
async def get_trust_score(user_id: str, request: Request):
    """Get user's trust score and fee discount"""
    try:
        result = await reputation_oracle.calculate_trust_score(user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating trust score: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/reputation/platform-fee/{user_id}")
async def get_platform_fee(user_id: str, request: Request):
    """Get dynamic platform fee rate for user"""
    try:
        result = await reputation_oracle.get_platform_fee_rate(user_id)
        return result
        
    except Exception as e:
        logger.error(f"Error calculating platform fee: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Evolving Agent Marketplace
@app.post("/api/v1/agents/list")
async def list_agent_for_rental(request: Request):
    """List an agent for rental in the marketplace"""
    try:
        data = await request.json()
        
        result = await agent_marketplace.list_agent_for_rental(
            owner_id=data.get("owner_id"),
            agent_type=data.get("agent_type"),
            rental_price_per_hour=data.get("rental_price_per_hour"),
            min_rental_hours=data.get("min_rental_hours", 1),
            max_rental_hours=data.get("max_rental_hours", 168),
            description=data.get("description", "")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/rent")
async def rent_agent(request: Request):
    """Rent an agent from the marketplace"""
    try:
        data = await request.json()
        
        result = await agent_marketplace.rent_agent(
            renter_id=data.get("renter_id"),
            agent_id=data.get("agent_id"),
            rental_duration_hours=data.get("rental_duration_hours"),
            payment_method=data.get("payment_method"),
            terms_accepted=data.get("terms_accepted", False)
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error renting agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/available")
async def get_available_agents(request: Request):
    """Get list of available agents for rental"""
    try:
        result = await agent_marketplace.get_available_agents(
            agent_type=request.query_params.get("agent_type"),
            max_price_per_hour=float(request.query_params.get("max_price_per_hour")) if request.query_params.get("max_price_per_hour") else None,
            min_experience_points=int(request.query_params.get("min_experience_points")) if request.query_params.get("min_experience_points") else None,
            sort_by=request.query_params.get("sort_by", "experience_points"),
            sort_order=request.query_params.get("sort_order", "desc")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting available agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/agents/my-rentals/{user_id}")
async def get_user_rented_agents(user_id: str, request: Request):
    """Get agents rented by a user"""
    try:
        result = await agent_marketplace.get_user_rented_agents(
            user_id=user_id,
            status=request.query_params.get("status")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting user rentals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/agents/end-rental/{rental_id}")
async def end_rental(rental_id: str, request: Request):
    """End an active rental and update agent"""
    try:
        data = await request.json()
        
        result = await agent_marketplace.end_rental(
            rental_id=rental_id,
            renter_id=data.get("renter_id"),
            rating=data.get("rating"),
            review=data.get("review")
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error ending rental: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Zero-Knowledge User Shield Endpoints
@app.post("/api/v1/auth/register")
async def secure_register(request: Request):
    """Secure user registration with PII protection"""
    try:
        # Use secure schema with SecretStr
        user_data = SecureUserRegistration(**await request.json())
        
        # Safe logging without exposing PII
        logger.info(f"📝 New registration: {ZeroKnowledgeShield.safe_log({'username': user_data.username, 'email': user_data.email}, 'registration_data')}")
        
        # Process registration (implementation would go here)
        # Note: user_data.password.get_secret_value() for actual password processing
        
        return {
            "success": True,
            "message": "User registration successful",
            "user_id": str(uuid.uuid4())  # Mock user ID
        }
        
    except Exception as e:
        logger.error(f"Error in secure registration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/auth/login")
async def secure_login(request: Request):
    """Secure user login with PII protection"""
    try:
        # Use secure schema with SecretStr
        login_data = SecureUserLogin(**await request.json())
        
        # Safe logging without exposing password
        logger.info(f"🔐 Login attempt: {ZeroKnowledgeShield.safe_log({'email': login_data.email, 'method': login_data.login_method}, 'login_data')}")
        
        # Process login (implementation would go here)
        # Note: login_data.password.get_secret_value() for actual password verification
        
        return {
            "success": True,
            "message": "Login successful",
            "token": "mock_jwt_token",  # Mock token
            "user_id": str(uuid.uuid4())   # Mock user ID
        }
        
    except Exception as e:
        logger.error(f"Error in secure login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/transactions/create")
async def secure_transaction(request: Request):
    """Secure transaction creation with PII protection"""
    try:
        # Use secure schema with SecretStr for sensitive data
        transaction_data = SecureTransaction(**await request.json())
        
        # Safe logging without exposing sensitive payment info
        safe_data = {
            'amount': transaction_data.amount,
            'recipient_id': transaction_data.recipient_id,
            'payment_method': transaction_data.payment_method
        }
        logger.info(f"💳 New transaction: {ZeroKnowledgeShield.safe_log(safe_data, 'transaction_data')}")
        
        # Process transaction (implementation would go here)
        # Note: transaction_data.card_number.get_secret_value() for actual processing
        
        return {
            "success": True,
            "message": "Transaction created successfully",
            "transaction_id": str(uuid.uuid4())  # Mock transaction ID
        }
        
    except Exception as e:
        logger.error(f"Error in secure transaction: {e}")
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
