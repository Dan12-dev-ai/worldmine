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
import pandas as pd
import re

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
        
    except Exception as e:
        print(f"💥 Fatal error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
