"""
AI Agent Governance API
Manages policies, compliance, approvals, and audit trails for AI agents
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

router = APIRouter(prefix="/api/ai-governance", tags=["AI Governance"])


# Models
class Policy(BaseModel):
    """Governance policy for AI agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    policy_type: str = Field(description="Type: capability, security, compliance, performance")
    rules: Dict[str, Any] = Field(default_factory=dict)
    applies_to: List[str] = Field(default_factory=list, description="Agent types this policy applies to")
    severity: str = Field(default="medium", description="Severity: low, medium, high, critical")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class PolicyViolation(BaseModel):
    """Record of a policy violation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    policy_id: str
    agent_id: str
    violation_type: str
    description: str
    severity: str
    occurred_at: datetime = Field(default_factory=datetime.utcnow)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None


class ApprovalRequest(BaseModel):
    """Request for agent approval"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    request_type: str = Field(description="Type: registration, update, deactivation")
    requester_id: str
    reason: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="pending", description="pending, approved, rejected")
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    review_notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AuditLog(BaseModel):
    """Audit log entry for agent actions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    action: str
    actor: str = Field(description="User or system that performed the action")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class ComplianceReport(BaseModel):
    """Compliance report for an agent"""
    agent_id: str
    report_period_start: datetime
    report_period_end: datetime
    total_violations: int
    violations_by_severity: Dict[str, int]
    compliance_score: float = Field(ge=0, le=100)
    recommendations: List[str] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=datetime.utcnow)


# In-memory storage (replace with database in production)
policies: Dict[str, Policy] = {}
policy_violations: Dict[str, PolicyViolation] = {}
approval_requests: Dict[str, ApprovalRequest] = {}
audit_logs: List[AuditLog] = []


# Endpoints
@router.post("/policies", response_model=Policy, status_code=status.HTTP_201_CREATED)
async def create_policy(policy: Policy):
    """Create a new governance policy"""
    policies[policy.id] = policy
    return policy


@router.get("/policies", response_model=List[Policy])
async def list_policies(
    policy_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """List all governance policies with optional filtering"""
    policy_list = list(policies.values())
    
    if policy_type:
        policy_list = [p for p in policy_list if p.policy_type == policy_type]
    if is_active is not None:
        policy_list = [p for p in policy_list if p.is_active == is_active]
    
    return policy_list[skip:skip + limit]


@router.get("/policies/{policy_id}", response_model=Policy)
async def get_policy(policy_id: str):
    """Get details of a specific policy"""
    if policy_id not in policies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID '{policy_id}' not found"
        )
    
    return policies[policy_id]


@router.put("/policies/{policy_id}", response_model=Policy)
async def update_policy(policy_id: str, policy: Policy):
    """Update a governance policy"""
    if policy_id not in policies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID '{policy_id}' not found"
        )
    
    policy.id = policy_id
    policy.updated_at = datetime.utcnow()
    policies[policy_id] = policy
    
    return policy


@router.delete("/policies/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(policy_id: str):
    """Delete a governance policy"""
    if policy_id not in policies:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Policy with ID '{policy_id}' not found"
        )
    
    del policies[policy_id]


@router.post("/violations", response_model=PolicyViolation, status_code=status.HTTP_201_CREATED)
async def report_violation(violation: PolicyViolation):
    """Report a policy violation"""
    policy_violations[violation.id] = violation
    return violation


@router.get("/violations", response_model=List[PolicyViolation])
async def list_violations(
    agent_id: Optional[str] = None,
    policy_id: Optional[str] = None,
    resolved: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """List policy violations with optional filtering"""
    violations = list(policy_violations.values())
    
    if agent_id:
        violations = [v for v in violations if v.agent_id == agent_id]
    if policy_id:
        violations = [v for v in violations if v.policy_id == policy_id]
    if resolved is not None:
        violations = [v for v in violations if v.resolved == resolved]
    
    violations.sort(key=lambda x: x.occurred_at, reverse=True)
    
    return violations[skip:skip + limit]


@router.put("/violations/{violation_id}/resolve")
async def resolve_violation(violation_id: str, resolution_notes: str):
    """Mark a policy violation as resolved"""
    if violation_id not in policy_violations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Violation with ID '{violation_id}' not found"
        )
    
    violation = policy_violations[violation_id]
    violation.resolved = True
    violation.resolved_at = datetime.utcnow()
    violation.resolution_notes = resolution_notes
    
    return {"message": "Violation resolved"}


@router.post("/approvals", response_model=ApprovalRequest, status_code=status.HTTP_201_CREATED)
async def create_approval_request(request: ApprovalRequest):
    """Create a new approval request for agent operations"""
    approval_requests[request.id] = request
    return request


@router.get("/approvals", response_model=List[ApprovalRequest])
async def list_approval_requests(
    agent_id: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List approval requests with optional filtering"""
    requests = list(approval_requests.values())
    
    if agent_id:
        requests = [r for r in requests if r.agent_id == agent_id]
    if status:
        requests = [r for r in requests if r.status == status]
    
    requests.sort(key=lambda x: x.created_at, reverse=True)
    
    return requests[skip:skip + limit]


@router.put("/approvals/{request_id}/approve")
async def approve_request(request_id: str, reviewer_id: str, notes: Optional[str] = None):
    """Approve an approval request"""
    if request_id not in approval_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request with ID '{request_id}' not found"
        )
    
    request = approval_requests[request_id]
    request.status = "approved"
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.utcnow()
    request.review_notes = notes
    
    return {"message": "Request approved"}


@router.put("/approvals/{request_id}/reject")
async def reject_request(request_id: str, reviewer_id: str, notes: Optional[str] = None):
    """Reject an approval request"""
    if request_id not in approval_requests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request with ID '{request_id}' not found"
        )
    
    request = approval_requests[request_id]
    request.status = "rejected"
    request.reviewed_by = reviewer_id
    request.reviewed_at = datetime.utcnow()
    request.review_notes = notes
    
    return {"message": "Request rejected"}


@router.post("/audit-log", response_model=AuditLog, status_code=status.HTTP_201_CREATED)
async def create_audit_log(log: AuditLog):
    """Create an audit log entry"""
    audit_logs.append(log)
    return log


@router.get("/audit-log", response_model=List[AuditLog])
async def list_audit_logs(
    agent_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List audit log entries with optional filtering"""
    logs = audit_logs
    
    if agent_id:
        logs = [l for l in logs if l.agent_id == agent_id]
    if action:
        logs = [l for l in logs if l.action == action]
    
    logs.sort(key=lambda x: x.timestamp, reverse=True)
    
    return logs[skip:skip + limit]


@router.get("/compliance-report/{agent_id}", response_model=ComplianceReport)
async def generate_compliance_report(agent_id: str, days: int = 30):
    """Generate a compliance report for an agent"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    agent_violations = [
        v for v in policy_violations.values()
        if v.agent_id == agent_id and start_date <= v.occurred_at <= end_date
    ]
    
    violations_by_severity = {}
    for violation in agent_violations:
        violations_by_severity[violation.severity] = violations_by_severity.get(violation.severity, 0) + 1
    
    total_violations = len(agent_violations)
    if total_violations == 0:
        compliance_score = 100.0
    else:
        severity_weights = {"low": 1, "medium": 5, "high": 10, "critical": 20}
        weighted_score = sum(
            violations_by_severity.get(sev, 0) * weight
            for sev, weight in severity_weights.items()
        )
        compliance_score = max(0, 100 - weighted_score)
    
    recommendations = []
    if violations_by_severity.get("critical", 0) > 0:
        recommendations.append("Immediate action required: Address critical violations")
    if violations_by_severity.get("high", 0) > 2:
        recommendations.append("Review and address high-severity violations")
    if violations_by_severity.get("medium", 0) > 5:
        recommendations.append("Consider implementing additional safeguards")
    
    report = ComplianceReport(
        agent_id=agent_id,
        report_period_start=start_date,
        report_period_end=end_date,
        total_violations=total_violations,
        violations_by_severity=violations_by_severity,
        compliance_score=compliance_score,
        recommendations=recommendations
    )
    
    return report


@router.get("/agent-status/{agent_id}")
async def get_agent_governance_status(agent_id: str):
    """Get overall governance status for an agent"""
    pending_approvals = [
        r for r in approval_requests.values()
        if r.agent_id == agent_id and r.status == "pending"
    ]
    
    unresolved_violations = [
        v for v in policy_violations.values()
        if v.agent_id == agent_id and not v.resolved
    ]
    
    recent_logs = [
        l for l in audit_logs
        if l.agent_id == agent_id
    ][:10]
    
    return {
        "agent_id": agent_id,
        "pending_approvals": len(pending_approvals),
        "unresolved_violations": len(unresolved_violations),
        "recent_audit_entries": len(recent_logs),
        "compliance_status": "compliant" if len(unresolved_violations) == 0 else "non-compliant"
    }
