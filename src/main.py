#!/usr/bin/env python3
"""
Main entry point for the Stock Allocation Tool application.
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from controllers.portfolio_controller import PortfolioController


def main():
    """Main application entry point."""
    try:
        # Create and initialize the controller
        controller = PortfolioController()
        
        # Initialize GUI and start the application
        controller.initialize_gui()
        controller.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)
    finally:
        # Clean shutdown
        try:
            controller.shutdown()
        except:
            pass


if __name__ == "__main__":
    main()