#!/usr/bin/env python3
"""
Recovery Wizard UI - Professional file recovery interface like EaseUS Data Recovery Wizard Pro.
"""

import sys
from pathlib import Path
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QProgressBar,
    QTreeWidget, QTreeWidgetItem, QComboBox, QCheckBox, QSpinBox, QGroupBox,
    QRadioButton, QButtonGroup, QTextEdit, QSplitter, QFrame, QScrollArea,
    QListWidget, QListWidgetItem, QStackedWidget, QGridLayout, QLineEdit,
    QSlider, QTabWidget, QHeaderView
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFont, QPainter, QColor

from .advanced_recovery import AdvancedRecoveryEngine, RecoveryMode, RecoveredFile
from .hardware_monitor import ScanHardwareMonitor


class RecoveryWizardThread(QThread):
    """Background thread for recovery operations."""
    progress_updated = Signal(int, str)  # progress, status
    files_found = Signal(list)  # List[RecoveredFile]
    scan_completed = Signal()
    error_occurred = Signal(str)
    
    def __init__(self, engine: AdvancedRecoveryEngine, drive_info: Dict, mode: RecoveryMode):
        super().__init__()
        self.engine = engine
        self.drive_info = drive_info
        self.mode = mode
        self._should_stop = False
    
    def run(self):
        """Execute the recovery scan."""
        try:
            def progress_callback(progress: int, status: str):
                if not self._should_stop:
                    self.progress_updated.emit(progress, status)
            
            recovered_files = self.engine.scan_drive(self.drive_info, self.mode, progress_callback)
            
            if not self._should_stop:
                self.files_found.emit(recovered_files)
                self.scan_completed.emit()
                
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop the scan operation."""
        self._should_stop = True
        self.engine.cancel_scan()


class DriveSelectionWidget(QWidget):
    """Drive selection step of the recovery wizard."""
    
    def __init__(self, engine: AdvancedRecoveryEngine):
        super().__init__()
        self.engine = engine
        self.selected_drive = None
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("🖥️ Select Drive to Scan")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        desc = QLabel("Choose the drive where your files were deleted from:")
        desc.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Drive list
        self.drive_tree = QTreeWidget()
        self.drive_tree.setHeaderLabels(["Drive", "Type", "Size", "Free Space", "Status"])
        self.drive_tree.header().resizeSection(0, 200)
        self.drive_tree.header().resizeSection(1, 100)
        self.drive_tree.header().resizeSection(2, 100)
        self.drive_tree.header().resizeSection(3, 100)
        self.drive_tree.itemSelectionChanged.connect(self.on_drive_selected)
        
        layout.addWidget(self.drive_tree)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Drives")
        refresh_btn.clicked.connect(self.refresh_drives)
        layout.addWidget(refresh_btn)
        
        self.refresh_drives()
    
    def refresh_drives(self):
        """Refresh the list of available drives."""
        self.drive_tree.clear()
        
        drives = self.engine.get_available_drives()
        
        for drive in drives:
            item = QTreeWidgetItem()
            item.setText(0, f"{drive['device']} ({drive['mountpoint']})")
            item.setText(1, drive.get('fstype', 'Unknown'))
            
            # Format sizes
            total_gb = drive.get('total', 0) / (1024**3)
            free_gb = drive.get('free', 0) / (1024**3)
            item.setText(2, f"{total_gb:.1f} GB")
            item.setText(3, f"{free_gb:.1f} GB")
            
            # Status
            if drive.get('opts', '').find('ro') != -1:
                item.setText(4, "Read-only")
                item.setForeground(4, QColor("#ff6b6b"))
            else:
                item.setText(4, "Available")
                item.setForeground(4, QColor("#51cf66"))
            
            # Store drive info
            item.setData(0, Qt.UserRole, drive)
            
            self.drive_tree.addTopLevelItem(item)
    
    def on_drive_selected(self):
        """Handle drive selection."""
        selected = self.drive_tree.selectedItems()
        if selected:
            self.selected_drive = selected[0].data(0, Qt.UserRole)
    
    def get_selected_drive(self) -> Optional[Dict]:
        """Get the currently selected drive."""
        return self.selected_drive


class ScanModeWidget(QWidget):
    """Scan mode selection step."""
    
    def __init__(self):
        super().__init__()
        self.selected_mode = RecoveryMode.DEEP_SCAN
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("⚙️ Choose Scan Mode")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(header)
        
        desc = QLabel("Select the type of scan to perform:")
        desc.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        # Mode selection
        self.mode_group = QButtonGroup()
        
        # Deep Scan
        deep_frame = QFrame()
        deep_frame.setFrameStyle(QFrame.Box)
        deep_frame.setStyleSheet("QFrame { border: 2px solid #e0e0e0; border-radius: 8px; padding: 10px; }")
        deep_layout = QVBoxLayout(deep_frame)
        
        self.deep_radio = QRadioButton("🔍 Deep Scan (Recommended)")
        self.deep_radio.setChecked(True)
        self.deep_radio.setFont(QFont("Arial", 12, QFont.Bold))
        deep_layout.addWidget(self.deep_radio)
        
        deep_desc = QLabel("• Analyzes file system structures (MFT, journal, FAT)\n• Finds older deleted files\n• Fast optimized scanning")
        deep_desc.setStyleSheet("color: #666; margin-left: 20px;")
        deep_layout.addWidget(deep_desc)
        
        self.mode_group.addButton(self.deep_radio, 0)
        layout.addWidget(deep_frame)
        
        # Raw Recovery
        raw_frame = QFrame()
        raw_frame.setFrameStyle(QFrame.Box)
        raw_frame.setStyleSheet("QFrame { border: 2px solid #e0e0e0; border-radius: 8px; padding: 10px; }")
        raw_layout = QVBoxLayout(raw_frame)
        
        self.raw_radio = QRadioButton("🔬 Raw Recovery (Advanced)")
        self.raw_radio.setFont(QFont("Arial", 12, QFont.Bold))
        raw_layout.addWidget(self.raw_radio)
        
        raw_desc = QLabel("• Signature-based file recovery\n• Finds files even after formatting\n• Optimized for faster scanning")
        raw_desc.setStyleSheet("color: #666; margin-left: 20px;")
        raw_layout.addWidget(raw_desc)
        
        self.mode_group.addButton(self.raw_radio, 1)
        layout.addWidget(raw_frame)
        
        # Connect signals
        self.mode_group.buttonClicked.connect(self.on_mode_selected)
        
        layout.addStretch()
    
    def on_mode_selected(self, button):
        """Handle mode selection."""
        if button == self.deep_radio:
            self.selected_mode = RecoveryMode.DEEP_SCAN
        elif button == self.raw_radio:
            self.selected_mode = RecoveryMode.RAW_RECOVERY
    
    def get_selected_mode(self) -> RecoveryMode:
        """Get the selected scan mode."""
        return self.selected_mode


class ScanProgressWidget(QWidget):
    """Scan progress display."""
    
    def __init__(self):
        super().__init__()
        self.hardware_monitor = ScanHardwareMonitor()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        self.header = QLabel("🔍 Scanning for Deleted Files...")
        self.header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Initializing scan...")
        self.status_label.setStyleSheet("color: #666; font-size: 14px;")
        layout.addWidget(self.status_label)
        
        # Statistics
        stats_group = QGroupBox("Scan Statistics")
        stats_layout = QGridLayout(stats_group)
        
        self.elapsed_label = QLabel("Elapsed: 0:00")
        self.remaining_label = QLabel("Remaining: --:--")
        self.found_label = QLabel("Files Found: 0")
        self.scanned_label = QLabel("Data Scanned: 0 MB")
        
        stats_layout.addWidget(QLabel("⏱️"), 0, 0)
        stats_layout.addWidget(self.elapsed_label, 0, 1)
        stats_layout.addWidget(QLabel("⏳"), 1, 0)
        stats_layout.addWidget(self.remaining_label, 1, 1)
        stats_layout.addWidget(QLabel("📄"), 0, 2)
        stats_layout.addWidget(self.found_label, 0, 3)
        stats_layout.addWidget(QLabel("💾"), 1, 2)
        stats_layout.addWidget(self.scanned_label, 1, 3)
        
        layout.addWidget(stats_group)
        
        # Hardware monitoring section
        hardware_group = QGroupBox("🖥️ Hardware Performance")
        hardware_layout = QGridLayout(hardware_group)
        
        # CPU monitoring
        self.cpu_usage_label = QLabel("CPU: 0%")
        self.cpu_temp_label = QLabel("0°C")
        
        # GPU monitoring  
        self.gpu_usage_label = QLabel("GPU: 0%")
        self.gpu_temp_label = QLabel("0°C")
        
        # Memory monitoring
        self.memory_usage_label = QLabel("RAM: 0%")
        
        hardware_layout.addWidget(QLabel("🔧"), 0, 0)
        hardware_layout.addWidget(self.cpu_usage_label, 0, 1)
        hardware_layout.addWidget(self.cpu_temp_label, 0, 2)
        
        hardware_layout.addWidget(QLabel("🎮"), 1, 0)  
        hardware_layout.addWidget(self.gpu_usage_label, 1, 1)
        hardware_layout.addWidget(self.gpu_temp_label, 1, 2)
        
        hardware_layout.addWidget(QLabel("💾"), 2, 0)
        hardware_layout.addWidget(self.memory_usage_label, 2, 1)
        
        layout.addWidget(hardware_group)
        
        # Cancel button
        self.cancel_button = QPushButton("❌ Cancel Scan")
        self.cancel_button.setStyleSheet("QPushButton { background: #ff6b6b; color: white; }")
        layout.addWidget(self.cancel_button)
        
        layout.addStretch()
        
        # Timer for elapsed time
        self.start_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        
    def start_scan(self):
        """Start the scan timer and hardware monitoring."""
        import time
        self.start_time = time.time()
        self.timer.start(1000)  # Update every second
        
        # Start hardware monitoring
        self.hardware_monitor.start_scan_monitoring(self.update_hardware_display)
        
    def stop_scan(self):
        """Stop the scan timer and hardware monitoring."""
        self.timer.stop()
        self.hardware_monitor.stop_monitoring()
        
    def update_progress(self, progress: int, status: str):
        """Update progress display."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        
    def update_statistics(self, files_found: int, data_scanned_mb: int):
        """Update scan statistics."""
        self.found_label.setText(f"Files Found: {files_found}")
        self.scanned_label.setText(f"Data Scanned: {data_scanned_mb} MB")
        
    def update_elapsed_time(self):
        """Update elapsed time display."""
        if self.start_time:
            import time
            elapsed = int(time.time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.elapsed_label.setText(f"Elapsed: {minutes}:{seconds:02d}")
    
    def update_hardware_display(self, stats):
        """Update hardware monitoring display."""
        try:
            # Update CPU stats
            cpu_percent = stats.get('cpu_percent', 0.0)
            cpu_temp = stats.get('cpu_temp', 0.0)
            self.cpu_usage_label.setText(f"CPU: {cpu_percent:.1f}%")
            
            if cpu_temp > 0:
                temp_color = self._get_temp_color(cpu_temp, 70, 85)  # CPU temp thresholds
                self.cpu_temp_label.setText(f"<span style='color: {temp_color}'>{cpu_temp:.1f}°C</span>")
            else:
                self.cpu_temp_label.setText("N/A")
            
            # Update GPU stats
            gpu_percent = stats.get('gpu_percent', 0.0)
            gpu_temp = stats.get('gpu_temp', 0.0)
            self.gpu_usage_label.setText(f"GPU: {gpu_percent:.1f}%")
            
            if gpu_temp > 0:
                temp_color = self._get_temp_color(gpu_temp, 75, 90)  # GPU temp thresholds
                self.gpu_temp_label.setText(f"<span style='color: {temp_color}'>{gpu_temp:.1f}°C</span>")
            else:
                self.gpu_temp_label.setText("N/A")
            
            # Update memory stats
            memory_percent = stats.get('memory_percent', 0.0)
            self.memory_usage_label.setText(f"RAM: {memory_percent:.1f}%")
            
        except Exception as e:
            print(f"Hardware display update error: {e}")
    
    def _get_temp_color(self, temp, warning_threshold, critical_threshold):
        """Get color based on temperature thresholds."""
        if temp >= critical_threshold:
            return "#ff4444"  # Red for critical
        elif temp >= warning_threshold:
            return "#ffaa00"  # Orange for warning
        else:
            return "#44ff44"  # Green for normal


class ResultsWidget(QWidget):
    """Scan results display and file management."""
    
    def __init__(self):
        super().__init__()
        self.recovered_files = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        self.header = QLabel("📁 Scan Results")
        self.header.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(self.header)
        
        # Statistics bar
        stats_layout = QHBoxLayout()
        self.total_files_label = QLabel("Total Files: 0")
        self.recoverable_label = QLabel("Recoverable: 0")
        self.selected_label = QLabel("Selected: 0")
        self.size_label = QLabel("Total Size: 0 MB")
        
        stats_layout.addWidget(self.total_files_label)
        stats_layout.addWidget(self.recoverable_label)
        stats_layout.addWidget(self.selected_label)
        stats_layout.addWidget(self.size_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        
        # Filters
        filter_group = QGroupBox("📋 Filters")
        filter_layout = QHBoxLayout(filter_group)
        
        # File type filter
        filter_layout.addWidget(QLabel("Type:"))
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Files", "Images", "Documents", "Videos", "Audio", "Archives", "Other"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.type_filter)
        
        # Size filter
        filter_layout.addWidget(QLabel("Size:"))
        self.size_filter = QComboBox()
        self.size_filter.addItems(["Any Size", "< 1 MB", "1-10 MB", "10-100 MB", "> 100 MB"])
        self.size_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.size_filter)
        
        # Quality filter
        filter_layout.addWidget(QLabel("Quality:"))
        self.quality_filter = QComboBox()
        self.quality_filter.addItems(["Any Quality", "High", "Medium", "Low"])
        self.quality_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.quality_filter)
        
        # Search
        filter_layout.addWidget(QLabel("Search:"))
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search filename...")
        self.search_box.textChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.search_box)
        
        layout.addWidget(filter_group)
        
        # File list
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Type", "Size", "Quality", "Path", "Status"])
        self.file_tree.header().resizeSection(0, 250)
        self.file_tree.header().resizeSection(1, 80)
        self.file_tree.header().resizeSection(2, 100)
        self.file_tree.header().resizeSection(3, 80)
        self.file_tree.header().resizeSection(4, 200)
        self.file_tree.header().resizeSection(5, 100)
        
        self.file_tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.file_tree.itemChanged.connect(self.on_item_changed)
        
        layout.addWidget(self.file_tree)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("✅ Select All")
        select_all_btn.clicked.connect(self.select_all_files)
        button_layout.addWidget(select_all_btn)
        
        select_none_btn = QPushButton("❌ Select None")
        select_none_btn.clicked.connect(self.select_no_files)
        button_layout.addWidget(select_none_btn)
        
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self.preview_selected_file)
        button_layout.addWidget(preview_btn)
        
        button_layout.addStretch()
        
        self.recover_btn = QPushButton("💾 Recover Selected Files")
        self.recover_btn.setStyleSheet("QPushButton { background: #51cf66; color: white; font-weight: bold; }")
        self.recover_btn.clicked.connect(self.recover_selected_files)
        button_layout.addWidget(self.recover_btn)
        
        layout.addLayout(button_layout)
    
    def set_results(self, files: List[RecoveredFile]):
        """Set the scan results."""
        self.recovered_files = files
        self.populate_file_list()
        self.update_statistics()
    
    def populate_file_list(self):
        """Populate the file tree with results."""
        self.file_tree.clear()
        
        for file_info in self.recovered_files:
            item = QTreeWidgetItem()
            item.setCheckState(0, Qt.Unchecked)
            item.setText(0, file_info.name)
            item.setText(1, file_info.file_type.upper())
            
            # Format size
            if file_info.size < 1024:
                size_str = f"{file_info.size} B"
            elif file_info.size < 1024*1024:
                size_str = f"{file_info.size/1024:.1f} KB"
            else:
                size_str = f"{file_info.size/(1024*1024):.1f} MB"
            item.setText(2, size_str)
            
            # Quality indicator
            quality_str = f"{file_info.quality*100:.0f}%"
            item.setText(3, quality_str)
            if file_info.quality >= 0.8:
                item.setForeground(3, QColor("#51cf66"))
            elif file_info.quality >= 0.5:
                item.setForeground(3, QColor("#ffd43b"))
            else:
                item.setForeground(3, QColor("#ff6b6b"))
            
            item.setText(4, file_info.path[:50] + "..." if len(file_info.path) > 50 else file_info.path)
            
            # Status
            if file_info.recoverable:
                item.setText(5, "Recoverable")
                item.setForeground(5, QColor("#51cf66"))
            else:
                item.setText(5, "Damaged")
                item.setForeground(5, QColor("#ff6b6b"))
                item.setCheckState(0, Qt.Unchecked)
                item.setDisabled(True)
            
            # Store file info
            item.setData(0, Qt.UserRole, file_info)
            
            self.file_tree.addTopLevelItem(item)
    
    def apply_filters(self):
        """Apply current filters to the file list."""
        # This would implement filtering logic
        pass
    
    def update_statistics(self):
        """Update statistics display."""
        total = len(self.recovered_files)
        recoverable = sum(1 for f in self.recovered_files if f.recoverable)
        
        self.total_files_label.setText(f"Total Files: {total}")
        self.recoverable_label.setText(f"Recoverable: {recoverable}")
        
        # Update selected count
        selected = self.get_selected_files()
        self.selected_label.setText(f"Selected: {len(selected)}")
        
        total_size_mb = sum(f.size for f in selected) / (1024*1024)
        self.size_label.setText(f"Total Size: {total_size_mb:.1f} MB")
    
    def get_selected_files(self) -> List[RecoveredFile]:
        """Get list of selected files."""
        selected = []
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                file_info = item.data(0, Qt.UserRole)
                selected.append(file_info)
        return selected
    
    def select_all_files(self):
        """Select all recoverable files."""
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            if not item.isDisabled():
                item.setCheckState(0, Qt.Checked)
        self.update_statistics()
    
    def select_no_files(self):
        """Deselect all files."""
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            item.setCheckState(0, Qt.Unchecked)
        self.update_statistics()
    
    def on_item_changed(self, item, column):
        """Handle item selection changes."""
        if column == 0:  # Checkbox column
            self.update_statistics()
    
    def preview_selected_file(self):
        """Preview the selected file."""
        # This would show a preview dialog
        pass
    
    def recover_selected_files(self):
        """Signal to recover selected files."""
        selected = self.get_selected_files()
        if selected:
            # Emit signal or call parent method
            print(f"Recovering {len(selected)} files...")


class RecoveryWizard(QWidget):
    """Main recovery wizard widget."""
    
    def __init__(self):
        super().__init__()
        self.engine = AdvancedRecoveryEngine()
        self.recovery_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("🐱 Oopsie Daisy - Advanced Recovery Wizard")
        self.setMinimumSize(1000, 700)
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🧙‍♀️ Advanced File Recovery Wizard")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        title.setStyleSheet("color: #FF69B4; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Step indicator
        self.step_indicator = QLabel("Step 1 of 4: Select Drive")
        self.step_indicator.setStyleSheet("color: #666; font-size: 14px; margin: 5px;")
        self.step_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.step_indicator)
        
        # Stacked widget for wizard steps
        self.stack = QStackedWidget()
        
        # Step 1: Drive Selection
        self.drive_widget = DriveSelectionWidget(self.engine)
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
        
        layout.addWidget(self.stack)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.back_btn = QPushButton("⬅️ Back")
        self.back_btn.clicked.connect(self.go_back)
        self.back_btn.setEnabled(False)
        nav_layout.addWidget(self.back_btn)
        
        nav_layout.addStretch()
        
        self.next_btn = QPushButton("Next ➡️")
        self.next_btn.clicked.connect(self.go_next)
        nav_layout.addWidget(self.next_btn)
        
        layout.addLayout(nav_layout)
        
        # Current step
        self.current_step = 0
        self.update_navigation()
    
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
        self.recovery_thread.files_found.connect(self.on_scan_completed)
        self.recovery_thread.error_occurred.connect(self.on_scan_error)
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
    
    def on_scan_completed(self, files: List[RecoveredFile]):
        """Handle scan completion."""
        self.progress_widget.stop_scan()
        self.results_widget.set_results(files)
        self.current_step = 3
        self.stack.setCurrentIndex(self.current_step)
        self.update_navigation()
        
        print(f"Scan completed! Found {len(files)} recoverable files.")
    
    def on_scan_error(self, error: str):
        """Handle scan error."""
        self.progress_widget.stop_scan()
        print(f"Scan error: {error}")
        # Show error dialog
        self.current_step = 1
        self.stack.setCurrentIndex(self.current_step)
        self.update_navigation()