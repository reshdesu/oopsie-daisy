#!/usr/bin/env python3
"""
Build script for creating distributable executables of Oopsie Daisy
Supports Windows (.exe), macOS (.app), and Linux (AppImage)
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller if not already installed"""
    try:
        import PyInstaller
        print("✅ PyInstaller already installed")
    except ImportError:
        print("📦 Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_spec_file():
    """Create PyInstaller spec file for better control"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/oopsie_daisy/__init__.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/oopsie_daisy/styles.py', 'oopsie_daisy'),
        ('README.md', '.'),
    ],
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui', 
        'PySide6.QtWidgets',
        'send2trash',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OopsieDaisy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if os.path.exists('assets/icon.ico') else None,
)
'''
    
    with open('oopsie_daisy.spec', 'w') as f:
        f.write(spec_content)
    print("✅ Created PyInstaller spec file")

def build_executable():
    """Build the executable using PyInstaller"""
    system = platform.system().lower()
    print(f"🏗️  Building for {system}...")
    
    # Build command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--clean",
        "--onefile",  # Single file executable
        "--windowed",  # No console window
        "--name", "OopsieDaisy",
        "--add-data", "src/oopsie_daisy/styles.py:oopsie_daisy",
        "--hidden-import", "PySide6.QtCore",
        "--hidden-import", "PySide6.QtGui", 
        "--hidden-import", "PySide6.QtWidgets",
        "--hidden-import", "send2trash",
        "src/oopsie_daisy/__init__.py"
    ]
    
    # Add icon if available
    if os.path.exists('assets/icon.ico'):
        cmd.extend(["--icon", "assets/icon.ico"])
    
    try:
        subprocess.check_call(cmd)
        print("✅ Build completed successfully!")
        
        # Show output location
        dist_dir = Path("dist")
        if system == "windows":
            exe_file = dist_dir / "OopsieDaisy.exe"
        else:
            exe_file = dist_dir / "OopsieDaisy"
            
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024 * 1024)
            print(f"📦 Executable created: {exe_file} ({size_mb:.1f} MB)")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False
    
    return True

def create_installer_script():
    """Create installer script for different platforms"""
    system = platform.system().lower()
    
    if system == "windows":
        # Create NSIS installer script
        nsis_script = '''
; Oopsie Daisy Installer Script
!define APPNAME "Oopsie Daisy"
!define COMPANYNAME "reshdesu"
!define DESCRIPTION "Cute kitten-themed file recovery tool"
!define VERSION "1.0.0"

Name "${APPNAME}"
OutFile "OopsieDaisy-Setup.exe"
InstallDir "$PROGRAMFILES\\${APPNAME}"

Page directory
Page instfiles

Section "install"
    SetOutPath $INSTDIR
    File "dist\\OopsieDaisy.exe"
    
    # Create desktop shortcut
    CreateShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\OopsieDaisy.exe"
    
    # Create start menu entry
    CreateDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    CreateShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\OopsieDaisy.exe"
    
    # Create uninstaller
    WriteUninstaller "$INSTDIR\\uninstall.exe"
SectionEnd

Section "uninstall"
    Delete "$INSTDIR\\OopsieDaisy.exe"
    Delete "$INSTDIR\\uninstall.exe"
    Delete "$DESKTOP\\${APPNAME}.lnk"
    Delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    RMDir "$INSTDIR"
    RMDir "$SMPROGRAMS\\${COMPANYNAME}"
SectionEnd
'''
        with open('installer.nsi', 'w') as f:
            f.write(nsis_script)
        print("✅ Created Windows installer script (installer.nsi)")
        print("💡 To create installer: Install NSIS and run 'makensis installer.nsi'")
    
    elif system == "darwin":  # macOS
        # Create .dmg creation script
        dmg_script = '''#!/bin/bash
# Create macOS DMG installer

APP_NAME="OopsieDaisy"
DMG_NAME="OopsieDaisy-Installer"
SOURCE_DIR="dist"
DMG_DIR="dmg_temp"

# Create temporary directory
mkdir -p "$DMG_DIR"

# Copy app bundle
cp -R "$SOURCE_DIR/$APP_NAME.app" "$DMG_DIR/"

# Create DMG
hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_DIR" -ov -format UDZO "$DMG_NAME.dmg"

# Clean up
rm -rf "$DMG_DIR"

echo "✅ Created $DMG_NAME.dmg"
'''
        with open('create_dmg.sh', 'w') as f:
            f.write(dmg_script)
        os.chmod('create_dmg.sh', 0o755)
        print("✅ Created macOS DMG script (create_dmg.sh)")

def main():
    print("🐱 Oopsie Daisy Build Script")
    print("=" * 40)
    
    # Install dependencies
    install_pyinstaller()
    
    # Build executable
    if build_executable():
        create_installer_script()
        print("\n🎉 Build process completed!")
        print("\nNext steps:")
        print("1. Test the executable in dist/ folder")
        print("2. Create installer using the generated scripts")
        print("3. Upload to GitHub Releases")
    else:
        print("\n❌ Build process failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()