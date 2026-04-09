"""
Marketplace Listings Service - Core DEDAN Mine Backend
Handles auctions, Buy-It-Now, and basic marketplace functionality
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc

from models import Listing, User, Auction, BuyItNowTransaction
from database import get_db
from security import quantum_sign_data

class ListingService:
    """Core marketplace service with competitor strengths + future-tech integration"""
    
    def __init__(self):
        self.db = next(get_db())
    
    async def create_listing(
        self,
        seller_id: str,
        title: str,
        description: str,
        category: str,
        gem_type: str,
        weight: float,
        unit: str,
        price: float,
        listing_type: str,
        images: List[str] = None,
        buy_it_now_price: float = None,
        reserve_price: float = None,
        auction_end_time: datetime = None,
        # Future features (optional)
        enable_traceability: bool = False,
        enable_video_negotiation: bool = False,
        ai_agent_managed: bool = False,
        esg_monitored: bool = False,
        mine_location: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new listing with progressive feature support"""
        
        try:
            # Core listing creation (always works)
            listing = Listing(
                id=str(uuid.uuid4()),
                seller_id=seller_id,
                title=title,
                description=description,
                category=category,
                gem_type=gem_type,
                weight=weight,
                unit=unit,
                price=price,
                listing_type=listing_type,
                images=images or [],
                buy_it_now_price=buy_it_now_price,
                reserve_price=reserve_price,
                auction_end_time=auction_end_time,
                mine_location=mine_location or {},
                
                # Future features (progressive enhancement)
                traceability_enabled=enable_traceability,
                video_negotiation_enabled=enable_video_negotiation,
                ai_agent_managed=ai_agent_managed,
                esg_monitored=esg_monitored,
                
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(listing)
            self.db.commit()
            self.db.refresh(listing)
            
            # Setup future features if requested (non-blocking)
            if enable_traceability:
                await self._setup_traceability(listing.id)
            
            if enable_video_negotiation:
                await self._enable_video_negotiation(listing.id)
            
            if ai_agent_managed:
                await self._configure_ai_agent(listing.id, seller_id)
            
            return {
                "success": True,
                "listing_id": listing.id,
                "message": "Listing created successfully",
                "features_enabled": {
                    "traceability": enable_traceability,
                    "video_negotiation": enable_video_negotiation,
                    "ai_agent": ai_agent_managed,
                    "esg_monitoring": esg_monitored
                }
            }
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_listings(
        self,
        page: int = 1,
        limit: int = 20,
        category: Optional[str] = None,
        gem_type: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        seller_location: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Browse listings with advanced filtering and sorting"""
        
        try:
            query = self.db.query(Listing).filter(Listing.is_active == True)
            
            # Apply filters
            if category:
                query = query.filter(Listing.category == category)
            
            if gem_type:
                query = query.filter(Listing.gem_type == gem_type)
            
            if min_price:
                query = query.filter(Listing.price >= min_price)
            
            if max_price:
                query = query.filter(Listing.price <= max_price)
            
            # Location-based filtering (competitor strength)
            if seller_location:
                lat = seller_location.get('lat')
                lng = seller_location.get('lng')
                if lat and lng:
                    # Simple distance calculation (would use PostGIS in production)
                    query = query.filter(
                        func.sqrt(
                            func.pow(Listing.mine_location['lat'] - lat, 2) +
                            func.pow(Listing.mine_location['lng'] - lng, 2)
                        ) <= 50  # 50km radius
                    )
            
            # Apply sorting
            if sort_by == "price":
                order_col = Listing.price if sort_order == "asc" else desc(Listing.price)
            elif sort_by == "created_at":
                order_col = desc(Listing.created_at) if sort_order == "desc" else asc(Listing.created_at)
            else:
                order_col = desc(Listing.created_at)  # default
            
            query = query.order_by(order_col)
            
            # Pagination
            total = query.count()
            listings = query.offset((page - 1) * limit).limit(limit).all()
            
            return {
                "success": True,
                "listings": [self._format_listing(listing) for listing in listings],
                "pagination": {
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "total_pages": (total + limit - 1) // limit
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_listing_details(self, listing_id: str) -> Dict[str, Any]:
        """Get detailed listing information with all features"""
        
        try:
            listing = self.db.query(Listing).filter(
                and_(Listing.id == listing_id, Listing.is_active == True)
            ).first()
            
            if not listing:
                raise HTTPException(status_code=404, detail="Listing not found")
            
            return {
                "success": True,
                "listing": self._format_listing(listing, include_details=True)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def place_bid(
        self,
        auction_id: str,
        bidder_id: str,
        amount: float,
        max_proxy_amount: Optional[float] = None,
        quantum_signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """Place a bid with quantum-resistant security"""
        
        try:
            # Verify quantum signature if provided
            if quantum_signature:
                if not await self._verify_quantum_signature(quantum_signature, bidder_id, amount):
                    raise HTTPException(status_code=400, detail="Invalid quantum signature")
            
            # Get auction and listing
            auction = self.db.query(Auction).filter(Auction.id == auction_id).first()
            if not auction:
                raise HTTPException(status_code=404, detail="Auction not found")
            
            listing = self.db.query(Listing).filter(Listing.id == auction.listing_id).first()
            
            # Validate bid
            if amount <= auction.current_bid:
                raise HTTPException(status_code=400, detail="Bid must be higher than current bid")
            
            if auction.reserve_price and amount < auction.reserve_price:
                raise HTTPException(status_code=400, detail="Bid is below reserve price")
            
            # Update auction
            auction.current_bid = amount
            auction.current_bidder_id = bidder_id
            auction.bid_count += 1
            auction.updated_at = datetime.now(timezone.utc)
            
            # Auto-extend auction if bid near end
            if auction.auction_end_time and auction.auto_extend:
                time_remaining = auction.auction_end_time - datetime.now(timezone.utc)
                if time_remaining.total_seconds() <= 600:  # 10 minutes
                    auction.auction_end_time = auction.auction_end_time + timedelta(minutes=auction.extend_time_minutes)
                    auction.extend_count += 1
            
            self.db.commit()
            
            return {
                "success": True,
                "message": "Bid placed successfully",
                "current_bid": amount,
                "auction_extended": auction.extend_count > 0,
                "new_end_time": auction.auction_end_time.isoformat() if auction.auction_end_time else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    async def buy_it_now(
        self,
        listing_id: str,
        buyer_id: str,
        payment_method: str = "stripe"
    ) -> Dict[str, Any]:
        """Execute Buy-It-Now transaction with 5% commission"""
        
        try:
            listing = self.db.query(Listing).filter(
                and_(Listing.id == listing_id, Listing.is_active == True)
            ).first()
            
            if not listing:
                raise HTTPException(status_code=404, detail="Listing not found")
            
            if not listing.buy_it_now_price:
                raise HTTPException(status_code=400, detail="Buy-It-Now not available for this listing")
            
            # Calculate commission (5% flat rate)
            commission_rate = 5.0
            commission_amount = listing.buy_it_now_price * (commission_rate / 100)
            seller_payout = listing.buy_it_now_price - commission_amount
            
            # Create transaction
            transaction = BuyItNowTransaction(
                id=str(uuid.uuid4()),
                listing_id=listing_id,
                buyer_id=buyer_id,
                seller_id=listing.seller_id,
                price=listing.buy_it_now_price,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                seller_payout=seller_payout,
                payment_method=payment_method,
                transaction_status="pending",
                created_at=datetime.now(timezone.utc)
            )
            
            # Deactivate listing
            listing.is_active = False
            listing.updated_at = datetime.now(timezone.utc)
            
            self.db.add(transaction)
            self.db.commit()
            
            return {
                "success": True,
                "transaction_id": transaction.id,
                "message": "Purchase successful",
                "price": listing.buy_it_now_price,
                "commission": {
                    "rate": f"{commission_rate}%",
                    "amount": commission_amount,
                    "seller_payout": seller_payout
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    
    def _format_listing(self, listing: Listing, include_details: bool = False) -> Dict[str, Any]:
        """Format listing for API response with progressive features"""
        
        base_data = {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "category": listing.category,
            "gem_type": listing.gem_type,
            "weight": listing.weight,
            "unit": listing.unit,
            "price": listing.price,
            "price_per_unit": listing.price / listing.weight,
            "listing_type": listing.listing_type,
            "images": listing.images,
            "created_at": listing.created_at.isoformat(),
            "seller_id": listing.seller_id
        }
        
        # Add auction-specific data
        if listing.listing_type == "auction":
            auction = self.db.query(Auction).filter(Auction.listing_id == listing.id).first()
            if auction:
                base_data.update({
                    "current_bid": auction.current_bid,
                    "bid_count": auction.bid_count,
                    "auction_end_time": auction.auction_end_time.isoformat() if auction.auction_end_time else None,
                    "reserve_price_met": auction.current_bid >= (listing.reserve_price or 0)
                })
        
        # Add Buy-It-Now data
        if listing.buy_it_now_price:
            base_data["buy_it_now_price"] = listing.buy_it_now_price
        
        if include_details:
            # Add future features if enabled
            future_features = {}
            
            if listing.traceability_enabled:
                future_features["traceability_score"] = self._get_traceability_score(listing.id)
            
            if listing.video_negotiation_enabled:
                future_features["video_negotiation_available"] = True
                future_features["video_sessions"] = self._get_video_sessions(listing.id)
            
            if listing.ai_agent_managed:
                future_features["ai_agent_recommendations"] = self._get_ai_recommendations(listing.id)
            
            if listing.esg_monitored:
                future_features["esg_score"] = self._get_esg_score(listing.id)
                future_features["carbon_footprint"] = self._get_carbon_footprint(listing.id)
            
            # Add trust signals
            future_features["trust_signals"] = self._get_trust_signals(listing.seller_id)
            
            base_data["future_features"] = future_features
        
        return base_data
    
    async def _setup_traceability(self, listing_id: str) -> None:
        """Setup traceability for listing (future feature)"""
        # This would integrate with IoT sensors, GPS, satellite
        pass
    
    async def _enable_video_negotiation(self, listing_id: str) -> None:
        """Enable video negotiation for listing (future feature)"""
        # This would setup WebRTC infrastructure
        pass
    
    async def _configure_ai_agent(self, listing_id: str, seller_id: str) -> None:
        """Configure AI agent for listing (future feature)"""
        # This would setup autonomous trading agent
        pass
    
    async def _verify_quantum_signature(self, signature: str, user_id: str, data: Any) -> bool:
        """Verify quantum-resistant signature"""
        # Implement quantum signature verification
        return await quantum_sign_data.verify_signature(signature, user_id, data)
    
    def _get_traceability_score(self, listing_id: str) -> Optional[float]:
        """Get traceability score for listing"""
        # Calculate based on IoT data, satellite verification, etc.
        return None
    
    def _get_video_sessions(self, listing_id: str) -> List[Dict[str, Any]]:
        """Get video negotiation sessions for listing"""
        # Return scheduled/active video sessions
        return []
    
    def _get_ai_recommendations(self, listing_id: str) -> List[Dict[str, Any]]:
        """Get AI agent recommendations for listing"""
        # Return AI-powered insights
        return []
    
    def _get_esg_score(self, listing_id: str) -> Optional[int]:
        """Get ESG score for listing"""
        # Calculate ESG score
        return None
    
    def _get_carbon_footprint(self, listing_id: str) -> Optional[float]:
        """Get carbon footprint for listing"""
        # Calculate carbon footprint in kg CO2
        return None
    
    def _get_trust_signals(self, seller_id: str) -> Dict[str, Any]:
        """Get trust signals for seller"""
        # Calculate reputation, feedback, etc.
        return {
            "reputation_score": 0.0,
            "positive_feedback_count": 0,
            "verification_level": "none",
            "watch_list_count": 0
        }
