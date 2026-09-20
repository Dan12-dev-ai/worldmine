"""
AI Agent Router API
Routes tasks to appropriate agents based on capabilities, load, and priority
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import heapq

router = APIRouter(prefix="/api/ai-router", tags=["AI Router"])


# Models
class RoutingStrategy(BaseModel):
    """Routing strategy configuration"""
    type: str = Field(default="capability", description="Strategy: capability, load-balanced, priority, round-robin")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseModel):
    """Task submission for routing"""
    task_type: str
    required_capabilities: List[str] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10, description="1=highest, 10=lowest")
    timeout_seconds: Optional[int] = Field(default=300, description="Task timeout")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RoutingDecision(BaseModel):
    """Routing decision result"""
    task_id: str
    assigned_agent_id: Optional[str] = None
    routing_strategy: str
    reason: str
    estimated_completion_time: Optional[int] = None
    alternative_agents: List[str] = Field(default_factory=list)


class AgentLoad(BaseModel):
    """Agent load information"""
    agent_id: str
    current_tasks: int
    max_concurrent_tasks: int
    load_percentage: float
    average_task_duration: float
    last_activity: datetime


class RoutingMetrics(BaseModel):
    """Routing system metrics"""
    total_tasks_routed: int
    tasks_routed_last_hour: int
    average_routing_time_ms: float
    success_rate: float
    agent_utilization: Dict[str, float]


# In-memory storage (replace with database in production)
routing_queue: List[tuple] = []  # Priority queue: (priority, timestamp, task)
routing_history: List[RoutingDecision] = []
agent_loads: Dict[str, AgentLoad] = {}
routing_metrics = RoutingMetrics(
    total_tasks_routed=0,
    tasks_routed_last_hour=0,
    average_routing_time_ms=0.0,
    success_rate=1.0,
    agent_utilization={}
)


# Helper functions
def calculate_agent_load(agent_id: str, current_tasks: int, max_tasks: int) -> float:
    """Calculate agent load percentage"""
    if max_tasks == 0:
        return 100.0
    return (current_tasks / max_tasks) * 100


def find_best_agent_by_capability(
    task_type: str,
    required_capabilities: List[str],
    available_agents: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Find best agent based on capability matching
    Returns agent_id or None
    """
    best_agent = None
    best_score = 0
    
    for agent in available_agents:
        if not agent.get('is_active', True):
            continue
        
        # Calculate capability match score
        score = 0
        agent_capabilities = agent.get('capabilities', {}).get('skills', [])
        
        for cap in required_capabilities:
            if cap in agent_capabilities:
                score += 1
        
        # Prefer agents with matching task type
        if agent.get('agent_type') == task_type:
            score += 2
        
        # Consider current load
        current_load = agent_loads.get(agent['id'], AgentLoad(
            agent_id=agent['id'],
            current_tasks=0,
            max_concurrent_tasks=agent.get('capabilities', {}).get('max_concurrent_tasks', 1),
            load_percentage=0.0,
            average_task_duration=0.0,
            last_activity=datetime.utcnow()
        )).load_percentage
        
        score -= (current_load / 100)
        
        if score > best_score:
            best_score = score
            best_agent = agent['id']
    
    return best_agent


def find_best_agent_by_load_balancing(
    available_agents: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Find agent with lowest current load
    Returns agent_id or None
    """
    best_agent = None
    lowest_load = 100.0
    
    for agent in available_agents:
        if not agent.get('is_active', True):
            continue
        
        load_info = agent_loads.get(agent['id'])
        if load_info:
            if load_info.load_percentage < lowest_load:
                lowest_load = load_info.load_percentage
                best_agent = agent['id']
        else:
            # Agent has no load info, assume it's available
            best_agent = agent['id']
            break
    
    return best_agent


def find_best_agent_by_priority(
    task_priority: int,
    available_agents: List[Dict[str, Any]]
) -> Optional[str]:
    """
    Find agent based on task priority
    High priority tasks go to high-capability agents
    Returns agent_id or None
    """
    # For high priority (1-3), use agents with most capabilities
    if task_priority <= 3:
        best_agent = None
        max_capabilities = 0
        
        for agent in available_agents:
            if not agent.get('is_active', True):
                continue
            
            capabilities = len(agent.get('capabilities', {}).get('skills', []))
            if capabilities > max_capabilities:
                max_capabilities = capabilities
                best_agent = agent['id']
        
        return best_agent
    else:
        # For lower priority, use load balancing
        return find_best_agent_by_load_balancing(available_agents)


# Endpoints
@router.post("/route-task", response_model=RoutingDecision)
async def route_task(task: TaskRequest, strategy: RoutingStrategy = RoutingStrategy()):
    """
    Route a task to the most appropriate agent
    """
    import time
    start_time = time.time()
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Get available agents (in production, this would query the agent registry)
    # For now, we'll use a mock approach
    available_agents = []
    # This would be populated from the agent registry API
    
    if not available_agents:
        return RoutingDecision(
            task_id=task_id,
            assigned_agent_id=None,
            routing_strategy=strategy.type,
            reason="No agents available",
            alternative_agents=[]
        )
    
    # Select agent based on strategy
    assigned_agent_id = None
    
    if strategy.type == "capability":
        assigned_agent_id = find_best_agent_by_capability(
            task.task_type,
            task.required_capabilities,
            available_agents
        )
        reason = "Selected based on capability match"
    elif strategy.type == "load-balanced":
        assigned_agent_id = find_best_agent_by_load_balancing(available_agents)
        reason = "Selected based on lowest load"
    elif strategy.type == "priority":
        assigned_agent_id = find_best_agent_by_priority(task.priority, available_agents)
        reason = "Selected based on task priority"
    elif strategy.type == "round-robin":
        # Simple round-robin implementation
        if available_agents:
            assigned_agent_id = available_agents[routing_metrics.total_tasks_routed % len(available_agents)]['id']
            reason = "Selected using round-robin"
    else:
        assigned_agent_id = find_best_agent_by_capability(
            task.task_type,
            task.required_capabilities,
            available_agents
        )
        reason = "Selected using default capability strategy"
    
    # Calculate alternative agents
    alternative_agents = [
        agent['id'] for agent in available_agents 
        if agent['id'] != assigned_agent_id and agent.get('is_active', True)
    ][:3]
    
    # Create routing decision
    decision = RoutingDecision(
        task_id=task_id,
        assigned_agent_id=assigned_agent_id,
        routing_strategy=strategy.type,
        reason=reason,
        estimated_completion_time=task.timeout_seconds,
        alternative_agents=alternative_agents
    )
    
    # Update metrics
    routing_time_ms = (time.time() - start_time) * 1000
    routing_metrics.total_tasks_routed += 1
    routing_metrics.tasks_routed_last_hour += 1
    routing_metrics.average_routing_time_ms = (
        (routing_metrics.average_routing_time_ms * (routing_metrics.total_tasks_routed - 1) + routing_time_ms)
        / routing_metrics.total_tasks_routed
    )
    
    # Store in history
    routing_history.append(decision)
    
    return decision


@router.get("/routing-metrics", response_model=RoutingMetrics)
async def get_routing_metrics():
    """
    Get routing system metrics
    """
    return routing_metrics


@router.get("/routing-history", response_model=List[RoutingDecision])
async def get_routing_history(
    limit: int = 100,
    skip: int = 0
):
    """
    Get routing decision history
    """
    return routing_history[skip:skip + limit]


@router.post("/agent-load/{agent_id}", response_model=AgentLoad)
async def update_agent_load(agent_id: str, load: AgentLoad):
    """
    Update agent load information
    """
    load.agent_id = agent_id
    agent_loads[agent_id] = load
    
    # Update utilization metrics
    routing_metrics.agent_utilization[agent_id] = load.load_percentage
    
    return load


@router.get("/agent-load/{agent_id}", response_model=AgentLoad)
async def get_agent_load(agent_id: str):
    """
    Get agent load information
    """
    if agent_id not in agent_loads:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Load information for agent '{agent_id}' not found"
        )
    
    return agent_loads[agent_id]


@router.get("/all-agent-loads", response_model=List[AgentLoad])
async def get_all_agent_loads():
    """
    Get load information for all agents
    """
    return list(agent_loads.values())


@router.post("/rebalance")
async def rebalance_tasks():
    """
    Rebalance tasks across agents based on current loads
    """
    rebalanced_count = 0
    
    # Get all agent loads
    loads = list(agent_loads.values())
    
    if not loads:
        return {"message": "No agents to rebalance", "rebalanced_count": 0}
    
    # Calculate average load
    avg_load = sum(load.load_percentage for load in loads) / len(loads)
    
    # Identify overloaded and underloaded agents
    overloaded = [load for load in loads if load.load_percentage > avg_load + 20]
    underloaded = [load for load in loads if load.load_percentage < avg_load - 20]
    
    # In a real implementation, this would move tasks from overloaded to underloaded agents
    # For now, we'll just report the potential rebalancing
    rebalanced_count = min(len(overloaded), len(underloaded))
    
    return {
        "message": f"Potential rebalancing: {rebalanced_count} tasks could be moved",
        "overloaded_agents": [load.agent_id for load in overloaded],
        "underloaded_agents": [load.agent_id for load in underloaded],
        "rebalanced_count": rebalanced_count
    }


@router.delete("/routing-history")
async def clear_routing_history():
    """
    Clear routing history (for maintenance)
    """
    routing_history.clear()
    return {"message": "Routing history cleared"}
