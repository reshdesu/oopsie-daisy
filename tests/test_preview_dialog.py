#!/usr/bin/env python3
"""
Unit tests for the file preview dialog functionality.
"""

import pytest
from unittest.mock import MagicMock, patch
from oopsie_daisy.recovery_wizard import MultiFilePreviewDialog, RecoveredFile


@pytest.fixture
def sample_recovered_file():
    """Create a sample RecoveredFile for testing."""
    file_info = MagicMock(spec=RecoveredFile)
    file_info.name = "test_document.txt"
    file_info.path = "/tmp/test_document.txt"
    file_info.size = 1024
    file_info.file_type = "txt"
    file_info.quality = 0.95
    file_info.recoverable = True
    file_info.signature = None
    file_info.created_time = None
    file_info.modified_time = None
    return file_info


class TestMultiFilePreviewDialog:
    """Test suite for MultiFilePreviewDialog class."""
    
    @pytest.mark.ui
    def test_file_icon_mapping(self, sample_recovered_file, qapp):
        """Test file type to icon mapping."""
        with patch.object(MultiFilePreviewDialog, 'setup_ui'):
            dialog = MultiFilePreviewDialog([sample_recovered_file])
            
            # Test common file types
            assert dialog._get_file_icon('txt') == '📝'
            assert dialog._get_file_icon('jpg') == '🖼️'
            assert dialog._get_file_icon('mp3') == '🎵'
            assert dialog._get_file_icon('zip') == '📦'
            assert dialog._get_file_icon('unknown') == '📄'  # default
    
    def test_format_file_size(self, sample_recovered_file):
        """Test file size formatting."""
        dialog = MultiFilePreviewDialog([sample_recovered_file])
        
        assert dialog._format_file_size(512) == "512 bytes"
        assert dialog._format_file_size(1024) == "1.0 KB"
        assert dialog._format_file_size(1024 * 1024) == "1.0 MB"
        assert dialog._format_file_size(1024 * 1024 * 1024) == "1.0 GB"
    
    def test_has_preview_content(self, sample_recovered_file):
        """Test preview content availability check."""
        dialog = MultiFilePreviewDialog([sample_recovered_file])
        
        # Most files should have some form of preview
        assert dialog._has_preview_content(sample_recovered_file) == True
    
    def test_single_file_dialog(self, sample_recovered_file):
        """Test dialog initialization with single file."""
        dialog = MultiFilePreviewDialog([sample_recovered_file])
        
        assert len(dialog.files) == 1
        assert dialog.files[0] == sample_recovered_file
        assert "test_document.txt" in dialog.windowTitle()
    
    def test_multiple_files_dialog(self, sample_recovered_file):
        """Test dialog initialization with multiple files."""
        file2 = MagicMock(spec=RecoveredFile)
        file2.name = "image.jpg"
        file2.size = 2048
        file2.file_type = "jpg"
        file2.quality = 0.8
        file2.recoverable = True
        
        dialog = MultiFilePreviewDialog([sample_recovered_file, file2])
        
        assert len(dialog.files) == 2
        assert "2 Selected Files" in dialog.windowTitle()