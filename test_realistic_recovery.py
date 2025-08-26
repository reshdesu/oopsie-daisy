#!/usr/bin/env python3
import os
import tempfile
import shutil
from pathlib import Path
import send2trash
from src.oopsie_daisy.file_recovery import FileRecoveryEngine

def test_file_recovery():
    print("🧪 Starting realistic file recovery test...\n")
    
    # Create test files in common locations
    test_files = []
    
    # Create files in Downloads
    downloads_dir = Path.home() / "Downloads"
    if downloads_dir.exists():
        test_file1 = downloads_dir / "test_recovery_doc.txt"
        with open(test_file1, 'w') as f:
            f.write("This is a test document for recovery testing.")
        test_files.append(test_file1)
        print(f"✅ Created: {test_file1}")
    
    # Create file in Documents
    docs_dir = Path.home() / "Documents"
    if docs_dir.exists():
        test_file2 = docs_dir / "important_notes.txt"
        with open(test_file2, 'w') as f:
            f.write("Important notes that were accidentally deleted!")
        test_files.append(test_file2)
        print(f"✅ Created: {test_file2}")
    
    # Create file in Desktop
    desktop_dir = Path.home() / "Desktop"
    if desktop_dir.exists():
        test_file3 = desktop_dir / "project_backup.txt"
        with open(test_file3, 'w') as f:
            f.write("Project backup file content.")
        test_files.append(test_file3)
        print(f"✅ Created: {test_file3}")
    
    # Create temp file (different scenario)
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp', prefix='deleted_') as f:
        f.write(b"Temporary file that was deleted")
        temp_file = Path(f.name)
        test_files.append(temp_file)
        print(f"✅ Created: {temp_file}")
    
    print(f"\n📋 Created {len(test_files)} test files")
    
    # Delete files using send2trash (moves to trash)
    print("\n🗑️  Deleting files (moving to trash)...")
    for file_path in test_files:
        if file_path.exists():
            try:
                send2trash.send2trash(str(file_path))
                print(f"   Moved to trash: {file_path.name}")
            except Exception as e:
                # Fallback to direct deletion
                os.unlink(file_path)
                print(f"   Directly deleted: {file_path.name}")
    
    print("\n🔍 Now testing our file recovery engine...")
    
    # Test recovery engine
    engine = FileRecoveryEngine()
    found_files = engine.scan_for_deleted_files()
    
    print(f"\n📊 Recovery Results:")
    print(f"   Found {len(found_files)} deleted files")
    
    if found_files:
        print("\n📄 Files found:")
        for i, file_info in enumerate(found_files[:10], 1):  # Show first 10
            size = file_info.get('size', 'unknown')
            name = file_info.get('name', 'unnamed')
            path = file_info.get('path', 'unknown location')
            print(f"   {i}. {name} ({size} bytes) at {path}")
        
        if len(found_files) > 10:
            print(f"   ... and {len(found_files) - 10} more files")
    else:
        print("   ❌ No deleted files found")
        print("   This could mean:")
        print("   - Files were permanently deleted")
        print("   - System cleaned up trash automatically")
        print("   - Files are in locations we don't scan")
    
    # Test restore functionality with first found file
    if found_files:
        print(f"\n🔄 Testing restore functionality...")
        restore_dir = Path.home() / "Desktop" / "recovered_files"
        restore_dir.mkdir(exist_ok=True)
        
        success = engine.restore_file(found_files[0], str(restore_dir))
        if success:
            print(f"   ✅ Successfully restored file to {restore_dir}")
        else:
            print(f"   ❌ Failed to restore file")
    
    print(f"\n🏁 Test completed!")
    return len(found_files)

if __name__ == "__main__":
    found_count = test_file_recovery()
    print(f"\nSummary: Recovery engine found {found_count} deleted files")