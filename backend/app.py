"""
Worldmine FastAPI Application with CORS Configuration
Production-ready API server for AI agent services
"""

import os
import time
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import uvicorn
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from cors_config import configure_cors, validate_cors_origin, add_security_headers
from main import MarketNewsAgent, AgentState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Worldmine AI Agent API starting up...")
    
    # Initialize any startup resources
    yield
    
    logger.info("🛑 Worldmine AI Agent API shutting down...")

# Create FastAPI application
app = FastAPI(
    title="Worldmine AI Agent API",
    description="AI-powered market analysis and news processing for Worldmine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
configure_cors(app)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add security headers middleware
@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to all responses"""
    return await add_security_headers(request, call_next)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["worldmine.vercel.app", "*.vercel.app", "localhost", "127.0.0.1"]
)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    # Validate origin
    origin = request.headers.get("origin")
    if origin and not validate_cors_origin(origin):
        logger.warning(f"🚫 Blocked request from unauthorized origin: {origin}")
        return JSONResponse(
            status_code=403,
            content={
                "error": "Origin not allowed",
                "message": "This origin is not allowed to access this API"
            }
        )
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"📊 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s - "
        f"Origin: {origin}"
    )
    
    return response

# Health check endpoint
@app.get("/health")
@limiter.limit("100/minute")
async def health_check():
    """Health check endpoint for Render keep-alive"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "service": "worldmine-ai-agent",
        "uptime": time.time(),
        "environment": os.getenv("ENVIRONMENT", "production")
    }

# API Health endpoint (alternative path)
@app.get("/api/health")
@limiter.limit("100/minute")
async def api_health_check():
    """API health check endpoint for frontend keep-alive"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "service": "worldmine-api",
        "message": "Worldmine API is operational"
    }

# Root endpoint
@app.get("/")
@limiter.limit("100/minute")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Worldmine AI Agent API",
        "version": "1.0.0",
        "description": "AI-powered market analysis and news processing",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "redoc": "/redoc",
            "analyze": "/analyze",
            "chat": "/chat",
            "translate": "/translate",
            "news": "/news"
        },
        "status": "operational"
    }

# News analysis endpoint
@app.post("/analyze")
@limiter.limit("30/minute")
async def analyze_news(request: Request):
    """Analyze news articles and extract insights"""
    try:
        # Get request data
        data = await request.json()
        
        # Validate required fields
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Initialize agent
        agent = MarketNewsAgent()
        
        # Create state for analysis
        state = AgentState(
            search_queries=[],
            raw_news=[{
                "title": data.get("title", ""),
                "content": data["content"],
                "url": data.get("url", ""),
                "published_date": data.get("published_date", ""),
                "query": "manual_analysis"
            }],
            processed_news=[],
            posted_news=[],
            errors=[]
        )
        
        # Run analysis
        processed_state = await agent.analyze_news(state)
        
        # Return results
        return {
            "success": True,
            "data": {
                "category": processed_state.processed_news[0].category if processed_state.processed_news else "Unknown",
                "analysis": processed_state.processed_news[0].analysis if processed_state.processed_news else "",
                "analysis_am": processed_state.processed_news[0].analysis_am if processed_state.processed_news else "",
                "price_trend": processed_state.processed_news[0].price_trend if processed_state.processed_news else None,
                "priority": processed_state.processed_news[0].priority if processed_state.processed_news else 1
            },
            "errors": processed_state.errors
        }
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
@limiter.limit("60/minute")
async def chat_with_ai(request: Request):
    """Chat with AI assistant"""
    try:
        data = await request.json()
        
        if not data.get("message"):
            raise HTTPException(status_code=400, detail="Message is required")
        
        # For now, return a simple response
        # In production, integrate with actual AI model
        return {
            "success": True,
            "response": f"I received your message: {data['message']}",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Translate endpoint
@app.post("/translate")
@limiter.limit("100/minute")
async def translate_text(request: Request):
    """Translate text to Amharic"""
    try:
        data = await request.json()
        
        if not data.get("text"):
            raise HTTPException(status_code=400, detail="Text is required")
        
        # For now, return a placeholder
        # In production, integrate with Google Translate API
        return {
            "success": True,
            "original": data["text"],
            "translated": f"[Amharic: {data['text'][:100]}...]",
            "language": "amharic",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Error in translate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# News processing endpoint
@app.post("/news/process")
@limiter.limit("10/minute")
async def process_news(request: Request):
    """Process news articles and post to database"""
    try:
        # Initialize agent
        agent = MarketNewsAgent()
        graph = agent.create_graph()
        
        # Run the full workflow
        result = await graph.ainvoke(AgentState(
            search_queries=agent.search_queries,
            raw_news=[],
            processed_news=[],
            posted_news=[],
            errors=[]
        ))
        
        return {
            "success": True,
            "summary": {
                "raw_news_found": len(result.raw_news),
                "news_processed": len(result.processed_news),
                "news_posted": len(result.posted_news),
                "errors": len(result.errors)
            },
            "errors": result.errors
        }
        
    except Exception as e:
        logger.error(f"Error in news processing endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Metrics endpoint
@app.get("/metrics")
@limiter.limit("100/minute")
async def get_metrics():
    """Get API metrics and status"""
    return {
        "status": "operational",
        "uptime": time.time(),
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze",
            "chat": "/chat",
            "translate": "/translate",
            "news/process": "/news/process"
        },
        "rate_limits": {
            "analyze": "30/minute",
            "chat": "60/minute",
            "translate": "100/minute",
            "news/process": "10/minute",
            "default": "100/minute"
        },
        "cors": {
            "allowed_origins": ["https://worldmine.vercel.app"],
            "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_credentials": True
        }
    }

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
    # Get environment variables
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    logger.info(f"🚀 Starting Worldmine AI Agent API on {host}:{port}")
    logger.info(f"🌍 Environment: {environment}")
    
    # Run with uvicorn
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        reload=environment == "development",
        log_level="info",
        access_log=True,
        ssl_keyfile=None,  # Add SSL cert path for production
        ssl_certfile=None,  # Add SSL cert path for production
    )
