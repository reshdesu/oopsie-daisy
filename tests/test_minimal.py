#!/usr/bin/env python3
"""
Minimal tests that work reliably in CI/CD without Qt dependencies.
"""

import pytest
import platform
from unittest.mock import patch, MagicMock


def test_python_version():
    """Test that we're running on Python 3.12+."""
    import sys
    assert sys.version_info >= (3, 12), f"Expected Python 3.12+, got {sys.version_info}"


def test_platform_detection():
    """Test basic platform detection."""
    system = platform.system().lower()
    assert system in ['linux', 'windows', 'darwin'], f"Unexpected platform: {system}"


def test_imports():
    """Test that our main modules can be imported."""
    # Test core imports
    import oopsie_daisy
    assert callable(oopsie_daisy.main)
    
    # Test hardware monitor import
    from oopsie_daisy.hardware_monitor_qt import HardwareMonitor
    assert HardwareMonitor is not None
    
    # Test recovery engine import  
    from oopsie_daisy.advanced_recovery import AdvancedRecoveryEngine
    assert AdvancedRecoveryEngine is not None


@patch('platform.system')
def test_hardware_monitor_platform_detection(mock_platform):
    """Test hardware monitor detects platform correctly."""
    # Test Linux detection
    mock_platform.return_value = 'Linux'
    from oopsie_daisy.hardware_monitor_qt import HardwareMonitor
    
    monitor = HardwareMonitor()
    assert monitor.system == 'linux'
    
    # Test Windows detection
    mock_platform.return_value = 'Windows'
    monitor2 = HardwareMonitor()
    assert monitor2.system == 'windows'
    
    # Test macOS detection
    mock_platform.return_value = 'Darwin'
    monitor3 = HardwareMonitor()
    assert monitor3.system == 'darwin'


def test_basic_functionality():
    """Test that basic functionality works without UI."""
    from oopsie_daisy.hardware_monitor_qt import HardwareMonitor
    
    monitor = HardwareMonitor()
    stats = monitor.get_current_stats()
    
    # Should have basic stats structure
    assert isinstance(stats, dict)
    assert 'cpu_percent' in stats
    assert 'memory_percent' in stats
    assert 'gpus' in stats
    assert isinstance(stats['gpus'], list)