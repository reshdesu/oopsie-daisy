import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtTest import QTest

from oopsie_daisy.app import OopsieDaisyMainWindow, FileRecoveryThread


class TestIntegrationWorkflows:
    """Integration tests that simulate complete user workflows."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def app_window(self, qtbot):
        """Create application window with real components."""
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_complete_scan_and_restore_workflow(self, qtbot, app_window, temp_dir):
        """Test the complete workflow from scan to restore."""
        # Mock the recovery engine to return test files
        mock_files = [
            {
                'name': 'lost_document.txt',
                'path': os.path.join(temp_dir, 'lost_document.txt'),
                'size': 512,
                'date_deleted': '2024-01-15 10:30:00'
            }
        ]
        
        with patch.object(app_window.recovery_engine, 'scan_for_deleted_files', return_value=mock_files):
            with patch.object(app_window.recovery_engine, 'restore_file', return_value=True):
                # Step 1: Start scan
                scan_button = app_window.centralWidget().layout().itemAt(2).widget()
                qtbot.mouseClick(scan_button, Qt.LeftButton)
                
                # Wait for scan to complete
                qtbot.wait(100)
                
                # Step 2: Verify files are found
                app_window.on_files_found(mock_files)
                app_window.on_scan_finished()
                
                assert app_window.files_list.count() == 1
                assert app_window.restore_button.isEnabled()
                
                # Step 3: Select file and restore
                app_window.files_list.setCurrentRow(0)
                
                with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value=temp_dir):
                    with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
                        qtbot.mouseClick(app_window.restore_button, Qt.LeftButton)
                        
                        # Verify success message shown
                        mock_info.assert_called_once()
                        args = mock_info.call_args[0]
                        assert "Success" in args[1]
    
    def test_scan_with_no_files_found(self, qtbot, app_window):
        """Test workflow when no deleted files are found."""
        with patch.object(app_window.recovery_engine, 'scan_for_deleted_files', return_value=[]):
            # Start scan
            scan_button = app_window.centralWidget().layout().itemAt(2).widget()
            qtbot.mouseClick(scan_button, Qt.LeftButton)
            
            # Complete scan
            app_window.on_files_found([])
            app_window.on_scan_finished()
            
            # Verify UI state
            assert app_window.files_list.count() == 0
            assert not app_window.restore_button.isEnabled()
            assert "Great news!" in app_window.status_label.text()
    
    def test_scan_thread_integration(self, qtbot, app_window):
        """Test the file recovery thread integration."""
        mock_files = [{'name': 'test.txt', 'size': 100}]
        
        with patch.object(app_window.recovery_engine, 'scan_for_deleted_files', return_value=mock_files):
            # Create and start thread
            thread = FileRecoveryThread(app_window.recovery_engine)
            
            # Connect signals for testing
            files_received = []
            finished_called = False
            
            def on_files_found(files):
                nonlocal files_received
                files_received = files
                
            def on_finished():
                nonlocal finished_called
                finished_called = True
            
            thread.files_found.connect(on_files_found)
            thread.finished.connect(on_finished)
            
            # Start thread and wait for completion
            thread.start()
            thread.wait(1000)  # Wait up to 1 second
            
            # Verify results
            assert files_received == mock_files
            assert finished_called
    
    def test_error_handling_during_restore(self, qtbot, app_window, temp_dir):
        """Test error handling when file restoration fails."""
        mock_files = [{'name': 'corrupted_file.txt', 'size': 1024}]
        
        # Mock restore to raise an exception
        with patch.object(app_window.recovery_engine, 'restore_file', side_effect=Exception("Restore failed")):
            # Setup files
            app_window.on_files_found(mock_files)
            app_window.on_scan_finished()
            app_window.files_list.setCurrentRow(0)
            
            # Attempt restore
            with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value=temp_dir):
                with patch('oopsie_daisy.app.QMessageBox.warning') as mock_warning:
                    qtbot.mouseClick(app_window.restore_button, Qt.LeftButton)
                    
                    # Verify error message shown
                    mock_warning.assert_called_once()
                    args = mock_warning.call_args[0]
                    assert "Restore Error" in args[1]
    
    def test_multiple_scan_operations(self, qtbot, app_window):
        """Test running multiple scan operations."""
        with patch.object(app_window.recovery_engine, 'scan_for_deleted_files', return_value=[]):
            scan_button = app_window.centralWidget().layout().itemAt(2).widget()
            
            # First scan
            qtbot.mouseClick(scan_button, Qt.LeftButton)
            app_window.on_scan_finished()
            
            # Second scan should work
            qtbot.mouseClick(scan_button, Qt.LeftButton)
            app_window.on_scan_finished()
            
            # Verify no issues
            assert "Ready to scan" in app_window.status_label.text() or "Great news" in app_window.status_label.text()


class TestUIStateManagement:
    """Test UI state changes and consistency."""
    
    @pytest.fixture
    def window(self, qtbot):
        """Create a window for state testing."""
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_button_states_during_scan(self, window):
        """Test button enable/disable states during scan."""
        scan_button = window.centralWidget().layout().itemAt(2).widget()
        
        # Initial state
        assert scan_button.isEnabled()
        assert not window.restore_button.isEnabled()
        
        # During scan (simulate)
        window.start_scan()
        # Note: In real scenario, scan button might be disabled during scan
        
        # After scan with files
        mock_files = [{'name': 'test.txt', 'size': 100}]
        window.on_files_found(mock_files)
        window.on_scan_finished()
        
        assert window.restore_button.isEnabled()
    
    def test_progress_bar_states(self, window):
        """Test progress bar state changes."""
        # Initially hidden
        assert not window.progress_bar.isVisible()
        
        # Start scan
        window.start_scan()
        assert window.progress_bar.isVisible()
        
        # Finish scan
        window.on_scan_finished()
        assert not window.progress_bar.isVisible()
    
    def test_status_label_updates(self, window):
        """Test status label updates throughout workflow."""
        initial_text = window.status_label.text()
        assert "Ready to scan" in initial_text
        
        # Start scan
        window.start_scan()
        scan_text = window.status_label.text()
        assert "Scanning" in scan_text
        
        # Finish with files
        mock_files = [{'name': 'test.txt', 'size': 100}]
        window.found_files = mock_files
        window.on_scan_finished()
        
        finished_text = window.status_label.text()
        assert "Found 1 deleted files" in finished_text


class TestAccessibilityAndUsability:
    """Test accessibility and usability features."""
    
    def test_keyboard_shortcuts(self, qtbot, app_window):
        """Test keyboard accessibility."""
        # Tab navigation should work
        qtbot.keyClick(app_window, Qt.Key_Tab)
        
        # Enter key on focused button should trigger click
        scan_button = app_window.centralWidget().layout().itemAt(2).widget()
        scan_button.setFocus()
        
        with patch.object(app_window, 'start_scan') as mock_scan:
            qtbot.keyClick(scan_button, Qt.Key_Return)
            mock_scan.assert_called_once()
    
    def test_window_minimum_size(self, app_window):
        """Test minimum window size constraints."""
        app_window.resize(100, 100)  # Try to make very small
        
        # Should respect minimum size
        assert app_window.width() >= 800
        assert app_window.height() >= 600
    
    def test_text_readability(self, app_window):
        """Test that text elements are readable."""
        # Check that important text elements exist
        title_found = False
        status_found = False
        
        def check_widget_text(widget):
            nonlocal title_found, status_found
            if hasattr(widget, 'text'):
                text = widget.text()
                if "Oopsie Daisy" in text:
                    title_found = True
                if "Ready to scan" in text:
                    status_found = True
        
        # Recursively check all widgets
        def check_all_children(widget):
            check_widget_text(widget)
            for child in widget.findChildren(object):
                check_widget_text(child)
        
        check_all_children(app_window)
        
        assert title_found
        assert status_found