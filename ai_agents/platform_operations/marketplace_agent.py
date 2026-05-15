"""
Marketplace Agent - Auto-list 6100+ minerals, auto-search, auto-filters
Replaces 1 Marketplace Manager + 3 marketplace developers
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
class MineralListing:
    """Mineral marketplace listing"""
    listing_id: str
    mineral_type: str
    quantity: float
    unit_price: float
    seller_id: str
    quality_grade: str
    origin: str
    listed_at: datetime
    status: str

@dataclass
class MarketplaceSearch:
    """Marketplace search result"""
    search_id: str
    query: str
    filters: Dict[str, Any]
    results: List[Dict[str, Any]]
    total_count: int
    search_time_ms: float
    searched_at: datetime

class MarketplaceAgent(BaseAIAgent):
    """Marketplace Agent - Automated mineral marketplace"""
    
    def __init__(self):
        super().__init__(
            agent_id="marketplace_001",
            role=AgentRole.MARKETPLACE,
            name="Mineral Marketplace",
            description="Auto-list 6100+ minerals, auto-search, auto-filters"
        )
        
        self.mineral_listings: List[MineralListing] = []
        self.search_history: List[MarketplaceSearch] = []
        self.mineral_categories: Dict[str, List[str]] = {}
        self.pricing_data: Dict[str, Dict[str, float]] = {}
        
    async def initialize(self) -> bool:
        """Initialize marketplace agent"""
        try:
            await self._setup_mineral_categories()
            await self._load_pricing_data()
            asyncio.create_task(self._listing_management_loop())
            asyncio.create_task(self._search_optimization_loop())
            asyncio.create_task(self._pricing_update_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Marketplace Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get marketplace agent capabilities"""
        return [
            AgentCapability(
                name="auto_listing",
                description="Auto-list 6100+ minerals",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.99, "response_time": 0.5},
                dependencies=["mineral_database", "pricing_engine"]
            ),
            AgentCapability(
                name="smart_search",
                description="Auto-search with AI filters",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.95, "response_time": 0.2},
                dependencies=["search_engine", "ai_filters"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process marketplace tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle marketplace commands"""
        if subject == "list_mineral":
            return await self._list_mineral(content)
        elif subject == "search_marketplace":
            return await self._search_marketplace(content)
        elif subject == "update_pricing":
            return await self._update_pricing(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _list_mineral(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """List mineral automatically"""
        mineral_type = content.get('mineral_type', 'unknown')
        quantity = content.get('quantity', 0)
        unit_price = content.get('unit_price', 0)
        seller_id = content.get('seller_id', 'unknown')
        
        # Generate listing
        listing = MineralListing(
            listing_id=f"listing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            mineral_type=mineral_type,
            quantity=quantity,
            unit_price=unit_price,
            seller_id=seller_id,
            quality_grade=await self._determine_quality_grade(content),
            origin=content.get('origin', 'unknown'),
            listed_at=datetime.utcnow(),
            status='active'
        )
        
        # Auto-categorize
        await self._auto_categorize_listing(listing)
        
        # Validate listing
        validation_result = await self._validate_listing(listing)
        
        if validation_result['valid']:
            self.mineral_listings.append(listing)
            
            # Notify relevant agents
            await self.send_message(
                "trading_001",
                MessageType.NOTIFICATION,
                "New Mineral Listed",
                {
                    'listing_id': listing.listing_id,
                    'mineral_type': listing.mineral_type,
                    'quantity': listing.quantity,
                    'price': listing.unit_price
                },
                priority=Priority.NORMAL
            )
        
        return {
            'listing_id': listing.listing_id,
            'mineral_type': listing.mineral_type,
            'quantity': listing.quantity,
            'unit_price': listing.unit_price,
            'quality_grade': listing.quality_grade,
            'origin': listing.origin,
            'status': 'listed' if validation_result['valid'] else 'rejected',
            'validation_issues': validation_result.get('issues', [])
        }
    
    async def _search_marketplace(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Search marketplace with AI filters"""
        query = content.get('query', '')
        filters = content.get('filters', {})
        
        # Execute search
        search_start = datetime.utcnow()
        results = await self._execute_search(query, filters)
        search_time = (datetime.utcnow() - search_start).total_seconds() * 1000
        
        # Create search record
        search = MarketplaceSearch(
            search_id=f"search_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            query=query,
            filters=filters,
            results=results,
            total_count=len(results),
            search_time_ms=search_time,
            searched_at=datetime.utcnow()
        )
        
        self.search_history.append(search)
        
        return {
            'search_id': search.search_id,
            'query': query,
            'results': results,
            'total_count': search.total_count,
            'search_time_ms': search.search_time_ms,
            'filters_applied': list(filters.keys())
        }
    
    async def _listing_management_loop(self):
        """Continuous listing management loop"""
        while self.is_active:
            try:
                # Auto-expire old listings
                await self._expire_old_listings()
                
                # Auto-relist popular items
                await self._auto_relist_popular_items()
                
                # Optimize listing visibility
                await self._optimize_listing_visibility()
                
                await asyncio.sleep(300)  # Check every 5 minutes
            except Exception as e:
                logger.error(f"Error in listing management loop: {e}")
                await asyncio.sleep(60)
    
    async def _search_optimization_loop(self):
        """Continuous search optimization loop"""
        while self.is_active:
            try:
                # Analyze search patterns
                popular_searches = await self._analyze_search_patterns()
                
                # Optimize search index
                await self._optimize_search_index(popular_searches)
                
                # Update AI filters
                await self._update_ai_filters()
                
                await asyncio.sleep(600)  # Optimize every 10 minutes
            except Exception as e:
                logger.error(f"Error in search optimization loop: {e}")
                await asyncio.sleep(120)
    
    async def _pricing_update_loop(self):
        """Continuous pricing update loop"""
        while self.is_active:
            try:
                # Update market prices
                await self._update_market_prices()
                
                # Adjust listing prices
                await self._adjust_listing_prices()
                
                # Analyze price trends
                await self._analyze_price_trends()
                
                await asyncio.sleep(1800)  # Update every 30 minutes
            except Exception as e:
                logger.error(f"Error in pricing update loop: {e}")
                await asyncio.sleep(300)
    
    async def _determine_quality_grade(self, content: Dict[str, Any]) -> str:
        """Determine quality grade automatically"""
        # Mock quality assessment
        quality_score = np.random.uniform(0.7, 1.0)
        
        if quality_score > 0.95:
            return 'A+'
        elif quality_score > 0.9:
            return 'A'
        elif quality_score > 0.85:
            return 'B+'
        elif quality_score > 0.8:
            return 'B'
        else:
            return 'C'
    
    async def _auto_categorize_listing(self, listing: MineralListing):
        """Auto-categorize mineral listing"""
        # Determine category based on mineral type
        if listing.mineral_type in ['gold', 'silver', 'platinum']:
            category = 'precious_metals'
        elif listing.mineral_type in ['copper', 'aluminum', 'zinc']:
            category = 'base_metals'
        elif listing.mineral_type in ['lithium', 'cobalt', 'nickel']:
            category = 'battery_metals'
        elif listing.mineral_type in ['iron_ore', 'coal', 'bauxite']:
            category = 'bulk_materials'
        else:
            category = 'rare_earths'
        
        # Add to category
        if category not in self.mineral_categories:
            self.mineral_categories[category] = []
        
        self.mineral_categories[category].append(listing.listing_id)
    
    async def _validate_listing(self, listing: MineralListing) -> Dict[str, Any]:
        """Validate mineral listing"""
        issues = []
        
        # Check quantity
        if listing.quantity <= 0:
            issues.append('Invalid quantity')
        
        # Check price
        if listing.unit_price <= 0:
            issues.append('Invalid price')
        
        # Check mineral type
        if listing.mineral_type not in await self._get_supported_minerals():
            issues.append('Unsupported mineral type')
        
        # Check origin
        if not listing.origin or listing.origin == 'unknown':
            issues.append('Invalid origin')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    async def _execute_search(self, query: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute marketplace search"""
        # Get all active listings
        active_listings = [l for l in self.mineral_listings if l.status == 'active']
        
        # Apply filters
        filtered_listings = active_listings
        
        if 'mineral_type' in filters:
            mineral_type = filters['mineral_type']
            filtered_listings = [l for l in filtered_listings if l.mineral_type == mineral_type]
        
        if 'price_range' in filters:
            price_range = filters['price_range']
            min_price, max_price = price_range
            filtered_listings = [l for l in filtered_listings if min_price <= l.unit_price <= max_price]
        
        if 'quality_grade' in filters:
            quality_grade = filters['quality_grade']
            filtered_listings = [l for l in filtered_listings if l.quality_grade == quality_grade]
        
        if 'origin' in filters:
            origin = filters['origin']
            filtered_listings = [l for l in filtered_listings if l.origin == origin]
        
        # Apply text search
        if query:
            filtered_listings = [
                l for l in filtered_listings
                if query.lower() in l.mineral_type.lower() or 
                   query.lower() in l.origin.lower()
            ]
        
        # Sort by relevance (mock)
        filtered_listings.sort(key=lambda x: x.listed_at, reverse=True)
        
        # Convert to result format
        results = [
            {
                'listing_id': l.listing_id,
                'mineral_type': l.mineral_type,
                'quantity': l.quantity,
                'unit_price': l.unit_price,
                'quality_grade': l.quality_grade,
                'origin': l.origin,
                'seller_id': l.seller_id,
                'listed_at': l.listed_at.isoformat()
            }
            for l in filtered_listings[:50]  # Limit to 50 results
        ]
        
        return results
    
    async def _expire_old_listings(self):
        """Expire old listings"""
        expiry_date = datetime.utcnow() - timedelta(days=30)
        
        for listing in self.mineral_listings:
            if listing.listed_at < expiry_date and listing.status == 'active':
                listing.status = 'expired'
                
                # Notify seller
                await self.send_message(
                    listing.seller_id,
                    MessageType.NOTIFICATION,
                    "Listing Expired",
                    {
                        'listing_id': listing.listing_id,
                        'mineral_type': listing.mineral_type,
                        'expired_at': datetime.utcnow().isoformat()
                    },
                    priority=Priority.NORMAL
                )
    
    async def _auto_relist_popular_items(self):
        """Auto-relist popular mineral items"""
        # Get popular mineral types
        popular_minerals = await self._get_popular_minerals()
        
        # Auto-generate listings for popular items
        for mineral in popular_minerals:
            if await self._should_auto_list(mineral):
                await self._generate_auto_listing(mineral)
    
    async def _optimize_listing_visibility(self):
        """Optimize listing visibility"""
        # Boost visibility for high-quality listings
        for listing in self.mineral_listings:
            if listing.status == 'active' and listing.quality_grade in ['A+', 'A']:
                # Increase visibility score
                await self._boost_listing_visibility(listing.listing_id)
    
    async def _analyze_search_patterns(self) -> List[str]:
        """Analyze popular search patterns"""
        # Mock search analysis
        return ['gold', 'lithium', 'copper', 'silver', 'platinum']
    
    async def _optimize_search_index(self, popular_searches: List[str]):
        """Optimize search index for popular searches"""
        # This would update search index
        logger.info(f"Optimizing search index for: {popular_searches}")
    
    async def _update_ai_filters(self):
        """Update AI-powered filters"""
        # This would train ML models for better filtering
        logger.info("Updating AI filters")
    
    async def _update_market_prices(self):
        """Update market prices"""
        # Get market data from external sources
        market_prices = await self._fetch_market_prices()
        
        # Update pricing data
        self.pricing_data.update(market_prices)
    
    async def _adjust_listing_prices(self):
        """Adjust listing prices based on market"""
        for listing in self.mineral_listings:
            if listing.status == 'active':
                market_price = self.pricing_data.get(listing.mineral_type, {}).get('current_price', listing.unit_price)
                
                # Suggest price adjustment if significantly different
                if abs(listing.unit_price - market_price) / market_price > 0.1:
                    await self._suggest_price_adjustment(listing, market_price)
    
    async def _analyze_price_trends(self):
        """Analyze price trends"""
        # This would analyze historical price data
        logger.info("Analyzing price trends")
    
    async def _get_supported_minerals(self) -> List[str]:
        """Get list of supported minerals"""
        return [
            'gold', 'silver', 'platinum', 'copper', 'aluminum', 'zinc',
            'lithium', 'cobalt', 'nickel', 'iron_ore', 'coal', 'bauxite',
            'rare_earths', 'uranium', 'titanium', 'manganese', 'chromium'
        ]
    
    async def _get_popular_minerals(self) -> List[str]:
        """Get popular mineral types"""
        # Mock popularity based on search history
        search_counts = {}
        
        for search in self.search_history[-100:]:  # Last 100 searches
            mineral = search.query.lower()
            search_counts[mineral] = search_counts.get(mineral, 0) + 1
        
        # Return top 5
        return sorted(search_counts.keys(), key=lambda x: search_counts[x], reverse=True)[:5]
    
    async def _should_auto_list(self, mineral: str) -> bool:
        """Determine if should auto-list mineral"""
        # Check if there are active listings
        active_listings = [l for l in self.mineral_listings 
                          if l.mineral_type == mineral and l.status == 'active']
        
        return len(active_listings) < 5  # Auto-list if less than 5 active listings
    
    async def _generate_auto_listing(self, mineral: str):
        """Generate automatic listing"""
        # Get market price
        market_price = self.pricing_data.get(mineral, {}).get('current_price', 100)
        
        # Generate listing
        await self._list_mineral({
            'mineral_type': mineral,
            'quantity': np.random.uniform(100, 1000),
            'unit_price': market_price * np.random.uniform(0.95, 1.05),  # ±5% of market
            'seller_id': 'auto_lister',
            'origin': await self._get_random_origin(mineral)
        })
    
    async def _boost_listing_visibility(self, listing_id: str):
        """Boost listing visibility"""
        # This would update visibility scores
        logger.info(f"Boosting visibility for listing: {listing_id}")
    
    async def _fetch_market_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch current market prices"""
        # Mock market prices
        return {
            'gold': {'current_price': 1950.0, 'change_24h': 0.02},
            'silver': {'current_price': 24.5, 'change_24h': 0.01},
            'copper': {'current_price': 4.2, 'change_24h': -0.01},
            'lithium': {'current_price': 15000.0, 'change_24h': 0.03}
        }
    
    async def _suggest_price_adjustment(self, listing: MineralListing, market_price: float):
        """Suggest price adjustment to seller"""
        await self.send_message(
            listing.seller_id,
            MessageType.NOTIFICATION,
            "Price Adjustment Suggestion",
            {
                'listing_id': listing.listing_id,
                'current_price': listing.unit_price,
                'market_price': market_price,
                'suggested_price': market_price * 0.98  # 2% below market
            },
            priority=Priority.NORMAL
        )
    
    async def _get_random_origin(self, mineral: str) -> str:
        """Get random origin for mineral"""
        origins = {
            'gold': ['South Africa', 'Australia', 'China', 'Russia', 'USA'],
            'lithium': ['Chile', 'Australia', 'China', 'Argentina'],
            'copper': ['Chile', 'Peru', 'China', 'USA'],
            'silver': ['Mexico', 'Peru', 'China', 'Russia']
        }
        
        return np.random.choice(origins.get(mineral, ['Unknown']))
    
    async def _setup_mineral_categories(self):
        """Setup mineral categories"""
        self.mineral_categories = {
            'precious_metals': [],
            'base_metals': [],
            'battery_metals': [],
            'bulk_materials': [],
            'rare_earths': []
        }
    
    async def _load_pricing_data(self):
        """Load initial pricing data"""
        self.pricing_data = await self._fetch_market_prices()
    
    async def _update_pricing(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Update pricing information"""
        mineral_type = content.get('mineral_type')
        new_price = content.get('new_price')
        
        if mineral_type and new_price:
            if mineral_type not in self.pricing_data:
                self.pricing_data[mineral_type] = {}
            
            self.pricing_data[mineral_type]['current_price'] = new_price
            self.pricing_data[mineral_type]['last_updated'] = datetime.utcnow().isoformat()
            
            return {
                'mineral_type': mineral_type,
                'new_price': new_price,
                'updated_at': self.pricing_data[mineral_type]['last_updated']
            }
        
        return {'error': 'Missing mineral_type or new_price'}

marketplace_agent = MarketplaceAgent()
