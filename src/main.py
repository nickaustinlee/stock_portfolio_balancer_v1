#!/usr/bin/env python3
"""
Main entry point for the Stock Allocation Tool application.

Usage:
    python src/main.py [--debug|-d]
    
    --debug, -d: Enable debug mode for verbose logging
    
Environment variables:
    STOCK_TOOL_DEBUG=1: Enable debug mode
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from controllers.portfolio_controller import PortfolioController
from utils.debug import logger


def main():
    """Main application entry point."""
    try:
        # Show debug status
        if logger.debug_enabled:
            logger.info("Debug mode enabled")
        
        # Create and initialize the controller
        controller = PortfolioController()
        
        # Initialize GUI and start the application
        controller.initialize_gui()
        controller.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error("Application error: %s", e)
        sys.exit(1)
    finally:
        # Clean shutdown
        try:
            controller.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()