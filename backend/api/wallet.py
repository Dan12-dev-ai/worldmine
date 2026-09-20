"""
World-Mine Wallet API
Production-ready wallet endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

from models import Wallet, Transaction
from database import get_db

router = APIRouter(prefix="/api/wallet", tags=["wallet"])


def serialize_wallet(wallet: Wallet) -> Dict[str, Any]:
    """Serialize a Wallet ORM object into a JSON-safe API payload."""
    return jsonable_encoder({
        "id": str(wallet.id),
        "user_id": str(wallet.user_id),
        "wallet_type": wallet.wallet_type,
        "currency": wallet.currency,
        "balance": wallet.balance,
        "frozen_balance": wallet.frozen_balance,
        "is_active": wallet.is_active,
        "created_at": wallet.created_at.isoformat() if wallet.created_at else None,
        "updated_at": wallet.updated_at.isoformat() if wallet.updated_at else None,
    })


def serialize_transaction(txn: Transaction) -> Dict[str, Any]:
    """Serialize a Transaction ORM object into a JSON-safe API payload."""
    return jsonable_encoder({
        "id": str(txn.id),
        "wallet_id": str(txn.wallet_id),
        "type": txn.type,
        "amount": txn.amount,
        "currency": txn.currency,
        "status": txn.status,
        "completed_at": txn.completed_at.isoformat() if txn.completed_at else None,
        "metadata": txn.txn_metadata or {},
        "created_at": txn.created_at.isoformat() if txn.created_at else None,
        "updated_at": txn.updated_at.isoformat() if txn.updated_at else None,
    })


# Request/Response Models
class WalletCreate(BaseModel):
    wallet_type: str
    currency: str

class DepositCreate(BaseModel):
    wallet_id: str
    amount: float
    payment_method: str

class WithdrawalCreate(BaseModel):
    wallet_id: str
    amount: float
    destination_address: str
    payment_method: str

class TransferCreate(BaseModel):
    from_wallet_id: str
    to_wallet_id: str
    amount: float

# Wallet Endpoints
@router.get("/wallets")
async def get_wallets(db: Session = Depends(get_db)):
    """Get all user wallets"""
    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
    return {"data": [serialize_wallet(w) for w in wallets]}

@router.get("/wallets/{wallet_id}")
async def get_wallet(wallet_id: str, db: Session = Depends(get_db)):
    """Get single wallet by ID"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"data": serialize_wallet(wallet)}

@router.post("/wallets")
async def create_wallet(wallet: WalletCreate, db: Session = Depends(get_db)):
    """Create new wallet"""
    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    new_wallet = Wallet(
        user_id=user_id,
        wallet_type=wallet.wallet_type,
        currency=wallet.currency,
        balance=0.0,
        frozen_balance=0.0,
        is_active=True
    )

    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)

    return {"data": serialize_wallet(new_wallet)}

@router.get("/wallets/{wallet_id}/balance")
async def get_wallet_balance(wallet_id: str, db: Session = Depends(get_db)):
    """Get wallet balance"""
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {
        "data": {
            "available": wallet.balance,
            "frozen": wallet.frozen_balance,
            "total": wallet.balance + wallet.frozen_balance
        }
    }

# Transaction Endpoints
@router.get("/transactions")
async def get_transactions(
    wallet_id: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get transactions with filters"""
    # TODO: Get user_id from auth token
    user_id = "00000000-0000-0000-0000-000000000001"  # Placeholder

    query = db.query(Transaction).join(Wallet).filter(Wallet.user_id == user_id)

    if wallet_id:
        query = query.filter(Transaction.wallet_id == wallet_id)
    if type:
        query = query.filter(Transaction.type == type)
    if status:
        query = query.filter(Transaction.status == status)

    transactions = query.limit(limit).all()
    total = query.count()

    return {
        "data": [serialize_transaction(t) for t in transactions],
        "total": total
    }

# Deposit Endpoints
@router.post("/deposits")
async def create_deposit(deposit: DepositCreate, db: Session = Depends(get_db)):
    """Create deposit transaction"""
    wallet = db.query(Wallet).filter(Wallet.id == deposit.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    transaction = Transaction(
        wallet_id=deposit.wallet_id,
        type="deposit",
        amount=deposit.amount,
        currency=wallet.currency,
        status="pending",
        txn_metadata={"payment_method": deposit.payment_method}
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # TODO: Integrate with actual payment provider (Stripe, Wise, etc.)
    # For now, return mock payment URL
    return {
        "data": {
            "transaction_id": str(transaction.id),
            "payment_url": f"https://payment-provider.example.com/pay/{transaction.id}"
        }
    }

# Withdrawal Endpoints
@router.post("/withdrawals")
async def create_withdrawal(withdrawal: WithdrawalCreate, db: Session = Depends(get_db)):
    """Create withdrawal transaction"""
    wallet = db.query(Wallet).filter(Wallet.id == withdrawal.wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if wallet.balance < withdrawal.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Freeze the amount
    wallet.balance -= withdrawal.amount
    wallet.frozen_balance += withdrawal.amount

    transaction = Transaction(
        wallet_id=withdrawal.wallet_id,
        type="withdrawal",
        amount=withdrawal.amount,
        currency=wallet.currency,
        status="pending",
        txn_metadata={
            "destination_address": withdrawal.destination_address,
            "payment_method": withdrawal.payment_method
        }
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {"data": {"transaction_id": str(transaction.id)}}

# Transfer Endpoints
@router.post("/transfers")
async def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    """Create transfer transaction"""
    from_wallet = db.query(Wallet).filter(Wallet.id == transfer.from_wallet_id).first()
    to_wallet = db.query(Wallet).filter(Wallet.id == transfer.to_wallet_id).first()

    if not from_wallet or not to_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if from_wallet.currency != to_wallet.currency:
        raise HTTPException(status_code=400, detail="Currency mismatch")

    if from_wallet.balance < transfer.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Deduct from source wallet
    from_wallet.balance -= transfer.amount

    # Add to destination wallet
    to_wallet.balance += transfer.amount

    # Create transaction record
    transaction = Transaction(
        wallet_id=transfer.from_wallet_id,
        type="transfer",
        amount=transfer.amount,
        currency=from_wallet.currency,
        status="completed",
        completed_at=datetime.utcnow(),
        txn_metadata={"to_wallet_id": transfer.to_wallet_id}
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return {"data": {"transaction_id": str(transaction.id)}}
