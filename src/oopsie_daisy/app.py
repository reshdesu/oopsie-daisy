import sys
import os
import platform
import subprocess
from pathlib import Path
from typing import List, Optional
import random
import math

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QLabel, QListWidget, QListWidgetItem, QProgressBar,
    QMessageBox, QFrame, QScrollArea, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsEllipseItem, QGraphicsOpacityEffect
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QBrush, QPen, QPainter

from .file_recovery import FileRecoveryEngine
from .styles import get_kitten_style
from .accelerated_scanner import get_optimal_scanner


class RealStarryBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.stars = []
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_stars)
        self.animation_timer.start(50)  # Update every 50ms for smooth twinkling
        
        # Create stars when widget is first shown
        QTimer.singleShot(100, self.create_initial_stars)
    
    def create_initial_stars(self):
        """Create initial stars covering the entire widget"""
        self.create_stars()
        self.update()
    
    def create_stars(self):
        """Create realistic twinkling stars across the entire area"""
        self.stars = []
        width = max(1200, self.width())
        height = max(800, self.height())
        
        # Create 500 stars for richer coverage
        for _ in range(500):
            star = {
                'x': random.randint(0, width),
                'y': random.randint(0, height),
                'size': random.choice([1, 1, 2, 2, 3]),  # Mostly small stars
                'base_brightness': random.uniform(0.3, 0.9),
                'current_brightness': random.uniform(0.3, 0.9),
                'twinkle_speed': random.uniform(0.02, 0.08),
                'twinkle_phase': random.uniform(0, 6.28),  # Random phase
                'color_type': random.choice(['white', 'white', 'white', 'pink', 'blue']),
                'flash_timer': random.randint(100, 500),  # For bright flashes
                'flash_counter': 0
            }
            self.stars.append(star)
    
    def update_stars(self):
        """Update star brightness for realistic twinkling"""
        for star in self.stars:
            # Basic sine wave twinkling
            star['twinkle_phase'] += star['twinkle_speed']
            if star['twinkle_phase'] > 6.28:
                star['twinkle_phase'] = 0
            
            # Calculate twinkling brightness
            twinkle_factor = 0.3 + 0.4 * (1 + math.sin(star['twinkle_phase'])) / 2
            base_brightness = star['base_brightness'] * twinkle_factor
            
            # Add occasional bright flashes (like real stars)
            star['flash_counter'] += 1
            if star['flash_counter'] >= star['flash_timer']:
                if random.random() < 0.1:  # 10% chance of flash
                    base_brightness = min(1.0, base_brightness + 0.5)
                star['flash_counter'] = 0
                star['flash_timer'] = random.randint(200, 800)
            
            # Add subtle random variations
            if random.random() < 0.05:  # 5% chance of random twinkle
                base_brightness += random.uniform(-0.2, 0.3)
            
            star['current_brightness'] = max(0.1, min(1.0, base_brightness))
        
        self.update()  # Trigger repaint
    
    def paintEvent(self, event):
        """Paint all the twinkling stars"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for star in self.stars:
            # Get color based on type
            if star['color_type'] == 'pink':
                color = QColor(255, 105, 180)
            elif star['color_type'] == 'blue':
                color = QColor(173, 216, 230)
            else:  # white
                color = QColor(255, 255, 255)
            
            # Apply current brightness - much brighter
            alpha = int(255 * min(1.0, star['current_brightness'] * 1.8))
            color.setAlpha(alpha)
            
            # Draw star
            painter.setBrush(QBrush(color))
            painter.setPen(Qt.NoPen)
            
            star_size = star['size']
            # Make brighter stars slightly larger
            if star['current_brightness'] > 0.8:
                star_size += 1
            
            painter.drawEllipse(
                int(star['x'] - star_size/2), 
                int(star['y'] - star_size/2),
                star_size, 
                star_size
            )
    
    def resizeEvent(self, event):
        """Recreate stars when widget is resized"""
        super().resizeEvent(event)
        if hasattr(self, 'stars'):
            QTimer.singleShot(50, self.create_stars)


class FileRecoveryThread(QThread):
    progress_updated = Signal(int)
    files_found = Signal(list)
    finished = Signal()
    
    def __init__(self, recovery_engine: FileRecoveryEngine):
        super().__init__()
        self.recovery_engine = recovery_engine
        
    def run(self):
        deleted_files = self.recovery_engine.scan_for_deleted_files()
        self.files_found.emit(deleted_files)
        self.finished.emit()


class AcceleratedScanThread(QThread):
    progress_updated = Signal(int)
    files_found = Signal(list)
    finished = Signal()
    
    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = Path(folder_path)
        self.scanner = get_optimal_scanner()
        
    def run(self):
        def progress_callback(progress):
            self.progress_updated.emit(progress)
        
        try:
            deleted_files = self.scanner.scan_folder_deep(self.folder_path, progress_callback)
            self.files_found.emit(deleted_files)
        except Exception as e:
            # Handle errors gracefully
            print(f"Accelerated scan error: {e}")
            self.files_found.emit([])
        finally:
            self.finished.emit()


class OopsieDaisyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.recovery_engine = FileRecoveryEngine()
        self.recovery_thread: Optional[FileRecoveryThread] = None
        self.found_files: List[dict] = []
        
        self.setup_ui()
        self.setup_style()
        
    def setup_ui(self):
        self.setWindowTitle("Oopsie Daisy - File Recovery")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Main container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Add realistic starry background layer covering entire window
        self.starry_background = RealStarryBackground(central_widget)
        self.starry_background.setGeometry(0, 0, self.width(), self.height())
        self.starry_background.lower()  # Send to back
        
        # Use horizontal layout for modern sidebar + main content design
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left sidebar
        sidebar = QWidget()
        sidebar.setFixedWidth(320)
        sidebar.setObjectName("sidebar")
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(32, 40, 32, 40)
        sidebar_layout.setSpacing(24)
        
        # Logo/Brand area
        brand_container = QWidget()
        brand_layout = QVBoxLayout(brand_container)
        brand_layout.setContentsMargins(0, 0, 0, 0)
        brand_layout.setSpacing(8)
        
        logo_label = QLabel("🐱")
        logo_label.setObjectName("logo")
        logo_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("Oopsie Daisy")
        title_label.setObjectName("brand-title")
        title_label.setAlignment(Qt.AlignCenter)
        
        tagline_label = QLabel("File Recovery Made Simple")
        tagline_label.setObjectName("tagline")
        tagline_label.setAlignment(Qt.AlignCenter)
        
        brand_layout.addWidget(logo_label)
        brand_layout.addWidget(title_label)
        brand_layout.addWidget(tagline_label)
        
        sidebar_layout.addWidget(brand_container)
        sidebar_layout.addSpacing(32)
        
        # Action buttons in sidebar
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setObjectName("primary-button")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setMinimumHeight(48)
        
        self.folder_scan_button = QPushButton("Scan Folder")
        self.folder_scan_button.setObjectName("folder-scan-button")
        self.folder_scan_button.clicked.connect(self.start_folder_scan)
        self.folder_scan_button.setMinimumHeight(48)
        self.folder_scan_button.setToolTip("Choose a specific folder to scan for deleted files")
        
        self.restore_button = QPushButton("Restore Files")
        self.restore_button.setObjectName("secondary-button")
        self.restore_button.clicked.connect(self.restore_selected_files)
        self.restore_button.setEnabled(False)
        self.restore_button.setMinimumHeight(48)
        
        sidebar_layout.addWidget(self.scan_button)
        sidebar_layout.addWidget(self.folder_scan_button)
        sidebar_layout.addWidget(self.restore_button)
        sidebar_layout.addSpacing(24)
        
        # Stats/info section
        self.stats_container = QWidget()
        self.stats_container.setObjectName("stats-card")
        stats_layout = QVBoxLayout(self.stats_container)
        stats_layout.setContentsMargins(16, 16, 16, 16)
        stats_layout.setSpacing(8)
        
        stats_title = QLabel("Scan Results")
        stats_title.setObjectName("stats-title")
        
        self.files_count_label = QLabel("0 files found")
        self.files_count_label.setObjectName("stats-value")
        
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(self.files_count_label)
        
        sidebar_layout.addWidget(self.stats_container)
        sidebar_layout.addStretch()
        
        # Progress section at bottom of sidebar
        self.progress_container = QWidget()
        progress_layout = QVBoxLayout(self.progress_container)
        progress_layout.setContentsMargins(0, 16, 0, 0)
        progress_layout.setSpacing(8)
        
        self.progress_label = QLabel("Ready to scan")
        self.progress_label.setObjectName("progress-text")
        self.progress_label.setAlignment(Qt.AlignCenter)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setObjectName("progress-bar")
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        sidebar_layout.addWidget(self.progress_container)
        
        # Main content area
        content_widget = QWidget()
        content_widget.setObjectName("main-content")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Header
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        content_title = QLabel("Deleted Files")
        content_title.setObjectName("content-title")
        
        self.status_label = QLabel("Click 'Start Scan' to begin searching for deleted files")
        self.status_label.setObjectName("status-text")
        
        header_layout.addWidget(content_title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        
        content_layout.addWidget(header_widget)
        
        # Files table/list
        self.files_list = QListWidget()
        self.files_list.setObjectName("files-list")
        self.files_list.setMinimumHeight(400)
        
        content_layout.addWidget(self.files_list)
        
        # Add widgets to main layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_widget, 1)
    
    def resizeEvent(self, event):
        """Handle window resize to update starry background"""
        super().resizeEvent(event)
        if hasattr(self, 'starry_background'):
            new_size = event.size()
            self.starry_background.setGeometry(0, 0, new_size.width(), new_size.height())
            # The RealStarryBackground will recreate stars for the new size
        
    def setup_style(self):
        # Modern UI with blue starry sky + pink accents
        modern_style = """
        /* Main window - Clean blue sky background (stars added via graphics) */
        QMainWindow {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #1E3A8A, stop:0.3 #3B82F6, stop:0.6 #60A5FA, stop:1 #1E3A8A);
        }
        
        /* Sidebar styling */
        QWidget[objectName="sidebar"] {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(30, 58, 138, 0.95), stop:1 rgba(59, 130, 246, 0.85));
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* Main content area */
        QWidget[objectName="main-content"] {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 0px;
        }
        
        /* Typography */
        QLabel {
            color: white;
            font-family: 'SF Pro Display', 'Segoe UI', system-ui, sans-serif;
            font-weight: 400;
        }
        
        QLabel[objectName="logo"] {
            font-size: 48px;
            margin: 8px;
        }
        
        QLabel[objectName="brand-title"] {
            color: #FF69B4;
            font-size: 28px;
            font-weight: 700;
            margin: 0;
        }
        
        QLabel[objectName="tagline"] {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            font-weight: 300;
            margin: 4px 0 0 0;
        }
        
        QLabel[objectName="content-title"] {
            color: white;
            font-size: 32px;
            font-weight: 700;
        }
        
        QLabel[objectName="status-text"] {
            color: rgba(255, 255, 255, 0.7);
            font-size: 16px;
            font-weight: 400;
        }
        
        QLabel[objectName="stats-title"] {
            color: #FF69B4;
            font-size: 14px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        QLabel[objectName="stats-value"] {
            color: white;
            font-size: 24px;
            font-weight: 700;
            margin-top: 4px;
        }
        
        QLabel[objectName="progress-text"] {
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
            font-weight: 500;
        }
        
        /* Modern buttons */
        QPushButton[objectName="primary-button"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF1493, stop:1 #C2185B);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            padding: 12px 24px;
        }
        
        QPushButton[objectName="primary-button"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #FF69B4, stop:1 #FF1493);
        }
        
        QPushButton[objectName="primary-button"]:pressed {
            background: #C2185B;
        }
        
        QPushButton[objectName="secondary-button"] {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid #FF69B4;
            border-radius: 8px;
            color: #FF69B4;
            font-size: 16px;
            font-weight: 600;
            padding: 12px 24px;
        }
        
        QPushButton[objectName="secondary-button"]:hover {
            background: rgba(255, 105, 180, 0.2);
            color: white;
        }
        
        QPushButton[objectName="secondary-button"]:pressed {
            background: rgba(255, 105, 180, 0.3);
        }
        
        QPushButton:disabled {
            background: rgba(255, 255, 255, 0.05);
            border: 2px solid rgba(255, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.4);
        }
        
        QPushButton[objectName=\"folder-scan-button\"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4A90E2, stop:1 #357ABD);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            padding: 12px 24px;
        }
        
        QPushButton[objectName=\"folder-scan-button\"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #5BA0F2, stop:1 #4A90E2);
        }
        
        QPushButton[objectName=\"folder-scan-button\"]:pressed {
            background: #357ABD;
        }
        
        /* Stats card */
        QWidget[objectName="stats-card"] {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
        }
        
        /* Files list */
        QListWidget[objectName="files-list"] {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 16px;
            color: white;
            font-size: 15px;
            outline: none;
        }
        
        QListWidget::item {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 105, 180, 0.3);
            border-radius: 8px;
            padding: 16px;
            margin: 4px 0;
            color: white;
        }
        
        QListWidget::item:hover {
            background: rgba(255, 105, 180, 0.2);
            border: 1px solid #FF69B4;
        }
        
        QListWidget::item:selected {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba(255, 20, 147, 0.6), stop:1 rgba(255, 105, 180, 0.6));
            border: 1px solid #FF1493;
            color: white;
            font-weight: 600;
        }
        
        /* Progress bar */
        QProgressBar[objectName="progress-bar"] {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 6px;
            text-align: center;
            color: white;
            font-weight: 500;
            min-height: 8px;
        }
        
        QProgressBar::chunk {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #FF1493, stop:1 #FF69B4);
            border-radius: 4px;
            margin: 1px;
        }
        
        /* Scrollbars */
        QScrollBar:vertical {
            background: rgba(255, 255, 255, 0.1);
            width: 8px;
            border-radius: 4px;
        }
        
        QScrollBar::handle:vertical {
            background: rgba(255, 105, 180, 0.6);
            border-radius: 4px;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: rgba(255, 105, 180, 0.8);
        }
        """
        
        self.setStyleSheet(modern_style)
        
    def start_scan(self):
        if self.recovery_thread and self.recovery_thread.isRunning():
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_label.setText("Scanning for deleted files...")
        self.status_label.setText("Scanning in progress")
        self.scan_button.setEnabled(False)
        self.folder_scan_button.setEnabled(False)
        self.files_list.clear()
        
        self.recovery_thread = FileRecoveryThread(self.recovery_engine)
        self.recovery_thread.files_found.connect(self.on_files_found)
        self.recovery_thread.finished.connect(self.on_scan_finished)
        self.recovery_thread.start()
    
    def start_folder_scan(self):
        """Start scanning a specific folder chosen by user."""
        if self.recovery_thread and self.recovery_thread.isRunning():
            return
            
        # Ask user to select folder
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "🔍 Choose folder to scan for deleted files",
            str(Path.home())
        )
        
        if not folder_path:
            return
            
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)  # Determinate progress for folder scan
        self.progress_label.setText(f"Deep scanning: {Path(folder_path).name}...")
        self.status_label.setText("Deep folder scan in progress")
        self.scan_button.setEnabled(False)
        self.folder_scan_button.setEnabled(False)
        self.files_list.clear()
        
        # Use accelerated scanner for folder scan
        self.recovery_thread = AcceleratedScanThread(folder_path)
        self.recovery_thread.progress_updated.connect(self.progress_bar.setValue)
        self.recovery_thread.files_found.connect(self.on_files_found)
        self.recovery_thread.finished.connect(self.on_scan_finished)
        self.recovery_thread.start()
        
    def on_files_found(self, files: List[dict]):
        self.found_files = files
        self.files_list.clear()
        
        for file_info in files:
            item_text = f"📄 {file_info['name']} ({file_info['size']} bytes)"
            if 'date_deleted' in file_info:
                item_text += f" - Deleted: {file_info['date_deleted']}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, file_info)
            self.files_list.addItem(item)
            
    def on_scan_finished(self):
        self.progress_bar.setVisible(False)
        self.scan_button.setEnabled(True)
        self.folder_scan_button.setEnabled(True)
        
        file_count = len(self.found_files)
        self.files_count_label.setText(f"{file_count} files found")
        
        if self.found_files:
            self.progress_label.setText("Scan completed")
            self.status_label.setText("Select files to restore")
            self.restore_button.setEnabled(True)
        else:
            self.progress_label.setText("No files found")
            self.status_label.setText("No deleted files found in scanned locations")
            
    def restore_selected_files(self):
        selected_items = self.files_list.selectedItems()
        
        if not selected_items:
            QMessageBox.information(
                self, 
                "🐱 Oopsie Daisy - No Files Selected", 
                "Oops! You need to select at least one file first! 💕\n\n"
                "📋 How to select files:\n"
                "  • Click once on a file to select it\n"
                "  • Hold Ctrl (or Cmd on Mac) and click to select multiple files\n"
                "  • Hold Shift and click to select a range of files\n\n"
                "Then come back and click this button again! 🐾"
            )
            return
            
        # Ask user where to restore files with helpful dialog
        restore_dir = QFileDialog.getExistingDirectory(
            self,
            f"🏠 Choose where to save your {len(selected_items)} recovered file{'s' if len(selected_items) != 1 else ''} - Recommended: Desktop or Documents",
            str(Path.home() / "Desktop")
        )
        
        if not restore_dir:
            return
            
        restored_count = 0
        for item in selected_items:
            file_info = item.data(Qt.UserRole)
            try:
                success = self.recovery_engine.restore_file(file_info, restore_dir)
                if success:
                    restored_count += 1
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "🙀 Oops! Restore Problem",
                    f"We had trouble restoring '{file_info['name']}' 😿\n\n"
                    f"Error details: {str(e)}\n\n"
                    f"💡 This might help:\n"
                    f"  • Try choosing a different folder (like Desktop)\n"
                    f"  • Make sure the folder isn't read-only\n"
                    f"  • Close any programs that might be using this file\n\n"
                    f"Don't worry - your original file is still safe! 🐾"
                )
                
        if restored_count > 0:
            QMessageBox.information(
                self,
                "🎉 Mission Accomplished!",
                f"Hooray! Successfully restored {restored_count} file{'s' if restored_count != 1 else ''} to:\n"
                f"📂 {restore_dir}\n\n"
                f"🎯 What to do now:\n"
                f"  • Open the folder above to see your recovered files\n"
                f"  • Your files are now safe and sound! 🛡️\n"
                f"  • Consider backing them up to prevent future scares\n\n"
                f"You're all set! Our virtual kittens are purring with pride! 🐱💕"
            )
        else:
            QMessageBox.warning(
                self,
                "😿 Restore Challenge",
                "We weren't able to restore any files this time. 😔\n\n"
                "🤔 This might mean:\n"
                "  • The files were permanently deleted\n"
                "  • They're corrupted or no longer accessible\n"
                "  • Permission issues with the chosen folder\n\n"
                "💡 You could try:\n"
                "  • Running the scan again (sometimes files appear later)\n"
                "  • Checking your Trash/Recycle Bin manually\n"
                "  • Using a different recovery tool for deeper scanning\n\n"
                "Don't give up - there might still be hope! 🌟"
            )


def run_app():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Oopsie Daisy")
    app.setApplicationDisplayName("🐱 Oopsie Daisy - File Recovery")
    app.setApplicationVersion("0.1.0")
    
    window = OopsieDaisyMainWindow()
    window.show()
    
    sys.exit(app.exec())