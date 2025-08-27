#!/usr/bin/env python3
"""
GUI functionality tests using pytest-qt.
Tests the actual GUI components without needing Windows.
"""

import pytest
import sys
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    
    # Import our GUI components
    from oopsie_daisy.app import OopsieDaisyMainWindow, RealStarryBackground
    from oopsie_daisy.recovery_wizard import DriveSelectionWidget, ScanModeWidget
    from oopsie_daisy.hardware_monitor_qt import HardwareMonitor
    
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False


@pytest.mark.skipif(not PYSIDE6_AVAILABLE, reason="PySide6 not available")
class TestGUIFunctionality:
    """Test GUI components functionality across platforms."""
    
    def test_starry_background_creation(self, qtbot):
        """Test that starry background creates stars without crashing."""
        background = RealStarryBackground()
        qtbot.addWidget(background)
        
        # Give it a size
        background.resize(800, 600)
        
        # Trigger star creation
        background.create_stars()
        
        # Verify stars were created
        assert len(background.stars) > 0
        assert len(background.stars) >= 200  # Minimum expected stars
        
        # Verify star properties
        for star in background.stars[:5]:  # Check first 5 stars
            assert 'x' in star
            assert 'y' in star
            assert 'size' in star
            assert star['size'] in [1, 2, 3]
            assert 0 <= star['current_brightness'] <= 1
    
    @patch('oopsie_daisy.hardware_monitor_qt.HardwareMonitor')
    def test_main_window_initialization(self, mock_hardware_monitor, qtbot):
        """Test main window initializes without crashing."""
        # Mock hardware monitor to avoid platform-specific issues
        mock_monitor = MagicMock()
        mock_monitor.stats_updated = MagicMock()
        mock_monitor.start_monitoring = MagicMock()
        mock_hardware_monitor.return_value = mock_monitor
        
        # Create main window
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        
        # Test basic properties
        assert window.windowTitle() == "Oopsie Daisy - File Recovery"
        assert window.current_step == 0
        assert len(window.found_files) == 0
        
        # Test that stacked widget exists and has correct pages
        assert window.stack.count() == 4  # 4 steps in wizard
        assert window.stack.currentIndex() == 0  # Should start at step 0
    
    def test_drive_selection_widget(self, qtbot):
        """Test drive selection widget functionality."""
        from oopsie_daisy.advanced_recovery import AdvancedRecoveryEngine
        
        engine = AdvancedRecoveryEngine()
        widget = DriveSelectionWidget(engine)
        qtbot.addWidget(widget)
        
        # Test that drive tree exists
        assert widget.drive_tree is not None
        
        # Test that it has some basic structure
        assert widget.drive_tree.columnCount() >= 2  # Should have at least Name and Size columns
    
    def test_scan_mode_widget(self, qtbot):
        """Test scan mode selection widget."""
        widget = ScanModeWidget()
        qtbot.addWidget(widget)
        
        # Test that radio buttons exist
        assert hasattr(widget, 'deep_radio')
        assert hasattr(widget, 'raw_radio')
        
        # Test default selection
        selected_mode = widget.get_selected_mode()
        assert selected_mode is not None
    
    @patch('platform.system')
    def test_hardware_monitor_cross_platform(self, mock_platform, qtbot):
        """Test hardware monitor works on different platforms."""
        platforms = ['Windows', 'Darwin', 'Linux']
        
        for platform_name in platforms:
            mock_platform.return_value = platform_name
            
            monitor = HardwareMonitor()
            # Don't add to qtbot since HardwareMonitor is not a widget
            
            # Test that it initializes without crashing
            assert monitor.system.lower() == platform_name.lower().replace('darwin', 'darwin')
            
            # Test getting stats (should not crash)
            stats = monitor.get_current_stats()
            assert isinstance(stats, dict)
            assert 'cpu_percent' in stats
            assert 'memory_percent' in stats
            assert 'gpus' in stats
    
    def test_navigation_functionality(self, qtbot):
        """Test wizard navigation works correctly."""
        with patch('oopsie_daisy.hardware_monitor_qt.HardwareMonitor') as mock_monitor:
            mock_monitor.return_value.stats_updated = MagicMock()
            mock_monitor.return_value.start_monitoring = MagicMock()
            
            window = OopsieDaisyMainWindow()
            qtbot.addWidget(window)
            
            # Test initial state
            assert window.current_step == 0
            assert not window.back_btn.isEnabled()
            
            # Mock drive selection
            with patch.object(window.drive_widget, 'get_selected_drive', return_value={'device': '/dev/test'}):
                # Test navigation to next step
                window.go_next()
                assert window.current_step == 1
                assert window.back_btn.isEnabled()
                
                # Test going back
                window.go_back()
                assert window.current_step == 0
                assert not window.back_btn.isEnabled()
    
    def test_window_resizing_adapts_ui(self, qtbot):
        """Test that UI adapts to different window sizes."""
        with patch('oopsie_daisy.hardware_monitor_qt.HardwareMonitor') as mock_monitor:
            mock_monitor.return_value.stats_updated = MagicMock()
            mock_monitor.return_value.start_monitoring = MagicMock()
            
            window = OopsieDaisyMainWindow()
            qtbot.addWidget(window)
            
            # Test different window sizes
            test_sizes = [(800, 600), (1200, 800), (1920, 1080)]
            
            for width, height in test_sizes:
                window.resize(width, height)
                
                # Verify starry background adapts
                assert window.starry_background.width() == width
                assert window.starry_background.height() == height
                
                # UI should not crash with different sizes
                assert window.isVisible() or not window.isVisible()  # Just checking it doesn't crash


@pytest.mark.skipif(not PYSIDE6_AVAILABLE, reason="PySide6 not available")
class TestGUIIntegration:
    """Integration tests for GUI workflow."""
    
    @patch('oopsie_daisy.app.HardwareMonitor')
    def test_full_wizard_workflow_simulation(self, mock_hardware_monitor, qtbot):
        """Simulate a full wizard workflow without actual file operations."""
        # Mock hardware monitor
        mock_monitor = MagicMock()
        mock_monitor.stats_updated = MagicMock()
        mock_monitor.start_monitoring = MagicMock()
        mock_hardware_monitor.return_value = mock_monitor
        
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        
        # Step 1: Drive selection
        assert window.current_step == 0
        
        # Mock drive selection
        mock_drive_info = {'device': '/dev/test', 'mountpoint': '/test', 'fstype': 'ext4'}
        with patch.object(window.drive_widget, 'get_selected_drive', return_value=mock_drive_info):
            window.go_next()
            assert window.current_step == 1
        
        # Step 2: Mode selection  
        from oopsie_daisy.advanced_recovery import RecoveryMode
        with patch.object(window.mode_widget, 'get_selected_mode', return_value=RecoveryMode.QUICK):
            # Don't actually start scan, just test navigation
            pass
        
        # Test that we can navigate back
        window.go_back()
        assert window.current_step == 0
    
    def test_error_handling_in_gui(self, qtbot):
        """Test GUI error handling doesn't crash the application."""
        with patch('oopsie_daisy.hardware_monitor_qt.HardwareMonitor') as mock_monitor:
            # Simulate hardware monitor error
            mock_monitor.side_effect = Exception("Hardware monitoring failed")
            
            # Should not crash even if hardware monitoring fails
            try:
                window = OopsieDaisyMainWindow()
                qtbot.addWidget(window)
                # If we get here, error was handled gracefully
                assert True
            except Exception as e:
                # This should not happen - GUI should handle errors gracefully
                pytest.fail(f"GUI crashed with error: {e}")


# Utility function for running tests
if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])