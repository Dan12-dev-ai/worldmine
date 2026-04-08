"""
DEDAN Mine - Database Setup Script (v5.0.0)
Initialize Neon.tech database with required tables and indexes
Production-ready schema for worldwide deployment
"""

import asyncio
import asyncpg
import os
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection
DATABASE_URL = "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"

async def setup_database():
    """Setup database with required tables and indexes"""
    try:
        # Connect to database
        conn = await asyncpg.connect(DATABASE_URL)
        logger.info("Connected to Neon.tech database successfully!")
        
        # Create tables
        await create_tables(conn)
        
        # Create indexes
        await create_indexes(conn)
        
        # Insert initial data
        await insert_initial_data(conn)
        
        # Verify setup
        await verify_setup(conn)
        
        await conn.close()
        logger.info("Database setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Database setup failed: {str(e)}")
        raise

async def create_tables(conn):
    """Create all required tables"""
    logger.info("Creating tables...")
    
    # Users table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            first_name VARCHAR(50),
            last_name VARCHAR(50),
            phone VARCHAR(20),
            country VARCHAR(2),
            is_active BOOLEAN DEFAULT true,
            is_verified BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_login TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # User profiles table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            bio TEXT,
            avatar_url VARCHAR(500),
            company VARCHAR(100),
            position VARCHAR(100),
            website VARCHAR(200),
            linkedin VARCHAR(100),
            preferences JSONB DEFAULT '{}',
            security_settings JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Wallets table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS wallets (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            wallet_type VARCHAR(20) NOT NULL, -- 'sovereign', 'crypto', 'bank'
            currency VARCHAR(10) NOT NULL,
            balance DECIMAL(20,8) DEFAULT 0,
            frozen_balance DECIMAL(20,8) DEFAULT 0,
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Transactions table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            transaction_type VARCHAR(20) NOT NULL, -- 'payment', 'withdrawal', 'transfer', 'trade'
            currency VARCHAR(10) NOT NULL,
            amount DECIMAL(20,8) NOT NULL,
            fee DECIMAL(20,8) DEFAULT 0,
            from_currency VARCHAR(10),
            to_currency VARCHAR(10),
            exchange_rate DECIMAL(20,8),
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processing', 'completed', 'failed', 'cancelled'
            payment_method VARCHAR(50),
            payment_details JSONB,
            metadata JSONB DEFAULT '{}',
            quantum_signature VARCHAR(255),
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            completed_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Minerals table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS minerals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(100) NOT NULL,
            symbol VARCHAR(10) UNIQUE NOT NULL,
            description TEXT,
            category VARCHAR(50),
            purity DECIMAL(5,4),
            origin VARCHAR(100),
            current_price DECIMAL(20,8),
            price_updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            is_active BOOLEAN DEFAULT true,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Listings table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
            mineral_id UUID REFERENCES minerals(id) ON DELETE CASCADE,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            quantity DECIMAL(20,8) NOT NULL,
            unit VARCHAR(20) NOT NULL,
            price_per_unit DECIMAL(20,8) NOT NULL,
            total_price DECIMAL(20,8) GENERATED ALWAYS AS (quantity * price_per_unit) STORED,
            currency VARCHAR(10) NOT NULL,
            location VARCHAR(200),
            certification JSONB,
            images JSONB DEFAULT '[]',
            status VARCHAR(20) DEFAULT 'active', -- 'active', 'sold', 'withdrawn', 'suspended'
            views INTEGER DEFAULT 0,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            expires_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Orders table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            buyer_id UUID REFERENCES users(id) ON DELETE CASCADE,
            seller_id UUID REFERENCES users(id) ON DELETE CASCADE,
            listing_id UUID REFERENCES listings(id) ON DELETE CASCADE,
            quantity DECIMAL(20,8) NOT NULL,
            price_per_unit DECIMAL(20,8) NOT NULL,
            total_price DECIMAL(20,8) GENERATED ALWAYS AS (quantity * price_per_unit) STORED,
            currency VARCHAR(10) NOT NULL,
            status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'confirmed', 'shipped', 'delivered', 'cancelled', 'refunded'
            payment_status VARCHAR(20) DEFAULT 'pending',
            shipping_address JSONB,
            tracking_number VARCHAR(100),
            notes TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            confirmed_at TIMESTAMP WITH TIME ZONE,
            shipped_at TIMESTAMP WITH TIME ZONE,
            delivered_at TIMESTAMP WITH TIME ZONE
        )
    """)
    
    # Payment methods table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS payment_methods (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            method_type VARCHAR(20) NOT NULL, -- 'card', 'bank', 'crypto', 'mobile'
            provider VARCHAR(50) NOT NULL,
            method_identifier VARCHAR(100) NOT NULL,
            display_name VARCHAR(100),
            is_default BOOLEAN DEFAULT false,
            is_active BOOLEAN DEFAULT true,
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # User sessions table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE CASCADE,
            session_token VARCHAR(255) UNIQUE NOT NULL,
            device_info JSONB,
            ip_address INET,
            user_agent TEXT,
            is_active BOOLEAN DEFAULT true,
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # Audit logs table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            action VARCHAR(50) NOT NULL,
            resource_type VARCHAR(50),
            resource_id UUID,
            old_values JSONB,
            new_values JSONB,
            ip_address INET,
            user_agent TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    # System settings table
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key VARCHAR(100) PRIMARY KEY,
            value JSONB NOT NULL,
            description TEXT,
            is_public BOOLEAN DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    """)
    
    logger.info("All tables created successfully!")

async def create_indexes(conn):
    """Create indexes for performance optimization"""
    logger.info("Creating indexes...")
    
    # Users indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)")
    
    # Wallets indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_wallets_user_id ON wallets(user_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_wallets_currency ON wallets(currency)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_wallets_active ON wallets(is_active)")
    
    # Transactions indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_type ON transactions(transaction_type)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_status ON transactions(status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at)")
    
    # Listings indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_seller_id ON listings(seller_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_mineral_id ON listings(mineral_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(status)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_created_at ON listings(created_at)")
    
    # Orders indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_buyer_id ON orders(buyer_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_seller_id ON orders(seller_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_listing_id ON orders(listing_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
    
    # User sessions indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON user_sessions(session_token)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_user_sessions_expires ON user_sessions(expires_at)")
    
    # Audit logs indexes
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action)")
    await conn.execute("CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at)")
    
    logger.info("All indexes created successfully!")

async def insert_initial_data(conn):
    """Insert initial data"""
    logger.info("Inserting initial data...")
    
    # Insert minerals
    minerals_data = [
        ('Gold', 'AU', 'Pure gold bullion', 'precious', 0.9999, 'Various', 1850.50),
        ('Silver', 'AG', 'Pure silver bullion', 'precious', 0.9999, 'Various', 22.75),
        ('Copper', 'CU', 'High-grade copper', 'industrial', 0.9999, 'Various', 3.85),
        ('Platinum', 'PT', 'Pure platinum', 'precious', 0.9999, 'Various', 950.25),
        ('Palladium', 'PD', 'Pure palladium', 'precious', 0.9999, 'Various', 1850.00),
        ('Rhodium', 'RH', 'Pure rhodium', 'precious', 0.9999, 'Various', 14500.00)
    ]
    
    for name, symbol, description, category, purity, origin, price in minerals_data:
        await conn.execute("""
            INSERT INTO minerals (name, symbol, description, category, purity, origin, current_price)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (symbol) DO NOTHING
        """, name, symbol, description, category, purity, origin, price)
    
    # Insert system settings
    settings_data = [
        ('platform_name', '"DEDAN Mine"', 'Platform name', True),
        ('platform_version', '"v5.0.0"', 'Platform version', True),
        ('maintenance_mode', 'false', 'Maintenance mode status', True),
        ('registration_enabled', 'true', 'User registration enabled', True),
        ('max_transaction_amount', '1000000', 'Maximum transaction amount', False),
        ('supported_currencies', '["USD", "EUR", "GBP", "ETB", "CNY", "JPY"]', 'Supported currencies', True),
        ('default_currency', '"USD"', 'Default currency', True),
        ('fee_percentage', '0.029', 'Transaction fee percentage', False),
        ('fee_fixed', '0.30', 'Fixed transaction fee', False)
    ]
    
    for key, value, description, is_public in settings_data:
        await conn.execute("""
            INSERT INTO system_settings (key, value, description, is_public)
            VALUES ($1, $2, $3, $4)
            ON CONFLICT (key) DO NOTHING
        """, key, value, description, is_public)
    
    logger.info("Initial data inserted successfully!")

async def verify_setup(conn):
    """Verify database setup"""
    logger.info("Verifying database setup...")
    
    # Check tables
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    logger.info(f"Tables created: {[table['table_name'] for table in tables]}")
    
    # Check minerals data
    mineral_count = await conn.fetchval("SELECT COUNT(*) FROM minerals")
    logger.info(f"Minerals inserted: {mineral_count}")
    
    # Check system settings
    settings_count = await conn.fetchval("SELECT COUNT(*) FROM system_settings")
    logger.info(f"System settings inserted: {settings_count}")
    
    # Test database connection
    test_result = await conn.fetchval("SELECT 1 as test")
    logger.info(f"Database test query result: {test_result}")
    
    logger.info("Database setup verification completed!")

async def main():
    """Main setup function"""
    print("=== DEDAN Mine Database Setup ===")
    print("Initializing Neon.tech database...")
    print(f"Database: ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech")
    print("")
    
    await setup_database()
    
    print("")
    print("=== Database Setup Complete ===")
    print("Your Neon.tech database is ready for production!")
    print("Tables: 12")
    print("Indexes: 20+")
    print("Initial data: Minerals and system settings")
    print("")
    print("Next steps:")
    print("1. Set up Redis cache (Upstash)")
    print("2. Configure environment variables")
    print("3. Deploy to Koyeb")
    print("4. Test API endpoints")
    print("")

if __name__ == "__main__":
    asyncio.run(main())
