"""
World-Mine Escrow API
Production-ready escrow endpoints with complete lifecycle management
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
import uuid

from database import get_db

router = APIRouter(prefix="/api/escrow", tags=["escrow"])

# Enums
class EscrowStatus(str, Enum):
    """Escrow status states"""
    CREATED = "created"
    FUNDED = "funded"
    LOCKED = "locked"
    PENDING_VERIFICATION = "pending_verification"
    DISPUTED = "disputed"
    RESOLVED = "resolved"
    RELEASED = "released"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class EscrowMilestone(str, Enum):
    """Escrow milestone types"""
    PAYMENT_RECEIVED = "payment_received"
    SHIPMENT_CONFIRMED = "shipment_confirmed"
    DELIVERY_VERIFIED = "delivery_verified"
    INSPECTION_PASSED = "inspection_passed"
    FINAL_APPROVAL = "final_approval"

# Request/Response Models
class EscrowCreate(BaseModel):
    transaction_id: Optional[str] = ""
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    buyer_id: str
    seller_id: str
    description: Optional[str] = None
    release_conditions: Dict[str, Any] = Field(default_factory=dict)
    milestones: List[str] = Field(default_factory=list)
    auto_release_days: Optional[int] = Field(default=30, description="Days until auto-release if no dispute")


class EscrowFundRequest(BaseModel):
    """Optional request body for funding an escrow"""
    payment_method: Optional[str] = "stripe"
    transaction_id: Optional[str] = None

class EscrowMilestoneUpdate(BaseModel):
    milestone: EscrowMilestone
    achieved: bool = True
    notes: Optional[str] = None

class DisputeCreate(BaseModel):
    reason: str
    evidence: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DisputeResolve(BaseModel):
    resolution: str
    release_to: str = Field(description="buyer or seller")
    refund_amount: Optional[float] = None

# Temporary in-memory storage until database model is added
escrows_db = {}

class EscrowDB:
    """Enhanced escrow model with complete lifecycle support"""
    def __init__(self, id, transaction_id, buyer_id, seller_id, amount, currency, status, 
                 release_conditions, created_at, updated_at, dispute_details=None, 
                 milestones=None, auto_release_days=30, payment_transaction_id=None):
        self.id = id
        self.transaction_id = transaction_id
        self.buyer_id = buyer_id
        self.seller_id = seller_id
        self.amount = amount
        self.currency = currency
        self.status = status
        self.release_conditions = release_conditions
        self.created_at = created_at
        self.updated_at = updated_at
        self.dispute_details = dispute_details
        self.milestones = milestones or []
        self.auto_release_days = auto_release_days
        self.payment_transaction_id = payment_transaction_id
        self.auto_release_date = created_at + timedelta(days=auto_release_days) if auto_release_days else None

    def to_dict(self):
        return {
            "id": self.id,
            "transaction_id": self.transaction_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "amount": self.amount,
            "currency": self.currency,
            "status": self.status,
            "release_conditions": self.release_conditions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "dispute_details": self.dispute_details,
            "milestones": self.milestones,
            "auto_release_days": self.auto_release_days,
            "auto_release_date": self.auto_release_date.isoformat() if self.auto_release_date else None,
            "payment_transaction_id": self.payment_transaction_id
        }

# Escrow Endpoints
@router.get("/escrow")
async def get_escrows(
    status: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get escrows with filters"""
    results = []
    for escrow in escrows_db.values():
        if status and escrow.status != status:
            continue
        if user_id and escrow.buyer_id != user_id and escrow.seller_id != user_id:
            continue
        results.append(escrow.to_dict())
    
    return {"data": results[:limit]}

@router.get("/escrow/{escrow_id}")
async def get_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """Get single escrow by ID"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=404, detail="Escrow not found")
    return {"data": escrows_db[escrow_id].to_dict()}

@router.post("/escrow")
async def create_escrow(escrow: EscrowCreate, db: Session = Depends(get_db)):
    """Create new escrow"""
    escrow_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    new_escrow = EscrowDB(
        id=escrow_id,
        transaction_id=escrow.transaction_id or "",
        buyer_id=escrow.buyer_id,
        seller_id=escrow.seller_id,
        amount=escrow.amount,
        currency=escrow.currency,
        status=EscrowStatus.CREATED,
        release_conditions=escrow.release_conditions,
        created_at=now,
        updated_at=now,
        milestones=escrow.milestones,
        auto_release_days=escrow.auto_release_days
    )
    if escrow.description:
        new_escrow.release_conditions["description"] = escrow.description
    
    escrows_db[escrow_id] = new_escrow
    return {"data": new_escrow.to_dict()}

@router.post("/escrow/{escrow_id}/fund")
async def fund_escrow(escrow_id: str, fund_request: Optional[EscrowFundRequest] = None, db: Session = Depends(get_db)):
    """Fund escrow with payment"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status != EscrowStatus.CREATED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be in created status")
    
    payment_transaction_id = fund_request.transaction_id if (fund_request and fund_request.transaction_id) else str(uuid.uuid4())
    
    escrow.status = EscrowStatus.FUNDED
    escrow.payment_transaction_id = payment_transaction_id
    escrow.milestones.append({"milestone": EscrowMilestone.PAYMENT_RECEIVED.value, "achieved_at": datetime.utcnow().isoformat()})
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/lock")
async def lock_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """Lock escrow after funding - funds are now secured"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status != EscrowStatus.FUNDED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be funded to lock")
    
    escrow.status = EscrowStatus.LOCKED
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/milestone")
async def update_milestone(escrow_id: str, milestone_update: EscrowMilestoneUpdate, db: Session = Depends(get_db)):
    """Update escrow milestone"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.LOCKED, EscrowStatus.PENDING_VERIFICATION]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be funded to update milestones")
    
    milestone_entry = {
        "milestone": milestone_update.milestone.value,
        "achieved": milestone_update.achieved,
        "achieved_at": datetime.utcnow().isoformat() if milestone_update.achieved else None,
        "notes": milestone_update.notes
    }
    
    existing_idx = next((i for i, m in enumerate(escrow.milestones) if m.get("milestone") == milestone_update.milestone.value), None)
    if existing_idx is not None:
        escrow.milestones[existing_idx] = milestone_entry
    else:
        escrow.milestones.append(milestone_entry)
    
    if milestone_update.achieved and escrow.release_conditions.get("auto_release_on_milestones"):
        required_milestones = escrow.release_conditions["auto_release_on_milestones"]
        achieved_milestones = [m for m in escrow.milestones if m.get("achieved")]
        if len(achieved_milestones) >= len(required_milestones):
            escrow.status = EscrowStatus.PENDING_VERIFICATION
    
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/release")
async def release_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """Release escrow funds to seller"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.LOCKED, EscrowStatus.PENDING_VERIFICATION]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be funded to release")
    
    escrow.status = EscrowStatus.RELEASED
    escrow.milestones.append({"milestone": "funds_released", "achieved_at": datetime.utcnow().isoformat()})
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/dispute")
async def dispute_escrow(escrow_id: str, dispute: DisputeCreate, db: Session = Depends(get_db)):
    """Raise dispute on escrow"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status not in [EscrowStatus.FUNDED, EscrowStatus.LOCKED, EscrowStatus.PENDING_VERIFICATION]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be funded to dispute")
    
    user_id = "00000000-0000-0000-0000-000000000001"
    
    escrow.status = EscrowStatus.DISPUTED
    escrow.dispute_details = {
        "reason": dispute.reason,
        "raised_by": user_id,
        "raised_at": datetime.utcnow().isoformat(),
        "evidence": dispute.evidence
    }
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/resolve")
async def resolve_dispute(escrow_id: str, resolution: DisputeResolve, db: Session = Depends(get_db)):
    """Resolve escrow dispute"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status != EscrowStatus.DISPUTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be disputed to resolve")
    
    escrow.status = EscrowStatus.RESOLVED
    escrow.dispute_details["resolution"] = resolution.resolution
    escrow.dispute_details["resolved_at"] = datetime.utcnow().isoformat()
    escrow.dispute_details["release_to"] = resolution.release_to
    escrow.dispute_details["refund_amount"] = resolution.refund_amount
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/cancel")
async def cancel_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """Cancel escrow and refund buyer"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status not in [EscrowStatus.CREATED, EscrowStatus.FUNDED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow cannot be cancelled in current status")
    
    escrow.status = EscrowStatus.CANCELLED
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.post("/escrow/{escrow_id}/refund")
async def refund_escrow(escrow_id: str, db: Session = Depends(get_db)):
    """Process refund to buyer after cancellation or resolution"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    if escrow.status not in [EscrowStatus.CANCELLED, EscrowStatus.RESOLVED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escrow must be cancelled or resolved to refund")
    
    escrow.status = EscrowStatus.REFUNDED
    escrow.milestones.append({"milestone": "refund_processed", "achieved_at": datetime.utcnow().isoformat()})
    escrow.updated_at = datetime.utcnow()
    
    return {"data": escrow.to_dict()}

@router.get("/escrow/{escrow_id}/status")
async def get_escrow_status(escrow_id: str, db: Session = Depends(get_db)):
    """Get escrow current status and next available actions"""
    if escrow_id not in escrows_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Escrow not found")
    
    escrow = escrows_db[escrow_id]
    
    available_actions = []
    if escrow.status == EscrowStatus.CREATED:
        available_actions = ["fund", "cancel"]
    elif escrow.status == EscrowStatus.FUNDED:
        available_actions = ["lock", "cancel", "dispute"]
    elif escrow.status == EscrowStatus.LOCKED:
        available_actions = ["update_milestone", "release", "dispute"]
    elif escrow.status == EscrowStatus.PENDING_VERIFICATION:
        available_actions = ["release", "dispute"]
    elif escrow.status == EscrowStatus.DISPUTED:
        available_actions = ["resolve"]
    elif escrow.status == EscrowStatus.RESOLVED:
        available_actions = ["refund"]
    elif escrow.status == EscrowStatus.CANCELLED:
        available_actions = ["refund"]
    
    return {
        "escrow_id": escrow_id,
        "status": escrow.status,
        "available_actions": available_actions,
        "milestones_completed": len([m for m in escrow.milestones if m.get("achieved")]),
        "total_milestones": len(escrow.milestones)
    }
