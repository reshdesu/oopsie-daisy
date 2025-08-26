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
    QPushButton, QLabel, QStackedWidget
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QBrush, QPen, QPainter

from .recovery_wizard import DriveSelectionWidget, ScanModeWidget, ScanProgressWidget, ResultsWidget, RecoveryWizardThread
from .advanced_recovery import AdvancedRecoveryEngine, RecoveryMode


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




class OopsieDaisyMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.engine = AdvancedRecoveryEngine()
        self.recovery_thread = None
        self.current_step = 0
        self.found_files = []
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
        
        # Navigation buttons for wizard steps
        nav_container = QWidget()
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setSpacing(12)
        
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.setObjectName("secondary-button")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.setObjectName("primary-button")
        self.next_btn.clicked.connect(self.go_next)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.next_btn)
        
        sidebar_layout.addWidget(nav_container)
        sidebar_layout.addSpacing(24)
        
        # Features section
        features_group = QWidget()
        features_group.setObjectName("stats-card")
        features_layout = QVBoxLayout(features_group)
        features_layout.setContentsMargins(16, 16, 16, 16)
        features_layout.setSpacing(8)
        
        features_title = QLabel("Professional Features")
        features_title.setObjectName("stats-title")
        features_layout.addWidget(features_title)
        
        features = [
            "🔍 Deep disk scanning",
            "🧬 Signature-based recovery", 
            "⚡ GPU acceleration",
            "🖥️ Multi-core processing",
            "📁 All file types supported",
            "💾 Raw partition recovery"
        ]
        
        for feature in features:
            feature_label = QLabel(feature)
            feature_label.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 12px; margin: 2px 0;")
            features_layout.addWidget(feature_label)
        
        sidebar_layout.addWidget(features_group)
        sidebar_layout.addStretch()
        
        # Main content area with integrated wizard
        content_widget = QWidget()
        content_widget.setObjectName("main-content")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Step indicator header
        self.step_indicator = QLabel("Step 1 of 4: Select Drive")
        self.step_indicator.setStyleSheet("color: #FF69B4; font-size: 18px; font-weight: bold; margin: 10px;")
        self.step_indicator.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(self.step_indicator)
        
        # Stacked widget for wizard steps (integrated into main content)
        self.stack = QStackedWidget()
        
        # Step 1: Drive Selection
        self.drive_widget = DriveSelectionWidget(self.engine)
        self.drive_widget.drive_tree.itemSelectionChanged.connect(self.update_navigation)
        self.stack.addWidget(self.drive_widget)
        
        # Step 2: Scan Mode
        self.mode_widget = ScanModeWidget()
        self.stack.addWidget(self.mode_widget)
        
        # Step 3: Scan Progress
        self.progress_widget = ScanProgressWidget()
        self.progress_widget.cancel_button.clicked.connect(self.cancel_scan)
        self.stack.addWidget(self.progress_widget)
        
        # Step 4: Results
        self.results_widget = ResultsWidget()
        self.stack.addWidget(self.results_widget)
        
        content_layout.addWidget(self.stack)
        
        # Initialize navigation
        self.update_navigation()
        
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
        
        QPushButton[objectName=\"advanced-button\"] {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #8E44AD, stop:1 #6C3483);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            padding: 12px 24px;
        }
        
        QPushButton[objectName=\"advanced-button\"]:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #9B59B6, stop:1 #8E44AD);
        }
        
        QPushButton[objectName=\"advanced-button\"]:pressed {
            background: #6C3483;
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
        
    def update_navigation(self):
        """Update navigation button states."""
        step_names = [
            "Step 1 of 4: Select Drive",
            "Step 2 of 4: Choose Scan Mode",
            "Step 3 of 4: Scanning...",
            "Step 4 of 4: Recovery Results"
        ]
        
        self.step_indicator.setText(step_names[self.current_step])
        
        self.back_btn.setEnabled(self.current_step > 0 and self.current_step != 2)
        
        if self.current_step == 0:
            self.next_btn.setText("Next ➡️")
            self.next_btn.setEnabled(self.drive_widget.get_selected_drive() is not None)
        elif self.current_step == 1:
            self.next_btn.setText("Start Scan 🚀")
            self.next_btn.setEnabled(True)
        elif self.current_step == 2:
            self.next_btn.setText("Scanning...")
            self.next_btn.setEnabled(False)
        elif self.current_step == 3:
            self.next_btn.setText("New Scan 🔄")
            self.next_btn.setEnabled(True)
    
    def go_back(self):
        """Go to previous step."""
        if self.current_step > 0:
            self.current_step -= 1
            self.stack.setCurrentIndex(self.current_step)
            self.update_navigation()
    
    def go_next(self):
        """Go to next step."""
        if self.current_step == 0:
            # Drive selection -> Scan mode
            self.current_step = 1
            self.stack.setCurrentIndex(self.current_step)
        elif self.current_step == 1:
            # Scan mode -> Start scan
            self.start_scan()
            self.current_step = 2
            self.stack.setCurrentIndex(self.current_step)
        elif self.current_step == 3:
            # Results -> Start over
            self.current_step = 0
            self.stack.setCurrentIndex(self.current_step)
        
        self.update_navigation()
    
    def start_scan(self):
        """Start the recovery scan."""
        drive_info = self.drive_widget.get_selected_drive()
        scan_mode = self.mode_widget.get_selected_mode()
        
        if not drive_info:
            return
        
        print(f"Starting {scan_mode.value} scan of {drive_info['device']}")
        
        # Update progress widget
        self.progress_widget.start_scan()
        
        # Start recovery thread
        self.recovery_thread = RecoveryWizardThread(self.engine, drive_info, scan_mode)
        self.recovery_thread.progress_updated.connect(self.progress_widget.update_progress)
        self.recovery_thread.files_found.connect(self.on_files_found)
        self.recovery_thread.scan_completed.connect(self.on_scan_completed)
        self.recovery_thread.error_occurred.connect(self.on_scan_error)
        self.recovery_thread.finished.connect(self.on_thread_finished)
        self.recovery_thread.start()
    
    def cancel_scan(self):
        """Cancel the current scan."""
        if self.recovery_thread and self.recovery_thread.isRunning():
            self.recovery_thread.stop()
            self.recovery_thread.wait()
        
        self.progress_widget.stop_scan()
        self.current_step = 1
        self.stack.setCurrentIndex(self.current_step)
        self.update_navigation()
    
    def on_files_found(self, files):
        """Handle files found during scan."""
        self.found_files = files
        print(f"Files found during scan: {len(files)}")
    
    def on_scan_completed(self):
        """Handle scan completion."""
        print("Scan completed signal received!")
        self.progress_widget.stop_scan()
        
        # Use the files found during scanning
        if hasattr(self, 'found_files'):
            self.results_widget.set_results(self.found_files)
            print(f"Setting results with {len(self.found_files)} files")
        else:
            self.results_widget.set_results([])
            print("No files found to display")
        
        self.current_step = 3
        self.stack.setCurrentIndex(self.current_step)
        self.update_navigation()
        print(f"UI updated to step {self.current_step}")
    
    def on_thread_finished(self):
        """Handle thread finished."""
        print("Recovery thread finished")
    
    def on_scan_error(self, error):
        """Handle scan error."""
        self.progress_widget.stop_scan()
        print(f"Scan error: {error}")
        # Show error dialog
        self.current_step = 1
        self.stack.setCurrentIndex(self.current_step)
        self.update_navigation()


def run_app():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Oopsie Daisy")
    app.setApplicationDisplayName("🐱 Oopsie Daisy - File Recovery")
    app.setApplicationVersion("0.1.0")
    
    window = OopsieDaisyMainWindow()
    window.show()
    
    sys.exit(app.exec())