# Cross-Platform Testing for Oopsie Daisy

This document outlines how we test the Oopsie Daisy file recovery application across Windows, macOS, and Linux platforms.

## 🧪 Testing Strategy

Since we develop on Ubuntu Linux, we use a multi-layered testing approach to ensure cross-platform compatibility:

### 1. **Automated Platform Simulation**
- **File**: `test_cross_platform.py`
- **Purpose**: Simulates Windows and macOS environments using Python mocking
- **Coverage**: Platform detection, hardware monitoring, error handling
- **Run**: `uv run python test_cross_platform.py`

### 2. **GitHub Actions Cross-Platform Builds**
- **Platforms**: Windows Server, macOS, Ubuntu
- **Purpose**: Real platform testing during CI/CD
- **Coverage**: Build process, dependency installation, executable creation
- **Trigger**: Every tag push (v*) or manual dispatch

### 3. **Platform-Specific Feature Testing**

#### Windows Testing
```powershell
# CPU Temperature (WMI)
Get-WmiObject -Namespace root/WMI -Class MSAcpi_ThermalZoneTemperature

# GPU Detection (WMI)
Get-WmiObject -Class Win32_VideoController | Where-Object {$_.Name -like '*AMD*'}
```

#### macOS Testing
```bash
# CPU Temperature
sudo powermetrics --samplers smc -n 1 -i 1

# GPU Detection
system_profiler SPDisplaysDataType -json
```

#### Linux Testing
```bash
# CPU Temperature  
cat /sys/class/thermal/thermal_zone*/temp

# GPU Detection
ls /sys/class/drm/card*/device/gpu_busy_percent
```

## 🔍 Test Coverage

### ✅ **Verified Features**
- Platform detection (Windows/macOS/Linux)
- Hardware monitoring API routing
- Error handling and graceful fallbacks
- Cross-platform file path handling
- UI rendering (PySide6/Qt6 is cross-platform)
- CSV export functionality
- File preview system

### ⚠️ **Platform-Specific Limitations**

#### Windows
- **CPU Temp**: Requires WMI permissions (usually available)
- **GPU Usage**: Limited without driver-specific APIs
- **Admin Rights**: Some features may need elevated permissions

#### macOS  
- **CPU Temp**: May require admin privileges for powermetrics
- **GPU Usage**: Limited system API exposure
- **Sandboxing**: App Store distribution may limit system access

#### Linux
- **Full Featured**: Complete hardware monitoring support
- **Permissions**: May need user in appropriate groups

## 🚀 Real-World Testing

### GitHub Actions Verification
1. **Windows Build**: Tests on `windows-latest` (Windows Server 2022)
2. **macOS Build**: Tests on `macos-latest` (macOS Monterey+)  
3. **Linux Build**: Tests on `ubuntu-latest` (Ubuntu 22.04+)

Each build:
- Installs dependencies
- Runs cross-platform compatibility tests
- Creates executable with PyInstaller
- Uploads artifacts for download

### Manual Testing Checklist

When testing on actual Windows/macOS machines:

#### Windows
- [ ] Application launches without errors
- [ ] Hardware monitoring shows CPU usage
- [ ] GPU detection finds available graphics cards
- [ ] CPU temperature displays (if WMI available)
- [ ] File recovery functionality works
- [ ] Preview system handles files correctly
- [ ] Export to CSV functions properly

#### macOS
- [ ] Application launches (may need security approval)
- [ ] Hardware monitoring shows CPU usage  
- [ ] GPU detection finds graphics hardware
- [ ] File recovery scans drives successfully
- [ ] Preview system displays file information
- [ ] Default Downloads folder detection works

## 🛠️ Debugging Cross-Platform Issues

### Common Issues and Solutions

1. **Missing Dependencies**
   - Solution: PyInstaller bundles all dependencies
   - Fallback: Use `--collect-all` flags in build

2. **Permission Errors**
   - Windows: Run as Administrator for full hardware access
   - macOS: Allow system access in Security & Privacy
   - Linux: Add user to appropriate groups

3. **Command Not Found**
   - All platforms gracefully handle missing system commands
   - Hardware monitoring degrades gracefully

### Testing Commands

```bash
# Test on current platform
uv run python test_cross_platform.py

# Test specific platform simulation
uv run python -c "
import platform
from unittest.mock import patch
with patch('platform.system', return_value='Windows'):
    from src.oopsie_daisy.hardware_monitor_qt import HardwareMonitor
    monitor = HardwareMonitor()
    print(f'Platform: {monitor.system}')
"
```

## 📊 Test Results

Latest test results show:
- ✅ Platform detection working correctly
- ✅ Windows simulation passing all tests  
- ✅ macOS simulation handling gracefully
- ✅ Error handling preventing crashes
- ✅ Cross-platform GPU routing functional

## 🎯 Future Testing Improvements

1. **Virtual Machines**: Set up Windows/macOS VMs for deeper testing
2. **User Testing**: Beta testing with actual Windows/macOS users
3. **CI Enhancement**: More comprehensive platform-specific tests
4. **Performance Testing**: Hardware monitoring performance across platforms

## 📞 User Feedback

Users can report platform-specific issues at:
- GitHub Issues: https://github.com/reshdesu/oopsie-daisy/issues
- Include: OS version, hardware specs, error logs