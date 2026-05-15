"""
Transaction Validator for DEDAN 2.0
ACID compliance and transaction integrity validation
"""

import asyncio
import asyncpg
import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionType(Enum):
    """Transaction types"""
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRADE = "trade"
    TRANSFER = "transfer"
    FEE = "fee"
    REFUND = "refund"

class TransactionStatus(Enum):
    """Transaction statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class TransactionValidation:
    """Transaction validation result"""
    transaction_id: str
    is_valid: bool
    validation_errors: List[str]
    warnings: List[str]
    acid_compliance: Dict[str, bool]
    integrity_score: float
    validated_at: datetime

class TransactionValidator:
    """Advanced transaction validator"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.validation_history: List[TransactionValidation] = []
        self.validation_rules = self._load_validation_rules()
        self.running = False
        
        # ACID properties to check
        self.acid_properties = ['atomicity', 'consistency', 'isolation', 'durability']
    
    async def validate_transaction(
        self, 
        transaction_id: str,
        transaction_data: Dict[str, Any]
    ) -> TransactionValidation:
        """Validate a single transaction"""
        start_time = time.time()
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            validation_errors = []
            warnings = []
            acid_compliance = {}
            
            # Validate ACID properties
            atomicity_valid, atomicity_errors = await self._validate_atomicity(conn, transaction_id, transaction_data)
            acid_compliance['atomicity'] = atomicity_valid
            validation_errors.extend(atomicity_errors)
            
            consistency_valid, consistency_errors = await self._validate_consistency(conn, transaction_id, transaction_data)
            acid_compliance['consistency'] = consistency_valid
            validation_errors.extend(consistency_errors)
            
            isolation_valid, isolation_errors = await self._validate_isolation(conn, transaction_id, transaction_data)
            acid_compliance['isolation'] = isolation_valid
            validation_errors.extend(isolation_errors)
            
            durability_valid, durability_errors = await self._validate_durability(conn, transaction_id, transaction_data)
            acid_compliance['durability'] = durability_valid
            validation_errors.extend(durability_errors)
            
            # Validate business rules
            business_valid, business_errors, business_warnings = await self._validate_business_rules(conn, transaction_id, transaction_data)
            validation_errors.extend(business_errors)
            warnings.extend(business_warnings)
            
            # Calculate integrity score
            integrity_score = self._calculate_integrity_score(acid_compliance, business_valid, len(validation_errors))
            
            # Create validation result
            validation = TransactionValidation(
                transaction_id=transaction_id,
                is_valid=len(validation_errors) == 0 and all(acid_compliance.values()),
                validation_errors=validation_errors,
                warnings=warnings,
                acid_compliance=acid_compliance,
                integrity_score=integrity_score,
                validated_at=datetime.utcnow()
            )
            
            self.validation_history.append(validation)
            
            validation_time = time.time() - start_time
            logger.info(f"Transaction {transaction_id} validated in {validation_time:.3f}s - Score: {integrity_score:.2f}")
            
            return validation
            
        finally:
            await conn.close()
    
    async def _validate_atomicity(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate atomicity - all or nothing"""
        errors = []
        
        try:
            # Get transaction details
            query = """
                SELECT type, amount, from_account, to_account, status
                FROM transactions
                WHERE id = $1
            """
            
            tx_details = await conn.fetchrow(query, transaction_id)
            
            if not tx_details:
                errors.append(f"Transaction {transaction_id} not found")
                return False, errors
            
            # Check if all related operations are consistent
            if tx_details['type'] == 'trade':
                # For trades, check both sides are processed
                buy_order = await conn.fetchrow(
                    "SELECT status FROM orders WHERE id = $1", 
                    transaction_data.get('buy_order_id')
                )
                sell_order = await conn.fetchrow(
                    "SELECT status FROM orders WHERE id = $1", 
                    transaction_data.get('sell_order_id')
                )
                
                if not buy_order or not sell_order:
                    errors.append("Trade transaction missing buy or sell order")
                elif buy_order['status'] != 'filled' or sell_order['status'] != 'filled':
                    errors.append("Trade transaction orders not both filled")
            
            # Check balance changes are atomic
            balance_changes = await conn.fetch(
                """
                SELECT account_id, amount, change_type
                FROM balance_changes
                WHERE transaction_id = $1
                """,
                transaction_id
            )
            
            if not balance_changes:
                errors.append("No balance changes found for transaction")
            else:
                # Verify sum of changes equals transaction amount
                total_debits = sum(
                    bc['amount'] for bc in balance_changes 
                    if bc['change_type'] == 'debit'
                )
                total_credits = sum(
                    bc['amount'] for bc in balance_changes 
                    if bc['change_type'] == 'credit'
                )
                
                if abs(total_debits - total_credits) > 0.01:  # Allow small floating point differences
                    errors.append(f"Balance changes not atomic: debits={total_debits}, credits={total_credits}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Atomicity validation error: {e}")
            return False, errors
    
    async def _validate_consistency(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate consistency - database remains in consistent state"""
        errors = []
        
        try:
            # Get transaction details
            tx_details = await conn.fetchrow(
                "SELECT type, amount, from_account, to_account FROM transactions WHERE id = $1",
                transaction_id
            )
            
            if not tx_details:
                errors.append(f"Transaction {transaction_id} not found")
                return False, errors
            
            # Check account balances after transaction
            if tx_details['from_account']:
                from_balance = await conn.fetchval(
                    "SELECT balance FROM accounts WHERE id = $1",
                    tx_details['from_account']
                )
                
                if from_balance is None:
                    errors.append(f"From account {tx_details['from_account']} not found")
                elif from_balance < 0:
                    errors.append(f"From account {tx_details['from_account']} has negative balance: {from_balance}")
            
            if tx_details['to_account']:
                to_balance = await conn.fetchval(
                    "SELECT balance FROM accounts WHERE id = $1",
                    tx_details['to_account']
                )
                
                if to_balance is None:
                    errors.append(f"To account {tx_details['to_account']} not found")
            
            # Check referential integrity
            if tx_details['type'] == 'trade':
                # Verify mineral exists
                mineral_id = transaction_data.get('mineral_id')
                if mineral_id:
                    mineral_exists = await conn.fetchval(
                        "SELECT 1 FROM minerals WHERE id = $1",
                        mineral_id
                    )
                    
                    if not mineral_exists:
                        errors.append(f"Mineral {mineral_id} not found for trade transaction")
            
            # Check business invariants
            total_system_balance = await conn.fetchval(
                "SELECT SUM(balance) FROM accounts"
            )
            
            # System balance should never be negative
            if total_system_balance < 0:
                errors.append(f"System balance is negative: {total_system_balance}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Consistency validation error: {e}")
            return False, errors
    
    async def _validate_isolation(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate isolation - concurrent transactions don't interfere"""
        errors = []
        
        try:
            # Check for concurrent transactions on same accounts
            tx_time = await conn.fetchval(
                "SELECT created_at FROM transactions WHERE id = $1",
                transaction_id
            )
            
            if not tx_time:
                errors.append(f"Transaction {transaction_id} not found")
                return False, errors
            
            # Look for overlapping transactions
            overlapping_tx = await conn.fetch(
                """
                SELECT t.id, t.type
                FROM transactions t
                JOIN balance_changes bc ON t.id = bc.transaction_id
                WHERE t.id != $1
                AND t.created_at BETWEEN $2 - INTERVAL '1 second' AND $2 + INTERVAL '1 second'
                AND bc.account_id IN (
                    SELECT account_id FROM balance_changes WHERE transaction_id = $1
                )
                """,
                transaction_id, tx_time
            )
            
            # Check if overlapping transactions could cause conflicts
            for tx in overlapping_tx:
                if tx['type'] in ['trade', 'transfer']:
                    # These operations are sensitive to ordering
                    errors.append(f"Potential isolation conflict with transaction {tx['id']}")
            
            # Check lock contention
            lock_info = await conn.fetch(
                """
                SELECT relation, mode, granted
                FROM pg_locks
                WHERE pid = pg_backend_pid()
                AND NOT granted
                """
            )
            
            if lock_info:
                errors.append(f"Lock contention detected: {lock_info}")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Isolation validation error: {e}")
            return False, errors
    
    async def _validate_durability(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """Validate durability - committed transactions survive crashes"""
        errors = []
        
        try:
            # Check transaction is properly committed
            tx_status = await conn.fetchval(
                "SELECT status FROM transactions WHERE id = $1",
                transaction_id
            )
            
            if tx_status != 'completed':
                errors.append(f"Transaction {transaction_id} not marked as completed: {tx_status}")
            
            # Check WAL (Write-Ahead Log) entries
            wal_info = await conn.fetchrow(
                """
                SELECT pg_current_wal_lsn() as current_lsn,
                       pg_current_wal_insert_lsn() as insert_lsn
                """
            )
            
            # Verify transaction is in WAL
            tx_lsn = await conn.fetchval(
                """
                SELECT lsn
                FROM pg_stat_progress_create_index
                WHERE relid = (
                    SELECT oid FROM pg_class WHERE relname = 'transactions'
                )
                LIMIT 1
                """
            )
            
            # Check replication status if applicable
            replication_lag = await conn.fetchval(
                """
                SELECT pg_xlog_location_diff(pg_current_xlog_location(), replay_location)
                FROM pg_stat_replication
                LIMIT 1
                """
            )
            
            if replication_lag and replication_lag > 1000:  # More than 1MB lag
                errors.append(f"High replication lag: {replication_lag} bytes")
            
            # Check backup status
            last_backup = await conn.fetchval(
                "SELECT pg_backup_start_time()"
            )
            
            if last_backup:
                backup_age = datetime.utcnow() - last_backup
                if backup_age > timedelta(hours=24):
                    errors.append(f"Last backup is {backup_age} old")
            
            return len(errors) == 0, errors
            
        except Exception as e:
            errors.append(f"Durability validation error: {e}")
            return False, errors
    
    async def _validate_business_rules(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any]
    ) -> Tuple[bool, List[str], List[str]]:
        """Validate business rules and constraints"""
        errors = []
        warnings = []
        
        try:
            # Get transaction details
            tx_details = await conn.fetchrow(
                "SELECT type, amount, from_account, to_account, created_at FROM transactions WHERE id = $1",
                transaction_id
            )
            
            if not tx_details:
                errors.append(f"Transaction {transaction_id} not found")
                return False, errors, warnings
            
            # Validate transaction amount
            amount = tx_details['amount']
            if amount <= 0:
                errors.append(f"Transaction amount must be positive: {amount}")
            elif amount > 1000000:  # $1M limit
                warnings.append(f"Large transaction amount: {amount}")
            
            # Validate transaction timing
            tx_time = tx_details['created_at']
            if tx_time > datetime.utcnow():
                errors.append(f"Transaction timestamp is in the future: {tx_time}")
            
            # Check daily limits
            daily_limit = 100000  # $100K daily limit
            today_total = await conn.fetchval(
                """
                SELECT COALESCE(SUM(amount), 0)
                FROM transactions
                WHERE DATE(created_at) = CURRENT_DATE
                AND from_account = $1
                AND status = 'completed'
                """,
                tx_details['from_account']
            )
            
            if today_total > daily_limit:
                warnings.append(f"Daily limit exceeded: {today_total} > {daily_limit}")
            
            # Validate specific transaction types
            if tx_details['type'] == 'trade':
                await self._validate_trade_rules(conn, transaction_id, transaction_data, errors, warnings)
            elif tx_details['type'] == 'transfer':
                await self._validate_transfer_rules(conn, transaction_id, transaction_data, errors, warnings)
            elif tx_details['type'] == 'withdrawal':
                await self._validate_withdrawal_rules(conn, transaction_id, transaction_data, errors, warnings)
            
            return len(errors) == 0, errors, warnings
            
        except Exception as e:
            errors.append(f"Business rules validation error: {e}")
            return False, errors, warnings
    
    async def _validate_trade_rules(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any],
        errors: List[str], 
        warnings: List[str]
    ):
        """Validate trade-specific rules"""
        # Check order matching
        buy_order_id = transaction_data.get('buy_order_id')
        sell_order_id = transaction_data.get('sell_order_id')
        
        if not buy_order_id or not sell_order_id:
            errors.append("Trade transaction missing buy or sell order")
            return
        
        # Verify orders exist and are valid
        buy_order = await conn.fetchrow(
            "SELECT * FROM orders WHERE id = $1",
            buy_order_id
        )
        
        sell_order = await conn.fetchrow(
            "SELECT * FROM orders WHERE id = $1",
            sell_order_id
        )
        
        if not buy_order or not sell_order:
            errors.append("Buy or sell order not found")
            return
        
        # Check price matching
        if buy_order['price'] < sell_order['price']:
            errors.append(f"Price mismatch: buy {buy_order['price']} < sell {sell_order['price']}")
        
        # Check quantity matching
        if buy_order['quantity'] != sell_order['quantity']:
            warnings.append(f"Quantity mismatch: buy {buy_order['quantity']} != sell {sell_order['quantity']}")
        
        # Check mineral consistency
        if buy_order['mineral_id'] != sell_order['mineral_id']:
            errors.append("Mineral ID mismatch between buy and sell orders")
    
    async def _validate_transfer_rules(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any],
        errors: List[str], 
        warnings: List[str]
    ):
        """Validate transfer-specific rules"""
        # Check self-transfer
        from_account = transaction_data.get('from_account')
        to_account = transaction_data.get('to_account')
        
        if from_account == to_account:
            errors.append("Cannot transfer to same account")
        
        # Check account types
        from_type = await conn.fetchval(
            "SELECT type FROM accounts WHERE id = $1",
            from_account
        )
        
        to_type = await conn.fetchval(
            "SELECT type FROM accounts WHERE id = $1",
            to_account
        )
        
        if from_type == 'savings':
            warnings.append("Transfer from savings account may incur fees")
        
        if to_type == 'savings' and transaction_data.get('amount') > 10000:
            warnings.append("Large transfer to savings account may require verification")
    
    async def _validate_withdrawal_rules(
        self, 
        conn: asyncpg.Connection, 
        transaction_id: str, 
        transaction_data: Dict[str, Any],
        errors: List[str], 
        warnings: List[str]
    ):
        """Validate withdrawal-specific rules"""
        # Check withdrawal limits
        daily_limit = 50000  # $50K daily withdrawal limit
        account_id = transaction_data.get('from_account')
        
        today_withdrawals = await conn.fetchval(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions
            WHERE DATE(created_at) = CURRENT_DATE
            AND from_account = $1
            AND type = 'withdrawal'
            AND status = 'completed'
            """,
            account_id
        )
        
        if today_withdrawals > daily_limit:
            errors.append(f"Daily withdrawal limit exceeded: {today_withdrawals} > {daily_limit}")
        
        # Check account balance
        balance = await conn.fetchval(
            "SELECT balance FROM accounts WHERE id = $1",
            account_id
        )
        
        withdrawal_amount = transaction_data.get('amount')
        if balance < withdrawal_amount:
            errors.append(f"Insufficient balance: {balance} < {withdrawal_amount}")
    
    def _calculate_integrity_score(
        self, 
        acid_compliance: Dict[str, bool], 
        business_valid: bool, 
        error_count: int
    ) -> float:
        """Calculate transaction integrity score"""
        # Base score from ACID compliance
        acid_score = sum(acid_compliance.values()) / len(acid_compliance) * 70
        
        # Business rules score
        business_score = 20 if business_valid else 0
        
        # Error penalty
        error_penalty = min(error_count * 2, 10)
        
        total_score = acid_score + business_score - error_penalty
        return max(0, min(100, total_score))
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration"""
        return {
            'acid_checks': True,
            'business_rules_checks': True,
            'daily_limits': {
                'withdrawal': 50000,
                'transfer': 100000
            },
            'max_transaction_amount': 1000000,
            'require_transaction_audit': True,
            'check_replication_lag': True
        }
    
    async def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation metrics"""
        if not self.validation_history:
            return {"message": "No validations performed yet"}
        
        total_validations = len(self.validation_history)
        valid_transactions = len([v for v in self.validation_history if v.is_valid])
        
        # ACID compliance rates
        atomicity_rate = sum(1 for v in self.validation_history if v.acid_compliance.get('atomicity', False)) / total_validations * 100
        consistency_rate = sum(1 for v in self.validation_history if v.acid_compliance.get('consistency', False)) / total_validations * 100
        isolation_rate = sum(1 for v in self.validation_history if v.acid_compliance.get('isolation', False)) / total_validations * 100
        durability_rate = sum(1 for v in self.validation_history if v.acid_compliance.get('durability', False)) / total_validations * 100
        
        # Average integrity score
        avg_integrity_score = sum(v.integrity_score for v in self.validation_history) / total_validations
        
        # Common validation errors
        error_counts = {}
        for validation in self.validation_history:
            for error in validation.validation_errors:
                error_type = error.split(':')[0] if ':' in error else error
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            'total_validations': total_validations,
            'valid_transactions': valid_transactions,
            'validation_success_rate': valid_transactions / total_validations * 100,
            'average_integrity_score': avg_integrity_score,
            'acid_compliance_rates': {
                'atomicity': atomicity_rate,
                'consistency': consistency_rate,
                'isolation': isolation_rate,
                'durability': durability_rate
            },
            'common_validation_errors': error_counts,
            'high_integrity_transactions': len([v for v in self.validation_history if v.integrity_score >= 90]),
            'low_integrity_transactions': len([v for v in self.validation_history if v.integrity_score < 70])
        }

# Usage example
async def main():
    """Main execution function"""
    validator = TransactionValidator("postgresql://dedan:password@localhost:5432/dedan")
    
    # Example transaction data
    transaction_data = {
        'type': 'trade',
        'amount': 1000.0,
        'from_account': 'user1',
        'to_account': 'user2',
        'buy_order_id': 'order_123',
        'sell_order_id': 'order_456',
        'mineral_id': 'gold'
    }
    
    # Validate transaction
    validation = await validator.validate_transaction('tx_789', transaction_data)
    
    print("Transaction Validation Results:")
    print(f"  Valid: {validation.is_valid}")
    print(f"  Integrity Score: {validation.integrity_score:.2f}")
    print(f"  ACID Compliance: {validation.acid_compliance}")
    print(f"  Errors: {validation.validation_errors}")
    print(f"  Warnings: {validation.warnings}")
    
    # Get metrics
    metrics = await validator.get_validation_metrics()
    print(f"\nValidation Metrics: {json.dumps(metrics, indent=2, default=str)}")

if __name__ == "__main__":
    asyncio.run(main())
