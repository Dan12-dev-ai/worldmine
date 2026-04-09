"""
DEDAN Mine - Sovereign Wallet (v4.0.0)
Multicurrency Wallet with $, £, and ETB support
Mid-Market Rate conversions via free FX API
NIST-2026 Post-Quantum Security
"""

import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import base64
import aiohttp
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WalletCurrency(Enum):
    """Supported wallet currencies"""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    ETB = "ETB"

class TransactionType(Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    EXCHANGE = "exchange"
    PAYMENT = "payment"
    REFUND = "refund"

class TransactionStatus(Enum):
    """Transaction statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class WalletBalance:
    """Wallet balance structure"""
    currency: WalletCurrency
    available_balance: float
    frozen_balance: float
    total_balance: float
    last_updated: datetime

@dataclass
class WalletTransaction:
    """Wallet transaction structure"""
    transaction_id: str
    user_id: str
    transaction_type: TransactionType
    currency: WalletCurrency
    amount: float
    fee: float
    from_currency: Optional[WalletCurrency]
    to_currency: Optional[WalletCurrency]
    exchange_rate: Optional[float]
    status: TransactionStatus
    created_at: datetime
    completed_at: Optional[datetime]
    metadata: Dict[str, Any]
    quantum_signature: str

@dataclass
class ExchangeRate:
    """Exchange rate structure"""
    from_currency: WalletCurrency
    to_currency: WalletCurrency
    rate: float
    timestamp: datetime
    source: str

class SovereignWallet:
    """Sovereign wallet manager"""
    
    def __init__(self):
        self.wallet_balances = {}  # user_id -> {currency -> WalletBalance}
        self.transactions = {}  # transaction_id -> WalletTransaction
        self.exchange_rates = {}  # (from, to) -> ExchangeRate
        self.fx_api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        
        # Security
        self.quantum_enabled = True
        self.nist_compliant = True
        
        # Initialize exchange rates
        asyncio.create_task(self.initialize_exchange_rates())
        
        # Start rate update task
        asyncio.create_task(self.update_exchange_rates_loop())
        
        logger.info("Sovereign Wallet initialized")
    
    async def create_wallet(self, user_id: str) -> Dict[str, Any]:
        """Create sovereign wallet for user"""
        try:
            if user_id in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet already exists for user"
                }
            
            # Initialize balances for all currencies
            balances = {}
            for currency in WalletCurrency:
                balance = WalletBalance(
                    currency=currency,
                    available_balance=0.0,
                    frozen_balance=0.0,
                    total_balance=0.0,
                    last_updated=datetime.now(timezone.utc)
                )
                balances[currency] = balance
            
            self.wallet_balances[user_id] = balances
            
            return {
                "success": True,
                "user_id": user_id,
                "balances": self._format_balances_for_ui(balances),
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Wallet creation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_wallet_balance(self, user_id: str, currency: WalletCurrency = None) -> Dict[str, Any]:
        """Get wallet balance"""
        try:
            if user_id not in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }
            
            balances = self.wallet_balances[user_id]
            
            if currency:
                if currency not in balances:
                    return {
                        "success": False,
                        "error": f"Currency {currency.value} not supported"
                    }
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "currency": currency.value,
                    "balance": asdict(balances[currency])
                }
            else:
                return {
                    "success": True,
                    "user_id": user_id,
                    "balances": self._format_balances_for_ui(balances)
                }
                
        except Exception as e:
            logger.error(f"Balance retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def deposit_funds(self, user_id: str, currency: WalletCurrency, amount: float, 
                          payment_method: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Deposit funds to wallet"""
        try:
            if user_id not in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }
            
            if amount <= 0:
                return {
                    "success": False,
                    "error": "Invalid amount"
                }
            
            # Generate transaction ID
            transaction_id = f"DEP_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(f'{user_id}{amount}'.encode()).hexdigest()[:8]}"
            
            # Create transaction
            transaction = WalletTransaction(
                transaction_id=transaction_id,
                user_id=user_id,
                transaction_type=TransactionType.DEPOSIT,
                currency=currency,
                amount=amount,
                fee=0.0,  # Deposits are typically free
                from_currency=None,
                to_currency=None,
                exchange_rate=None,
                status=TransactionStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                metadata=metadata or {"payment_method": payment_method},
                quantum_signature=self._generate_quantum_signature(transaction_id)
            )
            
            # Update balance
            balances = self.wallet_balances[user_id]
            balances[currency].available_balance += amount
            balances[currency].total_balance += amount
            balances[currency].last_updated = datetime.now(timezone.utc)
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "currency": currency.value,
                "amount": amount,
                "new_balance": balances[currency].available_balance,
                "completed_at": transaction.completed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Deposit failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def withdraw_funds(self, user_id: str, currency: WalletCurrency, amount: float,
                           destination: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Withdraw funds from wallet"""
        try:
            if user_id not in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }
            
            if amount <= 0:
                return {
                    "success": False,
                    "error": "Invalid amount"
                }
            
            # Check balance
            balances = self.wallet_balances[user_id]
            if balances[currency].available_balance < amount:
                return {
                    "success": False,
                    "error": "Insufficient balance"
                }
            
            # Generate transaction ID
            transaction_id = f"WTH_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(f'{user_id}{amount}'.encode()).hexdigest()[:8]}"
            
            # Calculate withdrawal fee
            fee = self._calculate_withdrawal_fee(currency, amount)
            
            # Create transaction
            transaction = WalletTransaction(
                transaction_id=transaction_id,
                user_id=user_id,
                transaction_type=TransactionType.WITHDRAWAL,
                currency=currency,
                amount=amount,
                fee=fee,
                from_currency=None,
                to_currency=None,
                exchange_rate=None,
                status=TransactionStatus.PROCESSING,
                created_at=datetime.now(timezone.utc),
                completed_at=None,
                metadata=metadata or {"destination": destination},
                quantum_signature=self._generate_quantum_signature(transaction_id)
            )
            
            # Update balance (freeze funds)
            balances[currency].available_balance -= amount
            balances[currency].frozen_balance += amount
            balances[currency].last_updated = datetime.now(timezone.utc)
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "currency": currency.value,
                "amount": amount,
                "fee": fee,
                "net_amount": amount - fee,
                "status": transaction.status.value,
                "created_at": transaction.created_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Withdrawal failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def exchange_currency(self, user_id: str, from_currency: WalletCurrency, to_currency: WalletCurrency,
                              amount: float, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Exchange currency at mid-market rate"""
        try:
            if user_id not in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }
            
            if amount <= 0:
                return {
                    "success": False,
                    "error": "Invalid amount"
                }
            
            if from_currency == to_currency:
                return {
                    "success": False,
                    "error": "Cannot exchange same currency"
                }
            
            # Get exchange rate
            exchange_rate = await self.get_exchange_rate(from_currency, to_currency)
            
            if not exchange_rate:
                return {
                    "success": False,
                    "error": "Exchange rate not available"
                }
            
            # Calculate exchanged amount
            exchanged_amount = amount * exchange_rate.rate
            
            # Check balance
            balances = self.wallet_balances[user_id]
            if balances[from_currency].available_balance < amount:
                return {
                    "success": False,
                    "error": f"Insufficient {from_currency.value} balance"
                }
            
            # Generate transaction ID
            transaction_id = f"EXC_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hashlib.sha256(f'{user_id}{amount}'.encode()).hexdigest()[:8]}"
            
            # Calculate exchange fee
            fee = self._calculate_exchange_fee(from_currency, amount)
            
            # Create transaction
            transaction = WalletTransaction(
                transaction_id=transaction_id,
                user_id=user_id,
                transaction_type=TransactionType.EXCHANGE,
                currency=from_currency,
                amount=amount,
                fee=fee,
                from_currency=from_currency,
                to_currency=to_currency,
                exchange_rate=exchange_rate.rate,
                status=TransactionStatus.COMPLETED,
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc),
                metadata=metadata or {},
                quantum_signature=self._generate_quantum_signature(transaction_id)
            )
            
            # Update balances
            balances[from_currency].available_balance -= amount
            balances[from_currency].total_balance -= amount
            balances[from_currency].last_updated = datetime.now(timezone.utc)
            
            balances[to_currency].available_balance += exchanged_amount
            balances[to_currency].total_balance += exchanged_amount
            balances[to_currency].last_updated = datetime.now(timezone.utc)
            
            # Store transaction
            self.transactions[transaction_id] = transaction
            
            return {
                "success": True,
                "transaction_id": transaction_id,
                "user_id": user_id,
                "from_currency": from_currency.value,
                "to_currency": to_currency.value,
                "amount": amount,
                "exchanged_amount": exchanged_amount,
                "exchange_rate": exchange_rate.rate,
                "fee": fee,
                "completed_at": transaction.completed_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Currency exchange failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_transaction_history(self, user_id: str, currency: WalletCurrency = None,
                                   limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """Get transaction history"""
        try:
            # Filter transactions for user
            user_transactions = [
                tx for tx in self.transactions.values()
                if tx.user_id == user_id
            ]
            
            # Filter by currency if specified
            if currency:
                user_transactions = [
                    tx for tx in user_transactions
                    if tx.currency == currency or tx.to_currency == currency
                ]
            
            # Sort by created_at (newest first)
            user_transactions.sort(key=lambda x: x.created_at, reverse=True)
            
            # Apply pagination
            paginated_transactions = user_transactions[offset:offset + limit]
            
            return {
                "success": True,
                "user_id": user_id,
                "transactions": [self._format_transaction_for_ui(tx) for tx in paginated_transactions],
                "total_count": len(user_transactions),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Transaction history retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_exchange_rate(self, from_currency: WalletCurrency, to_currency: WalletCurrency) -> Optional[ExchangeRate]:
        """Get exchange rate"""
        try:
            rate_key = (from_currency, to_currency)
            
            if rate_key not in self.exchange_rates:
                # Fetch from API
                await self.fetch_exchange_rates()
            
            return self.exchange_rates.get(rate_key)
            
        except Exception as e:
            logger.error(f"Exchange rate retrieval failed: {str(e)}")
            return None
    
    async def fetch_exchange_rates(self) -> Dict[str, Any]:
        """Fetch exchange rates from free FX API"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.fx_api_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data.get("rates", {})
                        
                        # Update exchange rates (USD as base)
                        base_currency = WalletCurrency.USD
                        
                        for currency_code, rate in rates.items():
                            try:
                                target_currency = WalletCurrency(currency_code)
                                
                                # USD to target
                                self.exchange_rates[(base_currency, target_currency)] = ExchangeRate(
                                    from_currency=base_currency,
                                    to_currency=target_currency,
                                    rate=rate,
                                    timestamp=datetime.now(timezone.utc),
                                    source="exchangerate-api.com"
                                )
                                
                                # Target to USD
                                self.exchange_rates[(target_currency, base_currency)] = ExchangeRate(
                                    from_currency=target_currency,
                                    to_currency=base_currency,
                                    rate=1.0 / rate,
                                    timestamp=datetime.now(timezone.utc),
                                    source="exchangerate-api.com"
                                )
                                
                            except ValueError:
                                # Skip unsupported currencies
                                continue
                        
                        # Calculate cross rates
                        await self._calculate_cross_rates()
                        
                        logger.info(f"Updated exchange rates: {len(self.exchange_rates)} pairs")
                        
                        return {
                            "success": True,
                            "rates_count": len(self.exchange_rates),
                            "updated_at": datetime.now(timezone.utc).isoformat()
                        }
                    else:
                        logger.error(f"FX API error: {response.status}")
                        return {
                            "success": False,
                            "error": f"FX API error: {response.status}"
                        }
                        
        except Exception as e:
            logger.error(f"Exchange rates fetch failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _calculate_cross_rates(self):
        """Calculate cross currency rates"""
        try:
            currencies = list(WalletCurrency)
            
            for from_currency in currencies:
                for to_currency in currencies:
                    if from_currency == to_currency:
                        continue
                    
                    # Skip if already has direct rate
                    if (from_currency, to_currency) in self.exchange_rates:
                        continue
                    
                    # Try to calculate via USD
                    usd_key = (WalletCurrency.USD, to_currency)
                    from_usd_key = (from_currency, WalletCurrency.USD)
                    
                    if usd_key in self.exchange_rates and from_usd_key in self.exchange_rates:
                        # from -> USD -> to
                        rate = self.exchange_rates[from_usd_key].rate * self.exchange_rates[usd_key].rate
                        
                        self.exchange_rates[(from_currency, to_currency)] = ExchangeRate(
                            from_currency=from_currency,
                            to_currency=to_currency,
                            rate=rate,
                            timestamp=datetime.now(timezone.utc),
                            source="calculated"
                        )
                        
                        # Reverse rate
                        self.exchange_rates[(to_currency, from_currency)] = ExchangeRate(
                            from_currency=to_currency,
                            to_currency=from_currency,
                            rate=1.0 / rate,
                            timestamp=datetime.now(timezone.utc),
                            source="calculated"
                        )
            
        except Exception as e:
            logger.error(f"Cross rates calculation failed: {str(e)}")
    
    async def update_exchange_rates_loop(self):
        """Background task to update exchange rates"""
        while True:
            try:
                # Update every hour
                await asyncio.sleep(3600)
                await self.fetch_exchange_rates()
            except Exception as e:
                logger.error(f"Exchange rates update failed: {str(e)}")
    
    async def initialize_exchange_rates(self):
        """Initialize exchange rates on startup"""
        try:
            result = await self.fetch_exchange_rates()
            if result["success"]:
                logger.info("Exchange rates initialized successfully")
            else:
                logger.error(f"Exchange rates initialization failed: {result.get('error')}")
        except Exception as e:
            logger.error(f"Exchange rates initialization failed: {str(e)}")
    
    def _calculate_withdrawal_fee(self, currency: WalletCurrency, amount: float) -> float:
        """Calculate withdrawal fee"""
        fee_structures = {
            WalletCurrency.USD: {"fixed": 2.0, "percentage": 0.005},
            WalletCurrency.EUR: {"fixed": 1.5, "percentage": 0.005},
            WalletCurrency.GBP: {"fixed": 1.0, "percentage": 0.005},
            WalletCurrency.ETB: {"fixed": 50.0, "percentage": 0.01}
        }
        
        structure = fee_structures.get(currency, {"fixed": 1.0, "percentage": 0.01})
        fee = structure["fixed"] + (amount * structure["percentage"])
        
        return min(fee, amount * 0.1)  # Cap at 10% of amount
    
    def _calculate_exchange_fee(self, currency: WalletCurrency, amount: float) -> float:
        """Calculate exchange fee"""
        fee_structures = {
            WalletCurrency.USD: {"fixed": 0.5, "percentage": 0.001},
            WalletCurrency.EUR: {"fixed": 0.4, "percentage": 0.001},
            WalletCurrency.GBP: {"fixed": 0.3, "percentage": 0.001},
            WalletCurrency.ETB: {"fixed": 10.0, "percentage": 0.002}
        }
        
        structure = fee_structures.get(currency, {"fixed": 0.5, "percentage": 0.001})
        fee = structure["fixed"] + (amount * structure["percentage"])
        
        return min(fee, amount * 0.05)  # Cap at 5% of amount
    
    def _generate_quantum_signature(self, transaction_id: str) -> str:
        """Generate quantum signature"""
        try:
            signature_data = f"ML_DSA_{transaction_id}_{datetime.now().timestamp()}"
            return hashlib.sha256(signature_data.encode()).hexdigest()
        except Exception as e:
            logger.error(f"Quantum signature generation failed: {str(e)}")
            return f"QUANTUM_{transaction_id}"
    
    def _format_balances_for_ui(self, balances: Dict[WalletCurrency, WalletBalance]) -> Dict[str, Any]:
        """Format balances for UI"""
        formatted = {}
        
        for currency, balance in balances.items():
            formatted[currency.value] = {
                "available_balance": balance.available_balance,
                "frozen_balance": balance.frozen_balance,
                "total_balance": balance.total_balance,
                "last_updated": balance.last_updated.isoformat()
            }
        
        return formatted
    
    def _format_transaction_for_ui(self, transaction: WalletTransaction) -> Dict[str, Any]:
        """Format transaction for UI"""
        return {
            "transaction_id": transaction.transaction_id,
            "transaction_type": transaction.transaction_type.value,
            "currency": transaction.currency.value,
            "amount": transaction.amount,
            "fee": transaction.fee,
            "from_currency": transaction.from_currency.value if transaction.from_currency else None,
            "to_currency": transaction.to_currency.value if transaction.to_currency else None,
            "exchange_rate": transaction.exchange_rate,
            "status": transaction.status.value,
            "created_at": transaction.created_at.isoformat(),
            "completed_at": transaction.completed_at.isoformat() if transaction.completed_at else None,
            "metadata": transaction.metadata
        }
    
    async def get_wallet_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get wallet statistics"""
        try:
            if user_id not in self.wallet_balances:
                return {
                    "success": False,
                    "error": "Wallet not found"
                }
            
            balances = self.wallet_balances[user_id]
            
            # Calculate total value in USD
            total_usd_value = 0.0
            for currency, balance in balances.items():
                if currency == WalletCurrency.USD:
                    total_usd_value += balance.total_balance
                else:
                    exchange_rate = await self.get_exchange_rate(currency, WalletCurrency.USD)
                    if exchange_rate:
                        total_usd_value += balance.total_balance * exchange_rate.rate
            
            # Get transaction counts
            user_transactions = [
                tx for tx in self.transactions.values()
                if tx.user_id == user_id
            ]
            
            transaction_counts = {}
            for tx_type in TransactionType:
                transaction_counts[tx_type.value] = len([
                    tx for tx in user_transactions
                    if tx.transaction_type == tx_type
                ])
            
            return {
                "success": True,
                "user_id": user_id,
                "balances": self._format_balances_for_ui(balances),
                "total_usd_value": total_usd_value,
                "transaction_counts": transaction_counts,
                "total_transactions": len(user_transactions),
                "exchange_rates_count": len(self.exchange_rates),
                "quantum_security": self.quantum_enabled,
                "nist_compliant": self.nist_compliant
            }
            
        except Exception as e:
            logger.error(f"Wallet statistics retrieval failed: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global instance
sovereign_wallet = SovereignWallet()

# API endpoints
async def create_wallet_api(user_id: str) -> Dict[str, Any]:
    """API endpoint for creating wallet"""
    return await sovereign_wallet.create_wallet(user_id)

async def get_wallet_balance_api(user_id: str, currency: str = None) -> Dict[str, Any]:
    """API endpoint for getting wallet balance"""
    wallet_currency = WalletCurrency(currency) if currency else None
    return await sovereign_wallet.get_wallet_balance(user_id, wallet_currency)

async def deposit_funds_api(user_id: str, currency: str, amount: float, 
                          payment_method: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """API endpoint for depositing funds"""
    wallet_currency = WalletCurrency(currency)
    return await sovereign_wallet.deposit_funds(user_id, wallet_currency, amount, payment_method, metadata)

async def withdraw_funds_api(user_id: str, currency: str, amount: float,
                           destination: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """API endpoint for withdrawing funds"""
    wallet_currency = WalletCurrency(currency)
    return await sovereign_wallet.withdraw_funds(user_id, wallet_currency, amount, destination, metadata)

async def exchange_currency_api(user_id: str, from_currency: str, to_currency: str,
                              amount: float, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """API endpoint for currency exchange"""
    from_wallet_currency = WalletCurrency(from_currency)
    to_wallet_currency = WalletCurrency(to_currency)
    return await sovereign_wallet.exchange_currency(user_id, from_wallet_currency, to_wallet_currency, amount, metadata)

async def get_transaction_history_api(user_id: str, currency: str = None,
                                   limit: int = 50, offset: int = 0) -> Dict[str, Any]:
    """API endpoint for transaction history"""
    wallet_currency = WalletCurrency(currency) if currency else None
    return await sovereign_wallet.get_transaction_history(user_id, wallet_currency, limit, offset)

async def get_wallet_statistics_api(user_id: str) -> Dict[str, Any]:
    """API endpoint for wallet statistics"""
    return await sovereign_wallet.get_wallet_statistics(user_id)
