"""
Load Testing Scenarios for DEDAN 2.0
100K concurrent users, 1M requests/sec testing
"""

import asyncio
import aiohttp
import pytest
import time
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import random
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadTestConfig:
    """Load test configuration"""
    BASE_URL = "https://api.dedan.ai"
    CONCURRENT_USERS = 100000
    REQUESTS_PER_SECOND = 1000000
    TEST_DURATION = 300  # 5 minutes
    RAMP_UP_TIME = 60  # 1 minute ramp up
    COOLDOWN_TIME = 30  # 30 seconds cooldown
    
class LoadTestMetrics:
    """Load test metrics collector"""
    
    def __init__(self):
        self.requests_sent = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.response_times = []
        self.errors = {}
        self.start_time = None
        self.end_time = None
        self.concurrent_users = 0
        self.peak_rps = 0
        self.current_rps = 0
    
    def record_request(self, success: bool, response_time: float, error: Optional[str] = None):
        """Record a request result"""
        self.requests_sent += 1
        
        if success:
            self.requests_successful += 1
            self.response_times.append(response_time)
        else:
            self.requests_failed += 1
            if error:
                self.errors[error] = self.errors.get(error, 0) + 1
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate performance metrics"""
        if not self.response_times:
            return {
                'requests_sent': self.requests_sent,
                'requests_successful': self.requests_successful,
                'requests_failed': self.requests_failed,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'p50_response_time': 0.0,
                'p95_response_time': 0.0,
                'p99_response_time': 0.0,
                'peak_rps': self.peak_rps,
                'avg_rps': 0.0,
                'errors': self.errors,
                'duration': 0.0
            }
        
        total_requests = self.requests_sent
        success_rate = (self.requests_successful / total_requests) * 100 if total_requests > 0 else 0
        
        sorted_times = sorted(self.response_times)
        total_time = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
        avg_rps = total_requests / total_time if total_time > 0 else 0
        
        return {
            'requests_sent': total_requests,
            'requests_successful': self.requests_successful,
            'requests_failed': self.requests_failed,
            'success_rate': success_rate,
            'avg_response_time': statistics.mean(self.response_times),
            'p50_response_time': statistics.median(self.response_times),
            'p95_response_time': self._percentile(sorted_times, 0.95),
            'p99_response_time': self._percentile(sorted_times, 0.99),
            'peak_rps': self.peak_rps,
            'avg_rps': avg_rps,
            'errors': self.errors,
            'duration': total_time
        }
    
    def _percentile(self, sorted_data: List[float], percentile: float) -> float:
        """Calculate percentile"""
        if not sorted_data:
            return 0.0
        
        index = int(len(sorted_data) * percentile)
        if index >= len(sorted_data):
            index = len(sorted_data) - 1
        
        return sorted_data[index]

class LoadTestRunner:
    """Load test runner"""
    
    def __init__(self):
        self.metrics = LoadTestMetrics()
        self.session = None
        self.running = False
        self.user_sessions = []
    
    async def run_load_test(self, test_type: str = "standard") -> Dict[str, Any]:
        """Run load test"""
        logger.info(f"Starting load test: {test_type}")
        
        self.metrics.start_time = datetime.utcnow()
        self.running = True
        
        try:
            if test_type == "100k_users":
                await self._run_100k_users_test()
            elif test_type == "1m_rps":
                await self._run_1m_rps_test()
            elif test_type == "stress":
                await self._run_stress_test()
            else:
                await self._run_standard_test()
        
        finally:
            self.metrics.end_time = datetime.utcnow()
            self.running = False
        
        return self.metrics.calculate_metrics()
    
    async def _run_100k_users_test(self):
        """Run test with 100K concurrent users"""
        logger.info("Running 100K concurrent users test")
        
        # Create session with high connection limits
        connector = aiohttp.TCPConnector(
            limit=200000,  # High connection limit
            limit_per_host=50000,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=60, connect=10)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DEDAN-LoadTest/1.0'}
        ) as session:
            self.session = session
            
            # Create user tasks
            tasks = []
            for user_id in range(LoadTestConfig.CONCURRENT_USERS):
                task = self._simulate_user_session(user_id)
                tasks.append(task)
            
            # Ramp up users
            await self._ramp_up_users(tasks, LoadTestConfig.RAMP_UP_TIME)
            
            # Run for test duration
            await asyncio.sleep(LoadTestConfig.TEST_DURATION)
            
            # Cooldown
            await self._cooldown_users(tasks, LoadTestConfig.COOLDOWN_TIME)
    
    async def _run_1m_rps_test(self):
        """Run test with 1M requests per second"""
        logger.info("Running 1M RPS test")
        
        # Calculate requests per task
        num_tasks = 1000
        requests_per_task = LoadTestConfig.REQUESTS_PER_SECOND // num_tasks
        
        connector = aiohttp.TCPConnector(
            limit=10000,
            limit_per_host=5000,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=5, connect=2)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DEDAN-LoadTest/1.0'}
        ) as session:
            self.session = session
            
            # Create high-frequency request tasks
            tasks = []
            for task_id in range(num_tasks):
                task = self._high_frequency_requests(task_id, requests_per_task)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_stress_test(self):
        """Run stress test with maximum load"""
        logger.info("Running stress test")
        
        # Extreme configuration for stress testing
        connector = aiohttp.TCPConnector(
            limit=500000,
            limit_per_host=100000,
            ttl_dns_cache=60,
            use_dns_cache=True,
            keepalive_timeout=60,
            enable_cleanup_closed=False  # Disable for max performance
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DEDAN-LoadTest/1.0'}
        ) as session:
            self.session = session
            
            # Create stress tasks
            tasks = []
            for i in range(200000):  # 200K concurrent connections
                task = self._stress_request(i)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _run_standard_test(self):
        """Run standard load test"""
        logger.info("Running standard load test")
        
        connector = aiohttp.TCPConnector(
            limit=10000,
            limit_per_host=1000,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=30
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=5)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DEDAN-LoadTest/1.0'}
        ) as session:
            self.session = session
            
            # Create standard load tasks
            tasks = []
            for i in range(10000):  # 10K concurrent users
                task = self._standard_user_session(i)
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _simulate_user_session(self, user_id: int):
        """Simulate a user session"""
        start_time = time.time()
        request_count = 0
        
        while self.running:
            try:
                # Simulate realistic user behavior
                await self._user_browse_minerals(user_id)
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
                await self._user_check_portfolio(user_id)
                await asyncio.sleep(random.uniform(0.2, 1.0))
                
                await self._user_place_order(user_id)
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
                request_count += 1
                
                # Update RPS
                current_time = time.time()
                elapsed = current_time - start_time
                if elapsed > 0:
                    current_rps = request_count / elapsed
                    self.metrics.current_rps = current_rps
                    self.metrics.peak_rps = max(self.metrics.peak_rps, current_rps)
                
            except Exception as e:
                self.metrics.record_request(False, 0, str(e))
                await asyncio.sleep(1.0)
    
    async def _user_browse_minerals(self, user_id: int):
        """Simulate user browsing minerals"""
        endpoints = [
            "/api/v1/minerals",
            "/api/v1/minerals/gold",
            "/api/v1/minerals/silver",
            "/api/v1/market/data",
            "/api/v1/market/stats"
        ]
        
        endpoint = random.choice(endpoints)
        start_time = time.time()
        
        try:
            async with self.session.get(f"{LoadTestConfig.BASE_URL}{endpoint}") as response:
                response_time = time.time() - start_time
                success = response.status == 200
                self.metrics.record_request(success, response_time)
                
                if success:
                    data = await response.json()
                    # Simulate processing the response
                    await asyncio.sleep(0.01)
        
        except Exception as e:
            self.metrics.record_request(False, time.time() - start_time, str(e))
    
    async def _user_check_portfolio(self, user_id: int):
        """Simulate user checking portfolio"""
        start_time = time.time()
        
        try:
            async with self.session.get(f"{LoadTestConfig.BASE_URL}/api/v1/portfolio/{user_id}") as response:
                response_time = time.time() - start_time
                success = response.status == 200
                self.metrics.record_request(success, response_time)
        
        except Exception as e:
            self.metrics.record_request(False, time.time() - start_time, str(e))
    
    async def _user_place_order(self, user_id: int):
        """Simulate user placing order"""
        start_time = time.time()
        
        order_data = {
            "mineral_id": random.choice(["gold", "silver", "copper", "iron"]),
            "order_type": random.choice(["buy", "sell"]),
            "quantity": random.uniform(1, 100),
            "price": random.uniform(10, 1000)
        }
        
        try:
            async with self.session.post(
                f"{LoadTestConfig.BASE_URL}/api/v1/orders",
                json=order_data
            ) as response:
                response_time = time.time() - start_time
                success = response.status in [200, 201]
                self.metrics.record_request(success, response_time)
        
        except Exception as e:
            self.metrics.record_request(False, time.time() - start_time, str(e))
    
    async def _high_frequency_requests(self, task_id: int, requests_per_second: int):
        """Generate high-frequency requests"""
        interval = 1.0 / requests_per_second
        
        while self.running:
            start_time = time.time()
            
            try:
                async with self.session.get(f"{LoadTestConfig.BASE_URL}/api/v1/health") as response:
                    response_time = time.time() - start_time
                    success = response.status == 200
                    self.metrics.record_request(success, response_time)
            
            except Exception as e:
                self.metrics.record_request(False, time.time() - start_time, str(e))
            
            await asyncio.sleep(interval)
    
    async def _stress_request(self, request_id: int):
        """Generate stress requests"""
        while self.running:
            start_time = time.time()
            
            try:
                # Use different endpoints for stress
                endpoints = [
                    "/api/v1/minerals",
                    "/api/v1/market/data",
                    "/api/v1/trades",
                    "/api/v1/orders"
                ]
                
                endpoint = random.choice(endpoints)
                method = random.choice(["GET", "POST"])
                
                if method == "GET":
                    async with self.session.get(f"{LoadTestConfig.BASE_URL}{endpoint}") as response:
                        response_time = time.time() - start_time
                        success = response.status == 200
                        self.metrics.record_request(success, response_time)
                else:
                    data = {"test": "data"} if endpoint == "/api/v1/orders" else None
                    async with self.session.post(f"{LoadTestConfig.BASE_URL}{endpoint}", json=data) as response:
                        response_time = time.time() - start_time
                        success = response.status in [200, 201]
                        self.metrics.record_request(success, response_time)
            
            except Exception as e:
                self.metrics.record_request(False, time.time() - start_time, str(e))
    
    async def _standard_user_session(self, user_id: int):
        """Simulate standard user session"""
        await self._simulate_user_session(user_id)
    
    async def _ramp_up_users(self, tasks: List, ramp_up_time: int):
        """Ramp up users gradually"""
        logger.info(f"Ramping up {len(tasks)} users over {ramp_up_time} seconds")
        
        batch_size = len(tasks) // ramp_up_time
        current_batch = 0
        
        for second in range(ramp_up_time):
            start_index = current_batch * batch_size
            end_index = min(start_index + batch_size, len(tasks))
            
            if start_index < len(tasks):
                batch_tasks = tasks[start_index:end_index]
                asyncio.create_task(asyncio.gather(*batch_tasks, return_exceptions=True))
            
            current_batch += 1
            await asyncio.sleep(1)
        
        # Start remaining tasks
        if current_batch * batch_size < len(tasks):
            remaining_tasks = tasks[current_batch * batch_size:]
            asyncio.create_task(asyncio.gather(*remaining_tasks, return_exceptions=True))
    
    async def _cooldown_users(self, tasks: List, cooldown_time: int):
        """Gradually cool down users"""
        logger.info(f"Cooldown {len(tasks)} users over {cooldown_time} seconds")
        
        # Stop user sessions gradually
        batch_size = len(tasks) // cooldown_time if cooldown_time > 0 else len(tasks)
        
        for second in range(cooldown_time):
            # This would normally stop user sessions
            # For load testing, we just wait
            await asyncio.sleep(1)

class TestLoadScenarios:
    """Test load scenarios"""
    
    @pytest.mark.asyncio
    @pytest.mark.load
    async def test_100k_concurrent_users(self):
        """Test 100K concurrent users"""
        runner = LoadTestRunner()
        
        # Run short test for pytest
        runner.metrics.start_time = datetime.utcnow()
        runner.running = True
        
        # Simulate 1000 users for pytest (reduced from 100K)
        tasks = []
        for i in range(1000):
            task = runner._simulate_user_session(i)
            tasks.append(task)
        
        # Run for 10 seconds
        await asyncio.sleep(10)
        runner.running = False
        runner.metrics.end_time = datetime.utcnow()
        
        metrics = runner.metrics.calculate_metrics()
        
        # Assert performance targets
        assert metrics['success_rate'] >= 95.0
        assert metrics['avg_response_time'] <= 2.0
        assert metrics['p95_response_time'] <= 5.0
        assert metrics['requests_sent'] >= 10000  # At least 10 requests per user
    
    @pytest.mark.asyncio
    @pytest.mark.load
    async def test_high_rps_load(self):
        """Test high RPS load"""
        runner = LoadTestRunner()
        
        runner.metrics.start_time = datetime.utcnow()
        runner.running = True
        
        # Simulate high RPS
        tasks = []
        for i in range(100):
            task = runner._high_frequency_requests(i, 100)  # 100 RPS per task
            tasks.append(task)
        
        # Run for 5 seconds
        await asyncio.sleep(5)
        runner.running = False
        runner.metrics.end_time = datetime.utcnow()
        
        metrics = runner.metrics.calculate_metrics()
        
        # Assert performance targets
        assert metrics['success_rate'] >= 90.0
        assert metrics['avg_response_time'] <= 1.0
        assert metrics['peak_rps'] >= 10000
    
    @pytest.mark.asyncio
    @pytest.mark.load
    async def test_stress_test(self):
        """Test stress scenario"""
        runner = LoadTestRunner()
        
        runner.metrics.start_time = datetime.utcnow()
        runner.running = True
        
        # Simulate stress
        tasks = []
        for i in range(500):
            task = runner._stress_request(i)
            tasks.append(task)
        
        # Run for 3 seconds
        await asyncio.sleep(3)
        runner.running = False
        runner.metrics.end_time = datetime.utcnow()
        
        metrics = runner.metrics.calculate_metrics()
        
        # Stress test should handle high load gracefully
        assert metrics['success_rate'] >= 80.0  # Allow some failures under stress
        assert metrics['requests_sent'] >= 1000
    
    @pytest.mark.asyncio
    @pytest.mark.load
    async def test_api_endpoints_load(self):
        """Test specific API endpoints under load"""
        runner = LoadTestRunner()
        
        runner.metrics.start_time = datetime.utcnow()
        runner.running = True
        
        # Test different endpoints
        endpoints = [
            "/api/v1/minerals",
            "/api/v1/market/data",
            "/api/v1/trades",
            "/api/v1/orders"
        ]
        
        tasks = []
        for endpoint in endpoints:
            for i in range(100):
                task = self._test_endpoint_load(runner, endpoint, i)
                tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        runner.running = False
        runner.metrics.end_time = datetime.utcnow()
        
        metrics = runner.metrics.calculate_metrics()
        
        # All endpoints should handle load
        assert metrics['success_rate'] >= 90.0
        assert metrics['avg_response_time'] <= 1.5
    
    async def _test_endpoint_load(self, runner: LoadTestRunner, endpoint: str, task_id: int):
        """Test specific endpoint under load"""
        start_time = time.time()
        
        try:
            async with runner.session.get(f"{LoadTestConfig.BASE_URL}{endpoint}") as response:
                response_time = time.time() - start_time
                success = response.status == 200
                runner.metrics.record_request(success, response_time)
        
        except Exception as e:
            runner.metrics.record_request(False, time.time() - start_time, str(e))

# Test runner
async def run_load_tests():
    """Run all load tests"""
    import subprocess
    import sys
    
    # Run pytest with load markers
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/integration/test_load_scenarios.py",
        "-v",
        "--tb=short",
        "-m", "load",
        "--maxfail=5",
        "--timeout=300"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("Load Test Results:")
    print(f"Return Code: {result.returncode}")
    print(f"Output:\n{result.stdout}")
    if result.stderr:
        print(f"Errors:\n{result.stderr}")
    
    return result.returncode == 0

if __name__ == "__main__":
    asyncio.run(run_load_tests())
