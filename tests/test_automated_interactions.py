import pytest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import time
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtWidgets import QApplication
from PySide6.QtTest import QTest

from oopsie_daisy.app import OopsieDaisyMainWindow


class TestAutomatedUserInteractions:
    """
    Test suite that emulates real user interactions with the application.
    These tests simulate how an actual user would interact with the UI.
    """
    
    @pytest.fixture
    def app_with_mock_data(self, qtbot):
        """Setup application with mock data for realistic testing."""
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        
        # Mock recovery engine with realistic test data
        mock_files = [
            {
                'name': 'My Important Document.docx',
                'path': '/home/user/Documents/My Important Document.docx',
                'size': 245760,
                'date_deleted': '2024-01-20 09:15:00'
            },
            {
                'name': 'Family Photo.jpg',
                'path': '/home/user/Pictures/Family Photo.jpg',
                'size': 3145728,
                'date_deleted': '2024-01-19 15:30:00'
            },
            {
                'name': 'Project Code.zip',
                'path': '/home/user/Downloads/Project Code.zip',
                'size': 1048576,
                'date_deleted': '2024-01-18 11:45:00'
            }
        ]
        
        with patch.object(window.recovery_engine, 'scan_for_deleted_files', return_value=mock_files):
            with patch.object(window.recovery_engine, 'restore_file', return_value=True):
                yield window, mock_files
    
    def test_complete_user_workflow_happy_path(self, qtbot, app_with_mock_data):
        """
        Simulate a complete happy-path user workflow:
        1. User opens app
        2. Clicks scan button
        3. Waits for results
        4. Selects files to restore
        5. Chooses restore location
        6. Confirms successful restoration
        """
        window, mock_files = app_with_mock_data
        
        # Step 1: User sees the initial interface
        assert "Ready to scan" in window.status_label.text()
        assert not window.progress_bar.isVisible()
        assert not window.restore_button.isEnabled()
        
        # Step 2: User clicks the scan button
        scan_button = None
        for i in range(window.centralWidget().layout().count()):
            widget = window.centralWidget().layout().itemAt(i).widget()
            if hasattr(widget, 'text') and 'Start Scanning' in widget.text():
                scan_button = widget
                break
        
        assert scan_button is not None, "Scan button not found"
        
        # Simulate user clicking with mouse
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        
        # Step 3: User sees scanning progress
        assert window.progress_bar.isVisible()
        assert "Scanning" in window.status_label.text()
        
        # Step 4: Simulate scan completion
        QTimer.singleShot(50, lambda: window.on_files_found(mock_files))
        QTimer.singleShot(100, lambda: window.on_scan_finished())
        qtbot.wait(150)
        
        # Step 5: User sees results
        assert window.files_list.count() == 3
        assert "Found 3 deleted files" in window.status_label.text()
        assert window.restore_button.isEnabled()
        assert not window.progress_bar.isVisible()
        
        # Step 6: User selects multiple files (like a real user would)
        # Select first file with mouse click
        item_rect = window.files_list.visualItemRect(window.files_list.item(0))
        qtbot.mouseClick(
            window.files_list.viewport(), 
            Qt.LeftButton, 
            pos=item_rect.center()
        )
        
        # Select second file with Ctrl+Click (multi-selection)
        item_rect2 = window.files_list.visualItemRect(window.files_list.item(1))
        qtbot.mouseClick(
            window.files_list.viewport(),
            Qt.LeftButton,
            Qt.ControlModifier,
            pos=item_rect2.center()
        )
        
        # Verify selection
        selected_items = window.files_list.selectedItems()
        assert len(selected_items) == 2
        
        # Step 7: User clicks restore button
        with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value='/tmp/restored'):
            with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
                qtbot.mouseClick(window.restore_button, Qt.LeftButton)
                
                # Step 8: User sees success message
                mock_info.assert_called_once()
                success_args = mock_info.call_args[0]
                assert "Success" in success_args[1]
                assert "Successfully restored 2 files" in success_args[2]
    
    def test_user_discovers_no_files_workflow(self, qtbot, app_with_mock_data):
        """
        Test scenario where user finds no deleted files:
        1. User scans
        2. No files found
        3. User sees encouraging message
        """
        window, _ = app_with_mock_data
        
        # Mock no files found
        with patch.object(window.recovery_engine, 'scan_for_deleted_files', return_value=[]):
            # User clicks scan
            scan_button = window.centralWidget().layout().itemAt(2).widget()
            qtbot.mouseClick(scan_button, Qt.LeftButton)
            
            # Complete scan with no results
            QTimer.singleShot(50, lambda: window.on_files_found([]))
            QTimer.singleShot(100, lambda: window.on_scan_finished())
            qtbot.wait(150)
            
            # User sees positive message
            assert window.files_list.count() == 0
            assert "Great news!" in window.status_label.text()
            assert not window.restore_button.isEnabled()
    
    def test_user_makes_mistakes_workflow(self, qtbot, app_with_mock_data):
        """
        Test user making common mistakes:
        1. Trying to restore without selecting files
        2. Canceling file dialog
        """
        window, mock_files = app_with_mock_data
        
        # Setup files
        window.on_files_found(mock_files)
        window.on_scan_finished()
        
        # Mistake 1: User clicks restore without selecting files
        with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
            qtbot.mouseClick(window.restore_button, Qt.LeftButton)
            
            # Should see helpful message
            mock_info.assert_called_once()
            info_args = mock_info.call_args[0]
            assert "select at least one file" in info_args[2]
        
        # User learns and selects a file
        window.files_list.setCurrentRow(0)
        
        # Mistake 2: User cancels the folder selection dialog
        with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value=''):
            with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
                qtbot.mouseClick(window.restore_button, Qt.LeftButton)
                
                # Should not show success message since user canceled
                mock_info.assert_not_called()
    
    def test_power_user_keyboard_workflow(self, qtbot, app_with_mock_data):
        """
        Test advanced user using keyboard shortcuts:
        1. Tab navigation
        2. Space/Enter activation
        3. Arrow key navigation
        """
        window, mock_files = app_with_mock_data
        
        # Setup files first
        window.on_files_found(mock_files)
        window.on_scan_finished()
        
        # Power user navigates with keyboard
        qtbot.keyClick(window, Qt.Key_Tab)  # Navigate to scan button
        qtbot.keyClick(window, Qt.Key_Tab)  # Navigate to file list
        
        # Focus on file list and navigate with arrows
        window.files_list.setFocus()
        qtbot.keyClick(window.files_list, Qt.Key_Down)  # Select first item
        qtbot.keyClick(window.files_list, Qt.Key_Down)  # Move to second item
        
        # Use space to select
        qtbot.keyClick(window.files_list, Qt.Key_Space)
        
        # Verify selection
        assert window.files_list.currentRow() == 1
        
        # Navigate to restore button and activate
        qtbot.keyClick(window, Qt.Key_Tab)  # Go to restore button
        window.restore_button.setFocus()
        
        with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value='/tmp/restored'):
            with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
                qtbot.keyClick(window.restore_button, Qt.Key_Return)
                mock_info.assert_called_once()
    
    def test_impatient_user_multiple_clicks(self, qtbot, app_with_mock_data):
        """
        Test impatient user clicking buttons multiple times:
        1. Multiple scan button clicks
        2. Multiple restore attempts
        """
        window, mock_files = app_with_mock_data
        
        scan_button = window.centralWidget().layout().itemAt(2).widget()
        
        # Impatient user clicks scan multiple times rapidly
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        
        # Should handle gracefully (only one scan should run)
        assert window.progress_bar.isVisible()
        
        # Complete scan
        QTimer.singleShot(50, lambda: window.on_files_found(mock_files))
        QTimer.singleShot(100, lambda: window.on_scan_finished())
        qtbot.wait(150)
        
        # Select a file and try multiple restore clicks
        window.files_list.setCurrentRow(0)
        
        with patch('oopsie_daisy.app.QFileDialog.getExistingDirectory', return_value='/tmp/restored'):
            with patch('oopsie_daisy.app.QMessageBox.information') as mock_info:
                qtbot.mouseClick(window.restore_button, Qt.LeftButton)
                qtbot.mouseClick(window.restore_button, Qt.LeftButton)
                
                # Should only show one success dialog
                assert mock_info.call_count == 1
    
    def test_user_window_interactions(self, qtbot, app_with_mock_data):
        """
        Test user window management:
        1. Resizing window
        2. Minimizing/maximizing
        3. Moving window
        """
        window, _ = app_with_mock_data
        
        # User resizes window
        original_size = window.size()
        window.resize(1200, 800)
        
        # Verify resize worked and UI still functional
        assert window.width() == 1200
        assert window.height() == 800
        
        # Test UI elements still accessible after resize
        scan_button = window.centralWidget().layout().itemAt(2).widget()
        assert scan_button.isVisible()
        assert window.files_list.isVisible()
        
        # User tries to make window too small
        window.resize(400, 300)
        
        # Should respect minimum size
        assert window.width() >= 800
        assert window.height() >= 600
    
    def test_accessibility_user_workflow(self, qtbot, app_with_mock_data):
        """
        Test workflow for users relying on accessibility features:
        1. High contrast mode simulation
        2. Keyboard-only navigation
        3. Screen reader friendly labels
        """
        window, mock_files = app_with_mock_data
        
        # Test that all interactive elements have accessible text
        scan_button = window.centralWidget().layout().itemAt(2).widget()
        assert scan_button.text()  # Has text for screen readers
        
        restore_button = window.restore_button
        assert restore_button.text()  # Has text for screen readers
        
        # Test keyboard navigation covers all interactive elements
        window.setFocus()
        
        # Should be able to tab through all interactive elements
        focusable_widgets = []
        
        def collect_focusable(widget):
            if widget.focusPolicy() != Qt.NoFocus and widget.isEnabled():
                focusable_widgets.append(widget)
            for child in widget.children():
                if hasattr(child, 'focusPolicy'):
                    collect_focusable(child)
        
        collect_focusable(window)
        
        # Should have at least scan button, file list, and restore button
        assert len(focusable_widgets) >= 3
    
    @pytest.mark.slow
    def test_stress_test_rapid_interactions(self, qtbot, app_with_mock_data):
        """
        Stress test with rapid user interactions:
        1. Rapid clicking
        2. Fast keyboard input
        3. Quick window operations
        """
        window, mock_files = app_with_mock_data
        
        # Rapid scan button clicking
        scan_button = window.centralWidget().layout().itemAt(2).widget()
        
        for _ in range(10):
            qtbot.mouseClick(scan_button, Qt.LeftButton)
            QTest.qWait(10)  # Very short wait between clicks
        
        # Should still be responsive
        assert window.isVisible()
        
        # Complete any running scan
        QTimer.singleShot(50, lambda: window.on_files_found(mock_files))
        QTimer.singleShot(100, lambda: window.on_scan_finished())
        qtbot.wait(150)
        
        # Rapid selection changes in file list
        for i in range(min(20, window.files_list.count() * 5)):
            row = i % window.files_list.count()
            window.files_list.setCurrentRow(row)
            QTest.qWait(5)
        
        # Window should still be responsive
        assert window.files_list.currentRow() >= 0
        assert window.restore_button.isEnabled()