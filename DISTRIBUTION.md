# 📦 Distribution Guide

This document explains how to create distributable executables for Oopsie Daisy.

## 🚀 Automatic Releases (Recommended)

The easiest way is using GitHub Actions:

1. **Create a version tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions will automatically:**
   - Build executables for Windows (.exe), macOS, and Linux
   - Create a GitHub Release with download links
   - Upload all executables as release assets

3. **Users can then download:**
   - Windows: `OopsieDaisy.exe` 
   - macOS: `OopsieDaisy` (Unix executable)
   - Linux: `OopsieDaisy` (Unix executable)

## 🛠️ Manual Building

### Prerequisites
```bash
# Install build dependencies
uv pip install pyinstaller

# For Windows icon support (optional)
uv pip install pillow
```

### Quick Build
```bash
# Run the build script
python build.py
```

This creates:
- `dist/OopsieDaisy.exe` (Windows)
- `dist/OopsieDaisy` (macOS/Linux)

### Advanced Building

#### Windows (.exe)
```bash
python -m PyInstaller \
  --clean --onefile --windowed \
  --name "OopsieDaisy" \
  --add-data "src/oopsie_daisy/styles.py;oopsie_daisy" \
  --hidden-import "PySide6.QtCore" \
  --hidden-import "PySide6.QtGui" \
  --hidden-import "PySide6.QtWidgets" \
  --hidden-import "send2trash" \
  --icon "assets/icon.ico" \
  src/oopsie_daisy/__init__.py
```

#### macOS (.app bundle)
```bash
python -m PyInstaller \
  --clean --onefile --windowed \
  --name "OopsieDaisy" \
  --add-data "src/oopsie_daisy/styles.py:oopsie_daisy" \
  --hidden-import "PySide6.QtCore" \
  --hidden-import "PySide6.QtGui" \
  --hidden-import "PySide6.QtWidgets" \
  --hidden-import "send2trash" \
  src/oopsie_daisy/__init__.py
```

#### Linux (executable)
```bash
python -m PyInstaller \
  --clean --onefile --windowed \
  --name "OopsieDaisy" \
  --add-data "src/oopsie_daisy/styles.py:oopsie_daisy" \
  --hidden-import "PySide6.QtCore" \
  --hidden-import "PySide6.QtGui" \
  --hidden-import "PySide6.QtWidgets" \
  --hidden-import "send2trash" \
  src/oopsie_daisy/__init__.py
```

## 📋 Distribution Checklist

### Before Building
- [ ] Update version in `pyproject.toml`
- [ ] Test app thoroughly: `uv run oopsie-daisy`
- [ ] Run tests: `uv run pytest tests/`
- [ ] Update `README.md` with new features
- [ ] Create/update `CHANGELOG.md`

### After Building
- [ ] Test executable on clean system (no Python installed)
- [ ] Verify file recovery functionality works
- [ ] Check starry sky animation displays correctly
- [ ] Test on different screen resolutions
- [ ] Scan executable with antivirus (some flag PyInstaller binaries)

### Release Process
- [ ] Create git tag: `git tag v1.0.0`
- [ ] Push tag: `git push origin v1.0.0`
- [ ] Wait for GitHub Actions to complete
- [ ] Test download links
- [ ] Announce release

## 🎯 User Instructions

Include these instructions for end users:

### Windows Users
1. Download `OopsieDaisy.exe`
2. Double-click to run
3. If Windows Defender warns, click "More info" → "Run anyway"

### macOS Users
1. Download `OopsieDaisy`
2. Double-click to run
3. If blocked, go to System Preferences → Security & Privacy → Allow

### Linux Users
1. Download `OopsieDaisy`
2. Make executable: `chmod +x OopsieDaisy`
3. Run: `./OopsieDaisy`

## 🔧 Troubleshooting

### Build Issues
- **Import errors**: Add missing modules to `--hidden-import`
- **File not found**: Check `--add-data` paths
- **Large file size**: Use `--exclude-module` for unused packages

### Runtime Issues
- **Qt platform plugin errors**: Include Qt platform plugins
- **Missing DLLs**: Use `--collect-all PySide6` for all dependencies

### Distribution Issues
- **Antivirus detection**: Submit to vendors as false positive
- **Slow startup**: PyInstaller creates temporary files on first run
- **macOS notarization**: Sign with Apple Developer certificate

## 📊 File Sizes (Approximate)

- Windows (.exe): 80-120 MB
- macOS (binary): 90-130 MB  
- Linux (binary): 85-125 MB

Large size is due to bundling Python interpreter and Qt framework.

## 🚀 Advanced: Custom Installers

### Windows (NSIS)
Use `installer.nsi` script created by `build.py`:
```bash
# Install NSIS, then:
makensis installer.nsi
# Creates OopsieDaisy-Setup.exe
```

### macOS (DMG)
Use `create_dmg.sh` script:
```bash
./create_dmg.sh
# Creates OopsieDaisy-Installer.dmg
```

### Linux (AppImage)
Consider creating AppImage for better Linux compatibility:
```bash
# Use tools like appimage-builder
```

---

**Need help?** Open an issue on GitHub! 🐱