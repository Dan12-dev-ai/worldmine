"""
🛠️ DEDAN 2.0 - UNIFIED UTILITIES PACKAGE
Consolidated utility functions eliminating all duplicate code
"""

# Legacy imports (for backward compatibility)
from .changelog_reader import read_changelog, get_version, get_changelog_summary

# New unified utilities
from .crypto import (
    unified_crypto,
    generate_biometric_hash,
    compare_biometric_hashes,
    generate_quantum_signature,
    verify_quantum_signature,
    get_explorer_url,
    verify_webhook_signature,
    generate_session_signature,
    encrypt_sensitive_data
)

from .database import (
    unified_db,
    get_database_connection,
    get_user_by_id,
    get_user_by_email
)

from .webhooks import (
    unified_webhooks,
    verify_webhook_signature as verify_webhook_signature_v2,
    process_webhook
)

__all__ = [
    # Legacy functions
    'read_changelog', 'get_version', 'get_changelog_summary',
    
    # Unified crypto utilities
    'unified_crypto',
    'generate_biometric_hash',
    'compare_biometric_hashes',
    'generate_quantum_signature',
    'verify_quantum_signature',
    'get_explorer_url',
    'verify_webhook_signature',
    'generate_session_signature',
    'encrypt_sensitive_data',
    
    # Unified database utilities
    'unified_db',
    'get_database_connection',
    'get_user_by_id',
    'get_user_by_email',
    
    # Unified webhook utilities
    'unified_webhooks',
    'verify_webhook_signature_v2',
    'process_webhook'
]
