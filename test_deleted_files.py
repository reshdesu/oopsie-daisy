#!/usr/bin/env python3
"""
Test script to demonstrate permanently deleted file detection.
"""

from pathlib import Path
from src.oopsie_daisy.advanced_recovery import AdvancedRecoveryEngine, RecoveryMode

def test_deleted_file_detection():
    """Test the deleted file detection functionality."""
    
    # Create recovery engine
    engine = AdvancedRecoveryEngine()
    
    # Get available drives
    drives = engine.get_available_drives()
    if not drives:
        print("❌ No drives found")
        return
    
    # Use the root drive
    root_drive = None
    for drive in drives:
        if drive['mountpoint'] == '/':
            root_drive = drive
            break
    
    if not root_drive:
        root_drive = drives[0]  # Use first available drive
    
    print(f"🔍 Testing deleted file detection on: {root_drive['device']} ({root_drive['mountpoint']})")
    
    def progress_callback(progress, status):
        print(f"  {progress}% - {status}")
    
    # Test deep scan which now includes permanently deleted file detection
    print("\n🚀 Starting deep scan with deleted file detection...")
    recovered_files = engine.scan_drive(root_drive, RecoveryMode.DEEP_SCAN, progress_callback)
    
    print(f"\n✅ Scan completed! Found {len(recovered_files)} potentially recoverable files:")
    
    # Group files by type
    file_types = {}
    for file_info in recovered_files:
        file_type = file_info.file_type
        if file_type not in file_types:
            file_types[file_type] = []
        file_types[file_type].append(file_info)
    
    # Display results
    for file_type, files in file_types.items():
        print(f"\n📁 {file_type.upper()} files ({len(files)}):")
        for file_info in files[:3]:  # Show first 3 of each type
            quality_stars = "⭐" * int(file_info.quality * 5)
            recoverable_status = "✅ Recoverable" if file_info.recoverable else "❌ Info Only"
            print(f"  • {file_info.name} ({file_info.size} bytes) {quality_stars} {recoverable_status}")
            if hasattr(file_info, 'deleted_time') and file_info.deleted_time:
                import time
                deleted_ago = int(time.time() - file_info.deleted_time)
                hours_ago = deleted_ago // 3600
                print(f"    Deleted approximately {hours_ago} hours ago")
        
        if len(files) > 3:
            print(f"  ... and {len(files) - 3} more files")

if __name__ == "__main__":
    test_deleted_file_detection()