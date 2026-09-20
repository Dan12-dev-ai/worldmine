"""
Admin Control Center API
Enterprise admin panel with all modules
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class UserRole(str, Enum):
    """User roles"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"


class SystemModule(str, Enum):
    """System modules"""
    MARKETPLACE = "marketplace"
    TRADING = "trading"
    WALLET = "wallet"
    ESCROW = "escrow"
    CONTRACTS = "contracts"
    LOGISTICS = "logistics"
    PAYMENTS = "payments"
    NOTIFICATIONS = "notifications"
    AI_AGENTS = "ai_agents"


class AdminAction(BaseModel):
    """Admin action log"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_id: str
    action: str
    target_type: str
    target_id: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SystemStats(BaseModel):
    """System statistics"""
    total_users: int
    active_users: int
    total_transactions: float
    total_escrow_amount: float
    active_shipments: int
    pending_notifications: int
    ai_agents_active: int
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ModuleHealth(BaseModel):
    """Module health status"""
    module: SystemModule
    status: str
    uptime_seconds: float
    error_rate: float
    last_check: datetime = Field(default_factory=datetime.utcnow)


class UserManagement(BaseModel):
    """User management"""
    user_id: str
    username: str
    email: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None


# In-memory storage
admin_actions: List[AdminAction] = []
system_stats: Dict[str, Any] = {
    "total_users": 1250,
    "active_users": 342,
    "total_transactions": 1500000.00,
    "total_escrow_amount": 450000.00,
    "active_shipments": 89,
    "pending_notifications": 234,
    "ai_agents_active": 12
}
module_health: Dict[SystemModule, ModuleHealth] = {}
users: Dict[str, UserManagement] = {}


@router.get("/dashboard/stats", response_model=SystemStats)
async def get_system_stats():
    """Get overall system statistics"""
    return SystemStats(**system_stats)


@router.get("/modules/health", response_model=List[ModuleHealth])
async def get_module_health():
    """Get health status of all modules"""
    health_list = []
    
    for module in SystemModule:
        health = ModuleHealth(
            module=module,
            status="healthy",
            uptime_seconds=86400.0,
            error_rate=0.01
        )
        health_list.append(health)
    
    return health_list


@router.get("/users", response_model=List[UserManagement])
async def list_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100
):
    """List all users with filters"""
    user_list = list(users.values())
    
    if role:
        user_list = [u for u in user_list if u.role == role]
    if is_active is not None:
        user_list = [u for u in user_list if u.is_active == is_active]
    
    user_list.sort(key=lambda x: x.created_at, reverse=True)
    
    return user_list[skip:skip + limit]


@router.get("/users/{user_id}", response_model=UserManagement)
async def get_user(user_id: str):
    """Get user by ID"""
    if user_id not in users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    return users[user_id]


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, new_role: UserRole, admin_id: str):
    """Update user role"""
    if user_id not in users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    
    old_role = users[user_id].role
    users[user_id].role = new_role
    
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="update_role",
        target_type="user",
        target_id=user_id,
        details={"old_role": old_role, "new_role": new_role}
    )
    admin_actions.append(action)
    
    return {"message": "User role updated"}


@router.put("/users/{user_id}/status")
async def update_user_status(user_id: str, is_active: bool, admin_id: str):
    """Update user active status"""
    if user_id not in users:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
    
    users[user_id].is_active = is_active
    
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="update_status",
        target_type="user",
        target_id=user_id,
        details={"is_active": is_active}
    )
    admin_actions.append(action)
    
    return {"message": "User status updated"}


@router.get("/audit-log", response_model=List[AdminAction])
async def get_audit_log(
    admin_id: Optional[str] = None,
    action: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """Get admin action audit log"""
    log_list = admin_actions
    
    if admin_id:
        log_list = [a for a in log_list if a.admin_id == admin_id]
    if action:
        log_list = [a for a in log_list if a.action == action]
    
    log_list.sort(key=lambda x: x.timestamp, reverse=True)
    
    return log_list[skip:skip + limit]


@router.post("/modules/{module}/restart")
async def restart_module(module: SystemModule, admin_id: str):
    """Restart a system module"""
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="restart_module",
        target_type="module",
        target_id=module.value,
        details={}
    )
    admin_actions.append(action)
    
    return {"message": f"Module {module.value} restart initiated"}


@router.get("/analytics/transactions")
async def get_transaction_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get transaction analytics"""
    return {
        "total_volume": 1500000.00,
        "transaction_count": 5420,
        "average_value": 276.86,
        "success_rate": 0.98,
        "by_type": {
            "deposit": 450000.00,
            "withdrawal": 320000.00,
            "transfer": 730000.00
        }
    }


@router.get("/analytics/users")
async def get_user_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get user analytics"""
    return {
        "new_users": 150,
        "active_users": 342,
        "churn_rate": 0.05,
        "average_session_duration": 1800.0,
        "by_role": {
            "admin": 5,
            "moderator": 12,
            "user": 1233
        }
    }


@router.post("/maintenance/enable")
async def enable_maintenance_mode(admin_id: str, reason: str):
    """Enable maintenance mode"""
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="enable_maintenance",
        target_type="system",
        target_id="global",
        details={"reason": reason}
    )
    admin_actions.append(action)
    
    return {"message": "Maintenance mode enabled"}


@router.post("/maintenance/disable")
async def disable_maintenance_mode(admin_id: str):
    """Disable maintenance mode"""
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="disable_maintenance",
        target_type="system",
        target_id="global",
        details={}
    )
    admin_actions.append(action)
    
    return {"message": "Maintenance mode disabled"}


@router.get("/config")
async def get_system_config():
    """Get system configuration"""
    return {
        "maintenance_mode": False,
        "registration_enabled": True,
        "max_login_attempts": 5,
        "session_timeout": 3600,
        "supported_currencies": ["USD", "EUR", "GBP"],
        "payment_providers": ["stripe", "wise", "paypal"]
    }


@router.put("/config")
async def update_system_config(config: Dict[str, Any], admin_id: str):
    """Update system configuration"""
    # Log admin action
    action = AdminAction(
        admin_id=admin_id,
        action="update_config",
        target_type="system",
        target_id="global",
        details=config
    )
    admin_actions.append(action)
    
    return {"message": "System configuration updated"}
