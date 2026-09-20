"""
World-Mine Marketplace API
Production-ready marketplace endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
import uuid

from models import (
    Listing, Auction, Bid, BuyItNowTransaction,
    User
)
from database import get_db

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


def serialize_listing(listing: Listing) -> Dict[str, Any]:
    """Serialize a Listing ORM object into a JSON-safe API contract payload.

    Maps legacy API fields (mineral_type, quantity, unit_price, ...) onto the
    Listing model columns so the frontend contract stays stable.
    """
    mine_location = listing.mine_location if isinstance(listing.mine_location, dict) else {}
    data = {
        "id": str(listing.id),
        "seller_id": str(listing.seller_id),
        "title": listing.title,
        "description": listing.description,
        # Legacy contract fields mapped from Listing columns
        "mineral_type": listing.gem_type,
        "quantity": listing.weight,
        "unit_price": listing.price_per_unit if listing.price_per_unit is not None else listing.price,
        "total_price": listing.price,
        "currency": "USD",
        "quality_grade": listing.quality_grade,
        "origin": mine_location.get("origin"),
        "country": mine_location.get("country"),
        "city": mine_location.get("city"),
        "latitude": mine_location.get("latitude"),
        "longitude": mine_location.get("longitude"),
        "status": "active" if listing.is_active else "inactive",
        "listing_type": listing.listing_type,
        "created_at": listing.created_at.isoformat() if listing.created_at else None,
        "updated_at": listing.updated_at.isoformat() if listing.updated_at else None,
    }
    return jsonable_encoder(data)


# Request/Response Models
class ListingCreate(BaseModel):
    title: str
    description: str = ""
    # Legacy contract fields (simple payload shape used by the frontend/tests)
    price: Optional[float] = None
    currency: str = "USD"
    category: Optional[str] = None
    # Rich fields (optional so simple payloads remain valid)
    mineral_type: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    quality_grade: Optional[str] = None
    origin: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class ListingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    status: Optional[str] = None

class BidCreate(BaseModel):
    amount: float

# Marketplace Endpoints
@router.get("/listings")
async def get_listings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    mineral_type: Optional[str] = None,
    quality_grade: Optional[str] = None,
    country: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated listings with filters"""
    query = db.query(Listing).filter(Listing.is_active == True)

    if mineral_type:
        query = query.filter(Listing.gem_type == mineral_type)
    if quality_grade:
        query = query.filter(Listing.quality_grade == quality_grade)
    if country:
        query = query.filter(Listing.mine_location['country'].astext == country)
    if min_price:
        query = query.filter(Listing.price >= min_price)
    if max_price:
        query = query.filter(Listing.price <= max_price)
    if search:
        query = query.filter(
            (Listing.title.ilike(f"%{search}%")) |
            (Listing.description.ilike(f"%{search}%"))
        )

    total = query.count()
    listings = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": [serialize_listing(l) for l in listings],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": page * page_size < total,
        "has_previous": page > 1
    }

@router.get("/listings/{listing_id}")
async def get_listing(listing_id: str, db: Session = Depends(get_db)):
    """Get single listing by ID"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return {"data": serialize_listing(listing)}

@router.post("/listings")
async def create_listing(listing: ListingCreate, db: Session = Depends(get_db)):
    """Create new listing"""
    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    price = listing.price if listing.price is not None else (listing.unit_price or 0.0)
    quantity = listing.quantity if listing.quantity is not None else 0.0
    mine_location = {
        key: value
        for key, value in {
            "origin": listing.origin,
            "country": listing.country,
            "city": listing.city,
            "latitude": listing.latitude,
            "longitude": listing.longitude
        }.items()
        if value is not None
    }

    new_listing = Listing(
        seller_id=user_id,
        title=listing.title,
        description=listing.description,
        category=listing.category or "minerals",
        gem_type=listing.mineral_type or "other",
        weight=quantity,
        unit="kg",
        price=price,
        price_per_unit=price,
        listing_type="buy_it_now",
        quality_grade=listing.quality_grade or "unknown",
        mine_location=mine_location,
        is_active=True
    )

    db.add(new_listing)
    db.commit()
    db.refresh(new_listing)

    return {"data": serialize_listing(new_listing)}

@router.put("/listings/{listing_id}")
async def update_listing(listing_id: str, listing: ListingUpdate, db: Session = Depends(get_db)):
    """Update existing listing"""
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # TODO: Verify user owns listing

    update_data = listing.dict(exclude_unset=True)
    if "quantity" in update_data:
        db_listing.weight = update_data.pop("quantity")
    if "unit_price" in update_data:
        price = update_data.pop("unit_price")
        db_listing.price = price
        db_listing.price_per_unit = price
    if "status" in update_data:
        status_value = update_data.pop("status")
        # Map API status values onto the Listing model's is_active flag
        status_map = {"active": True, "sold": False, "withdrawn": False, "suspended": False}
        db_listing.is_active = status_map.get(str(status_value).lower(), db_listing.is_active)
    for field, value in update_data.items():
        if hasattr(db_listing, field):
            setattr(db_listing, field, value)

    db.commit()
    db.refresh(db_listing)

    return {"data": serialize_listing(db_listing)}

@router.delete("/listings/{listing_id}")
async def delete_listing(listing_id: str, db: Session = Depends(get_db)):
    """Delete listing"""
    db_listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not db_listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # TODO: Verify user owns listing

    db.delete(db_listing)
    db.commit()

    return {"data": None}

# Auction Endpoints
@router.get("/auctions")
async def get_auctions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get paginated auctions"""
    query = db.query(Auction)

    if status:
        query = query.filter(Auction.auction_status == status)

    total = query.count()
    auctions = query.offset((page - 1) * page_size).limit(page_size).all()

    return {
        "data": auctions,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_next": page * page_size < total,
        "has_previous": page > 1
    }

@router.get("/auctions/{auction_id}")
async def get_auction(auction_id: str, db: Session = Depends(get_db)):
    """Get single auction by ID"""
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")
    return {"data": auction}

@router.post("/auctions/{auction_id}/bids")
async def place_bid(auction_id: str, bid: BidCreate, db: Session = Depends(get_db)):
    """Place bid on auction"""
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(status_code=404, detail="Auction not found")

    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    if bid.amount <= auction.current_bid:
        raise HTTPException(status_code=400, detail="Bid must be higher than current bid")

    new_bid = Bid(
        id=str(uuid.uuid4()),
        auction_id=auction_id,
        bidder_id=user_id,
        amount=bid.amount,
        created_at=datetime.utcnow()
    )

    auction.current_bid = bid.amount

    db.add(new_bid)
    db.commit()
    db.refresh(new_bid)

    return {"data": new_bid}

# Buy It Now Endpoints
@router.post("/listings/{listing_id}/buy-now")
async def buy_now(listing_id: str, db: Session = Depends(get_db)):
    """Buy listing immediately"""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")

    # TODO: Get user_id from auth token
    buyer_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    price = listing.price
    commission_rate = 5.0
    commission_amount = price * (commission_rate / 100)

    # Create transaction
    transaction = BuyItNowTransaction(
        id=str(uuid.uuid4()),
        listing_id=listing_id,
        buyer_id=buyer_id,
        seller_id=listing.seller_id,
        price=price,
        original_price=price,
        commission_rate=commission_rate,
        commission_amount=commission_amount,
        seller_payout=price - commission_amount,
        transaction_status="pending"
    )

    listing.is_active = False

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {"data": {"transaction_id": str(transaction.id)}}
