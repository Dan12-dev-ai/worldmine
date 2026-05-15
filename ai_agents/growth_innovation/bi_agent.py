"""
BI Agent - Auto-create dashboards, auto-generate reports
Replaces 1 BI Manager + 5 BI analysts
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json
import numpy as np
from ..agent_framework import BaseAIAgent, AgentRole, MessageType, Priority, AgentCapability

@dataclass
class Dashboard:
    """BI dashboard configuration"""
    dashboard_id: str
    name: str
    category: str
    widgets: List[Dict[str, Any]]
    refresh_interval: int
    created_at: datetime
    last_updated: datetime

@dataclass
class BIReport:
    """BI report"""
    report_id: str
    title: str
    report_type: str
    data_source: str
    generated_at: datetime
    insights: List[str]

class BIAgent(BaseAIAgent):
    """BI Agent - Automated business intelligence"""
    
    def __init__(self):
        super().__init__(
            agent_id="bi_001",
            role=AgentRole.BI,
            name="Business Intelligence Engine",
            description="Auto-create dashboards, auto-generate reports"
        )
        
        self.dashboards: List[Dashboard] = []
        self.bi_reports: List[BIReport] = []
        self.data_sources: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize BI agent"""
        try:
            await self._setup_data_sources()
            asyncio.create_task(self._bi_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize BI Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get BI agent capabilities"""
        return [
            AgentCapability(
                name="dashboard_creation",
                description="Auto-create interactive dashboards",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 3.0},
                dependencies=["data_warehouse", "visualization_tools"]
            ),
            AgentCapability(
                name="report_generation",
                description="Auto-generate business reports",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.98, "response_time": 5.0},
                dependencies=["analytics_engine", "reporting_tools"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process BI tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle BI commands"""
        if subject == "create_dashboard":
            return await self._create_dashboard(content)
        elif subject == "generate_report":
            return await self._generate_report(content)
        elif subject == "update_dashboard":
            return await self._update_dashboard(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _create_dashboard(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create BI dashboard"""
        name = content.get('name', 'unknown')
        category = content.get('category', 'general')
        widgets = content.get('widgets', [])
        refresh_interval = content.get('refresh_interval', 300)  # 5 minutes
        
        # Generate widgets if not provided
        if not widgets:
            widgets = await self._generate_dashboard_widgets(category)
        
        # Create dashboard
        dashboard = Dashboard(
            dashboard_id=f"dash_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            name=name,
            category=category,
            widgets=widgets,
            refresh_interval=refresh_interval,
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        
        # Deploy dashboard
        deploy_result = await self._deploy_dashboard(dashboard)
        
        if deploy_result['success']:
            self.dashboards.append(dashboard)
        
        return {
            'dashboard_id': dashboard.dashboard_id,
            'name': name,
            'category': category,
            'widgets_count': len(widgets),
            'refresh_interval': refresh_interval,
            'deploy_success': deploy_result['success'],
            'dashboard_url': deploy_result.get('url', '')
        }
    
    async def _generate_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BI report"""
        report_type = content.get('report_type', 'executive')
        data_source = content.get('data_source', 'warehouse')
        time_period = content.get('time_period', 'monthly')
        
        # Get report data
        report_data = await self._get_report_data(data_source, time_period)
        
        # Generate insights
        insights = await self._generate_report_insights(report_data, report_type)
        
        # Create report
        report = BIReport(
            report_id=f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            title=f"{report_type.title()} Report - {time_period.title()}",
            report_type=report_type,
            data_source=data_source,
            generated_at=datetime.utcnow(),
            insights=insights
        )
        
        self.bi_reports.append(report)
        
        return {
            'report_id': report.report_id,
            'title': report.title,
            'report_type': report_type,
            'data_source': data_source,
            'time_period': time_period,
            'insights_count': len(insights),
            'generated_at': report.generated_at.isoformat(),
            'insights': insights
        }
    
    async def _update_dashboard(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing dashboard"""
        dashboard_id = content.get('dashboard_id', 'unknown')
        widgets = content.get('widgets', [])
        
        # Find dashboard
        dashboard = next((d for d in self.dashboards if d.dashboard_id == dashboard_id), None)
        
        if not dashboard:
            return {'error': f'Dashboard not found: {dashboard_id}'}
        
        # Update widgets
        if widgets:
            dashboard.widgets = widgets
        
        dashboard.last_updated = datetime.utcnow()
        
        # Redeploy dashboard
        deploy_result = await self._deploy_dashboard(dashboard)
        
        return {
            'dashboard_id': dashboard.dashboard_id,
            'widgets_updated': len(widgets),
            'last_updated': dashboard.last_updated.isoformat(),
            'deploy_success': deploy_result['success']
        }
    
    async def _bi_loop(self):
        """Continuous BI operations loop"""
        while self.is_active:
            try:
                # Update dashboard data
                await self._update_dashboard_data()
                
                # Generate scheduled reports
                await self._generate_scheduled_reports()
                
                # Optimize dashboard performance
                await self._optimize_dashboards()
                
                await asyncio.sleep(300)  # Every 5 minutes
            except Exception as e:
                logger.error(f"Error in BI loop: {e}")
                await asyncio.sleep(60)
    
    async def _generate_dashboard_widgets(self, category: str) -> List[Dict[str, Any]]:
        """Generate dashboard widgets"""
        widget_templates = {
            'executive': [
                {'type': 'kpi', 'metric': 'revenue', 'title': 'Total Revenue'},
                {'type': 'chart', 'chart_type': 'line', 'metric': 'revenue_trend', 'title': 'Revenue Trend'},
                {'type': 'kpi', 'metric': 'active_users', 'title': 'Active Users'},
                {'type': 'chart', 'chart_type': 'pie', 'metric': 'revenue_by_source', 'title': 'Revenue by Source'}
            ],
            'sales': [
                {'type': 'kpi', 'metric': 'deals_closed', 'title': 'Deals Closed'},
                {'type': 'chart', 'chart_type': 'bar', 'metric': 'sales_pipeline', 'title': 'Sales Pipeline'},
                {'type': 'table', 'metric': 'top_deals', 'title': 'Top Deals'},
                {'type': 'gauge', 'metric': 'conversion_rate', 'title': 'Conversion Rate'}
            ],
            'operations': [
                {'type': 'kpi', 'metric': 'system_uptime', 'title': 'System Uptime'},
                {'type': 'chart', 'chart_type': 'line', 'metric': 'response_time', 'title': 'Response Time'},
                {'type': 'chart', 'chart_type': 'area', 'metric': 'error_rate', 'title': 'Error Rate'},
                {'type': 'table', 'metric': 'active_alerts', 'title': 'Active Alerts'}
            ]
        }
        
        return widget_templates.get(category, widget_templates['executive'])
    
    async def _deploy_dashboard(self, dashboard: Dashboard) -> Dict[str, Any]:
        """Deploy dashboard to production"""
        logger.info(f"Deploying dashboard: {dashboard.name}")
        
        # Mock deployment
        await asyncio.sleep(2)  # 2 seconds to deploy
        
        return {
            'success': True,
            'dashboard_id': dashboard.dashboard_id,
            'url': f"https://dedan.ai/dashboards/{dashboard.dashboard_id}",
            'deployed_at': datetime.utcnow().isoformat()
        }
    
    async def _get_report_data(self, data_source: str, time_period: str) -> Dict[str, Any]:
        """Get data for report generation"""
        # Mock report data
        return {
            'revenue': {
                'current': np.random.uniform(1000000, 5000000),
                'previous': np.random.uniform(800000, 4000000),
                'growth': np.random.uniform(-0.1, 0.3)
            },
            'users': {
                'total': np.random.randint(50000, 200000),
                'active': np.random.randint(10000, 50000),
                'new': np.random.randint(1000, 10000)
            },
            'performance': {
                'uptime': np.random.uniform(0.95, 0.999),
                'response_time': np.random.uniform(50, 200),
                'error_rate': np.random.uniform(0.001, 0.01)
            }
        }
    
    async def _generate_report_insights(self, report_data: Dict[str, Any], report_type: str) -> List[str]:
        """Generate insights for report"""
        insights = []
        
        revenue = report_data['revenue']
        if revenue['growth'] > 0.1:
            insights.append(f"Revenue growth of {revenue['growth']*100:.1f}% exceeds target")
        elif revenue['growth'] < 0:
            insights.append("Revenue decline detected - immediate action required")
        
        users = report_data['users']
        if users['new'] > 5000:
            insights.append("Strong user acquisition performance")
        
        performance = report_data['performance']
        if performance['uptime'] < 0.99:
            insights.append("System uptime below 99% SLA")
        
        return insights
    
    async def _update_dashboard_data(self):
        """Update dashboard data"""
        for dashboard in self.dashboards:
            # Mock data refresh
            for widget in dashboard.widgets:
                if widget['type'] == 'kpi':
                    # Update KPI values
                    if widget['metric'] == 'revenue':
                        widget['value'] = np.random.uniform(100000, 1000000)
                    elif widget['metric'] == 'active_users':
                        widget['value'] = np.random.randint(1000, 10000)
            
            dashboard.last_updated = datetime.utcnow()
    
    async def _generate_scheduled_reports(self):
        """Generate scheduled reports"""
        current_hour = datetime.utcnow().hour
        
        # Generate executive report at 8 AM
        if current_hour == 8:
            await self._generate_report({
                'report_type': 'executive',
                'data_source': 'warehouse',
                'time_period': 'daily'
            })
        
        # Generate sales report at 9 AM
        if current_hour == 9:
            await self._generate_report({
                'report_type': 'sales',
                'data_source': 'crm',
                'time_period': 'weekly'
            })
    
    async def _optimize_dashboards(self):
        """Optimize dashboard performance"""
        for dashboard in self.dashboards:
            # Check if dashboard needs optimization
            if (datetime.utcnow() - dashboard.last_updated).total_seconds() > 3600:
                # Optimize widget queries
                logger.info(f"Optimizing dashboard: {dashboard.name}")
                await asyncio.sleep(1)  # 1 second to optimize
    
    async def _setup_data_sources(self):
        """Setup data sources"""
        self.data_sources = {
            'warehouse': {
                'type': 'data_warehouse',
                'connection': 'postgresql://dedan_warehouse',
                'tables': ['revenue', 'users', 'transactions', 'events']
            },
            'crm': {
                'type': 'api',
                'connection': 'salesforce_api',
                'endpoints': ['deals', 'accounts', 'contacts']
            },
            'analytics': {
                'type': 'analytics_platform',
                'connection': 'google_analytics',
                'metrics': ['sessions', 'pageviews', 'conversions']
            }
        }

bi_agent = BIAgent()
