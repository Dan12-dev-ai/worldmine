"""
FastAPI Endpoints for Universal Payout Orchestrator
Ethiopian Sovereign Payout Gateway - NBE 2026 Compliant
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import asyncio
import logging
import uvicorn

from .orchestrator import (
    UniversalPayoutOrchestrator,
    PayoutRequest,
    PayoutRail,
    PayoutStatus,
    payout_orchestrator,
    security_guardian,
    compliance_tracker
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="DEDAN Mine - Universal Payout Orchestrator",
    description="Ethiopian Sovereign Payout Gateway - NBE 2026 Compliant",
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
class PayoutRequestModel(BaseModel):
    """Payout request model"""
    user_id: str = Field(..., description="User ID")
    amount: float = Field(..., gt=0, description="Payout amount")
    currency: str = Field(..., description="Currency code")
    rail: str = Field(..., description="Payout rail")
    destination: Dict[str, Any] = Field(..., description="Destination details")
    biometric_hash: Optional[str] = Field(None, description="Biometric hash")
    ip_address: Optional[str] = Field(None, description="IP address")
    device_fingerprint: Optional[str] = Field(None, description="Device fingerprint")
    satellite_provenance: Optional[str] = Field(None, description="Satellite provenance hash")

class PayoutResponse(BaseModel):
    """Payout response model"""
    success: bool
    transaction_id: Optional[str] = None
    status: Optional[str] = None
    rail: Optional[str] = None
    method: Optional[str] = None
    processed_at: Optional[str] = None
    estimated_settlement: Optional[str] = None
    error: Optional[str] = None
    compliance_info: Optional[Dict[str, Any]] = None

class TaxCalculationRequest(BaseModel):
    """Tax calculation request"""
    amount: float = Field(..., gt=0, description="Amount to calculate taxes for")
    user_type: str = Field("individual", description="User type")

class TaxCalculationResponse(BaseModel):
    """Tax calculation response"""
    gross_amount: float
    mining_royalty: float
    vat: float
    withholding_tax: float
    service_fee: float
    total_deductions: float
    net_amount: float
    tax_rate_breakdown: Dict[str, float]
    compliance_note: str
    calculated_at: str

class ComplianceReportRequest(BaseModel):
    """Compliance report request"""
    user_id: Optional[str] = Field(None, description="User ID (optional)")
    start_date: Optional[str] = Field(None, description="Start date (ISO format)")
    end_date: Optional[str] = Field(None, description="End date (ISO format)")

# Middleware for IP and device tracking
async def get_request_info(request):
    """Extract request information"""
    return {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
        "device_fingerprint": request.headers.get("x-device-fingerprint")
    }

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from token"""
    # Mock authentication - implement real JWT validation
    if not credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Validate token (mock)
    if credentials.credentials != "valid_token":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return {"user_id": "demo_user", "permissions": ["payout"]}

# Health check
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Universal Payout Orchestrator",
        "version": "2.0.0",
        "nbe_compliance": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "rails": [rail.value for rail in PayoutRail],
        "supported_currencies": ["ETB", "USD", "EUR", "USDT", "USDC", "ETH", "BTC"]
    }

# Tax calculation
@app.post("/tax/calculate", response_model=TaxCalculationResponse, tags=["Tax"])
async def calculate_taxes(request: TaxCalculationRequest):
    """Calculate Ethiopian taxes and fees"""
    try:
        from .orchestrator import EthiopianTaxOracle
        tax_oracle = EthiopianTaxOracle()
        result = await tax_oracle.calculate_taxes(request.amount, request.user_type)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TaxCalculationResponse(**result)
        
    except Exception as e:
        logger.error(f"Tax calculation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Payout processing
@app.post("/payout", response_model=PayoutResponse, tags=["Payout"])
async def process_payout(
    request: PayoutRequestModel,
    background_tasks: BackgroundTasks,
    request_info: Dict[str, Any] = Depends(get_request_info),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Process payout request"""
    try:
        # Create payout request
        payout_request = PayoutRequest(
            user_id=current_user["user_id"],
            amount=request.amount,
            currency=request.currency,
            rail=PayoutRail(request.rail),
            destination=request.destination,
            biometric_hash=request.biometric_hash,
            ip_address=request_info["ip_address"],
            device_fingerprint=request_info["device_fingerprint"],
            satellite_provenance=request.satellite_provenance
        )
        
        # Process payout
        result = await payout_orchestrator.process_payout(payout_request)
        
        # Add background task for compliance tracking
        background_tasks.add_task(
            log_compliance_event,
            "payout_processed",
            {
                "user_id": current_user["user_id"],
                "amount": request.amount,
                "rail": request.rail,
                "status": result.get("status")
            }
        )
        
        return PayoutResponse(**result)
        
    except Exception as e:
        logger.error(f"Payout processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Payout status check
@app.get("/payout/{transaction_id}", response_model=PayoutResponse, tags=["Payout"])
async def get_payout_status(
    transaction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get payout status"""
    try:
        # Mock status check - implement real database lookup
        result = {
            "success": True,
            "transaction_id": transaction_id,
            "status": "completed",
            "rail": "local_hub",
            "method": "telebirr",
            "processed_at": datetime.now(timezone.utc).isoformat()
        }
        
        return PayoutResponse(**result)
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Export permit generation
@app.get("/export-permit/{payout_id}", tags=["Compliance"])
async def get_export_permit(
    payout_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get export permit"""
    try:
        # Mock export permit generation
        permit_data = {
            "permit_id": f"EXP-{payout_id}",
            "user_id": current_user["user_id"],
            "payout_id": payout_id,
            "satellite_provenance": "satellite_hash_here",
            "nbe_compliance": True,
            "fx_directive": "FXD/04/2026",
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        }
        
        return {
            "success": True,
            "permit_data": permit_data,
            "pdf_url": f"https://dedan.mine/permits/EXP-{payout_id}.pdf",
            "qr_code": f"EXP-{payout_id}"
        }
        
    except Exception as e:
        logger.error(f"Export permit error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Compliance report
@app.post("/compliance/report", tags=["Compliance"])
async def generate_compliance_report(
    request: ComplianceReportRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Generate compliance report"""
    try:
        # Mock compliance report generation
        report = {
            "report_id": f"COMP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_by": current_user["user_id"],
            "period": {
                "start": request.start_date,
                "end": request.end_date
            },
            "total_payouts": 150,
            "total_amount": 2500000.00,
            "total_taxes_collected": 425000.00,
            "nbe_compliance_rate": 100.0,
            "fx_directive_compliance": True,
            "satellite_provenance_coverage": 98.5,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "report": report,
            "download_url": f"https://dedan.mine/reports/COMP-{report['report_id']}.pdf"
        }
        
    except Exception as e:
        logger.error(f"Compliance report error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Supported rails
@app.get("/rails", tags=["Info"])
async def get_supported_rails():
    """Get supported payout rails"""
    return {
        "local_hub": {
            "name": "Local Hub",
            "methods": ["telebirr", "bank_transfer"],
            "supported_banks": [
                "Commercial Bank of Ethiopia (CBE)",
                "Dashen Bank",
                "Awash Bank",
                "Wegagen Bank",
                "Bank of Abyssinia"
            ],
            "biometric_required": True,
            "settlement_time": "instant"
        },
        "institutional_hub": {
            "name": "Institutional Hub",
            "methods": ["payoneer", "swift"],
            "supported_currencies": ["USD", "EUR"],
            "biometric_required": False,
            "settlement_time": "1-3 business days"
        },
        "sovereign_crypto_bridge": {
            "name": "Sovereign Crypto-Bridge",
            "methods": ["web3_wallet"],
            "supported_tokens": [
                {"symbol": "USDT", "network": "BEP-20"},
                {"symbol": "USDC", "network": "BEP-20"},
                {"symbol": "ETH", "network": "ERC-20"},
                {"symbol": "BTC", "network": "Bitcoin"}
            ],
            "biometric_required": False,
            "nbe_compliance": True,
            "settlement_time": "instant"
        }
    }

# Security check
@app.post("/security/check", tags=["Security"])
async def security_check(
    request: PayoutRequestModel,
    request_info: Dict[str, Any] = Depends(get_request_info),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Perform security check"""
    try:
        payout_request = PayoutRequest(
            user_id=current_user["user_id"],
            amount=request.amount,
            currency=request.currency,
            rail=PayoutRail(request.rail),
            destination=request.destination,
            ip_address=request_info["ip_address"],
            device_fingerprint=request_info["device_fingerprint"]
        )
        
        result = await security_guardian.security_check(payout_request)
        
        return {
            "success": True,
            "security_result": result,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Security check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Biometric verification
@app.post("/biometric/verify", tags=["Security"])
async def verify_biometric(
    biometric_data: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Verify biometric data"""
    try:
        from .orchestrator import LocalHubPayout
        local_hub = LocalHubPayout()
        
        # Mock biometric verification
        result = {
            "verified": True,
            "confidence": 0.95,
            "behavioral_score": 0.92,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return {
            "success": True,
            "verification_result": result
        }
        
    except Exception as e:
        logger.error(f"Biometric verification error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task for compliance logging
async def log_compliance_event(event_type: str, event_data: Dict[str, Any]):
    """Log compliance events"""
    try:
        logger.info(f"Compliance event: {event_type} - {event_data}")
        # In real implementation, store in compliance database
    except Exception as e:
        logger.error(f"Compliance logging error: {str(e)}")

# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Global exception: {str(exc)}")
    return {
        "error": "Internal server error",
        "message": "An unexpected error occurred",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

# Run server
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
