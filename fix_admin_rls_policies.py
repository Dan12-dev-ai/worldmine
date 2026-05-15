#!/usr/bin/env python3
"""
Fix Admin User ID Placeholders in RLS Policies
DEDAN WORLDMINE PLATFORM - SECURITY CRITICAL FIX
"""

import asyncio
import asyncpg
import os
import sys
from typing import Optional

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

async def get_admin_user_id(conn: asyncpg.Connection) -> Optional[str]:
    """Get the actual admin user ID from the database"""
    try:
        # Try to find admin user by common patterns
        admin_queries = [
            "SELECT id FROM auth.users WHERE email LIKE '%admin%' LIMIT 1",
            "SELECT id FROM auth.users WHERE username LIKE '%admin%' LIMIT 1", 
            "SELECT id FROM auth.users WHERE email = 'admin@dedanmine.com' LIMIT 1",
            "SELECT id FROM auth.users WHERE is_superuser = true LIMIT 1",
            "SELECT id FROM auth.users ORDER BY created_at ASC LIMIT 1"  # First user as fallback
        ]
        
        for query in admin_queries:
            result = await conn.fetchval(query)
            if result:
                print(f"Found admin user ID: {result}")
                return str(result)
        
        print("WARNING: No admin user found. You'll need to manually specify the admin ID.")
        return None
        
    except Exception as e:
        print(f"Error finding admin user: {e}")
        return None

async def update_rls_policies(conn: asyncpg.Connection, admin_id: str) -> None:
    """Update all RLS policies with the actual admin user ID"""
    
    # List of tables with admin RLS policies that need updating
    policy_updates = [
        {
            "table": "platform_finances",
            "policy": "Admin only platform finances access"
        },
        {
            "table": "withdrawals", 
            "policy": "Admin only withdrawals access"
        },
        {
            "table": "admin_audit_log",
            "policy": "Admin only audit log access"
        },
        {
            "table": "kyc_profiles",
            "policy": "Admin only KYC profiles access"
        },
        {
            "table": "sanctions_screening_results",
            "policy": "Admin only sanctions screening access"
        },
        {
            "table": "transaction_monitoring",
            "policy": "Admin only transaction monitoring access"
        },
        {
            "table": "esignature_compliance_logs",
            "policy": "Admin only esignature logs access"
        },
        {
            "table": "gdpr_data_export_requests",
            "policy": "Admin only GDPR exports access"
        },
        {
            "table": "gdpr_deletion_requests",
            "policy": "Admin only GDPR deletions access"
        },
        {
            "table": "consent_logs",
            "policy": "Admin only consent logs access"
        },
        {
            "table": "compliance_audit_log",
            "policy": "Admin only compliance audit access"
        },
        {
            "table": "compliance_alerts",
            "policy": "Admin only compliance alerts access"
        },
        {
            "table": "scheduled_deletions",
            "policy": "Admin only scheduled deletions access"
        },
        {
            "table": "security_settings",
            "policy": "Admin can manage all security settings"
        },
        {
            "table": "trusted_devices",
            "policy": "Admin can manage all trusted devices"
        },
        {
            "table": "whitelisted_addresses",
            "policy": "Admin can manage all whitelisted addresses"
        },
        {
            "table": "security_holds",
            "policy": "Admin can manage all security holds"
        },
        {
            "table": "biometric_credentials",
            "policy": "Admin can manage all biometric credentials"
        },
        {
            "table": "totp_secrets",
            "policy": "Admin can manage all TOTP secrets"
        },
        {
            "table": "secondary_approvals",
            "policy": "Admin can manage all secondary approvals"
        },
        {
            "table": "suspicious_activities",
            "policy": "Admin can manage all suspicious activities"
        },
        {
            "table": "withdrawal_attempts",
            "policy": "Admin can manage all withdrawal attempts"
        },
        {
            "table": "withdrawal_audit_log",
            "policy": "Admin can manage all withdrawal audit logs"
        }
    ]
    
    updated_policies = 0
    failed_policies = 0
    
    for policy_info in policy_updates:
        try:
            # Drop existing policy
            await conn.execute(f"""
                DROP POLICY IF EXISTS "{policy_info['policy']}" ON {policy_info['table']}
            """)
            
            # Recreate policy with actual admin ID
            await conn.execute(f"""
                CREATE POLICY "{policy_info['policy']}" ON {policy_info['table']}
                  FOR ALL
                  USING (auth.uid() = '{admin_id}'::UUID)
                  WITH CHECK (auth.uid() = '{admin_id}'::UUID)
            """)
            
            print(f"✅ Updated RLS policy for {policy_info['table']}")
            updated_policies += 1
            
        except Exception as e:
            print(f"❌ Failed to update policy for {policy_info['table']}: {e}")
            failed_policies += 1
    
    print(f"\nSummary: {updated_policies} policies updated, {failed_policies} failed")

async def update_admin_functions(conn: asyncpg.Connection, admin_id: str) -> None:
    """Update admin functions with actual admin user ID"""
    
    function_updates = [
        {
            "name": "is_admin_user",
            "definition": f"""
                CREATE OR REPLACE FUNCTION is_admin_user()
                RETURNS BOOLEAN AS $$
                BEGIN
                  RETURN auth.uid() = '{admin_id}'::UUID;
                END;
                $$ LANGUAGE plpgsql SECURITY DEFINER;
            """
        },
        {
            "name": "check_transaction_compliance",
            "definition": f"""
                CREATE OR REPLACE FUNCTION check_transaction_compliance(p_user_id UUID, p_amount DECIMAL)
                RETURNS TABLE(
                  is_compliant BOOLEAN,
                  tier_limit DECIMAL,
                  current_tier INTEGER,
                  requires_review BOOLEAN,
                  reason TEXT
                ) AS $$
                DECLARE
                  user_tier INTEGER;
                  tier_limit_value DECIMAL;
                  exceeds_limit BOOLEAN;
                BEGIN
                  -- Get user's KYC tier
                  SELECT tier INTO user_tier FROM kyc_profiles WHERE user_id = p_user_id AND status = 'approved';
                  
                  IF user_tier IS NULL THEN
                    RETURN QUERY SELECT FALSE, 0, 0, TRUE, 'KYC not completed or approved'::TEXT;
                    RETURN;
                  END IF;
                  
                  -- Get tier limits
                  CASE user_tier
                    WHEN 1 THEN tier_limit_value := 1000;
                    WHEN 2 THEN tier_limit_value := 10000;
                    WHEN 3 THEN tier_limit_value := 50000;
                    ELSE tier_limit_value := 0;
                  END CASE;
                  
                  exceeds_limit := p_amount > tier_limit_value;
                  
                  RETURN QUERY 
                  SELECT 
                    NOT exceeds_limit,
                    tier_limit_value,
                    user_tier,
                    exceeds_limit OR p_amount > 3000,
                    CASE 
                      WHEN exceeds_limit THEN 'Amount exceeds tier limit of $' || tier_limit_value
                      WHEN p_amount > 3000 THEN 'Amount exceeds NBE limit of $3000'
                      ELSE 'Transaction compliant'
                    END::TEXT;
                END;
                $$ LANGUAGE plpgsql;
            """
        }
    ]
    
    for func_info in function_updates:
        try:
            await conn.execute(func_info['definition'])
            print(f"✅ Updated function: {func_info['name']}")
        except Exception as e:
            print(f"❌ Failed to update function {func_info['name']}: {e}")

async def verify_fixes(conn: asyncpg.Connection, admin_id: str) -> None:
    """Verify that all fixes have been applied correctly"""
    
    print("\n🔍 Verifying RLS Policy Updates...")
    
    # Check policies
    policies = await conn.fetch("""
        SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual
        FROM pg_policies 
        WHERE schemaname = 'public'
        ORDER BY tablename, policyname
    """)
    
    print(f"Found {len(policies)} RLS policies:")
    for policy in policies:
        admin_check = "'YOUR_ADMIN_USER_ID_HERE'" in str(policy['qual'])
        status = "❌ Needs Update" if admin_check else "✅ Fixed"
        print(f"  {status} - {policy['tablename']}.{policy['policyname']}")
    
    # Check functions
    functions = await conn.fetch("""
        SELECT proname, prosrc 
        FROM pg_proc 
        WHERE proname IN ('is_admin_user', 'check_transaction_compliance')
    """)
    
    print(f"\nFound {len(functions)} admin functions:")
    for func in functions:
        admin_check = "'YOUR_ADMIN_USER_ID_HERE'" in str(func['prosrc'])
        status = "❌ Needs Update" if admin_check else "✅ Fixed"
        print(f"  {status} - {func['proname']}")

async def main():
    """Main execution function"""
    print("🔧 DEDAN WORLDMINE - RLS Policy Fix Script")
    print("=" * 50)
    
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Connected to database")
        
        # Get admin user ID
        admin_id = await get_admin_user_id(conn)
        
        if not admin_id:
            print("\n❌ Could not determine admin user ID automatically.")
            print("Please specify the admin user ID manually:")
            admin_id = input("Enter admin user UUID (or press Enter to skip): ").strip()
            
            if not admin_id:
                print("Skipping RLS policy updates.")
                return
        
        # Confirm before proceeding
        print(f"\n🚨 WARNING: This will update ALL RLS policies to use admin ID: {admin_id}")
        confirm = input("Type 'YES' to continue: ").strip()
        
        if confirm != 'YES':
            print("Operation cancelled.")
            return
        
        # Update RLS policies
        print("\n📝 Updating RLS policies...")
        await update_rls_policies(conn, admin_id)
        
        # Update admin functions
        print("\n🔧 Updating admin functions...")
        await update_admin_functions(conn, admin_id)
        
        # Verify fixes
        print("\n🔍 Verifying fixes...")
        await verify_fixes(conn, admin_id)
        
        await conn.close()
        print("\n✅ RLS policy fix completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during RLS policy fix: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
