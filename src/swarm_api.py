"""
Swarm API - Backend API for Swarm Controller
Provides REST endpoints for swarm operations and status monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, List
import asyncio
from datetime import datetime
import sys
import os

# Add src to path for swarm imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from swarm.swarm_controller import swarm_controller

class SwarmStatusResponse(BaseModel):
    timestamp: str
    swarm_metrics: Dict[str, Any]
    agent_status: Dict[str, Any]
    global_reach: Dict[str, Any]
    operational_status: Dict[str, Any]

class SwarmStartResponse(BaseModel):
    message: str
    status: str
    agents_started: List[str]

# Create FastAPI app for swarm operations
swarm_app = FastAPI(title="DEDAN Swarm API", version="1.0.0")

@swarm_app.get("/api/swarm/status", response_model=SwarmStatusResponse)
async def get_swarm_status():
    """Get comprehensive swarm status"""
    try:
        status = await swarm_controller.get_swarm_status()
        return JSONResponse(content=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@swarm_app.post("/api/swarm/start", response_model=SwarmStartResponse)
async def start_swarm_operations():
    """Start all swarm operations"""
    try:
        # Start swarm operations in background
        asyncio.create_task(swarm_controller.start_swarm_operations())
        
        return SwarmStartResponse(
            message="Swarm operations started successfully",
            status="initializing",
            agents_started=["global_voice", "growth_hacker", "legal_architect", "b2b_negotiator"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@swarm_app.post("/api/swarm/emergency-restart", response_model=SwarmStartResponse)
async def emergency_restart_swarm():
    """Emergency restart of swarm operations"""
    try:
        # Emergency restart
        asyncio.create_task(swarm_controller.emergency_restart_swarm())
        
        return SwarmStartResponse(
            message="Emergency restart initiated",
            status="restarting",
            agents_started=["global_voice", "growth_hacker", "legal_architect", "b2b_negotiator"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@swarm_app.get("/api/swarm/metrics")
async def get_detailed_metrics():
    """Get detailed swarm metrics"""
    try:
        status = await swarm_controller.get_swarm_status()
        return JSONResponse(content={
            "detailed_metrics": status["swarm_metrics"],
            "agent_performance": status["agent_status"],
            "global_impact": status["global_reach"],
            "system_health": status["operational_status"]
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(swarm_app, host="0.0.0.0", port=8001)
