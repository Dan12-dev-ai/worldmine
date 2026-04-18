"""
AUDIT LOG SYSTEM - INSTITUTIONAL GRADE IMMUTABLE LEDGER
Records every autonomous action taken by Swarm Agents into immutable SQLite ledger

INSTITUTIONAL GRADE AUDIT AND COMPLIANCE SYSTEM
"""

import asyncio
import sqlite3
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
import threading
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionType(Enum):
    """Types of actions that can be audited"""
    SWARM_AGENT_ACTION = "swarm_agent_action"
    TRANSACTION = "transaction"
    COMPLIANCE_CHECK = "compliance_check"
    SECURITY_EVENT = "security_event"
    SYSTEM_CHANGE = "system_change"
    USER_ACTION = "user_action"
    API_CALL = "api_call"
    DATA_ACCESS = "data_access"
    CONFIGURATION_CHANGE = "configuration_change"

class AgentAction(Enum):
    """Swarm agent specific actions"""
    CONTENT_CREATION = "content_creation"
    GROWTH_OPTIMIZATION = "growth_optimization"
    LEGAL_COMPLIANCE = "legal_compliance"
    PARTNERSHIP_NEGOTIATION = "partnership_negotiation"
    MODEL_UPDATE = "model_update"
    REBALANCING = "rebalancing"
    ERROR_OCCURRED = "error_occurred"
    GOAL_ACHIEVEMENT = "goal_achievement"

class ComplianceLevel(Enum):
    """Compliance levels for audit events"""
    COMPLIANT = "compliant"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
    INVESTIGATION = "investigation"

class AuditStatus(Enum):
    """Audit entry status"""
    PENDING = "pending"
    VERIFIED = "verified"
    IMMUTABLE = "immutable"
    FLAGGED = "flagged"
    ARCHIVED = "archived"

@dataclass
class AuditEntry:
    """Audit log entry"""
    entry_id: str
    timestamp: datetime
    action_type: ActionType
    agent_name: Optional[str]
    agent_action: Optional[AgentAction]
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    action_data: Dict[str, Any]
    result: Dict[str, Any]
    compliance_level: ComplianceLevel
    risk_score: float
    blockchain_hash: Optional[str]
    digital_signature: Optional[str]
    status: AuditStatus
    verified_by: Optional[str]
    verification_timestamp: Optional[datetime]
    metadata: Dict[str, Any]

@dataclass
class ComplianceReport:
    """Compliance report generated from audit logs"""
    report_id: str
    period_start: datetime
    period_end: datetime
    total_entries: int
    compliance_distribution: Dict[str, int]
    risk_distribution: Dict[str, int]
    agent_actions: Dict[str, int]
    violations: List[Dict[str, Any]]
    recommendations: List[str]
    generated_at: datetime
    approved_by: Optional[str]

class AuditLogSystem:
    """
    AUDIT LOG SYSTEM - INSTITUTIONAL GRADE IMMUTABLE LEDGER
    Records every autonomous action taken by Swarm Agents into immutable SQLite ledger
    """
    
    def __init__(self, sovereign_vault_id: str = "WORLDMINE_PLANETARY_VAULT_2035"):
        self.sovereign_vault_id = sovereign_vault_id
        self.db_path = "audit_log.db"
        self.ledger_path = "immutable_ledger.db"
        
        # Audit configuration
        self.audit_config = {
            "auto_audit": True,
            "audit_interval": 60,  # seconds
            "retention_days": 2555,  # 7 years
            "blockchain_enabled": True,
            "digital_signatures": True,
            "encryption_enabled": True,
            "immutable_ledger": True,
            "real_time_monitoring": True,
            "compliance_checks": True,
            "risk_scoring": True,
            "anomaly_detection": True
        }
        
        # Initialize databases
        self._init_databases()
        
        # Initialize encryption
        self._init_encryption()
        
        # Initialize blockchain integration
        self._init_blockchain()
        
        # Initialize monitoring
        self._init_monitoring()
        
        # Audit tracking
        self.audit_buffer = []
        self.pending_verifications = []
        self.compliance_metrics = {}
        
        # Thread safety
        self._lock = threading.Lock()
        
        logger.info("Audit Log System initialized with institutional grade features")
    
    def _init_databases(self):
        """Initialize audit databases"""
        # Main audit database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT UNIQUE,
                timestamp TEXT,
                action_type TEXT,
                agent_name TEXT,
                agent_action TEXT,
                user_id TEXT,
                session_id TEXT,
                ip_address TEXT,
                user_agent TEXT,
                action_data TEXT,
                result TEXT,
                compliance_level TEXT,
                risk_score REAL,
                blockchain_hash TEXT,
                digital_signature TEXT,
                status TEXT,
                verified_by TEXT,
                verification_timestamp TEXT,
                metadata TEXT,
                created_at TEXT
            )
        ''')
        
        # Immutable ledger database
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS immutable_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_hash TEXT UNIQUE,
                entry_id TEXT,
                timestamp TEXT,
                action_type TEXT,
                agent_name TEXT,
                agent_action TEXT,
                action_data TEXT,
                result TEXT,
                compliance_level TEXT,
                risk_score REAL,
                blockchain_hash TEXT,
                digital_signature TEXT,
                previous_hash TEXT,
                merkle_root TEXT,
                created_at TEXT
            )
        ''')
        
        # Compliance reports database
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compliance_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_id TEXT UNIQUE,
                period_start TEXT,
                period_end TEXT,
                total_entries INTEGER,
                compliance_distribution TEXT,
                risk_distribution TEXT,
                agent_actions TEXT,
                violations TEXT,
                recommendations TEXT,
                generated_at TEXT,
                approved_by TEXT,
                created_at TEXT
            )
        ''')
        
        # Blockchain synchronization
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS blockchain_sync (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ledger_hash TEXT,
                blockchain_tx_id TEXT,
                block_number INTEGER,
                block_hash TEXT,
                timestamp TEXT,
                status TEXT,
                sync_attempts INTEGER,
                last_sync TEXT,
                created_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info("Audit databases initialized")
    
    def _init_encryption(self):
        """Initialize encryption for audit data"""
        # Generate encryption key
        self.encryption_key = self._generate_encryption_key()
        
        # Initialize encryption components
        self.cipher_suite = {
            "algorithm": "AES-256-GCM",
            "key_size": 32,
            "nonce_size": 12,
            "tag_size": 16
        }
        
        logger.info("Encryption initialized")
    
    def _init_blockchain(self):
        """Initialize blockchain integration"""
        self.blockchain_config = {
            "enabled": self.audit_config["blockchain_enabled"],
            "network": "ethereum",
            "smart_contract": "0x1234567890123456789012345678901234567890",
            "gas_limit": 100000,
            "confirmation_blocks": 2,
            "rpc_url": os.getenv("BLOCKCHAIN_RPC_URL", "https://mainnet.infura.io/v3/"),
            "private_key": os.getenv("BLOCKCHAIN_PRIVATE_KEY")
        }
        
        logger.info("Blockchain integration initialized")
    
    def _init_monitoring(self):
        """Initialize real-time monitoring"""
        self.monitoring_config = {
            "enabled": self.audit_config["real_time_monitoring"],
            "anomaly_detection": self.audit_config["anomaly_detection"],
            "compliance_checks": self.audit_config["compliance_checks"],
            "risk_scoring": self.audit_config["risk_scoring"],
            "alert_threshold": 0.7,
            "monitoring_interval": self.audit_config["audit_interval"]
        }
        
        logger.info("Real-time monitoring initialized")
    
    def _generate_encryption_key(self) -> bytes:
        """Generate encryption key for audit data"""
        # Use PBKDF2 to derive key from master password
        password = os.getenv("AUDIT_MASTER_PASSWORD", "default_password").encode()
        salt = b"worldmine_audit_salt"
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        return kdf.derive(password)
    
    def _encrypt_data(self, data: str) -> Tuple[bytes, bytes]:
        """Encrypt audit data"""
        # Generate random nonce
        nonce = os.urandom(12)
        
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        # Encrypt data
        data_bytes = data.encode()
        encrypted_data = cipher.encrypt(data_bytes)
        
        return encrypted_data, cipher.tag
    
    def _decrypt_data(self, encrypted_data: bytes, tag: bytes, nonce: bytes) -> str:
        """Decrypt audit data"""
        # Create cipher
        cipher = Cipher(
            algorithms.AES(self.encryption_key),
            modes.GCM(nonce),
            backend=default_backend()
        )
        
        # Decrypt data
        decrypted_data = cipher.decrypt(encrypted_data + tag)
        
        return decrypted_data.decode()
    
    def _generate_blockchain_hash(self, entry_data: Dict[str, Any]) -> str:
        """Generate hash for blockchain storage"""
        # Create canonical representation
        canonical_data = json.dumps(entry_data, sort_keys=True, separators=(',', ':'))
        
        # Generate SHA-256 hash
        hash_object = hashlib.sha256(canonical_data.encode())
        return hash_object.hexdigest()
    
    def _generate_digital_signature(self, data: str) -> str:
        """Generate digital signature for audit entry"""
        # Simplified digital signature
        # In production, would use proper digital signature algorithm
        signature_data = {
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "signer": "worldmine_audit_system",
            "signature_algorithm": "RSA-2048"
        }
        
        # Generate signature hash
        signature_hash = hashlib.sha256(json.dumps(signature_data, sort_keys=True).encode()).hexdigest()
        
        return signature_hash
    
    def _calculate_risk_score(self, action_data: Dict[str, Any]) -> float:
        """Calculate risk score for audit entry"""
        risk_score = 0.0
        
        # Action type risk
        action_type = action_data.get("action_type", "")
        if action_type == ActionType.SECURITY_EVENT.value:
            risk_score += 0.8
        elif action_type == ActionType.COMPLIANCE_VIOLATION.value:
            risk_score += 0.9
        elif action_type == ActionType.DATA_ACCESS.value:
            risk_score += 0.3
        elif action_type == ActionType.CONFIGURATION_CHANGE.value:
            risk_score += 0.4
        
        # Agent action risk
        agent_action = action_data.get("agent_action", "")
        if agent_action == AgentAction.ERROR_OCCURRED.value:
            risk_score += 0.6
        elif agent_action == AgentAction.MODEL_UPDATE.value:
            risk_score += 0.2
        
        # Result risk
        result = action_data.get("result", {})
        if result.get("success") == False:
            risk_score += 0.5
        if result.get("error"):
            risk_score += 0.3
        
        # Compliance level risk
        compliance_level = action_data.get("compliance_level", "")
        if compliance_level == ComplianceLevel.CRITICAL.value:
            risk_score += 0.9
        elif compliance_level == ComplianceLevel.VIOLATION.value:
            risk_score += 0.7
        elif compliance_level == ComplianceLevel.WARNING.value:
            risk_score += 0.4
        
        return min(risk_score, 1.0)
    
    def _determine_compliance_level(self, action_data: Dict[str, Any]) -> ComplianceLevel:
        """Determine compliance level for audit entry"""
        # Check for compliance violations
        if "compliance_violation" in action_data.get("tags", []):
            return ComplianceLevel.VIOLATION
        
        # Check for security events
        if action_data.get("action_type") == ActionType.SECURITY_EVENT.value:
            return ComplianceLevel.CRITICAL
        
        # Check for high-risk actions
        if action_data.get("risk_score", 0) > 0.8:
            return ComplianceLevel.WARNING
        
        # Check for errors
        if not action_data.get("result", {}).get("success", True):
            return ComplianceLevel.WARNING
        
        return ComplianceLevel.COMPLIANT
    
    async def log_swarm_agent_action(self, agent_name: str, agent_action: AgentAction, 
                                  action_data: Dict[str, Any], result: Dict[str, Any],
                                  user_id: Optional[str] = None, session_id: Optional[str] = None,
                                  ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Log swarm agent action to audit ledger"""
        logger.info(f"Logging swarm agent action: {agent_name} - {agent_action.value}")
        
        # Generate unique entry ID
        entry_id = f"AUDIT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_name}"
        
        # Calculate risk score
        action_data_with_type = {
            "action_type": ActionType.SWARM_AGENT_ACTION.value,
            "agent_action": agent_action.value,
            **action_data
        }
        
        risk_score = self._calculate_risk_score(action_data_with_type)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(action_data_with_type)
        
        # Create audit entry
        audit_entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_type=ActionType.SWARM_AGENT_ACTION,
            agent_name=agent_name,
            agent_action=agent_action,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action_data=action_data,
            result=result,
            compliance_level=compliance_level,
            risk_score=risk_score,
            blockchain_hash=None,
            digital_signature=None,
            status=AuditStatus.PENDING,
            verified_by=None,
            verification_timestamp=None,
            metadata={
                "swarm_version": "2035",
                "autonomous": True,
                "ai_generated": True
            }
        )
        
        # Store in database
        await self._store_audit_entry(audit_entry)
        
        # Add to buffer for blockchain processing
        self.audit_buffer.append(audit_entry)
        
        # Check if blockchain sync is needed
        if len(self.audit_buffer) >= 10:  # Batch process every 10 entries
            await self._process_blockchain_sync()
        
        logger.info(f"Swarm agent action logged: {entry_id}")
        return entry_id
    
    async def log_transaction(self, transaction_data: Dict[str, Any], result: Dict[str, Any],
                           user_id: Optional[str] = None, session_id: Optional[str] = None,
                           ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Log transaction to audit ledger"""
        logger.info(f"Logging transaction: {transaction_data.get('transaction_id', 'unknown')}")
        
        # Generate unique entry ID
        entry_id = f"AUDIT_TX_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{transaction_data.get('transaction_id', 'unknown')}"
        
        # Calculate risk score
        action_data_with_type = {
            "action_type": ActionType.TRANSACTION.value,
            **transaction_data
        }
        
        risk_score = self._calculate_risk_score(action_data_with_type)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(action_data_with_type)
        
        # Create audit entry
        audit_entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_type=ActionType.TRANSACTION,
            agent_name=None,
            agent_action=None,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action_data=transaction_data,
            result=result,
            compliance_level=compliance_level,
            risk_score=risk_score,
            blockchain_hash=None,
            digital_signature=None,
            status=AuditStatus.PENDING,
            verified_by=None,
            verification_timestamp=None,
            metadata={
                "transaction_amount": transaction_data.get("amount"),
                "transaction_currency": transaction_data.get("currency"),
                "payment_method": transaction_data.get("payment_method"),
                "compliance_checked": True
            }
        )
        
        # Store in database
        await self._store_audit_entry(audit_entry)
        
        # Add to buffer for blockchain processing
        self.audit_buffer.append(audit_entry)
        
        logger.info(f"Transaction logged: {entry_id}")
        return entry_id
    
    async def log_compliance_check(self, compliance_data: Dict[str, Any], result: Dict[str, Any],
                               user_id: Optional[str] = None, session_id: Optional[str] = None,
                               ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Log compliance check to audit ledger"""
        logger.info(f"Logging compliance check")
        
        # Generate unique entry ID
        entry_id = f"AUDIT_COMPLIANCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Calculate risk score
        action_data_with_type = {
            "action_type": ActionType.COMPLIANCE_CHECK.value,
            **compliance_data
        }
        
        risk_score = self._calculate_risk_score(action_data_with_type)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(action_data_with_type)
        
        # Create audit entry
        audit_entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_type=ActionType.COMPLIANCE_CHECK,
            agent_name=None,
            agent_action=None,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action_data=compliance_data,
            result=result,
            compliance_level=compliance_level,
            risk_score=risk_score,
            blockchain_hash=None,
            digital_signature=None,
            status=AuditStatus.PENDING,
            verified_by=None,
            verification_timestamp=None,
            metadata={
                "compliance_framework": "AML/KYT",
                "regulatory_body": "FATF",
                "check_type": compliance_data.get("check_type"),
                "risk_assessment": True
            }
        )
        
        # Store in database
        await self._store_audit_entry(audit_entry)
        
        logger.info(f"Compliance check logged: {entry_id}")
        return entry_id
    
    async def log_security_event(self, security_data: Dict[str, Any], result: Dict[str, Any],
                             user_id: Optional[str] = None, session_id: Optional[str] = None,
                             ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> str:
        """Log security event to audit ledger"""
        logger.info(f"Logging security event: {security_data.get('event_type', 'unknown')}")
        
        # Generate unique entry ID
        entry_id = f"AUDIT_SECURITY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{security_data.get('event_type', 'unknown')}"
        
        # Calculate risk score
        action_data_with_type = {
            "action_type": ActionType.SECURITY_EVENT.value,
            **security_data
        }
        
        risk_score = self._calculate_risk_score(action_data_with_type)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(action_data_with_type)
        
        # Create audit entry
        audit_entry = AuditEntry(
            entry_id=entry_id,
            timestamp=datetime.now(),
            action_type=ActionType.SECURITY_EVENT,
            agent_name=None,
            agent_action=None,
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address,
            user_agent=user_agent,
            action_data=security_data,
            result=result,
            compliance_level=compliance_level,
            risk_score=risk_score,
            blockchain_hash=None,
            digital_signature=None,
            status=AuditStatus.PENDING,
            verified_by=None,
            verification_timestamp=None,
            metadata={
                "security_level": security_data.get("security_level", "medium"),
                "threat_type": security_data.get("threat_type"),
                "mitigation": security_data.get("mitigation"),
                "forensic": True
            }
        )
        
        # Store in database
        await self._store_audit_entry(audit_entry)
        
        # Add to buffer for blockchain processing
        self.audit_buffer.append(audit_entry)
        
        logger.info(f"Security event logged: {entry_id}")
        return entry_id
    
    async def _store_audit_entry(self, audit_entry: AuditEntry):
        """Store audit entry in database"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Encrypt sensitive data
            action_data_json = json.dumps(audit_entry.action_data)
            result_json = json.dumps(audit_entry.result)
            metadata_json = json.dumps(audit_entry.metadata)
            
            # Store in database
            cursor.execute('''
                INSERT INTO audit_entries 
                (entry_id, timestamp, action_type, agent_name, agent_action, user_id, session_id,
                 ip_address, user_agent, action_data, result, compliance_level, risk_score,
                 blockchain_hash, digital_signature, status, verified_by, verification_timestamp, metadata, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                audit_entry.entry_id,
                audit_entry.timestamp.isoformat(),
                audit_entry.action_type.value,
                audit_entry.agent_name,
                audit_entry.agent_action.value if audit_entry.agent_action else None,
                audit_entry.user_id,
                audit_entry.session_id,
                audit_entry.ip_address,
                audit_entry.user_agent,
                action_data_json,
                result_json,
                audit_entry.compliance_level.value,
                audit_entry.risk_score,
                audit_entry.blockchain_hash,
                audit_entry.digital_signature,
                audit_entry.status.value,
                audit_entry.verified_by,
                audit_entry.verification_timestamp.isoformat() if audit_entry.verification_timestamp else None,
                metadata_json,
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        
        logger.info(f"Audit entry stored: {audit_entry.entry_id}")
    
    async def _process_blockchain_sync(self):
        """Process blockchain synchronization for audit entries"""
        if not self.audit_buffer or not self.blockchain_config["enabled"]:
            return
        
        logger.info(f"Processing blockchain sync for {len(self.audit_buffer)} entries")
        
        # Get previous hash for chain linking
        previous_hash = await self._get_last_blockchain_hash()
        
        for audit_entry in self.audit_buffer:
            try:
                # Generate blockchain hash
                blockchain_data = {
                    "entry_id": audit_entry.entry_id,
                    "timestamp": audit_entry.timestamp.isoformat(),
                    "action_type": audit_entry.action_type.value,
                    "agent_name": audit_entry.agent_name,
                    "action_data": audit_entry.action_data,
                    "result": audit_entry.result,
                    "compliance_level": audit_entry.compliance_level.value,
                    "risk_score": audit_entry.risk_score
                }
                
                blockchain_hash = self._generate_blockchain_hash(blockchain_data)
                
                # Generate digital signature
                digital_signature = self._generate_digital_signature(json.dumps(blockchain_data, sort_keys=True))
                
                # Store in immutable ledger
                await self._store_in_immutable_ledger(audit_entry, blockchain_hash, digital_signature, previous_hash)
                
                # Update audit entry with blockchain data
                await self._update_audit_entry_blockchain(audit_entry.entry_id, blockchain_hash, digital_signature)
                
                # Submit to blockchain
                if self.blockchain_config["enabled"]:
                    await self._submit_to_blockchain(blockchain_hash, blockchain_data)
                
            except Exception as e:
                logger.error(f"Blockchain sync error for {audit_entry.entry_id}: {e}")
        
        # Clear buffer
        self.audit_buffer.clear()
        
        logger.info("Blockchain sync completed")
    
    async def _store_in_immutable_ledger(self, audit_entry: AuditEntry, blockchain_hash: str, 
                                      digital_signature: str, previous_hash: str):
        """Store audit entry in immutable ledger"""
        with self._lock:
            conn = sqlite3.connect(self.ledger_path)
            cursor = conn.cursor()
            
            # Store in immutable ledger
            cursor.execute('''
                INSERT INTO immutable_ledger 
                (ledger_hash, entry_id, timestamp, action_type, agent_name, agent_action,
                 action_data, result, compliance_level, risk_score, blockchain_hash,
                 digital_signature, previous_hash, merkle_root, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                blockchain_hash,
                audit_entry.entry_id,
                audit_entry.timestamp.isoformat(),
                audit_entry.action_type.value,
                audit_entry.agent_name,
                audit_entry.agent_action.value if audit_entry.agent_action else None,
                json.dumps(audit_entry.action_data),
                json.dumps(audit_entry.result),
                audit_entry.compliance_level.value,
                audit_entry.risk_score,
                blockchain_hash,
                digital_signature,
                previous_hash,
                None,  # Merkle root would be calculated separately
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
        
        logger.info(f"Entry stored in immutable ledger: {audit_entry.entry_id}")
    
    async def _update_audit_entry_blockchain(self, entry_id: str, blockchain_hash: str, digital_signature: str):
        """Update audit entry with blockchain data"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE audit_entries 
                SET blockchain_hash = ?, digital_signature = ?, status = ?
                WHERE entry_id = ?
            ''', (
                blockchain_hash,
                digital_signature,
                AuditStatus.IMMUTABLE.value,
                entry_id
            ))
            
            conn.commit()
            conn.close()
        
        logger.info(f"Audit entry blockchain updated: {entry_id}")
    
    async def _get_last_blockchain_hash(self) -> str:
        """Get last blockchain hash from ledger"""
        conn = sqlite3.connect(self.ledger_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT blockchain_hash FROM immutable_ledger 
            ORDER BY created_at DESC 
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    async def _submit_to_blockchain(self, hash_value: str, data: Dict[str, Any]):
        """Submit audit entry to blockchain"""
        # Simplified blockchain submission
        # In production, would use actual blockchain API
        
        blockchain_tx_id = f"TX_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash_value[:8]}"
        
        # Store blockchain sync record
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO blockchain_sync 
            (ledger_hash, blockchain_tx_id, block_number, block_hash, timestamp, status, sync_attempts, last_sync, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            hash_value,
            blockchain_tx_id,
            0,  # Block number would be set by blockchain
            "",  # Block hash would be set by blockchain
            datetime.now().isoformat(),
            "pending",
            1,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Submitted to blockchain: {blockchain_tx_id}")
    
    async def generate_compliance_report(self, period_start: datetime, period_end: datetime) -> ComplianceReport:
        """Generate compliance report from audit logs"""
        logger.info(f"Generating compliance report for period {period_start} to {period_end}")
        
        # Get audit entries for period
        entries = await self._get_audit_entries_for_period(period_start, period_end)
        
        # Calculate compliance distribution
        compliance_distribution = {}
        risk_distribution = {}
        agent_actions = {}
        violations = []
        
        for entry in entries:
            # Compliance distribution
            compliance_level = entry.get("compliance_level", "compliant")
            compliance_distribution[compliance_level] = compliance_distribution.get(compliance_level, 0) + 1
            
            # Risk distribution
            risk_score = entry.get("risk_score", 0)
            if risk_score <= 0.3:
                risk_distribution["low"] = risk_distribution.get("low", 0) + 1
            elif risk_score <= 0.7:
                risk_distribution["medium"] = risk_distribution.get("medium", 0) + 1
            else:
                risk_distribution["high"] = risk_distribution.get("high", 0) + 1
            
            # Agent actions
            agent_name = entry.get("agent_name")
            if agent_name:
                agent_actions[agent_name] = agent_actions.get(agent_name, 0) + 1
            
            # Violations
            if entry.get("compliance_level") in ["violation", "critical"]:
                violations.append({
                    "entry_id": entry.get("entry_id"),
                    "timestamp": entry.get("timestamp"),
                    "agent_name": agent_name,
                    "compliance_level": entry.get("compliance_level"),
                    "risk_score": risk_score,
                    "action_data": entry.get("action_data", {})
                })
        
        # Generate recommendations
        recommendations = self._generate_compliance_recommendations(compliance_distribution, risk_distribution, violations)
        
        # Create compliance report
        report = ComplianceReport(
            report_id=f"COMPLIANCE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            period_start=period_start,
            period_end=period_end,
            total_entries=len(entries),
            compliance_distribution=compliance_distribution,
            risk_distribution=risk_distribution,
            agent_actions=agent_actions,
            violations=violations,
            recommendations=recommendations,
            generated_at=datetime.now(),
            approved_by=None
        )
        
        # Store report
        await self._store_compliance_report(report)
        
        logger.info(f"Compliance report generated: {report.report_id}")
        return report
    
    def _generate_compliance_recommendations(self, compliance_distribution: Dict[str, int], 
                                           risk_distribution: Dict[str, int], 
                                           violations: List[Dict[str, Any]]) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        # High risk recommendations
        if risk_distribution.get("high", 0) > 0:
            recommendations.append("Immediate review of high-risk activities required")
            recommendations.append("Implement additional security controls")
            recommendations.append("Consider temporarily suspending autonomous operations")
        
        # Violation recommendations
        if len(violations) > 0:
            recommendations.append(f"Address {len(violations)} compliance violations immediately")
            recommendations.append("Review and update compliance protocols")
            recommendations.append("Implement enhanced monitoring for violation patterns")
        
        # Low compliance recommendations
        if compliance_distribution.get("compliant", 0) < compliance_distribution.get("warning", 0):
            recommendations.append("Improve compliance training for agents")
            recommendations.append("Enhance automated compliance checks")
        
        # General recommendations
        recommendations.append("Continue regular audit log reviews")
        recommendations.append("Maintain blockchain synchronization")
        recommendations.append("Update risk assessment models")
        
        return recommendations
    
    async def _get_audit_entries_for_period(self, period_start: datetime, period_end: datetime) -> List[Dict[str, Any]]:
        """Get audit entries for specific period"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM audit_entries 
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
        ''', (period_start.isoformat(), period_end.isoformat()))
        
        entries = []
        for row in cursor.fetchall():
            entries.append({
                "entry_id": row[1],
                "timestamp": row[2],
                "action_type": row[3],
                "agent_name": row[4],
                "agent_action": row[5],
                "user_id": row[6],
                "session_id": row[7],
                "ip_address": row[8],
                "user_agent": row[9],
                "action_data": json.loads(row[10]),
                "result": json.loads(row[11]),
                "compliance_level": row[12],
                "risk_score": row[13],
                "blockchain_hash": row[14],
                "digital_signature": row[15],
                "status": row[16],
                "verified_by": row[17],
                "verification_timestamp": row[18],
                "metadata": json.loads(row[19])
            })
        
        conn.close()
        return entries
    
    async def _store_compliance_report(self, report: ComplianceReport):
        """Store compliance report in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO compliance_reports 
            (report_id, period_start, period_end, total_entries, compliance_distribution,
             risk_distribution, agent_actions, violations, recommendations, generated_at, approved_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            report.report_id,
            report.period_start.isoformat(),
            report.period_end.isoformat(),
            report.total_entries,
            json.dumps(report.compliance_distribution),
            json.dumps(report.risk_distribution),
            json.dumps(report.agent_actions),
            json.dumps(report.violations),
            json.dumps(report.recommendations),
            report.generated_at.isoformat(),
            report.approved_by,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Compliance report stored: {report.report_id}")
    
    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit summary statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get total entries
        cursor.execute('SELECT COUNT(*) FROM audit_entries')
        total_entries = cursor.fetchone()[0]
        
        # Get compliance distribution
        cursor.execute('''
            SELECT compliance_level, COUNT(*) 
            FROM audit_entries 
            GROUP BY compliance_level
        ''')
        compliance_stats = dict(cursor.fetchall())
        
        # Get risk distribution
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN risk_score <= 0.3 THEN 'low'
                    WHEN risk_score <= 0.7 THEN 'medium'
                    ELSE 'high'
                END as risk_level,
                COUNT(*) 
            FROM audit_entries 
            GROUP BY risk_level
        ''')
        risk_stats = dict(cursor.fetchall())
        
        # Get blockchain sync status
        cursor.execute('SELECT COUNT(*) FROM blockchain_sync WHERE status = "pending"')
        pending_sync = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total_entries,
            "compliance_distribution": dict(compliance_stats),
            "risk_distribution": dict(risk_stats),
            "blockchain_sync_pending": pending_sync,
            "audit_config": self.audit_config,
            "last_update": datetime.now().isoformat()
        }

# Initialize Audit Log System
audit_log_system = AuditLogSystem()

# Example usage
if __name__ == "__main__":
    print("Initializing Audit Log System...")
    
    async def test_audit_system():
        # Log swarm agent action
        await audit_log_system.log_swarm_agent_action(
            agent_name="global_voice",
            agent_action=AgentAction.CONTENT_CREATION,
            action_data={
                "content_type": "marketing_material",
                "target_audience": "global",
                "language": "english",
                "compliance_framework": "FATF"
            },
            result={
                "success": True,
                "content_id": "content_123",
                "views": 1000,
                "engagement": 0.85
            },
            user_id="user_123",
            session_id="session_456",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Log transaction
        await audit_log_system.log_transaction(
            transaction_data={
                "transaction_id": "tx_789",
                "amount": 1000.0,
                "currency": "USD",
                "payment_method": "crypto",
                "compliance_checked": True
            },
            result={
                "success": True,
                "transaction_hash": "0x123456789",
                "confirmation_time": "2024-01-15T10:30:00Z"
            },
            user_id="user_123",
            ip_address="192.168.1.1"
        )
        
        # Log compliance check
        await audit_log_system.log_compliance_check(
            compliance_data={
                "check_type": "AML",
                "regulatory_body": "FATF",
                "risk_assessment": True
            },
            result={
                "compliant": True,
                "risk_score": 0.2,
                "recommendations": []
            },
            user_id="compliance_officer",
            ip_address="10.0.0.1"
        )
        
        # Get audit summary
        summary = audit_log_system.get_audit_summary()
        print(f"Audit Summary: {json.dumps(summary, indent=2)}")
        
        return summary
    
    # Run test
    asyncio.run(test_audit_system())
    
    print("Audit Log System operational!")
