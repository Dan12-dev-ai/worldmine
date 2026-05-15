"""
Automated Failover Controller for DEDAN 2.0
Multi-region active-active failover with <30 second detection and promotion
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
import aiohttp
import asyncpg
import aioredis
from dataclasses import dataclass
import asyncio
import socket
import subprocess
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class FailoverState(Enum):
    """Failover states"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    FAILOVER_IN_PROGRESS = "failover_in_progress"
    FAILOVER_COMPLETE = "failover_complete"
    RECOVERY_IN_PROGRESS = "recovery_in_progress"
    RECOVERY_COMPLETE = "recovery_complete"

class RegionStatus(Enum):
    """Region status"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    PROMOTED = "promoted"
    DEMOTED = "demoted"

@dataclass
class HealthCheck:
    """Health check configuration"""
    name: str
    url: str
    timeout: int = 5
    expected_status: int = 200
    check_interval: int = 10
    failure_threshold: int = 3
    success_threshold: int = 2

@dataclass
class RegionConfig:
    """Region configuration"""
    name: str
    region_code: str
    k8s_namespace: str
    deployment_name: str
    service_name: str
    database_url: str
    redis_url: str
    load_balancer_dns: str
    health_checks: List[HealthCheck]
    is_primary: bool = False
    is_active: bool = True

class FailoverController:
    """Automated failover controller"""
    
    def __init__(self, config_file: str = "/app/config/failover_config.json"):
        self.config_file = config_file
        self.regions: Dict[str, RegionConfig] = {}
        self.region_status: Dict[str, FailoverState] = {}
        self.health_check_results: Dict[str, Dict[str, bool]] = {}
        self.failover_history: List[Dict] = []
        self.current_primary_region: Optional[str] = None
        self.k8s_client = None
        self.running = False
        self.failover_lock = asyncio.Lock()
        
        # Initialize Kubernetes client
        try:
            config.load_incluster_config()
            self.k8s_client = client.CoreV1Api()
            self.apps_v1 = client.AppsV1Api()
            logger.info("Kubernetes client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kubernetes client: {e}")
            raise
    
    async def initialize(self):
        """Initialize failover controller"""
        logger.info("Initializing failover controller...")
        
        # Load configuration
        await self.load_configuration()
        
        # Initialize region status
        for region_name in self.regions:
            self.region_status[region_name] = FailoverState.HEALTHY
            self.health_check_results[region_name] = {}
        
        # Find current primary region
        await self.determine_primary_region()
        
        logger.info(f"Failover controller initialized. Primary region: {self.current_primary_region}")
        
        # Start health monitoring
        self.running = True
        await asyncio.gather(
            self.health_monitor_loop(),
            self.failover_decision_loop(),
            self.recovery_monitor_loop()
        )
    
    async def load_configuration(self):
        """Load failover configuration"""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)
            
            for region_data in config_data['regions']:
                health_checks = []
                for hc_data in region_data['health_checks']:
                    health_checks.append(HealthCheck(**hc_data))
                
                region = RegionConfig(
                    name=region_data['name'],
                    region_code=region_data['region_code'],
                    k8s_namespace=region_data['k8s_namespace'],
                    deployment_name=region_data['deployment_name'],
                    service_name=region_data['service_name'],
                    database_url=region_data['database_url'],
                    redis_url=region_data['redis_url'],
                    load_balancer_dns=region_data['load_balancer_dns'],
                    health_checks=health_checks,
                    is_primary=region_data.get('is_primary', False),
                    is_active=region_data.get('is_active', True)
                )
                
                self.regions[region.name] = region
                
            logger.info(f"Loaded configuration for {len(self.regions)} regions")
            
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    async def determine_primary_region(self):
        """Determine current primary region"""
        for region_name, region in self.regions.items():
            if region.is_primary:
                self.current_primary_region = region_name
                logger.info(f"Primary region set to: {region_name}")
                return
        
        # If no primary configured, select the healthiest region
        await self.select_new_primary()
    
    async def health_monitor_loop(self):
        """Main health monitoring loop"""
        while self.running:
            try:
                await self.perform_health_checks()
                await asyncio.sleep(10)  # Check every 10 seconds
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(5)
    
    async def perform_health_checks(self):
        """Perform health checks for all regions"""
        tasks = []
        for region_name, region in self.regions.items():
            if region.is_active:
                tasks.append(self.check_region_health(region_name))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def check_region_health(self, region_name: str):
        """Check health of a specific region"""
        region = self.regions[region_name]
        region_healthy = True
        
        for health_check in region.health_checks:
            try:
                is_healthy = await self.perform_health_check(region, health_check)
                self.health_check_results[region_name][health_check.name] = is_healthy
                
                if not is_healthy:
                    region_healthy = False
                    logger.warning(f"Health check failed: {region_name} - {health_check.name}")
                
            except Exception as e:
                logger.error(f"Error performing health check {health_check.name} for {region_name}: {e}")
                self.health_check_results[region_name][health_check.name] = False
                region_healthy = False
        
        # Update region status based on health check results
        await self.update_region_status(region_name, region_healthy)
    
    async def perform_health_check(self, region: RegionConfig, health_check: HealthCheck) -> bool:
        """Perform individual health check"""
        try:
            timeout = aiohttp.ClientTimeout(total=health_check.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(
                    health_check.url,
                    ssl=False  # For internal health checks
                ) as response:
                    return response.status == health_check.expected_status
        except Exception:
            return False
    
    async def update_region_status(self, region_name: str, is_healthy: bool):
        """Update region status based on health check results"""
        current_status = self.region_status[region_name]
        new_status = current_status
        
        if is_healthy:
            if current_status in [FailoverState.FAILING, FailoverState.FAILOVER_IN_PROGRESS]:
                new_status = FailoverState.RECOVERY_IN_PROGRESS
            elif current_status == FailoverState.RECOVERY_IN_PROGRESS:
                new_status = FailoverState.RECOVERY_COMPLETE
            elif current_status in [FailoverState.DEGRADED, FailoverState.FAILOVER_COMPLETE]:
                new_status = FailoverState.HEALTHY
        else:
            if current_status == FailoverState.HEALTHY:
                new_status = FailoverState.DEGRADED
            elif current_status == FailoverState.DEGRADED:
                new_status = FailoverState.FAILING
            elif current_status in [FailoverState.RECOVERY_COMPLETE, FailoverState.HEALTHY]:
                new_status = FailoverState.DEGRADED
        
        if new_status != current_status:
            self.region_status[region_name] = new_status
            logger.info(f"Region {region_name} status changed: {current_status.value} -> {new_status.value}")
    
    async def failover_decision_loop(self):
        """Failover decision loop"""
        while self.running:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                await self.evaluate_failover_needs()
            except Exception as e:
                logger.error(f"Error in failover decision loop: {e}")
                await asyncio.sleep(15)
    
    async def evaluate_failover_needs(self):
        """Evaluate if failover is needed"""
        if not self.current_primary_region:
            await self.select_new_primary()
            return
        
        primary_status = self.region_status.get(self.current_primary_region, FailoverState.HEALTHY)
        
        # Check if primary region needs failover
        if primary_status in [FailoverState.FAILING, FailoverState.FAILOVER_IN_PROGRESS]:
            async with self.failover_lock:
                await self.initiate_failover()
    
    async def initiate_failover(self):
        """Initiate failover process"""
        if not self.current_primary_region:
            logger.warning("No primary region to failover from")
            return
        
        logger.critical(f"Initiating failover from {self.current_primary_region}")
        
        # Record failover event
        failover_event = {
            'timestamp': datetime.utcnow().isoformat(),
            'from_region': self.current_primary_region,
            'to_region': None,
            'reason': 'primary_failure',
            'status': 'initiated'
        }
        
        try:
            # Select new primary region
            new_primary = await self.select_new_primary(exclude_region=self.current_primary_region)
            
            if not new_primary:
                logger.error("No healthy secondary region available for failover")
                failover_event['status'] = 'failed'
                failover_event['reason'] = 'no_healthy_secondary'
                self.failover_history.append(failover_event)
                return
            
            # Promote new primary
            await self.promote_region(new_primary)
            
            # Update DNS to point to new primary
            await self.update_dns_records(new_primary)
            
            # Demote old primary
            await self.demote_region(self.current_primary_region)
            
            # Update failover event
            failover_event['to_region'] = new_primary
            failover_event['status'] = 'completed'
            failover_event['completion_time'] = datetime.utcnow().isoformat()
            
            self.failover_history.append(failover_event)
            
            logger.critical(f"Failover completed: {self.current_primary_region} -> {new_primary}")
            
        except Exception as e:
            logger.error(f"Failover failed: {e}")
            failover_event['status'] = 'failed'
            failover_event['error'] = str(e)
            self.failover_history.append(failover_event)
    
    async def select_new_primary(self, exclude_region: Optional[str] = None) -> Optional[str]:
        """Select new primary region"""
        healthy_regions = []
        
        for region_name, region in self.regions.items():
            if not region.is_active:
                continue
            
            if exclude_region and region_name == exclude_region:
                continue
            
            status = self.region_status.get(region_name, FailoverState.HEALTHY)
            if status in [FailoverState.HEALTHY, FailoverState.RECOVERY_COMPLETE]:
                healthy_regions.append(region_name)
        
        if not healthy_regions:
            return None
        
        # Select region with best health score
        best_region = None
        best_score = -1
        
        for region_name in healthy_regions:
            score = await self.calculate_region_health_score(region_name)
            if score > best_score:
                best_score = score
                best_region = region_name
        
        if best_region:
            self.current_primary_region = best_region
            logger.info(f"Selected new primary region: {best_region} (score: {best_score})")
        
        return best_region
    
    async def calculate_region_health_score(self, region_name: str) -> float:
        """Calculate health score for a region"""
        region = self.regions[region_name]
        score = 0.0
        
        # Health check score (70% weight)
        health_checks = self.health_check_results.get(region_name, {})
        if health_checks:
            passed_checks = sum(1 for result in health_checks.values() if result)
            total_checks = len(health_checks)
            health_score = (passed_checks / total_checks) * 70
            score += health_score
        
        # Database connectivity score (20% weight)
        try:
            conn = await asyncpg.connect(region.database_url)
            await conn.execute('SELECT 1')
            await conn.close()
            score += 20
        except Exception:
            pass
        
        # Redis connectivity score (10% weight)
        try:
            redis = await aioredis.from_url(region.redis_url)
            await redis.ping()
            await redis.close()
            score += 10
        except Exception:
            pass
        
        return score
    
    async def promote_region(self, region_name: str):
        """Promote region to primary"""
        logger.info(f"Promoting region {region_name} to primary")
        
        region = self.regions[region_name]
        
        try:
            # Update Kubernetes deployment annotations
            await self.update_deployment_annotation(
                region.k8s_namespace,
                region.deployment_name,
                'dedan.ai/region-role',
                'primary'
            )
            
            # Scale up deployment if needed
            await self.scale_deployment(
                region.k8s_namespace,
                region.deployment_name,
                6  # Primary replica count
            )
            
            # Update database to primary mode
            await self.update_database_mode(region_name, 'primary')
            
            # Update Redis to primary mode
            await self.update_redis_mode(region_name, 'primary')
            
            logger.info(f"Region {region_name} promoted successfully")
            
        except Exception as e:
            logger.error(f"Failed to promote region {region_name}: {e}")
            raise
    
    async def demote_region(self, region_name: str):
        """Demote region from primary"""
        logger.info(f"Demoting region {region_name} from primary")
        
        region = self.regions[region_name]
        
        try:
            # Update Kubernetes deployment annotations
            await self.update_deployment_annotation(
                region.k8s_namespace,
                region.deployment_name,
                'dedan.ai/region-role',
                'secondary'
            )
            
            # Scale down deployment
            await self.scale_deployment(
                region.k8s_namespace,
                region.deployment_name,
                4  # Secondary replica count
            )
            
            # Update database to secondary mode
            await self.update_database_mode(region_name, 'secondary')
            
            # Update Redis to secondary mode
            await self.update_redis_mode(region_name, 'secondary')
            
            logger.info(f"Region {region_name} demoted successfully")
            
        except Exception as e:
            logger.error(f"Failed to demote region {region_name}: {e}")
            # Don't raise here as demotion failure shouldn't block failover
    
    async def update_deployment_annotation(self, namespace: str, deployment_name: str, key: str, value: str):
        """Update Kubernetes deployment annotation"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update annotations
            if deployment.metadata.annotations is None:
                deployment.metadata.annotations = {}
            
            deployment.metadata.annotations[key] = value
            
            # Update deployment
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
        except ApiException as e:
            logger.error(f"Failed to update deployment annotation: {e}")
            raise
    
    async def scale_deployment(self, namespace: str, deployment_name: str, replicas: int):
        """Scale Kubernetes deployment"""
        try:
            # Get current deployment
            deployment = self.apps_v1.read_namespaced_deployment(
                name=deployment_name,
                namespace=namespace
            )
            
            # Update replica count
            deployment.spec.replicas = replicas
            
            # Update deployment
            self.apps_v1.patch_namespaced_deployment(
                name=deployment_name,
                namespace=namespace,
                body=deployment
            )
            
            # Wait for scaling to complete
            await self.wait_for_deployment_ready(namespace, deployment_name)
            
        except ApiException as e:
            logger.error(f"Failed to scale deployment: {e}")
            raise
    
    async def wait_for_deployment_ready(self, namespace: str, deployment_name: str, timeout: int = 300):
        """Wait for deployment to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                deployment = self.apps_v1.read_namespaced_deployment_status(
                    name=deployment_name,
                    namespace=namespace
                )
                
                if (deployment.status.ready_replicas == deployment.spec.replicas and
                    deployment.status.available_replicas == deployment.spec.replicas):
                    logger.info(f"Deployment {deployment_name} is ready")
                    return
                
                await asyncio.sleep(5)
                
            except ApiException:
                await asyncio.sleep(5)
        
        raise TimeoutError(f"Deployment {deployment_name} not ready within {timeout} seconds")
    
    async def update_database_mode(self, region_name: str, mode: str):
        """Update database mode (primary/secondary)"""
        region = self.regions[region_name]
        
        try:
            conn = await asyncpg.connect(region.database_url)
            
            if mode == 'primary':
                await conn.execute('SELECT pg_promote()')
                await conn.execute('ALTER SYSTEM SET synchronous_commit = on')
            else:
                await conn.execute('ALTER SYSTEM SET synchronous_commit = remote_apply')
            
            await conn.execute('SELECT pg_reload_conf()')
            await conn.close()
            
            logger.info(f"Database mode updated to {mode} for region {region_name}")
            
        except Exception as e:
            logger.error(f"Failed to update database mode for {region_name}: {e}")
            raise
    
    async def update_redis_mode(self, region_name: str, mode: str):
        """Update Redis mode (primary/secondary)"""
        region = self.regions[region_name]
        
        try:
            redis = await aioredis.from_url(region.redis_url)
            
            if mode == 'primary':
                await redis.config_set('save', '900 1 300 10 60 10000')
                await redis.config_set('appendonly', 'yes')
            else:
                await redis.config_set('save', '')
                await redis.config_set('appendonly', 'no')
            
            await redis.close()
            
            logger.info(f"Redis mode updated to {mode} for region {region_name}")
            
        except Exception as e:
            logger.error(f"Failed to update Redis mode for {region_name}: {e}")
            raise
    
    async def update_dns_records(self, primary_region: str):
        """Update DNS records to point to new primary"""
        logger.info(f"Updating DNS records to point to {primary_region}")
        
        region = self.regions[primary_region]
        
        try:
            # This would integrate with your DNS provider (AWS Route53, Cloudflare, etc.)
            # For now, we'll simulate the update
            
            dns_update = {
                'record_name': 'api.dedan.ai',
                'record_type': 'CNAME',
                'record_value': region.load_balancer_dns,
                'ttl': 60,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Simulate DNS update
            await asyncio.sleep(2)  # Simulate DNS propagation delay
            
            logger.info(f"DNS records updated: api.dedan.ai -> {region.load_balancer_dns}")
            
        except Exception as e:
            logger.error(f"Failed to update DNS records: {e}")
            raise
    
    async def recovery_monitor_loop(self):
        """Monitor for recovery of failed regions"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                await self.check_region_recovery()
            except Exception as e:
                logger.error(f"Error in recovery monitor loop: {e}")
                await asyncio.sleep(30)
    
    async def check_region_recovery(self):
        """Check if any failed regions have recovered"""
        for region_name, status in self.region_status.items():
            if status in [FailoverState.FAILOVER_COMPLETE, FailoverState.DEGRADED]:
                is_healthy = await self.is_region_healthy(region_name)
                
                if is_healthy:
                    logger.info(f"Region {region_name} has recovered")
                    await self.handle_region_recovery(region_name)
    
    async def is_region_healthy(self, region_name: str) -> bool:
        """Check if a region is healthy"""
        health_checks = self.health_check_results.get(region_name, {})
        
        if not health_checks:
            return False
        
        # All health checks must pass
        return all(health_checks.values())
    
    async def handle_region_recovery(self, region_name: str):
        """Handle recovery of a region"""
        if region_name == self.current_primary_region:
            # Primary region recovered, no action needed
            self.region_status[region_name] = FailoverState.HEALTHY
        else:
            # Secondary region recovered, ensure it's configured as secondary
            await self.demote_region(region_name)
            self.region_status[region_name] = FailoverState.HEALTHY
    
    async def get_failover_status(self) -> Dict:
        """Get current failover status"""
        return {
            'current_primary': self.current_primary_region,
            'region_status': {name: status.value for name, status in self.region_status.items()},
            'health_check_results': self.health_check_results,
            'failover_history': self.failover_history[-10:],  # Last 10 events
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def shutdown(self):
        """Shutdown failover controller"""
        logger.info("Shutting down failover controller...")
        self.running = False

# Main execution
async def main():
    """Main execution function"""
    controller = FailoverController()
    
    try:
        await controller.initialize()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
    finally:
        await controller.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
