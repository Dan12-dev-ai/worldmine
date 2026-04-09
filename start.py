#!/usr/bin/env python3
"""
DEDAN Mine - Production Startup Script
Entry point for Render deployment
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main startup function"""
    try:
        logger.info("?? Starting DEDAN Mine application...")
        
        # Import and run the FastAPI app
        from app import main as app_main
        app_main()
        
    except ImportError as e:
        logger.error(f"?? Import error: {e}")
        logger.error("?? Please ensure all dependencies are installed")
        sys.exit(1)
    except Exception as e:
        logger.error(f"?? Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
