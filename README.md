# 🐱 Oopsie Daisy - Professional File Recovery Tool

**A powerful, cross-platform file recovery application with adorable kitten theme, advanced recovery capabilities, and comprehensive hardware monitoring - designed for both beginners and power users!**

[![Build Status](https://github.com/reshdesu/oopsie-daisy/actions/workflows/build-releases.yml/badge.svg)](https://github.com/reshdesu/oopsie-daisy/actions)
[![Test Coverage](https://github.com/reshdesu/oopsie-daisy/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/reshdesu/oopsie-daisy/actions)
[![Release](https://img.shields.io/github/v/release/reshdesu/oopsie-daisy)](https://github.com/reshdesu/oopsie-daisy/releases)

## 🌟 What Makes Oopsie Daisy Special?

Oopsie Daisy combines **professional-grade file recovery** with a **delightfully cute interface**. Unlike complex recovery tools that intimidate users, we make file recovery accessible while providing enterprise-level features under the hood.

**Perfect for everyone** - From complete beginners to tech professionals! 💖

### ✨ Why Choose Oopsie Daisy?

- 🎯 **Beginner-Friendly**: Point-and-click interface, no technical knowledge needed
- 🚀 **Professional Power**: Advanced recovery algorithms rivaling commercial tools
- 🌍 **True Cross-Platform**: Native support for Windows, macOS, and Linux
- 🎮 **GPU-Accelerated**: Utilizes AMD, NVIDIA, and Intel GPUs for faster scanning
- 🐱 **Stress-Free Experience**: Cute kitten theme makes recovery less stressful
- 🔒 **Privacy-First**: Everything runs locally, no data leaves your computer

## 🎯 Features Overview

### 🔍 **Advanced Recovery Engine**
- **Professional-Grade Recovery**: Signature-based file detection for 20+ file types
- **Deep Disk Scanning**: Recovers files from unallocated disk space
- **File System Support**: NTFS, ext4, FAT32, and more
- **GPU Acceleration**: Uses OpenCL for faster scanning on AMD/NVIDIA/Intel GPUs
- **Multi-Threading**: Utilizes all CPU cores for maximum performance
- **Quality Assessment**: Recovery confidence scoring for each file

### 🎨 **Beautiful Interface**
- **Starry Sky Theme**: Realistic twinkling stars covering the entire application
- **Kitten Icons**: Adorable 🐱 icons throughout the interface
- **Adaptive UI**: Automatically adjusts to your screen size
- **Modern Design**: Clean, professional layout with pink accent colors
- **Progress Tracking**: Real-time progress with ETA calculations

### 🖥️ **System Monitoring**
- **Real-Time Hardware Stats**: CPU usage, temperature, and memory monitoring
- **Multi-GPU Support**: Displays stats for all graphics cards (NVIDIA, AMD, Intel)
- **Cross-Platform Monitoring**: Works on Windows (WMI), macOS (powermetrics), Linux (sysfs)
- **Temperature Alerts**: Color-coded temperature warnings

### 📄 **Multi-File Preview System**
- **Standardized Table View**: Professional file browser with sortable columns
- **Bulk Preview**: Preview multiple files simultaneously
- **File Metadata**: Size, type, recovery quality, timestamps
- **Export to CSV**: Save file lists for documentation
- **Smart Filtering**: Find specific files quickly

### 🎯 **Recovery Wizard**
- **Step-by-Step Process**: Guided recovery workflow
- **Drive Selection**: Choose specific drives or partitions to scan
- **Recovery Modes**: Quick scan vs. deep recovery options
- **Organized Output**: Creates timestamped recovery folders automatically
- **Smart Defaults**: Uses Downloads folder with graceful fallbacks

## 🚀 Quick Start

### 📥 Download & Install

**For Everyone (Recommended)**:
1. Go to [Releases](https://github.com/reshdesu/oopsie-daisy/releases)
2. Download for your platform:
   - **Windows**: `OopsieDaisy.exe` 
   - **macOS**: `OopsieDaisy-macOS`
   - **Linux**: `OopsieDaisy-Linux`
3. Double-click to run!

**For Developers**:
```bash
git clone https://github.com/reshdesu/oopsie-daisy.git
cd oopsie-daisy
uv sync --extra gpu
uv run oopsie-daisy
```

### 🎮 Usage Guide

#### **Step 1: Launch & Select Drive** 🖱️
1. Open Oopsie Daisy (look for the kitten icon!)
2. Choose the drive/partition to scan
3. Watch the real-time hardware monitoring in the sidebar

#### **Step 2: Choose Recovery Mode** ⚙️
- **Quick Scan**: Fast recovery from trash and recent deletions
- **Deep Recovery**: Comprehensive scan of unallocated disk space
- GPU acceleration automatically detected and used

#### **Step 3: Monitor Progress** 📊
- Real-time progress with ETA calculations
- Hardware stats show CPU/GPU utilization
- Temperature monitoring ensures system health

#### **Step 4: Preview & Select Files** 👁️
- **🐱 Preview Button**: View files in standardized table
- **Multi-File Support**: Select individual files or entire groups  
- **Quality Indicators**: Green (>80%), Yellow (50-80%), Red (<50%)
- **Export Lists**: Save file inventories to CSV

#### **Step 5: Recover Files** 💾
- **Smart Defaults**: Automatically suggests `Downloads/oopsie-daisy-recovery_timestamp`
- **Custom Locations**: Choose any folder you prefer
- **Organized Output**: Files organized by type and timestamp
- **Progress Tracking**: Real-time recovery progress

## 🌍 Cross-Platform Excellence

### **Windows Support** 🪟
- **Hardware Monitoring**: WMI-based CPU temperature and GPU detection
- **Native Integration**: Uses Windows APIs for optimal performance
- **GPU Support**: NVIDIA (nvidia-smi), AMD (WMI), Intel (WMI)

### **macOS Support** 🍎
- **Apple Silicon Ready**: Full M1/M2/M3 support
- **System Integration**: Uses system_profiler and powermetrics
- **Metal GPU Support**: Detects Apple GPUs and discrete cards

### **Linux Support** 🐧
- **Full Feature Set**: Complete hardware monitoring via sysfs
- **Distribution Agnostic**: Works on Ubuntu, Fedora, Arch, etc.
- **GPU Variety**: NVIDIA, AMD, Intel integrated graphics

## 🧪 Quality Assurance

### **Zero Broken Releases** 🛡️
- **Quality Gates**: Releases only created if ALL tests pass
- **Multi-Platform Testing**: Builds tested on Windows, macOS, Linux
- **Automated CI/CD**: GitHub Actions with comprehensive testing

### **Test Coverage**
```bash
# Run full test suite
uv run pytest tests/ -v --cov=src/oopsie_daisy

# Cross-platform compatibility tests
uv run pytest tests/test_cross_platform.py -v

# Hardware monitoring tests
uv run pytest tests/test_hardware_monitor.py -v
```

### **Current Test Results**
- ✅ **7 Core Tests** covering essential functionality
- ✅ **Cross-Platform** verification for Windows/macOS/Linux
- ✅ **Hardware Monitor** platform detection testing
- ✅ **Import Validation** ensures all modules load correctly

## 📊 Technical Architecture

### **Core Technologies**
- **Python 3.12+**: Modern, fast, and secure
- **PySide6/Qt6**: Cross-platform GUI framework
- **OpenCL**: GPU acceleration for scanning
- **psutil**: System monitoring and hardware stats
- **uv**: Lightning-fast package management

### **Recovery Engine**
- **File Signatures**: Detects files by content, not filename
- **Supported Types**: Documents, images, videos, audio, archives, executables
- **Deep Scanning**: Searches unallocated disk space
- **Quality Scoring**: Confidence levels for each recovered file

### **Performance Optimizations**
- **Multi-Threading**: ThreadPoolExecutor for parallel processing
- **GPU Acceleration**: OpenCL kernels for pattern matching
- **Memory Efficient**: Streaming file operations
- **Progress Tracking**: Real-time updates without blocking UI

## 🔒 Privacy & Security

### **Privacy-First Design** 🛡️
✅ **What We Do:**
- Process everything locally on your computer
- Never send data over the internet
- Only scan user-approved locations
- Create copies (never modify originals)

❌ **What We Don't Do:**
- Access files without permission
- Send telemetry or usage data
- Install background services
- Modify existing files

### **Security Features**
- **Safe Recovery**: Non-destructive operations only
- **User Consent**: Explicit approval for all actions
- **Sandboxed**: Isolated recovery environment
- **Open Source**: Full code transparency

## 🛠️ Development & Contributing

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/reshdesu/oopsie-daisy.git
cd oopsie-daisy

# Install dependencies with GPU support
uv sync --extra test --extra gpu

# Run in development mode
uv run oopsie-daisy

# Run tests
uv run pytest tests/ -v

# Build executable
uv run python build.py
```

### **Contributing Guidelines**
1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Test** your changes (`uv run pytest`)
4. **Commit** with clear messages
5. **Push** to your branch
6. **Open** a Pull Request

### **Code Quality Standards**
- **Tests Required**: All new features must include tests
- **Cross-Platform**: Code must work on Windows, macOS, Linux
- **Documentation**: Update README and docstrings
- **Type Hints**: Use Python type annotations

## 🆘 Troubleshooting

### **Common Issues**

#### **"No files found" / Empty results**
- Try **Deep Recovery** mode instead of Quick Scan
- Ensure you're scanning the correct drive
- Files may be permanently overwritten (try immediately after deletion)

#### **GPU not detected**
- **Windows**: Install latest graphics drivers
- **Linux**: Install OpenCL runtime (`sudo apt install ocl-icd-opencl-dev`)
- **macOS**: Update to latest macOS version

#### **Qt/GUI Issues (Linux)**
```bash
# Install Qt dependencies
sudo apt update
sudo apt install -y libxcb-cursor0 libgl1-mesa-dev libegl1-mesa-dev

# Set Qt platform
export QT_QPA_PLATFORM=xcb
uv run oopsie-daisy
```

#### **Permission Errors**
- **Windows**: Run as Administrator
- **macOS**: Allow system access in Security & Privacy
- **Linux**: Ensure user has disk access permissions

### **Getting Help**
- 📖 **Documentation**: Check `CI_CD_PROCESS.md` and `CROSS_PLATFORM_TESTING.md`
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/reshdesu/oopsie-daisy/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/reshdesu/oopsie-daisy/discussions)

## 📈 Roadmap

### **Upcoming Features**
- [ ] **File Type Filters**: Preview by file type (images, documents, etc.)
- [ ] **Recovery History**: Track and replay previous recovery sessions
- [ ] **Batch Recovery**: Automated recovery rules and schedules
- [ ] **Advanced Filters**: Search by date, size, filename patterns
- [ ] **Cloud Integration**: Recover from cloud trash (Google Drive, etc.)
- [ ] **Mobile Companion**: iOS/Android app for remote monitoring

### **Performance Improvements**
- [ ] **Enhanced GPU Kernels**: More sophisticated OpenCL algorithms
- [ ] **Machine Learning**: AI-powered file type detection
- [ ] **Incremental Scanning**: Resume interrupted scans
- [ ] **Memory Optimization**: Handle larger drives efficiently

## 🏆 Acknowledgments

- **Qt/PySide6**: Excellent cross-platform GUI framework
- **OpenCL**: GPU computing standard enabling acceleration
- **pytest**: Robust testing framework ensuring quality
- **uv**: Modern Python packaging that makes development joy
- **GitHub Actions**: Reliable CI/CD platform

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with 💖, powered by 🐱 virtual kittens, and lots of ✨ twinkling stars!**

*Oopsie Daisy - Because losing files doesn't have to ruin your day!* 🌈