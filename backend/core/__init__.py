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

__all__ = [
    "UnifiedStateManager",
    "UnifiedUserSession", 
    "FeatureRequest",
    "FeaturePriority",
    "FeatureStatus",
    "unified_state_manager"
]
