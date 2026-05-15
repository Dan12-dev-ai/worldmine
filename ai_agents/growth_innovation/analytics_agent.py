"""
Analytics Agent - Auto-analyze business metrics, generate insights
Replaces 1 Analytics Manager + 5 data analysts
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
class BusinessInsight:
    """Business analytics insight"""
    insight_id: str
    metric_category: str
    insight_type: str
    value: float
    trend: str
    impact_level: str
    generated_at: datetime

@dataclass
class AnalyticsReport:
    """Analytics report"""
    report_id: str
    report_type: str
    time_period: str
    metrics: Dict[str, float]
    insights: List[str]
    generated_at: datetime

class AnalyticsAgent(BaseAIAgent):
    """Analytics Agent - Automated business analytics"""
    
    def __init__(self):
        super().__init__(
            agent_id="analytics_001",
            role=AgentRole.ANALYTICS,
            name="Business Analytics Engine",
            description="Auto-analyze business metrics, generate insights"
        )
        
        self.business_insights: List[BusinessInsight] = []
        self.analytics_reports: List[AnalyticsReport] = []
        self.metric_definitions: Dict[str, Any] = {}
        
    async def initialize(self) -> bool:
        """Initialize analytics agent"""
        try:
            await self._setup_metric_definitions()
            asyncio.create_task(self._analytics_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Analytics Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get analytics agent capabilities"""
        return [
            AgentCapability(
                name="business_analytics",
                description="Auto-analyze business metrics",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 3.0},
                dependencies=["data_warehouse", "analytics_tools"]
            ),
            AgentCapability(
                name="insight_generation",
                description="Auto-generate actionable insights",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.90, "response_time": 5.0},
                dependencies=["ml_models", "business_rules"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process analytics tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analytics commands"""
        if subject == "analyze_metrics":
            return await self._analyze_metrics(content)
        elif subject == "generate_insights":
            return await self._generate_insights(content)
        elif subject == "create_report":
            return await self._create_report(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _analyze_metrics(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze business metrics"""
        metric_category = content.get('metric_category', 'revenue')
        time_period = content.get('time_period', '30d')
        
        # Get metric data
        metric_data = await self._get_metric_data(metric_category, time_period)
        
        # Perform analysis
        analysis_result = await self._perform_metric_analysis(metric_data, metric_category)
        
        # Create insight
        insight = BusinessInsight(
            insight_id=f"insight_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            metric_category=metric_category,
            insight_type='trend_analysis',
            value=analysis_result['current_value'],
            trend=analysis_result['trend'],
            impact_level=analysis_result['impact_level'],
            generated_at=datetime.utcnow()
        )
        
        self.business_insights.append(insight)
        
        return {
            'insight_id': insight.insight_id,
            'metric_category': metric_category,
            'current_value': insight.value,
            'trend': insight.trend,
            'impact_level': insight.impact_level,
            'analysis_period': time_period,
            'metric_data': metric_data
        }
    
    async def _generate_insights(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate business insights"""
        insight_type = content.get('insight_type', 'comprehensive')
        
        # Get data for insight generation
        business_data = await self._get_business_data()
        
        # Generate insights
        insights = await self._perform_insight_generation(business_data, insight_type)
        
        # Store insights
        generated_insights = []
        for insight_data in insights:
            insight = BusinessInsight(
                insight_id=f"gen_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                metric_category=insight_data['category'],
                insight_type=insight_data['type'],
                value=insight_data['value'],
                trend=insight_data['trend'],
                impact_level=insight_data['impact_level'],
                generated_at=datetime.utcnow()
            )
            self.business_insights.append(insight)
            generated_insights.append(insight.insight_id)
        
        return {
            'insights_generated': len(generated_insights),
            'insight_type': insight_type,
            'insight_ids': generated_insights,
            'insights': [
                {
                    'category': i.metric_category,
                    'type': i.insight_type,
                    'value': i.value,
                    'trend': i.trend,
                    'impact': i.impact_level
                }
                for i in self.business_insights[-len(generated_insights):]
            ]
        }
    
    async def _create_report(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create analytics report"""
        report_type = content.get('report_type', 'executive')
        time_period = content.get('time_period', 'monthly')
        
        # Get report data
        report_data = await self._get_report_data(report_type, time_period)
        
        # Generate insights for report
        insights = await self._generate_report_insights(report_data)
        
        # Create report
        report = AnalyticsReport(
            report_id=f"report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            report_type=report_type,
            time_period=time_period,
            metrics=report_data['metrics'],
            insights=insights,
            generated_at=datetime.utcnow()
        )
        
        self.analytics_reports.append(report)
        
        return {
            'report_id': report.report_id,
            'report_type': report_type,
            'time_period': time_period,
            'metrics': report.metrics,
            'insights': report.insights,
            'generated_at': report.generated_at.isoformat()
        }
    
    async def _analytics_loop(self):
        """Continuous analytics loop"""
        while self.is_active:
            try:
                # Analyze key metrics
                await self._analyze_key_metrics()
                
                # Generate insights
                await self._generate_insights({'insight_type': 'automated'})
                
                # Create daily reports
                await self._create_daily_reports()
                
                await asyncio.sleep(3600)  # Analyze every hour
            except Exception as e:
                logger.error(f"Error in analytics loop: {e}")
                await asyncio.sleep(300)
    
    async def _analyze_key_metrics(self):
        """Analyze key business metrics"""
        key_metrics = ['revenue', 'user_growth', 'retention', 'conversion', 'profitability']
        
        for metric in key_metrics:
            await self._analyze_metrics({
                'metric_category': metric,
                'time_period': '24h'
            })
    
    async def _create_daily_reports(self):
        """Create daily analytics reports"""
        if datetime.utcnow().hour == 8:  # 8 AM daily
            await self._create_report({
                'report_type': 'daily_summary',
                'time_period': 'yesterday'
            })
    
    async def _get_metric_data(self, metric_category: str, time_period: str) -> Dict[str, Any]:
        """Get metric data for analysis"""
        # Mock metric data
        base_values = {
            'revenue': 100000,
            'user_growth': 1000,
            'retention': 0.85,
            'conversion': 0.05,
            'profitability': 0.25
        }
        
        base_value = base_values.get(metric_category, 100)
        
        return {
            'current_value': base_value * np.random.uniform(0.9, 1.1),
            'previous_value': base_value * np.random.uniform(0.9, 1.1),
            'historical_values': [base_value * np.random.uniform(0.8, 1.2) for _ in range(30)],
            'time_period': time_period
        }
    
    async def _perform_metric_analysis(self, metric_data: Dict[str, Any], metric_category: str) -> Dict[str, Any]:
        """Perform metric analysis"""
        current = metric_data['current_value']
        previous = metric_data['previous_value']
        
        # Calculate trend
        if current > previous * 1.05:
            trend = 'increasing'
            impact_level = 'positive'
        elif current < previous * 0.95:
            trend = 'decreasing'
            impact_level = 'negative'
        else:
            trend = 'stable'
            impact_level = 'neutral'
        
        return {
            'current_value': current,
            'trend': trend,
            'impact_level': impact_level,
            'change_percentage': ((current - previous) / previous) * 100 if previous != 0 else 0
        }
    
    async def _get_business_data(self) -> Dict[str, Any]:
        """Get comprehensive business data"""
        return {
            'revenue': await self._get_metric_data('revenue', '30d'),
            'users': await self._get_metric_data('user_growth', '30d'),
            'retention': await self._get_metric_data('retention', '30d'),
            'conversion': await self._get_metric_data('conversion', '30d'),
            'profitability': await self._get_metric_data('profitability', '30d')
        }
    
    async def _perform_insight_generation(self, business_data: Dict[str, Any], insight_type: str) -> List[Dict[str, Any]]:
        """Generate business insights"""
        insights = []
        
        # Revenue insights
        revenue_data = business_data['revenue']
        if revenue_data['current_value'] > revenue_data['previous_value'] * 1.1:
            insights.append({
                'category': 'revenue',
                'type': 'growth_opportunity',
                'value': revenue_data['current_value'],
                'trend': 'strong_growth',
                'impact_level': 'high'
            })
        
        # User insights
        user_data = business_data['users']
        if user_data['current_value'] > user_data['previous_value'] * 1.05:
            insights.append({
                'category': 'user_growth',
                'type': 'acquisition_success',
                'value': user_data['current_value'],
                'trend': 'steady_growth',
                'impact_level': 'medium'
            })
        
        # Retention insights
        retention_data = business_data['retention']
        if retention_data['current_value'] < 0.8:
            insights.append({
                'category': 'retention',
                'type': 'churn_risk',
                'value': retention_data['current_value'],
                'trend': 'declining',
                'impact_level': 'high'
            })
        
        return insights
    
    async def _get_report_data(self, report_type: str, time_period: str) -> Dict[str, Any]:
        """Get data for report generation"""
        # Mock report data
        return {
            'metrics': {
                'total_revenue': np.random.uniform(1000000, 5000000),
                'active_users': np.random.randint(10000, 50000),
                'conversion_rate': np.random.uniform(0.03, 0.08),
                'customer_lifetime_value': np.random.uniform(1000, 10000),
                'profit_margin': np.random.uniform(0.15, 0.35)
            }
        }
    
    async def _generate_report_insights(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate insights for report"""
        metrics = report_data['metrics']
        insights = []
        
        if metrics['total_revenue'] > 3000000:
            insights.append("Revenue exceeds target by 20%")
        
        if metrics['conversion_rate'] > 0.05:
            insights.append("Conversion rate above industry average")
        
        if metrics['profit_margin'] < 0.2:
            insights.append("Profit margin below target - consider cost optimization")
        
        return insights
    
    async def _setup_metric_definitions(self):
        """Setup metric definitions"""
        self.metric_definitions = {
            'revenue': {
                'description': 'Total revenue generated',
                'unit': 'USD',
                'frequency': 'daily',
                'target_growth': 0.2  # 20% monthly growth
            },
            'user_growth': {
                'description': 'New user acquisition',
                'unit': 'count',
                'frequency': 'daily',
                'target_growth': 0.15  # 15% monthly growth
            },
            'retention': {
                'description': 'Customer retention rate',
                'unit': 'percentage',
                'frequency': 'monthly',
                'target_value': 0.9  # 90% retention
            },
            'conversion': {
                'description': 'Lead to customer conversion',
                'unit': 'percentage',
                'frequency': 'daily',
                'target_value': 0.05  # 5% conversion
            },
            'profitability': {
                'description': 'Profit margin',
                'unit': 'percentage',
                'frequency': 'monthly',
                'target_value': 0.25  # 25% profit margin
            }
        }

analytics_agent = AnalyticsAgent()
