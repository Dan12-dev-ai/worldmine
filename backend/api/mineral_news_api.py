"""
🌍 DEDAN 2.0 - Mineral News API Endpoints
RESTful API for mineral market news with AI-powered analysis
"""

from fastapi import APIRouter, HTTPException, Query, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel
import asyncio

from ..services.mineral_news_service import (
    mineral_news_service, 
    NewsArticle, 
    NewsCategory, 
    SentimentAnalysis, 
    ImpactLevel,
    NewsSource
)

# API Router
router = APIRouter(prefix="/api/v2/mineral-news", tags=["mineral-news"])

# Pydantic models for API responses
class NewsArticleResponse(BaseModel):
    id: str
    title: str
    summary: str
    url: str
    source: str
    category: str
    author: str
    published_at: str
    sentiment: str
    impact_level: str
    mentioned_minerals: List[str]
    mentioned_companies: List[str]
    mentioned_countries: List[str]
    price_impact: Dict[str, float]
    ai_analysis: str
    relevance_score: float
    verification_status: str
    tags: List[str]
    created_at: str
    updated_at: str

class NewsStatisticsResponse(BaseModel):
    total_articles: int
    category_distribution: Dict[str, int]
    impact_distribution: Dict[str, int]
    source_distribution: Dict[str, int]
    recent_articles_24h: int
    last_updated: str

class NewsFilters(BaseModel):
    category: Optional[str] = None
    sentiment: Optional[str] = None
    impact_level: Optional[str] = None
    source: Optional[str] = None
    minerals: Optional[List[str]] = []
    time_range: Optional[str] = "24h"
    verified_only: Optional[bool] = False

def convert_article_to_response(article: NewsArticle) -> NewsArticleResponse:
    """Convert NewsArticle to response model"""
    return NewsArticleResponse(
        id=article.id,
        title=article.title,
        summary=article.summary,
        url=article.url,
        source=article.source.value,
        category=article.category.value,
        author=article.author,
        published_at=article.published_at.isoformat(),
        sentiment=article.sentiment.value,
        impact_level=article.impact_level.value,
        mentioned_minerals=article.mentioned_minerals,
        mentioned_companies=article.mentioned_companies,
        mentioned_countries=article.mentioned_countries,
        price_impact=article.price_impact,
        ai_analysis=article.ai_analysis,
        relevance_score=article.relevance_score,
        verification_status=article.verification_status,
        tags=article.tags,
        created_at=article.created_at.isoformat(),
        updated_at=article.updated_at.isoformat()
    )

@router.get("/", response_model=List[NewsArticleResponse])
async def get_latest_news(
    limit: int = Query(50, ge=1, le=200),
    category: Optional[str] = Query(None),
    minerals: Optional[List[str]] = Query(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Get latest mineral news articles
    - **limit**: Number of articles to return (1-200)
    - **category**: Filter by news category
    - **minerals**: Filter by mentioned minerals
    """
    try:
        # Convert category string to enum
        category_enum = None
        if category:
            try:
                category_enum = NewsCategory(category)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
        
        # Get articles from service
        articles = await mineral_news_service.get_latest_news(
            limit=limit,
            category=category_enum,
            minerals=minerals or []
        )
        
        # Convert to response format
        response_articles = [convert_article_to_response(article) for article in articles]
        
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching news: {str(e)}")

@router.get("/critical", response_model=List[NewsArticleResponse])
async def get_critical_news(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get critical impact news articles
    - **limit**: Number of articles to return (1-100)
    """
    try:
        articles = await mineral_news_service.get_news_by_impact(
            impact_level=ImpactLevel.CRITICAL,
            limit=limit
        )
        
        response_articles = [convert_article_to_response(article) for article in articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching critical news: {str(e)}")

@router.get("/high-impact", response_model=List[NewsArticleResponse])
async def get_high_impact_news(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get high impact news articles
    - **limit**: Number of articles to return (1-100)
    """
    try:
        articles = await mineral_news_service.get_news_by_impact(
            impact_level=ImpactLevel.HIGH,
            limit=limit
        )
        
        response_articles = [convert_article_to_response(article) for article in articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching high impact news: {str(e)}")

@router.get("/statistics", response_model=NewsStatisticsResponse)
async def get_news_statistics():
    """
    Get comprehensive news statistics
    """
    try:
        stats = await mineral_news_service.get_news_statistics()
        return NewsStatisticsResponse(**stats)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@router.get("/categories")
async def get_news_categories():
    """
    Get all available news categories
    """
    try:
        categories = [
            {
                "value": category.value,
                "label": category.value.replace("_", " ").title(),
                "description": f"News about {category.value.replace('_', ' ')}"
            }
            for category in NewsCategory
        ]
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.get("/sources")
async def get_news_sources():
    """
    Get all available news sources
    """
    try:
        sources = [
            {
                "value": source.value,
                "label": source.value.replace("_", " ").title(),
                "description": f"News from {source.value.replace('_', ' ')}"
            }
            for source in NewsSource
        ]
        
        return {"sources": sources}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")

@router.get("/search", response_model=List[NewsArticleResponse])
async def search_news(
    query: str = Query(..., min_length=2, max_length=100),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = Query(None),
    sentiment: Optional[str] = Query(None),
    impact_level: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    time_range: Optional[str] = Query("24h"),
    verified_only: Optional[bool] = Query(False)
):
    """
    Search news articles with advanced filters
    - **query**: Search query (2-100 characters)
    - **limit**: Number of results to return (1-100)
    - **category**: Filter by category
    - **sentiment**: Filter by sentiment
    - **impact_level**: Filter by impact level
    - **source**: Filter by source
    - **time_range**: Time range (1h, 24h, 7d, 30d)
    - **verified_only**: Only show verified articles
    """
    try:
        # This would implement search functionality
        # For now, return latest news as placeholder
        articles = await mineral_news_service.get_latest_news(limit=limit)
        
        # Filter by search query (simple implementation)
        filtered_articles = []
        for article in articles:
            if (query.lower() in article.title.lower() or 
                query.lower() in article.summary.lower() or
                query.lower() in article.content.lower()):
                filtered_articles.append(article)
        
        response_articles = [convert_article_to_response(article) for article in filtered_articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching news: {str(e)}")

@router.get("/mineral/{mineral_name}", response_model=List[NewsArticleResponse])
async def get_news_by_mineral(
    mineral_name: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get news articles mentioning a specific mineral
    - **mineral_name**: Name of the mineral
    - **limit**: Number of articles to return (1-100)
    """
    try:
        articles = await mineral_news_service.get_latest_news(
            limit=limit,
            minerals=[mineral_name.lower()]
        )
        
        response_articles = [convert_article_to_response(article) for article in articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching mineral news: {str(e)}")

@router.get("/company/{company_name}", response_model=List[NewsArticleResponse])
async def get_news_by_company(
    company_name: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get news articles mentioning a specific company
    - **company_name**: Name of the company
    - **limit**: Number of articles to return (1-100)
    """
    try:
        # Get all articles and filter by company
        all_articles = await mineral_news_service.get_latest_news(limit=200)
        
        filtered_articles = []
        for article in all_articles:
            if any(company_name.lower() in company.lower() for company in article.mentioned_companies):
                filtered_articles.append(article)
        
        # Limit results
        filtered_articles = filtered_articles[:limit]
        
        response_articles = [convert_article_to_response(article) for article in filtered_articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching company news: {str(e)}")

@router.get("/country/{country_name}", response_model=List[NewsArticleResponse])
async def get_news_by_country(
    country_name: str,
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get news articles mentioning a specific country
    - **country_name**: Name of the country
    - **limit**: Number of articles to return (1-100)
    """
    try:
        # Get all articles and filter by country
        all_articles = await mineral_news_service.get_latest_news(limit=200)
        
        filtered_articles = []
        for article in all_articles:
            if any(country_name.lower() in country.lower() for country in article.mentioned_countries):
                filtered_articles.append(article)
        
        # Limit results
        filtered_articles = filtered_articles[:limit]
        
        response_articles = [convert_article_to_response(article) for article in filtered_articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching country news: {str(e)}")

@router.get("/trending", response_model=List[NewsArticleResponse])
async def get_trending_news(
    limit: int = Query(10, ge=1, le=50),
    time_range: Optional[str] = Query("24h")
):
    """
    Get trending news articles
    - **limit**: Number of articles to return (1-50)
    - **time_range**: Time range for trending (1h, 24h, 7d)
    """
    try:
        # Get high impact and critical articles
        critical_articles = await mineral_news_service.get_news_by_impact(
            impact_level=ImpactLevel.CRITICAL,
            limit=limit // 2
        )
        
        high_impact_articles = await mineral_news_service.get_news_by_impact(
            impact_level=ImpactLevel.HIGH,
            limit=limit // 2
        )
        
        # Combine and sort by relevance
        all_articles = critical_articles + high_impact_articles
        all_articles.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Limit results
        trending_articles = all_articles[:limit]
        
        response_articles = [convert_article_to_response(article) for article in trending_articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending news: {str(e)}")

@router.get("/price-impact", response_model=List[NewsArticleResponse])
async def get_price_impact_news(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get news articles with significant price impact predictions
    - **limit**: Number of articles to return (1-100)
    """
    try:
        # Get all articles and filter by price impact
        all_articles = await mineral_news_service.get_latest_news(limit=200)
        
        filtered_articles = []
        for article in all_articles:
            # Check if article has significant price impact
            has_significant_impact = any(
                abs(impact) >= 5.0 for impact in article.price_impact.values()
            )
            
            if has_significant_impact:
                filtered_articles.append(article)
        
        # Sort by maximum price impact
        filtered_articles.sort(
            key=lambda x: max(abs(impact) for impact in x.price_impact.values()),
            reverse=True
        )
        
        # Limit results
        filtered_articles = filtered_articles[:limit]
        
        response_articles = [convert_article_to_response(article) for article in filtered_articles]
        return response_articles
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching price impact news: {str(e)}")

@router.post("/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    """
    Trigger news refresh
    """
    try:
        # Add background task to refresh news
        background_tasks.add_task(
            mineral_news_service.fetch_news_from_all_sources
        )
        
        return {"message": "News refresh started", "status": "processing"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing news: {str(e)}")

@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Check if service is responsive
        stats = await mineral_news_service.get_news_statistics()
        
        return {
            "status": "healthy",
            "service": "mineral_news_service",
            "total_articles": stats.get("total_articles", 0),
            "last_updated": stats.get("last_updated", datetime.utcnow().isoformat())
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "mineral_news_service",
                "error": str(e)
            }
        )
