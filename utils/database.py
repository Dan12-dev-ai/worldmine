"""
🗄️ DEDAN 2.0 - UNIFIED DATABASE UTILITIES
Consolidated database connection management and common queries
Eliminates all duplicate database code across the codebase
"""

import os
import asyncio
import asyncpg
import aioredis
from typing import Dict, Any, Optional, List, AsyncGenerator
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class DatabaseConfig:
    """Unified database configuration"""
    
    def __init__(self):
        self.database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
        )
        self.redis_url = os.getenv(
            "REDIS_URL", 
            "redis://localhost:6379"
        )
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", "6379"))
        self.redis_password = os.getenv("REDIS_PASSWORD")
        self.redis_db = int(os.getenv("REDIS_DB", "0"))

class DatabaseManager:
    """Unified database connection management"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.config = config or DatabaseConfig()
        self.db_pool = None
        self.redis_pool = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize database and Redis connection pools"""
        if self._initialized:
            return
        
        try:
            # Initialize PostgreSQL connection pool
            self.db_pool = await asyncpg.create_pool(
                self.config.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60,
                server_settings={
                    'application_name': 'dedan_2_0',
                    'timezone': 'UTC'
                }
            )
            
            # Initialize Redis connection pool
            self.redis_pool = aioredis.ConnectionPool.from_url(
                self.config.redis_url,
                max_connections=20,
                socket_timeout=5,
                socket_connect_timeout=5,
                retry_on_timeout=True
            )
            
            self._initialized = True
            logger.info("✅ Database and Redis pools initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize database pools: {e}")
            raise
    
    async def close(self):
        """Close all connection pools"""
        if self.db_pool:
            await self.db_pool.close()
        if self.redis_pool:
            await self.redis_pool.disconnect()
        self._initialized = False
        logger.info("🔒 Database pools closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection from pool"""
        if not self._initialized:
            await self.initialize()
        
        async with self.db_pool.acquire() as conn:
            yield conn
    
    @asynccontextmanager
    async def get_redis(self):
        """Get Redis connection from pool"""
        if not self._initialized:
            await self.initialize()
        
        async with aioredis.Redis(connection_pool=self.redis_pool) as redis:
            yield redis

class UserQueries:
    """Consolidated user-related database queries"""
    
    @staticmethod
    async def get_user_by_id(conn: asyncpg.Connection, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID - consolidates duplicate queries"""
        try:
            result = await conn.fetchrow("""
                SELECT id, email, username, user_type, tier, verification_level,
                       esg_score, carbon_credits, reputation_score, total_transactions,
                       total_volume, location, profile_data, quantum_public_key,
                       created_at, updated_at, last_active, is_active, email_verified, phone_verified
                FROM users 
                WHERE id = $1
            """, user_id)
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Failed to get user by ID {user_id}: {e}")
            return None
    
    @staticmethod
    async def get_user_by_email(conn: asyncpg.Connection, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email - consolidates duplicate queries"""
        try:
            result = await conn.fetchrow("""
                SELECT id, email, username, user_type, tier, verification_level,
                       esg_score, carbon_credits, reputation_score, total_transactions,
                       total_volume, location, profile_data, quantum_public_key,
                       created_at, updated_at, last_active, is_active, email_verified, phone_verified
                FROM users 
                WHERE email = $1
            """, email)
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            return None
    
    @staticmethod
    async def check_email_exists(conn: asyncpg.Connection, email: str) -> bool:
        """Check if email exists - consolidates duplicate queries"""
        try:
            result = await conn.fetchval("SELECT COUNT(*) FROM users WHERE email = $1", email)
            return result > 0
        except Exception as e:
            logger.error(f"Failed to check email existence {email}: {e}")
            return False
    
    @staticmethod
    async def create_user(conn: asyncpg.Connection, user_data: Dict[str, Any]) -> Optional[str]:
        """Create new user - consolidates duplicate queries"""
        try:
            user_id = await conn.fetchval("""
                INSERT INTO users (
                    email, username, password_hash, user_type, tier, verification_level,
                    esg_score, carbon_credits, reputation_score, total_transactions,
                    total_volume, location, profile_data, quantum_public_key,
                    created_at, updated_at, last_active, is_active, email_verified, phone_verified
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20)
                RETURNING id
            """, 
                user_data['email'],
                user_data['username'],
                user_data['password_hash'],
                user_data.get('user_type', 'user'),
                user_data.get('tier', 'basic'),
                user_data.get('verification_level', 'none'),
                user_data.get('esg_score', 0),
                user_data.get('carbon_credits', 0.0),
                user_data.get('reputation_score', 0.0),
                user_data.get('total_transactions', 0),
                user_data.get('total_volume', 0.0),
                user_data.get('location', {}),
                user_data.get('profile_data', {}),
                user_data.get('quantum_public_key'),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                user_data.get('is_active', True),
                user_data.get('email_verified', False),
                user_data.get('phone_verified', False)
            )
            
            return user_id
            
        except Exception as e:
            logger.error(f"Failed to create user {user_data.get('email')}: {e}")
            return None

class TransactionQueries:
    """Consolidated transaction-related database queries"""
    
    @staticmethod
    async def create_transaction(conn: asyncpg.Connection, transaction_data: Dict[str, Any]) -> Optional[str]:
        """Create transaction - consolidates duplicate queries"""
        try:
            transaction_id = await conn.fetchval("""
                INSERT INTO transactions (
                    user_id, transaction_type, currency, amount, fee, from_currency, to_currency,
                    exchange_rate, status, payment_method, payment_details, metadata,
                    quantum_signature, created_at, updated_at, completed_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16)
                RETURNING id
            """,
                transaction_data['user_id'],
                transaction_data['transaction_type'],
                transaction_data['currency'],
                transaction_data['amount'],
                transaction_data.get('fee', 0),
                transaction_data.get('from_currency'),
                transaction_data.get('to_currency'),
                transaction_data.get('exchange_rate'),
                transaction_data.get('status', 'pending'),
                transaction_data.get('payment_method'),
                transaction_data.get('payment_details', {}),
                transaction_data.get('metadata', {}),
                transaction_data.get('quantum_signature'),
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
                transaction_data.get('completed_at')
            )
            
            return transaction_id
            
        except Exception as e:
            logger.error(f"Failed to create transaction: {e}")
            return None
    
    @staticmethod
    async def get_user_transactions(conn: asyncpg.Connection, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user transactions - consolidates duplicate queries"""
        try:
            results = await conn.fetch("""
                SELECT id, transaction_type, currency, amount, fee, from_currency, to_currency,
                       exchange_rate, status, payment_method, payment_details, metadata,
                       quantum_signature, created_at, updated_at, completed_at
                FROM transactions 
                WHERE user_id = $1 
                ORDER BY created_at DESC 
                LIMIT $2
            """, user_id, limit)
            
            return [dict(row) for row in results]
            
        except Exception as e:
            logger.error(f"Failed to get transactions for user {user_id}: {e}")
            return []

class SessionQueries:
    """Consolidated session-related database queries"""
    
    @staticmethod
    async def get_session_by_token(conn: asyncpg.Connection, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by token - consolidates duplicate queries"""
        try:
            result = await conn.fetchrow("""
                SELECT id, user_id, session_token, device_info, ip_address, expires_at, created_at
                FROM user_sessions 
                WHERE session_token = $1 AND expires_at > NOW()
            """, session_token)
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Failed to get session by token: {e}")
            return None
    
    @staticmethod
    async def create_session(conn: asyncpg.Connection, session_data: Dict[str, Any]) -> Optional[str]:
        """Create session - consolidates duplicate queries"""
        try:
            session_id = await conn.fetchval("""
                INSERT INTO user_sessions (
                    user_id, session_token, device_info, ip_address, expires_at, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """,
                session_data['user_id'],
                session_data['session_token'],
                session_data.get('device_info', {}),
                session_data.get('ip_address'),
                session_data['expires_at'],
                datetime.now(timezone.utc)
            )
            
            return session_id
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return None
    
    @staticmethod
    async def cleanup_expired_sessions(conn: asyncpg.Connection) -> int:
        """Clean up expired sessions - consolidates duplicate queries"""
        try:
            result = await conn.execute("""
                DELETE FROM user_sessions 
                WHERE expires_at <= NOW()
            """)
            
            # Extract number of deleted rows
            deleted_count = int(result.split()[-1]) if result else 0
            return deleted_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}")
            return 0

class CacheManager:
    """Unified Redis cache management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def get_cached_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get cached user data"""
        try:
            async with self.db_manager.get_redis() as redis:
                cached_data = await redis.get(f"user:{user_id}")
                if cached_data:
                    return json.loads(cached_data)
        except Exception as e:
            logger.error(f"Failed to get cached user {user_id}: {e}")
        return None
    
    async def cache_user(self, user_id: str, user_data: Dict[str, Any], ttl: int = 3600):
        """Cache user data"""
        try:
            async with self.db_manager.get_redis() as redis:
                await redis.setex(f"user:{user_id}", ttl, json.dumps(user_data))
        except Exception as e:
            logger.error(f"Failed to cache user {user_id}: {e}")
    
    async def invalidate_user_cache(self, user_id: str):
        """Invalidate user cache"""
        try:
            async with self.db_manager.get_redis() as redis:
                await redis.delete(f"user:{user_id}")
        except Exception as e:
            logger.error(f"Failed to invalidate user cache {user_id}: {e}")

class UnifiedDatabase:
    """Single interface for all database operations"""
    
    def __init__(self, config: DatabaseConfig = None):
        self.db_manager = DatabaseManager(config)
        self.users = UserQueries()
        self.transactions = TransactionQueries()
        self.sessions = SessionQueries()
        self.cache = CacheManager(self.db_manager)
    
    async def initialize(self):
        """Initialize database connections"""
        await self.db_manager.initialize()
    
    async def close(self):
        """Close database connections"""
        await self.db_manager.close()
    
    # User operations
    async def get_user_by_id(self, user_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Get user by ID with optional caching"""
        if use_cache:
            cached_user = await self.cache.get_cached_user(user_id)
            if cached_user:
                return cached_user
        
        async with self.db_manager.get_connection() as conn:
            user = await self.users.get_user_by_id(conn, user_id)
            if user and use_cache:
                await self.cache.cache_user(user_id, user)
            return user
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        async with self.db_manager.get_connection() as conn:
            return await self.users.get_user_by_email(conn, email)
    
    async def create_user(self, user_data: Dict[str, Any]) -> Optional[str]:
        """Create new user"""
        async with self.db_manager.get_connection() as conn:
            return await self.users.create_user(conn, user_data)
    
    # Transaction operations
    async def create_transaction(self, transaction_data: Dict[str, Any]) -> Optional[str]:
        """Create transaction"""
        async with self.db_manager.get_connection() as conn:
            return await self.transactions.create_transaction(conn, transaction_data)
    
    async def get_user_transactions(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user transactions"""
        async with self.db_manager.get_connection() as conn:
            return await self.transactions.get_user_transactions(conn, user_id, limit)
    
    # Session operations
    async def get_session_by_token(self, session_token: str) -> Optional[Dict[str, Any]]:
        """Get session by token"""
        async with self.db_manager.get_connection() as conn:
            return await self.sessions.get_session_by_token(conn, session_token)
    
    async def create_session(self, session_data: Dict[str, Any]) -> Optional[str]:
        """Create session"""
        async with self.db_manager.get_connection() as conn:
            return await self.sessions.create_session(conn, session_data)
    
    # Utility operations
    async def check_email_exists(self, email: str) -> bool:
        """Check if email exists"""
        async with self.db_manager.get_connection() as conn:
            return await self.users.check_email_exists(conn, email)
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions"""
        async with self.db_manager.get_connection() as conn:
            return await self.sessions.cleanup_expired_sessions(conn)

# Global instance for easy access
unified_db = UnifiedDatabase()

# Backward compatibility functions (to ease migration)
async def get_database_connection():
    """Backward compatibility wrapper"""
    return unified_db.db_manager.get_connection()

async def get_user_by_id(user_id: str):
    """Backward compatibility wrapper"""
    return await unified_db.get_user_by_id(user_id)

async def get_user_by_email(email: str):
    """Backward compatibility wrapper"""
    return await unified_db.get_user_by_email(email)

# Import required for JSON operations
import json
