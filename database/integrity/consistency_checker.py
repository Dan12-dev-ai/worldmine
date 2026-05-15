"""
Database Consistency Checker for DEDAN 2.0
Real-time consistency validation and repair
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

class ConsistencyIssue(Enum):
    """Types of consistency issues"""
    FOREIGN_KEY_VIOLATION = "foreign_key_violation"
    DUPLICATE_RECORD = "duplicate_record"
    NULL_CONSTRAINT_VIOLATION = "null_constraint_violation"
    CHECK_CONSTRAINT_VIOLATION = "check_constraint_violation"
    DATA_TYPE_MISMATCH = "data_type_mismatch"
    ORPHANED_RECORD = "orphaned_record"
    CIRCULAR_REFERENCE = "circular_reference"
    BALANCE_MISMATCH = "balance_mismatch"
    TRANSACTION_INTEGRITY = "transaction_integrity"
    AUDIT_TRAIL_BREAK = "audit_trail_break"

@dataclass
class ConsistencyViolation:
    """Consistency violation details"""
    issue_type: ConsistencyIssue
    table_name: str
    record_id: Optional[str]
    column_name: Optional[str]
    expected_value: Optional[Any]
    actual_value: Optional[Any]
    severity: str  # critical, high, medium, low
    description: str
    detected_at: datetime
    auto_fixable: bool
    fix_query: Optional[str]

class DatabaseConsistencyChecker:
    """Advanced database consistency checker"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.violations: List[ConsistencyViolation] = []
        self.check_history: List[Dict[str, Any]] = []
        self.auto_fix_enabled = True
        self.running = False
        self.check_interval = 300  # 5 minutes
        
        # Consistency rules
        self.consistency_rules = self._load_consistency_rules()
        
        # Critical tables
        self.critical_tables = [
            'users', 'user_balances', 'minerals', 'orders', 'trades',
            'transactions', 'audit_log', 'market_data', 'portfolio'
        ]
    
    async def start_consistency_checking(self):
        """Start continuous consistency checking"""
        logger.info("Starting database consistency checking...")
        self.running = True
        
        while self.running:
            try:
                await self.run_full_consistency_check()
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in consistency checking: {e}")
                await asyncio.sleep(60)
    
    async def stop_consistency_checking(self):
        """Stop consistency checking"""
        logger.info("Stopping database consistency checking...")
        self.running = False
    
    async def run_full_consistency_check(self) -> Dict[str, Any]:
        """Run complete consistency check"""
        start_time = time.time()
        self.violations.clear()
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            # Check all consistency rules
            await self._check_foreign_key_constraints(conn)
            await self._check_duplicate_records(conn)
            await self._check_null_constraints(conn)
            await self._check_balance_integrity(conn)
            await self._check_transaction_integrity(conn)
            await self._check_audit_trail(conn)
            await self._check_orphaned_records(conn)
            await self._check_circular_references(conn)
            await self._check_data_type_consistency(conn)
            await self._check_business_rules(conn)
            
            # Auto-fix violations if enabled
            if self.auto_fix_enabled:
                await self._auto_fix_violations(conn)
            
            # Generate report
            check_time = time.time() - start_time
            report = self._generate_consistency_report(check_time)
            
            # Store check history
            self.check_history.append({
                'timestamp': datetime.utcnow(),
                'duration_seconds': check_time,
                'violations_found': len(self.violations),
                'violations_fixed': len([v for v in self.violations if v.auto_fixable]),
                'report': report
            })
            
            logger.info(f"Consistency check completed in {check_time:.2f}s - {len(self.violations)} violations found")
            
            return report
            
        finally:
            await conn.close()
    
    async def _check_foreign_key_constraints(self, conn: asyncpg.Connection):
        """Check foreign key constraints"""
        foreign_keys = [
            ('orders', 'user_id', 'users', 'id'),
            ('orders', 'mineral_id', 'minerals', 'id'),
            ('trades', 'buy_order_id', 'orders', 'id'),
            ('trades', 'sell_order_id', 'orders', 'id'),
            ('user_balances', 'user_id', 'users', 'id'),
            ('portfolio', 'user_id', 'users', 'id'),
            ('portfolio', 'mineral_id', 'minerals', 'id')
        ]
        
        for table, fk_column, ref_table, ref_column in foreign_keys:
            query = f"""
                SELECT t.{fk_column} as fk_value, COUNT(*) as count
                FROM {table} t
                LEFT JOIN {ref_table} r ON t.{fk_column} = r.{ref_column}
                WHERE r.{ref_column} IS NULL
                GROUP BY t.{fk_column}
            """
            
            rows = await conn.fetch(query)
            
            for row in rows:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.FOREIGN_KEY_VIOLATION,
                    table_name=table,
                    record_id=str(row['fk_value']),
                    column_name=fk_column,
                    expected_value=None,
                    actual_value=row['fk_value'],
                    severity='critical',
                    description=f"Foreign key violation in {table}.{fk_column}: {row['fk_value']} not found in {ref_table}",
                    detected_at=datetime.utcnow(),
                    auto_fixable=False,
                    fix_query=f"DELETE FROM {table} WHERE {fk_column} = '{row['fk_value']}'"
                )
                self.violations.append(violation)
    
    async def _check_duplicate_records(self, conn: asyncpg.Connection):
        """Check for duplicate records"""
        unique_constraints = [
            ('users', 'email'),
            ('users', 'username'),
            ('minerals', 'symbol'),
            ('orders', 'id'),
            ('trades', 'id')
        ]
        
        for table, columns in unique_constraints:
            column_list = columns if isinstance(columns, list) else [columns]
            
            query = f"""
                SELECT {', '.join(column_list)}, COUNT(*) as count
                FROM {table}
                GROUP BY {', '.join(column_list)}
                HAVING COUNT(*) > 1
            """
            
            rows = await conn.fetch(query)
            
            for row in rows:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.DUPLICATE_RECORD,
                    table_name=table,
                    record_id=str(row.get('id', 'unknown')),
                    column_name=', '.join(column_list),
                    expected_value=1,
                    actual_value=row['count'],
                    severity='high',
                    description=f"Duplicate record in {table} for {', '.join(column_list)}: {dict(row)}",
                    detected_at=datetime.utcnow(),
                    auto_fixable=True,
                    fix_query=f"DELETE FROM {table} WHERE ctid NOT IN (SELECT min(ctid) FROM {table} GROUP BY {', '.join(column_list)})"
                )
                self.violations.append(violation)
    
    async def _check_null_constraints(self, conn: asyncpg.Connection):
        """Check null constraint violations"""
        not_null_columns = [
            ('users', 'email'),
            ('users', 'created_at'),
            ('orders', 'user_id'),
            ('orders', 'mineral_id'),
            ('trades', 'buy_order_id'),
            ('trades', 'sell_order_id')
        ]
        
        for table, column in not_null_columns:
            query = f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE {column} IS NULL
            """
            
            count = await conn.fetchval(query)
            
            if count > 0:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.NULL_CONSTRAINT_VIOLATION,
                    table_name=table,
                    record_id=None,
                    column_name=column,
                    expected_value='NOT NULL',
                    actual_value='NULL',
                    severity='high',
                    description=f"Null constraint violation in {table}.{column}: {count} records have NULL values",
                    detected_at=datetime.utcnow(),
                    auto_fixable=False,
                    fix_query=None
                )
                self.violations.append(violation)
    
    async def _check_balance_integrity(self, conn: asyncpg.Connection):
        """Check balance integrity across accounts"""
        # Check user balances match transaction sums
        query = """
            SELECT 
                ub.user_id,
                ub.balance as recorded_balance,
                COALESCE(SUM(
                    CASE 
                        WHEN t.type = 'credit' THEN t.amount
                        WHEN t.type = 'debit' THEN -t.amount
                        ELSE 0
                    END
                ), 0) as calculated_balance
            FROM user_balances ub
            LEFT JOIN transactions t ON ub.user_id = t.user_id
            GROUP BY ub.user_id, ub.balance
            HAVING ub.balance != COALESCE(SUM(
                CASE 
                    WHEN t.type = 'credit' THEN t.amount
                    WHEN t.type = 'debit' THEN -t.amount
                    ELSE 0
                END
            ), 0)
        """
        
        rows = await conn.fetch(query)
        
        for row in rows:
            violation = ConsistencyViolation(
                issue_type=ConsistencyIssue.BALANCE_MISMATCH,
                table_name='user_balances',
                record_id=str(row['user_id']),
                column_name='balance',
                expected_value=row['calculated_balance'],
                actual_value=row['recorded_balance'],
                severity='critical',
                description=f"Balance mismatch for user {row['user_id']}: recorded={row['recorded_balance']}, calculated={row['calculated_balance']}",
                detected_at=datetime.utcnow(),
                auto_fixable=True,
                fix_query=f"UPDATE user_balances SET balance = {row['calculated_balance']} WHERE user_id = {row['user_id']}"
            )
            self.violations.append(violation)
    
    async def _check_transaction_integrity(self, conn: asyncpg.Connection):
        """Check transaction integrity"""
        # Check for missing audit entries
        query = """
            SELECT t.id, t.user_id, t.amount, t.type
            FROM transactions t
            LEFT JOIN audit_log a ON t.id = a.resource_id AND a.action = 'CREATE_TRANSACTION'
            WHERE a.id IS NULL
        """
        
        rows = await conn.fetch(query)
        
        for row in rows:
            violation = ConsistencyViolation(
                issue_type=ConsistencyIssue.TRANSACTION_INTEGRITY,
                table_name='transactions',
                record_id=str(row['id']),
                column_name='audit_entry',
                expected_value='present',
                actual_value='missing',
                severity='high',
                description=f"Missing audit entry for transaction {row['id']}",
                detected_at=datetime.utcnow(),
                auto_fixable=True,
                fix_query=f"""
                    INSERT INTO audit_log (user_id, action, resource_id, resource_type, details, created_at)
                    VALUES ({row['user_id']}, 'CREATE_TRANSACTION', {row['id']}, 'TRANSACTION', 
                           'Auto-generated audit entry for transaction {row["id"]}', NOW())
                """
            )
            self.violations.append(violation)
    
    async def _check_audit_trail(self, conn: asyncpg.Connection):
        """Check audit trail integrity"""
        # Check for gaps in audit sequence
        query = """
            SELECT 
                a1.id as current_id,
                a2.id as previous_id,
                a1.created_at as current_time,
                a2.created_at as previous_time
            FROM audit_log a1
            LEFT JOIN audit_log a2 ON a1.id = a2.id + 1
            WHERE a2.id IS NULL AND a1.id > 1
        """
        
        rows = await conn.fetch(query)
        
        for row in rows:
            violation = ConsistencyViolation(
                issue_type=ConsistencyIssue.AUDIT_TRAIL_BREAK,
                table_name='audit_log',
                record_id=str(row['current_id']),
                column_name='sequence',
                expected_value='continuous',
                actual_value='gap',
                severity='medium',
                description=f"Audit trail break detected at ID {row['current_id']}",
                detected_at=datetime.utcnow(),
                auto_fixable=False,
                fix_query=None
            )
            self.violations.append(violation)
    
    async def _check_orphaned_records(self, conn: asyncpg.Connection):
        """Check for orphaned records"""
        orphan_checks = [
            ('portfolio', 'user_id', 'users', 'id'),
            ('portfolio', 'mineral_id', 'minerals', 'id'),
            ('market_data', 'mineral_id', 'minerals', 'id')
        ]
        
        for table, fk_column, ref_table, ref_column in orphan_checks:
            query = f"""
                SELECT t.id, t.{fk_column}
                FROM {table} t
                LEFT JOIN {ref_table} r ON t.{fk_column} = r.{ref_column}
                WHERE r.{ref_column} IS NULL
            """
            
            rows = await conn.fetch(query)
            
            for row in rows:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.ORPHANED_RECORD,
                    table_name=table,
                    record_id=str(row['id']),
                    column_name=fk_column,
                    expected_value=f"exists in {ref_table}",
                    actual_value='orphaned',
                    severity='medium',
                    description=f"Orphaned record in {table} ID {row['id']}: {fk_column}={row[fk_column]} not found in {ref_table}",
                    detected_at=datetime.utcnow(),
                    auto_fixable=True,
                    fix_query=f"DELETE FROM {table} WHERE id = {row['id']}"
                )
                self.violations.append(violation)
    
    async def _check_circular_references(self, conn: asyncpg.Connection):
        """Check for circular references"""
        # Check for circular references in self-referencing tables
        circular_checks = [
            ('users', 'referred_by', 'id')
        ]
        
        for table, fk_column, ref_column in circular_checks:
            # Use recursive CTE to detect cycles
            query = f"""
                WITH RECURSIVE cycle_check AS (
                    SELECT id, {fk_column}, 1 as depth
                    FROM {table}
                    WHERE {fk_column} IS NOT NULL
                    
                    UNION ALL
                    
                    SELECT t.id, t.{fk_column}, cc.depth + 1
                    FROM {table} t
                    JOIN cycle_check cc ON t.id = cc.{fk_column}
                    WHERE cc.depth < 10
                )
                SELECT DISTINCT id, {fk_column}
                FROM cycle_check
                WHERE id = {fk_column}
            """
            
            rows = await conn.fetch(query)
            
            for row in rows:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.CIRCULAR_REFERENCE,
                    table_name=table,
                    record_id=str(row['id']),
                    column_name=fk_column,
                    expected_value='no cycle',
                    actual_value='circular reference',
                    severity='high',
                    description=f"Circular reference in {table}: {row['id']} -> {row[fk_column]}",
                    detected_at=datetime.utcnow(),
                    auto_fixable=True,
                    fix_query=f"UPDATE {table} SET {fk_column} = NULL WHERE id = {row['id']}"
                )
                self.violations.append(violation)
    
    async def _check_data_type_consistency(self, conn: asyncpg.Connection):
        """Check data type consistency"""
        type_checks = [
            ('orders', 'price', 'numeric'),
            ('orders', 'quantity', 'numeric'),
            ('user_balances', 'balance', 'numeric'),
            ('minerals', 'current_price', 'numeric')
        ]
        
        for table, column, expected_type in type_checks:
            query = f"""
                SELECT COUNT(*) as count
                FROM {table}
                WHERE {column} IS NOT NULL AND 
                      {column}::text !~ '^[0-9]+(\.[0-9]+)?$'
            """
            
            count = await conn.fetchval(query)
            
            if count > 0:
                violation = ConsistencyViolation(
                    issue_type=ConsistencyIssue.DATA_TYPE_MISMATCH,
                    table_name=table,
                    record_id=None,
                    column_name=column,
                    expected_value=expected_type,
                    actual_value='invalid format',
                    severity='medium',
                    description=f"Data type mismatch in {table}.{column}: {count} records have invalid {expected_type} format",
                    detected_at=datetime.utcnow(),
                    auto_fixable=False,
                    fix_query=None
                )
                self.violations.append(violation)
    
    async def _check_business_rules(self, conn: asyncpg.Connection):
        """Check business rule compliance"""
        # Check for negative balances
        query = """
            SELECT user_id, balance
            FROM user_balances
            WHERE balance < 0
        """
        
        rows = await conn.fetch(query)
        
        for row in rows:
            violation = ConsistencyViolation(
                issue_type=ConsistencyIssue.CHECK_CONSTRAINT_VIOLATION,
                table_name='user_balances',
                record_id=str(row['user_id']),
                column_name='balance',
                expected_value='>= 0',
                actual_value=row['balance'],
                severity='critical',
                description=f"Negative balance for user {row['user_id']}: {row['balance']}",
                detected_at=datetime.utcnow(),
                auto_fixable=True,
                fix_query=f"UPDATE user_balances SET balance = 0 WHERE user_id = {row['user_id']}"
            )
            self.violations.append(violation)
        
        # Check for invalid order prices
        query = """
            SELECT id, price
            FROM orders
            WHERE price <= 0 OR price > 1000000
        """
        
        rows = await conn.fetch(query)
        
        for row in rows:
            violation = ConsistencyViolation(
                issue_type=ConsistencyIssue.CHECK_CONSTRAINT_VIOLATION,
                table_name='orders',
                record_id=str(row['id']),
                column_name='price',
                expected_value='0 < price <= 1000000',
                actual_value=row['price'],
                severity='high',
                description=f"Invalid order price for order {row['id']}: {row['price']}",
                detected_at=datetime.utcnow(),
                auto_fixable=False,
                fix_query=None
            )
            self.violations.append(violation)
    
    async def _auto_fix_violations(self, conn: asyncpg.Connection):
        """Auto-fix eligible violations"""
        auto_fixable_violations = [v for v in self.violations if v.auto_fixable]
        
        for violation in auto_fixable_violations:
            try:
                if violation.fix_query:
                    await conn.execute(violation.fix_query)
                    logger.info(f"Auto-fixed violation: {violation.description}")
            except Exception as e:
                logger.error(f"Failed to auto-fix violation: {e}")
    
    def _load_consistency_rules(self) -> Dict[str, Any]:
        """Load consistency rules configuration"""
        return {
            'foreign_key_checks': True,
            'duplicate_checks': True,
            'null_checks': True,
            'balance_checks': True,
            'audit_checks': True,
            'orphan_checks': True,
            'circular_checks': True,
            'type_checks': True,
            'business_rules_checks': True
        }
    
    def _generate_consistency_report(self, check_time: float) -> Dict[str, Any]:
        """Generate consistency check report"""
        violations_by_type = {}
        violations_by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        auto_fixable_count = 0
        
        for violation in self.violations:
            # Count by type
            issue_type = violation.issue_type.value
            violations_by_type[issue_type] = violations_by_type.get(issue_type, 0) + 1
            
            # Count by severity
            violations_by_severity[violation.severity] += 1
            
            # Count auto-fixable
            if violation.auto_fixable:
                auto_fixable_count += 1
        
        return {
            'check_timestamp': datetime.utcnow().isoformat(),
            'check_duration_seconds': check_time,
            'total_violations': len(self.violations),
            'violations_by_type': violations_by_type,
            'violations_by_severity': violations_by_severity,
            'auto_fixable_violations': auto_fixable_count,
            'critical_violations': violations_by_severity['critical'],
            'high_violations': violations_by_severity['high'],
            'medium_violations': violations_by_severity['medium'],
            'low_violations': violations_by_severity['low'],
            'consistency_score': max(0, 100 - (len(self.violations) * 2)),
            'violations': [
                {
                    'type': v.issue_type.value,
                    'table': v.table_name,
                    'record_id': v.record_id,
                    'column': v.column_name,
                    'severity': v.severity,
                    'description': v.description,
                    'auto_fixable': v.auto_fixable,
                    'detected_at': v.detected_at.isoformat()
                }
                for v in self.violations
            ]
        }
    
    async def get_consistency_metrics(self) -> Dict[str, Any]:
        """Get consistency metrics"""
        if not self.check_history:
            return {"message": "No consistency checks performed yet"}
        
        latest_check = self.check_history[-1]
        
        # Calculate trends
        if len(self.check_history) >= 2:
            previous_check = self.check_history[-2]
            violations_trend = latest_check['violations_found'] - previous_check['violations_found']
            consistency_trend = latest_check['report']['consistency_score'] - previous_check['report']['consistency_score']
        else:
            violations_trend = 0
            consistency_trend = 0
        
        return {
            'latest_check': latest_check,
            'total_checks': len(self.check_history),
            'violations_trend': violations_trend,
            'consistency_trend': consistency_trend,
            'average_violations': sum(check['violations_found'] for check in self.check_history) / len(self.check_history),
            'average_consistency_score': sum(check['report']['consistency_score'] for check in self.check_history) / len(self.check_history),
            'critical_violations_history': [check['report']['critical_violations'] for check in self.check_history],
            'auto_fix_rate': sum(check['violations_fixed'] for check in self.check_history) / max(1, sum(check['violations_found'] for check in self.check_history)) * 100
        }

# Usage example
async def main():
    """Main execution function"""
    checker = DatabaseConsistencyChecker("postgresql://dedan:password@localhost:5432/dedan")
    
    # Run single consistency check
    report = await checker.run_full_consistency_check()
    
    print("Database Consistency Report:")
    print(json.dumps(report, indent=2, default=str))
    
    # Get metrics
    metrics = await checker.get_consistency_metrics()
    print(f"\nConsistency Metrics:")
    print(json.dumps(metrics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
