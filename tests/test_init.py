#!/usr/bin/env python3
"""
Unit tests for the main module initialization.
"""

import pytest
from unittest.mock import patch
from oopsie_daisy import main


class TestMain:
    """Test suite for main module."""
    
    @patch('oopsie_daisy.app.run_app')
    def test_main_function_calls_run_app(self, mock_run_app):
        """Test that main() calls run_app()."""
        main()
        mock_run_app.assert_called_once()
    
    def test_main_function_exists(self):
        """Test that main function is properly defined."""
        assert callable(main)
        assert main.__doc__ is None  # Simple function without docstring