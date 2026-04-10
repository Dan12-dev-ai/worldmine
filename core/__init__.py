# Core Unified State Management
# Single Source of Truth for conflict-free architecture

from .StateManagement import (
    UnifiedStateManager,
    UnifiedUserSession,
    FeatureRequest,
    FeaturePriority,
    FeatureStatus,
    unified_state_manager
)
from .SovereignAuth import (
    SovereignAuthSystem,
    SovereignUser,
    AuthSession,
    AuthLayer,
    AuthStatus,
    sovereign_auth_system
)
from .ConflictPrevention import (
    ConflictPreventionSystem,
    conflict_prevention_system
)

__all__ = [
    "UnifiedStateManager",
    "UnifiedUserSession", 
    "FeatureRequest",
    "FeaturePriority",
    "FeatureStatus",
    "unified_state_manager",
    "SovereignAuthSystem",
    "SovereignUser",
    "AuthSession",
    "AuthLayer",
    "AuthStatus",
    "sovereign_auth_system",
    "ConflictPreventionSystem",
    "conflict_prevention_system"
]
