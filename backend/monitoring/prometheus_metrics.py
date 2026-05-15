"""
Prometheus Metrics for DEDAN 2.0
Comprehensive monitoring with 50+ custom metrics
"""

import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from prometheus_client import Counter, Histogram, Gauge, Info, Summary, CollectorRegistry, generate_latest, CONTENT_TYPE_LATEST
import psutil
import asyncio
import json
from functools import wraps
from contextlib import contextmanager
import threading
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MetricConfig:
    """Metric configuration"""
    name: str
    description: str
    labels: List[str]
    metric_type: str  # counter, histogram, gauge, info, summary
    buckets: Optional[List[float]] = None

class PrometheusMetrics:
    """Advanced Prometheus metrics collector"""
    
    def __init__(self, registry: Optional[CollectorRegistry] = None):
        self.registry = registry or CollectorRegistry()
        self.metrics = {}
        self.metric_configs = self._load_metric_configs()
        self.start_time = time.time()
        self.request_latencies = defaultdict(lambda: deque(maxlen=1000))
        self.error_counts = defaultdict(int)
        self.active_connections = defaultdict(int)
        
        # Initialize all metrics
        self._initialize_metrics()
        
        # Background monitoring thread
        self.monitoring_thread = None
        self.running = False
    
    def _load_metric_configs(self) -> List[MetricConfig]:
        """Load metric configurations"""
        return [
            # HTTP Metrics
            MetricConfig("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"], "counter"),
            MetricConfig("http_request_duration_seconds", "HTTP request duration", ["method", "endpoint"], "histogram", [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]),
            MetricConfig("http_request_size_bytes", "HTTP request size", ["method", "endpoint"], "summary"),
            MetricConfig("http_response_size_bytes", "HTTP response size", ["method", "endpoint"], "summary"),
            
            # Database Metrics
            MetricConfig("db_connections_active", "Active database connections", ["database", "pool"], "gauge"),
            MetricConfig("db_connections_idle", "Idle database connections", ["database", "pool"], "gauge"),
            MetricConfig("db_query_duration_seconds", "Database query duration", ["database", "query_type", "table"], "histogram", [0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]),
            MetricConfig("db_queries_total", "Total database queries", ["database", "query_type", "table", "status"], "counter"),
            MetricConfig("db_transactions_total", "Total database transactions", ["database", "status"], "counter"),
            
            # Trading Metrics
            MetricConfig("trading_orders_total", "Total trading orders", ["mineral", "order_type", "status"], "counter"),
            MetricConfig("trading_volume_usd", "Trading volume in USD", ["mineral", "market"], "counter"),
            MetricConfig("trading_price_usd", "Current trading price", ["mineral"], "gauge"),
            MetricConfig("trading_settlement_duration_seconds", "Trade settlement duration", ["mineral", "settlement_type"], "histogram", [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 25.0]),
            MetricConfig("trading_slippage_percent", "Trade slippage percentage", ["mineral", "order_type"], "histogram", [0.01, 0.05, 0.1, 0.25, 0.5, 1.0]),
            
            # Blockchain Metrics
            MetricConfig("blockchain_transactions_total", "Total blockchain transactions", ["blockchain", "status"], "counter"),
            MetricConfig("blockchain_transaction_duration_seconds", "Blockchain transaction duration", ["blockchain"], "histogram", [1.0, 5.0, 10.0, 30.0, 60.0, 300.0]),
            MetricConfig("blockchain_gas_price_gwei", "Blockchain gas price", ["blockchain"], "gauge"),
            MetricConfig("blockchain_block_number", "Current block number", ["blockchain"], "gauge"),
            MetricConfig("blockchain_confirmations", "Transaction confirmations", ["blockchain", "transaction"], "gauge"),
            
            # Quantum Metrics
            MetricConfig("quantum_circuits_executed_total", "Total quantum circuits executed", ["circuit_type", "backend"], "counter"),
            MetricConfig("quantum_circuit_duration_ms", "Quantum circuit execution duration", ["circuit_type", "backend"], "histogram", [0.5, 1.0, 2.5, 5.0, 10.0, 25.0, 50.0]),
            MetricConfig("quantum_fidelity", "Quantum circuit fidelity", ["circuit_type", "backend"], "gauge"),
            MetricConfig("quantum_qubits_used", "Quantum qubits used", ["circuit_type"], "gauge"),
            MetricConfig("quantum_advantage_percent", "Quantum advantage percentage", ["algorithm"], "gauge"),
            
            # Cache Metrics
            MetricConfig("cache_operations_total", "Total cache operations", ["cache", "operation", "status"], "counter"),
            MetricConfig("cache_hit_ratio", "Cache hit ratio", ["cache"], "gauge"),
            MetricConfig("cache_size_bytes", "Cache size in bytes", ["cache"], "gauge"),
            MetricConfig("cache_evictions_total", "Total cache evictions", ["cache"], "counter"),
            
            # System Metrics
            MetricConfig("system_cpu_usage_percent", "CPU usage percentage", ["core"], "gauge"),
            MetricConfig("system_memory_usage_bytes", "Memory usage in bytes", ["type"], "gauge"),
            MetricConfig("system_disk_usage_bytes", "Disk usage in bytes", ["device", "type"], "gauge"),
            MetricConfig("system_network_bytes_total", "Network bytes total", ["interface", "direction"], "counter"),
            MetricConfig("system_load_average", "System load average", ["period"], "gauge"),
            
            # Application Metrics
            MetricConfig("app_uptime_seconds", "Application uptime in seconds", [], "gauge"),
            MetricConfig("app_version_info", "Application version info", ["version", "build", "commit"], "info"),
            MetricConfig("app_errors_total", "Total application errors", ["module", "error_type", "severity"], "counter"),
            MetricConfig("app_warnings_total", "Total application warnings", ["module", "warning_type"], "counter"),
            MetricConfig("app_background_jobs_total", "Total background jobs", ["job_type", "status"], "counter"),
            MetricConfig("app_background_job_duration_seconds", "Background job duration", ["job_type"], "histogram", [1.0, 5.0, 10.0, 30.0, 60.0, 300.0]),
            
            # Business Metrics
            MetricConfig("business_users_active", "Active users", ["period"], "gauge"),
            MetricConfig("business_revenue_usd", "Revenue in USD", ["period", "source"], "counter"),
            MetricConfig("business_trading_volume_usd", "Trading volume in USD", ["period", "mineral"], "counter"),
            MetricConfig("business_fees_collected_usd", "Fees collected in USD", ["period", "fee_type"], "counter"),
            MetricConfig("business_portfolio_value_usd", "Total portfolio value", [], "gauge"),
            
            # Security Metrics
            MetricConfig("security_authentication_attempts_total", "Authentication attempts", ["method", "status"], "counter"),
            MetricConfig("security_rate_limit_exceeded_total", "Rate limit exceeded", ["endpoint", "user"], "counter"),
            MetricConfig("security_failed_logins_total", "Failed login attempts", ["reason", "source_ip"], "counter"),
            MetricConfig("security_blocked_requests_total", "Blocked requests", ["reason", "source_ip"], "counter"),
            
            # Performance Metrics
            MetricConfig("performance_response_time_p95_seconds", "95th percentile response time", ["endpoint"], "gauge"),
            MetricConfig("performance_response_time_p99_seconds", "99th percentile response time", ["endpoint"], "gauge"),
            MetricConfig("performance_throughput_requests_per_second", "Throughput", ["endpoint"], "gauge"),
            MetricConfig("performance_error_rate_percent", "Error rate percentage", ["endpoint"], "gauge"),
            
            # Integration Metrics
            MetricConfig("integration_api_calls_total", "API calls to external services", ["service", "endpoint", "status"], "counter"),
            MetricConfig("integration_api_duration_seconds", "External API call duration", ["service", "endpoint"], "histogram", [0.1, 0.5, 1.0, 2.5, 5.0, 10.0]),
            MetricConfig("integration_webhook_deliveries_total", "Webhook deliveries", ["service", "status"], "counter"),
            MetricConfig("integration_queue_size", "Queue size", ["queue"], "gauge"),
        ]
    
    def _initialize_metrics(self):
        """Initialize all metrics"""
        for config in self.metric_configs:
            try:
                if config.metric_type == "counter":
                    metric = Counter(
                        config.name,
                        config.description,
                        labelnames=config.labels,
                        registry=self.registry
                    )
                elif config.metric_type == "histogram":
                    metric = Histogram(
                        config.name,
                        config.description,
                        labelnames=config.labels,
                        buckets=config.buckets or [],
                        registry=self.registry
                    )
                elif config.metric_type == "gauge":
                    metric = Gauge(
                        config.name,
                        config.description,
                        labelnames=config.labels,
                        registry=self.registry
                    )
                elif config.metric_type == "info":
                    metric = Info(
                        config.name,
                        config.description,
                        labelnames=config.labels,
                        registry=self.registry
                    )
                elif config.metric_type == "summary":
                    metric = Summary(
                        config.name,
                        config.description,
                        labelnames=config.labels,
                        registry=self.registry
                    )
                else:
                    logger.warning(f"Unknown metric type: {config.metric_type}")
                    continue
                
                self.metrics[config.name] = metric
                logger.debug(f"Initialized metric: {config.name}")
                
            except Exception as e:
                logger.error(f"Failed to initialize metric {config.name}: {e}")
    
    def increment_counter(self, metric_name: str, labels: Dict[str, str] = None, value: int = 1):
        """Increment counter metric"""
        try:
            metric = self.metrics.get(metric_name)
            if metric and hasattr(metric, 'inc'):
                if labels:
                    metric.labels(**labels).inc(value)
                else:
                    metric.inc(value)
        except Exception as e:
            logger.error(f"Failed to increment counter {metric_name}: {e}")
    
    def observe_histogram(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Observe histogram metric"""
        try:
            metric = self.metrics.get(metric_name)
            if metric and hasattr(metric, 'observe'):
                if labels:
                    metric.labels(**labels).observe(value)
                else:
                    metric.observe(value)
        except Exception as e:
            logger.error(f"Failed to observe histogram {metric_name}: {e}")
    
    def set_gauge(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge metric"""
        try:
            metric = self.metrics.get(metric_name)
            if metric and hasattr(metric, 'set'):
                if labels:
                    metric.labels(**labels).set(value)
                else:
                    metric.set(value)
        except Exception as e:
            logger.error(f"Failed to set gauge {metric_name}: {e}")
    
    def set_info(self, metric_name: str, info: Dict[str, str]):
        """Set info metric"""
        try:
            metric = self.metrics.get(metric_name)
            if metric and hasattr(metric, 'info'):
                metric.info(info)
        except Exception as e:
            logger.error(f"Failed to set info {metric_name}: {e}")
    
    def observe_summary(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Observe summary metric"""
        try:
            metric = self.metrics.get(metric_name)
            if metric and hasattr(metric, 'observe'):
                if labels:
                    metric.labels(**labels).observe(value)
                else:
                    metric.observe(value)
        except Exception as e:
            logger.error(f"Failed to observe summary {metric_name}: {e}")
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.running:
            return
        
        self.running = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Started Prometheus metrics monitoring")
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Stopped Prometheus metrics monitoring")
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.running:
            try:
                self._collect_system_metrics()
                self._collect_application_metrics()
                self._calculate_derived_metrics()
                time.sleep(10)  # Collect every 10 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)
    
    def _collect_system_metrics(self):
        """Collect system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            for i in range(cpu_count):
                self.set_gauge("system_cpu_usage_percent", cpu_percent / cpu_count, {"core": str(i)})
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.set_gauge("system_memory_usage_bytes", memory.used, {"type": "used"})
            self.set_gauge("system_memory_usage_bytes", memory.available, {"type": "available"})
            self.set_gauge("system_memory_usage_bytes", memory.total, {"type": "total"})
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.set_gauge("system_disk_usage_bytes", disk.used, {"device": "/", "type": "used"})
            self.set_gauge("system_disk_usage_bytes", disk.free, {"device": "/", "type": "free"})
            self.set_gauge("system_disk_usage_bytes", disk.total, {"device": "/", "type": "total"})
            
            # Network metrics
            network = psutil.net_io_counters()
            if network:
                self.increment_counter("system_network_bytes_total", {"interface": "all", "direction": "sent"}, network.bytes_sent)
                self.increment_counter("system_network_bytes_total", {"interface": "all", "direction": "recv"}, network.bytes_recv)
            
            # Load average
            load_avg = psutil.getloadavg()
            self.set_gauge("system_load_average", load_avg[0], {"period": "1m"})
            self.set_gauge("system_load_average", load_avg[1], {"period": "5m"})
            self.set_gauge("system_load_average", load_avg[2], {"period": "15m"})
            
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    def _collect_application_metrics(self):
        """Collect application metrics"""
        try:
            # Uptime
            uptime = time.time() - self.start_time
            self.set_gauge("app_uptime_seconds", uptime)
            
            # Version info (static)
            self.set_info("app_version_info", {
                "version": "2.0.0",
                "build": "20240101",
                "commit": "abc123def456"
            })
            
        except Exception as e:
            logger.error(f"Error collecting application metrics: {e}")
    
    def _calculate_derived_metrics(self):
        """Calculate derived metrics"""
        try:
            # Calculate percentiles from latency data
            for endpoint, latencies in self.request_latencies.items():
                if latencies:
                    sorted_latencies = sorted(latencies)
                    n = len(sorted_latencies)
                    
                    if n > 0:
                        p95_index = int(0.95 * n)
                        p99_index = int(0.99 * n)
                        
                        p95 = sorted_latencies[min(p95_index, n - 1)]
                        p99 = sorted_latencies[min(p99_index, n - 1)]
                        
                        self.set_gauge("performance_response_time_p95_seconds", p95, {"endpoint": endpoint})
                        self.set_gauge("performance_response_time_p99_seconds", p99, {"endpoint": endpoint})
                        
                        # Calculate error rate
                        total_requests = len(latencies)
                        error_count = self.error_counts.get(endpoint, 0)
                        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0
                        
                        self.set_gauge("performance_error_rate_percent", error_rate, {"endpoint": endpoint})
                        
                        # Calculate throughput (requests per second in last minute)
                        recent_requests = sum(1 for t in latencies if time.time() - t < 60)
                        throughput = recent_requests / 60.0
                        
                        self.set_gauge("performance_throughput_requests_per_second", throughput, {"endpoint": endpoint})
            
        except Exception as e:
            logger.error(f"Error calculating derived metrics: {e}")
    
    def record_http_request(self, method: str, endpoint: str, status_code: int, duration: float, request_size: int, response_size: int):
        """Record HTTP request metrics"""
        status_category = "2xx" if 200 <= status_code < 300 else "3xx" if 300 <= status_code < 400 else "4xx" if 400 <= status_code < 500 else "5xx"
        
        self.increment_counter("http_requests_total", {"method": method, "endpoint": endpoint, "status": status_category})
        self.observe_histogram("http_request_duration_seconds", duration, {"method": method, "endpoint": endpoint})
        self.observe_summary("http_request_size_bytes", request_size, {"method": method, "endpoint": endpoint})
        self.observe_summary("http_response_size_bytes", response_size, {"method": method, "endpoint": endpoint})
        
        # Track latency for derived metrics
        self.request_latencies[endpoint].append(time.time())
        if status_code >= 400:
            self.error_counts[endpoint] += 1
    
    def record_database_query(self, database: str, query_type: str, table: str, duration: float, status: str):
        """Record database query metrics"""
        self.observe_histogram("db_query_duration_seconds", duration, {"database": database, "query_type": query_type, "table": table})
        self.increment_counter("db_queries_total", {"database": database, "query_type": query_type, "table": table, "status": status})
    
    def record_trading_order(self, mineral: str, order_type: str, status: str, volume_usd: float, settlement_duration: float = None, slippage: float = None):
        """Record trading order metrics"""
        self.increment_counter("trading_orders_total", {"mineral": mineral, "order_type": order_type, "status": status})
        self.increment_counter("trading_volume_usd", {"mineral": mineral, "market": "dedan"}, volume_usd)
        
        if settlement_duration:
            self.observe_histogram("trading_settlement_duration_seconds", settlement_duration, {"mineral": mineral, "settlement_type": "standard"})
        
        if slippage is not None:
            self.observe_histogram("trading_slippage_percent", slippage, {"mineral": mineral, "order_type": order_type})
    
    def record_blockchain_transaction(self, blockchain: str, duration: float, status: str, gas_price: float = None, block_number: int = None, confirmations: int = None):
        """Record blockchain transaction metrics"""
        self.increment_counter("blockchain_transactions_total", {"blockchain": blockchain, "status": status})
        self.observe_histogram("blockchain_transaction_duration_seconds", duration, {"blockchain": blockchain})
        
        if gas_price:
            self.set_gauge("blockchain_gas_price_gwei", gas_price, {"blockchain": blockchain})
        
        if block_number:
            self.set_gauge("blockchain_block_number", block_number, {"blockchain": blockchain})
        
        if confirmations:
            self.set_gauge("blockchain_confirmations", confirmations, {"blockchain": blockchain, "transaction": "latest"})
    
    def record_quantum_execution(self, circuit_type: str, backend: str, duration_ms: float, fidelity: float, qubits: int, advantage: float):
        """Record quantum execution metrics"""
        self.increment_counter("quantum_circuits_executed_total", {"circuit_type": circuit_type, "backend": backend})
        self.observe_histogram("quantum_circuit_duration_ms", duration_ms, {"circuit_type": circuit_type, "backend": backend})
        self.set_gauge("quantum_fidelity", fidelity, {"circuit_type": circuit_type, "backend": backend})
        self.set_gauge("quantum_qubits_used", qubits, {"circuit_type": circuit_type})
        self.set_gauge("quantum_advantage_percent", advantage, {"algorithm": circuit_type})
    
    def record_cache_operation(self, cache: str, operation: str, status: str, hit_ratio: float = None, size_bytes: int = None):
        """Record cache operation metrics"""
        self.increment_counter("cache_operations_total", {"cache": cache, "operation": operation, "status": status})
        
        if hit_ratio is not None:
            self.set_gauge("cache_hit_ratio", hit_ratio, {"cache": cache})
        
        if size_bytes:
            self.set_gauge("cache_size_bytes", size_bytes, {"cache": cache})
    
    def record_error(self, module: str, error_type: str, severity: str, message: str = None):
        """Record application error"""
        self.increment_counter("app_errors_total", {"module": module, "error_type": error_type, "severity": severity})
        logger.error(f"Error recorded: {module}:{error_type}:{severity} - {message}")
    
    def record_warning(self, module: str, warning_type: str, message: str = None):
        """Record application warning"""
        self.increment_counter("app_warnings_total", {"module": module, "warning_type": warning_type})
        logger.warning(f"Warning recorded: {module}:{warning_type} - {message}")
    
    def get_metrics_export(self) -> str:
        """Get metrics in Prometheus format"""
        try:
            return generate_latest(self.registry).decode('utf-8')
        except Exception as e:
            logger.error(f"Error generating metrics export: {e}")
            return ""
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        summary = {
            "total_metrics": len(self.metrics),
            "monitoring_duration_seconds": time.time() - self.start_time,
            "active_connections": dict(self.active_connections),
            "error_counts": dict(self.error_counts),
            "request_latencies": {
                endpoint: {
                    "count": len(latencies),
                    "avg": sum(latencies) / len(latencies) if latencies else 0,
                    "min": min(latencies) if latencies else 0,
                    "max": max(latencies) if latencies else 0
                }
                for endpoint, latencies in self.request_latencies.items()
            }
        }
        
        return summary

# Decorators for automatic metric recording
def track_http_requests(metrics: PrometheusMetrics):
    """Decorator to track HTTP requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            method = kwargs.get('method', 'GET')
            endpoint = kwargs.get('endpoint', 'unknown')
            request_size = len(str(kwargs.get('data', '')))
            
            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                response_size = len(str(getattr(result, 'body', '')))
                
                duration = time.time() - start_time
                metrics.record_http_request(method, endpoint, status_code, duration, request_size, response_size)
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_http_request(method, endpoint, 500, duration, request_size, 0)
                raise
        
        return wrapper
    return decorator

def track_database_queries(metrics: PrometheusMetrics):
    """Decorator to track database queries"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            query_type = kwargs.get('query_type', 'unknown')
            table = kwargs.get('table', 'unknown')
            database = kwargs.get('database', 'dedan')
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                metrics.record_database_query(database, query_type, table, duration, 'success')
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                metrics.record_database_query(database, query_type, table, duration, 'error')
                raise
        
        return wrapper
    return decorator

@contextmanager
def track_database_connections(metrics: PrometheusMetrics, database: str, pool: str):
    """Context manager to track database connections"""
    try:
        metrics.increment_counter("db_connections_active", {"database": database, "pool": pool})
        yield
    finally:
        metrics.increment_counter("db_connections_idle", {"database": database, "pool": pool})

# Global metrics instance
prometheus_metrics = PrometheusMetrics()

# Usage example
async def main():
    """Main execution function"""
    # Start monitoring
    prometheus_metrics.start_monitoring()
    
    # Record some example metrics
    prometheus_metrics.record_http_request('GET', '/api/v1/minerals', 200, 0.05, 100, 5000)
    prometheus_metrics.record_database_query('dedan', 'select', 'minerals', 0.02, 'success')
    prometheus_metrics.record_trading_order('gold', 'buy', 'filled', 10000.0, 0.5, 0.02)
    prometheus_metrics.record_blockchain_transaction('ethereum', 15.0, 'success', 20.5, 18500000, 12)
    prometheus_metrics.record_quantum_execution('settlement', 'ibm', 0.8, 0.95, 4, 15.5)
    prometheus_metrics.record_cache_operation('redis', 'get', 'hit', 0.85, 1024000)
    prometheus_metrics.record_error('trading', 'insufficient_balance', 'high', 'User has insufficient balance')
    
    # Get metrics export
    export = prometheus_metrics.get_metrics_export()
    print("Prometheus Metrics Export:")
    print(export[:1000] + "..." if len(export) > 1000 else export)
    
    # Get summary
    summary = prometheus_metrics.get_metrics_summary()
    print(f"\nMetrics Summary: {json.dumps(summary, indent=2, default=str)}")
    
    # Stop monitoring
    prometheus_metrics.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
