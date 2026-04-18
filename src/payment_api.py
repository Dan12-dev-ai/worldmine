"""
Payment API - Backend API for Universal Payment Hub
Provides REST endpoints for international payments and currency conversion
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from .universal_payment_hub import universal_payment_hub

class CurrencyConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class CurrencyConversionResponse(BaseModel):
    success: bool
    from_amount: float
    from_currency: str
    to_amount: float
    to_currency: str
    exchange_rate: float
    total_fee: float
    fee_percentage: float
    timestamp: str

class PaymentRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str
    payment_method: str
    country: str
    user_id: Optional[str] = None

class PaymentResponse(BaseModel):
    success: bool
    transaction_id: str
    original_amount: float
    converted_amount: float
    net_amount: float
    total_fees: float
    conversion_fee: float
    method_fee: float
    settlement_time: str
    status: str
    timestamp: str

class PaymentMethodsResponse(BaseModel):
    success: bool
    payment_methods: List[Dict[str, Any]]
    timestamp: str

class PaymentStatisticsResponse(BaseModel):
    timestamp: str
    total_transactions: int
    total_volume: float
    countries_served: int
    payment_method_usage: List[Dict[str, Any]]
    currencies_supported: int
    payment_methods_available: int
    last_exchange_rate_update: Optional[str]

# Create FastAPI app for payment hub
payment_app = FastAPI(title="DEDAN Payment Hub API", version="1.0.0")

@payment_app.get("/api/payments/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "payment_hub", "timestamp": "2024-01-01T00:00:00Z"}

@payment_app.post("/api/payments/convert", response_model=CurrencyConversionResponse)
async def convert_currency(request: CurrencyConversionRequest):
    """Convert currency with real-time exchange rates"""
    try:
        result = await universal_payment_hub.convert_currency(
            request.amount,
            request.from_currency,
            request.to_currency
        )
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payment_app.get("/api/payments/methods/{country}")
async def get_payment_methods(country: str, currency: str = None):
    """Get available payment methods for specific country"""
    try:
        methods = await universal_payment_hub.get_payment_methods_for_country(country, currency)
        return JSONResponse(content={
            "success": True,
            "payment_methods": methods,
            "timestamp": "2024-01-01T00:00:00Z"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payment_app.post("/api/payments/process", response_model=PaymentResponse)
async def process_payment(request: PaymentRequest):
    """Process international payment"""
    try:
        result = await universal_payment_hub.process_payment({
            "amount": request.amount,
            "from_currency": request.from_currency,
            "to_currency": request.to_currency,
            "payment_method": request.payment_method,
            "country": request.country,
            "user_id": request.user_id
        })
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payment_app.get("/api/payments/statistics", response_model=PaymentStatisticsResponse)
async def get_payment_statistics():
    """Get payment hub statistics"""
    try:
        stats = await universal_payment_hub.get_payment_statistics()
        return JSONResponse(content=stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payment_app.get("/api/payments/currencies")
async def get_supported_currencies():
    """Get list of supported currencies"""
    try:
        currencies = [
            {
                "code": currency.code,
                "name": currency.name,
                "symbol": currency.symbol,
                "country": currency.country,
                "region": currency.region
            }
            for currency in universal_payment_hub.supported_currencies.values()
        ]
        return JSONResponse(content={
            "success": True,
            "currencies": currencies,
            "total_supported": len(currencies)
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@payment_app.get("/api/payments/rates")
async def get_exchange_rates():
    """Get current exchange rates"""
    try:
        await universal_payment_hub.update_exchange_rates()
        rates = {
            currency.code: {
                "rate_to_usd": currency.exchange_rate,
                "last_updated": currency.last_updated
            }
            for currency in universal_payment_hub.supported_currencies.values()
        }
        return JSONResponse(content={
            "success": True,
            "base_currency": "USD",
            "rates": rates,
            "last_updated": universal_payment_hub.last_update.isoformat() if universal_payment_hub.last_update else None
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(payment_app, host="0.0.0.0", port=8002)
