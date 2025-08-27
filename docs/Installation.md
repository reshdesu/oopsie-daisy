# 📥 Installation Guide

Complete installation instructions for all platforms.

## 🚀 Quick Installation (Recommended)

### **Windows 10/11**
1. **[Download OopsieDaisy.exe](https://github.com/reshdesu/oopsie-daisy/releases/latest)**
2. **Double-click to run** (see [[Windows SmartScreen]] if Windows warns you)
3. **Allow administrator access** when prompted (needed for deep file scanning)

### **macOS 12+**
1. **[Download OopsieDaisy-macOS](https://github.com/reshdesu/oopsie-daisy/releases/latest)**  
2. **Make executable**: `chmod +x OopsieDaisy-macOS`
3. **Run**: `./OopsieDaisy-macOS`
4. **Allow in Security & Privacy** if macOS blocks it

### **Linux (All Distributions)**
1. **[Download OopsieDaisy-Linux](https://github.com/reshdesu/oopsie-daisy/releases/latest)**
2. **Make executable**: `chmod +x OopsieDaisy-Linux` 
3. **Install dependencies** (see platform-specific sections below)
4. **Run**: `./OopsieDaisy-Linux`

## 🐧 Linux Distribution-Specific

### **Ubuntu/Debian**
```bash
# Install Qt dependencies
sudo apt update
sudo apt install -y libxcb-cursor0 libgl1-mesa-dev libegl1-mesa-dev

# For GPU acceleration (optional)
sudo apt install -y ocl-icd-opencl-dev

# Download and run
wget https://github.com/reshdesu/oopsie-daisy/releases/latest/download/OopsieDaisy-Linux
chmod +x OopsieDaisy-Linux
./OopsieDaisy-Linux
```

### **Fedora/RHEL/CentOS**
```bash
# Install Qt dependencies  
sudo dnf install -y qt6-qtbase mesa-libGL-devel mesa-libEGL-devel

# For GPU acceleration (optional)
sudo dnf install -y ocl-icd-devel

# Download and run
wget https://github.com/reshdesu/oopsie-daisy/releases/latest/download/OopsieDaisy-Linux
chmod +x OopsieDaisy-Linux
./OopsieDaisy-Linux
```

### **Arch Linux**
```bash
# Install Qt dependencies
sudo pacman -S qt6-base mesa opencl-icd-loader

# Download and run  
wget https://github.com/reshdesu/oopsie-daisy/releases/latest/download/OopsieDaisy-Linux
chmod +x OopsieDaisy-Linux
./OopsieDaisy-Linux
```

## 🛠️ Development Installation

For developers who want to build from source:

### **Prerequisites**
- **Python 3.12+**
- **uv package manager**: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### **Installation Steps**
```bash
# Clone repository
git clone https://github.com/reshdesu/oopsie-daisy.git
cd oopsie-daisy

# Install dependencies
uv sync --extra test --extra gpu

# Run from source
uv run oopsie-daisy

# Or build executable
uv run python -m PyInstaller oopsie_daisy.spec
```

## 🔧 System Requirements

### **Minimum Requirements**
- **RAM**: 2GB available memory
- **Storage**: 100MB for application + space for recovered files
- **CPU**: Any modern processor (GPU acceleration optional)

### **Recommended for Best Performance**
- **RAM**: 8GB+ for large file recovery
- **GPU**: Dedicated graphics card (NVIDIA/AMD/Intel) for GPU acceleration
- **Storage**: SSD for faster scanning and recovery

### **Supported Platforms**
- ✅ **Windows**: 10, 11 (x64)
- ✅ **macOS**: 12+ (Intel & Apple Silicon)
- ✅ **Linux**: Ubuntu 20.04+, Fedora 35+, Arch Linux, other modern distributions

## 🚨 Common Installation Issues

### **Windows SmartScreen Warning**
**Issue**: "Windows protected your PC" warning appears
**Solution**: See our detailed [[Windows SmartScreen]] guide

### **macOS Permission Denied**
**Issue**: "Cannot be opened because the developer cannot be verified"
**Solution**: 
1. Right-click app → "Open"
2. Or System Preferences → Security & Privacy → "Open anyway"

### **Linux Missing Dependencies**
**Issue**: Application won't start or crashes
**Solution**: Install Qt6 dependencies for your distribution (see commands above)

### **GPU Acceleration Not Working**
**Issue**: Hardware monitoring shows no GPU or poor performance
**Solutions**:
- **Windows**: Update graphics drivers
- **Linux**: Install `ocl-icd-opencl-dev` (Ubuntu) or equivalent
- **macOS**: Update to latest macOS version

## 📦 Installation Verification

After installation, verify everything works:

### **Test Basic Functionality**
```bash
# Test mode (doesn't start GUI)
./OopsieDaisy-Linux --test

# Expected output:
# 🐱 Oopsie Daisy - File Recovery Tool
# ✅ Application loaded successfully  
# ✅ Hardware monitor import successful
# ✅ Recovery engine import successful
# ✅ UI components import successful
# ✅ Platform detected: Linux
# 🎉 All core functionality tests passed!
```

### **Test GUI Launch**
1. **Launch application** normally
2. **Verify starry background** appears
3. **Check hardware monitoring** shows CPU/GPU stats
4. **Test drive selection** shows your drives

## 🔄 Updating

### **Automatic Updates**
Currently, updates must be done manually by downloading new releases.

### **Manual Update Process**
1. **Download latest release** from GitHub
2. **Replace old executable** with new one
3. **Keep your settings** (stored separately from executable)

### **Future Update Plans**
- Automatic update checking
- In-app update notifications  
- Delta updates for faster downloads

---

**Need Help?** Check [[Common Issues]] or ask in [GitHub Discussions](https://github.com/reshdesu/oopsie-daisy/discussions)!