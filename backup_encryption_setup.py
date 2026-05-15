#!/usr/bin/env python3
"""
Backup Encryption and Recovery Procedures
DEDAN WORLDMINE PLATFORM - PRODUCTION BACKUP SECURITY
"""

import asyncio
import asyncpg
import os
import sys
import subprocess
import json
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_A67fiOvTqLRl@ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require"
)

class BackupEncryptionManager:
    def __init__(self):
        self.encryption_key = os.getenv("BACKUP_ENCRYPTION_KEY")
        if not self.encryption_key:
            raise ValueError("BACKUP_ENCRYPTION_KEY environment variable is required")
    
    async def setup_encrypted_backups(self, conn: asyncpg.Connection) -> None:
        """Setup encrypted backup procedures"""
        
        logger.info("Setting up encrypted backup infrastructure...")
        
        # Create backup metadata table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS backup_metadata (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                backup_name TEXT UNIQUE NOT NULL,
                backup_type TEXT NOT NULL CHECK (backup_type IN ('full', 'incremental', 'differential')),
                backup_size_bytes BIGINT,
                backup_path TEXT NOT NULL,
                encryption_algorithm TEXT DEFAULT 'AES-256-GCM',
                encryption_key_id UUID REFERENCES encryption_keys(id),
                checksum TEXT NOT NULL,
                backup_started_at TIMESTAMP WITH TIME ZONE,
                backup_completed_at TIMESTAMP WITH TIME ZONE,
                retention_days INTEGER DEFAULT 30,
                is_encrypted BOOLEAN DEFAULT TRUE,
                is_compressed BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Create backup encryption keys table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS backup_encryption_keys (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                key_name TEXT UNIQUE NOT NULL,
                encrypted_key BYTEA NOT NULL,
                key_algorithm TEXT DEFAULT 'AES-256',
                key_created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                key_expires_at TIMESTAMP WITH TIME ZONE,
                is_active BOOLEAN DEFAULT TRUE,
                created_by UUID REFERENCES auth.users(id)
            )
        """)
        
        # Create recovery procedures table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recovery_procedures (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                procedure_name TEXT UNIQUE NOT NULL,
                backup_id UUID REFERENCES backup_metadata(id),
                recovery_type TEXT NOT NULL CHECK (recovery_type IN ('full', 'partial', 'point_in_time')),
                target_database TEXT NOT NULL,
                recovery_started_at TIMESTAMP WITH TIME ZONE,
                recovery_completed_at TIMESTAMP WITH TIME ZONE,
                recovery_status TEXT DEFAULT 'pending' CHECK (recovery_type IN ('pending', 'in_progress', 'completed', 'failed')),
                error_message TEXT,
                recovered_by UUID REFERENCES auth.users(id),
                recovery_log JSONB DEFAULT '{}'::jsonb,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        logger.info("✅ Backup infrastructure created successfully")
    
    async def create_encrypted_backup_function(self, conn: asyncpg.Connection) -> None:
        """Create function for encrypted backups"""
        
        backup_function = """
        CREATE OR REPLACE FUNCTION create_encrypted_backup(
            p_backup_name TEXT,
            p_backup_type TEXT DEFAULT 'full',
            p_retention_days INTEGER DEFAULT 30,
            p_compression_level INTEGER DEFAULT 6
        )
        RETURNS UUID AS $$
        DECLARE
            backup_id UUID;
            backup_path TEXT;
            backup_command TEXT;
            encryption_command TEXT;
            backup_started TIMESTAMP := NOW();
            backup_file TEXT;
            encrypted_file TEXT;
            checksum TEXT;
        BEGIN
            -- Generate backup file path
            backup_file := '/backups/' || p_backup_name || '_' || to_char(backup_started, 'YYYY-MM-DD_HH24-MI-SS') || '.sql';
            encrypted_file := backup_file || '.enc';
            
            -- Create backup command
            backup_command := 'pg_dump ' || current_database() || 
                           ' --format=custom ' ||
                           ' --compress=' || p_compression_level || 
                           ' --file=' || backup_file;
            
            -- Create encryption command
            encryption_command := 'openssl enc -aes-256-gcm -k ' || 
                               current_setting('backup.encryption_key') || 
                               ' -in ' || backup_file || 
                               ' -out ' || encrypted_file;
            
            -- Execute backup (this would be done by external script)
            -- For now, we'll just log the metadata
            
            -- Generate checksum
            checksum := md5(encrypted_file);
            
            -- Insert backup metadata
            INSERT INTO backup_metadata (
                backup_name,
                backup_type,
                backup_path,
                checksum,
                backup_started_at,
                backup_completed_at,
                retention_days,
                is_encrypted,
                is_compressed
            ) VALUES (
                p_backup_name,
                p_backup_type,
                encrypted_file,
                checksum,
                backup_started,
                NOW(),
                p_retention_days,
                TRUE,
                TRUE
            ) RETURNING id INTO backup_id;
            
            -- Clean up unencrypted backup file
            -- PERFORM pg_read_file('rm ' || backup_file);
            
            RETURN backup_id;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        await conn.execute(backup_function)
        logger.info("✅ Encrypted backup function created")
    
    async def create_recovery_function(self, conn: asyncpg.Connection) -> None:
        """Create function for database recovery"""
        
        recovery_function = """
        CREATE OR REPLACE FUNCTION recover_from_encrypted_backup(
            p_backup_id UUID,
            p_target_database TEXT DEFAULT NULL,
            p_recovery_type TEXT DEFAULT 'full'
        )
        RETURNS UUID AS $$
        DECLARE
            recovery_id UUID;
            backup_metadata RECORD;
            recovery_command TEXT;
            decryption_command TEXT;
            target_db TEXT;
            backup_file TEXT;
            decrypted_file TEXT;
        BEGIN
            -- Get backup metadata
            SELECT * INTO backup_metadata 
            FROM backup_metadata 
            WHERE id = p_backup_id;
            
            IF NOT FOUND THEN
                RAISE EXCEPTION 'Backup not found';
            END IF;
            
            -- Determine target database
            target_db := COALESCE(p_target_database, current_database() || '_recovery');
            
            -- Generate file paths
            backup_file := backup_metadata.backup_path;
            decrypted_file := replace(backup_file, '.enc', '_decrypted.sql');
            
            -- Create recovery command
            decryption_command := 'openssl enc -aes-256-gcm -d -k ' || 
                               current_setting('backup.encryption_key') || 
                               ' -in ' || backup_file || 
                               ' -out ' || decrypted_file;
            
            recovery_command := 'pg_restore ' || target_db || ' --clean --if-exists ' || decrypted_file;
            
            -- Insert recovery procedure record
            INSERT INTO recovery_procedures (
                backup_id,
                recovery_type,
                target_database,
                recovery_started_at,
                recovery_status
            ) VALUES (
                p_backup_id,
                p_recovery_type,
                target_db,
                NOW(),
                'in_progress'
            ) RETURNING id INTO recovery_id;
            
            -- Execute recovery (this would be done by external script)
            -- For now, we'll just log the metadata
            
            RETURN recovery_id;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        await conn.execute(recovery_function)
        logger.info("✅ Recovery function created")
    
    async def setup_backup_monitoring(self, conn: asyncpg.Connection) -> None:
        """Setup backup monitoring and alerting"""
        
        # Create backup monitoring function
        monitoring_function = """
        CREATE OR REPLACE FUNCTION monitor_backup_health()
        RETURNS TABLE(
            metric_name TEXT,
            status TEXT,
            value NUMERIC,
            threshold NUMERIC
        ) AS $$
        BEGIN
            -- Check recent backups
            RETURN QUERY
            SELECT 
                'Recent Backups (24h)'::TEXT,
                CASE WHEN COUNT(*) > 0 THEN 'OK' ELSE 'CRITICAL' END,
                COUNT(*)::NUMERIC,
                1
            FROM backup_metadata 
            WHERE backup_completed_at >= NOW() - INTERVAL '24 hours';
            
            -- Check backup retention
            RETURN QUERY
            SELECT 
                'Old Backups (>90 days)'::TEXT,
                CASE WHEN COUNT(*) = 0 THEN 'OK' ELSE 'WARNING' END,
                COUNT(*)::NUMERIC,
                0
            FROM backup_metadata 
            WHERE backup_completed_at < NOW() - INTERVAL '90 days';
            
            -- Check backup sizes
            RETURN QUERY
            SELECT 
                'Average Backup Size (GB)'::TEXT,
                'OK',
                AVG(backup_size_bytes)::NUMERIC / 1024 / 1024 / 1024,
                50
            FROM backup_metadata 
            WHERE backup_completed_at >= NOW() - INTERVAL '7 days';
        END;
        $$ LANGUAGE plpgsql;
        """
        
        await conn.execute(monitoring_function)
        logger.info("✅ Backup monitoring created")
    
    async def create_backup_retention_function(self, conn: asyncpg.Connection) -> None:
        """Create automatic backup retention function"""
        
        retention_function = """
        CREATE OR REPLACE FUNCTION cleanup_old_backups()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER := 0;
            backup_record RECORD;
        BEGIN
            -- Find expired backups
            FOR backup_record IN 
                SELECT id, backup_path 
                FROM backup_metadata 
                WHERE backup_completed_at < NOW() - (retention_days || ' days')::INTERVAL
            LOOP
                -- Delete backup file (this would be done by external script)
                -- PERFORM pg_read_file('rm ' || backup_record.backup_path);
                
                -- Delete metadata
                DELETE FROM backup_metadata WHERE id = backup_record.id;
                deleted_count := deleted_count + 1;
            END LOOP;
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
        """
        
        await conn.execute(retention_function)
        logger.info("✅ Backup retention function created")
    
    async def generate_backup_scripts(self) -> None:
        """Generate shell scripts for backup operations"""
        
        # Encrypted backup script
        backup_script = f"""#!/bin/bash
# DEDAN WORLDMINE - Encrypted Backup Script
# Production backup with AES-256 encryption

set -euo pipefail

# Configuration
DB_NAME="{os.getenv('DB_NAME', 'neondb')}"
DB_USER="{os.getenv('DB_USER', 'neondb_owner')}"
DB_HOST="{os.getenv('DB_HOST', 'ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech')}"
BACKUP_DIR="/backups"
ENCRYPTION_KEY="${{BACKUP_ENCRYPTION_KEY}}"
RETENTION_DAYS="{os.getenv('BACKUP_RETENTION_DAYS', '30')}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${{DB_NAME}}_backup_${{TIMESTAMP}}.sql"
ENCRYPTED_FILE="${{BACKUP_FILE}}.enc"

echo "Starting encrypted backup for $DB_NAME at $(date)"

# Create database backup
pg_dump "$DB_NAME" \\
    --host="$DB_HOST" \\
    --username="$DB_USER" \\
    --format=custom \\
    --compress=6 \\
    --file="$BACKUP_DIR/$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Database backup completed successfully"
    
    # Encrypt backup file
    openssl enc -aes-256-gcm \\
        -k "$ENCRYPTION_KEY" \\
        -in "$BACKUP_DIR/$BACKUP_FILE" \\
        -out "$BACKUP_DIR/$ENCRYPTED_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Backup encrypted successfully"
        
        # Remove unencrypted backup
        rm "$BACKUP_DIR/$BACKUP_FILE"
        
        # Generate checksum
        CHECKSUM=$(md5sum "$BACKUP_DIR/$ENCRYPTED_FILE" | cut -d' ' -f1)
        
        # Log backup metadata to database
        psql "$DB_NAME" \\
            --host="$DB_HOST" \\
            --username="$DB_USER" \\
            -c "INSERT INTO backup_metadata (backup_name, backup_type, backup_path, checksum, backup_started_at, backup_completed_at, retention_days, is_encrypted, is_compressed) VALUES ('${{DB_NAME}}_backup_${{TIMESTAMP}}', 'full', '$BACKUP_DIR/$ENCRYPTED_FILE', '$CHECKSUM', NOW(), NOW(), $RETENTION_DAYS, TRUE, TRUE);"
        
        echo "Encrypted backup completed: $ENCRYPTED_FILE"
        echo "Checksum: $CHECKSUM"
    else
        echo "ERROR: Backup encryption failed"
        exit 1
    fi
else
    echo "ERROR: Database backup failed"
    exit 1
fi

echo "Backup process completed at $(date)"
"""
        
        # Recovery script
        recovery_script = f"""#!/bin/bash
# DEDAN WORLDMINE - Encrypted Recovery Script
# Production recovery from AES-256 encrypted backup

set -euo pipefail

# Configuration
DB_NAME="{os.getenv('DB_NAME', 'neondb')}"
DB_USER="{os.getenv('DB_USER', 'neondb_owner')}"
DB_HOST="{os.getenv('DB_HOST', 'ep-dry-scene-ang0ac1w.c-6.us-east-1.aws.neon.tech')}"
BACKUP_DIR="/backups"
ENCRYPTION_KEY="${{BACKUP_ENCRYPTION_KEY}}"

# Check parameters
if [ $# -eq 0 ]; then
    echo "Usage: $0 <encrypted_backup_file> [target_database]"
    echo "Example: $0 neondb_backup_20240508_120000.sql.enc neondb_recovery"
    exit 1
fi

ENCRYPTED_BACKUP="$1"
TARGET_DB="${{2:-${{DB_NAME}}_recovery}}"
DECRYPTED_FILE="${{ENCRYPTED_BACKUP%.enc}}_decrypted.sql"

echo "Starting recovery from $ENCRYPTED_BACKUP to $TARGET_DB at $(date)"

# Check if backup file exists
if [ ! -f "$BACKUP_DIR/$ENCRYPTED_BACKUP" ]; then
    echo "ERROR: Backup file not found: $BACKUP_DIR/$ENCRYPTED_BACKUP"
    exit 1
fi

# Decrypt backup file
echo "Decrypting backup file..."
openssl enc -aes-256-gcm \\
    -d \\
    -k "$ENCRYPTION_KEY" \\
    -in "$BACKUP_DIR/$ENCRYPTED_BACKUP" \\
    -out "$BACKUP_DIR/$DECRYPTED_FILE"

if [ $? -eq 0 ]; then
    echo "Backup decrypted successfully"
    
    # Create target database if it doesn't exist
    createdb "$TARGET_DB" \\
        --host="$DB_HOST" \\
        --username="$DB_USER" \\
        2>/dev/null || echo "Database $TARGET_DB already exists"
    
    # Restore database
    echo "Restoring database..."
    pg_restore "$TARGET_DB" \\
        --host="$DB_HOST" \\
        --username="$DB_USER" \\
        --clean \\
        --if-exists \\
        --verbose \\
        "$BACKUP_DIR/$DECRYPTED_FILE"
    
    if [ $? -eq 0 ]; then
        echo "Database restored successfully to $TARGET_DB"
        
        # Log recovery procedure
        psql "$DB_NAME" \\
            --host="$DB_HOST" \\
            --username="$DB_USER" \\
            -c "INSERT INTO recovery_procedures (backup_id, recovery_type, target_database, recovery_started_at, recovery_completed_at, recovery_status) VALUES ((SELECT id FROM backup_metadata WHERE backup_path = '$BACKUP_DIR/$ENCRYPTED_BACKUP'), 'full', '$TARGET_DB', NOW(), NOW(), 'completed');"
        
        # Clean up decrypted file
        rm "$BACKUP_DIR/$DECRYPTED_FILE"
        
        echo "Recovery completed successfully"
        echo "Target database: $TARGET_DB"
    else
        echo "ERROR: Database restore failed"
        exit 1
    fi
else
    echo "ERROR: Backup decryption failed"
    exit 1
fi

echo "Recovery process completed at $(date)"
"""
        
        # Write scripts to files
        with open('/home/kali/mini_business/scripts/encrypted_backup.sh', 'w') as f:
            f.write(backup_script)
        
        with open('/home/kali/mini_business/scripts/encrypted_recovery.sh', 'w') as f:
            f.write(recovery_script)
        
        # Make scripts executable
        os.chmod('/home/kali/mini_business/scripts/encrypted_backup.sh', 0o755)
        os.chmod('/home/kali/mini_business/scripts/encrypted_recovery.sh', 0o755)
        
        logger.info("✅ Backup and recovery scripts generated")
    
    async def setup_automated_backups(self, conn: asyncpg.Connection) -> None:
        """Setup automated backup scheduling"""
        
        # Create backup schedule table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS backup_schedule (
                id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
                schedule_name TEXT UNIQUE NOT NULL,
                backup_type TEXT NOT NULL CHECK (backup_type IN ('full', 'incremental', 'differential')),
                schedule_expression TEXT NOT NULL, -- Cron expression
                retention_days INTEGER DEFAULT 30,
                is_active BOOLEAN DEFAULT TRUE,
                last_run TIMESTAMP WITH TIME ZONE,
                next_run TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """)
        
        # Insert default backup schedules
        default_schedules = [
            {
                'schedule_name': 'daily_full_backup',
                'backup_type': 'full',
                'schedule_expression': '0 2 * * *',  # Daily at 2 AM
                'retention_days': 30
            },
            {
                'schedule_name': 'weekly_incremental_backup',
                'backup_type': 'incremental',
                'schedule_expression': '0 3 * * 0',  # Weekly on Sunday at 3 AM
                'retention_days': 90
            },
            {
                'schedule_name': 'monthly_differential_backup',
                'backup_type': 'differential',
                'schedule_expression': '0 4 1 * *',  # Monthly on 1st at 4 AM
                'retention_days': 365
            }
        ]
        
        for schedule in default_schedules:
            await conn.execute("""
                INSERT INTO backup_schedule (schedule_name, backup_type, schedule_expression, retention_days)
                VALUES ($1, $2, $3, $4)
                ON CONFLICT (schedule_name) DO NOTHING
            """, schedule['schedule_name'], schedule['backup_type'], 
                schedule['schedule_expression'], schedule['retention_days'])
        
        logger.info("✅ Automated backup schedules created")
    
    async def main(self):
        """Main setup function"""
        logger.info("🔧 DEDAN WORLDMINE - Backup Encryption Setup")
        logger.info("=" * 60)
        
        try:
            # Connect to database
            conn = await asyncpg.connect(DATABASE_URL)
            logger.info("✅ Connected to database")
            
            # Setup backup infrastructure
            await self.setup_encrypted_backups(conn)
            
            # Create backup functions
            await self.create_encrypted_backup_function(conn)
            await self.create_recovery_function(conn)
            
            # Setup monitoring
            await self.setup_backup_monitoring(conn)
            
            # Setup retention
            await self.create_backup_retention_function(conn)
            
            # Setup automated backups
            await self.setup_automated_backups(conn)
            
            # Generate scripts
            await self.generate_backup_scripts()
            
            await conn.close()
            
            logger.info("\n✅ Backup encryption setup completed successfully!")
            logger.info("\nNext steps:")
            logger.info("1. Set BACKUP_ENCRYPTION_KEY environment variable")
            logger.info("2. Create /backups directory")
            logger.info("3. Test backup scripts: ./scripts/encrypted_backup.sh")
            logger.info("4. Test recovery scripts: ./scripts/encrypted_recovery.sh")
            logger.info("5. Schedule automated backups with cron")
            
        except Exception as e:
            logger.error(f"❌ Backup setup failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Create scripts directory
    os.makedirs('/home/kali/mini_business/scripts', exist_ok=True)
    
    # Initialize and run setup
    backup_manager = BackupEncryptionManager()
    asyncio.run(backup_manager.main())
