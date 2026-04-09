"""
Simplified Worldmine Backend for Render Free Tier
Provides essential API endpoints without heavy dependencies
"""

import asyncio
import os
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from supabase import create_client, Client

# Load environment variables
load_dotenv()

class SimpleMarketNewsAgent:
    """Simplified agent for basic functionality"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        )
    
    async def get_basic_news(self) -> list:
        """Get basic news from Supabase"""
        try:
            result = self.supabase.table('market_news').select('*').limit(10).execute()
            return result.data or []
        except Exception as e:
            print(f"Error fetching news: {e}")
            return []
    
    async def analyze_simple_text(self, text: str) -> Dict[str, Any]:
        """Simple text analysis without AI"""
        try:
            # Basic analysis
            word_count = len(text.split())
            char_count = len(text)
            
            # Simple sentiment based on keywords
            positive_words = ['good', 'great', 'excellent', 'positive', 'growth', 'increase']
            negative_words = ['bad', 'terrible', 'negative', 'decline', 'decrease', 'loss']
            
            positive_count = sum(1 for word in positive_words if word in text.lower())
            negative_count = sum(1 for word in negative_words if word in text.lower())
            
            sentiment = 'neutral'
            if positive_count > negative_count:
                sentiment = 'positive'
            elif negative_count > positive_count:
                sentiment = 'negative'
            
            return {
                'word_count': word_count,
                'char_count': char_count,
                'sentiment': sentiment,
                'positive_score': positive_count,
                'negative_score': negative_count,
                'analysis': f"Text contains {word_count} words with {sentiment} sentiment."
            }
        except Exception as e:
            print(f"Error analyzing text: {e}")
            return {'error': str(e)}

# Global agent instance
agent = SimpleMarketNewsAgent()

async def main():
    """Main execution function for testing"""
    print("🚀 Starting Simple Worldmine Backend...")
    
    try:
        # Test basic functionality
        news = await agent.get_basic_news()
        print(f"✅ Found {len(news)} news items")
        
        # Test simple analysis
        test_text = "The market is showing positive growth today"
        analysis = await agent.analyze_simple_text(test_text)
        print(f"✅ Analysis completed: {analysis}")
        
        print("🎉 Simple backend test completed successfully!")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
