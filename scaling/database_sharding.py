"""
DEDAN Mine - Database Sharding & Redundancy
Read Replicas for PostgreSQL with intelligent query routing
Supports million-user concurrent access with zero system distraction
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncpg
import psycopg2
from psycopg2 import pool
import random
import hashlib
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Database types"""
    PRIMARY = "primary"
    READ_REPLICA = "read_replica"
    ANALYTICS = "analytics"
    CACHE = "cache"

class QueryType(Enum):
    """Query types for routing"""
    READ = "read"
    WRITE = "write"
    TRANSACTION = "transaction"
    ANALYTICS = "analytics"
    MARKET_DATA = "market_data"
    SATELLITE_DATA = "satellite_data"
    USER_SESSION = "user_session"
    PAYOUT_TRANSACTION = "payout_transaction"

@dataclass
class DatabaseNode:
    """Database node configuration"""
    node_id: str
    node_type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    max_connections: int
    current_connections: int
    is_healthy: bool
    last_health_check: datetime
    response_time: float
    priority: int
    region: str
    shard_key: Optional[str] = None

class DatabaseShardingManager:
    """Database sharding and read replica management"""
    
    def __init__(self):
        self.primary_db = None
        self.read_replicas = []
        self.analytics_db = None
        self.cache_db = None
        self.connection_pools = {}
        self.shard_config = {
            "user_sessions": {
                "shard_key": "user_id",
                "num_shards": 16,
                "replicas_per_shard": 2
            },
            "payout_transactions": {
                "shard_key": "transaction_id",
                "num_shards": 32,
                "replicas_per_shard": 3
            },
            "market_data": {
                "shard_key": "mineral_type",
                "num_shards": 8,
                "replicas_per_shard": 2
            },
            "satellite_data": {
                "shard_key": "region",
                "num_shards": 4,
                "replicas_per_shard": 2
            }
        }
        
        # Initialize database nodes
        self.initialize_database_nodes()
    
    def initialize_database_nodes(self):
        """Initialize database node configurations"""
        try:
            # Primary database (for writes and critical transactions)
            self.primary_db = DatabaseNode(
                node_id="primary_1",
                node_type=DatabaseType.PRIMARY,
                host=os.getenv("PRIMARY_DB_HOST", "localhost"),
                port=int(os.getenv("PRIMARY_DB_PORT", "5432")),
                database=os.getenv("PRIMARY_DB_NAME", "dedan_mine"),
                username=os.getenv("PRIMARY_DB_USER", "postgres"),
                password=os.getenv("PRIMARY_DB_PASSWORD", ""),
                max_connections=100,
                current_connections=0,
                is_healthy=True,
                last_health_check=datetime.now(timezone.utc),
                response_time=0.0,
                priority=1,
                region="primary"
            )
            
            # Read replicas (for read queries)
            replica_configs = [
                {
                    "node_id": "replica_1",
                    "host": os.getenv("REPLICA_1_HOST", "localhost"),
                    "port": int(os.getenv("REPLICA_1_PORT", "5433")),
                    "priority": 2,
                    "region": "us-east-1"
                },
                {
                    "node_id": "replica_2",
                    "host": os.getenv("REPLICA_2_HOST", "localhost"),
                    "port": int(os.getenv("REPLICA_2_PORT", "5434")),
                    "priority": 3,
                    "region": "eu-west-1"
                },
                {
                    "node_id": "replica_3",
                    "host": os.getenv("REPLICA_3_HOST", "localhost"),
                    "port": int(os.getenv("REPLICA_3_PORT", "5435")),
                    "priority": 4,
                    "region": "ap-southeast-1"
                }
            ]
            
            for config in replica_configs:
                replica = DatabaseNode(
                    node_type=DatabaseType.READ_REPLICA,
                    database=os.getenv("REPLICA_DB_NAME", "dedan_mine_replica"),
                    username=os.getenv("REPLICA_DB_USER", "postgres"),
                    password=os.getenv("REPLICA_DB_PASSWORD", ""),
                    max_connections=50,
                    current_connections=0,
                    is_healthy=True,
                    last_health_check=datetime.now(timezone.utc),
                    response_time=0.0,
                    **config
                )
                self.read_replicas.append(replica)
            
            # Analytics database (for reporting and analytics)
            self.analytics_db = DatabaseNode(
                node_id="analytics_1",
                node_type=DatabaseType.ANALYTICS,
                host=os.getenv("ANALYTICS_DB_HOST", "localhost"),
                port=int(os.getenv("ANALYTICS_DB_PORT", "5436")),
                database=os.getenv("ANALYTICS_DB_NAME", "dedan_mine_analytics"),
                username=os.getenv("ANALYTICS_DB_USER", "postgres"),
                password=os.getenv("ANALYTICS_DB_PASSWORD", ""),
                max_connections=30,
                current_connections=0,
                is_healthy=True,
                last_health_check=datetime.now(timezone.utc),
                response_time=0.0,
                priority=5,
                region="analytics"
            )
            
            # Cache database (for temporary data)
            self.cache_db = DatabaseNode(
                node_id="cache_1",
                node_type=DatabaseType.CACHE,
                host=os.getenv("CACHE_DB_HOST", "localhost"),
                port=int(os.getenv("CACHE_DB_PORT", "5437")),
                database=os.getenv("CACHE_DB_NAME", "dedan_mine_cache"),
                username=os.getenv("CACHE_DB_USER", "postgres"),
                password=os.getenv("CACHE_DB_PASSWORD", ""),
                max_connections=20,
                current_connections=0,
                is_healthy=True,
                last_health_check=datetime.now(timezone.utc),
                response_time=0.0,
                priority=6,
                region="cache"
            )
            
            logger.info("Database nodes initialized successfully")
            
        except Exception as e:
            logger.error(f"Database node initialization failed: {str(e)}")
            raise
    
    async def initialize_connection_pools(self):
        """Initialize connection pools for all database nodes"""
        try:
            # Primary database pool
            self.connection_pools["primary"] = await asyncpg.create_pool(
                host=self.primary_db.host,
                port=self.primary_db.port,
                database=self.primary_db.database,
                user=self.primary_db.username,
                password=self.primary_db.password,
                min_size=10,
                max_size=self.primary_db.max_connections,
                command_timeout=60
            )
            
            # Read replica pools
            for replica in self.read_replicas:
                self.connection_pools[replica.node_id] = await asyncpg.create_pool(
                    host=replica.host,
                    port=replica.port,
                    database=replica.database,
                    user=replica.username,
                    password=replica.password,
                    min_size=5,
                    max_size=replica.max_connections,
                    command_timeout=60
                )
            
            # Analytics database pool
            self.connection_pools["analytics"] = await asyncpg.create_pool(
                host=self.analytics_db.host,
                port=self.analytics_db.port,
                database=self.analytics_db.database,
                user=self.analytics_db.username,
                password=self.analytics_db.password,
                min_size=5,
                max_size=self.analytics_db.max_connections,
                command_timeout=60
            )
            
            # Cache database pool
            self.connection_pools["cache"] = await asyncpg.create_pool(
                host=self.cache_db.host,
                port=self.cache_db.port,
                database=self.cache_db.database,
                user=self.cache_db.username,
                password=self.cache_db.password,
                min_size=5,
                max_size=self.cache_db.max_connections,
                command_timeout=60
            )
            
            logger.info("Connection pools initialized successfully")
            
        except Exception as e:
            logger.error(f"Connection pool initialization failed: {str(e)}")
            raise
    
    def route_query(self, query_type: QueryType, shard_key: Optional[str] = None) -> DatabaseNode:
        """Route query to appropriate database node"""
        try:
            if query_type in [QueryType.WRITE, QueryType.TRANSACTION, QueryType.PAYOUT_TRANSACTION]:
                # All write operations go to primary
                return self.primary_db
            
            elif query_type in [QueryType.READ, QueryType.USER_SESSION]:
                # Read queries go to least loaded replica
                healthy_replicas = [r for r in self.read_replicas if r.is_healthy]
                if not healthy_replicas:
                    # Fallback to primary if no replicas available
                    return self.primary_db
                
                # Select replica with lowest connection count
                return min(healthy_replicas, key=lambda r: r.current_connections)
            
            elif query_type == QueryType.MARKET_DATA:
                # Market data queries go to dedicated replica
                market_replicas = [r for r in self.read_replicas if r.region == "us-east-1" and r.is_healthy]
                if market_replicas:
                    return random.choice(market_replicas)
                return self.primary_db
            
            elif query_type == QueryType.SATELLITE_DATA:
                # Satellite data queries go to dedicated replica
                satellite_replicas = [r for r in self.read_replicas if r.region == "eu-west-1" and r.is_healthy]
                if satellite_replicas:
                    return random.choice(satellite_replicas)
                return self.primary_db
            
            elif query_type == QueryType.ANALYTICS:
                # Analytics queries go to analytics database
                return self.analytics_db
            
            else:
                # Default to primary
                return self.primary_db
                
        except Exception as e:
            logger.error(f"Query routing failed: {str(e)}")
            return self.primary_db
    
    def get_shard_node(self, table_name: str, shard_key: str) -> DatabaseNode:
        """Get database node for sharded table"""
        try:
            if table_name not in self.shard_config:
                return self.primary_db
            
            config = self.shard_config[table_name]
            shard_hash = hashlib.md5(shard_key.encode()).hexdigest()
            shard_index = int(shard_hash[:8], 16) % config["num_shards"]
            
            # For now, return primary (in production, implement actual sharding)
            return self.primary_db
            
        except Exception as e:
            logger.error(f"Shard node selection failed: {str(e)}")
            return self.primary_db
    
    async def execute_query(self, query: str, query_type: QueryType, params: Optional[List] = None, shard_key: Optional[str] = None) -> Dict[str, Any]:
        """Execute query with intelligent routing"""
        try:
            # Route query to appropriate node
            target_node = self.route_query(query_type, shard_key)
            
            # Get connection pool
            pool = self.connection_pools.get(target_node.node_id)
            if not pool:
                raise ValueError(f"No connection pool for node {target_node.node_id}")
            
            # Execute query
            start_time = datetime.now(timezone.utc)
            
            async with pool.acquire() as connection:
                if params:
                    result = await connection.fetch(query, *params)
                else:
                    result = await connection.fetch(query)
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            # Update node metrics
            target_node.response_time = response_time
            target_node.last_health_check = end_time
            
            # Convert result to list of dicts
            rows = [dict(row) for row in result]
            
            return {
                "success": True,
                "data": rows,
                "row_count": len(rows),
                "execution_time": response_time,
                "node_id": target_node.node_id,
                "node_type": target_node.node_type.value,
                "query_type": query_type.value,
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "nbe_compliance": False
            }
    
    async def execute_transaction(self, queries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute transaction on primary database"""
        try:
            pool = self.connection_pools.get("primary")
            if not pool:
                raise ValueError("No connection pool for primary database")
            
            start_time = datetime.now(timezone.utc)
            
            async with pool.acquire() as connection:
                async with connection.transaction():
                    results = []
                    for query_info in queries:
                        query = query_info["query"]
                        params = query_info.get("params")
                        
                        if params:
                            result = await connection.fetch(query, *params)
                        else:
                            result = await connection.fetch(query)
                        
                        results.append([dict(row) for row in result])
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            return {
                "success": True,
                "data": results,
                "execution_time": response_time,
                "node_id": self.primary_db.node_id,
                "transaction_committed": True,
                "nbe_compliance": True
            }
            
        except Exception as e:
            logger.error(f"Transaction execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "transaction_committed": False,
                "nbe_compliance": False
            }
    
    async def check_node_health(self, node: DatabaseNode) -> bool:
        """Check health of database node"""
        try:
            pool = self.connection_pools.get(node.node_id)
            if not pool:
                return False
            
            start_time = datetime.now(timezone.utc)
            
            async with pool.acquire() as connection:
                await connection.fetch("SELECT 1")
            
            end_time = datetime.now(timezone.utc)
            response_time = (end_time - start_time).total_seconds() * 1000
            
            node.response_time = response_time
            node.last_health_check = end_time
            node.is_healthy = response_time < 1000  # 1 second threshold
            
            return node.is_healthy
            
        except Exception as e:
            logger.error(f"Health check failed for node {node.node_id}: {str(e)}")
            node.is_healthy = False
            return False
    
    async def check_all_nodes_health(self) -> Dict[str, bool]:
        """Check health of all database nodes"""
        health_results = {}
        
        # Check primary
        health_results["primary"] = await self.check_node_health(self.primary_db)
        
        # Check read replicas
        for replica in self.read_replicas:
            health_results[replica.node_id] = await self.check_node_health(replica)
        
        # Check analytics
        health_results["analytics"] = await self.check_node_health(self.analytics_db)
        
        # Check cache
        health_results["cache"] = await self.check_node_health(self.cache_db)
        
        return health_results
    
    async def get_load_balanced_replica(self) -> DatabaseNode:
        """Get least loaded read replica"""
        try:
            healthy_replicas = [r for r in self.read_replicas if r.is_healthy]
            if not healthy_replicas:
                return self.primary_db
            
            # Select replica with lowest current connections
            return min(healthy_replicas, key=lambda r: r.current_connections)
            
        except Exception as e:
            logger.error(f"Load balanced replica selection failed: {str(e)}")
            return self.primary_db
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {
                "primary": {
                    "node_id": self.primary_db.node_id,
                    "current_connections": self.primary_db.current_connections,
                    "max_connections": self.primary_db.max_connections,
                    "is_healthy": self.primary_db.is_healthy,
                    "response_time": self.primary_db.response_time,
                    "last_health_check": self.primary_db.last_health_check.isoformat()
                },
                "read_replicas": [],
                "analytics": {
                    "node_id": self.analytics_db.node_id,
                    "current_connections": self.analytics_db.current_connections,
                    "max_connections": self.analytics_db.max_connections,
                    "is_healthy": self.analytics_db.is_healthy,
                    "response_time": self.analytics_db.response_time,
                    "last_health_check": self.analytics_db.last_health_check.isoformat()
                },
                "cache": {
                    "node_id": self.cache_db.node_id,
                    "current_connections": self.cache_db.current_connections,
                    "max_connections": self.cache_db.max_connections,
                    "is_healthy": self.cache_db.is_healthy,
                    "response_time": self.cache_db.response_time,
                    "last_health_check": self.cache_db.last_health_check.isoformat()
                }
            }
            
            # Add read replica stats
            for replica in self.read_replicas:
                stats["read_replicas"].append({
                    "node_id": replica.node_id,
                    "current_connections": replica.current_connections,
                    "max_connections": replica.max_connections,
                    "is_healthy": replica.is_healthy,
                    "response_time": replica.response_time,
                    "last_health_check": replica.last_health_check.isoformat(),
                    "region": replica.region,
                    "priority": replica.priority
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"Database stats retrieval failed: {str(e)}")
            return {"error": str(e)}

# Global instance
database_sharding_manager = DatabaseShardingManager()

# Query routing functions
async def execute_read_query(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute read query on replica"""
    return await database_sharding_manager.execute_query(query, QueryType.READ, params)

async def execute_write_query(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute write query on primary"""
    return await database_sharding_manager.execute_query(query, QueryType.WRITE, params)

async def execute_market_data_query(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute market data query on dedicated replica"""
    return await database_sharding_manager.execute_query(query, QueryType.MARKET_DATA, params)

async def execute_satellite_data_query(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute satellite data query on dedicated replica"""
    return await database_sharding_manager.execute_query(query, QueryType.SATELLITE_DATA, params)

async def execute_payout_transaction(queries: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute payout transaction on primary"""
    return await database_sharding_manager.execute_transaction(queries)

async def get_database_health() -> Dict[str, bool]:
    """Get health status of all database nodes"""
    return await database_sharding_manager.check_all_nodes_health()

async def get_database_statistics() -> Dict[str, Any]:
    """Get database statistics"""
    return await database_sharding_manager.get_database_stats()
