"""
⚙️ DEDAN 2.0 - CONFIGURATION PACKAGE
Centralized configuration management
"""

from .settings import (
    settings,
    get_database_url,
    get_redis_url,
    get_cors_origins,
    is_development,
    is_production
)

__all__ = [
    'settings',
    'get_database_url',
    'get_redis_url',
    'get_cors_origins',
    'is_development',
    'is_production'
]
