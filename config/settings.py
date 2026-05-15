"""
⚙️ DEDAN 2.0 - UNIFIED CONFIGURATION MANAGEMENT
Centralized configuration for all environment variables and settings
Eliminates all duplicate configuration code across the codebase
"""

import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class Environment(Enum):
    """Environment types"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(Enum):
    """Log levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    pool_size: int = 20
    max_connections: int = 20
    min_connections: int = 5
    command_timeout: int = 60
    server_settings: Dict[str, str] = None
    
    def __post_init__(self):
        if self.server_settings is None:
            self.server_settings = {
                'application_name': 'dedan_2_0',
                'timezone': 'UTC'
            }

@dataclass
class RedisConfig:
    """Redis configuration"""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    max_connections: int = 20
    socket_timeout: int = 5
    socket_connect_timeout: int = 5

@dataclass
class CORSConfig:
    """CORS configuration"""
    allowed_origins: List[str]
    allowed_methods: List[str]
    allowed_headers: List[str]
    allow_credentials: bool = True
    max_age: int = 86400

@dataclass
class SecurityConfig:
    """Security configuration"""
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_hash_rounds: int = 12

@dataclass
class APIConfig:
    """API configuration"""
    title: str = "DEDAN 2.0 API"
    description: str = "World's First Quantum-AI Hybrid Mineral Marketplace"
    version: str = "2.0.0"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    rate_limit_per_minute: int = 60

class Settings:
    """Unified settings management"""
    
    def __init__(self):
        self.environment = self._get_environment()
        self.debug = self._get_bool("DEBUG", default=self.environment == Environment.DEVELOPMENT)
        self.log_level = self._get_log_level()
        
        # Database configuration
        self.database = self._get_database_config()
        
        # Redis configuration
        self.redis = self._get_redis_config()
        
        # CORS configuration
        self.cors = self._get_cors_config()
        
        # Security configuration
        self.security = self._get_security_config()
        
        # API configuration
        self.api = self._get_api_config()
        
        # External service configurations
        self.external_services = self._get_external_services_config()
        
        # Feature flags
        self.features = self._get_feature_flags()
    
    def _get_environment(self) -> Environment:
        """Get current environment"""
        env_name = os.getenv("ENVIRONMENT", "development").lower()
        try:
            return Environment(env_name)
        except ValueError:
            return Environment.DEVELOPMENT
    
    def _get_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable"""
        value = os.getenv(key, str(default)).lower()
        return value in ("true", "1", "yes", "on")
    
    def _get_log_level(self) -> LogLevel:
        """Get log level"""
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        try:
            return LogLevel(level_name)
        except ValueError:
            return LogLevel.INFO
    
    def _get_database_config(self) -> DatabaseConfig:
        """
        Get database configuration
        Consolidates duplicate DATABASE_URL configurations from:
        - database_setup.py
        - database.py
        - backup_encryption_setup.py
        - production_health.py
        """
        return DatabaseConfig(
            url=os.getenv(
                "DATABASE_URL",
                "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
            ),
            pool_size=int(os.getenv("DB_POOL_SIZE", "20")),
            max_connections=int(os.getenv("DB_MAX_CONNECTIONS", "20")),
            min_connections=int(os.getenv("DB_MIN_CONNECTIONS", "5")),
            command_timeout=int(os.getenv("DB_COMMAND_TIMEOUT", "60"))
        )
    
    def _get_redis_config(self) -> RedisConfig:
        """
        Get Redis configuration
        Consolidates duplicate Redis configurations from:
        - redis_caching_layer.py
        - scaling/scaling/stateless_backend.py
        """
        return RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "20")),
            socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            socket_connect_timeout=int(os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5"))
        )
    
    def _get_cors_config(self) -> CORSConfig:
        """
        Get CORS configuration
        Consolidates duplicate CORS configurations from:
        - app.py
        - ai-agent/cors_config.py
        - test_app.py
        """
        if self.environment == Environment.PRODUCTION:
            allowed_origins = [
                "https://dedan-mine.vercel.app",
                "https://worldmine.vercel.app",
                "*.vercel.app"
            ]
        else:
            allowed_origins = [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000",
                "https://worldmine.vercel.app"  # For testing production
            ]
        
        return CORSConfig(
            allowed_origins=allowed_origins,
            allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allowed_headers=["*"],
            allow_credentials=True,
            max_age=86400
        )
    
    def _get_security_config(self) -> SecurityConfig:
        """Get security configuration"""
        return SecurityConfig(
            secret_key=os.getenv("SECRET_KEY", self._generate_secret_key()),
            algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
            access_token_expire_minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
            refresh_token_expire_days=int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
            password_hash_rounds=int(os.getenv("PASSWORD_HASH_ROUNDS", "12"))
        )
    
    def _get_api_config(self) -> APIConfig:
        """Get API configuration"""
        return APIConfig(
            title=os.getenv("API_TITLE", "DEDAN 2.0 API"),
            description=os.getenv("API_DESCRIPTION", "World's First Quantum-AI Hybrid Mineral Marketplace"),
            version=os.getenv("API_VERSION", "2.0.0"),
            docs_url=os.getenv("API_DOCS_URL", "/docs"),
            redoc_url=os.getenv("API_REDOC_URL", "/redoc"),
            rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
        )
    
    def _get_external_services_config(self) -> Dict[str, Dict[str, str]]:
        """Get external service configurations"""
        return {
            "stripe": {
                "api_key": os.getenv("STRIPE_API_KEY"),
                "webhook_secret": os.getenv("STRIPE_WEBHOOK_SECRET"),
                "publishable_key": os.getenv("STRIPE_PUBLISHABLE_KEY")
            },
            "paypal": {
                "client_id": os.getenv("PAYPAL_CLIENT_ID"),
                "client_secret": os.getenv("PAYPAL_CLIENT_SECRET"),
                "webhook_secret": os.getenv("PAYPAL_WEBHOOK_SECRET")
            },
            "chapa": {
                "api_key": os.getenv("CHAPA_API_KEY"),
                "webhook_secret": os.getenv("CHAPA_WEBHOOK_SECRET")
            },
            "wise": {
                "api_key": os.getenv("WISE_API_KEY"),
                "webhook_secret": os.getenv("WISE_WEBHOOK_SECRET")
            },
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "model": os.getenv("OPENAI_MODEL", "gpt-4")
            },
            "anthropic": {
                "api_key": os.getenv("ANTHROPIC_API_KEY"),
                "model": os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            },
            "ibm_quantum": {
                "api_key": os.getenv("IBM_QUANTUM_API_KEY"),
                "backend": os.getenv("IBM_QUANTUM_BACKEND", "ibmq_quito")
            }
        }
    
    def _get_feature_flags(self) -> Dict[str, bool]:
        """Get feature flags"""
        return {
            "quantum_settlement": self._get_bool("ENABLE_QUANTUM_SETTLEMENT", True),
            "predictive_fraud_ai": self._get_bool("ENABLE_PREDICTIVE_FRAUD_AI", True),
            "autonomous_market_makers": self._get_bool("ENABLE_AUTONOMOUS_MARKET_MAKERS", True),
            "zero_knowledge_privacy": self._get_bool("ENABLE_ZERO_KNOWLEDGE_PRIVACY", True),
            "blockchain_integration": self._get_bool("ENABLE_BLOCKCHAIN_INTEGRATION", True),
            "ai_market_analysis": self._get_bool("ENABLE_AI_MARKET_ANALYSIS", True),
            "advanced_analytics": self._get_bool("ENABLE_ADVANCED_ANALYTICS", True),
            "multi_language_support": self._get_bool("ENABLE_MULTI_LANGUAGE_SUPPORT", True),
            "mobile_app_support": self._get_bool("ENABLE_MOBILE_APP_SUPPORT", True),
            "api_rate_limiting": self._get_bool("ENABLE_API_RATE_LIMITING", True)
        }
    
    def _generate_secret_key(self) -> str:
        """Generate secret key if not provided"""
        import secrets
        return secrets.token_urlsafe(32)
    
    def get_database_url(self) -> str:
        """Get database URL"""
        return self.database.url
    
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    def is_development(self) -> bool:
        """Check if in development environment"""
        return self.environment == Environment.DEVELOPMENT
    
    def is_production(self) -> bool:
        """Check if in production environment"""
        return self.environment == Environment.PRODUCTION
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled"""
        return self.features.get(feature, False)

# Global settings instance
settings = Settings()

# Backward compatibility functions (to ease migration)
def get_database_url() -> str:
    """Backward compatibility wrapper"""
    return settings.get_database_url()

def get_redis_url() -> str:
    """Backward compatibility wrapper"""
    return settings.get_redis_url()

def get_cors_origins() -> List[str]:
    """Backward compatibility wrapper"""
    return settings.cors.allowed_origins

def is_development() -> bool:
    """Backward compatibility wrapper"""
    return settings.is_development()

def is_production() -> bool:
    """Backward compatibility wrapper"""
    return settings.is_production()
