"""
Minimal test app for Render deployment
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
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
    allowed_hosts=["worldmine.vercel.app", "*.vercel.app", "localhost", "127.0.0.1"]
)

# Add gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"📊 {request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
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
def read_root():
    return {"status": "online", "platform": "Worldmine AI"}

# Simple analyze endpoint
@app.post("/analyze")
async def analyze_news(request: Request):
    """Analyze news articles and extract insights"""
    try:
        data = await request.json()
        
        if not data.get("content"):
            raise HTTPException(status_code=400, detail="Content is required")
        
        # Simple analysis
        content = data["content"]
        word_count = len(content.split())
        char_count = len(content)
        
        # Simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'positive', 'growth', 'increase']
        negative_words = ['bad', 'terrible', 'negative', 'decline', 'decrease', 'loss']
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        sentiment = 'neutral'
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        
        return {
            "success": True,
            "data": {
                "category": "General",
                "analysis": f"Text contains {word_count} words with {sentiment} sentiment.",
                "word_count": word_count,
                "sentiment": sentiment,
                "priority": 1
            },
            "errors": []
        }
        
    except Exception as e:
        logger.error(f"Error in analyze endpoint: {e}")
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

# Run the application
if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")
    
    logger.info(f"🚀 Starting Worldmine AI Agent API on {host}:{port}")
    logger.info(f"🌍 Environment: {environment}")
    
    uvicorn.run(
        "test_app:app",
        host=host,
        port=port,
        reload=environment == "development",
        log_level="info",
        access_log=True
    )
