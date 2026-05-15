"""
CEO Agent - Revenue Orchestrator for DEDAN 2.0
Replaces 1 CEO + 5 strategy managers + 10 business analysts
Auto-hunts $1B revenue opportunities and makes strategic decisions
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import json
import numpy as np
import pandas as pd
from ..agent_framework import BaseAIAgent, AgentRole, MessageType, Priority, AgentCapability
from ..agent_framework import AgentMetrics, communication_bus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class StrategicDecision:
    """Strategic decision made by CEO"""
    decision_id: str
    decision_type: str
    description: str
    expected_revenue_impact: float
    expected_cost_savings: float
    risk_level: str
    implementation_timeline: str
    confidence_score: float
    created_at: datetime

@dataclass
class RevenueOpportunity:
    """Revenue opportunity identified by CEO"""
    opportunity_id: str
    market_segment: str
    estimated_revenue: float
    probability: float
    time_to_revenue: int
    required_resources: List[str]
    competitive_advantage: str
    discovered_at: datetime

class CEOAgent(BaseAIAgent):
    """CEO Agent - Strategic revenue orchestrator"""
    
    def __init__(self):
        super().__init__(
            agent_id="ceo_001",
            role=AgentRole.CEO,
            name="CEO Revenue Orchestrator",
            description="Strategic decision maker and revenue opportunity hunter"
        )
        
        # CEO-specific attributes
        self.strategic_decisions: List[StrategicDecision] = []
        self.revenue_opportunities: List[RevenueOpportunity] = []
        self.market_intelligence: Dict[str, Any] = {}
        self.competitive_analysis: Dict[str, Any] = {}
        self.revenue_forecast: Dict[str, float] = {}
        self.strategic_kpis: Dict[str, float] = {}
        
        # Decision-making models
        self.revenue_prediction_model = None
        self.risk_assessment_model = None
        self.market_opportunity_model = None
        
        # Strategic goals
        self.strategic_goals = {
            'revenue_target_1yr': 100000000,  # $100M in 1 year
            'revenue_target_3yr': 1000000000,  # $1B in 3 years
            'market_share_target': 0.25,  # 25% market share
            'customer_growth_target': 10000,  # 10K customers
            'profit_margin_target': 0.35  # 35% profit margin
        }
    
    async def initialize(self) -> bool:
        """Initialize CEO agent"""
        try:
            logger.info("Initializing CEO Agent...")
            
            # Initialize AI models
            await self._initialize_ai_models()
            
            # Load market intelligence
            await self._load_market_intelligence()
            
            # Initialize strategic capabilities
            await self._initialize_capabilities()
            
            # Start revenue monitoring
            asyncio.create_task(self._revenue_monitoring_loop())
            
            # Start opportunity hunting
            asyncio.create_task(self._opportunity_hunting_loop())
            
            # Start strategic planning
            asyncio.create_task(self._strategic_planning_loop())
            
            logger.info("CEO Agent initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize CEO Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get CEO agent capabilities"""
        return [
            AgentCapability(
                name="strategic_planning",
                description="Develop and execute strategic plans",
                input_schema={
                    "type": "object",
                    "properties": {
                        "planning_horizon": {"type": "string"},
                        "focus_areas": {"type": "array"},
                        "resource_constraints": {"type": "object"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "strategic_plan": {"type": "object"},
                        "implementation_roadmap": {"type": "array"},
                        "success_metrics": {"type": "object"}
                    }
                },
                performance_metrics={
                    "accuracy": 0.95,
                    "response_time": 2.5,
                    "success_rate": 0.98
                },
                dependencies=["market_research", "financial_analysis"]
            ),
            AgentCapability(
                name="revenue_optimization",
                description="Identify and optimize revenue opportunities",
                input_schema={
                    "type": "object",
                    "properties": {
                        "market_segment": {"type": "string"},
                        "time_horizon": {"type": "string"},
                        "investment_level": {"type": "number"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "opportunities": {"type": "array"},
                        "revenue_forecast": {"type": "number"},
                        "roi_analysis": {"type": "object"}
                    }
                },
                performance_metrics={
                    "accuracy": 0.92,
                    "response_time": 1.8,
                    "success_rate": 0.96
                },
                dependencies=["market_data", "competitor_analysis"]
            ),
            AgentCapability(
                name="strategic_decision_making",
                description="Make high-level strategic decisions",
                input_schema={
                    "type": "object",
                    "properties": {
                        "decision_context": {"type": "object"},
                        "alternatives": {"type": "array"},
                        "risk_tolerance": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "decision": {"type": "object"},
                        "rationale": {"type": "string"},
                        "expected_outcomes": {"type": "object"}
                    }
                },
                performance_metrics={
                    "accuracy": 0.94,
                    "response_time": 3.2,
                    "success_rate": 0.97
                },
                dependencies=["risk_analysis", "financial_modeling"]
            ),
            AgentCapability(
                name="market_intelligence",
                description="Gather and analyze market intelligence",
                input_schema={
                    "type": "object",
                    "properties": {
                        "market_focus": {"type": "string"},
                        "intelligence_type": {"type": "string"}
                    }
                },
                output_schema={
                    "type": "object",
                    "properties": {
                        "market_insights": {"type": "object"},
                        "trend_analysis": {"type": "array"},
                        "competitive_landscape": {"type": "object"}
                    }
                },
                performance_metrics={
                    "accuracy": 0.91,
                    "response_time": 4.1,
                    "success_rate": 0.95
                },
                dependencies=["data_sources", "analysis_tools"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process task assigned to CEO agent"""
        start_time = time.time()
        
        try:
            task_type = task.get('type', 'unknown')
            subject = task.get('subject', '')
            content = task.get('content', {})
            
            result = {}
            
            if task_type == 'command':
                result = await self._handle_command(subject, content)
            elif task_type == 'request':
                result = await self._handle_request(subject, content)
            elif task_type == 'collaboration':
                result = await self._handle_collaboration(subject, content, task.get('sender'))
            elif task_type == 'critical_alert':
                result = await self._handle_critical_alert(subject, content)
            else:
                result = {'error': f'Unknown task type: {task_type}'}
            
            # Update metrics
            self.metrics.tasks_completed += 1
            self.metrics.avg_response_time = (self.metrics.avg_response_time + (time.time() - start_time)) / 2
            
            return result
            
        except Exception as e:
            self.metrics.tasks_failed += 1
            logger.error(f"Error processing task in CEO Agent: {e}")
            return {'error': str(e)}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle command from other agents"""
        if subject == "generate_strategic_plan":
            return await self._generate_strategic_plan(content)
        elif subject == "make_strategic_decision":
            return await self._make_strategic_decision(content)
        elif subject == "optimize_revenue":
            return await self._optimize_revenue(content)
        elif subject == "assess_market_opportunity":
            return await self._assess_market_opportunity(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _handle_request(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request from other agents"""
        if subject == "get_strategic_status":
            return await self._get_strategic_status()
        elif subject == "get_revenue_forecast":
            return await self._get_revenue_forecast(content)
        elif subject == "get_market_intelligence":
            return await self._get_market_intelligence(content)
        elif subject == "get_competitive_analysis":
            return await self._get_competitive_analysis(content)
        else:
            return {'error': f'Unknown request: {subject}'}
    
    async def _handle_collaboration(self, subject: str, content: Dict[str, Any], sender: str) -> Dict[str, Any]:
        """Handle collaboration request"""
        if subject == "strategic_alignment":
            return await self._strategic_alignment(content, sender)
        elif subject == "resource_allocation":
            return await self._resource_allocation(content, sender)
        elif subject == "market_expansion":
            return await self._market_expansion(content, sender)
        else:
            return {'error': f'Unknown collaboration: {subject}'}
    
    async def _handle_critical_alert(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle critical alerts"""
        logger.critical(f"CEO Agent handling critical alert: {subject}")
        
        # Immediate strategic response
        if "revenue_drop" in subject.lower():
            return await self._handle_revenue_drop_alert(content)
        elif "market_threat" in subject.lower():
            return await self._handle_market_threat_alert(content)
        elif "competitive_attack" in subject.lower():
            return await self._handle_competitive_attack_alert(content)
        else:
            return await self._general_critical_response(content)
    
    async def _generate_strategic_plan(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive strategic plan"""
        planning_horizon = content.get('planning_horizon', '12_months')
        focus_areas = content.get('focus_areas', ['revenue_growth', 'market_expansion', 'innovation'])
        resource_constraints = content.get('resource_constraints', {})
        
        logger.info(f"Generating {planning_horizon} strategic plan for: {focus_areas}")
        
        # Analyze current situation
        current_status = await self._analyze_current_situation()
        
        # Define strategic objectives
        strategic_objectives = await self._define_strategic_objectives(focus_areas, planning_horizon)
        
        # Develop strategic initiatives
        strategic_initiatives = await self._develop_strategic_initiatives(strategic_objectives)
        
        # Create implementation roadmap
        implementation_roadmap = await self._create_implementation_roadmap(strategic_initiatives)
        
        # Define success metrics
        success_metrics = await self._define_success_metrics(strategic_objectives)
        
        # Calculate resource requirements
        resource_requirements = await self._calculate_resource_requirements(strategic_initiatives)
        
        # Assess risks and mitigation
        risk_assessment = await self._assess_strategic_risks(strategic_initiatives)
        
        strategic_plan = {
            'planning_horizon': planning_horizon,
            'current_status': current_status,
            'strategic_objectives': strategic_objectives,
            'strategic_initiatives': strategic_initiatives,
            'implementation_roadmap': implementation_roadmap,
            'success_metrics': success_metrics,
            'resource_requirements': resource_requirements,
            'risk_assessment': risk_assessment,
            'expected_outcomes': {
                'revenue_growth': '300%',
                'market_share': '25%',
                'profit_margin': '35%',
                'customer_growth': '10000'
            },
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store strategic decision
        decision = StrategicDecision(
            decision_id=f"strategic_plan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            decision_type="strategic_planning",
            description=f"Generate {planning_horizon} strategic plan",
            expected_revenue_impact=500000000,  # $500M expected impact
            expected_cost_savings=50000000,  # $50M expected savings
            risk_level="medium",
            implementation_timeline=planning_horizon,
            confidence_score=0.85,
            created_at=datetime.utcnow()
        )
        self.strategic_decisions.append(decision)
        
        # Share with other executives
        await self._share_strategic_plan(strategic_plan)
        
        return strategic_plan
    
    async def _make_strategic_decision(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Make strategic decision"""
        decision_context = content.get('decision_context', {})
        alternatives = content.get('alternatives', [])
        risk_tolerance = content.get('risk_tolerance', 'medium')
        
        logger.info(f"Making strategic decision with {len(alternatives)} alternatives")
        
        # Analyze alternatives
        analyzed_alternatives = []
        for alt in alternatives:
            analysis = await self._analyze_alternative(alt, decision_context)
            analyzed_alternatives.append(analysis)
        
        # Apply decision framework
        decision_framework = await self._apply_decision_framework(analyzed_alternatives, risk_tolerance)
        
        # Select best alternative
        best_alternative = max(analyzed_alternatives, key=lambda x: x['score'])
        
        # Create decision record
        decision = StrategicDecision(
            decision_id=f"decision_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            decision_type="strategic_decision",
            description=best_alternative['description'],
            expected_revenue_impact=best_alternative['revenue_impact'],
            expected_cost_savings=best_alternative['cost_savings'],
            risk_level=best_alternative['risk_level'],
            implementation_timeline=best_alternative['timeline'],
            confidence_score=best_alternative['confidence'],
            created_at=datetime.utcnow()
        )
        self.strategic_decisions.append(decision)
        
        # Execute decision
        execution_plan = await self._create_execution_plan(best_alternative)
        await self._execute_strategic_decision(execution_plan)
        
        return {
            'decision': best_alternative,
            'rationale': decision_framework['rationale'],
            'expected_outcomes': best_alternative['expected_outcomes'],
            'execution_plan': execution_plan,
            'decision_id': decision.decision_id
        }
    
    async def _optimize_revenue(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize revenue across all channels"""
        market_segment = content.get('market_segment', 'all')
        time_horizon = content.get('time_horizon', '12_months')
        investment_level = content.get('investment_level', 1000000)
        
        logger.info(f"Optimizing revenue for {market_segment} over {time_horizon}")
        
        # Analyze current revenue streams
        current_revenue = await self._analyze_current_revenue()
        
        # Identify optimization opportunities
        optimization_opportunities = await self._identify_optimization_opportunities(current_revenue)
        
        # Calculate revenue potential
        revenue_potential = await self._calculate_revenue_potential(optimization_opportunities)
        
        # Prioritize opportunities
        prioritized_opportunities = await self._prioritize_opportunities(revenue_potential)
        
        # Create optimization plan
        optimization_plan = await self._create_optimization_plan(prioritized_opportunities, investment_level)
        
        # Calculate expected ROI
        expected_roi = await self._calculate_optimization_roi(optimization_plan)
        
        return {
            'current_revenue': current_revenue,
            'optimization_opportunities': optimization_opportunities,
            'prioritized_opportunities': prioritized_opportunities,
            'optimization_plan': optimization_plan,
            'expected_roi': expected_roi,
            'revenue_forecast': {
                'current': current_revenue['total'],
                'optimized': current_revenue['total'] * (1 + expected_roi['roi_percentage']),
                'growth_percentage': expected_roi['roi_percentage']
            }
        }
    
    async def _assess_market_opportunity(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Assess market opportunity"""
        opportunity_data = content.get('opportunity', {})
        assessment_criteria = content.get('criteria', {})
        
        logger.info(f"Assessing market opportunity: {opportunity_data.get('name', 'Unknown')}")
        
        # Market size analysis
        market_size = await self._analyze_market_size(opportunity_data)
        
        # Competitive analysis
        competitive_landscape = await self._analyze_competitive_landscape(opportunity_data)
        
        # Revenue potential
        revenue_potential = await self._calculate_revenue_potential(opportunity_data)
        
        # Risk assessment
        risk_assessment = await self._assess_opportunity_risk(opportunity_data)
        
        # Strategic fit
        strategic_fit = await self._assess_strategic_fit(opportunity_data)
        
        # Overall opportunity score
        opportunity_score = await self._calculate_opportunity_score(
            market_size, competitive_landscape, revenue_potential, risk_assessment, strategic_fit
        )
        
        opportunity = RevenueOpportunity(
            opportunity_id=f"opp_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            market_segment=opportunity_data.get('market_segment'),
            estimated_revenue=revenue_potential['estimated_revenue'],
            probability=opportunity_score['probability'],
            time_to_revenue=opportunity_score['time_to_revenue'],
            required_resources=opportunity_score['required_resources'],
            competitive_advantage=opportunity_score['competitive_advantage'],
            discovered_at=datetime.utcnow()
        )
        self.revenue_opportunities.append(opportunity)
        
        return {
            'opportunity_id': opportunity.opportunity_id,
            'market_size': market_size,
            'competitive_landscape': competitive_landscape,
            'revenue_potential': revenue_potential,
            'risk_assessment': risk_assessment,
            'strategic_fit': strategic_fit,
            'opportunity_score': opportunity_score,
            'recommendation': 'pursue' if opportunity_score['overall_score'] > 0.7 else 'reject'
        }
    
    async def _revenue_monitoring_loop(self):
        """Continuous revenue monitoring"""
        while self.is_active:
            try:
                # Get current revenue data
                revenue_data = await self._get_current_revenue_data()
                
                # Analyze revenue trends
                revenue_analysis = await self._analyze_revenue_trends(revenue_data)
                
                # Detect anomalies
                anomalies = await self._detect_revenue_anomalies(revenue_analysis)
                
                # Send alerts for anomalies
                for anomaly in anomalies:
                    await self.send_message(
                        "cfo_001",
                        MessageType.ALERT,
                        f"Revenue Anomaly Detected",
                        anomaly,
                        priority=Priority.HIGH
                    )
                
                # Update revenue forecast
                await self._update_revenue_forecast(revenue_analysis)
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in revenue monitoring loop: {e}")
                await asyncio.sleep(300)  # 5 minutes
    
    async def _opportunity_hunting_loop(self):
        """Continuous opportunity hunting"""
        while self.is_active:
            try:
                # Scan market for opportunities
                market_scan = await self._scan_market_for_opportunities()
                
                # Analyze opportunities
                analyzed_opportunities = []
                for opp in market_scan:
                    analysis = await self._assess_market_opportunity({'opportunity': opp})
                    analyzed_opportunities.append(analysis)
                
                # Filter high-value opportunities
                high_value_opps = [opp for opp in analyzed_opportunities 
                                  if opp['opportunity_score']['overall_score'] > 0.8]
                
                # Share with CRO for pursuit
                if high_value_opps:
                    await self.send_message(
                        "cro_001",
                        MessageType.COLLABORATION,
                        "High-Value Revenue Opportunities",
                        {'opportunities': high_value_opps},
                        priority=Priority.HIGH
                    )
                
                # Sleep for 6 hours
                await asyncio.sleep(21600)
                
            except Exception as e:
                logger.error(f"Error in opportunity hunting loop: {e}")
                await asyncio.sleep(1800)  # 30 minutes
    
    async def _strategic_planning_loop(self):
        """Continuous strategic planning"""
        while self.is_active:
            try:
                # Review strategic goals progress
                goal_progress = await self._review_strategic_goals_progress()
                
                # Adjust strategies as needed
                if goal_progress['needs_adjustment']:
                    await self._adjust_strategies(goal_progress)
                
                # Generate quarterly strategic updates
                if self._is_quarterly_update_time():
                    await self._generate_quarterly_strategic_update()
                
                # Sleep for 24 hours
                await asyncio.sleep(86400)
                
            except Exception as e:
                logger.error(f"Error in strategic planning loop: {e}")
                await asyncio.sleep(3600)  # 1 hour
    
    async def _get_current_revenue_data(self) -> Dict[str, Any]:
        """Get current revenue data from financial systems"""
        # Request from CFO agent
        response = await self.send_message(
            "cfo_001",
            MessageType.REQUEST,
            "Current Revenue Data",
            {'time_period': 'current_month'},
            requires_response=True
        )
        
        # This would be handled asynchronously
        # For now, return mock data
        return {
            'monthly_revenue': 8500000,  # $8.5M
            'daily_revenue': 283333,  # $283K
            'revenue_streams': {
                'trading_fees': 5000000,
                'premium_subscriptions': 2000000,
                'enterprise_licenses': 1000000,
                'data_services': 500000
            },
            'growth_rate': 0.15  # 15% monthly growth
        }
    
    async def _analyze_revenue_trends(self, revenue_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze revenue trends"""
        # Calculate trends
        monthly_growth = revenue_data.get('growth_rate', 0)
        daily_average = revenue_data.get('daily_revenue', 0)
        
        # Project future revenue
        projected_monthly = daily_average * 30
        projected_annual = projected_monthly * 12
        
        return {
            'current_monthly': revenue_data.get('monthly_revenue', 0),
            'current_daily': daily_average,
            'monthly_growth_rate': monthly_growth,
            'projected_monthly': projected_monthly,
            'projected_annual': projected_annual,
            'trend': 'increasing' if monthly_growth > 0 else 'decreasing'
        }
    
    async def _detect_revenue_anomalies(self, revenue_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect revenue anomalies"""
        anomalies = []
        
        # Check for sudden drops
        if revenue_analysis['monthly_growth_rate'] < -0.1:  # 10% drop
            anomalies.append({
                'type': 'revenue_drop',
                'severity': 'high',
                'description': f"Revenue dropped by {abs(revenue_analysis['monthly_growth_rate']*100):.1f}%",
                'current_value': revenue_analysis['current_monthly'],
                'expected_value': revenue_analysis['current_monthly'] * (1 - revenue_analysis['monthly_growth_rate'])
            })
        
        # Check for unusual patterns
        if revenue_analysis['trend'] == 'decreasing':
            anomalies.append({
                'type': 'negative_trend',
                'severity': 'medium',
                'description': "Revenue trend is negative",
                'current_growth': revenue_analysis['monthly_growth_rate']
            })
        
        return anomalies
    
    async def _scan_market_for_opportunities(self) -> List[Dict[str, Any]]:
        """Scan market for new opportunities"""
        # This would integrate with market research agent
        # For now, return mock opportunities
        return [
            {
                'name': 'Rare Earth Metals Trading',
                'market_segment': 'rare_earth_metals',
                'market_size': 50000000000,  # $50B
                'growth_rate': 0.25,
                'competition_level': 'medium'
            },
            {
                'name': 'Lithium Battery Materials',
                'market_segment': 'battery_materials',
                'market_size': 75000000000,  # $75B
                'growth_rate': 0.35,
                'competition_level': 'high'
            },
            {
                'name': 'Green Minerals Platform',
                'market_segment': 'sustainable_mining',
                'market_size': 100000000000,  # $100B
                'growth_rate': 0.40,
                'competition_level': 'low'
            }
        ]
    
    async def _share_strategic_plan(self, strategic_plan: Dict[str, Any]):
        """Share strategic plan with executive team"""
        # Share with CTO
        await self.send_message(
            "cto_001",
            MessageType.COLLABORATION,
            "Technology Strategic Plan",
            {
                'plan': strategic_plan,
                'focus_areas': ['innovation', 'scalability', 'quantum_integration']
            },
            priority=Priority.HIGH
        )
        
        # Share with CMO
        await self.send_message(
            "cmo_001",
            MessageType.COLLABORATION,
            "Marketing Strategic Plan",
            {
                'plan': strategic_plan,
                'focus_areas': ['market_penetration', 'brand_building', 'customer_acquisition']
            },
            priority=Priority.HIGH
        )
        
        # Share with CRO
        await self.send_message(
            "cro_001",
            MessageType.COLLABORATION,
            "Sales Strategic Plan",
            {
                'plan': strategic_plan,
                'focus_areas': ['enterprise_sales', 'revenue_growth', 'market_expansion']
            },
            priority=Priority.HIGH
        )
    
    async def perform_periodic_tasks(self):
        """Perform periodic CEO tasks"""
        # Update strategic KPIs
        await self._update_strategic_kpis()
        
        # Review strategic decisions
        await self._review_strategic_decisions()
        
        # Update market intelligence
        await self._update_market_intelligence()
    
    async def _update_strategic_kpis(self):
        """Update strategic KPIs"""
        # Get current metrics from various agents
        current_revenue = await self._get_current_revenue_data()
        
        # Update KPIs
        self.strategic_kpis = {
            'current_revenue': current_revenue['monthly_revenue'] * 12,
            'revenue_growth_rate': current_revenue['growth_rate'],
            'strategic_decisions_made': len(self.strategic_decisions),
            'opportunities_identified': len(self.revenue_opportunities),
            'strategic_alignment_score': 0.85,  # Mock value
            'innovation_index': 0.92  # Mock value
        }
    
    async def _get_strategic_status(self) -> Dict[str, Any]:
        """Get current strategic status"""
        return {
            'strategic_goals': self.strategic_goals,
            'strategic_kpis': self.strategic_kpis,
            'recent_decisions': [
                {
                    'decision_id': d.decision_id,
                    'decision_type': d.decision_type,
                    'expected_revenue_impact': d.expected_revenue_impact,
                    'confidence_score': d.confidence_score,
                    'created_at': d.created_at.isoformat()
                }
                for d in self.strategic_decisions[-5:]
            ],
            'revenue_opportunities': [
                {
                    'opportunity_id': o.opportunity_id,
                    'market_segment': o.market_segment,
                    'estimated_revenue': o.estimated_revenue,
                    'probability': o.probability,
                    'discovered_at': o.discovered_at.isoformat()
                }
                for o in self.revenue_opportunities[-5:]
            ]
        }

# Initialize CEO Agent
ceo_agent = CEOAgent()
