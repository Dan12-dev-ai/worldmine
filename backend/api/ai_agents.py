"""
AI Agent Registry API
Manages registration, discovery, and lifecycle of AI agents in the World-Mine platform
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/ai_agents", tags=["AI Agents"])


# Models
class AgentCapabilities(BaseModel):
    """Agent capabilities and skills"""
    skills: List[str] = Field(default_factory=list)
    max_concurrent_tasks: int = Field(default=1)
    supported_data_types: List[str] = Field(default_factory=list)
    compute_requirements: Dict[str, Any] = Field(default_factory=dict)


class AgentConfig(BaseModel):
    """Agent configuration"""
    model_type: str = Field(description="Type of AI model (e.g., 'gpt-4', 'claude-3')")
    version: str = Field(default="1.0.0")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    resource_limits: Dict[str, Any] = Field(default_factory=dict)


class AgentRegistration(BaseModel):
    """Agent registration request"""
    name: str = Field(..., description="Unique agent name")
    agent_type: Optional[str] = Field(default=None, description="Type of agent (e.g., 'trading', 'logistics', 'analytics')")
    type: Optional[str] = Field(default=None, description="Alias for agent_type")
    description: str = Field(default="")
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    config: Optional[AgentConfig] = None
    owner_id: str = Field(default="system", description="User or system ID that owns this agent")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentStatus(BaseModel):
    """Agent status"""
    state: str = Field(default="idle", description="Current state: idle, busy, error, maintenance")
    last_heartbeat: Optional[datetime] = None
    tasks_completed: int = Field(default=0)
    tasks_failed: int = Field(default=0)
    uptime_seconds: int = Field(default=0)


class Agent(AgentRegistration):
    """Full agent model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: AgentStatus = Field(default_factory=AgentStatus)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)


class AgentUpdate(BaseModel):
    """Agent update request"""
    description: Optional[str] = None
    capabilities: Optional[AgentCapabilities] = None
    config: Optional[AgentConfig] = None
    is_active: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class TaskAssignment(BaseModel):
    """Task assignment to agent"""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: int = Field(default=5, ge=1, le=10)


class TaskResult(BaseModel):
    """Task result from agent"""
    task_id: str
    agent_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    completed_at: datetime = Field(default_factory=datetime.utcnow)


# In-memory storage (replace with database in production)
agents_registry: Dict[str, Agent] = {}
task_queue: List[TaskAssignment] = []
task_results: Dict[str, TaskResult] = {}


# Endpoints
@router.post("/register", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def register_agent(registration: AgentRegistration):
    """
    Register a new AI agent in the platform
    """
    # Check if agent name already exists
    for agent in agents_registry.values():
        if agent.name == registration.name:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Agent with name '{registration.name}' already exists"
            )
    
    data = registration.dict()
    if not data.get("agent_type"):
        data["agent_type"] = data.get("type") or "general"
    agent = Agent(**data)
    agents_registry[agent.id] = agent
    
    return agent


@router.post("/agents")
async def register_agent_compat(registration: AgentRegistration):
    """Register an agent, returning the platform-standard {data: ...} envelope"""
    agent = await register_agent(registration)
    return {"data": jsonable_encoder(agent)}


@router.get("/agents")
async def list_agents_compat():
    """List agents, returning the platform-standard list shape"""
    return list(agents_registry.values())


@router.get("/", response_model=List[Agent])
async def list_agents(
    agent_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """
    List all registered agents with optional filtering
    """
    agents = list(agents_registry.values())
    
    # Apply filters
    if agent_type:
        agents = [a for a in agents if a.agent_type == agent_type]
    if is_active is not None:
        agents = [a for a in agents if a.is_active == is_active]
    
    # Apply pagination
    return agents[skip:skip + limit]


@router.get("/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """
    Get details of a specific agent
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    return agents_registry[agent_id]


@router.put("/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, update: AgentUpdate):
    """
    Update agent configuration or status
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    agent = agents_registry[agent_id]
    
    # Update fields
    if update.description is not None:
        agent.description = update.description
    if update.capabilities is not None:
        agent.capabilities = update.capabilities
    if update.config is not None:
        agent.config = update.config
    if update.is_active is not None:
        agent.is_active = update.is_active
    if update.metadata is not None:
        agent.metadata.update(update.metadata)
    
    agent.updated_at = datetime.utcnow()
    
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(agent_id: str):
    """
    Deactivate an agent (soft delete)
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    agents_registry[agent_id].is_active = False
    agents_registry[agent_id].updated_at = datetime.utcnow()


@router.post("/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, status: AgentStatus):
    """
    Receive heartbeat from agent to update status
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    agents_registry[agent_id].status = status
    agents_registry[agent_id].status.last_heartbeat = datetime.utcnow()
    agents_registry[agent_id].updated_at = datetime.utcnow()
    
    return {"message": "Heartbeat received"}


@router.post("/{agent_id}/assign-task", response_model=TaskAssignment)
async def assign_task(agent_id: str, task: TaskAssignment):
    """
    Assign a task to a specific agent
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    agent = agents_registry[agent_id]
    
    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent '{agent_id}' is not active"
        )
    
    if agent.status.state == "busy":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Agent '{agent_id}' is currently busy"
        )
    
    # Add to task queue
    task_queue.append(task)
    
    # Update agent status
    agent.status.state = "busy"
    agent.status.last_heartbeat = datetime.utcnow()
    agent.updated_at = datetime.utcnow()
    
    return task


@router.post("/{agent_id}/task-result", response_model=TaskResult)
async def submit_task_result(agent_id: str, result: TaskResult):
    """
    Submit task result from agent
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    # Store result
    task_results[result.task_id] = result
    
    # Update agent status
    agent = agents_registry[agent_id]
    if result.status == "completed":
        agent.status.tasks_completed += 1
    elif result.status == "failed":
        agent.status.tasks_failed += 1
    
    agent.status.state = "idle"
    agent.status.last_heartbeat = datetime.utcnow()
    agent.updated_at = datetime.utcnow()
    
    return result


@router.get("/{agent_id}/tasks", response_model=List[TaskAssignment])
async def get_agent_tasks(agent_id: str):
    """
    Get tasks assigned to a specific agent
    """
    if agent_id not in agents_registry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )
    
    # Filter tasks for this agent (in a real implementation, this would query the database)
    return [task for task in task_queue if task.task_id.startswith(agent_id)]


@router.get("/discover/by-capability/{capability}", response_model=List[Agent])
async def discover_agents_by_capability(capability: str):
    """
    Discover agents that have a specific capability
    """
    matching_agents = []
    for agent in agents_registry.values():
        if agent.is_active and capability in agent.capabilities.skills:
            matching_agents.append(agent)
    
    return matching_agents


@router.get("/discover/by-type/{agent_type}", response_model=List[Agent])
async def discover_agents_by_type(agent_type: str):
    """
    Discover agents of a specific type
    """
    matching_agents = []
    for agent in agents_registry.values():
        if agent.is_active and agent.agent_type == agent_type:
            matching_agents.append(agent)
    
    return matching_agents
