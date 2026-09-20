"""
Payment API
REST endpoints for payment processing using the Universal Payment Hub
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/payments", tags=["Payments"])
# Compatibility router matching the legacy singular prefix used by
# `/api/payment/...` clients.
payment_compat_router = APIRouter(prefix="/api/payment", tags=["Payments"], include_in_schema=False)


# Models
class PaymentRequest(BaseModel):
    """Payment request"""
    user_id: Optional[str] = Field(default="00000000-0000-0000-0000-000000000001")
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    provider: Optional[str] = None
    payment_method: Optional[str] = Field(default=None, description="stripe, adyen, apple_pay, google_pay, sepa, ideal, pix, alipay, telebirr")
    customer_ip: Optional[str] = None
    customer_country: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PaymentResponse(BaseModel):
    """Payment response"""
    request_id: str
    transaction_id: str
    status: str
    amount_usd: float
    original_amount: float
    original_currency: str
    exchange_rate: float
    provider: str
    created_at: datetime
    payment_url: Optional[str] = None
    client_secret: Optional[str] = None


class WithdrawalRequest(BaseModel):
    """Withdrawal request"""
    user_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field(default="USD")
    withdrawal_rail: str = Field(description="swift, stablecoin, payoneer, local_local")
    destination_address: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WithdrawalResponse(BaseModel):
    """Withdrawal response"""
    request_id: str
    transaction_id: str
    status: str
    amount: float
    currency: str
    rail: str
    estimated_arrival: Optional[str] = None
    created_at: datetime


class RefundRequest(BaseModel):
    """Refund request"""
    transaction_id: str
    amount: Optional[float] = None
    reason: str


class RefundResponse(BaseModel):
    """Refund response"""
    refund_id: str
    transaction_id: str
    status: str
    amount: float
    created_at: datetime


class Transaction(BaseModel):
    """Transaction details"""
    transaction_id: str
    user_id: str
    type: str
    amount: float
    currency: str
    status: str
    provider: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict)


# In-memory storage
transactions: Dict[str, Transaction] = {}
payment_requests: Dict[str, PaymentRequest] = {}


# Endpoints
@router.post("/create-payment", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(request: PaymentRequest):
    """Create a new payment request"""
    return _create_payment_impl(request)


@payment_compat_router.post("/payments")
@payment_compat_router.post("/create-payment", response_model=PaymentResponse, status_code=status.HTTP_200_OK)
async def create_payment_compat(request: PaymentRequest):
    """Create payment — legacy path, returns the {data: ...} envelope"""
    payment = _create_payment_impl(request)
    return {"data": jsonable_encoder(payment)}


def _create_payment_impl(request: PaymentRequest) -> PaymentResponse:
    request_id = str(uuid.uuid4())
    transaction_id = str(uuid.uuid4())
    
    payment_requests[request_id] = request
    
    response = PaymentResponse(
        request_id=request_id,
        transaction_id=transaction_id,
        status="pending",
        amount_usd=request.amount,
        original_amount=request.amount,
        original_currency=request.currency,
        exchange_rate=1.0,
        provider=request.payment_method or request.provider or "stripe",
        created_at=datetime.utcnow(),
        payment_url=f"https://payment.example.com/pay/{transaction_id}"
    )
    
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=request.user_id,
        type="payment",
        amount=request.amount,
        currency=request.currency,
        status="pending",
        provider=request.payment_method or request.provider or "stripe",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata=request.metadata
    )
    transactions[transaction_id] = transaction
    
    return response


@router.get("/payment/{request_id}", response_model=PaymentResponse)
async def get_payment(request_id: str):
    """Get payment request details"""
    if request_id not in payment_requests:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Payment request with ID '{request_id}' not found")
    
    request = payment_requests[request_id]
    
    transaction = None
    for tx in transactions.values():
        if tx.type == "payment" and tx.user_id == request.user_id:
            transaction = tx
            break
    
    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction not found for payment request '{request_id}'")
    
    return PaymentResponse(
        request_id=request_id,
        transaction_id=transaction.transaction_id,
        status=transaction.status,
        amount_usd=request.amount,
        original_amount=request.amount,
        original_currency=request.currency,
        exchange_rate=1.0,
        provider=request.payment_method,
        created_at=transaction.created_at
    )


@router.post("/create-withdrawal", response_model=WithdrawalResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(request: WithdrawalRequest):
    """Create a withdrawal request"""
    request_id = str(uuid.uuid4())
    transaction_id = str(uuid.uuid4())
    
    transaction = Transaction(
        transaction_id=transaction_id,
        user_id=request.user_id,
        type="withdrawal",
        amount=request.amount,
        currency=request.currency,
        status="pending",
        provider=request.withdrawal_rail,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata=request.metadata
    )
    transactions[transaction_id] = transaction
    
    response = WithdrawalResponse(
        request_id=request_id,
        transaction_id=transaction_id,
        status="pending",
        amount=request.amount,
        currency=request.currency,
        rail=request.withdrawal_rail,
        estimated_arrival="3-5 business days",
        created_at=datetime.utcnow()
    )
    
    return response


@router.post("/refund", response_model=RefundResponse, status_code=status.HTTP_201_CREATED)
async def create_refund(request: RefundRequest):
    """Create a refund request"""
    if request.transaction_id not in transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID '{request.transaction_id}' not found")
    
    transaction = transactions[request.transaction_id]
    
    if transaction.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot refund transaction with status '{transaction.status}'")
    
    refund_id = str(uuid.uuid4())
    refund_amount = request.amount if request.amount else transaction.amount
    
    refund_transaction = Transaction(
        transaction_id=refund_id,
        user_id=transaction.user_id,
        type="refund",
        amount=refund_amount,
        currency=transaction.currency,
        status="pending",
        provider=transaction.provider,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={"original_transaction_id": request.transaction_id, "reason": request.reason}
    )
    transactions[refund_id] = refund_transaction
    
    response = RefundResponse(
        refund_id=refund_id,
        transaction_id=request.transaction_id,
        status="pending",
        amount=refund_amount,
        created_at=datetime.utcnow()
    )
    
    return response


@router.get("/transactions", response_model=List[Transaction])
@payment_compat_router.get("/transactions", response_model=List[Transaction])
async def list_transactions(
    user_id: Optional[str] = None,
    transaction_type: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
):
    """List transactions with optional filtering"""
    tx_list = list(transactions.values())
    
    if user_id:
        tx_list = [tx for tx in tx_list if tx.user_id == user_id]
    if transaction_type:
        tx_list = [tx for tx in tx_list if tx.type == transaction_type]
    if status:
        tx_list = [tx for tx in tx_list if tx.status == status]
    
    tx_list.sort(key=lambda x: x.created_at, reverse=True)
    
    return tx_list[skip:skip + limit]


@router.get("/transactions/{transaction_id}", response_model=Transaction)
async def get_transaction(transaction_id: str):
    """Get transaction details"""
    if transaction_id not in transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID '{transaction_id}' not found")
    
    return transactions[transaction_id]


@router.put("/transactions/{transaction_id}/status")
async def update_transaction_status(transaction_id: str, new_status: str):
    """Update transaction status (webhook endpoint)"""
    if transaction_id not in transactions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Transaction with ID '{transaction_id}' not found")
    
    valid_statuses = ["pending", "processing", "completed", "failed", "cancelled", "refunded"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
    
    transactions[transaction_id].status = new_status
    transactions[transaction_id].updated_at = datetime.utcnow()
    
    return {"message": f"Transaction status updated to {new_status}"}


@router.get("/user/{user_id}/balance")
async def get_user_balance(user_id: str):
    """Get user's available balance"""
    user_transactions = [
        tx for tx in transactions.values()
        if tx.user_id == user_id and tx.status == "completed"
    ]
    
    balance = sum(
        tx.amount if tx.type == "payment" else -tx.amount
        for tx in user_transactions
    )
    
    return {
        "user_id": user_id,
        "balance": balance,
        "currency": "USD",
        "transaction_count": len(user_transactions)
    }


@router.get("/providers")
async def list_payment_providers():
    """List available payment providers"""
    providers = [
        {"id": "stripe", "name": "Stripe", "currencies": ["USD", "EUR", "GBP"]},
        {"id": "adyen", "name": "Adyen", "currencies": ["USD", "EUR", "GBP", "JPY"]},
        {"id": "apple_pay", "name": "Apple Pay", "currencies": ["USD", "EUR", "GBP"]},
        {"id": "google_pay", "name": "Google Pay", "currencies": ["USD", "EUR", "GBP"]},
        {"id": "sepa", "name": "SEPA", "currencies": ["EUR"]},
        {"id": "ideal", "name": "iDEAL", "currencies": ["EUR"]},
        {"id": "pix", "name": "PIX", "currencies": ["BRL"]},
        {"id": "alipay", "name": "Alipay", "currencies": ["CNY"]},
        {"id": "telebirr", "name": "Telebirr", "currencies": ["ETB"]}
    ]
    
    return {"providers": providers}


@router.get("/currencies")
async def list_supported_currencies():
    """List supported currencies"""
    currencies = [
        {"code": "USD", "name": "US Dollar", "symbol": "$"},
        {"code": "EUR", "name": "Euro", "symbol": "€"},
        {"code": "GBP", "name": "British Pound", "symbol": "£"},
        {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
        {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
        {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
        {"code": "CHF", "name": "Swiss Franc", "symbol": "Fr"},
        {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
        {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
        {"code": "BRL", "name": "Brazilian Real", "symbol": "R$"},
        {"code": "MXN", "name": "Mexican Peso", "symbol": "$"},
        {"code": "ZAR", "name": "South African Rand", "symbol": "R"},
        {"code": "ETB", "name": "Ethiopian Birr", "symbol": "Br"}
    ]
    
    return {"currencies": currencies}
