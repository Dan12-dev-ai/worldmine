"""
Simplified Worldmine FastAPI Application for Render Free Tier
Production-ready API server with essential functionality only
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

from cors_config import configure_cors, validate_cors_origin, add_security_headers
from main_simple import SimpleMarketNewsAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
async def root():
    return {"status": "online", "platform": "Worldmine AI"}

# News analysis endpoint
@app.post("/analyze")
async def analyze_news(request: Request):
    """Analyze news articles and extract insights"""
    try:
        # Get request data
        data = await request.json()
        
        # Validate required fields
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Initialize simple agent
        agent = SimpleMarketNewsAgent()
        
        # Run simple analysis
        analysis = await agent.analyze_simple_text(data["content"])
        
        # Return results
        return {
            "success": True,
            "data": {
                "category": "General",
                "analysis": analysis.get("analysis", ""),
                "word_count": analysis.get("word_count", 0),
                "sentiment": analysis.get("sentiment", "neutral"),
                "priority": 1
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
async def chat_with_ai(request: Request):
    """Chat with AI assistant"""
    try:
        data = await request.json()
        
        if not data.get("message"):
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Simple response for now
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
async def translate_text(request: Request):
    """Translate text to Amharic"""
    try:
        data = await request.json()
        
        if not data.get("text"):
            raise HTTPException(status_code=400, detail="Text is required")
        
        # Simple placeholder translation
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
async def process_news(request: Request):
    """Process news articles and post to database"""
    try:
        # Initialize simple agent
        agent = SimpleMarketNewsAgent()
        
        # Get basic news
        news = await agent.get_basic_news()
        
        return {
            "success": True,
            "summary": {
                "news_found": len(news),
                "news_processed": len(news),
                "news_posted": 0,
                "errors": 0
            },
            "data": news[:5],  # Return first 5 news items
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Error in news processing endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Metrics endpoint
@app.get("/metrics")
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
