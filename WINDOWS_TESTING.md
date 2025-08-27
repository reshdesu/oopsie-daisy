# Windows Testing Guide

This document outlines how to test Oopsie Daisy on Windows systems without having direct access to Windows.

## 🤖 Automated Testing (Current)

### **GitHub Actions Windows Testing**
Every release automatically tests on `windows-latest` (Windows Server 2022/2025):

1. **Build Verification**: PyInstaller creates executable successfully
2. **File Structure Test**: Executable exists and has valid PE structure
3. **Dependency Loading**: Core imports load without errors
4. **Functionality Test**: `--test` mode verifies all components

**View test results**: https://github.com/reshdesu/oopsie-daisy/actions

### **Test Mode Usage**
Run without GUI to verify functionality:
```cmd
OopsieDaisy.exe --test
```

Expected output:
```
🐱 Oopsie Daisy - File Recovery Tool
✅ Application loaded successfully
✅ Hardware monitor import successful
✅ Recovery engine import successful
✅ UI components import successful
✅ Platform detected: Windows
🎉 All core functionality tests passed!
```

## 🧪 Manual Testing Options

### **Option 1: Windows VM (Free)**
- **VirtualBox + Windows 11 VM**: Microsoft provides free Windows 11 VMs for testing
- **Download**: https://developer.microsoft.com/en-us/windows/downloads/virtual-machines/
- **License**: 90-day evaluation (renewable)

### **Option 2: GitHub Codespaces**
- Run Windows container in browser
- Limited to command-line testing
- Good for import/dependency verification

### **Option 3: Community Testing**
- **Beta testers**: Recruit Windows users from GitHub community
- **Issue template**: Provide testing checklist
- **Feedback loop**: Quick bug reports and fixes

## 🔍 Testing Checklist

### **Critical Tests**
- [ ] Executable launches without immediate crash
- [ ] SmartScreen warning appears (expected)
- [ ] "More info" → "Run anyway" works
- [ ] Administrator UAC prompt appears for system scanning
- [ ] Main window appears with starry background
- [ ] Drive selection shows available drives
- [ ] Hardware monitoring displays CPU/GPU stats
- [ ] File scanning can start (even if no results)

### **Windows 11 Specific**
- [ ] Unicode/emoji display works correctly
- [ ] High DPI scaling works properly
- [ ] Windows 11 theme integration
- [ ] Modern context menus work
- [ ] File associations work correctly

### **Error Scenarios**
- [ ] Graceful handling when no admin rights given
- [ ] Proper error messages for missing drives
- [ ] Network drive handling
- [ ] Antivirus interference handling

## 📊 Current Test Coverage

### **Automated (✅ Working)**
- Import verification
- Platform detection
- PE file structure validation
- Core component loading

### **Manual Required (⚠️ Needs Community)**
- GUI rendering and interaction
- File system scanning
- Hardware monitoring accuracy
- User workflow testing
- SmartScreen bypass experience
- Administrator elevation flow

## 🤝 Community Testing Program

### **How to Participate**
1. Download latest release from GitHub
2. Follow the testing checklist
3. Report results in GitHub Issues with `[Windows Testing]` tag
4. Include system info (Windows version, hardware)

### **Reward System**
- Credit in README contributors section
- Early access to new features
- Direct feedback channel with developers

### **Bug Report Template**
```
**System Info:**
- Windows Version: 
- Hardware: 
- Antivirus: 

**Test Results:**
- [ ] Download successful
- [ ] SmartScreen bypass worked
- [ ] Application launched
- [ ] Main features functional

**Issues Found:**
(Detailed description)

**Screenshots:**
(If applicable)
```

## 🛡️ Trust & Verification

### **Source Code Transparency**
- All code is open source on GitHub
- Build process is public in GitHub Actions
- No obfuscated or hidden functionality

### **Security Verification**
- VirusTotal scanning of releases
- Reproducible builds (same source = same binary)
- Community code reviews welcome

### **What We Promise**
- ✅ Honest about limitations
- ✅ Fix bugs quickly when reported
- ✅ Never claim untested functionality
- ✅ Transparent about testing gaps

## 📈 Improving Coverage

### **Planned Improvements**
- [ ] Expand GitHub Actions testing to include more scenarios
- [ ] Create automated UI testing with Windows containers
- [ ] Partner with Windows testing services
- [ ] Build Windows testing community

### **Long-term Goals**
- Achieve 90%+ Windows functionality coverage
- Sub-24-hour bug fix response time
- Zero false claims about Windows compatibility
- Professional-grade Windows user experience

---

**Current Status**: 🟡 **Partially Tested**
- Core functionality verified through automation
- GUI and user workflows require community testing
- Actively seeking Windows testing volunteers!