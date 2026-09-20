"""
Logistics Platform API
Shipment tracking, GPS synchronization, and logistics operations
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import uuid

router = APIRouter(prefix="/api/logistics", tags=["Logistics"])


class ShipmentStatus(str, Enum):
    """Shipment status states"""
    PENDING = "pending"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELAYED = "delayed"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class TransportMode(str, Enum):
    """Transport modes (accepts both 'ground' and 'truck' naming)"""
    TRUCK = "truck"
    GROUND = "ground"
    SHIP = "ship"
    AIR = "air"
    RAIL = "rail"


class Shipment(BaseModel):
    """Shipment model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tracking_number: str = Field(default_factory=lambda: str(uuid.uuid4()))
    order_id: str = Field(default="")
    sender_id: str = Field(default="system")
    recipient_id: str = Field(default="system")
    origin_address: Union[Dict[str, Any], str] = ""
    destination_address: Union[Dict[str, Any], str] = ""
    status: ShipmentStatus = Field(default=ShipmentStatus.PENDING)
    transport_mode: Union[TransportMode, str] = TransportMode.GROUND
    weight: Optional[float] = Field(default=None, ge=0)
    weight_kg: Optional[float] = Field(default=None, ge=0)
    dimensions: Dict[str, float] = Field(default_factory=dict)
    estimated_delivery: Optional[datetime] = None
    actual_delivery: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GPSCoordinate(BaseModel):
    """GPS coordinate"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    altitude: Optional[float] = None
    accuracy: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ShipmentCreate(BaseModel):
    """Flexible shipment creation payload.

    Accepts both a rich shape (order_id/sender_id/recipient_id/dimensions)
    and the simple shape used by clients (flat address strings + weight).
    """
    tracking_number: Optional[str] = None
    order_id: Optional[str] = None
    sender_id: Optional[str] = None
    recipient_id: Optional[str] = None
    origin_address: Union[Dict[str, Any], str] = ""
    destination_address: Union[Dict[str, Any], str] = ""
    transport_mode: Union[TransportMode, str] = TransportMode.GROUND
    weight: Optional[float] = Field(default=None, ge=0)
    weight_kg: Optional[float] = Field(default=None, ge=0)
    dimensions: Dict[str, float] = Field(default_factory=dict)
    estimated_delivery: Optional[datetime] = None


class ShipmentUpdate(BaseModel):
    """Shipment status update"""
    status: Union[ShipmentStatus, str]
    location: Optional[GPSCoordinate] = None
    notes: Optional[str] = None
    updated_by: Optional[str] = "system"


class TrackingEvent(BaseModel):
    """Tracking event"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    shipment_id: str
    status: ShipmentStatus
    location: Optional[GPSCoordinate] = None
    description: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# In-memory storage
shipments: Dict[str, Shipment] = {}
tracking_events: List[TrackingEvent] = []


def _coerce_status(value: Union[ShipmentStatus, str]) -> ShipmentStatus:
    if isinstance(value, ShipmentStatus):
        return value
    try:
        return ShipmentStatus(str(value))
    except ValueError:
        return ShipmentStatus.PENDING


@router.post("/shipments")
async def create_shipment(payload: ShipmentCreate):
    """Create a new shipment"""
    shipment = Shipment(
        tracking_number=payload.tracking_number or str(uuid.uuid4()),
        order_id=payload.order_id or "",
        sender_id=payload.sender_id or "system",
        recipient_id=payload.recipient_id or "system",
        origin_address=payload.origin_address,
        destination_address=payload.destination_address,
        status=ShipmentStatus.PENDING,
        transport_mode=payload.transport_mode,
        weight=payload.weight,
        weight_kg=payload.weight_kg if payload.weight_kg is not None else payload.weight,
        dimensions=payload.dimensions,
        estimated_delivery=payload.estimated_delivery,
    )
    shipments[shipment.id] = shipment

    # Create initial tracking event
    event = TrackingEvent(
        shipment_id=shipment.id,
        status=ShipmentStatus.PENDING,
        description="Shipment created"
    )
    tracking_events.append(event)

    return {"data": jsonable_encoder(shipment)}


@router.get("/shipments", response_model=List[Shipment])
async def list_shipments(
    status: Optional[ShipmentStatus] = None,
    sender_id: Optional[str] = None,
    recipient_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List shipments with filters"""
    shipment_list = list(shipments.values())

    if status:
        shipment_list = [s for s in shipment_list if s.status == status]
    if sender_id:
        shipment_list = [s for s in shipment_list if s.sender_id == sender_id]
    if recipient_id:
        shipment_list = [s for s in shipment_list if s.recipient_id == recipient_id]

    shipment_list.sort(key=lambda x: x.created_at, reverse=True)

    return shipment_list[skip:skip + limit]


@router.get("/shipments/tracking/{tracking_number}", response_model=Shipment)
async def track_by_number(tracking_number: str):
    """Track shipment by tracking number"""
    for shipment in shipments.values():
        if shipment.tracking_number == tracking_number:
            return shipment
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")


@router.get("/track/{tracking_number}")
async def track_compat(tracking_number: str):
    """Track shipment by tracking number (legacy path), {data: ...} envelope"""
    for shipment in shipments.values():
        if shipment.tracking_number == tracking_number:
            return {"data": jsonable_encoder(shipment)}
    raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")


@router.get("/shipments/{shipment_id}", response_model=Shipment)
async def get_shipment(shipment_id: str):
    """Get shipment by ID"""
    if shipment_id not in shipments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")
    return shipments[shipment_id]


@router.put("/shipments/{shipment_id}/status")
async def update_shipment_status_by_id(shipment_id: str, update: ShipmentUpdate):
    """Update shipment status by shipment id"""
    return await _apply_status_update(shipment_id, update)


@router.put("/shipments/status/{shipment_id}")
async def update_shipment_status_compat(shipment_id: str, update: ShipmentUpdate):
    """Update shipment status (legacy path)"""
    return await _apply_status_update(shipment_id, update)


async def _apply_status_update(shipment_id: str, update: ShipmentUpdate):
    """Shared status update logic for both route shapes"""
    if shipment_id not in shipments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")

    shipment = shipments[shipment_id]
    shipment.status = _coerce_status(update.status)
    shipment.updated_at = datetime.utcnow()

    if shipment.status == ShipmentStatus.DELIVERED:
        shipment.actual_delivery = datetime.utcnow()

    # Create tracking event
    event = TrackingEvent(
        shipment_id=shipment_id,
        status=shipment.status,
        location=update.location,
        description=update.notes or f"Status updated to {shipment.status}"
    )
    tracking_events.append(event)

    return {"data": jsonable_encoder(shipment), "message": "Shipment status updated"}


@router.get("/shipments/{shipment_id}/tracking", response_model=List[TrackingEvent])
async def get_tracking_history(shipment_id: str):
    """Get tracking history for a shipment"""
    if shipment_id not in shipments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")

    events = [e for e in tracking_events if e.shipment_id == shipment_id]
    events.sort(key=lambda x: x.timestamp, reverse=True)

    return events


@router.post("/shipments/{shipment_id}/location")
async def update_location(shipment_id: str, location: GPSCoordinate):
    """Update shipment GPS location"""
    if shipment_id not in shipments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")

    shipment = shipments[shipment_id]

    # Create tracking event for location update
    event = TrackingEvent(
        shipment_id=shipment_id,
        status=shipment.status,
        location=location,
        description="Location updated"
    )
    tracking_events.append(event)

    shipment.updated_at = datetime.utcnow()

    return {"message": "Location updated"}


@router.get("/shipments/{shipment_id}/route")
async def get_route(shipment_id: str):
    """Get estimated route for shipment"""
    if shipment_id not in shipments:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Shipment not found")

    shipment = shipments[shipment_id]

    # In production, this would call a routing service
    return {
        "shipment_id": shipment_id,
        "origin": shipment.origin_address,
        "destination": shipment.destination_address,
        "transport_mode": shipment.transport_mode,
        "estimated_distance_km": 500.0,
        "estimated_duration_hours": 24.0
    }
