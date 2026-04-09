"""
Guardian AI Security Middleware - DEDAN Mine
Monitors all requests and flags suspicious activity
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import json
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from services.guardian import guardian_agent
from services.reputation import reputation_oracle

class GuardianMiddleware(BaseHTTPMiddleware):
    """Security middleware that monitors all user activity"""
    
    def __init__(self, app):
        super().__init__(app)
        self.high_risk_endpoints = [
            "/api/v1/transactions/create",
            "/api/v1/listings/create",
            "/api/v1/auctions/bid",
            "/api/v1/users/update-profile"
        ]
        
        self.medium_risk_endpoints = [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/wallet/withdraw"
        ]
    
    async def dispatch(self, request: Request, call_next):
        """Process request through Guardian AI monitoring"""
        try:
            # Skip monitoring for health checks and docs
            if self._should_skip_monitoring(request.url.path):
                return await call_next(request)
            
            # Extract user information
            user_id = await self._extract_user_id(request)
            if not user_id:
                return await call_next(request)
            
            # Prepare activity data for Guardian AI
            activity_data = await self._prepare_activity_data(request)
            
            # Monitor activity with Guardian AI
            guardian_result = await guardian_agent.monitor_user_activity(
                user_id=user_id,
                activity_data=activity_data
            )
            
            # Check if activity should be blocked
            if self._should_block_activity(guardian_result):
                return self._create_security_response(guardian_result)
            
            # Add security headers to response
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Guardian-Monitored"] = "true"
            response.headers["X-Risk-Score"] = str(guardian_result.get("risk_score", 0))
            
            if guardian_result.get("risk_score", 0) >= 60:
                response.headers["X-Security-Alert"] = "true"
            
            return response
            
        except Exception as e:
            # Log error but don't block requests on middleware failure
            print(f"Guardian middleware error: {e}")
            return await call_next(request)
    
    def _should_skip_monitoring(self, path: str) -> bool:
        """Determine if path should be skipped from monitoring"""
        skip_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/favicon.ico",
            "/static"
        ]
        
        return any(path.startswith(skip_path) for skip_path in skip_paths)
    
    async def _extract_user_id(self, request: Request) -> Optional[str]:
        """Extract user ID from request"""
        try:
            # Try to get from Authorization header
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # This would decode JWT token to get user_id
                # For now, return mock user_id
                return "mock_user_id"
            
            # Try to get from session
            session_data = getattr(request.state, 'session', {})
            if 'user_id' in session_data:
                return session_data['user_id']
            
            # Try to get from request body (for testing)
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                    if "user_id" in body:
                        return body["user_id"]
                    if "seller_id" in body:
                        return body["seller_id"]
                    if "buyer_id" in body:
                        return body["buyer_id"]
                except:
                    pass
            
            return None
            
        except Exception as e:
            print(f"Error extracting user ID: {e}")
            return None
    
    async def _prepare_activity_data(self, request: Request) -> Dict[str, Any]:
        """Prepare activity data for Guardian AI analysis"""
        try:
            activity_data = {
                "activity_type": self._get_activity_type(request),
                "endpoint": request.url.path,
                "method": request.method,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_agent": request.headers.get("user-agent", ""),
                "ip_address": self._get_client_ip(request),
                "request_size": request.headers.get("content-length", "0")
            }
            
            # Add request-specific data
            if request.method in ["POST", "PUT", "PATCH"]:
                try:
                    body = await request.json()
                    
                    # Extract relevant data based on endpoint
                    if "/transactions/" in request.url.path:
                        activity_data.update({
                            "amount": body.get("amount", 0),
                            "recipient": body.get("recipient_id", ""),
                            "payment_method": body.get("payment_method", "")
                        })
                    
                    elif "/listings/" in request.url.path:
                        activity_data.update({
                            "listing_type": body.get("listing_type", ""),
                            "category": body.get("category", ""),
                            "price": body.get("price", 0),
                            "weight": body.get("weight", 0)
                        })
                    
                    elif "/auctions/" in request.url.path:
                        activity_data.update({
                            "bid_amount": body.get("amount", 0),
                            "auction_id": body.get("auction_id", "")
                        })
                    
                    elif "/auth/login" in request.url.path:
                        activity_data.update({
                            "login_method": body.get("method", "password"),
                            "location": body.get("location", {})
                        })
                        
                except Exception as e:
                    print(f"Error parsing request body: {e}")
            
            return activity_data
            
        except Exception as e:
            print(f"Error preparing activity data: {e}")
            return {
                "activity_type": "unknown",
                "endpoint": request.url.path,
                "method": request.method,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }
    
    def _get_activity_type(self, request: Request) -> str:
        """Determine activity type based on endpoint and method"""
        path = request.url.path
        method = request.method
        
        if "/auth/login" in path:
            return "login"
        elif "/auth/register" in path:
            return "registration"
        elif "/transactions/" in path and method == "POST":
            return "transaction"
        elif "/listings/" in path and method == "POST":
            return "listing"
        elif "/auctions/" in path and method == "POST":
            return "bid"
        elif "/wallet/withdraw" in path:
            return "withdrawal"
        elif "/users/update" in path:
            return "profile_update"
        else:
            return "general"
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request"""
        # Check for forwarded IP
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fall back to client IP
        return request.client.host if request.client else "unknown"
    
    def _should_block_activity(self, guardian_result: Dict[str, Any]) -> bool:
        """Determine if activity should be blocked based on Guardian AI result"""
        risk_score = guardian_result.get("risk_score", 0)
        alerts = guardian_result.get("alerts", [])
        
        # Block high-risk activities
        if risk_score >= 80:
            return True
        
        # Block activities with critical alerts
        critical_alerts = [
            "HIGH RISK",
            "IMMEDIATE SECURITY REVIEW",
            "UNUSUAL LARGE TRANSACTION",
            "MULTIPLE FAILED ATTEMPTS"
        ]
        
        for alert in alerts:
            if any(critical in alert.upper() for critical in critical_alerts):
                return True
        
        return False
    
    def _create_security_response(self, guardian_result: Dict[str, Any]) -> JSONResponse:
        """Create security response for blocked activity"""
        return JSONResponse(
            status_code=403,
            content={
                "error": "Security Alert",
                "message": "Activity blocked by Guardian AI security system",
                "risk_score": guardian_result.get("risk_score", 0),
                "alerts": guardian_result.get("alerts", []),
                "recommendations": guardian_result.get("recommendations", []),
                "requires_verification": True,
                "contact_support": True
            },
            headers={
                "X-Guardian-Blocked": "true",
                "X-Risk-Score": str(guardian_result.get("risk_score", 0)),
                "X-Security-Alert": "true"
            }
        )
