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
    QSlider, QTabWidget, QHeaderView, QDialog, QFileDialog, QMessageBox,
    QScrollArea, QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QPixmap, QIcon, QFont, QPainter, QColor

from .advanced_recovery import AdvancedRecoveryEngine, RecoveryMode, RecoveredFile
from .hardware_monitor_qt import ScanHardwareMonitor


class FileRecoveryThread(QThread):
    """Background thread for file recovery operations."""
    progress_updated = Signal(int, str, str)  # progress, current_file, status
    recovery_completed = Signal(int, int)  # successful, failed
    error_occurred = Signal(str)
    
    def __init__(self, engine: AdvancedRecoveryEngine, files: List[RecoveredFile], output_path: str):
        super().__init__()
        self.engine = engine
        self.files = files
        self.output_path = output_path
        self._should_stop = False
        
    def run(self):
        """Execute file recovery."""
        successful = 0
        failed = 0
        
        try:
            from pathlib import Path
            import time
            
            output_dir = Path(self.output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            total_files = len(self.files)
            
            for i, file_info in enumerate(self.files):
                if self._should_stop:
                    break
                    
                progress = int((i / total_files) * 100)
                self.progress_updated.emit(progress, file_info.name, "Recovering...")
                
                # Simulate recovery time
                time.sleep(0.5)
                
                try:
                    success = self.engine.recover_file(file_info, str(output_dir))
                    if success:
                        successful += 1
                        self.progress_updated.emit(progress, file_info.name, "✅ Recovered")
                    else:
                        failed += 1
                        self.progress_updated.emit(progress, file_info.name, "❌ Failed")
                except Exception as e:
                    failed += 1
                    self.progress_updated.emit(progress, file_info.name, f"❌ Error: {str(e)[:30]}")
                
                time.sleep(0.2)  # Brief pause between files
                
            self.progress_updated.emit(100, "Complete", f"Finished: {successful} successful, {failed} failed")
            self.recovery_completed.emit(successful, failed)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def stop(self):
        """Stop the recovery operation."""
        self._should_stop = True


class FileRecoveryDialog(QDialog):
    """Progress dialog for file recovery operations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recovery_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("🔄 Recovering Files...")
        self.setModal(True)
        
        # Adaptive dialog size based on screen
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Scale dialog size to screen
            dialog_width = max(400, min(600, int(screen_width * 0.35)))
            dialog_height = max(250, min(350, int(screen_height * 0.25)))
            
            self.setFixedSize(dialog_width, dialog_height)
        else:
            self.setFixedSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("💾 File Recovery in Progress")
        header.setFont(QFont("Arial", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Current file
        self.current_file_label = QLabel("Preparing...")
        self.current_file_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        layout.addWidget(self.current_file_label)
        
        # Status
        self.status_label = QLabel("Initializing recovery process...")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Stats
        stats_layout = QHBoxLayout()
        self.successful_label = QLabel("✅ Success: 0")
        self.failed_label = QLabel("❌ Failed: 0")
        stats_layout.addWidget(self.successful_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_btn = QPushButton("❌ Cancel")
        self.cancel_btn.clicked.connect(self.cancel_recovery)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Track stats
        self.successful_count = 0
        self.failed_count = 0
        
    def start_recovery(self, engine: AdvancedRecoveryEngine, files: List[RecoveredFile], output_path: str):
        """Start the file recovery process."""
        self.recovery_thread = FileRecoveryThread(engine, files, output_path)
        self.recovery_thread.progress_updated.connect(self.update_progress)
        self.recovery_thread.recovery_completed.connect(self.on_recovery_completed)
        self.recovery_thread.error_occurred.connect(self.on_recovery_error)
        self.recovery_thread.start()
        
    def update_progress(self, progress: int, current_file: str, status: str):
        """Update progress display."""
        self.progress_bar.setValue(progress)
        self.current_file_label.setText(f"📄 {current_file}")
        self.status_label.setText(status)
        
        # Update stats
        if "✅" in status:
            self.successful_count += 1
            self.successful_label.setText(f"✅ Success: {self.successful_count}")
        elif "❌" in status and "Failed" in status:
            self.failed_count += 1
            self.failed_label.setText(f"❌ Failed: {self.failed_count}")
            
    def on_recovery_completed(self, successful: int, failed: int):
        """Handle recovery completion."""
        self.cancel_btn.setText("✅ Close")
        self.cancel_btn.clicked.disconnect()
        self.cancel_btn.clicked.connect(self.accept)
        
        # Show completion message
        QMessageBox.information(self, "Recovery Complete", 
                               f"File recovery completed!\n\n"
                               f"✅ Successfully recovered: {successful} files\n"
                               f"❌ Failed to recover: {failed} files")
        
    def on_recovery_error(self, error: str):
        """Handle recovery error."""
        QMessageBox.critical(self, "Recovery Error", f"An error occurred during recovery:\n\n{error}")
        self.reject()
        
    def cancel_recovery(self):
        """Cancel the recovery process."""
        if self.recovery_thread and self.recovery_thread.isRunning():
            self.recovery_thread.stop()
            self.recovery_thread.wait()
        self.reject()
        
    def closeEvent(self, event):
        """Handle dialog close."""
        if self.recovery_thread and self.recovery_thread.isRunning():
            self.recovery_thread.stop()
            self.recovery_thread.wait()
        event.accept()


class MultiFilePreviewDialog(QDialog):
    """Dialog for previewing multiple recovered files in a standardized table format."""
    
    def __init__(self, files: List[RecoveredFile], parent=None):
        super().__init__(parent)
        self.files = files
        self.setup_ui()
        
    def setup_ui(self):
        file_count = len(self.files)
        if file_count == 1:
            self.setWindowTitle(f"📄 Preview: {self.files[0].name}")
        else:
            self.setWindowTitle(f"📄 Preview: {file_count} Selected Files")
        
        # Adaptive dialog size
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Larger dialog for multiple files
            dialog_width = max(800, min(1200, int(screen_width * 0.7)))
            dialog_height = max(600, min(900, int(screen_height * 0.8)))
            
            self.resize(dialog_width, dialog_height)
        else:
            self.resize(1000, 750)
            
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Summary info
        summary_layout = QVBoxLayout()
        
        if file_count == 1:
            file_icon = self._get_file_icon(self.files[0].file_type)
            title_text = f"{file_icon} {self.files[0].name}"
        else:
            title_text = f"📁 {file_count} Files Selected for Preview"
            
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2E86AB; margin-bottom: 5px;")
        summary_layout.addWidget(title_label)
        
        # Calculate summary stats
        total_size = sum(f.size for f in self.files)
        avg_quality = sum(f.quality for f in self.files) / len(self.files) if self.files else 0
        file_types = len(set(f.file_type.lower() for f in self.files))
        recoverable_count = sum(1 for f in self.files if f.recoverable)
        
        stats_text = (f"📊 Summary: {file_count} files, "
                     f"{self._format_file_size(total_size)} total, "
                     f"{avg_quality*100:.1f}% avg quality, "
                     f"{file_types} different types, "
                     f"{recoverable_count} recoverable")
        
        stats_label = QLabel(stats_text)
        stats_label.setStyleSheet("color: #666; font-size: 14px;")
        summary_layout.addWidget(stats_label)
        
        header_layout.addLayout(summary_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        layout.addWidget(separator)
        
        # Main content with tabs for single vs multiple files
        if file_count == 1:
            self._setup_single_file_view(layout, self.files[0])
        else:
            self._setup_multi_file_table(layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if file_count > 1:
            export_btn = QPushButton("📋 Export List")
            export_btn.clicked.connect(self.export_file_list)
            button_layout.addWidget(export_btn)
        
        close_btn = QPushButton("✅ Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setDefault(True)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _setup_single_file_view(self, layout, file_info):
        """Setup detailed view for single file (existing functionality)."""
        # File details table
        details_label = QLabel("📋 File Details")
        details_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(details_label)
        
        details_table = QTableWidget(0, 2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])
        details_table.horizontalHeader().setStretchLastSection(True)
        details_table.setAlternatingRowColors(True)
        details_table.setEditTriggers(QTableWidget.NoEditTriggers)
        details_table.setMaximumHeight(200)
        
        # Add file properties
        properties = [
            ("Full Path", file_info.path),
            ("File Type", file_info.file_type.upper()),
            ("Size", self._format_file_size(file_info.size)),
            ("Recovery Quality", f"{file_info.quality * 100:.1f}%"),
            ("Recoverable", "✅ Yes" if file_info.recoverable else "❌ No"),
        ]
        
        if file_info.signature:
            properties.append(("Signature", file_info.signature.description))
            properties.append(("MIME Type", file_info.signature.mime_type))
        
        if file_info.created_time:
            import datetime
            created = datetime.datetime.fromtimestamp(file_info.created_time)
            properties.append(("Created", created.strftime("%Y-%m-%d %H:%M:%S")))
            
        if file_info.modified_time:
            import datetime
            modified = datetime.datetime.fromtimestamp(file_info.modified_time)
            properties.append(("Modified", modified.strftime("%Y-%m-%d %H:%M:%S")))
        
        for prop, value in properties:
            row = details_table.rowCount()
            details_table.insertRow(row)
            details_table.setItem(row, 0, QTableWidgetItem(prop))
            details_table.setItem(row, 1, QTableWidgetItem(str(value)))
        
        layout.addWidget(details_table)
        
        # Content preview section
        preview_content = self._get_preview_content(file_info)
        if preview_content:
            preview_label = QLabel("🐱 Content Preview")
            preview_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(preview_label)
            
            preview_text = QTextEdit()
            preview_text.setPlainText(preview_content)
            preview_text.setReadOnly(True)
            preview_text.setMaximumHeight(250)
            preview_text.setFont(QFont("Courier", 10))
            layout.addWidget(preview_text)
        else:
            no_preview_label = QLabel("🚫 Content preview not available for this file type")
            no_preview_label.setStyleSheet("color: #888; font-style: italic; margin: 20px;")
            layout.addWidget(no_preview_label)
    
    def _setup_multi_file_table(self, layout):
        """Setup table view for multiple files."""
        table_label = QLabel("📋 File Details Table")
        table_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(table_label)
        
        # Create comprehensive table
        table = QTableWidget()
        headers = ["📁 Name", "📄 Type", "📏 Size", "⭐ Quality", "🔧 Recoverable", "📅 Path", "🐱 Preview"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(self.files))
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # Populate table
        for row, file_info in enumerate(self.files):
            # File name with icon
            name_item = QTableWidgetItem(f"{self._get_file_icon(file_info.file_type)} {file_info.name}")
            table.setItem(row, 0, name_item)
            
            # File type
            type_item = QTableWidgetItem(file_info.file_type.upper())
            table.setItem(row, 1, type_item)
            
            # File size
            size_item = QTableWidgetItem(self._format_file_size(file_info.size))
            table.setItem(row, 2, size_item)
            
            # Quality with color coding
            quality_item = QTableWidgetItem(f"{file_info.quality * 100:.1f}%")
            if file_info.quality >= 0.8:
                quality_item.setForeground(QColor("#51cf66"))  # Green
            elif file_info.quality >= 0.5:
                quality_item.setForeground(QColor("#fab005"))  # Yellow
            else:
                quality_item.setForeground(QColor("#fa5252"))  # Red
            table.setItem(row, 3, quality_item)
            
            # Recoverable status
            recoverable_item = QTableWidgetItem("✅ Yes" if file_info.recoverable else "❌ No")
            if file_info.recoverable:
                recoverable_item.setForeground(QColor("#51cf66"))
            else:
                recoverable_item.setForeground(QColor("#fa5252"))
            table.setItem(row, 4, recoverable_item)
            
            # File path (truncated for display)
            path_display = file_info.path
            if len(path_display) > 50:
                path_display = "..." + path_display[-47:]
            path_item = QTableWidgetItem(path_display)
            path_item.setToolTip(file_info.path)  # Full path on hover
            table.setItem(row, 5, path_item)
            
            # Preview availability
            has_preview = self._has_preview_content(file_info)
            preview_item = QTableWidgetItem("🐱 Available" if has_preview else "🚫 No preview")
            if has_preview:
                preview_item.setForeground(QColor("#2E86AB"))
            else:
                preview_item.setForeground(QColor("#888"))
            table.setItem(row, 6, preview_item)
        
        # Resize columns to content
        table.resizeColumnsToContents()
        
        # Set minimum column widths
        table.setColumnWidth(0, max(200, table.columnWidth(0)))  # Name
        table.setColumnWidth(1, 80)   # Type
        table.setColumnWidth(2, 100)  # Size  
        table.setColumnWidth(3, 80)   # Quality
        table.setColumnWidth(4, 100)  # Recoverable
        table.setColumnWidth(5, 250)  # Path
        table.setColumnWidth(6, 120)  # Preview
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        layout.addWidget(table)
        
        # Add double-click handler for detailed view
        table.doubleClicked.connect(lambda index: self._show_detailed_view(self.files[index.row()]))
        
        # Info label
        info_label = QLabel("💡 Double-click any row to see detailed preview of that file")
        info_label.setStyleSheet("color: #666; font-style: italic; margin: 5px;")
        layout.addWidget(info_label)
    
    def _show_detailed_view(self, file_info):
        """Show detailed view for a specific file."""
        detailed_dialog = MultiFilePreviewDialog([file_info], self)
        detailed_dialog.exec()
    
    def export_file_list(self):
        """Export file list to CSV."""
        try:
            from PySide6.QtWidgets import QFileDialog
            import csv
            from datetime import datetime
            
            # Get save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"oopsie_daisy_preview_{timestamp}.csv"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save File List", default_name,
                "CSV files (*.csv);;All files (*.*)"
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow([
                    'Name', 'Type', 'Size (bytes)', 'Size (formatted)', 'Quality (%)', 
                    'Recoverable', 'Path', 'Has Preview', 'Created', 'Modified'
                ])
                
                # Write file data
                for file_info in self.files:
                    created_str = ""
                    modified_str = ""
                    
                    if file_info.created_time:
                        created_str = datetime.fromtimestamp(file_info.created_time).strftime("%Y-%m-%d %H:%M:%S")
                    if file_info.modified_time:
                        modified_str = datetime.fromtimestamp(file_info.modified_time).strftime("%Y-%m-%d %H:%M:%S")
                    
                    writer.writerow([
                        file_info.name,
                        file_info.file_type.upper(),
                        file_info.size,
                        self._format_file_size(file_info.size),
                        f"{file_info.quality * 100:.1f}",
                        "Yes" if file_info.recoverable else "No",
                        file_info.path,
                        "Yes" if self._has_preview_content(file_info) else "No",
                        created_str,
                        modified_str
                    ])
            
            QMessageBox.information(self, "Export Complete", f"File list exported to:\n{file_path}")
            
        except Exception as e:
            QMessageBox.warning(self, "Export Error", f"Failed to export file list:\n{str(e)}")
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get emoji icon for file type."""
        icons = {
            'txt': '📝', 'doc': '📝', 'docx': '📝', 'rtf': '📝',
            'pdf': '📄', 'html': '🌐', 'htm': '🌐',
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️', 'ico': '🖼️', 'svg': '🖼️',
            'xls': '📊', 'xlsx': '📊', 'csv': '📊', 'ods': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦',
            'exe': '⚙️', 'msi': '⚙️', 'dll': '⚙️',
            'sqlite': '🗃️', 'db': '🗃️', 'pst': '📧'
        }
        return icons.get(file_type.lower(), '📄')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _get_preview_content(self, file_info) -> Optional[str]:
        """Get preview content for the file."""
        try:
            file_path = Path(file_info.path)
            if not file_path.exists():
                return "⚠️ File not accessible for preview (may be deleted or in unallocated space)"
            
            # Text files
            if file_info.file_type.lower() in ['txt', 'log', 'ini', 'cfg', 'conf']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # First 1000 characters
                        if len(content) == 1000:
                            content += "\n\n... (file continues)"
                        return content
                except Exception:
                    return "❌ Unable to read file content"
            
            # Image files - show basic info
            elif file_info.file_type.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return f"🖼️ Image file\nFormat: {file_info.file_type.upper()}\nSize: {self._format_file_size(file_info.size)}\n\n💡 Use an image viewer to see the actual image after recovery."
            
            # PDF files
            elif file_info.file_type.lower() == 'pdf':
                return f"📄 PDF Document\nSize: {self._format_file_size(file_info.size)}\n\n💡 Use a PDF viewer to read the document after recovery."
            
            # Archive files
            elif file_info.file_type.lower() in ['zip', 'rar', '7z', 'tar']:
                return f"📦 Archive file\nFormat: {file_info.file_type.upper()}\nSize: {self._format_file_size(file_info.size)}\n\n💡 Extract the archive after recovery to access its contents."
            
            # Media files
            elif file_info.file_type.lower() in ['mp3', 'wav', 'flac', 'mp4', 'avi', 'mov']:
                media_type = "🎵 Audio" if file_info.file_type.lower() in ['mp3', 'wav', 'flac'] else "🎬 Video"
                return f"{media_type} file\nFormat: {file_info.file_type.upper()}\nSize: {self._format_file_size(file_info.size)}\n\n💡 Use a media player to play the file after recovery."
            
            else:
                return f"📁 {file_info.file_type.upper()} file\nSize: {self._format_file_size(file_info.size)}\n\n💡 File preview not available for this format."
                
        except Exception as e:
            return f"❌ Error generating preview: {str(e)}"
    
    def _has_preview_content(self, file_info) -> bool:
        """Check if file has preview content available."""
        try:
            file_path = Path(file_info.path)
            if not file_path.exists():
                return False
            
            # Text files have preview
            if file_info.file_type.lower() in ['txt', 'log', 'ini', 'cfg', 'conf']:
                return True
                
            # All other file types have basic info preview
            return True
            
        except Exception:
            return False


class FilePreviewDialog(QDialog):
    """Dialog for previewing recovered file information and content."""
    
    def __init__(self, file_info: RecoveredFile, parent=None):
        super().__init__(parent)
        self.file_info = file_info
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle(f"📄 Preview: {self.file_info.name}")
        
        # Adaptive dialog size
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Scale dialog size to screen (larger than recovery dialog)
            dialog_width = max(600, min(800, int(screen_width * 0.5)))
            dialog_height = max(500, min(700, int(screen_height * 0.6)))
            
            self.resize(dialog_width, dialog_height)
        else:
            self.resize(700, 600)
            
        self.setModal(True)
        
        layout = QVBoxLayout(self)
        
        # Header with file icon and name
        header_layout = QHBoxLayout()
        
        # File icon based on type
        file_icon = self._get_file_icon(self.file_info.file_type)
        icon_label = QLabel(file_icon)
        icon_label.setStyleSheet("font-size: 48px;")
        header_layout.addWidget(icon_label)
        
        # File name and basic info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.file_info.name)
        name_label.setFont(QFont("Arial", 16, QFont.Bold))
        name_label.setStyleSheet("color: #2E86AB;")
        info_layout.addWidget(name_label)
        
        type_label = QLabel(f"Type: {self.file_info.file_type.upper()}")
        type_label.setStyleSheet("color: #666; font-size: 14px;")
        info_layout.addWidget(type_label)
        
        size_label = QLabel(f"Size: {self._format_file_size(self.file_info.size)}")
        size_label.setStyleSheet("color: #666; font-size: 14px;")
        info_layout.addWidget(size_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameStyle(QFrame.HLine | QFrame.Sunken)
        layout.addWidget(separator)
        
        # File details table
        details_label = QLabel("📋 File Details")
        details_label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(details_label)
        
        details_table = QTableWidget(0, 2)
        details_table.setHorizontalHeaderLabels(["Property", "Value"])
        details_table.horizontalHeader().setStretchLastSection(True)
        details_table.setAlternatingRowColors(True)
        details_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add file properties
        properties = [
            ("Full Path", self.file_info.path),
            ("File Type", self.file_info.file_type.upper()),
            ("Size", self._format_file_size(self.file_info.size)),
            ("Recovery Quality", f"{self.file_info.quality * 100:.1f}%"),
            ("Recoverable", "Yes" if self.file_info.recoverable else "No"),
            ("Preview Available", "Yes" if self.file_info.preview_available else "No"),
        ]
        
        if self.file_info.signature:
            properties.append(("Signature", self.file_info.signature.description))
            properties.append(("MIME Type", self.file_info.signature.mime_type))
        
        if self.file_info.created_time:
            import datetime
            created = datetime.datetime.fromtimestamp(self.file_info.created_time)
            properties.append(("Created", created.strftime("%Y-%m-%d %H:%M:%S")))
            
        if self.file_info.modified_time:
            import datetime
            modified = datetime.datetime.fromtimestamp(self.file_info.modified_time)
            properties.append(("Modified", modified.strftime("%Y-%m-%d %H:%M:%S")))
            
        if self.file_info.deleted_time:
            import datetime
            deleted = datetime.datetime.fromtimestamp(self.file_info.deleted_time)
            properties.append(("Deleted", deleted.strftime("%Y-%m-%d %H:%M:%S")))
        
        details_table.setRowCount(len(properties))
        for i, (prop, value) in enumerate(properties):
            details_table.setItem(i, 0, QTableWidgetItem(prop))
            details_table.setItem(i, 1, QTableWidgetItem(str(value)))
        
        layout.addWidget(details_table)
        
        # Content preview section
        if self.file_info.preview_available:
            preview_label = QLabel("🐱 Content Preview")
            preview_label.setFont(QFont("Arial", 14, QFont.Bold))
            layout.addWidget(preview_label)
            
            preview_content = self._get_preview_content()
            if preview_content:
                preview_scroll = QScrollArea()
                preview_widget = QWidget()
                preview_layout = QVBoxLayout(preview_widget)
                
                preview_text = QLabel(preview_content)
                preview_text.setWordWrap(True)
                preview_text.setStyleSheet("""
                    QLabel {
                        background: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 4px;
                        padding: 12px;
                        font-family: 'Consolas', 'Monaco', monospace;
                        font-size: 12px;
                    }
                """)
                preview_layout.addWidget(preview_text)
                
                preview_scroll.setWidget(preview_widget)
                preview_scroll.setMaximumHeight(200)
                layout.addWidget(preview_scroll)
        else:
            no_preview_label = QLabel("🚫 Preview not available for this file type")
            no_preview_label.setStyleSheet("color: #888; font-style: italic; padding: 20px;")
            no_preview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(no_preview_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        if self.file_info.recoverable:
            recover_btn = QPushButton("💾 Recover This File")
            recover_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #51cf66, stop:1 #37b24d);
                    border: none;
                    border-radius: 6px;
                    color: white;
                    font-weight: bold;
                    padding: 10px 20px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #69db7c, stop:1 #51cf66);
                }
            """)
            recover_btn.clicked.connect(self.recover_single_file)
            button_layout.addWidget(recover_btn)
        
        close_btn = QPushButton("✖️ Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get appropriate emoji icon for file type."""
        icons = {
            'jpg': '🖼️', 'jpeg': '🖼️', 'png': '🖼️', 'gif': '🖼️', 'bmp': '🖼️', 'webp': '🖼️', 'tiff': '🖼️',
            'pdf': '📄', 'doc': '📝', 'docx': '📝', 'txt': '📄', 'rtf': '📝',
            'xls': '📊', 'xlsx': '📊', 'csv': '📊',
            'ppt': '📽️', 'pptx': '📽️',
            'mp3': '🎵', 'wav': '🎵', 'flac': '🎵', 'aac': '🎵',
            'mp4': '🎬', 'avi': '🎬', 'mov': '🎬', 'mkv': '🎬',
            'zip': '📦', 'rar': '📦', '7z': '📦', 'tar': '📦',
            'exe': '⚙️', 'msi': '⚙️', 'dll': '⚙️',
            'sqlite': '🗃️', 'db': '🗃️', 'pst': '📧'
        }
        return icons.get(file_type.lower(), '📄')
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human readable format."""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def _get_preview_content(self) -> Optional[str]:
        """Get preview content for the file."""
        try:
            file_path = Path(self.file_info.path)
            if not file_path.exists():
                return "⚠️ File not accessible for preview (may be deleted or in unallocated space)"
            
            # Text files
            if self.file_info.file_type.lower() in ['txt', 'log', 'ini', 'cfg', 'conf']:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read(1000)  # First 1000 characters
                        if len(content) == 1000:
                            content += "\n\n... (file continues)"
                        return content
                except Exception:
                    return "❌ Unable to read file content"
            
            # Image files - show basic info
            elif self.file_info.file_type.lower() in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']:
                return f"🖼️ Image file\nFormat: {self.file_info.file_type.upper()}\nSize: {self._format_file_size(self.file_info.size)}\n\n💡 Use an image viewer to see the actual image after recovery."
            
            # PDF files
            elif self.file_info.file_type.lower() == 'pdf':
                return f"📄 PDF Document\nSize: {self._format_file_size(self.file_info.size)}\n\n💡 Use a PDF viewer to read the document after recovery."
            
            # Archive files
            elif self.file_info.file_type.lower() in ['zip', 'rar', '7z', 'tar']:
                return f"📦 Archive file\nFormat: {self.file_info.file_type.upper()}\nSize: {self._format_file_size(self.file_info.size)}\n\n💡 Extract the archive after recovery to access its contents."
            
            # Media files
            elif self.file_info.file_type.lower() in ['mp3', 'wav', 'flac', 'mp4', 'avi', 'mov']:
                media_type = "🎵 Audio" if self.file_info.file_type.lower() in ['mp3', 'wav', 'flac'] else "🎬 Video"
                return f"{media_type} file\nFormat: {self.file_info.file_type.upper()}\nSize: {self._format_file_size(self.file_info.size)}\n\n💡 Use a media player to play the file after recovery."
            
            else:
                return f"📁 {self.file_info.file_type.upper()} file\nSize: {self._format_file_size(self.file_info.size)}\n\n💡 File preview not available for this format."
                
        except Exception as e:
            return f"❌ Error generating preview: {str(e)}"
    
    def recover_single_file(self):
        """Recover just this single file."""
        # Create default recovery directory name with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_folder_name = f"oopsie-daisy-recovery_{timestamp}"
        
        # Try to use Downloads folder first, fall back gracefully
        possible_base_paths = [
            Path.home() / "Downloads",
            Path.home() / "Desktop", 
            Path.home() / "Documents",
            Path.home()  # Final fallback
        ]
        
        default_base_path = None
        for base_path in possible_base_paths:
            if base_path.exists() and base_path.is_dir():
                default_base_path = base_path
                break
                
        if not default_base_path:
            # Create Downloads folder if none of the standard folders exist
            default_base_path = Path.home() / "Downloads"
            try:
                default_base_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                default_base_path = Path.home()  # Ultimate fallback to home
        
        default_recovery_path = default_base_path / default_folder_name
        
        # Ask user if they want to use default location or choose custom
        reply = QMessageBox.question(
            self, 
            "📁 Choose Recovery Location",
            f"Where would you like to save '{self.file_info.name}'?\n\n"
            f"🎯 Recommended (Default):\n{default_recovery_path}\n\n"
            f"This creates an organized folder with timestamp so you can easily find your file later.\n\n"
            f"Choose 'Yes' for recommended location, or 'No' to select a custom directory.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Cancel:
            return
        elif reply == QMessageBox.Yes:
            # Use default location
            output_dir = str(default_recovery_path)
            # Create the directory
            try:
                default_recovery_path.mkdir(parents=True, exist_ok=True)
                QMessageBox.information(
                    self,
                    "📂 Recovery Folder Created", 
                    f"Recovery folder created:\n{output_dir}\n\nYour file will be recovered to this organized location!"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "⚠️ Folder Creation Failed",
                    f"Could not create default folder:\n{e}\n\nPlease choose a custom location."
                )
                # Fall back to custom selection
                reply = QMessageBox.No
        
        if reply == QMessageBox.No:
            # Let user choose custom directory
            output_dir = QFileDialog.getExistingDirectory(
                self, 
                "🗂️ Select Custom Recovery Directory",
                str(default_base_path),
                QFileDialog.ShowDirsOnly
            )
        
        if not output_dir:
            return  # User cancelled
        
        # Create and show progress dialog for single file
        recovery_dialog = FileRecoveryDialog(self)
        
        # Get the engine from parent
        engine = None
        parent = self.parent()
        while parent and not hasattr(parent, 'engine'):
            parent = parent.parent()
        if parent and hasattr(parent, 'engine'):
            engine = parent.engine
        else:
            engine = AdvancedRecoveryEngine()
        
        recovery_dialog.start_recovery(engine, [self.file_info], output_dir)
        recovery_dialog.exec()


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
        self.hardware_monitor = ScanHardwareMonitor(self)
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
        
        # Scan start info section
        scan_start_group = QGroupBox("🚀 Scan Started")
        scan_start_layout = QVBoxLayout(scan_start_group)
        
        self.scan_start_time_label = QLabel("Not started")
        self.scan_start_stats_label = QLabel("Initial hardware stats will appear here")
        self.scan_start_stats_label.setStyleSheet("color: #888; font-size: 11px;")
        self.scan_start_stats_label.setWordWrap(True)
        
        scan_start_layout.addWidget(self.scan_start_time_label)
        scan_start_layout.addWidget(self.scan_start_stats_label)
        
        layout.addWidget(scan_start_group)
        
        # Hardware monitoring section
        hardware_group = QGroupBox("🖥️ Hardware Performance")
        hardware_layout = QGridLayout(hardware_group)
        
        # CPU monitoring
        self.cpu_usage_label = QLabel("CPU: 0%")
        self.cpu_temp_label = QLabel("0°C")
        
        # GPU monitoring - will be populated dynamically
        self.gpu_labels = []  # Will hold list of GPU display widgets
        
        # Memory monitoring
        self.memory_usage_label = QLabel("RAM: 0%")
        
        hardware_layout.addWidget(QLabel("🔧"), 0, 0)
        hardware_layout.addWidget(self.cpu_usage_label, 0, 1)
        hardware_layout.addWidget(self.cpu_temp_label, 0, 2)
        
        # GPU section starts at row 1 - will be expanded dynamically
        self.gpu_start_row = 1
        
        # Memory at the bottom - will be moved down as GPUs are added
        self.memory_row = 2  # Will be updated dynamically
        hardware_layout.addWidget(QLabel("💾"), self.memory_row, 0)
        hardware_layout.addWidget(self.memory_usage_label, self.memory_row, 1)
        
        # Store layout reference for dynamic updates
        self.hardware_layout = hardware_layout
        
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
        from datetime import datetime
        
        self.start_time = time.time()
        self.timer.start(1000)  # Update every second
        
        # Update scan start info
        start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scan_start_time_label.setText(f"Started at: {start_datetime}")
        
        # Start hardware monitoring and connect signal
        self.hardware_monitor.stats_updated.connect(self.update_hardware_display)
        self.hardware_monitor.start_scan_monitoring()
        
        # Get initial hardware stats after a brief delay to let monitoring start
        QTimer.singleShot(500, self._capture_initial_stats)
    
    def _capture_initial_stats(self):
        """Capture initial hardware stats when scan starts."""
        try:
            initial_stats = self.hardware_monitor.get_current_stats()
            
            # Format initial stats text
            cpu_percent = initial_stats.get('cpu_percent', 0.0)
            cpu_temp = initial_stats.get('cpu_temp', 0.0)
            memory_percent = initial_stats.get('memory_percent', 0.0)
            gpu_list = initial_stats.get('gpus', [])
            
            stats_text = f"Initial stats: CPU {cpu_percent:.1f}%, RAM {memory_percent:.1f}%"
            
            # Add GPU information for all GPUs
            if gpu_list:
                gpu_info_parts = []
                for i, gpu in enumerate(gpu_list):
                    gpu_name = gpu.get('name', f'GPU{i}')[:8]  # Short name
                    gpu_usage = gpu.get('usage', 0.0)
                    gpu_info_parts.append(f"{gpu_name} {gpu_usage:.1f}%")
                
                if gpu_info_parts:
                    stats_text += f", GPUs: {', '.join(gpu_info_parts)}"
            else:
                stats_text += ", GPUs: None detected"
            
            # Add temperatures
            if cpu_temp > 0:
                stats_text += f", CPU temp {cpu_temp:.1f}°C"
                
            gpu_temps = [f"{gpu.get('name', f'GPU{i}')[:8]} {gpu.get('temp', 0.0):.1f}°C" 
                        for i, gpu in enumerate(gpu_list) if gpu.get('temp', 0.0) > 0]
            if gpu_temps:
                stats_text += f", GPU temps: {', '.join(gpu_temps)}"
                
            self.scan_start_stats_label.setText(stats_text)
            
        except Exception as e:
            print(f"Error capturing initial stats: {e}")
            self.scan_start_stats_label.setText("Initial stats: Unable to capture")
        
    def stop_scan(self):
        """Stop the scan timer and hardware monitoring."""
        self.timer.stop()
        self.hardware_monitor.stop_monitoring()
        
    def update_progress(self, progress: int, status: str):
        """Update progress display."""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status)
        
        # Calculate and update ETA
        if self.start_time and progress > 0:
            import time
            elapsed = time.time() - self.start_time
            if progress < 100:
                # Estimate remaining time based on current progress
                estimated_total_time = elapsed * (100 / progress)
                remaining_time = estimated_total_time - elapsed
                
                if remaining_time > 0:
                    remaining_minutes = int(remaining_time // 60)
                    remaining_seconds = int(remaining_time % 60)
                    self.remaining_label.setText(f"Remaining: {remaining_minutes}:{remaining_seconds:02d}")
                else:
                    self.remaining_label.setText("Remaining: Nearly done")
            else:
                self.remaining_label.setText("Remaining: Complete")
        
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
            
            # Update GPU stats - handle multiple GPUs
            gpu_list = stats.get('gpus', [])
            self._update_gpu_display(gpu_list)
            
            # Update memory stats
            memory_percent = stats.get('memory_percent', 0.0)
            self.memory_usage_label.setText(f"RAM: {memory_percent:.1f}%")
            
        except Exception as e:
            print(f"Hardware display update error: {e}")
    
    def _update_gpu_display(self, gpu_list):
        """Update display for all GPUs."""
        try:
            # If we have a different number of GPUs, recreate the display
            if len(self.gpu_labels) != len(gpu_list):
                self._recreate_gpu_display(gpu_list)
            
            # Update each GPU's stats
            for i, gpu_info in enumerate(gpu_list):
                if i < len(self.gpu_labels):
                    usage_label, temp_label = self.gpu_labels[i]
                    
                    # Update usage
                    gpu_name = gpu_info.get('name', f"GPU {i}")[:15]  # Limit length
                    gpu_usage = gpu_info.get('usage', 0.0)
                    usage_label.setText(f"{gpu_name}: {gpu_usage:.1f}%")
                    
                    # Update temperature
                    gpu_temp = gpu_info.get('temp', 0.0)
                    if gpu_temp > 0:
                        temp_color = self._get_temp_color(gpu_temp, 75, 90)
                        temp_label.setText(f"<span style='color: {temp_color}'>{gpu_temp:.1f}°C</span>")
                    else:
                        temp_label.setText("N/A")
                        
        except Exception as e:
            print(f"GPU display update error: {e}")
    
    def _recreate_gpu_display(self, gpu_list):
        """Recreate GPU display widgets for new GPU count."""
        try:
            # Remove existing GPU labels from layout
            for usage_label, temp_label in self.gpu_labels:
                self.hardware_layout.removeWidget(usage_label)
                self.hardware_layout.removeWidget(temp_label)
                usage_label.deleteLater()
                temp_label.deleteLater()
            
            # Remove existing GPU icons
            for row in range(self.gpu_start_row, self.memory_row):
                icon_item = self.hardware_layout.itemAtPosition(row, 0)
                if icon_item:
                    icon_widget = icon_item.widget()
                    if icon_widget:
                        self.hardware_layout.removeWidget(icon_widget)
                        icon_widget.deleteLater()
            
            self.gpu_labels.clear()
            
            # Create new GPU display widgets
            for i, gpu_info in enumerate(gpu_list):
                row = self.gpu_start_row + i
                
                # GPU icon
                gpu_icon = QLabel("🎮")
                self.hardware_layout.addWidget(gpu_icon, row, 0)
                
                # Usage label
                usage_label = QLabel(f"GPU {i}: 0%")
                self.hardware_layout.addWidget(usage_label, row, 1)
                
                # Temperature label
                temp_label = QLabel("0°C")
                self.hardware_layout.addWidget(temp_label, row, 2)
                
                self.gpu_labels.append((usage_label, temp_label))
            
            # Move memory row to bottom
            self.memory_row = self.gpu_start_row + len(gpu_list)
            
            # Remove existing memory widgets
            memory_icon_item = self.hardware_layout.itemAtPosition(2, 0)  # Old position
            if memory_icon_item:
                memory_icon = memory_icon_item.widget()
                if memory_icon:
                    self.hardware_layout.removeWidget(memory_icon)
                    self.hardware_layout.addWidget(memory_icon, self.memory_row, 0)
            
            self.hardware_layout.removeWidget(self.memory_usage_label)
            self.hardware_layout.addWidget(self.memory_usage_label, self.memory_row, 1)
                        
        except Exception as e:
            print(f"GPU display recreation error: {e}")
    
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
        
        preview_btn = QPushButton("🐱 Preview")
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
        """Preview the selected files with standardized table format."""
        selected = self.get_selected_files()
        if not selected:
            QMessageBox.warning(self, "No File Selected", "Please select one or more files to preview first.")
            return
        
        # Use new multi-file preview dialog (handles both single and multiple files)
        preview_dialog = MultiFilePreviewDialog(selected, self)
        preview_dialog.exec()
    
    def recover_selected_files(self):
        """Recover selected files with progress dialog."""
        selected = self.get_selected_files()
        if not selected:
            QMessageBox.warning(self, "No Files Selected", "Please select files to recover first.")
            return
        
        # Create default recovery directory name with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_folder_name = f"oopsie-daisy-recovery_{timestamp}"
        
        # Try to use Downloads folder first, fall back gracefully
        possible_base_paths = [
            Path.home() / "Downloads",
            Path.home() / "Desktop", 
            Path.home() / "Documents",
            Path.home()  # Final fallback
        ]
        
        default_base_path = None
        for base_path in possible_base_paths:
            if base_path.exists() and base_path.is_dir():
                default_base_path = base_path
                break
                
        if not default_base_path:
            # Create Downloads folder if none of the standard folders exist
            default_base_path = Path.home() / "Downloads"
            try:
                default_base_path.mkdir(parents=True, exist_ok=True)
            except Exception:
                default_base_path = Path.home()  # Ultimate fallback to home
        
        default_recovery_path = default_base_path / default_folder_name
        
        # Ask user if they want to use default location or choose custom
        reply = QMessageBox.question(
            self, 
            "📁 Choose Recovery Location",
            f"Where would you like to save the recovered files?\n\n"
            f"🎯 Recommended (Default):\n{default_recovery_path}\n\n"
            f"This creates an organized folder with timestamp so you can easily find your files later.\n\n"
            f"Choose 'Yes' for recommended location, or 'No' to select a custom directory.",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        if reply == QMessageBox.Cancel:
            return
        elif reply == QMessageBox.Yes:
            # Use default location
            output_dir = str(default_recovery_path)
            # Create the directory
            try:
                default_recovery_path.mkdir(parents=True, exist_ok=True)
                QMessageBox.information(
                    self,
                    "📂 Recovery Folder Created", 
                    f"Recovery folder created:\n{output_dir}\n\nYour files will be recovered to this organized location!"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "⚠️ Folder Creation Failed",
                    f"Could not create default folder:\n{e}\n\nPlease choose a custom location."
                )
                # Fall back to custom selection
                reply = QMessageBox.No
        
        if reply == QMessageBox.No:
            # Let user choose custom directory
            output_dir = QFileDialog.getExistingDirectory(
                self, 
                "🗂️ Select Custom Recovery Directory",
                str(default_base_path),
                QFileDialog.ShowDirsOnly
            )
        
        if not output_dir:
            return  # User cancelled
            
        # Create and show progress dialog
        recovery_dialog = FileRecoveryDialog(self)
        
        # Get the engine from parent wizard
        engine = None
        parent = self.parent()
        while parent and not hasattr(parent, 'engine'):
            parent = parent.parent()
        if parent and hasattr(parent, 'engine'):
            engine = parent.engine
        else:
            # Fallback - create new engine
            engine = AdvancedRecoveryEngine()
        
        recovery_dialog.start_recovery(engine, selected, output_dir)
        recovery_dialog.exec()


class RecoveryWizard(QWidget):
    """Main recovery wizard widget."""
    
    def __init__(self):
        super().__init__()
        self.engine = AdvancedRecoveryEngine()
        self.recovery_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("🐱 Oopsie Daisy - Advanced Recovery Wizard")
        
        # Get screen dimensions for adaptive sizing
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            screen_width = screen_geometry.width()
            screen_height = screen_geometry.height()
            
            # Adaptive minimum size
            min_width = min(800, int(screen_width * 0.6))
            min_height = min(600, int(screen_height * 0.65))
            self.setMinimumSize(min_width, min_height)
        else:
            self.setMinimumSize(800, 600)
        
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