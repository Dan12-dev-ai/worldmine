"""
DEDAN Mine - Pay-as-you-Earn Revenue Model (v3.1.0)
Stripe Connect for international payments + Chapa for Ethiopian payments
Zero fixed monthly costs - only pay on successful transactions
Usage-based billing with transparent pricing
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import aiohttp
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentProvider(Enum):
    """Payment providers"""
    STRIPE_CONNECT = "stripe_connect"
    CHAPA = "chapa"
    BINANCE = "binance"
    PAYONEER = "payoneer"

class TransactionType(Enum):
    """Transaction types"""
    PAYMENT = "payment"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    TRADE_FEE = "trade_fee"
    PROCESSING_FEE = "processing_fee"

class Currency(Enum):
    """Supported currencies"""
    USD = "USD"
    ETB = "ETB"
    EUR = "EUR"
    GBP = "GBP"
    CNY = "CNY"
    JPY = "JPY"
    USDT = "USDT"
    USDC = "USDC"

@dataclass
class TransactionFee:
    """Transaction fee structure"""
    provider: PaymentProvider
    transaction_type: TransactionType
    fixed_fee: float  # Fixed fee in USD
    percentage_fee: float  # Percentage fee
    minimum_fee: float  # Minimum fee in USD
    maximum_fee: Optional[float]  # Maximum fee in USD
    
    def calculate_fee(self, amount: float, currency: str = "USD") -> float:
        """Calculate fee for given amount"""
        # Convert to USD for calculation
        usd_amount = self._convert_to_usd(amount, currency)
        
        # Calculate percentage fee
        percentage_fee = usd_amount * (self.percentage_fee / 100)
        
        # Calculate total fee
        total_fee = self.fixed_fee + percentage_fee
        
        # Apply minimum and maximum limits
        total_fee = max(total_fee, self.minimum_fee)
        if self.maximum_fee:
            total_fee = min(total_fee, self.maximum_fee)
        
        # Convert back to original currency
        return self._convert_from_usd(total_fee, currency)
    
    def _convert_to_usd(self, amount: float, currency: str) -> float:
        """Convert amount to USD (mock exchange rates)"""
        exchange_rates = {
            "USD": 1.0,
            "ETB": 0.018,  # 1 ETB = 0.018 USD
            "EUR": 1.08,
            "GBP": 1.27,
            "CNY": 0.14,
            "JPY": 0.0067,
            "USDT": 1.0,
            "USDC": 1.0
        }
        return amount * exchange_rates.get(currency, 1.0)
    
    def _convert_from_usd(self, amount: float, currency: str) -> float:
        """Convert USD amount to target currency"""
        exchange_rates = {
            "USD": 1.0,
            "ETB": 55.56,  # 1 USD = 55.56 ETB
            "EUR": 0.93,
            "GBP": 0.79,
            "CNY": 7.14,
            "JPY": 149.25,
            "USDT": 1.0,
            "USDC": 1.0
        }
        return amount * exchange_rates.get(currency, 1.0)

@dataclass
class PaymentTransaction:
    """Payment transaction structure"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    provider: PaymentProvider
    transaction_type: TransactionType
    fee_amount: float
    net_amount: float
    status: str
    created_at: datetime
    processed_at: Optional[datetime]
    metadata: Dict[str, Any]
    external_id: Optional[str]

class StripeConnectManager:
    """Stripe Connect manager for international payments"""
    
    def __init__(self):
        self.secret_key = os.getenv("STRIPE_SECRET_KEY")
        self.webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        self.base_url = "https://api.stripe.com/v1"
        self.session = None
        
        # Fee structure for Stripe Connect
        self.fees = {
            TransactionType.PAYMENT: TransactionFee(
                provider=PaymentProvider.STRIPE_CONNECT,
                transaction_type=TransactionType.PAYMENT,
                fixed_fee=0.30,
                percentage_fee=2.9,
                minimum_fee=0.30,
                maximum_fee=None
            ),
            TransactionType.WITHDRAWAL: TransactionFee(
                provider=PaymentProvider.STRIPE_CONNECT,
                transaction_type=TransactionType.WITHDRAWAL,
                fixed_fee=0.25,
                percentage_fee=0.8,
                minimum_fee=0.25,
                maximum_fee=5.00
            ),
            TransactionType.TRANSFER: TransactionFee(
                provider=PaymentProvider.STRIPE_CONNECT,
                transaction_type=TransactionType.TRANSFER,
                fixed_fee=0.10,
                percentage_fee=0.5,
                minimum_fee=0.10,
                maximum_fee=2.00
            )
        }
    
    async def get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.secret_key}"}
            )
        return self.session
    
    async def create_payment_intent(self, amount: float, currency: str, user_id: str, 
                                 metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create payment intent using Stripe Connect"""
        try:
            session = await self.get_session()
            
            # Calculate fee
            fee_structure = self.fees[TransactionType.PAYMENT]
            fee_amount = fee_structure.calculate_fee(amount, currency)
            net_amount = amount - fee_amount
            
            # Create payment intent
            async with session.post(
                f"{self.base_url}/payment_intents",
                json={
                    "amount": int(amount * 100),  # Convert to cents
                    "currency": currency.lower(),
                    "metadata": metadata or {},
                    "automatic_payment_methods": {
                        "enabled": True
                    },
                    "description": f"DEDAN Mine payment for user {user_id}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "payment_intent_id": data["id"],
                        "client_secret": data["client_secret"],
                        "amount": amount,
                        "currency": currency,
                        "fee_amount": fee_amount,
                        "net_amount": net_amount,
                        "status": data["status"]
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Stripe payment intent creation failed: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"Stripe API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Stripe payment intent creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_withdrawal(self, amount: float, currency: str, user_id: str,
                            destination_account: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create withdrawal using Stripe Connect"""
        try:
            session = await self.get_session()
            
            # Calculate fee
            fee_structure = self.fees[TransactionType.WITHDRAWAL]
            fee_amount = fee_structure.calculate_fee(amount, currency)
            net_amount = amount - fee_amount
            
            # Create payout
            async with session.post(
                f"{self.base_url}/payouts",
                json={
                    "amount": int(amount * 100),  # Convert to cents
                    "currency": currency.lower(),
                    "destination": destination_account,
                    "metadata": metadata or {},
                    "description": f"DEDAN Mine withdrawal for user {user_id}"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "payout_id": data["id"],
                        "amount": amount,
                        "currency": currency,
                        "fee_amount": fee_amount,
                        "net_amount": net_amount,
                        "status": data["status"],
                        "arrival_date": data.get("arrival_date")
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Stripe withdrawal creation failed: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"Stripe API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Stripe withdrawal creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            import stripe
            return stripe.Webhook.construct_event(
                payload, signature, self.webhook_secret
            )
        except Exception as e:
            logger.error(f"Stripe webhook verification failed: {str(e)}")
            return False
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class ChapaManager:
    """Chapa manager for Ethiopian payments"""
    
    def __init__(self):
        self.api_key = os.getenv("CHAPA_API_KEY")
        self.base_url = "https://api.chapa.co/v1"
        self.session = None
        
        # Fee structure for Chapa
        self.fees = {
            TransactionType.PAYMENT: TransactionFee(
                provider=PaymentProvider.CHAPA,
                transaction_type=TransactionType.PAYMENT,
                fixed_fee=0.05,
                percentage_fee=1.5,
                minimum_fee=0.05,
                maximum_fee=10.00
            ),
            TransactionType.WITHDRAWAL: TransactionFee(
                provider=PaymentProvider.CHAPA,
                transaction_type=TransactionType.WITHDRAWAL,
                fixed_fee=0.10,
                percentage_fee=1.0,
                minimum_fee=0.10,
                maximum_fee=5.00
            )
        }
    
    async def get_session(self):
        """Get HTTP session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self.session
    
    async def initialize_payment(self, amount: float, currency: str, user_id: str,
                            email: str, phone: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Initialize payment using Chapa"""
        try:
            session = await self.get_session()
            
            # Calculate fee
            fee_structure = self.fees[TransactionType.PAYMENT]
            fee_amount = fee_structure.calculate_fee(amount, currency)
            net_amount = amount - fee_amount
            
            # Create transaction reference
            tx_ref = f"DEDAN_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
            
            # Initialize payment
            async with session.post(
                f"{self.base_url}/transaction/initialize",
                json={
                    "amount": amount,
                    "currency": currency,
                    "email": email,
                    "phone_number": phone,
                    "tx_ref": tx_ref,
                    "callback_url": "https://dedanmine.io/api/payments/chapa/callback",
                    "return_url": "https://dedanmine.io/payments/success",
                    "customization": {
                        "title": "DEDAN Mine Payment",
                        "description": f"Payment for user {user_id}"
                    },
                    "meta": metadata or {}
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "checkout_url": data["data"]["checkout_url"],
                        "tx_ref": tx_ref,
                        "amount": amount,
                        "currency": currency,
                        "fee_amount": fee_amount,
                        "net_amount": net_amount
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Chapa payment initialization failed: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"Chapa API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Chapa payment initialization failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def verify_transaction(self, tx_ref: str) -> Dict[str, Any]:
        """Verify transaction using Chapa"""
        try:
            session = await self.get_session()
            
            async with session.get(
                f"{self.base_url}/transaction/verify/{tx_ref}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    return {
                        "success": True,
                        "verified": data["data"]["status"] == "success",
                        "amount": data["data"]["amount"],
                        "currency": data["data"]["currency"],
                        "tx_ref": tx_ref
                    }
                else:
                    error_data = await response.text()
                    logger.error(f"Chapa transaction verification failed: {response.status} - {error_data}")
                    return {
                        "success": False,
                        "error": f"Chapa API error: {response.status}"
                    }
                    
        except Exception as e:
            logger.error(f"Chapa transaction verification failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close session"""
        if self.session:
            await self.session.close()

class PayAsYouEarnManager:
    """Pay-as-you-earn revenue model manager"""
    
    def __init__(self):
        self.stripe_manager = StripeConnectManager()
        self.chapa_manager = ChapaManager()
        
        # Transaction storage (in production, use database)
        self.transactions = {}
        
        # Revenue tracking
        self.daily_revenue = 0.0
        self.monthly_revenue = 0.0
        self.total_revenue = 0.0
        
        # Cost tracking
        self.daily_costs = 0.0
        self.monthly_costs = 0.0
        self.total_costs = 0.0
        
        # Provider preferences
        self.provider_preferences = {
            "international": PaymentProvider.STRIPE_CONNECT,
            "ethiopia": PaymentProvider.CHAPA,
            "crypto": PaymentProvider.BINANCE
        }
    
    async def create_payment(self, user_id: str, amount: float, currency: str,
                         payment_method: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create payment using appropriate provider"""
        try:
            # Determine provider based on currency and user location
            provider = self._determine_provider(currency, payment_method, metadata)
            
            transaction_id = f"PAY_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
            
            if provider == PaymentProvider.STRIPE_CONNECT:
                result = await self.stripe_manager.create_payment_intent(
                    amount, currency, user_id, metadata
                )
            elif provider == PaymentProvider.CHAPA:
                # Chapa requires email and phone
                email = metadata.get("email", "")
                phone = metadata.get("phone", "")
                result = await self.chapa_manager.initialize_payment(
                    amount, currency, user_id, email, phone, metadata
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported payment provider: {provider.value}"
                }
            
            if result["success"]:
                # Create transaction record
                transaction = PaymentTransaction(
                    transaction_id=transaction_id,
                    user_id=user_id,
                    amount=amount,
                    currency=currency,
                    provider=provider,
                    transaction_type=TransactionType.PAYMENT,
                    fee_amount=result["fee_amount"],
                    net_amount=result["net_amount"],
                    status="pending",
                    created_at=datetime.now(timezone.utc),
                    processed_at=None,
                    metadata=metadata or {},
                    external_id=result.get("payment_intent_id") or result.get("tx_ref")
                )
                
                self.transactions[transaction_id] = transaction
                
                # Update revenue tracking
                self.daily_revenue += result["fee_amount"]
                self.monthly_revenue += result["fee_amount"]
                self.total_revenue += result["fee_amount"]
                
                result["transaction_id"] = transaction_id
                result["provider"] = provider.value
            
            return result
            
        except Exception as e:
            logger.error(f"Payment creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_withdrawal(self, user_id: str, amount: float, currency: str,
                             destination: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create withdrawal using appropriate provider"""
        try:
            # Determine provider based on currency and destination
            provider = self._determine_provider(currency, "withdrawal", metadata)
            
            transaction_id = f"WD_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
            
            if provider == PaymentProvider.STRIPE_CONNECT:
                result = await self.stripe_manager.create_withdrawal(
                    amount, currency, user_id, destination, metadata
                )
            elif provider == PaymentProvider.CHAPA:
                # Chapa withdrawal (bank transfer)
                result = await self.chapa_manager.initialize_payment(
                    amount, currency, user_id, 
                    metadata.get("email", ""), 
                    metadata.get("phone", ""), 
                    metadata
                )
            else:
                return {
                    "success": False,
                    "error": f"Unsupported withdrawal provider: {provider.value}"
                }
            
            if result["success"]:
                # Create transaction record
                transaction = PaymentTransaction(
                    transaction_id=transaction_id,
                    user_id=user_id,
                    amount=amount,
                    currency=currency,
                    provider=provider,
                    transaction_type=TransactionType.WITHDRAWAL,
                    fee_amount=result["fee_amount"],
                    net_amount=result["net_amount"],
                    status="pending",
                    created_at=datetime.now(timezone.utc),
                    processed_at=None,
                    metadata=metadata or {},
                    external_id=result.get("payout_id") or result.get("tx_ref")
                )
                
                self.transactions[transaction_id] = transaction
                
                # Update revenue tracking (withdrawals also generate fees)
                self.daily_revenue += result["fee_amount"]
                self.monthly_revenue += result["fee_amount"]
                self.total_revenue += result["fee_amount"]
                
                result["transaction_id"] = transaction_id
                result["provider"] = provider.value
            
            return result
            
        except Exception as e:
            logger.error(f"Withdrawal creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _determine_provider(self, currency: str, payment_method: str, metadata: Dict[str, Any]) -> PaymentProvider:
        """Determine appropriate payment provider"""
        # Ethiopian payments use Chapa
        if currency == "ETB" or metadata.get("country") == "ET":
            return PaymentProvider.CHAPA
        
        # International payments use Stripe Connect
        if currency in ["USD", "EUR", "GBP"]:
            return PaymentProvider.STRIPE_CONNECT
        
        # Default to Stripe Connect
        return PaymentProvider.STRIPE_CONNECT
    
    async def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """Get transaction status"""
        try:
            transaction = self.transactions.get(transaction_id)
            
            if not transaction:
                return {
                    "success": False,
                    "error": f"Transaction not found: {transaction_id}"
                }
            
            # Check status with provider
            if transaction.provider == PaymentProvider.STRIPE_CONNECT:
                # In production, check Stripe API
                pass
            elif transaction.provider == PaymentProvider.CHAPA:
                # Check Chapa API
                if transaction.external_id:
                    result = await self.chapa_manager.verify_transaction(transaction.external_id)
                    if result["success"] and result["verified"]:
                        transaction.status = "completed"
                        transaction.processed_at = datetime.now(timezone.utc)
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "status": transaction.status,
                "provider": transaction.provider.value,
                "amount": transaction.amount,
                "currency": transaction.currency,
                "fee_amount": transaction.fee_amount,
                "net_amount": transaction.net_amount,
                "created_at": transaction.created_at.isoformat(),
                "processed_at": transaction.processed_at.isoformat() if transaction.processed_at else None
            }
            
        except Exception as e:
            logger.error(f"Transaction status check failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_revenue_stats(self) -> Dict[str, Any]:
        """Get revenue statistics"""
        return {
            "daily_revenue": self.daily_revenue,
            "monthly_revenue": self.monthly_revenue,
            "total_revenue": self.total_revenue,
            "daily_costs": self.daily_costs,
            "monthly_costs": self.monthly_costs,
            "total_costs": self.total_costs,
            "net_profit": self.total_revenue - self.total_costs,
            "transaction_count": len(self.transactions),
            "providers": {
                "stripe_connect": len([t for t in self.transactions.values() if t.provider == PaymentProvider.STRIPE_CONNECT]),
                "chapa": len([t for t in self.transactions.values() if t.provider == PaymentProvider.CHAPA])
            },
            "model": "pay_as_you_earn",
            "no_fixed_costs": True,
            "usage_based_billing": True
        }
    
    def get_fee_schedule(self) -> Dict[str, Any]:
        """Get fee schedule for all providers"""
        return {
            "stripe_connect": {
                "payment": {
                    "fixed_fee": self.stripe_manager.fees[TransactionType.PAYMENT].fixed_fee,
                    "percentage_fee": self.stripe_manager.fees[TransactionType.PAYMENT].percentage_fee,
                    "minimum_fee": self.stripe_manager.fees[TransactionType.PAYMENT].minimum_fee
                },
                "withdrawal": {
                    "fixed_fee": self.stripe_manager.fees[TransactionType.WITHDRAWAL].fixed_fee,
                    "percentage_fee": self.stripe_manager.fees[TransactionType.WITHDRAWAL].percentage_fee,
                    "minimum_fee": self.stripe_manager.fees[TransactionType.WITHDRAWAL].minimum_fee,
                    "maximum_fee": self.stripe_manager.fees[TransactionType.WITHDRAWAL].maximum_fee
                }
            },
            "chapa": {
                "payment": {
                    "fixed_fee": self.chapa_manager.fees[TransactionType.PAYMENT].fixed_fee,
                    "percentage_fee": self.chapa_manager.fees[TransactionType.PAYMENT].percentage_fee,
                    "minimum_fee": self.chapa_manager.fees[TransactionType.PAYMENT].minimum_fee,
                    "maximum_fee": self.chapa_manager.fees[TransactionType.PAYMENT].maximum_fee
                },
                "withdrawal": {
                    "fixed_fee": self.chapa_manager.fees[TransactionType.WITHDRAWAL].fixed_fee,
                    "percentage_fee": self.chapa_manager.fees[TransactionType.WITHDRAWAL].percentage_fee,
                    "minimum_fee": self.chapa_manager.fees[TransactionType.WITHDRAWAL].minimum_fee,
                    "maximum_fee": self.chapa_manager.fees[TransactionType.WITHDRAWAL].maximum_fee
                }
            }
        }
    
    async def close(self):
        """Close all manager sessions"""
        await self.stripe_manager.close()
        await self.chapa_manager.close()

# Global instance
pay_as_you_earn = PayAsYouEarnManager()

# API endpoints
async def create_payment_api(user_id: str, amount: float, currency: str,
                          payment_method: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """API endpoint for creating payments"""
    return await pay_as_you_earn.create_payment(user_id, amount, currency, payment_method, metadata)

async def create_withdrawal_api(user_id: str, amount: float, currency: str,
                               destination: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """API endpoint for creating withdrawals"""
    return await pay_as_you_earn.create_withdrawal(user_id, amount, currency, destination, metadata)

async def get_transaction_status_api(transaction_id: str) -> Dict[str, Any]:
    """API endpoint for transaction status"""
    return await pay_as_you_earn.get_transaction_status(transaction_id)

async def get_revenue_stats_api() -> Dict[str, Any]:
    """API endpoint for revenue statistics"""
    return pay_as_you_earn.get_revenue_stats()

async def get_fee_schedule_api() -> Dict[str, Any]:
    """API endpoint for fee schedule"""
    return pay_as_you_earn.get_fee_schedule()
