import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
import sys


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for testing."""
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    yield app
    app.quit()


@pytest.fixture
def qtbot(qtbot):
    """Enhanced qtbot fixture with additional helpers."""
    return qtbot


@pytest.fixture
def mock_recovery_engine():
    """Mock file recovery engine for testing."""
    class MockFileRecoveryEngine:
        def __init__(self):
            self.mock_files = [
                {
                    'name': 'test_document.txt',
                    'path': '/tmp/test_document.txt',
                    'size': 1024,
                    'date_deleted': '2024-01-15 14:30:00'
                },
                {
                    'name': 'important_photo.jpg',
                    'path': '/tmp/important_photo.jpg', 
                    'size': 2048576,
                    'date_deleted': '2024-01-14 09:15:00'
                }
            ]
            
        def scan_for_deleted_files(self):
            return self.mock_files
            
        def restore_file(self, file_info, restore_path):
            return True
            
    return MockFileRecoveryEngine()