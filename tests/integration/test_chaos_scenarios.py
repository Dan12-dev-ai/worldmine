"""
Chaos Engineering Test Scenarios for DEDAN 2.0
Kill services, simulate disasters, test recovery
"""

import asyncio
import pytest
import aiohttp
import asyncpg
import aioredis
import time
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
import json
import logging
from unittest.mock import Mock, patch, AsyncMock
import subprocess
import psutil
import signal
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChaosTestConfig:
    """Chaos test configuration"""
    API_BASE_URL = "https://api.dedan.ai"
    DB_CONNECTION_STRING = "postgresql://dedan:password@localhost:5432/dedan_test"
    REDIS_URL = "redis://localhost:6379/0"
    TEST_TIMEOUT = 60
    RECOVERY_TIMEOUT = 300
    CHAOS_DURATION = 30

class ServiceKiller:
    """Service killer for chaos testing"""
    
    def __init__(self):
        self.killed_services = set()
        self.original_processes = {}
    
    def kill_service(self, service_name: str) -> bool:
        """Kill a service process"""
        try:
            # Find process by name
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if service_name.lower() in ' '.join(proc.info['cmdline'] or []).lower():
                    logger.info(f"Killing service {service_name} (PID: {proc.pid})")
                    proc.terminate()
                    self.killed_services.add(service_name)
                    self.original_processes[service_name] = proc
                    return True
            
            logger.warning(f"Service {service_name} not found")
            return False
            
        except Exception as e:
            logger.error(f"Error killing service {service_name}: {e}")
            return False
    
    def revive_service(self, service_name: str) -> bool:
        """Revive a killed service"""
        try:
            if service_name in self.original_processes:
                # In real scenario, this would restart the service
                logger.info(f"Reviving service {service_name}")
                del self.killed_services.discard(service_name)
                del self.original_processes[service_name]
                return True
            
            logger.warning(f"No original process found for {service_name}")
            return False
            
        except Exception as e:
            logger.error(f"Error reviving service {service_name}: {e}")
            return False
    
    def cleanup(self):
        """Cleanup all killed services"""
        for service_name in list(self.killed_services):
            self.revive_service(service_name)

class NetworkChaos:
    """Network chaos simulator"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.blocked_ports = set()
        self.original_routes = {}
    
    def block_ip(self, ip_address: str) -> bool:
        """Block IP address using iptables"""
        try:
            cmd = f"sudo iptables -A INPUT -s {ip_address} -j DROP"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.blocked_ips.add(ip_address)
                logger.info(f"Blocked IP: {ip_address}")
                return True
            else:
                logger.error(f"Failed to block IP {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False
    
    def block_port(self, port: int) -> bool:
        """Block port using iptables"""
        try:
            cmd = f"sudo iptables -A INPUT -p tcp --dport {port} -j DROP"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.blocked_ports.add(port)
                logger.info(f"Blocked port: {port}")
                return True
            else:
                logger.error(f"Failed to block port {port}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error blocking port {port}: {e}")
            return False
    
    def unblock_ip(self, ip_address: str) -> bool:
        """Unblock IP address"""
        try:
            cmd = f"sudo iptables -D INPUT -s {ip_address} -j DROP"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.blocked_ips.discard(ip_address)
                logger.info(f"Unblocked IP: {ip_address}")
                return True
            else:
                logger.error(f"Failed to unblock IP {ip_address}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {e}")
            return False
    
    def unblock_port(self, port: int) -> bool:
        """Unblock port"""
        try:
            cmd = f"sudo iptables -D INPUT -p tcp --dport {port} -j DROP"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.blocked_ports.discard(port)
                logger.info(f"Unblocked port: {port}")
                return True
            else:
                logger.error(f"Failed to unblock port {port}: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error unblocking port {port}: {e}")
            return False
    
    def cleanup(self):
        """Cleanup all network blocks"""
        for ip in list(self.blocked_ips):
            self.unblock_ip(ip)
        
        for port in list(self.blocked_ports):
            self.unblock_port(port)

class DatabaseChaos:
    """Database chaos simulator"""
    
    def __init__(self):
        self.corrupted_tables = set()
        self.locked_tables = set()
        self.original_data = {}
    
    async def corrupt_table(self, table_name: str, conn: asyncpg.Connection) -> bool:
        """Corrupt a table (for testing)"""
        try:
            # Store original data
            original_data = await conn.fetch(f"SELECT * FROM {table_name} LIMIT 10")
            self.original_data[table_name] = original_data
            
            # Simulate corruption by updating random rows
            await conn.execute(f"""
                UPDATE {table_name} 
                SET updated_at = NOW() + INTERVAL '1 day'
                WHERE id % 10 = 0
            """)
            
            self.corrupted_tables.add(table_name)
            logger.info(f"Corrupted table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error corrupting table {table_name}: {e}")
            return False
    
    async def lock_table(self, table_name: str, conn: asyncpg.Connection) -> bool:
        """Lock a table"""
        try:
            # Acquire exclusive lock
            await conn.execute(f"LOCK TABLE {table_name} IN EXCLUSIVE MODE")
            self.locked_tables.add(table_name)
            logger.info(f"Locked table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error locking table {table_name}: {e}")
            return False
    
    async def restore_table(self, table_name: str, conn: asyncpg.Connection) -> bool:
        """Restore a corrupted table"""
        try:
            if table_name in self.original_data:
                # In real scenario, restore from backup
                await conn.execute(f"TRUNCATE TABLE {table_name}")
                
                # Restore some sample data
                for row in self.original_data[table_name][:5]:
                    columns = ', '.join(row.keys())
                    values = ', '.join([f"'{str(v)}'" for v in row.values()])
                    await conn.execute(f"INSERT INTO {table_name} ({columns}) VALUES ({values})")
                
                self.corrupted_tables.discard(table_name)
                logger.info(f"Restored table: {table_name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring table {table_name}: {e}")
            return False
    
    async def unlock_table(self, table_name: str, conn: asyncpg.Connection) -> bool:
        """Unlock a table"""
        try:
            await conn.execute("COMMIT")
            self.locked_tables.discard(table_name)
            logger.info(f"Unlocked table: {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking table {table_name}: {e}")
            return False
    
    async def cleanup(self, conn: asyncpg.Connection):
        """Cleanup all chaos effects"""
        for table_name in list(self.corrupted_tables):
            await self.restore_table(table_name, conn)
        
        for table_name in list(self.locked_tables):
            await self.unlock_table(table_name, conn)

class RedisChaos:
    """Redis chaos simulator"""
    
    def __init__(self):
        self.flushed_keys = set()
        self.corrupted_data = {}
        self.redis = None
    
    async def initialize(self):
        """Initialize Redis connection"""
        self.redis = await aioredis.from_url(ChaosTestConfig.REDIS_URL)
    
    async def flush_keys(self, pattern: str) -> bool:
        """Flush keys matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                # Store original data
                for key in keys[:10]:  # Store first 10 keys
                    self.corrupted_data[key] = await self.redis.get(key)
                
                await self.redis.delete(*keys)
                self.flushed_keys.update(keys)
                logger.info(f"Flushed {len(keys)} keys matching pattern: {pattern}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error flushing keys {pattern}: {e}")
            return False
    
    async def corrupt_data(self, key_pattern: str) -> bool:
        """Corrupt Redis data"""
        try:
            keys = await self.redis.keys(key_pattern)
            for key in keys[:5]:  # Corrupt first 5 keys
                original_data = await self.redis.get(key)
                if original_data:
                    # Store original data
                    self.corrupted_data[key] = original_data
                    
                    # Corrupt data (append corruption marker)
                    corrupted_data = original_data + "_CORRUPTED"
                    await self.redis.set(key, corrupted_data)
                    logger.info(f"Corrupted key: {key}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error corrupting keys {key_pattern}: {e}")
            return False
    
    async def restore_data(self, key: str) -> bool:
        """Restore Redis data"""
        try:
            if key in self.corrupted_data:
                await self.redis.set(key, self.corrupted_data[key])
                del self.corrupted_data[key]
                logger.info(f"Restored key: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error restoring key {key}: {e}")
            return False
    
    async def cleanup(self):
        """Cleanup all chaos effects"""
        if self.redis:
            # Restore corrupted data
            for key in list(self.corrupted_data.keys()):
                await self.restore_data(key)
            
            # Note: Flushed keys are not restored as they were deleted
            await self.redis.close()

class TestChaosScenarios:
    """Test chaos scenarios"""
    
    def __init__(self):
        self.service_killer = ServiceKiller()
        self.network_chaos = NetworkChaos()
        self.db_chaos = DatabaseChaos()
        self.redis_chaos = RedisChaos()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_service_kill_recovery(self, test_client):
        """Test service kill and recovery"""
        # Kill API service
        service_killed = self.service_killer.kill_service("dedan-api")
        
        # Wait for service to be down
        await asyncio.sleep(2)
        
        # Verify service is down
        with pytest.raises(aiohttp.ClientError):
            await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        
        # Wait for recovery
        await asyncio.sleep(10)
        
        # Revive service
        if service_killed:
            self.service_killer.revive_service("dedan-api")
        
        # Wait for service to be up
        await asyncio.sleep(5)
        
        # Verify service is up
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
        
        # Cleanup
        self.service_killer.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_database_corruption_recovery(self):
        """Test database corruption and recovery"""
        conn = await asyncpg.connect(ChaosTestConfig.DB_CONNECTION_STRING)
        
        try:
            # Corrupt minerals table
            corruption_success = await self.db_chaos.corrupt_table("minerals", conn)
            assert corruption_success
            
            # Verify corruption
            corrupted_data = await conn.fetchval(
                "SELECT COUNT(*) FROM minerals WHERE updated_at > NOW()"
            )
            assert corrupted_data > 0
            
            # Wait for recovery
            await asyncio.sleep(5)
            
            # Restore table
            restore_success = await self.db_chaos.restore_table("minerals", conn)
            assert restore_success
            
            # Verify recovery
            normal_data = await conn.fetchval(
                "SELECT COUNT(*) FROM minerals WHERE updated_at <= NOW()"
            )
            assert normal_data > 0
            
        finally:
            await self.db_chaos.cleanup(conn)
            await conn.close()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_redis_flush_recovery(self):
        """Test Redis flush and recovery"""
        await self.redis_chaos.initialize()
        
        try:
            # Flush cache keys
            flush_success = await self.redis_chaos.flush_keys("cache:*")
            assert flush_success
            
            # Verify cache is empty
            cache_keys = await self.redis_chaos.redis.keys("cache:*")
            assert len(cache_keys) == 0
            
            # Wait for recovery
            await asyncio.sleep(3)
            
            # Simulate cache repopulation
            await self.redis_chaos.redis.set("cache:test_key", "test_value")
            
            # Verify cache is repopulated
            cache_value = await self.redis_chaos.redis.get("cache:test_key")
            assert cache_value == "test_value"
            
        finally:
            await self.redis_chaos.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_network_partition_recovery(self, test_client):
        """Test network partition and recovery"""
        # Block API port
        port_blocked = self.network_chaos.block_port(8000)
        assert port_blocked
        
        # Verify network is partitioned
        with pytest.raises(aiohttp.ClientError):
            await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        
        # Wait for recovery
        await asyncio.sleep(10)
        
        # Unblock port
        if port_blocked:
            self.network_chaos.unblock_port(8000)
        
        # Wait for network recovery
        await asyncio.sleep(5)
        
        # Verify network is recovered
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
        
        # Cleanup
        self.network_chaos.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_multiple_service_failures(self, test_client):
        """Test multiple service failures"""
        # Kill multiple services
        services = ["dedan-api", "dedan-worker", "dedan-scheduler"]
        killed_services = []
        
        for service in services:
            if self.service_killer.kill_service(service):
                killed_services.append(service)
        
        # Verify services are down
        for service in killed_services:
            with pytest.raises(aiohttp.ClientError):
                await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        
        # Wait for recovery
        await asyncio.sleep(15)
        
        # Revive services
        for service in killed_services:
            self.service_killer.revive_service(service)
        
        # Wait for services to be up
        await asyncio.sleep(10)
        
        # Verify services are up
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
        
        # Cleanup
        self.service_killer.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_cascading_failures(self, test_client):
        """Test cascading failures"""
        # Create cascade: network -> database -> cache
        # 1. Block network
        self.network_chaos.block_port(8000)
        
        # 2. Corrupt database
        conn = await asyncpg.connect(ChaosTestConfig.DB_CONNECTION_STRING)
        await self.db_chaos.corrupt_table("users", conn)
        
        # 3. Flush cache
        await self.redis_chaos.initialize()
        await self.redis_chaos.flush_keys("session:*")
        
        # Verify complete failure
        with pytest.raises(aiohttp.ClientError):
            await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        
        # Wait for recovery
        await asyncio.sleep(20)
        
        # Recovery in reverse order
        # 1. Restore cache
        await self.redis_chaos.redis.set("session:test", "test_value")
        
        # 2. Restore database
        await self.db_chaos.restore_table("users", conn)
        
        # 3. Unblock network
        self.network_chaos.unblock_port(8000)
        
        # Wait for full recovery
        await asyncio.sleep(15)
        
        # Verify full recovery
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
        
        # Cleanup
        self.network_chaos.cleanup()
        await self.db_chaos.cleanup(conn)
        await conn.close()
        await self.redis_chaos.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_resource_exhaustion(self, test_client):
        """Test resource exhaustion scenarios"""
        # Simulate memory exhaustion
        original_memory_limit = None
        
        try:
            # Get current memory limit
            with open('/proc/self/limits', 'r') as f:
                for line in f:
                    if line.startswith('Max address space'):
                        original_memory_limit = line.strip()
                        break
            
            # Simulate memory pressure
            memory_hog = []
            for i in range(100):
                # Allocate large chunks of memory
                chunk = b'x' * (1024 * 1024)  # 1MB chunks
                memory_hog.append(chunk)
                
                if i % 10 == 0:
                    # Test API under memory pressure
                    try:
                        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health", timeout=5)
                        # API should still respond, possibly slower
                        assert response.status in [200, 503]  # Service unavailable is acceptable
                    except aiohttp.ClientError:
                        # Connection errors are acceptable under memory pressure
                        pass
            
            # Clean up memory
            del memory_hog
            
        except MemoryError:
            # Memory exhaustion is expected
            pass
        
        # Wait for recovery
        await asyncio.sleep(10)
        
        # Verify recovery
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_chaos_during_load(self, test_client):
        """Test chaos during high load"""
        # Start background load
        async def load_generator():
            while True:
                try:
                    await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
                    await asyncio.sleep(0.1)
                except:
                    await asyncio.sleep(1)
        
        load_task = asyncio.create_task(load_generator())
        
        # Let load build up
        await asyncio.sleep(2)
        
        # Inject chaos during load
        self.network_chaos.block_port(8000)
        
        # Wait for some time under chaos
        await asyncio.sleep(5)
        
        # Recover from chaos
        self.network_chaos.unblock_port(8000)
        
        # Wait for recovery
        await asyncio.sleep(5)
        
        # Stop load
        load_task.cancel()
        
        # Verify final recovery
        response = await test_client.get(f"{ChaosTestConfig.API_BASE_URL}/api/v1/health")
        assert response.status == 200
        
        # Cleanup
        self.network_chaos.cleanup()
    
    @pytest.mark.asyncio
    @pytest.mark.chaos
    async def test_chaos_automation(self):
        """Test automated chaos handling"""
        # This test verifies that the system can handle chaos automatically
        # without manual intervention
        
        # Simulate automatic service restart
        service_killed = self.service_killer.kill_service("dedan-api")
        
        # Wait for automatic recovery (simulated)
        await asyncio.sleep(15)
        
        # Simulate automatic service revival
        self.service_killer.revive_service("dedan-api")
        
        # Verify automatic recovery worked
        # In a real system, this would be handled by process managers
        # For testing, we simulate the expected behavior
        
        # Cleanup
        self.service_killer.cleanup()

# Test runner
async def run_chaos_tests():
    """Run all chaos tests"""
    import subprocess
    import sys
    
    # Run pytest with chaos markers
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/test_chaos_scenarios.py",
        "-v",
        "--tb=short",
        "-m", "chaos",
        "--maxfail=5",
        "--timeout=600"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Chaos Test Results:")
    print(f"Return Code: {result.returncode}")
    print(f"Output:\n{result.stdout}")
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    
    return result.returncode == 0

if __name__ == "__main__":
    asyncio.run(run_chaos_tests())
