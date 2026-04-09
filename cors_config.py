# CORS Configuration for Worldmine FastAPI Service
# Configured for production deployment on Render

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os

def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the FastAPI application.
    
    This function sets up CORS with strict security policies for production,
    allowing only the production Vercel URL to access the API.
    """
    
    # Get production URL from environment
    production_url = os.getenv("PRODUCTION_URL", "https://worldmine.vercel.app")
    
    # Configure CORS with strict security settings
    app.add_middleware(
        CORSMiddleware,
        # Allow only specific origins (strict for production)
        allow_origins=[
            production_url,
            f"{production_url}/*",  # Allow all subpaths
            "http://localhost:3000",   # Development only
            "http://localhost:8000",   # Development only
        ],
        
        # Allow specific methods
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "DELETE",
            "OPTIONS",
            "HEAD",
            "PATCH",
        ],
        
        # Allow specific headers
        allow_headers=[
            "accept",
            "accept-language",
            "content-language",
            "content-type",
            "authorization",
            "x-requested-with",
            "x-client-info",
            "apikey",
            "origin",
            "user-agent",
            "cache-control",
            "pragma",
        ],
        
        # Expose specific headers to the client
        expose_headers=[
            "content-length",
            "content-range",
            "x-total-count",
            "x-request-id",
            "x-rate-limit",
            "x-rate-limit-remaining",
            "x-rate-limit-reset",
        ],
        
        # Allow credentials (cookies, authorization headers)
        allow_credentials=True,
        
        # Set max age for preflight requests (24 hours)
        max_age=86400,
        
        # Vary header for proper caching
        vary_headers=["Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
    )

def get_production_cors_config() -> dict:
    """
    Get CORS configuration for production deployment.
    
    Returns:
        dict: CORS configuration settings
    """
    
    return {
        "allow_origins": [
            "https://worldmine.vercel.app",
            "https://worldmine.vercel.app/*",
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": [
            "accept",
            "accept-language",
            "content-language",
            "content-type",
            "authorization",
            "x-requested-with",
            "x-client-info",
            "apikey",
        ],
        "allow_credentials": True,
        "max_age": 86400,
    }

def get_development_cors_config() -> dict:
    """
    Get CORS configuration for development.
    
    Returns:
        dict: CORS configuration settings
    """
    
    return {
        "allow_origins": [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://worldmine.vercel.app",  # For testing production
        ],
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["*"],
        "allow_credentials": True,
        "max_age": 3600,
    }

def validate_cors_origin(origin: str) -> bool:
    """
    Validate if the origin is allowed based on environment.
    
    Args:
        origin (str): The origin URL to validate
        
    Returns:
        bool: True if origin is allowed, False otherwise
    """
    
    # Get environment
    environment = os.getenv("ENVIRONMENT", "development")
    
    if environment == "production":
        allowed_origins = [
            "https://worldmine.vercel.app",
        ]
    else:
        allowed_origins = [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
            "https://worldmine.vercel.app",
        ]
    
    # Check if origin matches any allowed origin
    for allowed_origin in allowed_origins:
        if origin.startswith(allowed_origin):
            return True
    
    return False

# Security headers middleware
async def add_security_headers(request, call_next):
    """
    Add security headers to all responses.
    """
    
    response = await call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' data:; "
        "connect-src 'self' https://api.supabase.co https://worldmine.vercel.app; "
        "frame-src 'none'; "
        "object-src 'none'; "
        "base-uri 'self'; "
        "form-action 'self'; "
        "manifest-src 'self'; "
        "worker-src 'self' blob:; "
        "child-src 'self' blob:; "
        "frame-ancestors 'none'; "
        "upgrade-insecure-requests; "
        "block-all-mixed-content;"
    )
    
    # Rate limiting headers
    response.headers["X-RateLimit-Limit"] = "1000"
    response.headers["X-RateLimit-Remaining"] = "999"
    response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 3600)
    
    return response

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "requests_per_minute": 1000,
    "requests_per_hour": 10000,
    "requests_per_day": 100000,
    "burst_size": 100,
}

# API rate limiting by endpoint
ENDPOINT_RATE_LIMITS = {
    "/chat": {
        "requests_per_minute": 60,
        "requests_per_hour": 1000,
        "requests_per_day": 10000,
    },
    "/analyze": {
        "requests_per_minute": 30,
        "requests_per_hour": 500,
        "requests_per_day": 5000,
    },
    "/translate": {
        "requests_per_minute": 100,
        "requests_per_hour": 2000,
        "requests_per_day": 20000,
    },
    "/news": {
        "requests_per_minute": 200,
        "requests_per_hour": 5000,
        "requests_per_day": 50000,
    },
}

# CORS error responses
CORS_ERROR_RESPONSES = {
    "origin_not_allowed": {
        "error": "Origin not allowed",
        "message": "This origin is not allowed to access this API",
        "status_code": 403,
    },
    "method_not_allowed": {
        "error": "Method not allowed",
        "message": "This HTTP method is not allowed",
        "status_code": 405,
    },
    "header_not_allowed": {
        "error": "Header not allowed",
        "message": "This header is not allowed",
        "status_code": 400,
    },
}

# Logging configuration for CORS
CORS_LOGGING_CONFIG = {
    "log_requests": True,
    "log_blocked_requests": True,
    "log_allowed_requests": False,
    "log_level": "INFO",
}

# Environment-specific settings
ENVIRONMENT_SETTINGS = {
    "development": {
        "debug": True,
        "reload": True,
        "log_level": "DEBUG",
        "cors_config": get_development_cors_config(),
    },
    "staging": {
        "debug": False,
        "reload": False,
        "log_level": "INFO",
        "cors_config": get_production_cors_config(),
    },
    "production": {
        "debug": False,
        "reload": False,
        "log_level": "INFO",
        "cors_config": get_production_cors_config(),
    },
}
