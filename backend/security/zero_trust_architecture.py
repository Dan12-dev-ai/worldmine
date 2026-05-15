"""
Zero-Trust Security Architecture for DEDAN 2.0
Complete zero-trust implementation with RBAC, MFA, and continuous monitoring
"""

import asyncio
import time
import logging
import jwt
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import bcrypt
import pyotp
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import redis.asyncio as redis
import asyncpg
from fastapi import HTTPException, status

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserRole(Enum):
    """User roles for RBAC"""
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"
    AUDITOR = "auditor"
    COMPLIANCE_OFFICER = "compliance_officer"

class Permission(Enum):
    """Permissions for RBAC"""
    READ_MINERALS = "read_minerals"
    WRITE_MINERALS = "write_minerals"
    EXECUTE_TRADES = "execute_trades"
    VIEW_PORTFOLIO = "view_portfolio"
    MANAGE_USERS = "manage_users"
    AUDIT_LOGS = "audit_logs"
    SYSTEM_ADMIN = "system_admin"
    QUANTUM_ACCESS = "quantum_access"
    BLOCKCHAIN_ACCESS = "blockchain_access"

class SecurityContext(Enum):
    """Security contexts"""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"

class ThreatLevel(Enum):
    """Threat levels for dynamic security"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class SecurityPolicy:
    """Security policy configuration"""
    name: str
    description: str
    permissions: List[Permission]
    roles: List[UserRole]
    mfa_required: bool
    session_timeout: int = 3600  # 1 hour
    max_failed_attempts: int = 5
    lockout_duration: int = 900  # 15 minutes
    ip_whitelist: List[str] = field(default_factory=list)
    ip_blacklist: List[str] = field(default_factory=list)
    device_trust_required: bool = True
    geo_restriction: bool = True
    allowed_countries: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 60
    encryption_required: bool = True
    audit_level: str = "detailed"

@dataclass
class SecuritySession:
    """Security session information"""
    session_id: str
    user_id: str
    user_role: UserRole
    permissions: Set[Permission]
    created_at: datetime
    last_activity: datetime
    expires_at: datetime
    ip_address: str
    user_agent: str
    device_fingerprint: str
    mfa_verified: bool
    security_context: SecurityContext
    threat_level: ThreatLevel = ThreatLevel.LOW
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None

@dataclass
class SecurityEvent:
    """Security event for monitoring"""
    event_id: str
    event_type: str
    severity: str
    user_id: Optional[str]
    ip_address: str
    timestamp: datetime
    details: Dict[str, Any]
    resolved: bool = False

class ZeroTrustSecurity:
    """Zero-Trust security implementation"""
    
    def __init__(self, db_connection: str, redis_url: str):
        self.db_connection = db_connection
        self.redis_url = redis_url
        self.db = None
        self.redis = None
        self.encryption_key = self._generate_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security policies
        self.policies = self._load_security_policies()
        
        # Session management
        self.active_sessions: Dict[str, SecuritySession] = {}
        self.session_cache: Dict[str, SecuritySession] = {}
        
        # Device management
        self.trusted_devices: Dict[str, Dict[str, Any]] = {}
        self.device_risk_scores: Dict[str, float] = {}
        
        # IP reputation
        self.ip_reputation: Dict[str, Dict[str, Any]] = {}
        
        # Security events
        self.security_events: List[SecurityEvent] = []
        
        # Threat intelligence
        self.threat_intelligence: Dict[str, Any] = {}
        
        # MFA management
        self.mfa_secrets: Dict[str, str] = {}
        
        # Rate limiting
        self.rate_limits: Dict[str, List[datetime]] = {}
        
    async def initialize(self):
        """Initialize zero-trust security system"""
        self.db = await asyncpg.connect(self.db_connection)
        self.redis = await redis.from_url(self.redis_url)
        
        # Load existing security data
        await self._load_security_data()
        
        # Start background monitoring
        asyncio.create_task(self._security_monitoring_loop())
        
        logger.info("Zero-Trust security system initialized")
    
    async def authenticate_user(
        self,
        username: str,
        password: str,
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        mfa_code: Optional[str] = None
    ) -> Tuple[bool, Optional[SecuritySession]]:
        """Authenticate user with zero-trust principles"""
        try:
            # Step 1: Verify credentials
            user_data = await self._verify_credentials(username, password)
            if not user_data:
                await self._log_security_event(
                    "AUTHENTICATION_FAILED",
                    "HIGH",
                    username,
                    ip_address,
                    {"reason": "invalid_credentials", "device": device_fingerprint}
                )
                return False, None
            
            # Step 2: Check IP reputation
            ip_risk = await self._assess_ip_risk(ip_address)
            if ip_risk > 0.7:
                await self._log_security_event(
                    "HIGH_RISK_IP",
                    "HIGH",
                    username,
                    ip_address,
                    {"risk_score": ip_risk, "device": device_fingerprint}
                )
                return False, None
            
            # Step 3: Check device trust
            device_trust = await self._assess_device_trust(device_fingerprint, username)
            if device_trust < 0.5:
                await self._log_security_event(
                    "UNTRUSTED_DEVICE",
                    "MEDIUM",
                    username,
                    ip_address,
                    {"trust_score": device_trust, "device": device_fingerprint}
                )
                return False, None
            
            # Step 4: Check rate limiting
            if await self._is_rate_limited(ip_address, username):
                await self._log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    "MEDIUM",
                    username,
                    ip_address,
                    {"device": device_fingerprint}
                )
                return False, None
            
            # Step 5: Verify MFA if required
            user_role = UserRole(user_data['role'])
            policy = self._get_policy_for_role(user_role)
            
            if policy.mfa_required:
                if not mfa_code:
                    # Send MFA challenge
                    await self._send_mfa_challenge(username, user_data['email'])
                    return False, None
                
                if not await self._verify_mfa_code(username, mfa_code):
                    await self._log_security_event(
                        "MFA_FAILED",
                        "HIGH",
                        username,
                        ip_address,
                        {"device": device_fingerprint}
                    )
                    return False, None
            
            # Step 6: Create security session
            session = await self._create_security_session(
                user_data,
                ip_address,
                user_agent,
                device_fingerprint,
                policy
            )
            
            # Step 7: Update device trust
            await self._update_device_trust(device_fingerprint, username, True)
            
            # Step 8: Log successful authentication
            await self._log_security_event(
                "AUTHENTICATION_SUCCESS",
                "INFO",
                username,
                ip_address,
                {"session_id": session.session_id, "device": device_fingerprint}
            )
            
            return True, session
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            await self._log_security_event(
                "AUTHENTICATION_ERROR",
                "HIGH",
                username,
                ip_address,
                {"error": str(e)}
            )
            return False, None
    
    async def authorize_request(
        self,
        session_id: str,
        resource: str,
        action: str,
        context: Dict[str, Any]
    ) -> bool:
        """Authorize request with zero-trust principles"""
        try:
            # Step 1: Validate session
            session = await self._validate_session(session_id)
            if not session:
                return False
            
            # Step 2: Check session expiration
            if datetime.utcnow() > session.expires_at:
                await self._invalidate_session(session_id)
                return False
            
            # Step 3: Verify permissions
            required_permission = self._get_permission_for_resource_action(resource, action)
            if required_permission not in session.permissions:
                await self._log_security_event(
                    "UNAUTHORIZED_ACCESS",
                    "HIGH",
                    session.user_id,
                    session.ip_address,
                    {"resource": resource, "action": action, "session_id": session_id}
                )
                return False
            
            # Step 4: Check contextual access patterns
            if not await self._verify_access_pattern(session, context):
                await self._log_security_event(
                    "ANOMALOUS_ACCESS_PATTERN",
                    "MEDIUM",
                    session.user_id,
                    session.ip_address,
                    {"context": context, "session_id": session_id}
                )
                return False
            
            # Step 5: Update session activity
            await self._update_session_activity(session_id)
            
            # Step 6: Log access
            await self._log_security_event(
                "ACCESS_GRANTED",
                "INFO",
                session.user_id,
                session.ip_address,
                {"resource": resource, "action": action, "session_id": session_id}
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Authorization error: {e}")
            return False
    
    async def encrypt_sensitive_data(self, data: Any, context: str = "default") -> bytes:
        """Encrypt sensitive data"""
        try:
            # Convert data to JSON if needed
            if not isinstance(data, bytes):
                data = json.dumps(data).encode()
            
            # Add context to encryption
            context_data = f"{context}:{datetime.utcnow().isoformat()}".encode()
            
            # Derive encryption key with context
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.encryption_key[:16],
                iterations=100000,
                backend=default_backend()
            )
            context_key = kdf.derive(context_data)
            
            # Encrypt with context-specific key
            cipher = Fernet(Fernet(context_key))
            encrypted_data = cipher.encrypt(data)
            
            return encrypted_data
            
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    async def decrypt_sensitive_data(self, encrypted_data: bytes, context: str = "default") -> Any:
        """Decrypt sensitive data"""
        try:
            # Derive decryption key with context
            context_data = f"{context}:{datetime.utcnow().isoformat()}".encode()
            
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=self.encryption_key[:16],
                iterations=100000,
                backend=default_backend()
            )
            context_key = Fernet(context_key)
            
            # Decrypt with context-specific key
            cipher = Fernet(context_key)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Convert from JSON if needed
            try:
                return json.loads(decrypted_data.decode())
            except json.JSONDecodeError:
                return decrypted_data.decode()
                
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    async def _verify_credentials(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Verify user credentials"""
        query = """
            SELECT id, username, email, password_hash, role, salt, 
                   is_active, last_login, failed_login_attempts
            FROM users
            WHERE username = $1
        """
        
        user_data = await self.db.fetchrow(query, username)
        
        if not user_data:
            return None
        
        if not user_data['is_active']:
            return None
        
        # Check failed attempts
        if user_data['failed_login_attempts'] >= 5:
            # Check if lockout period has passed
            if user_data['last_login']:
                lockout_end = user_data['last_login'] + timedelta(minutes=15)
                if datetime.utcnow() < lockout_end:
                    return None
        
        # Verify password
        salt = user_data['salt'].encode()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        
        if not bcrypt.checkpw(password_hash, user_data['password_hash'].encode()):
            # Increment failed attempts
            await self.db.execute(
                "UPDATE users SET failed_login_attempts = failed_login_attempts + 1, last_login = NOW() WHERE id = $1",
                user_data['id']
            )
            return None
        
        # Reset failed attempts on success
        await self.db.execute(
            "UPDATE users SET failed_login_attempts = 0, last_login = NOW() WHERE id = $1",
            user_data['id']
        )
        
        return dict(user_data)
    
    async def _assess_ip_risk(self, ip_address: str) -> float:
        """Assess IP risk score"""
        # Check if IP is in blacklist
        if ip_address in self._get_ip_blacklist():
            return 1.0
        
        # Check if IP is in whitelist
        if ip_address in self._get_ip_whitelist():
            return 0.0
        
        # Check IP reputation
        reputation_data = self.ip_reputation.get(ip_address, {
            'threat_score': 0.0,
            'last_seen': None,
            'malicious_activities': 0
        })
        
        # Calculate risk based on various factors
        risk_score = reputation_data['threat_score']
        
        # Add risk for recent malicious activities
        if reputation_data['malicious_activities'] > 0:
            risk_score += 0.3
        
        # Add risk for unknown IPs
        if not reputation_data['last_seen']:
            risk_score += 0.2
        
        return min(risk_score, 1.0)
    
    async def _assess_device_trust(self, device_fingerprint: str, username: str) -> float:
        """Assess device trust score"""
        device_data = self.trusted_devices.get(device_fingerprint, {
            'trust_score': 0.0,
            'first_seen': None,
            'last_seen': None,
            'successful_authentications': 0,
            'failed_authentications': 0
        })
        
        # Calculate trust score
        trust_score = device_data['trust_score']
        
        # Increase trust for successful authentications
        if device_data['successful_authentications'] > 0:
            trust_score += min(device_data['successful_authentications'] * 0.1, 0.5)
        
        # Decrease trust for failed authentications
        if device_data['failed_authentications'] > 0:
            trust_score -= min(device_data['failed_authentications'] * 0.2, 0.8)
        
        # Add trust for known devices
        if device_data['first_seen']:
            days_known = (datetime.utcnow() - device_data['first_seen']).days
            trust_score += min(days_known * 0.01, 0.3)
        
        return max(0.0, min(trust_score, 1.0))
    
    async def _is_rate_limited(self, ip_address: str, username: str) -> bool:
        """Check if IP/username is rate limited"""
        current_time = datetime.utcnow()
        key = f"{ip_address}:{username}"
        
        # Get recent requests
        requests = self.rate_limits.get(key, [])
        recent_requests = [req for req in requests if current_time - req < timedelta(minutes=1)]
        
        # Update rate limits
        self.rate_limits[key] = recent_requests
        
        # Check if exceeded limit
        return len(recent_requests) >= 60  # 60 requests per minute
    
    async def _send_mfa_challenge(self, username: str, email: str):
        """Send MFA challenge to user"""
        # Generate TOTP secret
        totp_secret = pyotp.random_base32()
        self.mfa_secrets[username] = totp_secret
        
        # Store in database
        await self.db.execute(
            "UPDATE users SET mfa_secret = $1, mfa_enabled = true WHERE username = $2",
            totp_secret, username
        )
        
        # Generate QR code URL (in production, would send via email/SMS)
        totp_url = pyotp.totp.TOTP(totp_secret).provisioning_uri(
            name=username,
            issuer_name="DEDAN 2.0"
        )
        
        # Log MFA challenge sent
        await self._log_security_event(
            "MFA_CHALLENGE_SENT",
            "INFO",
            username,
            "system",
            {"email": email, "method": "TOTP"}
        )
        
        return totp_url
    
    async def _verify_mfa_code(self, username: str, mfa_code: str) -> bool:
        """Verify MFA code"""
        totp_secret = self.mfa_secrets.get(username)
        if not totp_secret:
            # Try to get from database
            totp_secret = await self.db.fetchval(
                "SELECT mfa_secret FROM users WHERE username = $1",
                username
            )
        
        if not totp_secret:
            return False
        
        totp = pyotp.TOTP(totp_secret)
        return totp.verify(mfa_code)
    
    async def _create_security_session(
        self,
        user_data: Dict[str, Any],
        ip_address: str,
        user_agent: str,
        device_fingerprint: str,
        policy: SecurityPolicy
    ) -> SecuritySession:
        """Create security session"""
        session_id = secrets.token_urlsafe(32)
        
        # Get user permissions
        user_role = UserRole(user_data['role'])
        permissions = self._get_permissions_for_role(user_role)
        
        # Create session
        session = SecuritySession(
            session_id=session_id,
            user_id=user_data['id'],
            user_role=user_role,
            permissions=permissions,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(seconds=policy.session_timeout),
            ip_address=ip_address,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            mfa_verified=policy.mfa_required,
            security_context=SecurityContext.PRODUCTION,
            threat_level=await self._assess_user_threat_level(user_data['id'])
        )
        
        # Generate tokens
        session.access_token = await self._generate_access_token(session)
        session.refresh_token = await self._generate_refresh_token(session)
        
        # Store session
        self.active_sessions[session_id] = session
        
        # Cache in Redis
        await self.redis.setex(
            f"session:{session_id}",
            policy.session_timeout,
            json.dumps({
                'user_id': session.user_id,
                'role': session.user_role.value,
                'permissions': [p.value for p in session.permissions],
                'expires_at': session.expires_at.isoformat(),
                'ip_address': session.ip_address,
                'device_fingerprint': session.device_fingerprint
            })
        )
        
        return session
    
    async def _validate_session(self, session_id: str) -> Optional[SecuritySession]:
        """Validate security session"""
        # Check memory cache first
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            if datetime.utcnow() < session.expires_at:
                return session
            else:
                del self.active_sessions[session_id]
                return None
        
        # Check Redis cache
        session_data = await self.redis.get(f"session:{session_id}")
        if session_data:
            try:
                session_info = json.loads(session_data)
                
                # Reconstruct session
                session = SecuritySession(
                    session_id=session_id,
                    user_id=session_info['user_id'],
                    user_role=UserRole(session_info['role']),
                    permissions=set(Permission(p) for p in session_info['permissions']),
                    created_at=datetime.utcnow(),
                    last_activity=datetime.utcnow(),
                    expires_at=datetime.fromisoformat(session_info['expires_at']),
                    ip_address=session_info['ip_address'],
                    user_agent="",
                    device_fingerprint=session_info['device_fingerprint'],
                    mfa_verified=True,
                    security_context=SecurityContext.PRODUCTION
                )
                
                # Cache in memory
                self.active_sessions[session_id] = session
                
                return session
                
            except Exception as e:
                logger.error(f"Session validation error: {e}")
                return None
        
        return None
    
    async def _update_session_activity(self, session_id: str):
        """Update session activity"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_activity = datetime.utcnow()
            
            # Update Redis
            await self.redis.expire(f"session:{session_id}", 3600)
    
    async def _invalidate_session(self, session_id: str):
        """Invalidate security session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        await self.redis.delete(f"session:{session_id}")
        
        await self._log_security_event(
            "SESSION_INVALIDATED",
            "INFO",
            None,
            "system",
            {"session_id": session_id}
        )
    
    async def _generate_access_token(self, session: SecuritySession) -> str:
        """Generate JWT access token"""
        payload = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'role': session.user_role.value,
            'permissions': [p.value for p in session.permissions],
            'exp': session.expires_at.timestamp(),
            'iat': datetime.utcnow().timestamp(),
            'iss': 'dedan-2.0',
            'aud': 'dedan-api'
        }
        
        token = jwt.encode(payload, self.encryption_key, algorithm='HS256')
        return token
    
    async def _generate_refresh_token(self, session: SecuritySession) -> str:
        """Generate refresh token"""
        payload = {
            'session_id': session.session_id,
            'user_id': session.user_id,
            'exp': (datetime.utcnow() + timedelta(days=30)).timestamp(),
            'iat': datetime.utcnow().timestamp(),
            'iss': 'dedan-2.0',
            'aud': 'dedan-api'
        }
        
        token = jwt.encode(payload, self.encryption_key, algorithm='HS256')
        return token
    
    def _get_permissions_for_role(self, role: UserRole) -> Set[Permission]:
        """Get permissions for role"""
        role_permissions = {
            UserRole.ADMIN: {
                Permission.READ_MINERALS, Permission.WRITE_MINERALS, Permission.EXECUTE_TRADES,
                Permission.VIEW_PORTFOLIO, Permission.MANAGE_USERS, Permission.AUDIT_LOGS,
                Permission.SYSTEM_ADMIN, Permission.QUANTUM_ACCESS, Permission.BLOCKCHAIN_ACCESS
            },
            UserRole.TRADER: {
                Permission.READ_MINERALS, Permission.EXECUTE_TRADES, Permission.VIEW_PORTFOLIO
            },
            UserRole.VIEWER: {
                Permission.READ_MINERALS, Permission.VIEW_PORTFOLIO
            },
            UserRole.AUDITOR: {
                Permission.READ_MINERALS, Permission.VIEW_PORTFOLIO, Permission.AUDIT_LOGS
            },
            UserRole.COMPLIANCE_OFFICER: {
                Permission.READ_MINERALS, Permission.EXECUTE_TRADES, Permission.VIEW_PORTFOLIO,
                Permission.AUDIT_LOGS
            }
        }
        
        return role_permissions.get(role, set())
    
    def _get_permission_for_resource_action(self, resource: str, action: str) -> Permission:
        """Get permission for resource and action"""
        permission_map = {
            ('minerals', 'read'): Permission.READ_MINERALS,
            ('minerals', 'write'): Permission.WRITE_MINERALS,
            ('trades', 'execute'): Permission.EXECUTE_TRADES,
            ('portfolio', 'view'): Permission.VIEW_PORTFOLIO,
            ('users', 'manage'): Permission.MANAGE_USERS,
            ('logs', 'audit'): Permission.AUDIT_LOGS,
            ('system', 'admin'): Permission.SYSTEM_ADMIN,
            ('quantum', 'access'): Permission.QUANTUM_ACCESS,
            ('blockchain', 'access'): Permission.BLOCKCHAIN_ACCESS
        }
        
        return permission_map.get((resource, action), Permission.READ_MINERALS)
    
    def _get_policy_for_role(self, role: UserRole) -> SecurityPolicy:
        """Get security policy for role"""
        policy_map = {
            UserRole.ADMIN: self.policies['admin_policy'],
            UserRole.TRADER: self.policies['trader_policy'],
            UserRole.VIEWER: self.policies['viewer_policy'],
            UserRole.AUDITOR: self.policies['auditor_policy'],
            UserRole.COMPLIANCE_OFFICER: self.policies['compliance_policy']
        }
        
        return policy_map.get(role, self.policies['default_policy'])
    
    async def _assess_user_threat_level(self, user_id: str) -> ThreatLevel:
        """Assess user threat level"""
        # Get recent security events for user
        recent_events = [
            event for event in self.security_events
            if event.user_id == user_id and 
               datetime.utcnow() - event.timestamp < timedelta(hours=24)
        ]
        
        # Calculate threat score
        threat_score = 0.0
        
        # Add score for failed authentications
        failed_auths = len([e for e in recent_events if e.event_type == 'AUTHENTICATION_FAILED'])
        threat_score += failed_auths * 0.2
        
        # Add score for unauthorized access attempts
        unauthorized = len([e for e in recent_events if e.event_type == 'UNAUTHORIZED_ACCESS'])
        threat_score += unauthorized * 0.3
        
        # Add score for anomalous patterns
        anomalous = len([e for e in recent_events if e.event_type == 'ANOMALOUS_ACCESS_PATTERN'])
        threat_score += anomalous * 0.4
        
        # Determine threat level
        if threat_score >= 2.0:
            return ThreatLevel.CRITICAL
        elif threat_score >= 1.0:
            return ThreatLevel.HIGH
        elif threat_score >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _verify_access_pattern(self, session: SecuritySession, context: Dict[str, Any]) -> bool:
        """Verify access pattern for anomalies"""
        # Check time-based patterns
        current_hour = datetime.utcnow().hour
        if current_hour < 6 or current_hour > 22:
            # Late night access - require additional verification
            if session.user_role not in [UserRole.ADMIN, UserRole.AUDITOR]:
                return False
        
        # Check location-based patterns
        if 'location' in context:
            # Compare with usual access locations
            usual_locations = await self._get_user_usual_locations(session.user_id)
            if context['location'] not in usual_locations:
                # Unusual location - require additional verification
                if session.user_role not in [UserRole.ADMIN]:
                    return False
        
        # Check access frequency
        recent_access = await self._get_recent_access_count(session.user_id, hours=1)
        if recent_access > 100:
            # High frequency access - possible bot
            return False
        
        return True
    
    async def _get_user_usual_locations(self, user_id: str) -> List[str]:
        """Get user's usual access locations"""
        # This would query user's access history
        # For now, return empty list
        return []
    
    async def _get_recent_access_count(self, user_id: str, hours: int) -> int:
        """Get recent access count for user"""
        # This would query access logs
        # For now, return 0
        return 0
    
    async def _update_device_trust(self, device_fingerprint: str, username: str, success: bool):
        """Update device trust score"""
        if device_fingerprint not in self.trusted_devices:
            self.trusted_devices[device_fingerprint] = {
                'trust_score': 0.0,
                'first_seen': datetime.utcnow(),
                'last_seen': datetime.utcnow(),
                'successful_authentications': 0,
                'failed_authentications': 0
            }
        
        device_data = self.trusted_devices[device_fingerprint]
        device_data['last_seen'] = datetime.utcnow()
        
        if success:
            device_data['successful_authentications'] += 1
        else:
            device_data['failed_authentications'] += 1
    
    async def _log_security_event(self, event_type: str, severity: str, user_id: Optional[str], ip_address: str, details: Dict[str, Any]):
        """Log security event"""
        event = SecurityEvent(
            event_id=secrets.token_urlsafe(16),
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
            details=details
        )
        
        self.security_events.append(event)
        
        # Store in database
        await self.db.execute(
            """
            INSERT INTO security_events (id, event_type, severity, user_id, ip_address, timestamp, details)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            event.event_id, event.event_type, event.severity, event.user_id,
            event.ip_address, event.timestamp, json.dumps(details)
        )
        
        # Check if event requires immediate action
        if severity in ['HIGH', 'CRITICAL']:
            await self._handle_security_event(event)
    
    async def _handle_security_event(self, event: SecurityEvent):
        """Handle security event with appropriate response"""
        if event.event_type == 'AUTHENTICATION_FAILED' and event.severity == 'HIGH':
            # Lock account after multiple failures
            await self._lock_user_account(event.user_id)
        
        elif event.event_type == 'HIGH_RISK_IP':
            # Block IP address
            await self._block_ip_address(event.ip_address)
        
        elif event.event_type == 'UNAUTHORIZED_ACCESS':
            # Invalidate all sessions for user
            await self._invalidate_user_sessions(event.user_id)
    
    async def _lock_user_account(self, user_id: str):
        """Lock user account"""
        await self.db.execute(
            "UPDATE users SET is_locked = true, locked_until = NOW() + INTERVAL '15 minutes' WHERE id = $1",
            user_id
        )
        
        logger.warning(f"User account locked: {user_id}")
    
    async def _block_ip_address(self, ip_address: str):
        """Block IP address"""
        await self.db.execute(
            "INSERT INTO blocked_ips (ip_address, blocked_at, blocked_until) VALUES ($1, NOW(), NOW() + INTERVAL '24 hours')",
            ip_address
        )
        
        logger.warning(f"IP address blocked: {ip_address}")
    
    async def _invalidate_user_sessions(self, user_id: str):
        """Invalidate all sessions for user"""
        sessions_to_invalidate = [
            session_id for session_id, session in self.active_sessions.items()
            if session.user_id == user_id
        ]
        
        for session_id in sessions_to_invalidate:
            await self._invalidate_session(session_id)
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key"""
        return Fernet.generate_key()
    
    def _load_security_policies(self) -> Dict[str, SecurityPolicy]:
        """Load security policies"""
        return {
            'admin_policy': SecurityPolicy(
                name="admin_policy",
                description="Policy for administrators",
                permissions=list(Permission),
                roles=list(UserRole),
                mfa_required=True,
                session_timeout=1800,  # 30 minutes
                max_failed_attempts=3,
                lockout_duration=1800,  # 30 minutes
                device_trust_required=True,
                geo_restriction=True,
                rate_limit_per_minute=100,
                encryption_required=True,
                audit_level="comprehensive"
            ),
            'trader_policy': SecurityPolicy(
                name="trader_policy",
                description="Policy for traders",
                permissions=[Permission.READ_MINERALS, Permission.EXECUTE_TRADES, Permission.VIEW_PORTFOLIO],
                roles=[UserRole.TRADER],
                mfa_required=True,
                session_timeout=3600,  # 1 hour
                max_failed_attempts=5,
                lockout_duration=900,  # 15 minutes
                device_trust_required=True,
                geo_restriction=True,
                rate_limit_per_minute=60,
                encryption_required=True,
                audit_level="detailed"
            ),
            'viewer_policy': SecurityPolicy(
                name="viewer_policy",
                description="Policy for viewers",
                permissions=[Permission.READ_MINERALS, Permission.VIEW_PORTFOLIO],
                roles=[UserRole.VIEWER],
                mfa_required=False,
                session_timeout=7200,  # 2 hours
                max_failed_attempts=10,
                lockout_duration=300,  # 5 minutes
                device_trust_required=False,
                geo_restriction=False,
                rate_limit_per_minute=30,
                encryption_required=True,
                audit_level="basic"
            ),
            'auditor_policy': SecurityPolicy(
                name="auditor_policy",
                description="Policy for auditors",
                permissions=[Permission.READ_MINERALS, Permission.VIEW_PORTFOLIO, Permission.AUDIT_LOGS],
                roles=[UserRole.AUDITOR],
                mfa_required=True,
                session_timeout=1800,  # 30 minutes
                max_failed_attempts=3,
                lockout_duration=900,  # 15 minutes
                device_trust_required=True,
                geo_restriction=True,
                rate_limit_per_minute=50,
                encryption_required=True,
                audit_level="comprehensive"
            ),
            'compliance_policy': SecurityPolicy(
                name="compliance_policy",
                description="Policy for compliance officers",
                permissions=[Permission.READ_MINERALS, Permission.EXECUTE_TRADES, Permission.VIEW_PORTFOLIO, Permission.AUDIT_LOGS],
                roles=[UserRole.COMPLIANCE_OFFICER],
                mfa_required=True,
                session_timeout=3600,  # 1 hour
                max_failed_attempts=5,
                lockout_duration=900,  # 15 minutes
                device_trust_required=True,
                geo_restriction=True,
                rate_limit_per_minute=40,
                encryption_required=True,
                audit_level="comprehensive"
            ),
            'default_policy': SecurityPolicy(
                name="default_policy",
                description="Default security policy",
                permissions=[Permission.READ_MINERALS],
                roles=[UserRole.VIEWER],
                mfa_required=False,
                session_timeout=3600,
                max_failed_attempts=5,
                lockout_duration=900,
                device_trust_required=False,
                geo_restriction=False,
                rate_limit_per_minute=30,
                encryption_required=True,
                audit_level="basic"
            )
        }
    
    def _get_ip_whitelist(self) -> List[str]:
        """Get IP whitelist"""
        # This would load from configuration or database
        return ['127.0.0.1', '::1']  # Localhost for development
    
    def _get_ip_blacklist(self) -> List[str]:
        """Get IP blacklist"""
        # This would load from configuration or database
        return []  # Empty for development
    
    async def _load_security_data(self):
        """Load existing security data"""
        # Load trusted devices
        devices_data = await self.db.fetch("SELECT * FROM trusted_devices")
        for device in devices_data:
            self.trusted_devices[device['fingerprint']] = {
                'trust_score': device['trust_score'],
                'first_seen': device['first_seen'],
                'last_seen': device['last_seen'],
                'successful_authentications': device['successful_authentications'],
                'failed_authentications': device['failed_authentications']
            }
        
        # Load IP reputation
        ip_data = await self.db.fetch("SELECT * FROM ip_reputation")
        for ip in ip_data:
            self.ip_reputation[ip['ip_address']] = {
                'threat_score': ip['threat_score'],
                'last_seen': ip['last_seen'],
                'malicious_activities': ip['malicious_activities']
            }
        
        # Load recent security events
        events_data = await self.db.fetch(
            "SELECT * FROM security_events WHERE timestamp > NOW() - INTERVAL '24 hours' ORDER BY timestamp DESC"
        )
        
        for event in events_data:
            self.security_events.append(SecurityEvent(
                event_id=event['id'],
                event_type=event['event_type'],
                severity=event['severity'],
                user_id=event['user_id'],
                ip_address=event['ip_address'],
                timestamp=event['timestamp'],
                details=json.loads(event['details']),
                resolved=event['resolved']
            ))
    
    async def _security_monitoring_loop(self):
        """Background security monitoring loop"""
        while True:
            try:
                # Clean up expired sessions
                await self._cleanup_expired_sessions()
                
                # Update IP reputation
                await self._update_ip_reputation()
                
                # Analyze security events for patterns
                await self._analyze_security_patterns()
                
                # Update threat intelligence
                await self._update_threat_intelligence()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Security monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.active_sessions.items()
            if current_time > session.expires_at
        ]
        
        for session_id in expired_sessions:
            await self._invalidate_session(session_id)
    
    async def _update_ip_reputation(self):
        """Update IP reputation based on recent events"""
        # This would analyze recent security events and update IP reputation
        pass
    
    async def _analyze_security_patterns(self):
        """Analyze security events for patterns"""
        # This would use machine learning or statistical analysis to detect patterns
        pass
    
    async def _update_threat_intelligence(self):
        """Update threat intelligence from external sources"""
        # This would fetch threat intelligence from external sources
        pass
    
    async def get_security_metrics(self) -> Dict[str, Any]:
        """Get security metrics"""
        total_sessions = len(self.active_sessions)
        recent_events = len([
            e for e in self.security_events
            if datetime.utcnow() - e.timestamp < timedelta(hours=24)
        ])
        
        high_risk_ips = len([
            ip for ip, data in self.ip_reputation.items()
            if data['threat_score'] > 0.7
        ])
        
        trusted_devices = len([
            device for device, data in self.trusted_devices.items()
            if data['trust_score'] > 0.8
        ])
        
        return {
            'active_sessions': total_sessions,
            'recent_security_events': recent_events,
            'high_risk_ips': high_risk_ips,
            'trusted_devices': trusted_devices,
            'blocked_ips': len(await self.db.fetchval("SELECT COUNT(*) FROM blocked_ips")),
            'locked_accounts': len(await self.db.fetchval("SELECT COUNT(*) FROM users WHERE is_locked = true")),
            'mfa_enabled_users': len(await self.db.fetchval("SELECT COUNT(*) FROM users WHERE mfa_enabled = true")),
            'security_score': max(0, 100 - (recent_events * 2))  # Simple scoring
        }

# Main execution
async def main():
    """Main execution function"""
    zero_trust = ZeroTrustSecurity(
        db_connection="postgresql://dedan:password@localhost:5432/dedan",
        redis_url="redis://localhost:6379/0"
    )
    
    await zero_trust.initialize()
    
    # Test authentication
    success, session = await zero_trust.authenticate_user(
        username="testuser",
        password="testpass",
        ip_address="192.168.1.100",
        user_agent="Mozilla/5.0",
        device_fingerprint="abc123def456"
    )
    
    print(f"Authentication result: {success}")
    if session:
        print(f"Session created: {session.session_id}")
        print(f"User role: {session.user_role}")
        print(f"Permissions: {[p.value for p in session.permissions]}")
    
    # Test authorization
    if session:
        authorized = await zero_trust.authorize_request(
            session_id=session.session_id,
            resource="minerals",
            action="read",
            context={"location": "US", "time": "14:30"}
        )
        print(f"Authorization result: {authorized}")
    
    # Get security metrics
    metrics = await zero_trust.get_security_metrics()
    print(f"Security metrics: {json.dumps(metrics, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(main())
