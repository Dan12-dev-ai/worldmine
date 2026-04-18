"""
Market Expansion Agent - DISCOVERY AGENT
Identifies small tasks on Upwork and GitHub that agents can solve
Alerts via Telegram bot for global market expansion
"""

import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import sqlite3

@dataclass
class TaskOpportunity:
    platform: str
    task_id: str
    title: str
    description: str
    budget: str
    skills_required: List[str]
    location: str
    posted_date: str
    deadline: str
    agent_match: str
    confidence_score: float
    estimated_completion_time: str

@dataclass
class GitHubIssue:
    repo: str
    issue_number: int
    title: str
    description: str
    labels: List[str]
    language: str
    posted_date: str
    agent_match: str
    confidence_score: float
    estimated_completion_time: str

class MarketExpansionAgent:
    """DISCOVERY AGENT - Identifies opportunities for global market expansion"""
    
    def __init__(self):
        self.agent_capabilities = {
            "global_voice": {
                "skills": ["content_creation", "social_media_marketing", "video_production", "translation", "copywriting"],
                "hourly_rate": "$50-150",
                "specializations": ["4K_video", "multilingual_content", "viral_marketing", "global_campaigns"]
            },
            "growth_hacker": {
                "skills": ["seo_optimization", "growth_hacking", "influencer_outreach", "market_analysis", "content_strategy"],
                "hourly_rate": "$75-200",
                "specializations": ["technical_seo", "viral_content", "influencer_marketing", "data_analysis"]
            },
            "legal_architect": {
                "skills": ["legal_compliance", "smart_contracts", "regulatory_analysis", "document_generation", "jurisdiction_expertise"],
                "hourly_rate": "$100-300",
                "specializations": ["blockchain_law", "international_compliance", "smart_contract_development", "risk_management"]
            },
            "b2b_negotiator": {
                "skills": ["business_development", "partnership_negotiation", "market_research", "proposal_writing", "relationship_management"],
                "hourly_rate": "$80-250",
                "specializations": ["b2b_sales", "partnership_development", "market_expansion", "strategic_planning"]
            }
        }
        
        # Initialize database for opportunity tracking
        self.db_path = "market_expansion.db"
        self._init_database()
        
        # Telegram bot configuration
        self.telegram_bot_token = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN")
        self.telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID", "YOUR_CHAT_ID")
        
        # Opportunity tracking
        self.opportunities_found = []
        self.issues_found = []
        
    def _init_database(self):
        """Initialize SQLite database for market expansion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT,
                task_id TEXT,
                title TEXT,
                description TEXT,
                budget TEXT,
                skills_required TEXT,
                location TEXT,
                posted_date TEXT,
                deadline TEXT,
                agent_match TEXT,
                confidence_score REAL,
                estimated_completion_time TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS github_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo TEXT,
                issue_number INTEGER,
                title TEXT,
                description TEXT,
                labels TEXT,
                language TEXT,
                posted_date TEXT,
                agent_match TEXT,
                confidence_score REAL,
                estimated_completion_time TEXT,
                status TEXT,
                created_at TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                alert_type TEXT,
                opportunity_id TEXT,
                message TEXT,
                sent_at TEXT,
                response_received TEXT,
                status TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    async def scan_upwork_opportunities(self) -> List[TaskOpportunity]:
        """Scan Upwork for tasks that agents can solve"""
        print("🔍 SCANNING UPWORK FOR AGENT OPPORTUNITIES...")
        
        opportunities = []
        
        # Simulate Upwork API calls for different job categories
        categories = [
            "content_marketing", "seo", "social_media_marketing", 
            "legal_consulting", "business_consulting", "market_research"
        ]
        
        for category in categories:
            try:
                # Simulate API response with realistic opportunities
                category_opportunities = await self._fetch_upwork_jobs(category)
                opportunities.extend(category_opportunities)
                
                # Rate limiting
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"⚠️ Error scanning {category}: {e}")
        
        # Match opportunities with agents
        matched_opportunities = []
        for opportunity in opportunities:
            match_result = self._match_opportunity_with_agent(opportunity)
            if match_result["match"]:
                matched_opportunity.append(TaskOpportunity(
                    platform="upwork",
                    task_id=opportunity["id"],
                    title=opportunity["title"],
                    description=opportunity["description"],
                    budget=opportunity["budget"],
                    skills_required=opportunity["skills_required"],
                    location=opportunity["location"],
                    posted_date=opportunity["posted_date"],
                    deadline=opportunity["deadline"],
                    agent_match=match_result["agent"],
                    confidence_score=match_result["confidence"],
                    estimated_completion_time=match_result["estimated_time"]
                ))
        
        self.opportunities_found.extend(matched_opportunities)
        print(f"🎯 Found {len(matched_opportunities)} Upwork opportunities for agents")
        
        return matched_opportunities
    
    async def _fetch_upwork_jobs(self, category: str) -> List[Dict[str, Any]]:
        """Fetch jobs from Upwork API (simulated)"""
        # Simulate realistic Upwork job postings
        jobs = []
        
        if category == "content_marketing":
            jobs = [
                {
                    "id": f"UPW_CONTENT_{datetime.now().strftime('%H%M%S')}",
                    "title": "Need 4K Video Content for Global Mining Platform",
                    "description": "Looking for content creator to produce 4K marketing videos for blockchain mining platform. Must be able to create content in multiple languages.",
                    "budget": "$500-1,000",
                    "skills_required": ["video_production", "content_creation", "multilingual", "blockchain"],
                    "location": "Remote",
                    "posted_date": datetime.now().isoformat(),
                    "deadline": (datetime.now() + timedelta(days=7)).isoformat()
                },
                {
                    "id": f"UPW_SOCIAL_{datetime.now().strftime('%H%M%S')}",
                    "title": "Social Media Manager for Crypto Trading Platform",
                    "description": "Need experienced social media manager to handle global crypto trading platform accounts. Must manage 10+ platforms across different time zones.",
                    "budget": "$1,000-3,000",
                    "skills_required": ["social_media_marketing", "crypto", "global_marketing", "content_strategy"],
                    "location": "Remote",
                    "posted_date": datetime.now().isoformat(),
                    "deadline": (datetime.now() + timedelta(days=14)).isoformat()
                }
            ]
        elif category == "seo":
            jobs = [
                {
                    "id": f"UPW_SEO_{datetime.now().strftime('%H%M%S')}",
                    "title": "SEO Expert for Global Mining Marketplace",
                    "description": "Need SEO expert to optimize global mining marketplace for 256 countries. Must have experience with international SEO and multiple search engines.",
                    "budget": "$2,000-5,000",
                    "skills_required": ["seo", "international_marketing", "technical_seo", "analytics"],
                    "location": "Remote",
                    "posted_date": datetime.now().isoformat(),
                    "deadline": (datetime.now() + timedelta(days=30)).isoformat()
                }
            ]
        elif category == "legal_consulting":
            jobs = [
                {
                    "id": f"UPW_LEGAL_{datetime.now().strftime('%H%M%S')}",
                    "title": "Blockchain Legal Consultant for Global Platform",
                    "description": "Need legal expert to review smart contracts and ensure compliance across 256 jurisdictions. Experience with international crypto law required.",
                    "budget": "$3,000-8,000",
                    "skills_required": ["blockchain_law", "smart_contracts", "compliance", "international_law"],
                    "location": "Remote",
                    "posted_date": datetime.now().isoformat(),
                    "deadline": (datetime.now() + timedelta(days=45)).isoformat()
                }
            ]
        elif category == "business_consulting":
            jobs = [
                {
                    "id": f"UPW_BIZ_{datetime.now().strftime('%H%M%S')}",
                    "title": "B2B Partnership Developer for Mining Platform",
                    "description": "Need business development expert to establish partnerships with mining companies globally. Must have experience with Fortune 500 negotiations.",
                    "budget": "$2,500-6,000",
                    "skills_required": ["business_development", "partnership_negotiation", "mining_industry", "b2b_sales"],
                    "location": "Remote",
                    "posted_date": datetime.now().isoformat(),
                    "deadline": (datetime.now() + timedelta(days=21)).isoformat()
                }
            ]
        
        return jobs
    
    async def scan_github_issues(self) -> List[GitHubIssue]:
        """Scan GitHub for issues that agents can solve"""
        print("🔍 SCANNING GITHUB FOR AGENT OPPORTUNITIES...")
        
        issues = []
        
        # Target repositories relevant to our agents' capabilities
        target_repos = [
            "ethereum/solidity", "openzeppelin/openzeppelin-contracts",
            "hardhat/hardhat", "truffle-box/truffle",
            "uniswap/v2-core", "compound-finance/compound-protocol",
            "aave/aave-v3-core", "makerdao/dss",
            "chainlink/chainlink", "graphprotocol/graph-node",
            "ipfs/ipfs", "filecoin-project/filecoin-ffi",
            "solana-labs/solana-web3.js", "rust-lang/rust"
        ]
        
        for repo in target_repos:
            try:
                # Simulate GitHub API calls
                repo_issues = await self._fetch_github_issues(repo)
                issues.extend(repo_issues)
                
                # Rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"⚠️ Error scanning {repo}: {e}")
        
        # Match issues with agents
        matched_issues = []
        for issue in issues:
            match_result = self._match_issue_with_agent(issue)
            if match_result["match"]:
                matched_issues.append(GitHubIssue(
                    repo=issue["repo"],
                    issue_number=issue["number"],
                    title=issue["title"],
                    description=issue["description"],
                    labels=issue["labels"],
                    language=issue["language"],
                    posted_date=issue["posted_date"],
                    agent_match=match_result["agent"],
                    confidence_score=match_result["confidence"],
                    estimated_completion_time=match_result["estimated_time"]
                ))
        
        self.issues_found.extend(matched_issues)
        print(f"🎯 Found {len(matched_issues)} GitHub issues for agents")
        
        return matched_issues
    
    async def _fetch_github_issues(self, repo: str) -> List[Dict[str, Any]]:
        """Fetch issues from GitHub API (simulated)"""
        # Simulate realistic GitHub issues
        issues = []
        
        if "solidity" in repo or "openzeppelin" in repo:
            issues = [
                {
                    "repo": repo,
                    "number": 1234,
                    "title": "Smart contract gas optimization needed",
                    "description": "Looking for expert to optimize gas costs in DeFi smart contracts. Need someone with experience in gas optimization patterns.",
                    "labels": ["smart-contracts", "optimization", "gas"],
                    "language": "Solidity",
                    "posted_date": datetime.now().isoformat()
                },
                {
                    "repo": repo,
                    "number": 1235,
                    "title": "Multi-chain deployment automation",
                    "description": "Need help automating smart contract deployment across multiple blockchain networks. Experience with cross-chain bridges required.",
                    "labels": ["automation", "deployment", "multi-chain"],
                    "language": "Solidity",
                    "posted_date": datetime.now().isoformat()
                }
            ]
        elif "hardhat" in repo or "truffle" in repo:
            issues = [
                {
                    "repo": repo,
                    "number": 2341,
                    "title": "Testing framework integration issues",
                    "description": "Having trouble integrating advanced testing patterns with Hardhat. Need expert in testing frameworks and CI/CD.",
                    "labels": ["testing", "integration", "ci-cd"],
                    "language": "JavaScript",
                    "posted_date": datetime.now().isoformat()
                }
            ]
        elif "uniswap" in repo or "aave" in repo or "compound" in repo:
            issues = [
                {
                    "repo": repo,
                    "number": 3456,
                    "title": "Liquidity pool optimization strategies",
                    "description": "Looking for DeFi expert to help optimize liquidity pool strategies for better yield farming. Experience with AMM protocols required.",
                    "labels": ["defi", "liquidity", "yield-farming"],
                    "language": "Solidity",
                    "posted_date": datetime.now().isoformat()
                }
            ]
        
        return issues
    
    def _match_opportunity_with_agent(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Match Upwork opportunity with best agent"""
        opportunity_skills = [skill.lower() for skill in opportunity["skills_required"]]
        
        best_match = {"agent": None, "confidence": 0.0, "estimated_time": "N/A"}
        
        for agent_name, agent_config in self.agent_capabilities.items():
            agent_skills = [skill.lower() for skill in agent_config["skills"]]
            
            # Calculate skill match percentage
            matching_skills = set(opportunity_skills) & set(agent_skills)
            match_percentage = len(matching_skills) / len(agent_skills)
            
            # Calculate budget compatibility
            budget_range = opportunity["budget"].replace("$", "").split("-")
            min_budget = float(budget_range[0])
            max_budget = float(budget_range[1])
            agent_rate = agent_config["hourly_rate"].replace("$", "").split("-")
            agent_min_rate = float(agent_rate[0])
            agent_max_rate = float(agent_rate[1])
            
            # Check if budget aligns with agent rates
            budget_compatible = (min_budget >= agent_min_rate * 20) and (max_budget <= agent_max_rate * 40)
            
            # Calculate overall confidence score
            confidence = match_percentage * 0.7 + (0.3 if budget_compatible else 0.0)
            
            if confidence > best_match["confidence"]:
                best_match = {
                    "agent": agent_name,
                    "confidence": confidence,
                    "estimated_time": f"{int(20 / match_percentage)} hours" if match_percentage > 0 else "N/A"
                }
        
        best_match["match"] = best_match["confidence"] > 0.5
        return best_match
    
    def _match_issue_with_agent(self, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Match GitHub issue with best agent"""
        issue_text = f"{issue['title']} {issue['description']}".lower()
        issue_labels = [label.lower() for label in issue["labels"]]
        
        best_match = {"agent": None, "confidence": 0.0, "estimated_time": "N/A"}
        
        for agent_name, agent_config in self.agent_capabilities.items():
            agent_skills = [skill.lower() for skill in agent_config["skills"]]
            agent_specializations = [spec.lower() for spec in agent_config["specializations"]]
            
            # Calculate text match
            text_match = 0
            for skill in agent_skills:
                if skill in issue_text:
                    text_match += 1
            
            # Calculate label match
            label_match = 0
            for spec in agent_specializations:
                for label in issue_labels:
                    if spec in label:
                        label_match += 1
            
            # Calculate overall confidence
            confidence = (text_match * 0.6 + label_match * 0.4) / max(len(agent_skills), len(agent_specializations))
            
            if confidence > best_match["confidence"]:
                best_match = {
                    "agent": agent_name,
                    "confidence": confidence,
                    "estimated_time": f"{int(40 / (confidence + 0.1))} hours" if confidence > 0 else "N/A"
                }
        
        best_match["match"] = best_match["confidence"] > 0.3
        return best_match
    
    async def send_telegram_alert(self, message: str, opportunity_type: str = "opportunity") -> bool:
        """Send alert via Telegram bot"""
        try:
            if not self.telegram_bot_token or self.telegram_bot_token == "YOUR_BOT_TOKEN":
                print("⚠️ Telegram bot token not configured")
                return False
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": f"🌍 DEDAN MARKET EXPANSION ALERT\n\n{message}",
                "parse_mode": "HTML",
                "disable_web_page_preview": False
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        print(f"📱 Telegram alert sent: {opportunity_type}")
                        return True
                    else:
                        print(f"❌ Failed to send Telegram alert: {response.status}")
                        return False
                        
        except Exception as e:
            print(f"❌ Telegram alert error: {e}")
            return False
    
    def _store_opportunity(self, opportunity: TaskOpportunity):
        """Store opportunity in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO opportunities 
            (platform, task_id, title, description, budget, skills_required, location, posted_date, deadline, agent_match, confidence_score, estimated_completion_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            opportunity.platform, opportunity.task_id, opportunity.title, opportunity.description,
            opportunity.budget, json.dumps(opportunity.skills_required), opportunity.location,
            opportunity.posted_date, opportunity.deadline, opportunity.agent_match,
            opportunity.confidence_score, opportunity.estimated_completion_time, "new",
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _store_github_issue(self, issue: GitHubIssue):
        """Store GitHub issue in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO github_issues 
            (repo, issue_number, title, description, labels, language, posted_date, agent_match, confidence_score, estimated_completion_time, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            issue.repo, issue.issue_number, issue.title, issue.description,
            json.dumps(issue.labels), issue.language, issue.posted_date,
            issue.agent_match, issue.confidence_score, issue.estimated_completion_time,
            "new", datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    async def run_market_expansion_cycle(self) -> Dict[str, Any]:
        """Run complete market expansion cycle"""
        print("🌍 MARKET EXPANSION AGENT: Starting global opportunity discovery...")
        
        cycle_results = {
            "cycle_timestamp": datetime.now().isoformat(),
            "upwork_opportunities": [],
            "github_issues": [],
            "total_opportunities": 0,
            "high_confidence_opportunities": 0,
            "alerts_sent": 0
        }
        
        # Scan Upwork opportunities
        upwork_opportunities = await self.scan_upwork_opportunities()
        cycle_results["upwork_opportunities"] = upwork_opportunities
        
        # Scan GitHub issues
        github_issues = await self.scan_github_issues()
        cycle_results["github_issues"] = github_issues
        
        # Calculate totals
        cycle_results["total_opportunities"] = len(upwork_opportunities) + len(github_issues)
        cycle_results["high_confidence_opportunities"] = len(
            [opp for opp in upwork_opportunities if opp.confidence_score > 0.7]
        ) + len(
            [issue for issue in github_issues if issue.confidence_score > 0.5]
        )
        
        # Store opportunities in database
        for opportunity in upwork_opportunities:
            self._store_opportunity(opportunity)
        
        for issue in github_issues:
            self._store_github_issue(issue)
        
        # Send high-confidence alerts via Telegram
        alerts_sent = 0
        
        # Alert for high-confidence Upwork opportunities
        for opportunity in upwork_opportunities:
            if opportunity.confidence_score > 0.8:
                alert_message = f"""
🎯 HIGH-CONFIDENCE OPPORTUNITY DETECTED

📋 Platform: Upwork
🏷️ Agent: {opportunity.agent_match}
💰 Budget: {opportunity.budget}
⏱️ Confidence: {opportunity.confidence_score:.1%}
⏰ Est. Time: {opportunity.estimated_completion_time}

📝 Title: {opportunity.title}
📍 Location: {opportunity.location}
🗓️ Deadline: {opportunity.deadline}

🔗 Task ID: {opportunity.task_id}
                """
                
                if await self.send_telegram_alert(alert_message, "upwork_high_confidence"):
                    alerts_sent += 1
        
        # Alert for high-confidence GitHub issues
        for issue in github_issues:
            if issue.confidence_score > 0.6:
                alert_message = f"""
🔧 HIGH-CONFIDENCE GITHUB ISSUE DETECTED

📋 Platform: GitHub
🏷️ Agent: {issue.agent_match}
⏱️ Confidence: {issue.confidence_score:.1%}
⏰ Est. Time: {issue.estimated_completion_time}

📝 Title: {issue.title}
🏷️ Labels: {', '.join(issue.labels)}
🐙 Language: {issue.language}
🗓️ Posted: {issue.posted_date}

🔗 Issue: {issue.repo}#{issue.issue_number}
                """
                
                if await self.send_telegram_alert(alert_message, "github_high_confidence"):
                    alerts_sent += 1
        
        cycle_results["alerts_sent"] = alerts_sent
        
        print(f"🌍 Market Expansion Cycle Results:")
        print(f"   Total Opportunities: {cycle_results['total_opportunities']}")
        print(f"   High Confidence: {cycle_results['high_confidence_opportunities']}")
        print(f"   Telegram Alerts: {cycle_results['alerts_sent']}")
        
        return cycle_results
    
    async def start_continuous_market_expansion(self):
        """Start continuous market expansion operations"""
        print("🌍 MARKET EXPANSION AGENT: Starting continuous opportunity discovery...")
        
        while True:
            try:
                # Run market expansion cycle every 2 hours
                results = await self.run_market_expansion_cycle()
                
                # Store results for analytics
                self._store_cycle_results(results)
                
                print(f"🌍 Market expansion cycle completed. Next cycle in 2 hours...")
                await asyncio.sleep(7200)  # 2 hours
                
            except Exception as e:
                print(f"❌ Error in market expansion cycle: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retry
    
    def _store_cycle_results(self, results: Dict[str, Any]):
        """Store cycle results for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO agent_alerts 
            (agent_name, alert_type, opportunity_id, message, sent_at, response_received, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            "market_expansion_agent",
            "cycle_results",
            results["cycle_timestamp"],
            json.dumps(results),
            datetime.now().isoformat(),
            None,
            "completed"
        ))
        
        conn.commit()
        conn.close()
        
        print(f"💾 Market expansion results stored: {results['cycle_timestamp']}")
        print(f"   Opportunities found: {results['total_opportunities']}")
        print(f"   High confidence: {results['high_confidence_opportunities']}")
        print(f"   Alerts sent: {results['alerts_sent']}")

# Initialize Market Expansion Agent
market_expansion_agent = MarketExpansionAgent()
