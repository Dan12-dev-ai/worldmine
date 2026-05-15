"""
Payment Agent - Auto-deposits/withdrawals, auto-escrow, auto-refunds
Replaces 1 Payment Engineer + 3 payment specialists
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
class PaymentTransaction:
    """Payment transaction record"""
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    transaction_type: str
    status: str
    initiated_at: datetime
    completed_at: Optional[datetime] = None
    fees: float = 0.0

@dataclass
class EscrowAccount:
    """Escrow account record"""
    escrow_id: str
    trade_id: str
    buyer_id: str
    seller_id: str
    amount: float
    currency: str
    status: str
    created_at: datetime
    released_at: Optional[datetime] = None

class PaymentAgent(BaseAIAgent):
    """Payment Agent - Automated payment processing"""
    
    def __init__(self):
        super().__init__(
            agent_id="payment_001",
            role=AgentRole.PAYMENT,
            name="Payment Processor",
            description="Auto-deposits/withdrawals, auto-escrow, auto-refunds"
        )
        
        self.transactions: List[PaymentTransaction] = []
        self.escrow_accounts: List[EscrowAccount] = []
        self.payment_methods: Dict[str, Any] = {}
        self.fee_structure: Dict[str, float] = {}
        
    async def initialize(self) -> bool:
        """Initialize payment agent"""
        try:
            await self._setup_payment_methods()
            await self._load_fee_structure()
            asyncio.create_task(self._transaction_processing_loop())
            asyncio.create_task(self._escrow_management_loop())
            asyncio.create_task(self._refund_processing_loop())
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Payment Agent: {e}")
            return False
    
    async def get_capabilities(self) -> List[AgentCapability]:
        """Get payment agent capabilities"""
        return [
            AgentCapability(
                name="auto_deposit",
                description="Auto-process deposits instantly",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.999, "response_time": 1.0},
                dependencies=["payment_gateways", "banking_apis"]
            ),
            AgentCapability(
                name="auto_withdrawal",
                description="Auto-process withdrawals securely",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.998, "response_time": 2.0},
                dependencies=["payment_gateways", "compliance_checks"]
            ),
            AgentCapability(
                name="auto_escrow",
                description="Auto-manage escrow accounts",
                input_schema={"type": "object"},
                output_schema={"type": "object"},
                performance_metrics={"accuracy": 0.999, "response_time": 0.5},
                dependencies=["smart_contracts", "multi_sig"]
            )
        ]
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Process payment tasks"""
        task_type = task.get('type', 'unknown')
        
        if task_type == 'command':
            return await self._handle_command(task.get('subject', ''), task.get('content', {}))
        else:
            return {'error': f'Unknown task type: {task_type}'}
    
    async def _handle_command(self, subject: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Handle payment commands"""
        if subject == "process_deposit":
            return await self._process_deposit(content)
        elif subject == "process_withdrawal":
            return await self._process_withdrawal(content)
        elif subject == "create_escrow":
            return await self._create_escrow(content)
        elif subject == "release_escrow":
            return await self._release_escrow(content)
        elif subject == "process_refund":
            return await self._process_refund(content)
        else:
            return {'error': f'Unknown command: {subject}'}
    
    async def _process_deposit(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Process deposit automatically"""
        user_id = content.get('user_id', 'unknown')
        amount = content.get('amount', 0)
        currency = content.get('currency', 'USD')
        payment_method = content.get('payment_method', 'bank_transfer')
        
        # Validate deposit
        validation_result = await self._validate_deposit(user_id, amount, currency)
        
        if not validation_result['valid']:
            return {
                'error': 'Deposit validation failed',
                'issues': validation_result['issues']
            }
        
        # Calculate fees
        fees = await self._calculate_fees(amount, currency, 'deposit')
        
        # Create transaction
        transaction = PaymentTransaction(
            transaction_id=f"deposit_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id,
            amount=amount,
            currency=currency,
            transaction_type='deposit',
            status='processing',
            initiated_at=datetime.utcnow(),
            fees=fees
        )
        
        # Process payment
        payment_result = await self._execute_deposit(transaction, payment_method)
        
        transaction.status = payment_result['status']
        transaction.completed_at = datetime.utcnow()
        
        self.transactions.append(transaction)
        
        return {
            'transaction_id': transaction.transaction_id,
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'fees': fees,
            'net_amount': amount - fees,
            'status': transaction.status,
            'completed_at': transaction.completed_at.isoformat()
        }
    
    async def _process_withdrawal(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Process withdrawal automatically"""
        user_id = content.get('user_id', 'unknown')
        amount = content.get('amount', 0)
        currency = content.get('currency', 'USD')
        destination = content.get('destination', {})
        
        # Validate withdrawal
        validation_result = await self._validate_withdrawal(user_id, amount, currency)
        
        if not validation_result['valid']:
            return {
                'error': 'Withdrawal validation failed',
                'issues': validation_result['issues']
            }
        
        # Calculate fees
        fees = await self._calculate_fees(amount, currency, 'withdrawal')
        
        # Create transaction
        transaction = PaymentTransaction(
            transaction_id=f"withdrawal_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            user_id=user_id,
            amount=amount,
            currency=currency,
            transaction_type='withdrawal',
            status='processing',
            initiated_at=datetime.utcnow(),
            fees=fees
        )
        
        # Process withdrawal
        withdrawal_result = await self._execute_withdrawal(transaction, destination)
        
        transaction.status = withdrawal_result['status']
        transaction.completed_at = datetime.utcnow()
        
        self.transactions.append(transaction)
        
        return {
            'transaction_id': transaction.transaction_id,
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'fees': fees,
            'net_amount': amount - fees,
            'destination': destination,
            'status': transaction.status,
            'completed_at': transaction.completed_at.isoformat()
        }
    
    async def _create_escrow(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Create escrow account automatically"""
        trade_id = content.get('trade_id', 'unknown')
        buyer_id = content.get('buyer_id', 'unknown')
        seller_id = content.get('seller_id', 'unknown')
        amount = content.get('amount', 0)
        currency = content.get('currency', 'USD')
        
        # Create escrow
        escrow = EscrowAccount(
            escrow_id=f"escrow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            trade_id=trade_id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            amount=amount,
            currency=currency,
            status='created',
            created_at=datetime.utcnow()
        )
        
        # Lock funds from buyer
        lock_result = await self._lock_escrow_funds(escrow)
        
        if lock_result['success']:
            escrow.status = 'funded'
            self.escrow_accounts.append(escrow)
            
            # Notify trading system
            await self.send_message(
                "trading_001",
                MessageType.NOTIFICATION,
                "Escrow Funded",
                {
                    'escrow_id': escrow.escrow_id,
                    'trade_id': trade_id,
                    'amount': amount,
                    'currency': currency
                },
                priority=Priority.NORMAL
            )
        
        return {
            'escrow_id': escrow.escrow_id,
            'trade_id': trade_id,
            'buyer_id': buyer_id,
            'seller_id': seller_id,
            'amount': amount,
            'currency': currency,
            'status': escrow.status,
            'created_at': escrow.created_at.isoformat()
        }
    
    async def _release_escrow(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Release escrow funds automatically"""
        escrow_id = content.get('escrow_id', 'unknown')
        release_reason = content.get('release_reason', 'trade_completed')
        
        # Find escrow
        escrow = next((e for e in self.escrow_accounts if e.escrow_id == escrow_id), None)
        
        if not escrow:
            return {'error': f'Escrow not found: {escrow_id}'}
        
        # Release funds to seller
        release_result = await self._release_escrow_funds(escrow, release_reason)
        
        if release_result['success']:
            escrow.status = 'released'
            escrow.released_at = datetime.utcnow()
            
            # Notify trading system
            await self.send_message(
                "trading_001",
                MessageType.NOTIFICATION,
                "Escrow Released",
                {
                    'escrow_id': escrow.escrow_id,
                    'trade_id': escrow.trade_id,
                    'amount': escrow.amount,
                    'released_to': escrow.seller_id
                },
                priority=Priority.NORMAL
            )
        
        return {
            'escrow_id': escrow.escrow_id,
            'trade_id': escrow.trade_id,
            'amount': escrow.amount,
            'currency': escrow.currency,
            'released_to': escrow.seller_id,
            'status': escrow.status,
            'released_at': escrow.released_at.isoformat() if escrow.released_at else None
        }
    
    async def _process_refund(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Process refund automatically"""
        original_transaction_id = content.get('original_transaction_id', 'unknown')
        refund_amount = content.get('refund_amount', 0)
        refund_reason = content.get('refund_reason', 'user_request')
        
        # Find original transaction
        original_transaction = next(
            (t for t in self.transactions if t.transaction_id == original_transaction_id), 
            None
        )
        
        if not original_transaction:
            return {'error': f'Original transaction not found: {original_transaction_id}'}
        
        # Create refund transaction
        refund_transaction = PaymentTransaction(
            transaction_id=f"refund_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            user_id=original_transaction.user_id,
            amount=refund_amount,
            currency=original_transaction.currency,
            transaction_type='refund',
            status='processing',
            initiated_at=datetime.utcnow()
        )
        
        # Process refund
        refund_result = await self._execute_refund(refund_transaction, original_transaction)
        
        refund_transaction.status = refund_result['status']
        refund_transaction.completed_at = datetime.utcnow()
        
        self.transactions.append(refund_transaction)
        
        return {
            'refund_transaction_id': refund_transaction.transaction_id,
            'original_transaction_id': original_transaction_id,
            'user_id': refund_transaction.user_id,
            'refund_amount': refund_amount,
            'currency': refund_transaction.currency,
            'refund_reason': refund_reason,
            'status': refund_transaction.status,
            'completed_at': refund_transaction.completed_at.isoformat()
        }
    
    async def _transaction_processing_loop(self):
        """Continuous transaction processing loop"""
        while self.is_active:
            try:
                # Process pending transactions
                pending_transactions = [t for t in self.transactions if t.status == 'processing']
                
                for transaction in pending_transactions:
                    if transaction.transaction_type == 'deposit':
                        result = await self._check_deposit_status(transaction)
                    elif transaction.transaction_type == 'withdrawal':
                        result = await self._check_withdrawal_status(transaction)
                    else:
                        continue
                    
                    if result['completed']:
                        transaction.status = 'completed'
                        transaction.completed_at = datetime.utcnow()
                
                await asyncio.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in transaction processing loop: {e}")
                await asyncio.sleep(1)
    
    async def _escrow_management_loop(self):
        """Continuous escrow management loop"""
        while self.is_active:
            try:
                # Check for auto-release conditions
                auto_release_escrows = await self._check_auto_release_conditions()
                
                for escrow in auto_release_escrows:
                    await self._release_escrow({
                        'escrow_id': escrow.escrow_id,
                        'release_reason': 'auto_release'
                    })
                
                await asyncio.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in escrow management loop: {e}")
                await asyncio.sleep(10)
    
    async def _refund_processing_loop(self):
        """Continuous refund processing loop"""
        while self.is_active:
            try:
                # Check for automatic refunds
                auto_refunds = await self._check_auto_refund_conditions()
                
                for refund_data in auto_refunds:
                    await self._process_refund(refund_data)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Error in refund processing loop: {e}")
                await asyncio.sleep(15)
    
    async def _validate_deposit(self, user_id: str, amount: float, currency: str) -> Dict[str, Any]:
        """Validate deposit request"""
        issues = []
        
        # Check amount
        if amount <= 0:
            issues.append('Amount must be positive')
        
        if amount > 1000000:  # $1M daily limit
            issues.append('Amount exceeds daily limit')
        
        # Check currency
        if currency not in ['USD', 'EUR', 'GBP', 'BTC', 'ETH']:
            issues.append('Unsupported currency')
        
        # Check user status
        user_status = await self._get_user_status(user_id)
        if not user_status['active']:
            issues.append('User account not active')
        
        if user_status['restricted']:
            issues.append('User account restricted')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    async def _validate_withdrawal(self, user_id: str, amount: float, currency: str) -> Dict[str, Any]:
        """Validate withdrawal request"""
        issues = []
        
        # Check amount
        if amount <= 0:
            issues.append('Amount must be positive')
        
        # Check user balance
        balance = await self._get_user_balance(user_id, currency)
        if amount > balance:
            issues.append('Insufficient balance')
        
        # Check withdrawal limits
        daily_withdrawn = await self._get_daily_withdrawn(user_id)
        daily_limit = await self._get_daily_limit(user_id)
        
        if daily_withdrawn + amount > daily_limit:
            issues.append('Amount exceeds daily withdrawal limit')
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    async def _calculate_fees(self, amount: float, currency: str, transaction_type: str) -> float:
        """Calculate transaction fees"""
        # Get fee structure
        fee_config = self.fee_structure.get(transaction_type, {})
        
        # Calculate percentage fee
        percentage_fee = fee_config.get('percentage', 0.01) * amount  # 1% default
        
        # Calculate fixed fee
        fixed_fee = fee_config.get('fixed', 0.0)
        
        # Calculate minimum fee
        min_fee = fee_config.get('minimum', 1.0)
        
        # Total fee
        total_fee = max(percentage_fee + fixed_fee, min_fee)
        
        return total_fee
    
    async def _execute_deposit(self, transaction: PaymentTransaction, payment_method: str) -> Dict[str, Any]:
        """Execute deposit transaction"""
        # Mock deposit execution
        success = np.random.random() > 0.01  # 99% success rate
        
        return {
            'success': success,
            'status': 'completed' if success else 'failed',
            'payment_method': payment_method,
            'processing_time': np.random.uniform(1.0, 5.0)  # 1-5 seconds
        }
    
    async def _execute_withdrawal(self, transaction: PaymentTransaction, destination: Dict[str, Any]) -> Dict[str, Any]:
        """Execute withdrawal transaction"""
        # Mock withdrawal execution
        success = np.random.random() > 0.02  # 98% success rate
        
        return {
            'success': success,
            'status': 'completed' if success else 'failed',
            'destination': destination,
            'processing_time': np.random.uniform(2.0, 10.0)  # 2-10 seconds
        }
    
    async def _lock_escrow_funds(self, escrow: EscrowAccount) -> Dict[str, Any]:
        """Lock funds in escrow"""
        # Mock escrow funding
        success = np.random.random() > 0.005  # 99.5% success rate
        
        return {
            'success': success,
            'locked_amount': escrow.amount,
            'locked_at': datetime.utcnow().isoformat()
        }
    
    async def _release_escrow_funds(self, escrow: EscrowAccount, release_reason: str) -> Dict[str, Any]:
        """Release escrow funds"""
        # Mock escrow release
        success = np.random.random() > 0.001  # 99.9% success rate
        
        return {
            'success': success,
            'released_amount': escrow.amount,
            'released_to': escrow.seller_id,
            'release_reason': release_reason,
            'released_at': datetime.utcnow().isoformat()
        }
    
    async def _execute_refund(self, refund_transaction: PaymentTransaction, original_transaction: PaymentTransaction) -> Dict[str, Any]:
        """Execute refund transaction"""
        # Mock refund execution
        success = np.random.random() > 0.01  # 99% success rate
        
        return {
            'success': success,
            'status': 'completed' if success else 'failed',
            'original_transaction': original_transaction.transaction_id,
            'processing_time': np.random.uniform(3.0, 15.0)  # 3-15 seconds
        }
    
    async def _check_deposit_status(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check deposit status"""
        # Mock status check
        completed = np.random.random() > 0.1  # 90% complete within 5 seconds
        
        return {
            'completed': completed,
            'status': 'completed' if completed else 'processing'
        }
    
    async def _check_withdrawal_status(self, transaction: PaymentTransaction) -> Dict[str, Any]:
        """Check withdrawal status"""
        # Mock status check
        completed = np.random.random() > 0.2  # 80% complete within 5 seconds
        
        return {
            'completed': completed,
            'status': 'completed' if completed else 'processing'
        }
    
    async def _check_auto_release_conditions(self) -> List[EscrowAccount]:
        """Check for automatic escrow release conditions"""
        auto_release_escrows = []
        
        for escrow in self.escrow_accounts:
            if escrow.status == 'funded':
                # Check if trade is completed
                trade_completed = await self._check_trade_completion(escrow.trade_id)
                
                if trade_completed:
                    auto_release_escrows.append(escrow)
        
        return auto_release_escrows
    
    async def _check_auto_refund_conditions(self) -> List[Dict[str, Any]]:
        """Check for automatic refund conditions"""
        auto_refunds = []
        
        # Check for failed transactions
        failed_transactions = [t for t in self.transactions if t.status == 'failed']
        
        for transaction in failed_transactions:
            # Auto-refund failed deposits
            if transaction.transaction_type == 'deposit':
                auto_refunds.append({
                    'original_transaction_id': transaction.transaction_id,
                    'refund_amount': transaction.amount,
                    'refund_reason': 'failed_deposit'
                })
        
        return auto_refunds
    
    async def _get_user_status(self, user_id: str) -> Dict[str, Any]:
        """Get user status"""
        # Mock user status
        return {
            'active': np.random.random() > 0.05,  # 95% active
            'restricted': np.random.random() < 0.02,  # 2% restricted
            'verified': np.random.random() > 0.1,  # 90% verified
            'kyc_completed': np.random.random() > 0.15  # 85% KYC completed
        }
    
    async def _get_user_balance(self, user_id: str, currency: str) -> float:
        """Get user balance"""
        # Mock balance
        return np.random.uniform(100, 100000)  # $100-$100K
    
    async def _get_daily_withdrawn(self, user_id: str) -> float:
        """Get daily withdrawn amount"""
        # Mock daily withdrawn
        return np.random.uniform(0, 5000)  # $0-$5K
    async def _get_daily_limit(self, user_id: str) -> float:
        """Get daily withdrawal limit"""
        # Mock daily limit
        return 10000  # $10K daily limit
    
    async def _check_trade_completion(self, trade_id: str) -> bool:
        """Check if trade is completed"""
        # Mock trade completion check
        return np.random.random() > 0.3  # 70% completed
    
    async def _setup_payment_methods(self):
        """Setup supported payment methods"""
        self.payment_methods = {
            'bank_transfer': {
                'name': 'Bank Transfer',
                'supported_currencies': ['USD', 'EUR', 'GBP'],
                'processing_time': '1-3 business days',
                'fees': {'percentage': 0.01, 'fixed': 5.0, 'minimum': 10.0}
            },
            'credit_card': {
                'name': 'Credit Card',
                'supported_currencies': ['USD', 'EUR', 'GBP'],
                'processing_time': 'instant',
                'fees': {'percentage': 0.029, 'fixed': 0.30, 'minimum': 1.0}
            },
            'crypto': {
                'name': 'Cryptocurrency',
                'supported_currencies': ['BTC', 'ETH', 'USDT'],
                'processing_time': '10-60 minutes',
                'fees': {'percentage': 0.005, 'fixed': 0.0, 'minimum': 5.0}
            },
            'wire_transfer': {
                'name': 'Wire Transfer',
                'supported_currencies': ['USD', 'EUR', 'GBP'],
                'processing_time': 'same day',
                'fees': {'percentage': 0.005, 'fixed': 15.0, 'minimum': 25.0}
            }
        }
    
    async def _load_fee_structure(self):
        """Load fee structure"""
        self.fee_structure = {
            'deposit': {
                'percentage': 0.0,  # No deposit fees
                'fixed': 0.0,
                'minimum': 0.0
            },
            'withdrawal': {
                'percentage': 0.01,  # 1% withdrawal fee
                'fixed': 2.0,
                'minimum': 5.0
            },
            'escrow': {
                'percentage': 0.005,  # 0.5% escrow fee
                'fixed': 1.0,
                'minimum': 2.0
            },
            'refund': {
                'percentage': 0.0,  # No refund fees
                'fixed': 0.0,
                'minimum': 0.0
            }
        }

payment_agent = PaymentAgent()
