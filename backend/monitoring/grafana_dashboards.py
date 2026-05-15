"""
Grafana Dashboards for DEDAN 2.0
Complete monitoring dashboards with 15+ panels
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class DashboardConfig:
    """Dashboard configuration"""
    title: str
    uid: str
    tags: List[str]
    timezone: str
    panels: List[Dict[str, Any]]
    time_from: str
    time_to: str
    refresh: str

class GrafanaDashboardBuilder:
    """Builds comprehensive Grafana dashboards"""
    
    def __init__(self):
        self.dashboards = []
        self.panel_id_counter = 1
    
    def create_main_dashboard(self) -> DashboardConfig:
        """Create main overview dashboard"""
        panels = []
        
        # System Overview Panel
        panels.append(self._create_system_overview_panel())
        
        # Application Health Panel
        panels.append(self._create_app_health_panel())
        
        # Trading Metrics Panel
        panels.append(self._create_trading_metrics_panel())
        
        # Database Performance Panel
        panels.append(self._create_database_panel())
        
        # Blockchain Metrics Panel
        panels.append(self._create_blockchain_panel())
        
        # Quantum Metrics Panel
        panels.append(self._create_quantum_panel())
        
        # Network Traffic Panel
        panels.append(self._create_network_panel())
        
        # Alert Status Panel
        panels.append(self._create_alerts_panel())
        
        return DashboardConfig(
            title="DEDAN 2.0 - Main Dashboard",
            uid="dedan-main",
            tags=["dedan", "main", "overview"],
            timezone="browser",
            panels=panels,
            time_from="now-1h",
            time_to="now",
            refresh="30s"
        )
    
    def create_trading_dashboard(self) -> DashboardConfig:
        """Create trading-specific dashboard"""
        panels = []
        
        # Real-time Price Chart
        panels.append(self._create_price_chart_panel())
        
        # Order Book Depth
        panels.append(self._create_orderbook_panel())
        
        # Trading Volume
        panels.append(self._create_volume_panel())
        
        # Settlement Performance
        panels.append(self._create_settlement_panel())
        
        # Slippage Analysis
        panels.append(self._create_slippage_panel())
        
        # Market Liquidity
        panels.append(self._create_liquidity_panel())
        
        return DashboardConfig(
            title="DEDAN 2.0 - Trading Dashboard",
            uid="dedan-trading",
            tags=["dedan", "trading", "market"],
            timezone="browser",
            panels=panels,
            time_from="now-6h",
            time_to="now",
            refresh="5s"
        )
    
    def create_performance_dashboard(self) -> DashboardConfig:
        """Create performance monitoring dashboard"""
        panels = []
        
        # Response Time Distribution
        panels.append(self._create_response_time_panel())
        
        # Throughput Metrics
        panels.append(self._create_throughput_panel())
        
        # Error Rate Analysis
        panels.append(self._create_error_rate_panel())
        
        # Cache Performance
        panels.append(self._create_cache_performance_panel())
        
        # Resource Utilization
        panels.append(self._create_resource_panel())
        
        # Performance Trends
        panels.append(self._create_performance_trends_panel())
        
        return DashboardConfig(
            title="DEDAN 2.0 - Performance Dashboard",
            uid="dedan-performance",
            tags=["dedan", "performance", "metrics"],
            timezone="browser",
            panels=panels,
            time_from="now-24h",
            time_to="now",
            refresh="10s"
        )
    
    def create_blockchain_dashboard(self) -> DashboardConfig:
        """Create blockchain monitoring dashboard"""
        panels = []
        
        # Transaction Throughput
        panels.append(self._create_blockchain_throughput_panel())
        
        # Gas Price Analysis
        panels.append(self._create_gas_price_panel())
        
        # Block Confirmation Time
        panels.append(self._create_block_time_panel())
        
        # Smart Contract Calls
        panels.append(self._create_contract_calls_panel())
        
        # Network Health
        panels.append(self._create_network_health_panel())
        
        return DashboardConfig(
            title="DEDAN 2.0 - Blockchain Dashboard",
            uid="dedan-blockchain",
            tags=["dedan", "blockchain", "web3"],
            timezone="browser",
            panels=panels,
            time_from="now-12h",
            time_to="now",
            refresh="15s"
        )
    
    def create_quantum_dashboard(self) -> DashboardConfig:
        """Create quantum computing dashboard"""
        panels = []
        
        # Circuit Execution Time
        panels.append(self._create_quantum_execution_panel())
        
        # Fidelity Metrics
        panels.append(self._create_fidelity_panel())
        
        # Quantum Advantage
        panels.append(self._create_quantum_advantage_panel())
        
        # Qubit Utilization
        panels.append(self._create_qubit_utilization_panel())
        
        # Quantum State Visualization
        panels.append(self._create_quantum_state_panel())
        
        return DashboardConfig(
            title="DEDAN 2.0 - Quantum Dashboard",
            uid="dedan-quantum",
            tags=["dedan", "quantum", "computing"],
            timezone="browser",
            panels=panels,
            time_from="now-6h",
            time_to="now",
            refresh="20s"
        )
    
    def _create_system_overview_panel(self) -> Dict[str, Any]:
        """Create system overview panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "System Overview",
            "type": "stat",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "system_cpu_usage_percent",
                    "legendFormat": "CPU: {{value}}%",
                    "refId": "A"
                },
                {
                    "expr": "system_memory_usage_bytes{type=\"used\"} / system_memory_usage_bytes{type=\"total\"} * 100",
                    "legendFormat": "Memory: {{value}}%",
                    "refId": "B"
                },
                {
                    "expr": "system_disk_usage_bytes{device=\"/\",type=\"used\"} / system_disk_usage_bytes{device=\"/\",type=\"total\"} * 100",
                    "legendFormat": "Disk: {{value}}%",
                    "refId": "C"
                },
                {
                    "expr": "app_uptime_seconds",
                    "legendFormat": "Uptime: {{value}}s",
                    "refId": "D"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {"displayMode": "list", "orientation": "horizontal"},
                    "mappings": [],
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "red", "value": 80}
                        ]
                    },
                    "unit": "short"
                }
            },
            "options": {
                "colorMode": "value",
                "graphMode": "area",
                "justifyMode": "auto",
                "orientation": "auto",
                "reduceOptions": {
                    "values": false,
                    "calcs": ["lastNotNull"],
                    "fields": ""
                },
                "textMode": "auto"
            }
        }
    
    def _create_app_health_panel(self) -> Dict[str, Any]:
        """Create application health panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Application Health",
            "type": "stat",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
            "targets": [
                {
                    "expr": "rate(http_requests_total[5m])",
                    "legendFormat": "RPS: {{value}}",
                    "refId": "A"
                },
                {
                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
                    "legendFormat": "P95: {{value}}s",
                    "refId": "B"
                },
                {
                    "expr": "rate(app_errors_total[5m]) / rate(http_requests_total[5m]) * 100",
                    "legendFormat": "Error Rate: {{value}}%",
                    "refId": "C"
                },
                {
                    "expr": "business_users_active{period=\"1m\"}",
                    "legendFormat": "Active Users: {{value}}",
                    "refId": "D"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "custom": {"displayMode": "list", "orientation": "horizontal"},
                    "mappings": [],
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 50},
                            {"color": "red", "value": 80}
                        ]
                    }
                }
            }
        }
    
    def _create_trading_metrics_panel(self) -> Dict[str, Any]:
        """Create trading metrics panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Trading Metrics",
            "type": "stat",
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8},
            "targets": [
                {
                    "expr": "trading_volume_usd{period=\"1h\"}",
                    "legendFormat": "Volume (1h): ${{value}}",
                    "refId": "A"
                },
                {
                    "expr": "trading_orders_total{status=\"filled\"} - trading_orders_total{status=\"filled\"} offset 1h",
                    "legendFormat": "Orders (1h): {{value}}",
                    "refId": "B"
                },
                {
                    "expr": "business_trading_volume_usd{period=\"1d\"}",
                    "legendFormat": "Volume (24h): ${{value}}",
                    "refId": "C"
                },
                {
                    "expr": "business_fees_collected_usd{period=\"1h\"}",
                    "legendFormat": "Fees (1h): ${{value}}",
                    "refId": "D"
                },
                {
                    "expr": "trading_price_usd{mineral=\"gold\"}",
                    "legendFormat": "Gold: ${{value}}",
                    "refId": "E"
                },
                {
                    "expr": "trading_price_usd{mineral=\"silver\"}",
                    "legendFormat": "Silver: ${{value}}",
                    "refId": "F"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "continuous-GrYlRd"},
                    "custom": {"displayMode": "list", "orientation": "horizontal"},
                    "mappings": [],
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None}
                        ]
                    },
                    "unit": "short"
                }
            }
        }
    
    def _create_database_panel(self) -> Dict[str, Any]:
        """Create database performance panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Database Performance",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 16},
            "targets": [
                {
                    "expr": "db_connections_active{database=\"dedan\",pool=\"main\"}",
                    "legendFormat": "Active Connections",
                    "refId": "A"
                },
                {
                    "expr": "rate(db_queries_total{database=\"dedan\",query_type=\"select\"}[5m])",
                    "legendFormat": "Select QPS",
                    "refId": "B"
                },
                {
                    "expr": "histogram_quantile(0.95, rate(db_query_duration_seconds_bucket{database=\"dedan\"}[5m]))",
                    "legendFormat": "P95 Query Time",
                    "refId": "C"
                },
                {
                    "expr": "rate(db_transactions_total{database=\"dedan\",status=\"committed\"}[5m])",
                    "legendFormat": "Transactions/sec",
                    "refId": "D"
                }
            ],
            "yAxes": [
                {
                    "label": "Count",
                    "show": True,
                    "min": 0
                }
            ],
            "xAxes": [
                {
                    "show": True,
                    "mode": "time"
                }
            ]
        }
    
    def _create_blockchain_panel(self) -> Dict[str, Any]:
        """Create blockchain metrics panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Blockchain Metrics",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 16},
            "targets": [
                {
                    "expr": "blockchain_transactions_total{blockchain=\"ethereum\",status=\"success\"}",
                    "legendFormat": "Transactions",
                    "refId": "A"
                },
                {
                    "expr": "blockchain_gas_price_gwei{blockchain=\"ethereum\"}",
                    "legendFormat": "Gas Price (Gwei)",
                    "refId": "B"
                },
                {
                    "expr": "histogram_quantile(0.95, rate(blockchain_transaction_duration_seconds_bucket{blockchain=\"ethereum\"}[5m]))",
                    "legendFormat": "P95 Confirmation Time",
                    "refId": "C"
                },
                {
                    "expr": "blockchain_block_number{blockchain=\"ethereum\"}",
                    "legendFormat": "Block Number",
                    "refId": "D"
                }
            ],
            "yAxes": [
                {
                    "label": "Value",
                    "show": True
                }
            ]
        }
    
    def _create_quantum_panel(self) -> Dict[str, Any]:
        """Create quantum metrics panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Quantum Metrics",
            "type": "graph",
            "gridPos": {"h": 8, "w": 24, "x": 0, "y": 24},
            "targets": [
                {
                    "expr": "rate(quantum_circuits_executed_total{circuit_type=\"settlement\"}[5m])",
                    "legendFormat": "Settlement Circuits/min",
                    "refId": "A"
                },
                {
                    "expr": "quantum_fidelity{circuit_type=\"settlement\"}",
                    "legendFormat": "Fidelity",
                    "refId": "B"
                },
                {
                    "expr": "histogram_quantile(0.95, rate(quantum_circuit_duration_ms_bucket{circuit_type=\"settlement\"}[5m]))",
                    "legendFormat": "P95 Execution Time (ms)",
                    "refId": "C"
                },
                {
                    "expr": "quantum_qubits_used{circuit_type=\"settlement\"}",
                    "legendFormat": "Qubits Used",
                    "refId": "D"
                },
                {
                    "expr": "quantum_advantage_percent{algorithm=\"settlement\"}",
                    "legendFormat": "Quantum Advantage %",
                    "refId": "E"
                }
            ],
            "yAxes": [
                {
                    "label": "Value",
                    "show": True
                }
            ]
        }
    
    def _create_network_panel(self) -> Dict[str, Any]:
        """Create network traffic panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Network Traffic",
            "type": "graph",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 32},
            "targets": [
                {
                    "expr": "rate(system_network_bytes_total{interface=\"all\",direction=\"sent\"}[5m])",
                    "legendFormat": "Bytes Out/sec",
                    "refId": "A"
                },
                {
                    "expr": "rate(system_network_bytes_total{interface=\"all\",direction=\"recv\"}[5m])",
                    "legendFormat": "Bytes In/sec",
                    "refId": "B"
                }
            ],
            "yAxes": [
                {
                    "label": "Bytes/sec",
                    "show": True
                }
            ]
        }
    
    def _create_alerts_panel(self) -> Dict[str, Any]:
        """Create alerts status panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Alert Status",
            "type": "table",
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 32},
            "targets": [
                {
                    "expr": "ALERTS_FOR_STATE{alertstate=\"firing\"}",
                    "legendFormat": "{{alertname}} - {{summary}}",
                    "refId": "A",
                    "format": "table"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "thresholds"},
                    "thresholds": {
                        "steps": [
                            {"color": "green", "value": None},
                            {"color": "yellow", "value": 1},
                            {"color": "red", "value": 2}
                        ]
                    }
                }
            }
        }
    
    def _create_price_chart_panel(self) -> Dict[str, Any]:
        """Create price chart panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Real-time Price Chart",
            "type": "timeseries",
            "gridPos": {"h": 9, "w": 24, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "trading_price_usd{mineral=\"gold\"}",
                    "legendFormat": "Gold",
                    "refId": "A"
                },
                {
                    "expr": "trading_price_usd{mineral=\"silver\"}",
                    "legendFormat": "Silver",
                    "refId": "B"
                },
                {
                    "expr": "trading_price_usd{mineral=\"copper\"}",
                    "legendFormat": "Copper",
                    "refId": "C"
                }
            ],
            "fieldConfig": {
                "defaults": {
                    "color": {"mode": "palette-classic"},
                    "custom": {"lineStyle": {"fill": "solid"}},
                    "unit": "currencyUSD"
                }
            }
        }
    
    def _create_response_time_panel(self) -> Dict[str, Any]:
        """Create response time panel"""
        return {
            "id": self._get_next_panel_id(),
            "title": "Response Time Distribution",
            "type": "heatmap",
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
            "targets": [
                {
                    "expr": "rate(http_request_duration_seconds_bucket[5m])",
                    "legendFormat": "{{le}}",
                    "refId": "A"
                }
            ]
        }
    
    def _get_next_panel_id(self) -> int:
        """Get next panel ID"""
        panel_id = self.panel_id_counter
        self.panel_id_counter += 1
        return panel_id
    
    def generate_all_dashboards(self) -> List[DashboardConfig]:
        """Generate all dashboards"""
        return [
            self.create_main_dashboard(),
            self.create_trading_dashboard(),
            self.create_performance_dashboard(),
            self.create_blockchain_dashboard(),
            self.create_quantum_dashboard()
        ]
    
    def export_dashboards(self, output_dir: str = "/home/kali/mini_business/monitoring/grafana"):
        """Export dashboards to JSON files"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        
        dashboards = self.generate_all_dashboards()
        
        for dashboard in dashboards:
            filename = f"{dashboard.uid}.json"
            filepath = os.path.join(output_dir, filename)
            
            dashboard_json = {
                "dashboard": {
                    "id": None,
                    "title": dashboard.title,
                    "tags": dashboard.tags,
                    "timezone": dashboard.timezone,
                    "panels": dashboard.panels,
                    "time": {
                        "from": dashboard.time_from,
                        "to": dashboard.time_to
                    },
                    "refresh": dashboard.refresh
                },
                "overwrite": True
            }
            
            with open(filepath, 'w') as f:
                json.dump(dashboard_json, f, indent=2)
            
            logger.info(f"Exported dashboard: {filepath}")
    
    def create_alert_rules(self) -> List[Dict[str, Any]]:
        """Create alert rules"""
        return [
            {
                "name": "High Error Rate",
                "condition": "rate(app_errors_total[5m]) / rate(http_requests_total[5m]) > 0.05",
                "for": "2m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "Error rate is above 5%",
                    "description": "Error rate has been above 5% for more than 2 minutes"
                }
            },
            {
                "name": "High Response Time",
                "condition": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1",
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "P95 response time is above 1 second",
                    "description": "95th percentile response time has been above 1 second for more than 5 minutes"
                }
            },
            {
                "name": "Database Connection Pool Exhaustion",
                "condition": "db_connections_active{database=\"dedan\",pool=\"main\"} / 20 > 0.8",
                "for": "1m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "Database connection pool is 80% full",
                    "description": "Database connection pool utilization is above 80%"
                }
            },
            {
                "name": "Blockchain Transaction Failure",
                "condition": "rate(blockchain_transactions_total{blockchain=\"ethereum\",status=\"error\"}[5m]) > 0.1",
                "for": "3m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "Blockchain transaction failure rate is high",
                    "description": "More than 10% of blockchain transactions are failing"
                }
            },
            {
                "name": "Quantum Circuit Failure",
                "condition": "rate(quantum_circuits_executed_total{status=\"error\"}[5m]) > 0.05",
                "for": "2m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "Quantum circuit failure rate is high",
                    "description": "More than 5% of quantum circuits are failing"
                }
            },
            {
                "name": "Low Cache Hit Rate",
                "condition": "cache_hit_ratio{cache=\"redis\"} < 0.8",
                "for": "5m",
                "labels": {"severity": "warning"},
                "annotations": {
                    "summary": "Cache hit rate is below 80%",
                    "description": "Redis cache hit rate has dropped below 80%"
                }
            },
            {
                "name": "High CPU Usage",
                "condition": "avg(system_cpu_usage_percent[5m]) > 80",
                "for": "3m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "CPU usage is above 80%",
                    "description": "Average CPU usage has been above 80% for more than 3 minutes"
                }
            },
            {
                "name": "High Memory Usage",
                "condition": "system_memory_usage_bytes{type=\"used\"} / system_memory_usage_bytes{type=\"total\"} > 0.85",
                "for": "5m",
                "labels": {"severity": "critical"},
                "annotations": {
                    "summary": "Memory usage is above 85%",
                    "description": "Memory utilization has been above 85% for more than 5 minutes"
                }
            }
        ]

# Main execution
def main():
    """Main execution function"""
    builder = GrafanaDashboardBuilder()
    
    # Export dashboards
    builder.export_dashboards()
    
    # Create alert rules
    alert_rules = builder.create_alert_rules()
    
    # Export alert rules
    alerts_file = "/home/kali/mini_business/monitoring/grafana/alerts.json"
    with open(alerts_file, 'w') as f:
        json.dump(alert_rules, f, indent=2)
    
    logger.info(f"Exported {len(alert_rules)} alert rules to {alerts_file}")
    logger.info("Grafana dashboards and alerts exported successfully!")

if __name__ == "__main__":
    main()
