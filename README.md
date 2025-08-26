# 🐱 Oopsie Daisy - File Recovery Tool

**A cute, kitten-themed file recovery application with pink aesthetics and twinkling starry sky, designed for users who have absolutely no coding experience!**

## 🌟 What is Oopsie Daisy?

Oopsie Daisy is a user-friendly file recovery tool that helps you find and restore accidentally deleted files. With its adorable kitten theme, pink color scheme, and beautiful starry night sky background, it makes the stressful experience of losing files a little more pleasant! 

**Perfect for non-technical users** - No command line knowledge required, no complex settings, just click and recover! 💕

## ✨ Features

- 🔍 **Easy Scanning**: One-click scanning for deleted files in trash and temp locations
- 💖 **Beautiful Interface**: Cute kitten-themed design with pink colors and twinkling stars
- 🌌 **Starry Sky Background**: Realistic twinkling stars covering the entire application
- 🖱️ **Point & Click**: No technical knowledge required
- 📁 **Multiple File Support**: Select and restore multiple files at once
- 🏠 **Choose Your Location**: Pick exactly where to restore your files
- ⚡ **Fast Recovery**: Quick scanning and restoration process
- 🛡️ **Safe**: Non-destructive recovery - your existing files are never touched

## 🚀 Quick Start

### Installation

**For Complete Beginners**:
1. Download the latest release 
2. Double-click to install
3. Launch "Oopsie Daisy" from your applications

**For Developers**:
```bash
git clone https://github.com/your-repo/oopsie-daisy.git
cd oopsie-daisy
uv sync
uv run oopsie-daisy
```

### Usage Guide

#### 🔍 **Finding Your Lost Files**

1. **Launch the App**: Open Oopsie Daisy (look for the cute kitten icon!)

2. **Start Scanning**: 
   - Click the **"Start Scan"** button in the pink sidebar
   - Don't worry - this is completely safe and won't change anything on your computer
   - The progress indicator will show that we're working hard to find your files!

3. **Wait Patiently**: 
   - Scanning can take 30 seconds to a few minutes depending on your system
   - Our virtual kittens search through trash and temporary file locations
   - Watch the beautiful twinkling stars while you wait!

#### 📄 **Reviewing Found Files**

4. **See Your Results**:
   - Found files appear in the main content area with names, sizes, and deletion info
   - Each file shows: 📄 filename (size bytes) - Deleted: date
   - The sidebar shows total count of files found

5. **Select Files to Recover**:
   - **Single file**: Click once on the file you want
   - **Multiple files**: Hold `Ctrl` (Windows/Linux) or `Cmd` (Mac) and click multiple files
   - **Range selection**: Click first file, then hold `Shift` and click the last file

#### 🔄 **Restoring Your Files**

6. **Restore Files**:
   - Click **"Restore Files"** in the sidebar
   - Choose where to restore your files (Desktop or Documents recommended)
   - A success message will confirm restoration

## 🆘 Troubleshooting

### "I don't see any deleted files!"

**Don't panic! Here's what might be happening:**

- Files might be permanently deleted (emptied from trash)
- Files in locations we don't scan yet
- System automatically cleaned temporary files

**What to try:**
- Run the scan again (sometimes files appear in recoverable locations later)
- Check your Trash/Recycle Bin manually first
- Look in Downloads folder manually

### Ubuntu/Linux Qt Issues

If you see Qt platform plugin errors:

```bash
# Install required libraries
sudo apt install -y libxcb-cursor0 libxcb-cursor-dev

# Set Qt platform
export QT_QPA_PLATFORM=xcb
uv run oopsie-daisy
```

### "Restore failed" or "Can't restore files"

**Solutions:**
- Try restoring to your Desktop instead
- Close other programs that might be using the files
- Run with administrator/elevated permissions

## 🔒 Privacy & Safety

**Your privacy matters to us!**

✅ **What we DO:**
- Scan only safe, common locations for deleted files (trash, temp directories)
- Work entirely on your local computer (no internet required)
- Create copies of your files (never move or delete anything)
- Show you exactly what we found before any action

❌ **What we DON'T:**
- Access your personal files without permission
- Send any data over the internet
- Modify or delete your existing files
- Install background services or trackers

## 🎨 Technical Details

- **Built with**: Python 3.12+, PySide6 (Qt for Python)
- **Package Manager**: uv (modern, fast Python package manager)  
- **Testing**: pytest with pytest-qt for UI testing
- **Cross-platform**: Windows, macOS, and Linux
- **File Recovery**: Scans trash/recycle bin and temporary file locations
- **UI Features**: Custom twinkling star animation, modern sidebar layout, pink kitten theme

## 🧪 Testing

### Test File Recovery
```bash
# Test the recovery engine
uv run python test_realistic_recovery.py

# Run full test suite
uv sync --extra test
uv run pytest tests/ -v
```

---

**Made with 💖 and lots of virtual kittens** 🐾✨