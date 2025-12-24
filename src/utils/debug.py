"""
Debug utilities for the Stock Allocation Tool.
"""

import os
import sys
from typing import Any


class DebugLogger:
    """Simple debug logger that can be enabled/disabled."""
    
    def __init__(self):
        # Check for debug mode via environment variable or command line
        self.debug_enabled = (
            os.getenv('STOCK_TOOL_DEBUG', '').lower() in ('1', 'true', 'yes') or
            '--debug' in sys.argv or
            '-d' in sys.argv
        )
    
    def debug(self, message: str, *args: Any) -> None:
        """Print debug message if debug mode is enabled."""
        if self.debug_enabled:
            try:
                if args:
                    message = message % args
            except (ValueError, TypeError):
                # If string formatting fails, just use the original message
                pass
            print(f"DEBUG: {message}")
    
    def info(self, message: str, *args: Any) -> None:
        """Print info message if debug mode is enabled."""
        if self.debug_enabled:
            try:
                if args:
                    message = message % args
            except (ValueError, TypeError):
                # If string formatting fails, just use the original message
                pass
            print(f"INFO: {message}")
    
    def error(self, message: str, *args: Any) -> None:
        """Always print error messages."""
        try:
            if args:
                message = message % args
        except (ValueError, TypeError):
            # If string formatting fails, just use the original message
            pass
        print(f"ERROR: {message}")


# Global debug logger instance
logger = DebugLogger()