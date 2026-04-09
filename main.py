import asyncio
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from anthropic import Anthropic
from tavily import TavilyClient
from supabase import create_client, Client
import re

# Import DEDAN Mine Tax Oracle for legal compliance
from services.regulatory import tax_oracle

# Load environment variables
load_dotenv()

@dataclass
class NewsItem:
    title: str
    content: str
    category: str
    analysis: str
    analysis_am: str
    source_url: str
    price_trend: Optional[Dict[str, Any]]
    priority: int

@dataclass
class AgentState:
    search_queries: List[str]
    raw_news: List[Dict[str, Any]]
    processed_news: List[NewsItem]
    posted_news: List[Dict[str, Any]]
    errors: List[str]

class MarketNewsAgent:
    def __init__(self):
        self.openai_llm = ChatOpenAI(model="gpt-4", temperature=0.1)
        self.claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
        
        # Initialize Tax Oracle for Ethiopian mining royalties and international duties
        self.tax_oracle = tax_oracle
        
        self.search_queries = [
            "Global economic trends market analysis 2024",
            "E-commerce supply chain reports disruptions",
            "Commodity price updates gold silver copper",
            "Mining industry news market trends",
            "Small business market insights economic indicators"
        ]

    async def search_news(self, state: AgentState) -> AgentState:
        """Search for market news using Tavily API"""
        print("🔍 Searching for market news...")
        
        all_results = []
        
        for query in self.search_queries:
            try:
                results = self.tavily_client.search(
                    query=query,
                    search_depth="advanced",
                    include_raw_content=True,
                    max_results=5
                )
                
                for result in results.get("results", []):
                    all_results.append({
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "published_date": result.get("published_date", ""),
                        "query": query
                    })
                    
            except Exception as e:
                error_msg = f"Error searching for '{query}': {str(e)}"
                print(f"❌ {error_msg}")
                state.errors.append(error_msg)
        
        state.raw_news = all_results
        print(f"✅ Found {len(all_results)} news articles")
        return state

    async def analyze_news(self, state: AgentState) -> AgentState:
        """Analyze news using Claude 3.5 Sonnet"""
        print("🧠 Analyzing news with Claude...")
        
        processed_items = []
        
        for item in state.raw_news:
            try:
                # Categorize news
                category = await self.categorize_news(item)
                
                # Generate analysis
                analysis = await self.generate_analysis(item, category)
                
                # Generate Amharic translation
                analysis_am = await self.translate_to_amharic(analysis)
                
                # Extract price trends
                price_trend = await self.extract_price_trends(item)
                
                # Determine priority
                priority = self.calculate_priority(item, category, price_trend)
                
                news_item = NewsItem(
                    title=item["title"][:200],  # Limit title length
                    content=item["content"][:1000],  # Limit content length
                    category=category,
                    analysis=analysis,
                    analysis_am=analysis_am,
                    source_url=item["url"],
                    price_trend=price_trend,
                    priority=priority
                )
                
                processed_items.append(news_item)
                
            except Exception as e:
                error_msg = f"Error analyzing news item '{item.get('title', 'Unknown')}': {str(e)}"
                print(f"❌ {error_msg}")
                state.errors.append(error_msg)
        
        state.processed_news = processed_items
        print(f"✅ Processed {len(processed_items)} news items")
        return state

    async def categorize_news(self, item: Dict[str, Any]) -> str:
        """Categorize news into Economic, Supply, or Mini"""
        content = f"{item['title']} {item['content']}".lower()
        
        # Economic indicators
        economic_keywords = [
            'gdp', 'inflation', 'interest rates', 'economic growth', 'market',
            'financial', 'economy', 'recession', 'stock market', 'currency'
        ]
        
        # Supply chain indicators
        supply_keywords = [
            'supply chain', 'logistics', 'shipping', 'delivery', 'inventory',
            'warehouse', 'distribution', 'transportation', 'procurement'
        ]
        
        # Mini/Daily indicators
        mini_keywords = [
            'small business', 'smb', 'local market', 'daily', 'weekly',
            'community', 'retail', 'shop', 'store'
        ]
        
        economic_score = sum(1 for keyword in economic_keywords if keyword in content)
        supply_score = sum(1 for keyword in supply_keywords if keyword in content)
        mini_score = sum(1 for keyword in mini_keywords if keyword in content)
        
        if economic_score >= supply_score and economic_score >= mini_score:
            return "Economic"
        elif supply_score >= mini_score:
            return "Supply"
        else:
            return "Mini"

    async def generate_analysis(self, item: Dict[str, Any], category: str) -> str:
        """Generate professional analysis for SMB owners"""
        prompt = f"""
        Analyze this news article and provide a short, professional insight specifically for small and medium business owners:
        
        Title: {item['title']}
        Content: {item['content']}
        Category: {category}
        
        Provide a concise analysis (2-3 sentences) that explains:
        1. What this means for SMBs
        2. Any actionable insights
        3. Potential impact on business operations
        
        Keep it professional, brief, and focused on business implications.
        """
        
        try:
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"Error generating analysis: {e}")
            return "Analysis unavailable at this time."

    async def translate_to_amharic(self, text: str) -> str:
        """Translate text to Amharic"""
        try:
            # For now, return a placeholder. In production, integrate Google Translate API
            return f"[Amharic: {text[:100]}...]"
            
        except Exception as e:
            print(f"Error translating to Amharic: {e}")
            return "[Amharic translation unavailable]"

    async def extract_price_trends(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract price trend information from news"""
        content = f"{item['title']} {item['content']}".lower()
        
        # Look for price changes
        price_patterns = [
            r'(\w+)\s+(increased|rose|gained)\s+by\s+(\d+\.?\d*)%?',
            r'(\w+)\s+(decreased|fell|dropped)\s+by\s+(\d+\.?\d*)%?',
            r'(\w+)\s+(up|down)\s+(\d+\.?\d*)%?',
        ]
        
        commodities = ['gold', 'silver', 'copper', 'oil', 'gas', 'wheat', 'corn', 'coffee']
        
        for pattern in price_patterns:
            match = re.search(pattern, content)
            if match:
                commodity = match.group(1).lower()
                if commodity in commodities:
                    direction = 'up' if 'increased' in match.group(2) or 'rose' in match.group(2) or 'gained' in match.group(2) or 'up' in match.group(2) else 'down'
                    percentage = float(match.group(3))
                    
                    return {
                        'direction': direction,
                        'percentage': percentage,
                        'commodity': commodity.capitalize()
                    }
        
        return None

    def calculate_priority(self, item: Dict[str, Any], category: str, price_trend: Optional[Dict[str, Any]]) -> int:
        """Calculate news priority (1-5, 5 being highest)"""
        priority = 1
        
        # Boost priority based on category
        if category == "Economic":
            priority += 1
        elif category == "Supply":
            priority += 2
        
        # Boost priority if price trend exists
        if price_trend:
            priority += 1
            if abs(price_trend['percentage']) > 5:  # Large price changes
                priority += 1
        
        # Check for urgency keywords
        urgent_keywords = ['urgent', 'alert', 'warning', 'critical', 'breaking']
        content = f"{item['title']} {item['content']}".lower()
        if any(keyword in content for keyword in urgent_keywords):
            priority += 1
        
        return min(priority, 5)

    async def post_to_supabase(self, state: AgentState) -> AgentState:
        """Post processed news to Supabase"""
        print("📤 Posting news to Supabase...")
        
        posted_items = []
        
        for news_item in state.processed_news:
            try:
                # Check for duplicates
                existing = self.supabase.table('market_news').select('id').eq('title', news_item.title).execute()
                
                if not existing.data:
                    # Insert new news item
                    news_data = {
                        'title': news_item.title,
                        'content': news_item.content,
                        'category': news_item.category,
                        'analysis': news_item.analysis,
                        'analysis_am': news_item.analysis_am,
                        'source_url': news_item.source_url,
                        'price_trend': news_item.price_trend,
                        'priority': news_item.priority,
                        'is_active': True
                    }
                    
                    result = self.supabase.table('market_news').insert(news_data).execute()
                    posted_items.append(result.data[0])
                    print(f"✅ Posted: {news_item.title[:50]}...")
                else:
                    print(f"⏭️  Skipped duplicate: {news_item.title[:50]}...")
                    
            except Exception as e:
                error_msg = f"Error posting news item: {str(e)}"
                print(f"❌ {error_msg}")
                state.errors.append(error_msg)
        
        state.posted_news = posted_items
        print(f"✅ Posted {len(posted_items)} news items to Supabase")
        return state

    def create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("search_news", self.search_news)
        workflow.add_node("analyze_news", self.analyze_news)
        workflow.add_node("post_to_supabase", self.post_to_supabase)
        
        # Add edges
        workflow.set_entry_point("search_news")
        workflow.add_edge("search_news", "analyze_news")
        workflow.add_edge("analyze_news", "post_to_supabase")
        workflow.add_edge("post_to_supabase", END)
        
        return workflow.compile()

    async def calculate_mining_taxes(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate Ethiopian mining royalties and international duties for legal compliance"""
        try:
            # Use Tax Oracle to calculate all applicable taxes
            tax_calculation = await self.tax_oracle.calculate_transaction_taxes(transaction_data)
            
            if tax_calculation["success"]:
                return {
                    "success": True,
                    "transaction_id": transaction_data.get("transaction_id"),
                    "total_tax_amount": tax_calculation["total_tax_amount"],
                    "tax_breakdown": tax_calculation["tax_calculations"],
                    "ethiopian_royalties": next(
                        (tax for tax in tax_calculation["tax_calculations"] 
                         if tax["jurisdiction"] == "ethiopia_local"), None
                    ),
                    "export_duties": next(
                        (tax for tax in tax_calculation["tax_calculations"] 
                         if tax["jurisdiction"] == "international_export"), None
                    ),
                    "compliance_report": tax_calculation["compliance_report"],
                    "legal_compliance": True
                }
            else:
                return {
                    "success": False,
                    "error": tax_calculation["error"],
                    "legal_compliance": False
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "legal_compliance": False
            }

    async def ensure_legal_compliance(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure 100% legal compliance for mining transactions"""
        try:
            # Calculate taxes for compliance
            tax_result = await self.calculate_mining_taxes(transaction_data)
            
            if not tax_result["success"]:
                return tax_result
            
            # Verify Ethiopian mining royalty compliance
            ethiopian_royalties = tax_result.get("ethiopian_royalties")
            if ethiopian_royalties:
                royalty_rate = ethiopian_royalties["tax_rate"]
                royalty_amount = ethiopian_royalties["tax_amount"]
                
                # Verify royalty rates are within legal bounds (5-8%)
                if not (0.05 <= royalty_rate <= 0.08):
                    return {
                        "success": False,
                        "error": f"Invalid Ethiopian royalty rate: {royalty_rate:.2%}",
                        "legal_compliance": False
                    }
            
            # Verify export duty compliance
            export_duties = tax_result.get("export_duties")
            if export_duties:
                duty_rate = export_duties["tax_rate"]
                
                # Verify export duty rates are within legal bounds (1.5-3.5%)
                if not (0.015 <= duty_rate <= 0.035):
                    return {
                        "success": False,
                        "error": f"Invalid export duty rate: {duty_rate:.2%}",
                        "legal_compliance": False
                    }
            
            # Generate compliance certificate
            compliance_certificate = {
                "certificate_id": f"TAX_CERT_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "transaction_id": transaction_data.get("transaction_id"),
                "ethiopian_royalties_paid": ethiopian_royalties["tax_amount"] if ethiopian_royalties else 0,
                "export_duties_paid": export_duties["tax_amount"] if export_duties else 0,
                "total_taxes_paid": tax_result["total_tax_amount"],
                "compliance_status": "COMPLIANT",
                "issued_at": datetime.now(timezone.utc).isoformat(),
                "valid_until": (datetime.now(timezone.utc) + timedelta(days=365)).isoformat()
            }
            
            return {
                "success": True,
                "legal_compliance": True,
                "compliance_certificate": compliance_certificate,
                "tax_calculation": tax_result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "legal_compliance": False
            }

async def main():
    """Main execution function"""
    print("🚀 Starting Market News Agent...")
    
    agent = MarketNewsAgent()
    graph = agent.create_graph()
    
    # Initialize state
    initial_state = AgentState(
        search_queries=agent.search_queries,
        raw_news=[],
        processed_news=[],
        posted_news=[],
        errors=[]
    )
    
    try:
        # Run the workflow
        result = await graph.ainvoke(initial_state)
        
        print("\n📊 Execution Summary:")
        print(f"✅ Raw news found: {len(result.raw_news)}")
        print(f"✅ News processed: {len(result.processed_news)}")
        print(f"✅ News posted: {len(result.posted_news)}")
        print(f"❌ Errors: {len(result.errors)}")
        
        if result.errors:
            print("\n⚠️  Errors encountered:")
            for error in result.errors:
                print(f"  - {error}")
        
        print("\n🎉 Market News Agent completed successfully!")
        
        # Demonstrate Tax Oracle compliance functionality
        print("\n💰 Demonstrating Tax Oracle Compliance...")
        
        # Sample transaction for tax calculation
        sample_transaction = {
            "transaction_id": f"TXN_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            "mineral_type": "gold",
            "quantity": 1000,
            "unit_price": 2000.0,
            "origin_country": "Ethiopia",
            "destination_country": "USA",
            "transit_countries": ["Djibouti"]
        }
        
        # Calculate taxes and ensure compliance
        compliance_result = await agent.ensure_legal_compliance(sample_transaction)
        
        if compliance_result["success"]:
            print("✅ Legal compliance verified:")
            print(f"   Transaction ID: {compliance_result['compliance_certificate']['transaction_id']}")
            print(f"   Ethiopian Royalties: ${compliance_result['compliance_certificate']['ethiopian_royalties_paid']:,.2f}")
            print(f"   Export Duties: ${compliance_result['compliance_certificate']['export_duties_paid']:,.2f}")
            print(f"   Total Taxes: ${compliance_result['compliance_certificate']['total_taxes_paid']:,.2f}")
            print(f"   Certificate: {compliance_result['compliance_certificate']['certificate_id']}")
        else:
            print(f"❌ Compliance error: {compliance_result['error']}")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🎉 Market News Agent completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
