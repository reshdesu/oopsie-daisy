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
    QPushButton, QLabel
)
from PySide6.QtCore import Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve, QRect, QPointF
from PySide6.QtGui import QFont, QPixmap, QPalette, QColor, QBrush, QPen, QPainter

from .recovery_wizard import RecoveryWizard


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
        
        # Main recovery button
        self.recovery_button = QPushButton("🧙‍♀️ Start File Recovery")
        self.recovery_button.setObjectName("primary-button")
        self.recovery_button.clicked.connect(self.open_recovery_wizard)
        self.recovery_button.setMinimumHeight(60)
        self.recovery_button.setToolTip("Launch professional file recovery wizard")
        
        sidebar_layout.addWidget(self.recovery_button)
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
        
        # Main content area
        content_widget = QWidget()
        content_widget.setObjectName("main-content")
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(40, 40, 40, 40)
        content_layout.setSpacing(24)
        
        # Welcome content
        welcome_widget = QWidget()
        welcome_layout = QVBoxLayout(welcome_widget)
        welcome_layout.setAlignment(Qt.AlignCenter)
        welcome_layout.setSpacing(30)
        
        # Large icon
        icon_label = QLabel("🔮")
        icon_label.setStyleSheet("font-size: 120px;")
        icon_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel("Professional File Recovery")
        title_label.setObjectName("content-title")
        title_label.setAlignment(Qt.AlignCenter)
        welcome_layout.addWidget(title_label)
        
        # Description
        desc_text = """
        <div style='text-align: center; color: rgba(255,255,255,0.8); font-size: 16px; line-height: 1.6;'>
        <p><b>Recover your lost files like a pro!</b></p>
        <p>Our advanced recovery wizard uses professional-grade techniques:</p>
        <br>
        <p>• <b>Deep Disk Scanning</b> - Analyzes file system structures</p>
        <p>• <b>Signature Recovery</b> - Finds files even after formatting</p>
        <p>• <b>GPU Acceleration</b> - Lightning-fast scanning with your graphics card</p>
        <p>• <b>Multi-format Support</b> - Documents, images, videos, and more</p>
        <br>
        <p>Click the recovery button to get started! 🚀</p>
        </div>
        """
        
        desc_label = QLabel(desc_text)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(600)
        welcome_layout.addWidget(desc_label)
        
        content_layout.addWidget(welcome_widget)
        
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
        
    def open_recovery_wizard(self):
        """Open the professional recovery wizard."""
        if hasattr(self, 'recovery_wizard') and self.recovery_wizard.isVisible():
            self.recovery_wizard.raise_()
            self.recovery_wizard.activateWindow()
            return
        
        self.recovery_wizard = RecoveryWizard()
        self.recovery_wizard.show()


def run_app():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Oopsie Daisy")
    app.setApplicationDisplayName("🐱 Oopsie Daisy - File Recovery")
    app.setApplicationVersion("0.1.0")
    
    window = OopsieDaisyMainWindow()
    window.show()
    
    sys.exit(app.exec())