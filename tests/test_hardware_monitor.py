#!/usr/bin/env python3
"""
Unit tests for the hardware monitoring functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from oopsie_daisy.hardware_monitor_qt import HardwareMonitor


class TestHardwareMonitor:
    """Test suite for HardwareMonitor class."""
    
    def test_initialization(self):
        """Test HardwareMonitor initializes correctly."""
        monitor = HardwareMonitor()
        
        assert monitor.system is not None
        assert monitor.current_stats is not None
        assert 'cpu_percent' in monitor.current_stats
        assert 'gpu_percent' in monitor.current_stats
        assert 'memory_percent' in monitor.current_stats
        assert isinstance(monitor.current_stats['gpus'], list)
    
    def test_get_current_stats(self):
        """Test getting current hardware statistics."""
        monitor = HardwareMonitor()
        stats = monitor.get_current_stats()
        
        assert isinstance(stats, dict)
        assert 'cpu_percent' in stats
        assert 'memory_percent' in stats
        assert 'gpus' in stats
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_update_stats_with_psutil(self, mock_memory, mock_cpu):
        """Test stats update with psutil available."""
        # Mock psutil responses
        mock_cpu.return_value = 45.5
        mock_memory.return_value = MagicMock(percent=67.2)
        
        monitor = HardwareMonitor()
        monitor._update_stats()
        
        stats = monitor.get_current_stats()
        assert stats['cpu_percent'] == 45.5
        assert stats['memory_percent'] == 67.2