"""
World-Mine Row Level Security (RLS) Policies
Enterprise-grade tenant-aware security for sensitive tables
"""

import logging
from typing import Dict, Any, List, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RLSOperation(Enum):
    SELECT = "SELECT"
    INSERT = "INSERT"
    UPDATE = "UPDATE"
    DELETE = "DELETE"

class RLSPolicy:
    """Row Level Security Policy"""
    
    def __init__(
        self,
        table_name: str,
        policy_name: str,
        operation: RLSOperation,
        using_expression: str,
        check_expression: Optional[str] = None
    ):
        self.table_name = table_name
        self.policy_name = policy_name
        self.operation = operation
        self.using_expression = using_expression
        self.check_expression = check_expression
        
    def to_sql(self) -> str:
        """Generate SQL for RLS policy"""
        sql = f"""
        CREATE POLICY {self.policy_name}
        ON {self.table_name}
        FOR {self.operation.value}
        """
        
        if self.using_expression:
            sql += f"\n        USING ({self.using_expression})"
            
        if self.check_expression:
            sql += f"\n        WITH CHECK ({self.check_expression})"
            
        return sql

class RLSPolicyManager:
    """Enterprise-grade RLS policy manager"""
    
    def __init__(self):
        self.policies: List[RLSPolicy] = []
        
    def add_policy(self, policy: RLSPolicy):
        """Add RLS policy"""
        self.policies.append(policy)
        logger.info(f"Added RLS policy: {policy.policy_name} on {policy.table_name}")
        
    def get_policies_for_table(self, table_name: str) -> List[RLSPolicy]:
        """Get all policies for a table"""
        return [p for p in self.policies if p.table_name == table_name]
        
    def generate_all_policies_sql(self) -> str:
        """Generate SQL for all policies"""
        sql_statements = []
        
        # Enable RLS on all tables
        tables = set(p.table_name for p in self.policies)
        for table in tables:
            sql_statements.append(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            
        # Add policies
        for policy in self.policies:
            sql_statements.append(policy.to_sql() + ";")
            
        return "\n".join(sql_statements)

# Initialize RLS policies for sensitive tables
rls_manager = RLSPolicyManager()

# Users table - Users can only see their own data
rls_manager.add_policy(RLSPolicy(
    table_name="users",
    policy_name="users_select_own",
    operation=RLSOperation.SELECT,
    using_expression="user_id = current_user_id()"
))

rls_manager.add_policy(RLSPolicy(
    table_name="users",
    policy_name="users_update_own",
    operation=RLSOperation.UPDATE,
    using_expression="user_id = current_user_id()",
    check_expression="user_id = current_user_id()"
))

# Listings table - Sellers can see/edit their own listings
rls_manager.add_policy(RLSPolicy(
    table_name="listings",
    policy_name="listings_select_own",
    operation=RLSOperation.SELECT,
    using_expression="seller_id = current_user_id() OR is_public = true"
))

rls_manager.add_policy(RLSPolicy(
    table_name="listings",
    policy_name="listings_update_own",
    operation=RLSOperation.UPDATE,
    using_expression="seller_id = current_user_id()",
    check_expression="seller_id = current_user_id()"
))

# Transactions table - Users can see their own transactions
rls_manager.add_policy(RLSPolicy(
    table_name="transactions",
    policy_name="transactions_select_own",
    operation=RLSOperation.SELECT,
    using_expression="buyer_id = current_user_id() OR seller_id = current_user_id()"
))

# Bids table - Users can see bids on their listings or their own bids
rls_manager.add_policy(RLSPolicy(
    table_name="bids",
    policy_name="bids_select_relevant",
    operation=RLSOperation.SELECT,
    using_expression="bidder_id = current_user_id() OR listing_id IN (SELECT id FROM listings WHERE seller_id = current_user_id())"
))

rls_manager.add_policy(RLSPolicy(
    table_name="bids",
    policy_name="bids_insert_own",
    operation=RLSOperation.INSERT,
    check_expression="bidder_id = current_user_id()"
))

# Audit logs - Only admins can see all logs
rls_manager.add_policy(RLSPolicy(
    table_name="audit_logs",
    policy_name="audit_logs_select_admin",
    operation=RLSOperation.SELECT,
    using_expression="EXISTS (SELECT 1 FROM users WHERE user_id = current_user_id() AND user_type = 'admin')"
))

# AI logs - Users can see logs for their own AI interactions
rls_manager.add_policy(RLSPolicy(
    table_name="ai_logs",
    policy_name="ai_logs_select_own",
    operation=RLSOperation.SELECT,
    using_expression="user_id = current_user_id() OR EXISTS (SELECT 1 FROM users WHERE user_id = current_user_id() AND user_type = 'admin')"
))

def get_rls_migration_sql() -> str:
    """Get complete RLS migration SQL"""
    return rls_manager.generate_all_policies_sql()

def apply_rls_policies():
    """Apply RLS policies to database"""
    sql = get_rls_migration_sql()
    logger.info("RLS policies generated for application")
    return sql
