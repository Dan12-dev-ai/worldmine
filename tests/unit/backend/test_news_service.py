"""
Unit tests for mineral news service
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../backend'))

from services.mineral_news_service import MineralNewsService, NewsCategory, SentimentAnalysis

class TestMineralNewsService:
    """Test suite for MineralNewsService class"""
    
    @pytest.fixture
    def news_service(self):
        """Create test news service instance"""
        with patch('services.mineral_news_service.create_engine'), \
             patch('services.mineral_news_service.redis.Redis'), \
             patch('services.mineral_news_service.openai.OpenAI'):
            return MineralNewsService()
    
    def test_initialization(self, news_service):
        """Test service initialization"""
        assert news_service is not None
        assert hasattr(news_service, 'news_sources')
        assert hasattr(news_service, 'mineral_keywords')
    
    def test_news_categories(self, news_service):
        """Test news categories enum"""
        categories = list(NewsCategory)
        assert len(categories) >= 8
        assert NewsCategory.MARKET_UPDATES in categories
        assert NewsCategory.DISCOVERIES in categories
    
    def test_sentiment_analysis(self, news_service):
        """Test sentiment analysis enum"""
        sentiments = list(SentimentAnalysis)
        assert len(sentiments) >= 5
        assert SentimentAnalysis.POSITIVE in sentiments
        assert SentimentAnalysis.NEGATIVE in sentiments
    
    def test_extract_minerals(self, news_service):
        """Test mineral extraction from text"""
        text = "Gold prices surged while lithium demand increased"
        minerals = news_service._extract_minerals(text)
        
        assert isinstance(minerals, list)
        # Should find gold and lithium
        assert any('gold' in m.lower() for m in minerals)
        assert any('lithium' in m.lower() for m in minerals)
    
    def test_extract_companies(self, news_service):
        """Test company extraction from text"""
        text = "Rio Tinto and BHP announced new mining operations"
        companies = news_service._extract_companies(text)
        
        assert isinstance(companies, list)
        # Should find the companies
        assert any('rio tinto' in c.lower() for c in companies)
        assert any('bhp' in c.lower() for c in companies)
    
    def test_analyze_sentiment(self, news_service):
        """Test sentiment analysis"""
        # Positive text
        positive_text = "Gold prices reached new highs today"
        sentiment = news_service._analyze_sentiment(positive_text)
        assert sentiment in [SentimentAnalysis.POSITIVE, SentimentAnalysis.VERY_POSITIVE]
        
        # Negative text
        negative_text = "Mining operations faced significant challenges"
        sentiment = news_service._analyze_sentiment(negative_text)
        assert sentiment in [SentimentAnalysis.NEGATIVE, SentimentAnalysis.VERY_NEGATIVE]
    
    def test_categorize_article(self, news_service):
        """Test article categorization"""
        # Market update
        market_text = "Prices surged in trading today with high volume"
        category = news_service._categorize_article("Market Update", market_text)
        assert category == NewsCategory.MARKET_UPDATES
        
        # Discovery
        discovery_text = "New gold deposit discovered in Australia"
        category = news_service._categorize_article("Gold Discovery", discovery_text)
        assert category == NewsCategory.DISCOVERIES

if __name__ == "__main__":
    pytest.main([__file__])
