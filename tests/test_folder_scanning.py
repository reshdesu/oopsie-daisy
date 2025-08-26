#!/usr/bin/env python3
"""
Tests for folder-specific scanning functionality.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog

from src.oopsie_daisy.app import OopsieDaisyMainWindow, AcceleratedScanThread


class TestFolderScanning:
    """Test folder-specific scanning functionality."""
    
    @pytest.fixture
    def test_folder_structure(self):
        """Create a complex folder structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create main directory files
            (temp_path / "document.txt").write_text("Main document")
            (temp_path / "image.jpg").write_text("Image data")
            (temp_path / "temp_file.tmp").write_text("Temp content")
            (temp_path / ".hidden").write_text("Hidden file")
            
            # Create subdirectories
            sub1 = temp_path / "subfolder1"
            sub1.mkdir()
            (sub1 / "nested_doc.pdf").write_text("Nested document")
            (sub1 / "backup~").write_text("Backup file")
            
            sub2 = temp_path / "subfolder2"
            sub2.mkdir()
            (sub2 / "cache.tmp").write_text("Cache file")
            (sub2 / ".config").write_text("Config file")
            
            # Deep nesting
            deep = sub1 / "deep" / "nested"
            deep.mkdir(parents=True)
            (deep / "deep_file.txt").write_text("Deep nested file")
            
            yield temp_path
    
    @pytest.fixture
    def app_window(self, qtbot):
        """Create app window for UI testing."""
        window = OopsieDaisyMainWindow()
        qtbot.addWidget(window)
        return window
    
    def test_folder_scan_button_exists(self, app_window):
        """Test that folder scan button exists and is properly configured."""
        assert hasattr(app_window, 'folder_scan_button')
        assert app_window.folder_scan_button.text() == "Scan Folder"
        assert app_window.folder_scan_button.isEnabled()
        assert app_window.folder_scan_button.toolTip() == "Choose a specific folder to scan for deleted files"
    
    @patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory')
    def test_folder_scan_dialog_cancelled(self, mock_dialog, app_window, qtbot):
        """Test folder scan when user cancels dialog."""
        # Mock user cancelling dialog
        mock_dialog.return_value = ""
        
        # Click folder scan button
        qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
        
        # Should not start scan
        assert mock_dialog.called
        assert app_window.folder_scan_button.isEnabled()
        assert not hasattr(app_window, 'recovery_thread') or app_window.recovery_thread is None
    
    @patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory')
    def test_folder_scan_dialog_success(self, mock_dialog, app_window, qtbot, test_folder_structure):
        """Test folder scan when user selects a folder."""
        # Mock user selecting folder
        mock_dialog.return_value = str(test_folder_structure)
        
        # Click folder scan button
        qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
        
        # Should start accelerated scan
        assert mock_dialog.called
        assert not app_window.folder_scan_button.isEnabled()
        assert not app_window.scan_button.isEnabled()
        assert app_window.progress_bar.isVisible()
        assert "Deep scanning" in app_window.progress_label.text()
    
    def test_accelerated_scan_thread_creation(self, test_folder_structure):
        """Test AcceleratedScanThread initialization."""
        thread = AcceleratedScanThread(str(test_folder_structure))
        
        assert thread.folder_path == test_folder_structure
        assert hasattr(thread, 'scanner')
        assert hasattr(thread.scanner, 'scan_folder_deep')
    
    @patch('src.oopsie_daisy.app.get_optimal_scanner')
    def test_accelerated_scan_thread_execution(self, mock_scanner, test_folder_structure, qtbot):
        """Test AcceleratedScanThread execution."""
        # Mock scanner
        mock_scanner_instance = Mock()
        mock_scanner_instance.scan_folder_deep.return_value = [
            {'name': 'test.txt', 'path': '/test/test.txt', 'size': 100, 'score': 0.8},
            {'name': 'temp.tmp', 'path': '/test/temp.tmp', 'size': 50, 'score': 0.3}
        ]
        mock_scanner.return_value = mock_scanner_instance
        
        thread = AcceleratedScanThread(str(test_folder_structure))
        
        # Track signals
        progress_updates = []
        files_found = []
        finished_called = []
        
        thread.progress_updated.connect(progress_updates.append)
        thread.files_found.connect(files_found.append)
        thread.finished.connect(lambda: finished_called.append(True))
        
        # Run thread
        thread.run()
        
        # Verify results
        assert len(files_found) == 1
        assert len(files_found[0]) == 2
        assert files_found[0][0]['name'] == 'test.txt'
        assert len(finished_called) == 1
        
        # Verify scanner was called correctly
        mock_scanner_instance.scan_folder_deep.assert_called_once()
        call_args = mock_scanner_instance.scan_folder_deep.call_args
        assert call_args[0][0] == test_folder_structure
        assert callable(call_args[1]['progress_callback'])
    
    def test_accelerated_scan_thread_error_handling(self, qtbot):
        """Test AcceleratedScanThread error handling."""
        # Use non-existent path
        thread = AcceleratedScanThread("/nonexistent/path")
        
        files_found = []
        finished_called = []
        
        thread.files_found.connect(files_found.append)
        thread.finished.connect(lambda: finished_called.append(True))
        
        # Run thread (should handle errors gracefully)
        thread.run()
        
        # Should emit empty results and finish
        assert len(files_found) == 1
        assert files_found[0] == []
        assert len(finished_called) == 1
    
    @patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory')
    def test_folder_scan_progress_updates(self, mock_dialog, app_window, qtbot, test_folder_structure):
        """Test that folder scan shows progress updates."""
        mock_dialog.return_value = str(test_folder_structure)
        
        # Mock the scanner to simulate progress
        with patch('src.oopsie_daisy.app.AcceleratedScanThread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread_class.return_value = mock_thread
            
            # Click folder scan button
            qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
            
            # Verify thread setup
            mock_thread.progress_updated.connect.assert_called_once()
            mock_thread.files_found.connect.assert_called_once()
            mock_thread.finished.connect.assert_called_once()
            mock_thread.start.assert_called_once()
    
    def test_folder_scan_concurrent_prevention(self, app_window, qtbot):
        """Test that concurrent scans are prevented."""
        # Mock running thread
        app_window.recovery_thread = Mock()
        app_window.recovery_thread.isRunning.return_value = True
        
        with patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory') as mock_dialog:
            # Try to start folder scan
            qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
            
            # Dialog should not be called
            assert not mock_dialog.called
    
    @patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory')
    def test_folder_scan_ui_state_management(self, mock_dialog, app_window, qtbot, test_folder_structure):
        """Test UI state changes during folder scan."""
        mock_dialog.return_value = str(test_folder_structure)
        
        # Initial state
        assert app_window.folder_scan_button.isEnabled()
        assert app_window.scan_button.isEnabled()
        assert not app_window.progress_bar.isVisible()
        
        # Start scan
        qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
        
        # During scan state
        assert not app_window.folder_scan_button.isEnabled()
        assert not app_window.scan_button.isEnabled()
        assert app_window.progress_bar.isVisible()
        assert app_window.progress_bar.minimum() == 0
        assert app_window.progress_bar.maximum() == 100  # Determinate progress
        
        # Simulate scan completion
        app_window.on_scan_finished()
        
        # After scan state
        assert app_window.folder_scan_button.isEnabled()
        assert app_window.scan_button.isEnabled()
        assert not app_window.progress_bar.isVisible()
    
    def test_folder_scan_results_display(self, app_window, qtbot):
        """Test that folder scan results are displayed correctly."""
        # Simulate scan completion with results
        mock_files = [
            {'name': 'document.pdf', 'path': '/test/document.pdf', 'size': 1024},
            {'name': 'image.jpg', 'path': '/test/image.jpg', 'size': 2048},
            {'name': 'temp.tmp', 'path': '/test/temp.tmp', 'size': 512}
        ]
        
        app_window.on_files_found(mock_files)
        app_window.on_scan_finished()
        
        # Check UI updates
        assert app_window.files_count_label.text() == "3 files found"
        assert app_window.files_list.count() == 3
        assert app_window.restore_button.isEnabled()
        assert "Select files to restore" in app_window.status_label.text()
    
    def test_folder_scan_no_results(self, app_window, qtbot):
        """Test folder scan when no files are found."""
        # Simulate scan completion with no results
        app_window.on_files_found([])
        app_window.on_scan_finished()
        
        # Check UI updates
        assert app_window.files_count_label.text() == "0 files found"
        assert app_window.files_list.count() == 0
        assert not app_window.restore_button.isEnabled()
        assert "No deleted files found" in app_window.status_label.text()
    
    def test_folder_scan_dialog_parameters(self, app_window, qtbot):
        """Test that folder selection dialog has correct parameters."""
        with patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = ""  # User cancels
            
            qtbot.mouseClick(app_window.folder_scan_button, Qt.LeftButton)
            
            # Check dialog parameters
            mock_dialog.assert_called_once_with(
                app_window,
                "🔍 Choose folder to scan for deleted files",
                str(Path.home())
            )


class TestFolderScanIntegration:
    """Integration tests for folder scanning with real scanner."""
    
    @pytest.fixture
    def realistic_folder(self):
        """Create a realistic folder structure for integration testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create realistic file types
            files = [
                ("important_document.pdf", "PDF document content"),
                ("photo_backup.jpg", "JPEG image data" * 100),
                ("spreadsheet.xlsx", "Excel data"),
                ("presentation.pptx", "PowerPoint content"),
                ("code_backup.py", "print('Hello World')"),
                ("readme.txt", "This is a readme file"),
                ("temp_download.tmp", "Temporary download"),
                ("cache_file.cache", "Application cache"),
                (".DS_Store", "macOS system file"),
                ("~document.docx", "Word backup file"),
            ]
            
            for filename, content in files:
                (temp_path / filename).write_text(content)
            
            # Create nested structure
            downloads = temp_path / "Downloads"
            downloads.mkdir()
            (downloads / "installer.exe").write_text("Installer binary")
            (downloads / "archive.zip").write_text("Compressed archive")
            
            documents = temp_path / "Documents"
            documents.mkdir()
            (documents / "work_file.docx").write_text("Work document")
            (documents / "personal_notes.txt").write_text("Personal notes")
            
            yield temp_path
    
    def test_real_folder_scan_performance(self, realistic_folder):
        """Test folder scanning performance with realistic data."""
        import time
        
        thread = AcceleratedScanThread(str(realistic_folder))
        
        start_time = time.time()
        thread.run()
        scan_time = time.time() - start_time
        
        # Should complete reasonably quickly
        assert scan_time < 5.0  # Less than 5 seconds
    
    def test_real_folder_scan_accuracy(self, realistic_folder):
        """Test that folder scan finds expected files."""
        thread = AcceleratedScanThread(str(realistic_folder))
        
        results = []
        thread.files_found.connect(results.append)
        thread.run()
        
        assert len(results) == 1
        found_files = results[0]
        
        # Should find most files (some may be filtered)
        assert len(found_files) >= 8
        
        # Check that different file types are found
        file_names = [f['name'] for f in found_files]
        assert any('.pdf' in name for name in file_names)
        assert any('.txt' in name for name in file_names)
        assert any('tmp' in name for name in file_names)
        
        # Check that nested files are found
        file_paths = [f['path'] for f in found_files]
        assert any('Downloads' in path for path in file_paths)
        assert any('Documents' in path for path in file_paths)