import pytest
from unittest.mock import Mock, patch
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMessageBox
from PySide6.QtTest import QTest

from oopsie_daisy.app import OopsieDaisyMainWindow


class TestOopsieDaisyUI:
    """Test suite for the main UI functionality."""
    
    @pytest.fixture
    def main_window(self, qtbot, mock_recovery_engine):
        """Create a main window instance for testing."""
        with patch('oopsie_daisy.app.FileRecoveryEngine', return_value=mock_recovery_engine):
            window = OopsieDaisyMainWindow()
            qtbot.addWidget(window)
            return window
    
    def test_window_initialization(self, main_window):
        """Test that the main window initializes properly."""
        assert main_window.windowTitle() == "🐱 Oopsie Daisy - File Recovery Tool"
        assert main_window.width() >= 800
        assert main_window.height() >= 600
        
    def test_initial_ui_state(self, main_window):
        """Test the initial state of UI elements."""
        assert not main_window.progress_bar.isVisible()
        assert not main_window.restore_button.isEnabled()
        assert main_window.status_label.text() == "Ready to scan! Click the button above to start. 🌟"
        assert main_window.files_list.count() == 0
        
    def test_scan_button_click(self, qtbot, main_window):
        """Test clicking the scan button."""
        scan_button = main_window.findChild(object, name="scan_button") or main_window.centralWidget().layout().itemAt(2).widget()
        
        # Click the scan button
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        
        # Check that progress bar becomes visible
        assert main_window.progress_bar.isVisible()
        assert "Scanning" in main_window.status_label.text()
        
    def test_file_scanning_workflow(self, qtbot, main_window, mock_recovery_engine):
        """Test the complete file scanning workflow."""
        # Start scan
        scan_button = main_window.centralWidget().layout().itemAt(2).widget()
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        
        # Wait for the thread to finish (simulate)
        QTimer.singleShot(100, lambda: main_window.on_files_found(mock_recovery_engine.mock_files))
        QTimer.singleShot(200, lambda: main_window.on_scan_finished())
        
        # Process events to handle the signals
        qtbot.wait(300)
        
        # Check results
        assert main_window.files_list.count() == 2
        assert main_window.restore_button.isEnabled()
        assert "Found 2 deleted files" in main_window.status_label.text()
        
    def test_file_list_population(self, main_window, mock_recovery_engine):
        """Test that files are properly added to the list."""
        main_window.on_files_found(mock_recovery_engine.mock_files)
        
        assert main_window.files_list.count() == 2
        
        # Check first item
        item1 = main_window.files_list.item(0)
        assert "test_document.txt" in item1.text()
        assert "1024 bytes" in item1.text()
        
        # Check second item  
        item2 = main_window.files_list.item(1)
        assert "important_photo.jpg" in item2.text()
        assert "2048576 bytes" in item2.text()
        
    def test_file_selection(self, qtbot, main_window, mock_recovery_engine):
        """Test file selection in the list."""
        # Populate the list
        main_window.on_files_found(mock_recovery_engine.mock_files)
        
        # Select first item
        main_window.files_list.setCurrentRow(0)
        selected_items = main_window.files_list.selectedItems()
        
        assert len(selected_items) == 1
        assert "test_document.txt" in selected_items[0].text()
        
    @patch('oopsie_daisy.app.QMessageBox')
    def test_restore_without_selection(self, mock_msgbox, qtbot, main_window, mock_recovery_engine):
        """Test restore button click without selecting files."""
        # Populate files but don't select any
        main_window.on_files_found(mock_recovery_engine.mock_files)
        main_window.on_scan_finished()
        
        # Click restore button
        qtbot.mouseClick(main_window.restore_button, Qt.LeftButton)
        
        # Should show information message
        mock_msgbox.information.assert_called_once()
        
    @patch('oopsie_daisy.app.QFileDialog')
    @patch('oopsie_daisy.app.QMessageBox')
    def test_successful_restore(self, mock_msgbox, mock_filedialog, qtbot, main_window, mock_recovery_engine):
        """Test successful file restoration."""
        # Setup
        mock_filedialog.getExistingDirectory.return_value = "/tmp/restore"
        
        # Populate and select files
        main_window.on_files_found(mock_recovery_engine.mock_files)
        main_window.on_scan_finished()
        main_window.files_list.setCurrentRow(0)
        
        # Click restore button
        qtbot.mouseClick(main_window.restore_button, Qt.LeftButton)
        
        # Should show success message
        mock_msgbox.information.assert_called_once()
        args = mock_msgbox.information.call_args[0]
        assert "Success" in args[1]
        assert "Successfully restored 1 files" in args[2]
        
    def test_kitten_theme_applied(self, main_window):
        """Test that the kitten theme styles are applied."""
        stylesheet = main_window.styleSheet()
        
        # Check for pink colors in stylesheet
        assert "#FF69B4" in stylesheet  # Hot pink
        assert "#FFB6C1" in stylesheet  # Light pink
        assert "#FFF0F5" in stylesheet  # Lavender blush
        
    def test_window_responsiveness(self, qtbot, main_window):
        """Test window resizing and responsiveness."""
        # Test minimum size
        main_window.resize(800, 600)
        assert main_window.width() >= 800
        assert main_window.height() >= 600
        
        # Test larger size
        main_window.resize(1200, 900)
        assert main_window.width() == 1200
        assert main_window.height() == 900


class TestUIInteractions:
    """Test suite for advanced UI interactions."""
    
    @pytest.fixture
    def window_with_files(self, qtbot, mock_recovery_engine):
        """Create a window with files already loaded."""
        with patch('oopsie_daisy.app.FileRecoveryEngine', return_value=mock_recovery_engine):
            window = OopsieDaisyMainWindow()
            qtbot.addWidget(window)
            window.on_files_found(mock_recovery_engine.mock_files)
            window.on_scan_finished()
            return window
    
    def test_multiple_file_selection(self, qtbot, window_with_files):
        """Test selecting multiple files."""
        # Select first file
        window_with_files.files_list.setCurrentRow(0)
        
        # Add second file to selection (Ctrl+Click simulation)
        item1 = window_with_files.files_list.item(1)
        window_with_files.files_list.setItemSelected(item1, True)
        
        selected = window_with_files.files_list.selectedItems()
        assert len(selected) == 2
        
    def test_keyboard_navigation(self, qtbot, window_with_files):
        """Test keyboard navigation in the file list."""
        # Focus on the list
        window_with_files.files_list.setFocus()
        
        # Use arrow keys to navigate
        qtbot.keyClick(window_with_files.files_list, Qt.Key_Down)
        assert window_with_files.files_list.currentRow() == 0
        
        qtbot.keyClick(window_with_files.files_list, Qt.Key_Down)
        assert window_with_files.files_list.currentRow() == 1
        
    def test_progress_bar_behavior(self, qtbot, main_window):
        """Test progress bar visibility and behavior."""
        # Initially hidden
        assert not main_window.progress_bar.isVisible()
        
        # Start scan - should become visible
        scan_button = main_window.centralWidget().layout().itemAt(2).widget()
        qtbot.mouseClick(scan_button, Qt.LeftButton)
        
        assert main_window.progress_bar.isVisible()
        
        # Finish scan - should be hidden again
        main_window.on_scan_finished()
        assert not main_window.progress_bar.isVisible()


@pytest.mark.parametrize("file_count,expected_message", [
    (0, "Great news! No recently deleted files found"),
    (1, "Found 1 deleted files"),
    (5, "Found 5 deleted files"),
])
def test_status_messages(main_window, file_count, expected_message):
    """Test different status messages based on file count."""
    mock_files = [{'name': f'file{i}.txt', 'size': 1024} for i in range(file_count)]
    main_window.found_files = mock_files
    main_window.on_scan_finished()
    
    assert expected_message in main_window.status_label.text()