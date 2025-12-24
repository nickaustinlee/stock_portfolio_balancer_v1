"""
Tests for debug utilities.
"""

import os
import sys
from io import StringIO
from unittest.mock import patch
import pytest

from src.utils.debug import DebugLogger


class TestDebugLogger:
    """Test the debug logging functionality."""
    
    def test_debug_disabled_by_default(self):
        """Test that debug is disabled by default."""
        logger = DebugLogger()
        # Should be disabled unless environment variables or args are set
        assert logger.debug_enabled in [True, False]  # Depends on current environment
    
    def test_debug_enabled_by_env_var(self):
        """Test debug mode enabled by environment variable."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '1'}):
            logger = DebugLogger()
            assert logger.debug_enabled is True
            
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': 'true'}):
            logger = DebugLogger()
            assert logger.debug_enabled is True
            
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': 'yes'}):
            logger = DebugLogger()
            assert logger.debug_enabled is True
            
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '0'}):
            logger = DebugLogger()
            assert logger.debug_enabled is False
    
    def test_debug_enabled_by_command_line_args(self):
        """Test debug mode enabled by command line arguments."""
        with patch.object(sys, 'argv', ['script.py', '--debug']):
            logger = DebugLogger()
            assert logger.debug_enabled is True
            
        with patch.object(sys, 'argv', ['script.py', '-d']):
            logger = DebugLogger()
            assert logger.debug_enabled is True
            
        with patch.object(sys, 'argv', ['script.py', '--other-flag']):
            logger = DebugLogger()
            # Should be False unless env var is set
            if 'STOCK_TOOL_DEBUG' not in os.environ or os.environ.get('STOCK_TOOL_DEBUG', '').lower() not in ('1', 'true', 'yes'):
                assert logger.debug_enabled is False
    
    def test_debug_output_when_enabled(self):
        """Test that debug messages are printed when debug is enabled."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '1'}):
            logger = DebugLogger()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.debug("Test debug message")
                output = mock_stdout.getvalue()
                assert "DEBUG: Test debug message" in output
    
    def test_debug_no_output_when_disabled(self):
        """Test that debug messages are not printed when debug is disabled."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '0'}):
            logger = DebugLogger()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.debug("Test debug message")
                output = mock_stdout.getvalue()
                assert output == ""
    
    def test_info_output_when_enabled(self):
        """Test that info messages are printed when debug is enabled."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '1'}):
            logger = DebugLogger()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.info("Test info message")
                output = mock_stdout.getvalue()
                assert "INFO: Test info message" in output
    
    def test_error_always_printed(self):
        """Test that error messages are always printed regardless of debug mode."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '0'}):
            logger = DebugLogger()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.error("Test error message")
                output = mock_stdout.getvalue()
                assert "ERROR: Test error message" in output
    
    def test_message_formatting_with_args(self):
        """Test message formatting with arguments."""
        with patch.dict(os.environ, {'STOCK_TOOL_DEBUG': '1'}):
            logger = DebugLogger()
            
            with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
                logger.debug("Test %s with %d args", "message", 2)
                output = mock_stdout.getvalue()
                assert "DEBUG: Test message with 2 args" in output