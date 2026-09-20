"""
AI Agent Monitoring API
Provides health checks, performance metrics, alerts, and real-time monitoring
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/ai_monitoring", tags=["AI Monitoring"])


# Models
class HealthCheck(BaseModel):
    """Agent health check result"""
    agent_id: str
    status: str = Field(description="healthy, degraded, unhealthy, unknown")
    last_check: datetime = Field(default_factory=datetime.utcnow)
    response_time_ms: float
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100)
    active_connections: int
    error_rate: float = Field(ge=0, le=100)
    uptime_seconds: int


class PerformanceMetric(BaseModel):
    """Performance metric for an agent"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    metric_name: str
    metric_value: float
    unit: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Alert(BaseModel):
    """Monitoring alert"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    alert_type: str = Field(description="health, performance, security, compliance")
    severity: str = Field(description="info, warning, error, critical")
    title: str
    description: str
    threshold_value: Optional[float] = None
    current_value: Optional[float] = None
    triggered_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None


class AgentMetricsSummary(BaseModel):
    """Summary of metrics for an agent"""
    agent_id: str
    period_start: datetime
    period_end: datetime
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    error_rate: float
    uptime_percentage: float


class SystemOverview(BaseModel):
    """Overall system monitoring overview"""
    total_agents: int
    healthy_agents: int
    degraded_agents: int
    unhealthy_agents: int
    active_alerts: int
    critical_alerts: int
    average_response_time_ms: float
    total_requests_last_hour: int


# In-memory storage (replace with database in production)
health_checks: Dict[str, HealthCheck] = {}
performance_metrics: List[PerformanceMetric] = []
alerts: Dict[str, Alert] = {}


# Helper functions
def calculate_percentile(values: List[float], percentile: float) -> float:
    """Calculate percentile from a list of values"""
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = int(len(sorted_values) * percentile / 100)
    return sorted_values[min(index, len(sorted_values) - 1)]


# Endpoints
@router.post("/health-check/{agent_id}", response_model=HealthCheck)
async def submit_health_check(agent_id: str, health: HealthCheck):
    """Submit a health check result for an agent"""
    health.agent_id = agent_id
    health.last_check = datetime.utcnow()
    health_checks[agent_id] = health
    
    # Check if health status warrants an alert
    if health.status in ["degraded", "unhealthy"]:
        alert = Alert(
            agent_id=agent_id,
            alert_type="health",
            severity="critical" if health.status == "unhealthy" else "warning",
            title=f"Agent {health.status}",
            description=f"Agent health status is {health.status}",
            current_value=health.response_time_ms
        )
        alerts[alert.id] = alert
    
    return health


@router.get("/health-check/{agent_id}", response_model=HealthCheck)
@router.get("/health/{agent_id}", response_model=HealthCheck)
async def get_health_check(agent_id: str):
    """Get the latest health check for an agent"""
    if agent_id not in health_checks:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Health check for agent '{agent_id}' not found"
        )
    
    return health_checks[agent_id]


@router.get("/health-checks", response_model=List[HealthCheck])
async def list_health_checks(
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List all health checks with optional filtering"""
    checks = list(health_checks.values())
    
    if status:
        checks = [c for c in checks if c.status == status]
    
    return checks[skip:skip + limit]


@router.post("/metrics", response_model=PerformanceMetric, status_code=status.HTTP_201_CREATED)
async def submit_metric(metric: PerformanceMetric):
    """Submit a performance metric for an agent"""
    performance_metrics.append(metric)
    
    # Keep only last 10000 metrics per agent to prevent memory bloat
    agent_metrics = [m for m in performance_metrics if m.agent_id == metric.agent_id]
    if len(agent_metrics) > 10000:
        # Remove oldest metrics for this agent
        agent_ids_to_remove = [m.id for m in agent_metrics[:-10000]]
        performance_metrics = [m for m in performance_metrics if m.id not in agent_ids_to_remove]
    
    return metric


@router.get("/metrics/{agent_id}", response_model=List[PerformanceMetric])
async def get_agent_metrics(
    agent_id: str,
    metric_name: Optional[str] = None,
    hours: int = 24,
    skip: int = 0,
    limit: int = 1000
):
    """Get performance metrics for an agent"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    metrics = [
        m for m in performance_metrics
        if m.agent_id == agent_id and m.timestamp >= cutoff_time
    ]
    
    if metric_name:
        metrics = [m for m in metrics if m.metric_name == metric_name]
    
    # Sort by timestamp descending
    metrics.sort(key=lambda x: x.timestamp, reverse=True)
    
    return metrics[skip:skip + limit]


@router.get("/metrics/{agent_id}/summary", response_model=AgentMetricsSummary)
async def get_agent_metrics_summary(agent_id: str, hours: int = 24):
    """Get a summary of metrics for an agent"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    agent_metrics = [
        m for m in performance_metrics
        if m.agent_id == agent_id and m.timestamp >= cutoff_time
    ]
    
    # Calculate summary statistics
    total_requests = len(agent_metrics)
    successful_requests = len([m for m in agent_metrics if m.metric_value >= 0])
    failed_requests = total_requests - successful_requests
    
    response_times = [m.metric_value for m in agent_metrics if m.metric_name == "response_time"]
    
    if response_times:
        avg_response = sum(response_times) / len(response_times)
        p50 = calculate_percentile(response_times, 50)
        p95 = calculate_percentile(response_times, 95)
        p99 = calculate_percentile(response_times, 99)
    else:
        avg_response = 0.0
        p50 = 0.0
        p95 = 0.0
        p99 = 0.0
    
    error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0.0
    
    # Calculate uptime based on health checks
    if agent_id in health_checks:
        uptime_percentage = 100.0 if health_checks[agent_id].status == "healthy" else 0.0
    else:
        uptime_percentage = 0.0
    
    summary = AgentMetricsSummary(
        agent_id=agent_id,
        period_start=cutoff_time,
        period_end=datetime.utcnow(),
        total_requests=total_requests,
        successful_requests=successful_requests,
        failed_requests=failed_requests,
        average_response_time_ms=avg_response,
        p50_response_time_ms=p50,
        p95_response_time_ms=p95,
        p99_response_time_ms=p99,
        error_rate=error_rate,
        uptime_percentage=uptime_percentage
    )
    
    return summary


@router.post("/alerts", response_model=Alert, status_code=status.HTTP_201_CREATED)
async def create_alert(alert: Alert):
    """Create a monitoring alert"""
    alerts[alert.id] = alert
    return alert


@router.get("/alerts", response_model=List[Alert])
async def list_alerts(
    agent_id: Optional[str] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    resolved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """List monitoring alerts with optional filtering"""
    alert_list = list(alerts.values())
    
    if agent_id:
        alert_list = [a for a in alert_list if a.agent_id == agent_id]
    if alert_type:
        alert_list = [a for a in alert_list if a.alert_type == alert_type]
    if severity:
        alert_list = [a for a in alert_list if a.severity == severity]
    if resolved is not None:
        alert_list = [a for a in alert_list if a.resolved == resolved]
    
    # Sort by triggered_at descending
    alert_list.sort(key=lambda x: x.triggered_at, reverse=True)
    
    return alert_list[skip:skip + limit]


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str):
    """Acknowledge an alert"""
    if alert_id not in alerts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found"
        )
    
    alerts[alert_id].acknowledged_by = acknowledged_by
    
    return {"message": "Alert acknowledged"}


@router.put("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Resolve an alert"""
    if alert_id not in alerts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID '{alert_id}' not found"
        )
    
    alerts[alert_id].resolved = True
    alerts[alert_id].resolved_at = datetime.utcnow()
    
    return {"message": "Alert resolved"}


@router.get("/system-overview", response_model=SystemOverview)
async def get_system_overview():
    """Get overall system monitoring overview"""
    total_agents = len(health_checks)
    
    healthy = len([c for c in health_checks.values() if c.status == "healthy"])
    degraded = len([c for c in health_checks.values() if c.status == "degraded"])
    unhealthy = len([c for c in health_checks.values() if c.status == "unhealthy"])
    
    active_alerts = len([a for a in alerts.values() if not a.resolved])
    critical_alerts = len([a for a in alerts.values() if a.severity == "critical" and not a.resolved])
    
    response_times = [c.response_time_ms for c in health_checks.values()]
    avg_response = sum(response_times) / len(response_times) if response_times else 0.0
    
    # Calculate total requests in last hour
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    recent_metrics = [m for m in performance_metrics if m.timestamp >= cutoff_time]
    total_requests = len(recent_metrics)
    
    overview = SystemOverview(
        total_agents=total_agents,
        healthy_agents=healthy,
        degraded_agents=degraded,
        unhealthy_agents=unhealthy,
        active_alerts=active_alerts,
        critical_alerts=critical_alerts,
        average_response_time_ms=avg_response,
        total_requests_last_hour=total_requests
    )
    
    return overview


@router.delete("/alerts")
async def clear_old_alerts(days: int = 30):
    """Clear alerts older than specified days"""
    cutoff_time = datetime.utcnow() - timedelta(days=days)
    
    alerts_to_remove = [
        alert_id for alert_id, alert in alerts.items()
        if alert.triggered_at < cutoff_time and alert.resolved
    ]
    
    for alert_id in alerts_to_remove:
        del alerts[alert_id]
    
    return {"message": f"Cleared {len(alerts_to_remove)} old alerts"}
