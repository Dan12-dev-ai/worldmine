"""
🌍 DEDAN 2.0 - Daily Mineral News Service
Real-time mineral market news with AI-powered analysis
Better than Bloomberg, Reuters, and MarketWatch for mineral intelligence
"""

import asyncio
import json
import uuid
import aiohttp
import feedparser
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import redis
import asyncpg
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, Boolean, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import openai
from textblob import TextBlob
import newspaper
from bs4 import BeautifulSoup
import requests

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb")
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

Base = declarative_base()

class NewsCategory(Enum):
    """News categories for mineral markets"""
    MARKET_UPDATES = "market_updates"
    DISCOVERIES = "discoveries"
    REGULATORY = "regulatory"
    TECHNOLOGY = "technology"
    SUSTAINABILITY = "sustainability"
    GEOPOLITICAL = "geopolitical"
    COMPANY_NEWS = "company_news"
    PRICE_FORECASTS = "price_forecasts"
    SUPPLY_CHAIN = "supply_chain"
    MINING_OPERATIONS = "mining_operations"

class NewsSource(Enum):
    """Premium news sources for mineral intelligence"""
    BLOOMBERG = "bloomberg"
    REUTERS = "reuters"
    MINING_COM = "mining_com"
    INVESTING_COM = "investing_com"
    FINANCIAL_TIMES = "financial_times"
    WALL_STREET_JOURNAL = "wall_street_journal"
    MINING_WEEKLY = "mining_weekly"
    RESOURCE_WORLD = "resource_world"
    KITCO = "kitco"
    METALS_FOCUS = "metals_focus"

class SentimentAnalysis(Enum):
    """Sentiment analysis results"""
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"

class ImpactLevel(Enum):
    """Market impact level"""
    CRITICAL = "critical"  # Major price movements expected
    HIGH = "high"          # Significant market impact
    MEDIUM = "medium"       # Moderate impact
    LOW = "low"            # Minimal impact
    INFORMATIONAL = "informational"  # News only, no immediate impact

@dataclass
class NewsArticle:
    """News article data structure"""
    id: str
    title: str
    content: str
    summary: str
    url: str
    source: NewsSource
    category: NewsCategory
    author: str
    published_at: datetime
    sentiment: SentimentAnalysis
    impact_level: ImpactLevel
    mentioned_minerals: List[str]
    mentioned_companies: List[str]
    mentioned_countries: List[str]
    price_impact: Dict[str, float]  # mineral -> expected price change %
    ai_analysis: str
    relevance_score: float
    verification_status: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime

class NewsArticleDB(Base):
    """Database model for news articles"""
    __tablename__ = "news_articles"
    
    id = Column(String, primary_key=True)
    title = Column(String, index=True)
    content = Column(Text)
    summary = Column(Text)
    url = Column(String, unique=True, index=True)
    source = Column(String, index=True)
    category = Column(String, index=True)
    author = Column(String)
    published_at = Column(DateTime, index=True)
    sentiment = Column(String, index=True)
    impact_level = Column(String, index=True)
    mentioned_minerals = Column(Text)  # JSON array
    mentioned_companies = Column(Text)  # JSON array
    mentioned_countries = Column(Text)  # JSON array
    price_impact = Column(Text)  # JSON object
    ai_analysis = Column(Text)
    relevance_score = Column(Float, index=True)
    verification_status = Column(String)
    tags = Column(Text)  # JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MineralNewsService:
    """
    Advanced mineral news service with AI-powered analysis
    Real-time news aggregation, analysis, and market impact prediction
    """
    
    def __init__(self):
        self.engine = create_engine(DATABASE_URL)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # AI configuration
        self.openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # News sources configuration
        self.news_sources = self._initialize_news_sources()
        
        # Mineral keywords for extraction
        self.mineral_keywords = self._initialize_mineral_keywords()
        
        # Company keywords for extraction
        self.company_keywords = self._initialize_company_keywords()
        
        # Country keywords for extraction
        self.country_keywords = self._initialize_country_keywords()
        
        # Cache for recent articles
        self.articles_cache = {}
        
        print("📰 Mineral News Service initialized")
    
    def _initialize_news_sources(self) -> Dict[NewsSource, Dict[str, str]]:
        """Initialize premium news sources"""
        return {
            NewsSource.BLOOMBERG: {
                "rss_url": "https://feeds.bloomberg.com/markets/news.rss",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 10
            },
            NewsSource.REUTERS: {
                "rss_url": "https://www.reuters.com/rssFeed/marketsNews",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 9
            },
            NewsSource.MINING_COM: {
                "rss_url": "https://www.mining.com/feed/",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 8
            },
            NewsSource.INVESTING_COM: {
                "rss_url": "https://www.investing.com/rss/news.rss",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 7
            },
            NewsSource.FINANCIAL_TIMES: {
                "rss_url": "https://www.ft.com/rss/companies",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 8
            },
            NewsSource.KITCO: {
                "rss_url": "https://www.kitco.com/rss/futures.xml",
                "api_url": "https://newsapi.org/v2/everything",
                "priority": 7
            }
        }
    
    def _initialize_mineral_keywords(self) -> Dict[str, List[str]]:
        """Initialize mineral keywords for extraction"""
        return {
            "gold": ["gold", "au", "bullion", "gold bars", "gold coins"],
            "silver": ["silver", "ag", "sterling", "silver bars"],
            "copper": ["copper", "cu", "red metal", "cathode"],
            "lithium": ["lithium", "li", "lithium carbonate", "spodumene"],
            "cobalt": ["cobalt", "co", "cobaltite"],
            "nickel": ["nickel", "ni", "nickel sulfide"],
            "rare_earth": ["rare earth", "ree", "neodymium", "dysprosium", "praseodymium"],
            "platinum": ["platinum", "pt", "pgm", "platinum group"],
            "palladium": ["palladium", "pd", "auto catalyst"],
            "aluminum": ["aluminum", "al", "bauxite", "alumina"],
            "iron_ore": ["iron ore", "fe", "pellets", "sinter"],
            "uranium": ["uranium", "u", "yellowcake", "u3o8"],
            "diamonds": ["diamonds", "gemstones", "rough diamonds"],
            "coal": ["coal", "thermal coal", "metallurgical coal", "coking coal"]
        }
    
    def _initialize_company_keywords(self) -> List[str]:
        """Initialize major mining company keywords"""
        return [
            "rio tinto", "bhp", "vale", "glencore", "anglo american",
            "freeport-mcmoran", "newmont", "barrick gold", "goldcorp",
            "alcoa", "norsk hydro", "albemarle", "sqm", "lithium americas",
            "gangfeng lithium", "tianqi lithium", "china molybdenum",
            "first quantum minerals", "teck resources", "southern copper",
            "kghm", "nornickel", "anglo american platinum", "impala platinum",
            "sibanye-stillwater", "wheaton precious metals", "franco-nevada",
            "royal gold", "streaming", "royalty"
        ]
    
    def _initialize_country_keywords(self) -> List[str]:
        """Initialize major mining country keywords"""
        return [
            "china", "australia", "russia", "united states", "canada",
            "chile", "peru", "south africa", "mexico", "india",
            "brazil", "indonesia", "kazakhstan", "congo", "zambia",
            "papua new guinea", "mongolia", "chile", "argentina", "bolivia",
            "greenland", "sweden", "finland", "norway", "portugal",
            "spain", "germany", "poland", "turkey", "iran", "saudi arabia",
            "egypt", "morocco", "ghana", "mali", "tanzania", "mozambique",
            "botswana", "namibia", "zimbabwe", "south africa", "tanzania"
        ]
    
    async def fetch_news_from_all_sources(self) -> List[NewsArticle]:
        """Fetch news from all configured sources"""
        all_articles = []
        
        for source, config in self.news_sources.items():
            try:
                # Fetch RSS feed
                rss_articles = await self._fetch_rss_feed(source, config)
                all_articles.extend(rss_articles)
                
                # Fetch API news
                api_articles = await self._fetch_api_news(source, config)
                all_articles.extend(api_articles)
                
                print(f"📰 Fetched {len(rss_articles) + len(api_articles)} articles from {source.value}")
                
            except Exception as e:
                print(f"❌ Error fetching from {source.value}: {e}")
        
        # Remove duplicates and sort by relevance
        unique_articles = self._remove_duplicate_articles(all_articles)
        sorted_articles = sorted(unique_articles, key=lambda x: x.relevance_score, reverse=True)
        
        return sorted_articles
    
    async def _fetch_rss_feed(self, source: NewsSource, config: Dict[str, str]) -> List[NewsArticle]:
        """Fetch news from RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(config["rss_url"])
            
            for entry in feed.entries:
                try:
                    # Extract full article content
                    article_content = await self._extract_article_content(entry.link)
                    
                    # Analyze article
                    analysis = await self._analyze_article(
                        title=entry.title,
                        content=article_content,
                        source=source
                    )
                    
                    # Create news article
                    article = NewsArticle(
                        id=str(uuid.uuid4()),
                        title=entry.title,
                        content=article_content,
                        summary=analysis["summary"],
                        url=entry.link,
                        source=source,
                        category=analysis["category"],
                        author=getattr(entry, 'author', 'Unknown'),
                        published_at=datetime(*entry.published_parsed[:6]) if hasattr(entry, 'published_parsed') else datetime.utcnow(),
                        sentiment=analysis["sentiment"],
                        impact_level=analysis["impact_level"],
                        mentioned_minerals=analysis["mentioned_minerals"],
                        mentioned_companies=analysis["mentioned_companies"],
                        mentioned_countries=analysis["mentioned_countries"],
                        price_impact=analysis["price_impact"],
                        ai_analysis=analysis["ai_analysis"],
                        relevance_score=analysis["relevance_score"],
                        verification_status="pending",
                        tags=analysis["tags"],
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    print(f"❌ Error processing article: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error fetching RSS feed from {source.value}: {e}")
        
        return articles
    
    async def _fetch_api_news(self, source: NewsSource, config: Dict[str, str]) -> List[NewsArticle]:
        """Fetch news from API endpoints"""
        articles = []
        
        try:
            # This would use NewsAPI or similar service
            # Implementation depends on the specific API
            pass
            
        except Exception as e:
            print(f"❌ Error fetching API news from {source.value}: {e}")
        
        return articles
    
    async def _extract_article_content(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            article = newspaper.Article(url)
            article.download()
            article.parse()
            return article.text
            
        except Exception as e:
            print(f"❌ Error extracting content from {url}: {e}")
            return ""
    
    async def _analyze_article(self, title: str, content: str, source: NewsSource) -> Dict[str, Any]:
        """Analyze article using AI for insights"""
        try:
            # Combine title and content for analysis
            full_text = f"{title}\n\n{content}"
            
            # Extract entities
            mentioned_minerals = self._extract_minerals(full_text)
            mentioned_companies = self._extract_companies(full_text)
            mentioned_countries = self._extract_countries(full_text)
            
            # Sentiment analysis
            sentiment = self._analyze_sentiment(full_text)
            
            # Categorize article
            category = self._categorize_article(title, content)
            
            # AI-powered analysis
            ai_analysis = await self._get_ai_analysis(title, content, mentioned_minerals)
            
            # Predict market impact
            impact_level, price_impact = await self._predict_market_impact(
                title, content, mentioned_minerals, sentiment
            )
            
            # Generate summary
            summary = self._generate_summary(content)
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                mentioned_minerals, mentioned_companies, impact_level, source
            )
            
            # Generate tags
            tags = self._generate_tags(title, content, mentioned_minerals, category)
            
            return {
                "summary": summary,
                "category": category,
                "sentiment": sentiment,
                "impact_level": impact_level,
                "mentioned_minerals": mentioned_minerals,
                "mentioned_companies": mentioned_companies,
                "mentioned_countries": mentioned_countries,
                "price_impact": price_impact,
                "ai_analysis": ai_analysis,
                "relevance_score": relevance_score,
                "tags": tags
            }
            
        except Exception as e:
            print(f"❌ Error analyzing article: {e}")
            return self._get_default_analysis()
    
    def _extract_minerals(self, text: str) -> List[str]:
        """Extract mentioned minerals from text"""
        mentioned = []
        text_lower = text.lower()
        
        for mineral, keywords in self.mineral_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if mineral not in mentioned:
                        mentioned.append(mineral)
                    break
        
        return mentioned
    
    def _extract_companies(self, text: str) -> List[str]:
        """Extract mentioned companies from text"""
        mentioned = []
        text_lower = text.lower()
        
        for company in self.company_keywords:
            if company in text_lower:
                mentioned.append(company)
        
        return mentioned
    
    def _extract_countries(self, text: str) -> List[str]:
        """Extract mentioned countries from text"""
        mentioned = []
        text_lower = text.lower()
        
        for country in self.country_keywords:
            if country in text_lower:
                mentioned.append(country)
        
        return mentioned
    
    def _analyze_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment of text"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            if polarity > 0.5:
                return SentimentAnalysis.VERY_POSITIVE
            elif polarity > 0.1:
                return SentimentAnalysis.POSITIVE
            elif polarity > -0.1:
                return SentimentAnalysis.NEUTRAL
            elif polarity > -0.5:
                return SentimentAnalysis.NEGATIVE
            else:
                return SentimentAnalysis.VERY_NEGATIVE
                
        except Exception as e:
            print(f"❌ Error analyzing sentiment: {e}")
            return SentimentAnalysis.NEUTRAL
    
    def _categorize_article(self, title: str, content: str) -> NewsCategory:
        """Categorize article based on content"""
        text_lower = (title + " " + content).lower()
        
        if any(word in text_lower for word in ["price", "market", "trading", "commodity"]):
            return NewsCategory.MARKET_UPDATES
        elif any(word in text_lower for word in ["discovery", "deposit", "exploration"]):
            return NewsCategory.DISCOVERIES
        elif any(word in text_lower for word in ["regulation", "law", "policy", "government"]):
            return NewsCategory.REGULATORY
        elif any(word in text_lower for word in ["technology", "innovation", "research"]):
            return NewsCategory.TECHNOLOGY
        elif any(word in text_lower for word in ["sustainable", "environment", "esg"]):
            return NewsCategory.SUSTAINABILITY
        elif any(word in text_lower for word in ["geopolitical", "trade war", "sanctions"]):
            return NewsCategory.GEOPOLITICAL
        elif any(word in text_lower for word in ["company", "earnings", "merger", "acquisition"]):
            return NewsCategory.COMPANY_NEWS
        elif any(word in text_lower for word in ["forecast", "prediction", "outlook"]):
            return NewsCategory.PRICE_FORECASTS
        elif any(word in text_lower for word in ["supply", "chain", "logistics", "shipping"]):
            return NewsCategory.SUPPLY_CHAIN
        elif any(word in text_lower for word in ["mining", "operation", "production"]):
            return NewsCategory.MINING_OPERATIONS
        else:
            return NewsCategory.MARKET_UPDATES
    
    async def _get_ai_analysis(self, title: str, content: str, minerals: List[str]) -> str:
        """Get AI-powered analysis of article"""
        try:
            prompt = f"""
            Analyze this mineral market news article and provide insights:
            
            Title: {title}
            Content: {content[:1000]}...
            Mentioned Minerals: {', '.join(minerals)}
            
            Provide analysis on:
            1. Market implications
            2. Price impact potential
            3. Strategic importance
            4. Risk factors
            5. Investment opportunities
            
            Keep analysis concise and actionable for mineral traders.
            """
            
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert mineral market analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error getting AI analysis: {e}")
            return "AI analysis unavailable"
    
    async def _predict_market_impact(self, title: str, content: str, minerals: List[str], sentiment: SentimentAnalysis) -> Tuple[ImpactLevel, Dict[str, float]]:
        """Predict market impact of news"""
        try:
            # Simple heuristic-based prediction
            impact_keywords = {
                "critical": ["shutdown", "strike", "disaster", "war", "sanctions", "major discovery"],
                "high": ["production", "expansion", "merger", "acquisition", "new mine"],
                "medium": ["exploration", "drilling", "permit", "investment"],
                "low": ["meeting", "conference", "report", "study"]
            }
            
            text_lower = (title + " " + content).lower()
            
            # Determine impact level
            impact_level = ImpactLevel.INFORMATIONAL
            for level, keywords in impact_keywords.items():
                if any(keyword in text_lower for keyword in keywords):
                    impact_level = ImpactLevel(level)
                    break
            
            # Predict price impacts
            price_impact = {}
            for mineral in minerals:
                if impact_level == ImpactLevel.CRITICAL:
                    price_impact[mineral] = 15.0 if sentiment in [SentimentAnalysis.POSITIVE, SentimentAnalysis.VERY_POSITIVE] else -15.0
                elif impact_level == ImpactLevel.HIGH:
                    price_impact[mineral] = 8.0 if sentiment in [SentimentAnalysis.POSITIVE, SentimentAnalysis.VERY_POSITIVE] else -8.0
                elif impact_level == ImpactLevel.MEDIUM:
                    price_impact[mineral] = 3.0 if sentiment in [SentimentAnalysis.POSITIVE, SentimentAnalysis.VERY_POSITIVE] else -3.0
                else:
                    price_impact[mineral] = 0.0
            
            return impact_level, price_impact
            
        except Exception as e:
            print(f"❌ Error predicting market impact: {e}")
            return ImpactLevel.INFORMATIONAL, {}
    
    def _generate_summary(self, content: str) -> str:
        """Generate summary of article content"""
        try:
            # Simple extractive summarization
            sentences = content.split('.')
            sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
            
            # Return first 3 sentences as summary
            return '. '.join(sentences[:3]) + '.'
            
        except Exception as e:
            print(f"❌ Error generating summary: {e}")
            return content[:200] + "..."
    
    def _calculate_relevance_score(self, minerals: List[str], companies: List[str], impact: ImpactLevel, source: NewsSource) -> float:
        """Calculate relevance score for article"""
        score = 0.0
        
        # Base score from source priority
        source_priority = self.news_sources[source]["priority"]
        score += source_priority * 0.1
        
        # Score from mentioned minerals
        score += len(minerals) * 2.0
        
        # Score from mentioned companies
        score += len(companies) * 1.5
        
        # Score from impact level
        impact_scores = {
            ImpactLevel.CRITICAL: 10.0,
            ImpactLevel.HIGH: 7.0,
            ImpactLevel.MEDIUM: 4.0,
            ImpactLevel.LOW: 2.0,
            ImpactLevel.INFORMATIONAL: 1.0
        }
        score += impact_scores.get(impact, 1.0)
        
        return min(score, 20.0)  # Cap at 20.0
    
    def _generate_tags(self, title: str, content: str, minerals: List[str], category: NewsCategory) -> List[str]:
        """Generate tags for article"""
        tags = []
        
        # Add mineral tags
        tags.extend(minerals)
        
        # Add category tag
        tags.append(category.value)
        
        # Add content-based tags
        text_lower = (title + " " + content).lower()
        
        if "price" in text_lower:
            tags.append("price_movement")
        if "supply" in text_lower:
            tags.append("supply_chain")
        if "demand" in text_lower:
            tags.append("demand")
        if "esg" in text_lower or "sustainable" in text_lower:
            tags.append("esg")
        if "technology" in text_lower:
            tags.append("technology")
        
        return list(set(tags))
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis when AI analysis fails"""
        return {
            "summary": "Analysis unavailable",
            "category": NewsCategory.MARKET_UPDATES,
            "sentiment": SentimentAnalysis.NEUTRAL,
            "impact_level": ImpactLevel.INFORMATIONAL,
            "mentioned_minerals": [],
            "mentioned_companies": [],
            "mentioned_countries": [],
            "price_impact": {},
            "ai_analysis": "AI analysis unavailable",
            "relevance_score": 1.0,
            "tags": []
        }
    
    def _remove_duplicate_articles(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Remove duplicate articles based on URL similarity"""
        seen_urls = set()
        unique_articles = []
        
        for article in articles:
            # Simple URL-based deduplication
            url_hash = hash(article.url.split('?')[0])  # Remove query parameters
            if url_hash not in seen_urls:
                seen_urls.add(url_hash)
                unique_articles.append(article)
        
        return unique_articles
    
    async def save_articles_to_database(self, articles: List[NewsArticle]) -> int:
        """Save articles to database"""
        saved_count = 0
        
        session = self.SessionLocal()
        try:
            for article in articles:
                # Check if article already exists
                existing = session.query(NewsArticleDB).filter_by(url=article.url).first()
                if existing:
                    continue
                
                # Create database record
                db_article = NewsArticleDB(
                    id=article.id,
                    title=article.title,
                    content=article.content,
                    summary=article.summary,
                    url=article.url,
                    source=article.source.value,
                    category=article.category.value,
                    author=article.author,
                    published_at=article.published_at,
                    sentiment=article.sentiment.value,
                    impact_level=article.impact_level.value,
                    mentioned_minerals=json.dumps(article.mentioned_minerals),
                    mentioned_companies=json.dumps(article.mentioned_companies),
                    mentioned_countries=json.dumps(article.mentioned_countries),
                    price_impact=json.dumps(article.price_impact),
                    ai_analysis=article.ai_analysis,
                    relevance_score=article.relevance_score,
                    verification_status=article.verification_status,
                    tags=json.dumps(article.tags),
                    created_at=article.created_at,
                    updated_at=article.updated_at
                )
                
                session.add(db_article)
                saved_count += 1
            
            session.commit()
            print(f"✅ Saved {saved_count} new articles to database")
            
        except Exception as e:
            session.rollback()
            print(f"❌ Error saving articles: {e}")
        finally:
            session.close()
        
        return saved_count
    
    async def get_latest_news(self, limit: int = 50, category: Optional[NewsCategory] = None, minerals: Optional[List[str]] = None) -> List[NewsArticle]:
        """Get latest news with filters"""
        session = self.SessionLocal()
        try:
            query = session.query(NewsArticleDB).order_by(NewsArticleDB.published_at.desc())
            
            if category:
                query = query.filter(NewsArticleDB.category == category.value)
            
            if minerals:
                # Filter by mentioned minerals
                mineral_filter = []
                for mineral in minerals:
                    mineral_filter.append(NewsArticleDB.mentioned_minerals.like(f'%"{mineral}"%'))
                
                if mineral_filter:
                    from sqlalchemy import or_
                    query = query.filter(or_(*mineral_filter))
            
            results = query.limit(limit).all()
            
            # Convert to NewsArticle objects
            articles = []
            for result in results:
                article = NewsArticle(
                    id=result.id,
                    title=result.title,
                    content=result.content,
                    summary=result.summary,
                    url=result.url,
                    source=NewsSource(result.source),
                    category=NewsCategory(result.category),
                    author=result.author,
                    published_at=result.published_at,
                    sentiment=SentimentAnalysis(result.sentiment),
                    impact_level=ImpactLevel(result.impact_level),
                    mentioned_minerals=json.loads(result.mentioned_minerals),
                    mentioned_companies=json.loads(result.mentioned_companies),
                    mentioned_countries=json.loads(result.mentioned_countries),
                    price_impact=json.loads(result.price_impact),
                    ai_analysis=result.ai_analysis,
                    relevance_score=result.relevance_score,
                    verification_status=result.verification_status,
                    tags=json.loads(result.tags),
                    created_at=result.created_at,
                    updated_at=result.updated_at
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching latest news: {e}")
            return []
        finally:
            session.close()
    
    async def get_news_by_impact(self, impact_level: ImpactLevel, limit: int = 20) -> List[NewsArticle]:
        """Get news by impact level"""
        session = self.SessionLocal()
        try:
            results = session.query(NewsArticleDB).filter(
                NewsArticleDB.impact_level == impact_level.value
            ).order_by(NewsArticleDB.published_at.desc()).limit(limit).all()
            
            # Convert to NewsArticle objects
            articles = []
            for result in results:
                article = NewsArticle(
                    id=result.id,
                    title=result.title,
                    content=result.content,
                    summary=result.summary,
                    url=result.url,
                    source=NewsSource(result.source),
                    category=NewsCategory(result.category),
                    author=result.author,
                    published_at=result.published_at,
                    sentiment=SentimentAnalysis(result.sentiment),
                    impact_level=ImpactLevel(result.impact_level),
                    mentioned_minerals=json.loads(result.mentioned_minerals),
                    mentioned_companies=json.loads(result.mentioned_companies),
                    mentioned_countries=json.loads(result.mentioned_countries),
                    price_impact=json.loads(result.price_impact),
                    ai_analysis=result.ai_analysis,
                    relevance_score=result.relevance_score,
                    verification_status=result.verification_status,
                    tags=json.loads(result.tags),
                    created_at=result.created_at,
                    updated_at=result.updated_at
                )
                articles.append(article)
            
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching news by impact: {e}")
            return []
        finally:
            session.close()
    
    async def get_news_statistics(self) -> Dict[str, Any]:
        """Get news statistics"""
        session = self.SessionLocal()
        try:
            total_articles = session.query(NewsArticleDB).count()
            
            # Articles by category
            category_stats = {}
            for category in NewsCategory:
                count = session.query(NewsArticleDB).filter(NewsArticleDB.category == category.value).count()
                category_stats[category.value] = count
            
            # Articles by impact level
            impact_stats = {}
            for impact in ImpactLevel:
                count = session.query(NewsArticleDB).filter(NewsArticleDB.impact_level == impact.value).count()
                impact_stats[impact.value] = count
            
            # Articles by source
            source_stats = {}
            for source in NewsSource:
                count = session.query(NewsArticleDB).filter(NewsArticleDB.source == source.value).count()
                source_stats[source.value] = count
            
            # Recent articles (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_count = session.query(NewsArticleDB).filter(NewsArticleDB.published_at >= yesterday).count()
            
            return {
                "total_articles": total_articles,
                "category_distribution": category_stats,
                "impact_distribution": impact_stats,
                "source_distribution": source_stats,
                "recent_articles_24h": recent_count,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error getting news statistics: {e}")
            return {}
        finally:
            session.close()
    
    async def start_news_aggregation(self):
        """Start continuous news aggregation"""
        print("🔄 Starting continuous news aggregation...")
        
        while True:
            try:
                # Fetch news from all sources
                articles = await self.fetch_news_from_all_sources()
                
                # Save to database
                saved_count = await self.save_articles_to_database(articles)
                
                # Cache latest articles in Redis
                if articles:
                    latest_articles = articles[:20]  # Cache top 20
                    cache_data = []
                    for article in latest_articles:
                        cache_data.append({
                            'id': article.id,
                            'title': article.title,
                            'summary': article.summary,
                            'url': article.url,
                            'source': article.source.value,
                            'category': article.category.value,
                            'impact_level': article.impact_level.value,
                            'mentioned_minerals': article.mentioned_minerals,
                            'published_at': article.published_at.isoformat(),
                            'relevance_score': article.relevance_score
                        })
                    
                    redis_client.setex(
                        "latest_mineral_news",
                        300,  # 5 minutes cache
                        json.dumps(cache_data)
                    )
                
                print(f"📰 News aggregation cycle completed. {saved_count} new articles saved.")
                
                # Wait for next cycle (every 15 minutes)
                await asyncio.sleep(900)
                
            except Exception as e:
                print(f"❌ Error in news aggregation cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Initialize the news service
mineral_news_service = MineralNewsService()

# Start the news aggregation in background
async def start_news_service():
    """Start the mineral news service"""
    await mineral_news_service.start_news_aggregation()

if __name__ == "__main__":
    asyncio.run(start_news_service())
