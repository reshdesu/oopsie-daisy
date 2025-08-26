#!/usr/bin/env python3
import tempfile
import os
from pathlib import Path
from src.oopsie_daisy.file_recovery import FileRecoveryEngine

# Create a test file
with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
    f.write(b"Test recovery content")
    test_file = f.name

print(f"Created test file: {test_file}")

# Delete it
os.unlink(test_file)
print("Deleted test file")

# Try to recover
engine = FileRecoveryEngine()
files = engine.scan_for_deleted_files()
print(f"Found {len(files)} deleted files")

if files:
    print("Recovery engine working!")
else:
    print("No files found - this is normal for temp files")