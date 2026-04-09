"""
DEDAN Mine - Changelog Reader Utility
Safe changelog reading with error handling
"""

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def read_changelog() -> Dict[str, Any]:
    """
    Safely read the CHANGELOG.txt file with error handling
    
    Returns:
        Dict containing changelog information or default values if file not found
    """
    try:
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.txt"
        
        if not changelog_path.exists():
            logger.warning("CHANGELOG.txt not found, using default version information")
            return {
                "version": "v5.0.0",
                "last_updated": "April 2026",
                "platform": "DEDAN Mine",
                "entries": [
                    "v1.0.0 - Initial Production Launch",
                    "v1.1.0 - AI Marketplace Integration"
                ],
                "file_found": False
            }
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Parse basic information from changelog
        lines = content.split('\n')
        version_line = next((line for line in lines if line.startswith('v') and '.' in line), None)
        
        return {
            "version": version_line.split(' - ')[0] if version_line else "v5.0.0",
            "content": content,
            "file_found": True,
            "file_path": str(changelog_path)
        }
        
    except FileNotFoundError:
        logger.warning("CHANGELOG.txt file not found, using default version")
        return {
            "version": "v5.0.0",
            "last_updated": "April 2026",
            "platform": "DEDAN Mine",
            "entries": [
                "v1.0.0 - Initial Production Launch",
                "v1.1.0 - AI Marketplace Integration"
            ],
            "file_found": False
        }
    except Exception as e:
        logger.error(f"Error reading CHANGELOG.txt: {str(e)}")
        return {
            "version": "v5.0.0",
            "last_updated": "April 2026",
            "platform": "DEDAN Mine",
            "entries": [
                "v1.0.0 - Initial Production Launch",
                "v1.1.0 - AI Marketplace Integration"
            ],
            "file_found": False,
            "error": str(e)
        }

def get_version() -> str:
    """
    Get current version from changelog
    
    Returns:
        Version string or default if changelog not available
    """
    changelog_info = read_changelog()
    return changelog_info.get("version", "v5.0.0")

def get_changelog_summary() -> str:
    """
    Get a summary of the changelog
    
    Returns:
        Summary string or default message
    """
    changelog_info = read_changelog()
    if changelog_info.get("file_found"):
        return f"DEDAN Mine {changelog_info.get('version', 'v5.0.0')} - Changelog available"
    else:
        return f"DEDAN Mine {changelog_info.get('version', 'v5.0.0')} - No changelog file found"
