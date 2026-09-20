"""
World-Mine Centralized System Logging
Enterprise-grade logging with system_logs, audit_logs, AI_logs
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class LogCategory(Enum):
    SYSTEM = "system"
    AUDIT = "audit"
    AI = "ai"
    SECURITY = "security"
    PERFORMANCE = "performance"

@dataclass
class LogEntry:
    log_id: str
    timestamp: datetime
    level: LogLevel
    category: LogCategory
    message: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert log entry to dictionary"""
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp.isoformat(),
            "level": self.level.value,
            "category": self.category.value,
            "message": self.message,
            "user_id": self.user_id,
            "correlation_id": self.correlation_id,
            "metadata": self.metadata
        }

class CentralizedLogger:
    """Enterprise-grade centralized logging system"""
    
    def __init__(self):
        self.system_logs: List[LogEntry] = []
        self.audit_logs: List[LogEntry] = []
        self.ai_logs: List[LogEntry] = []
        self._max_logs_per_category = 10000
        
    def log_system(
        self,
        level: LogLevel,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log system event"""
        log_entry = LogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=level,
            category=LogCategory.SYSTEM,
            message=message,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        
        self.system_logs.append(log_entry)
        self._trim_logs(self.system_logs)
        
        logger.info(f"[SYSTEM] {level.value.upper()}: {message}")
        return log_entry.log_id
        
    def log_audit(
        self,
        user_id: str,
        action: str,
        resource: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log audit event"""
        message = f"User {user_id} performed {action} on {resource}"
        
        log_entry = LogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=LogLevel.INFO,
            category=LogCategory.AUDIT,
            message=message,
            user_id=user_id,
            correlation_id=correlation_id,
            metadata={
                "action": action,
                "resource": resource,
                **(metadata or {})
            }
        )
        
        self.audit_logs.append(log_entry)
        self._trim_logs(self.audit_logs)
        
        logger.info(f"[AUDIT] {message}")
        return log_entry.log_id
        
    def log_ai(
        self,
        agent_id: str,
        action: str,
        recommendation: Dict[str, Any],
        governance_result: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """Log AI agent event"""
        message = f"Agent {agent_id} performed {action}"
        
        log_entry = LogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=LogLevel.INFO,
            category=LogCategory.AI,
            message=message,
            correlation_id=correlation_id,
            metadata={
                "agent_id": agent_id,
                "action": action,
                "recommendation": recommendation,
                "governance_result": governance_result
            }
        )
        
        self.ai_logs.append(log_entry)
        self._trim_logs(self.ai_logs)
        
        logger.info(f"[AI] {message}")
        return log_entry.log_id
        
    def log_security(
        self,
        level: LogLevel,
        event_type: str,
        user_id: Optional[str],
        details: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> str:
        """Log security event"""
        message = f"Security event: {event_type}"
        
        log_entry = LogEntry(
            log_id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            level=level,
            category=LogCategory.SECURITY,
            message=message,
            user_id=user_id,
            correlation_id=correlation_id,
            metadata={
                "event_type": event_type,
                **details
            }
        )
        
        self.system_logs.append(log_entry)
        self._trim_logs(self.system_logs)
        
        logger.warning(f"[SECURITY] {level.value.upper()}: {message}")
        return log_entry.log_id
        
    def _trim_logs(self, logs: List[LogEntry]):
        """Trim logs to max size"""
        while len(logs) > self._max_logs_per_category:
            logs.pop(0)
            
    def get_system_logs(
        self,
        level: Optional[LogLevel] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get system logs"""
        logs = self.system_logs
        if level:
            logs = [l for l in logs if l.level == level]
        return [l.to_dict() for l in logs[-limit:]]
        
    def get_audit_logs(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get audit logs"""
        logs = self.audit_logs
        if user_id:
            logs = [l for l in logs if l.user_id == user_id]
        return [l.to_dict() for l in logs[-limit:]]
        
    def get_ai_logs(
        self,
        agent_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get AI logs"""
        logs = self.ai_logs
        if agent_id:
            logs = [l for l in logs if l.metadata.get("agent_id") == agent_id]
        return [l.to_dict() for l in logs[-limit:]]
        
    def get_logs_by_correlation(self, correlation_id: str) -> List[Dict[str, Any]]:
        """Get all logs by correlation ID"""
        all_logs = self.system_logs + self.audit_logs + self.ai_logs
        filtered = [l for l in all_logs if l.correlation_id == correlation_id]
        return [l.to_dict() for l in filtered]
        
    def get_log_summary(self) -> Dict[str, Any]:
        """Get logging summary"""
        return {
            "system_logs_count": len(self.system_logs),
            "audit_logs_count": len(self.audit_logs),
            "ai_logs_count": len(self.ai_logs),
            "total_logs": len(self.system_logs) + len(self.audit_logs) + len(self.ai_logs),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Global centralized logger instance
centralized_logger = CentralizedLogger()
