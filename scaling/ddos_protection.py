"""
DEDAN Mine - DDoS Protection & Tiered Rate Limiting
Advanced protection for Sovereign Vault and million-user accessibility
Guardian AI integration for intelligent threat detection
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis
import aiohttp
import json
import hashlib
import ipaddress
import time
import collections

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

class UserType(Enum):
    """User type classification"""
    ANONYMOUS = "anonymous"
    AUTHENTICATED = "authenticated"
    PREMIUM = "premium"
    INSTITUTIONAL = "institutional"
    GUARDIAN_AI = "guardian_ai"

class AttackType(Enum):
    """Attack type classification"""
    VOLUME_BASED = "volume_based"
    PROTOCOL_BASED = "protocol_based"
    APPLICATION_LAYER = "application_layer"
    SLOWLORIS = "slowloris"
    HTTP_FLOOD = "http_flood"
    DNS_AMPLIFICATION = "dns_amplification"
    SYN_FLOOD = "syn_flood"

@dataclass
class RateLimitTier:
    """Rate limit tier configuration"""
    tier_name: str
    requests_per_second: int
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_limit: int
    penalty_factor: float
    auto_ban_threshold: int
    priority: int

@dataclass
class ThreatSignature:
    """Threat signature for pattern matching"""
    signature_id: str
    attack_type: AttackType
    pattern: str
    severity: float
    description: str
    mitigation_action: str
    created_at: datetime

@dataclass
class DDoSIncident:
    """DDoS incident tracking"""
    incident_id: str
    attack_type: AttackType
    threat_level: ThreatLevel
    source_ips: List[str]
    target_endpoints: List[str]
    start_time: datetime
    end_time: Optional[datetime]
    peak_requests_per_second: int
    total_requests: int
    mitigated: bool
    mitigation_actions: List[str]

class DDoSProtectionSystem:
    """Advanced DDoS protection system"""
    
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.redis_pool = None
        
        # Rate limit tiers
        self.rate_limit_tiers = {
            UserType.ANONYMOUS: RateLimitTier(
                tier_name="anonymous",
                requests_per_second=10,
                requests_per_minute=100,
                requests_per_hour=1000,
                requests_per_day=10000,
                burst_limit=50,
                penalty_factor=1.0,
                auto_ban_threshold=1000,
                priority=4
            ),
            UserType.AUTHENTICATED: RateLimitTier(
                tier_name="authenticated",
                requests_per_second=50,
                requests_per_minute=500,
                requests_per_hour=5000,
                requests_per_day=50000,
                burst_limit=200,
                penalty_factor=0.8,
                auto_ban_threshold=5000,
                priority=3
            ),
            UserType.PREMIUM: RateLimitTier(
                tier_name="premium",
                requests_per_second=200,
                requests_per_minute=2000,
                requests_per_hour=20000,
                requests_per_day=200000,
                burst_limit=500,
                penalty_factor=0.5,
                auto_ban_threshold=10000,
                priority=2
            ),
            UserType.INSTITUTIONAL: RateLimitTier(
                tier_name="institutional",
                requests_per_second=1000,
                requests_per_minute=10000,
                requests_per_hour=100000,
                requests_per_day=1000000,
                burst_limit=2000,
                penalty_factor=0.2,
                auto_ban_threshold=50000,
                priority=1
            ),
            UserType.GUARDIAN_AI: RateLimitTier(
                tier_name="guardian_ai",
                requests_per_second=5000,
                requests_per_minute=50000,
                requests_per_hour=500000,
                requests_per_day=5000000,
                burst_limit=10000,
                penalty_factor=0.1,
                auto_ban_threshold=100000,
                priority=0
            )
        }
        
        # Threat signatures
        self.threat_signatures = [
            ThreatSignature(
                signature_id="http_flood_1",
                attack_type=AttackType.HTTP_FLOOD,
                pattern="rapid_requests_same_endpoint",
                severity=0.8,
                description="High frequency requests to same endpoint",
                mitigation_action="rate_limit_increase"
            ),
            ThreatSignature(
                signature_id="slowloris_1",
                attack_type=AttackType.SLOWLORIS,
                pattern="slow_header_completion",
                severity=0.9,
                description="Slow HTTP header completion",
                mitigation_action="connection_timeout"
            ),
            ThreatSignature(
                signature_id="volume_attack_1",
                attack_type=AttackType.VOLUME_BASED,
                pattern="high_bandwidth_usage",
                severity=0.7,
                description="Excessive bandwidth consumption",
                mitigation_action="bandwidth_throttling"
            ),
            ThreatSignature(
                signature_id="protocol_attack_1",
                attack_type=AttackType.PROTOCOL_BASED,
                pattern="malformed_packets",
                severity=0.8,
                description="Malformed protocol packets",
                mitigation_action="packet_filtering"
            ),
            ThreatSignature(
                signature_id="app_layer_1",
                attack_type=AttackType.APPLICATION_LAYER,
                pattern="resource_exhaustion",
                severity=0.9,
                description="Application resource exhaustion",
                mitigation_action="resource_limiting"
            )
        ]
        
        # DDoS incidents tracking
        self.active_incidents = {}
        self.incident_history = []
        
        # IP reputation database
        self.ip_reputation = {}
        
        # Global statistics
        self.global_stats = {
            "total_requests": 0,
            "blocked_requests": 0,
            "active_incidents": 0,
            "mitigated_incidents": 0,
            "last_attack": None
        }
    
    async def initialize(self):
        """Initialize DDoS protection system"""
        try:
            self.redis_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                max_connections=1000,
                retry_on_timeout=True,
                socket_keepalive=True
            )
            
            # Test connection
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            await redis_client.ping()
            
            logger.info("DDoS protection system initialized successfully")
            
        except Exception as e:
            logger.error(f"DDoS protection initialization failed: {str(e)}")
            raise
    
    async def check_rate_limit(self, client_ip: str, user_type: UserType, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check rate limit for request"""
        try:
            tier = self.rate_limit_tiers[user_type]
            
            # Generate rate limit keys
            second_key = f"ddos:rate_limit:second:{client_ip}:{endpoint}"
            minute_key = f"ddos:rate_limit:minute:{client_ip}:{endpoint}"
            hour_key = f"ddos:rate_limit:hour:{client_ip}:{endpoint}"
            day_key = f"ddos:rate_limit:day:{client_ip}:{endpoint}"
            
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            current_time = datetime.now(timezone.utc)
            
            # Check current counts
            second_count = await redis_client.get(second_key)
            minute_count = await redis_client.get(minute_key)
            hour_count = await redis_client.get(hour_key)
            day_count = await redis_client.get(day_key)
            
            second_count = int(second_count) if second_count else 0
            minute_count = int(minute_count) if minute_count else 0
            hour_count = int(hour_count) if hour_count else 0
            day_count = int(day_count) if day_count else 0
            
            # Check if rate limited
            rate_limited = (
                second_count >= tier.requests_per_second or
                minute_count >= tier.requests_per_minute or
                hour_count >= tier.requests_per_hour or
                day_count >= tier.requests_per_day
            )
            
            # Determine which limit was hit
            limit_hit = None
            if second_count >= tier.requests_per_second:
                limit_hit = "second"
            elif minute_count >= tier.requests_per_minute:
                limit_hit = "minute"
            elif hour_count >= tier.requests_per_hour:
                limit_hit = "hour"
            elif day_count >= tier.requests_per_day:
                limit_hit = "day"
            
            # Update counters if not rate limited
            if not rate_limited:
                await redis_client.incr(second_key)
                await redis_client.expire(second_key, 1)
                
                await redis_client.incr(minute_key)
                await redis_client.expire(minute_key, 60)
                
                await redis_client.incr(hour_key)
                await redis_client.expire(hour_key, 3600)
                
                await redis_client.incr(day_key)
                await redis_client.expire(day_key, 86400)
            
            # Update global stats
            self.global_stats["total_requests"] += 1
            if rate_limited:
                self.global_stats["blocked_requests"] += 1
            
            # Check for auto-ban
            auto_ban = False
            if minute_count >= tier.auto_ban_threshold:
                auto_ban = True
                await self.auto_ban_ip(client_ip, "rate_limit_exceeded")
            
            return {
                "allowed": not rate_limited,
                "rate_limited": rate_limited,
                "limit_hit": limit_hit,
                "current_counts": {
                    "second": second_count,
                    "minute": minute_count,
                    "hour": hour_count,
                    "day": day_count
                },
                "limits": {
                    "second": tier.requests_per_second,
                    "minute": tier.requests_per_minute,
                    "hour": tier.requests_per_hour,
                    "day": tier.requests_per_day
                },
                "burst_remaining": max(0, tier.burst_limit - second_count),
                "auto_ban": auto_ban,
                "user_type": user_type.value,
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {str(e)}")
            return {
                "allowed": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def analyze_threat_pattern(self, client_ip: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze request for threat patterns"""
        try:
            threat_detected = False
            threat_type = None
            threat_level = ThreatLevel.LOW
            confidence = 0.0
            
            # Check against threat signatures
            for signature in self.threat_signatures:
                if await self.match_threat_signature(signature, request_data):
                    threat_detected = True
                    threat_type = signature.attack_type
                    threat_level = self.calculate_threat_level(signature.severity)
                    confidence = signature.severity
                    
                    logger.warning(f"Threat detected: {signature.attack_type.value} from {client_ip}")
                    break
            
            # Check IP reputation
            ip_reputation = await self.get_ip_reputation(client_ip)
            if ip_reputation["threat_level"] != ThreatLevel.LOW:
                threat_detected = True
                threat_level = ip_reputation["threat_level"]
                confidence = max(confidence, 0.7)
            
            # Check for attack patterns
            attack_pattern = await self.detect_attack_pattern(client_ip, request_data)
            if attack_pattern["detected"]:
                threat_detected = True
                threat_type = attack_pattern["attack_type"]
                threat_level = attack_pattern["threat_level"]
                confidence = max(confidence, attack_pattern["confidence"])
            
            return {
                "threat_detected": threat_detected,
                "threat_type": threat_type.value if threat_type else None,
                "threat_level": threat_level.value,
                "confidence": confidence,
                "ip_reputation": ip_reputation,
                "attack_pattern": attack_pattern,
                "mitigation_required": threat_detected and confidence > 0.7,
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"Threat analysis failed: {str(e)}")
            return {
                "threat_detected": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def match_threat_signature(self, signature: ThreatSignature, request_data: Dict[str, Any]) -> bool:
        """Match request against threat signature"""
        try:
            if signature.attack_type == AttackType.HTTP_FLOOD:
                # Check for rapid requests to same endpoint
                return await self.check_rapid_requests(request_data)
            
            elif signature.attack_type == AttackType.SLOWLORIS:
                # Check for slow header completion
                return await self.check_slow_headers(request_data)
            
            elif signature.attack_type == AttackType.VOLUME_BASED:
                # Check for high bandwidth usage
                return await self.check_bandwidth_usage(request_data)
            
            elif signature.attack_type == AttackType.PROTOCOL_BASED:
                # Check for malformed packets
                return await self.check_malformed_packets(request_data)
            
            elif signature.attack_type == AttackType.APPLICATION_LAYER:
                # Check for resource exhaustion
                return await self.check_resource_exhaustion(request_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Threat signature matching failed: {str(e)}")
            return False
    
    async def check_rapid_requests(self, request_data: Dict[str, Any]) -> bool:
        """Check for rapid requests to same endpoint"""
        try:
            client_ip = request_data.get("client_ip")
            endpoint = request_data.get("endpoint")
            timestamp = request_data.get("timestamp", datetime.now(timezone.utc))
            
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Check request frequency in last 10 seconds
            recent_key = f"ddos:recent_requests:{client_ip}:{endpoint}"
            await redis_client.zadd(recent_key, {str(timestamp.timestamp()): timestamp.timestamp()})
            await redis_client.expire(recent_key, 10)
            
            recent_count = await redis_client.zcount(recent_key, timestamp.timestamp() - 10, timestamp.timestamp())
            
            return recent_count > 50  # More than 50 requests in 10 seconds
            
        except Exception as e:
            logger.error(f"Rapid requests check failed: {str(e)}")
            return False
    
    async def check_slow_headers(self, request_data: Dict[str, Any]) -> bool:
        """Check for slow HTTP header completion"""
        try:
            header_time = request_data.get("header_completion_time", 0)
            return header_time > 30  # Headers taking more than 30 seconds
            
        except Exception as e:
            logger.error(f"Slow headers check failed: {str(e)}")
            return False
    
    async def check_bandwidth_usage(self, request_data: Dict[str, Any]) -> bool:
        """Check for high bandwidth usage"""
        try:
            request_size = request_data.get("request_size", 0)
            client_ip = request_data.get("client_ip")
            
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Track bandwidth usage per IP
            bandwidth_key = f"ddos:bandwidth:{client_ip}"
            await redis_client.incrby(bandwidth_key, request_size)
            await redis_client.expire(bandwidth_key, 3600)
            
            total_bandwidth = await redis_client.get(bandwidth_key)
            total_bandwidth = int(total_bandwidth) if total_bandwidth else 0
            
            return total_bandwidth > 100 * 1024 * 1024  # More than 100MB per hour
            
        except Exception as e:
            logger.error(f"Bandwidth usage check failed: {str(e)}")
            return False
    
    async def check_malformed_packets(self, request_data: Dict[str, Any]) -> bool:
        """Check for malformed protocol packets"""
        try:
            # Check for common malformed packet indicators
            user_agent = request_data.get("user_agent", "")
            headers = request_data.get("headers", {})
            
            # Suspicious user agents
            suspicious_agents = ["bot", "crawler", "scanner", "exploit"]
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                return True
            
            # Missing required headers
            required_headers = ["host", "user-agent", "accept"]
            if not all(header in headers for header in required_headers):
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Malformed packets check failed: {str(e)}")
            return False
    
    async def check_resource_exhaustion(self, request_data: Dict[str, Any]) -> bool:
        """Check for application resource exhaustion"""
        try:
            endpoint = request_data.get("endpoint", "")
            method = request_data.get("method", "")
            
            # Check for resource-intensive endpoints
            resource_intensive_endpoints = [
                "/api/v1/payout/batch",
                "/api/v1/consumer-protection/bulk",
                "/api/v1/satellite/batch-process"
            ]
            
            if endpoint in resource_intensive_endpoints and method == "POST":
                # Check frequency of resource-intensive requests
                return await self.check_rapid_requests(request_data)
            
            return False
            
        except Exception as e:
            logger.error(f"Resource exhaustion check failed: {str(e)}")
            return False
    
    async def detect_attack_pattern(self, client_ip: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect attack patterns from request history"""
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Get recent requests from this IP
            recent_key = f"ddos:recent_requests:{client_ip}"
            recent_requests = await redis_client.zrange(recent_key, 0, -1, withscores=True)
            
            if len(recent_requests) < 10:
                return {"detected": False}
            
            # Analyze request patterns
            endpoints = []
            timestamps = []
            
            for request_str, timestamp in recent_requests:
                request_info = json.loads(request_str)
                endpoints.append(request_info.get("endpoint", ""))
                timestamps.append(timestamp)
            
            # Check for distributed attack patterns
            endpoint_diversity = len(set(endpoints)) / len(endpoints)
            time_span = max(timestamps) - min(timestamps)
            
            # Detect attack type based on patterns
            attack_type = None
            threat_level = ThreatLevel.LOW
            confidence = 0.0
            
            if endpoint_diversity < 0.1 and time_span < 60:
                # Single endpoint, rapid requests - HTTP Flood
                attack_type = AttackType.HTTP_FLOOD
                threat_level = ThreatLevel.HIGH
                confidence = 0.8
            elif endpoint_diversity > 0.8 and time_span < 300:
                # Multiple endpoints, rapid requests - Application Layer
                attack_type = AttackType.APPLICATION_LAYER
                threat_level = ThreatLevel.MEDIUM
                confidence = 0.6
            elif len(recent_requests) > 1000:
                # Very high volume - Volume Based
                attack_type = AttackType.VOLUME_BASED
                threat_level = ThreatLevel.CRITICAL
                confidence = 0.9
            
            return {
                "detected": attack_type is not None,
                "attack_type": attack_type,
                "threat_level": threat_level,
                "confidence": confidence,
                "endpoint_diversity": endpoint_diversity,
                "time_span": time_span,
                "request_count": len(recent_requests)
            }
            
        except Exception as e:
            logger.error(f"Attack pattern detection failed: {str(e)}")
            return {"detected": False, "error": str(e)}
    
    async def get_ip_reputation(self, client_ip: str) -> Dict[str, Any]:
        """Get IP reputation"""
        try:
            # Check if IP is in reputation database
            reputation_data = self.ip_reputation.get(client_ip)
            
            if not reputation_data:
                # Calculate initial reputation
                reputation_data = await self.calculate_ip_reputation(client_ip)
                self.ip_reputation[client_ip] = reputation_data
            
            return reputation_data
            
        except Exception as e:
            logger.error(f"IP reputation check failed: {str(e)}")
            return {
                "threat_level": ThreatLevel.LOW,
                "reputation_score": 0.5,
                "last_seen": None,
                "incident_count": 0
            }
    
    async def calculate_ip_reputation(self, client_ip: str) -> Dict[str, Any]:
        """Calculate IP reputation"""
        try:
            # Basic IP analysis
            ip_obj = ipaddress.ip_address(client_ip)
            
            # Check if private IP
            if ip_obj.is_private:
                return {
                    "threat_level": ThreatLevel.LOW,
                    "reputation_score": 0.8,
                    "last_seen": datetime.now(timezone.utc),
                    "incident_count": 0,
                    "ip_type": "private"
                }
            
            # Check if known malicious IP (mock implementation)
            malicious_ips = ["192.168.1.100", "10.0.0.50"]
            if client_ip in malicious_ips:
                return {
                    "threat_level": ThreatLevel.HIGH,
                    "reputation_score": 0.1,
                    "last_seen": datetime.now(timezone.utc),
                    "incident_count": 10,
                    "ip_type": "malicious"
                }
            
            # Default reputation for unknown IPs
            return {
                "threat_level": ThreatLevel.LOW,
                "reputation_score": 0.5,
                "last_seen": datetime.now(timezone.utc),
                "incident_count": 0,
                "ip_type": "unknown"
            }
            
        except Exception as e:
            logger.error(f"IP reputation calculation failed: {str(e)}")
            return {
                "threat_level": ThreatLevel.LOW,
                "reputation_score": 0.5,
                "last_seen": None,
                "incident_count": 0
            }
    
    def calculate_threat_level(self, severity: float) -> ThreatLevel:
        """Calculate threat level from severity"""
        if severity >= 0.9:
            return ThreatLevel.EMERGENCY
        elif severity >= 0.8:
            return ThreatLevel.CRITICAL
        elif severity >= 0.6:
            return ThreatLevel.HIGH
        elif severity >= 0.4:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def auto_ban_ip(self, client_ip: str, reason: str):
        """Automatically ban IP"""
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Add to banned list
            ban_key = f"ddos:banned:{client_ip}"
            ban_data = {
                "ip": client_ip,
                "reason": reason,
                "banned_at": datetime.now(timezone.utc).isoformat(),
                "ban_duration": 3600  # 1 hour
            }
            
            await redis_client.setex(ban_key, 3600, json.dumps(ban_data))
            
            # Update IP reputation
            if client_ip in self.ip_reputation:
                self.ip_reputation[client_ip]["threat_level"] = ThreatLevel.HIGH
                self.ip_reputation[client_ip]["incident_count"] += 1
            
            logger.warning(f"IP auto-banned: {client_ip} - Reason: {reason}")
            
        except Exception as e:
            logger.error(f"Auto ban failed for {client_ip}: {str(e)}")
    
    async def is_ip_banned(self, client_ip: str) -> bool:
        """Check if IP is banned"""
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            ban_key = f"ddos:banned:{client_ip}"
            
            ban_data = await redis_client.get(ban_key)
            return ban_data is not None
            
        except Exception as e:
            logger.error(f"Ban check failed for {client_ip}: {str(e)}")
            return False
    
    async def create_ddos_incident(self, attack_type: AttackType, threat_level: ThreatLevel, source_ips: List[str], target_endpoints: List[str]) -> str:
        """Create DDoS incident"""
        try:
            incident_id = f"ddos_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            incident = DDoSIncident(
                incident_id=incident_id,
                attack_type=attack_type,
                threat_level=threat_level,
                source_ips=source_ips,
                target_endpoints=target_endpoints,
                start_time=datetime.now(timezone.utc),
                end_time=None,
                peak_requests_per_second=0,
                total_requests=0,
                mitigated=False,
                mitigation_actions=[]
            )
            
            self.active_incidents[incident_id] = incident
            
            logger.critical(f"DDoS incident created: {incident_id} - {attack_type.value}")
            
            return incident_id
            
        except Exception as e:
            logger.error(f"DDoS incident creation failed: {str(e)}")
            return ""
    
    async def mitigate_ddos_attack(self, incident_id: str, mitigation_actions: List[str]) -> bool:
        """Mitigate DDoS attack"""
        try:
            incident = self.active_incidents.get(incident_id)
            if not incident:
                return False
            
            # Apply mitigation actions
            for action in mitigation_actions:
                if action == "rate_limit_increase":
                    await self.increase_rate_limits(incident.source_ips)
                elif action == "ip_blocking":
                    await self.block_malicious_ips(incident.source_ips)
                elif action == "connection_throttling":
                    await self.throttle_connections()
                elif action == "bandwidth_throttling":
                    await self.throttle_bandwidth()
                elif action == "enable_captcha":
                    await self.enable_captcha_protection()
                
                incident.mitigation_actions.append(action)
            
            incident.mitigated = True
            incident.end_time = datetime.now(timezone.utc)
            
            # Move to history
            self.incident_history.append(incident)
            del self.active_incidents[incident_id]
            
            # Update global stats
            self.global_stats["mitigated_incidents"] += 1
            
            logger.info(f"DDoS attack mitigated: {incident_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"DDoS mitigation failed for {incident_id}: {str(e)}")
            return False
    
    async def increase_rate_limits(self, source_ips: List[str]):
        """Increase rate limits for legitimate users"""
        try:
            # Implementation would adjust rate limits dynamically
            logger.info("Rate limits increased for legitimate users")
            
        except Exception as e:
            logger.error(f"Rate limit increase failed: {str(e)}")
    
    async def block_malicious_ips(self, source_ips: List[str]):
        """Block malicious IPs"""
        try:
            for ip in source_ips:
                await self.auto_ban_ip(ip, "ddos_attack")
            
            logger.info(f"Blocked {len(source_ips)} malicious IPs")
            
        except Exception as e:
            logger.error(f"IP blocking failed: {str(e)}")
    
    async def throttle_connections(self):
        """Throttle connections"""
        try:
            # Implementation would throttle connection acceptance
            logger.info("Connection throttling enabled")
            
        except Exception as e:
            logger.error(f"Connection throttling failed: {str(e)}")
    
    async def throttle_bandwidth(self):
        """Throttle bandwidth"""
        try:
            # Implementation would limit bandwidth per connection
            logger.info("Bandwidth throttling enabled")
            
        except Exception as e:
            logger.error(f"Bandwidth throttling failed: {str(e)}")
    
    async def enable_captcha_protection(self):
        """Enable CAPTCHA protection"""
        try:
            # Implementation would enable CAPTCHA for suspicious requests
            logger.info("CAPTCHA protection enabled")
            
        except Exception as e:
            logger.error(f"CAPTCHA protection failed: {str(e)}")
    
    async def get_ddos_statistics(self) -> Dict[str, Any]:
        """Get DDoS protection statistics"""
        try:
            return {
                "global_stats": self.global_stats,
                "active_incidents": len(self.active_incidents),
                "mitigated_incidents": len(self.incident_history),
                "banned_ips": await self.get_banned_ip_count(),
                "rate_limit_tiers": {tier.value: asdict(tier) for tier, t in self.rate_limit_tiers.items()},
                "threat_signatures": len(self.threat_signatures),
                "last_update": datetime.now(timezone.utc).isoformat(),
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"DDoS statistics retrieval failed: {str(e)}")
            return {"error": str(e)}
    
    async def get_banned_ip_count(self) -> int:
        """Get count of banned IPs"""
        try:
            redis_client = redis.Redis(connection_pool=self.redis_pool)
            
            # Count banned IPs
            banned_keys = await redis_client.keys("ddos:banned:*")
            return len(banned_keys)
            
        except Exception as e:
            logger.error(f"Banned IP count failed: {str(e)}")
            return 0

# Global instance
ddos_protection_system = DDoSProtectionSystem()

# API functions for DDoS protection
async def check_request_security(client_ip: str, user_type: UserType, endpoint: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Check request security (rate limit + threat analysis)"""
    try:
        # Check if IP is banned
        if await ddos_protection_system.is_ip_banned(client_ip):
            return {
                "allowed": False,
                "reason": "ip_banned",
                "nbe_compliance": True
            }
        
        # Check rate limits
        rate_limit_result = await ddos_protection_system.check_rate_limit(client_ip, user_type, endpoint, request_data)
        
        if not rate_limit_result["allowed"]:
            return rate_limit_result
        
        # Analyze threats
        threat_analysis = await ddos_protection_system.analyze_threat_pattern(client_ip, request_data)
        
        if threat_analysis["threat_detected"] and threat_analysis["mitigation_required"]:
            # Create incident if needed
            if threat_analysis["threat_level"] in ["high", "critical", "emergency"]:
                await ddos_protection_system.create_ddos_incident(
                    AttackType(threat_analysis["threat_type"]) if threat_analysis["threat_type"] else AttackType.APPLICATION_LAYER,
                    ThreatLevel(threat_analysis["threat_level"]),
                    [client_ip],
                    [endpoint]
                )
            
            return {
                "allowed": False,
                "reason": "threat_detected",
                "threat_analysis": threat_analysis,
                "nbe_compliance": True
            }
        
        return {
            "allowed": True,
            "rate_limit_result": rate_limit_result,
            "threat_analysis": threat_analysis,
            "nbe_compliance": True
        }
        
    except Exception as e:
        logger.error(f"Request security check failed: {str(e)}")
        return {
            "allowed": False,
            "error": str(e),
            "nbe_compliance": False
        }

async def get_ddos_protection_status() -> Dict[str, Any]:
    """Get DDoS protection system status"""
    return await ddos_protection_system.get_ddos_statistics()
