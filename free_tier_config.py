"""
DEDAN Mine - Free Tier Infrastructure Configuration (v3.1.0)
Zero-Cost Planetary Deployment with World-Class Performance
Neon.tech + Koyeb + EdgeOne + Pay-as-you-earn model
"""

import os
from typing import Dict, Any
from dataclasses import dataclass
from enum import Enum

class InfrastructureProvider(Enum):
    """Free tier infrastructure providers"""
    NEON_TECH = "neon_tech"
    KOYEB = "koyeb"
    RENDER = "render"
    EDGEONE = "edgeone"
    GROQ = "groq"
    GEMINI = "gemini"

class ServiceTier(Enum):
    """Service tiers"""
    FREE = "free"
    PAY_AS_YOU_EARN = "pay_as_you_earn"
    USAGE_BASED = "usage_based"

@dataclass
class NeonConfig:
    """Neon.tech database configuration"""
    project_id: str
    database_url: str
    connection_pool_size: int = 10
    max_connections: int = 20
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {
                "storage_gb": 3,
                "compute_hours": 480,  # 20 hours/day * 24 days
                "active_connections": 20,
                "bandwidth_gb": 100
            }

@dataclass
class KoyebConfig:
    """Koyeb deployment configuration"""
    app_name: str
    region: str = "was"  # Washington DC
    instance_type: str = "nano"
    min_instances: int = 0
    max_instances: int = 1
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {
                "hours_per_month": 720,  # 24 hours/day * 30 days
                "bandwidth_gb": 100,
                "builds_per_month": 500,
                "instances": 1
            }

@dataclass
class EdgeOneConfig:
    """Tencent EdgeOne CDN configuration"""
    domain: str
    origin: str
    cache_ttl: int = 3600
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {
                "bandwidth_gb": 100,
                "requests_per_month": 10000000,
                "ddos_protection": True,
                "ssl_certificates": True
            }

@dataclass
class GroqConfig:
    """Groq AI configuration for free tier"""
    api_key: str
    model: str = "llama3-8b-8192"
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {
                "requests_per_day": 1440,  # 1 per minute
                "tokens_per_day": 100000,
                "concurrent_requests": 1
            }

@dataclass
class GeminiConfig:
    """Google Gemini AI configuration for free tier"""
    api_key: str
    model: str = "gemini-1.5-flash"
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {
                "requests_per_minute": 15,
                "tokens_per_minute": 32000,
                "requests_per_day": 1500
            }

class FreeTierInfrastructure:
    """Free tier infrastructure manager"""
    
    def __init__(self):
        self.configs = {
            "neon": NeonConfig(
                project_id=os.getenv("NEON_PROJECT_ID", ""),
                database_url=os.getenv("NEON_DATABASE_URL", "")
            ),
            "koyeb": KoyebConfig(
                app_name="dedan-mine-api",
                region="was"
            ),
            "edgeone": EdgeOneConfig(
                domain="dedanmine.io",
                origin="https://dedan-mine-api.koyeb.app"
            ),
            "groq": GroqConfig(
                api_key=os.getenv("GROQ_API_KEY", "")
            ),
            "gemini": GeminiConfig(
                api_key=os.getenv("GEMINI_API_KEY", "")
            )
        }
        
        self.cost_optimization_enabled = True
        self.cold_start_optimization = True
        self.auto_scaling_enabled = True
    
    def get_neon_connection_string(self) -> str:
        """Get Neon.tech connection string"""
        return self.configs["neon"].database_url
    
    def get_koyeb_deployment_config(self) -> Dict[str, Any]:
        """Get Koyeb deployment configuration"""
        return {
            "name": self.configs["koyeb"].app_name,
            "region": self.configs["koyeb"].region,
            "instance_type": self.configs["koyeb"].instance_type,
            "min_instances": self.configs["koyeb"].min_instances,
            "max_instances": self.configs["koyeb"].max_instances,
            "env": {
                "DATABASE_URL": self.get_neon_connection_string(),
                "REDIS_URL": "redis://localhost:6379",  # Use local Redis for free tier
                "NODE_ENV": "production"
            },
            "ports": [8000],
            "health_check": {
                "path": "/health",
                "port": 8000,
                "interval": 30,
                "timeout": 10,
                "retries": 3
            },
            "build_command": "pip install -r requirements.txt",
            "run_command": "uvicorn main:app --host 0.0.0.0 --port 8000"
        }
    
    def get_edgeone_cdn_config(self) -> Dict[str, Any]:
        """Get EdgeOne CDN configuration"""
        return {
            "domain": self.configs["edgeone"].domain,
            "origin": self.configs["edgeone"].origin,
            "cache_rules": [
                {
                    "path": "/static/*",
                    "ttl": 86400,  # 24 hours
                    "browser_cache_ttl": 86400
                },
                {
                    "path": "/api/*",
                    "ttl": 300,  # 5 minutes
                    "browser_cache_ttl": 0
                }
            ],
            "compression": {
                "enabled": True,
                "types": ["text/html", "text/css", "application/javascript", "application/json"]
            },
            "security": {
                "ddos_protection": True,
                "ssl": True,
                "https_redirect": True
            }
        }
    
    def get_ai_config(self, provider: str) -> Dict[str, Any]:
        """Get AI provider configuration"""
        if provider == "groq":
            return {
                "api_key": self.configs["groq"].api_key,
                "model": self.configs["groq"].model,
                "base_url": "https://api.groq.com/openai/v1",
                "limits": self.configs["groq"].free_tier_limits
            }
        elif provider == "gemini":
            return {
                "api_key": self.configs["gemini"].api_key,
                "model": self.configs["gemini"].model,
                "base_url": "https://generativelanguage.googleapis.com/v1beta",
                "limits": self.configs["gemini"].free_tier_limits
            }
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")
    
    def get_cold_start_config(self) -> Dict[str, Any]:
        """Get cold start optimization configuration"""
        return {
            "enabled": self.cold_start_optimization,
            "prewarm_instances": 0,
            "startup_timeout": 30,
            "health_check_delay": 10,
            "graceful_shutdown_timeout": 10,
            "keep_alive_interval": 300,  # 5 minutes
            "idle_timeout": 900  # 15 minutes
        }
    
    def get_cost_optimization_config(self) -> Dict[str, Any]:
        """Get cost optimization configuration"""
        return {
            "enabled": self.cost_optimization_enabled,
            "auto_scaling": self.auto_scaling_enabled,
            "resource_monitoring": True,
            "usage_tracking": True,
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 80,
                "bandwidth_usage": 90,
                "database_connections": 80
            }
        }
    
    def get_free_tier_status(self) -> Dict[str, Any]:
        """Get free tier status and limits"""
        return {
            "neon": {
                "provider": "Neon.tech",
                "service": "Serverless PostgreSQL",
                "limits": self.configs["neon"].free_tier_limits,
                "status": "active"
            },
            "koyeb": {
                "provider": "Koyeb",
                "service": "App Platform",
                "limits": self.configs["koyeb"].free_tier_limits,
                "status": "active"
            },
            "edgeone": {
                "provider": "Tencent Cloud",
                "service": "EdgeOne CDN",
                "limits": self.configs["edgeone"].free_tier_limits,
                "status": "active"
            },
            "groq": {
                "provider": "Groq",
                "service": "AI API",
                "limits": self.configs["groq"].free_tier_limits,
                "status": "active"
            },
            "gemini": {
                "provider": "Google",
                "service": "Gemini AI",
                "limits": self.configs["gemini"].free_tier_limits,
                "status": "active"
            }
        }
    
    def get_deployment_manifest(self) -> Dict[str, Any]:
        """Get complete deployment manifest"""
        return {
            "version": "v3.1.0",
            "deployment_type": "zero_cost_planetary",
            "infrastructure": {
                "database": self.get_neon_connection_string(),
                "backend": self.get_koyeb_deployment_config(),
                "cdn": self.get_edgeone_cdn_config(),
                "ai": {
                    "groq": self.get_ai_config("groq"),
                    "gemini": self.get_ai_config("gemini")
                },
                "optimization": {
                    "cold_start": self.get_cold_start_config(),
                    "cost_optimization": self.get_cost_optimization_config()
                }
            },
            "free_tier_status": self.get_free_tier_status(),
            "pay_as_you_earn": {
                "stripe_connect": True,
                "chapa": True,
                "no_fixed_costs": True,
                "usage_based_billing": True
            }
        }

# Global instance
free_tier_infra = FreeTierInfrastructure()

# Environment variables for deployment
def get_production_env_vars() -> Dict[str, str]:
    """Get production environment variables"""
    return {
        # Database
        "DATABASE_URL": free_tier_infra.get_neon_connection_string(),
        
        # AI Services
        "GROQ_API_KEY": free_tier_infra.configs["groq"].api_key,
        "GEMINI_API_KEY": free_tier_infra.configs["gemini"].api_key,
        
        # Payment Services
        "STRIPE_SECRET_KEY": os.getenv("STRIPE_SECRET_KEY", ""),
        "STRIPE_WEBHOOK_SECRET": os.getenv("STRIPE_WEBHOOK_SECRET", ""),
        "CHAPA_API_KEY": os.getenv("CHAPA_API_KEY", ""),
        
        # Infrastructure
        "NODE_ENV": "production",
        "LOG_LEVEL": "INFO",
        
        # Free Tier Optimizations
        "COLD_START_ENABLED": "true",
        "AUTO_SCALING_ENABLED": "true",
        "COST_OPTIMIZATION_ENABLED": "true",
        
        # Service URLs
        "FRONTEND_URL": "https://dedanmine.io",
        "BACKEND_URL": "https://dedan-mine-api.koyeb.app",
        "CDN_URL": "https://dedanmine.io"
    }

def get_deployment_commands() -> Dict[str, str]:
    """Get deployment commands for each service"""
    return {
        "neon": "echo 'Database already configured via connection string'",
        "koyeb": "koyeb app create --name dedan-mine-api --region was --instance-type nano --min-instances 0 --max-instances 1 --port 8000",
        "edgeone": "echo 'Configure via Tencent Cloud console with domain dedanmine.io'",
        "frontend": "cd frontend && npm run build && npx vercel --prod",
        "backend": "pip install -r requirements.txt && koyeb app deploy",
        "monitoring": "koyeb service logs dedan-mine-api --follow"
    }
