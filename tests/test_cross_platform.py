#!/usr/bin/env python3
"""
Cross-platform hardware monitoring tests.
Tests hardware monitoring across Windows, macOS, and Linux platforms.
"""

import pytest
import platform
from unittest.mock import patch, MagicMock

from oopsie_daisy.hardware_monitor_qt import HardwareMonitor

@pytest.mark.integration
def test_platform_detection():
    """Test that platform detection works correctly."""
    print("🔍 Testing platform detection...")
    
    monitor = HardwareMonitor()
    current_system = platform.system().lower()
    
    print(f"✅ Current platform detected as: {current_system}")
    print(f"✅ Monitor system property: {monitor.system}")
    
    assert monitor.system == current_system, f"Platform mismatch: {monitor.system} != {current_system}"
    print("✅ Platform detection working correctly!\n")

@pytest.mark.integration  
def test_windows_simulation():
    """Simulate Windows platform and test Windows-specific methods."""
    print("🪟 Testing Windows simulation...")
    
    with patch('platform.system', return_value='Windows'):
        with patch('subprocess.run') as mock_subprocess:
            # Mock Windows PowerShell responses
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = '{"CurrentTemperature": 3131}'  # 50°C in tenths of Kelvin
            mock_subprocess.return_value = mock_result
            
            monitor = HardwareMonitor()
            
            # Test platform detection
            assert monitor.system == "windows", f"Expected 'windows', got '{monitor.system}'"
            print("✅ Platform simulation working")
            
            # Test Windows CPU temperature method
            temp = monitor._get_windows_cpu_temp()
            print(f"✅ Windows CPU temp method returned: {temp}")
            
            # Test Windows GPU detection
            mock_result.stdout = '[{"Name": "AMD Radeon RX 6800", "AdapterRAM": 17179869184}]'
            amd_gpus = monitor._get_all_amd_windows_stats()
            print(f"✅ Windows AMD GPU detection returned: {len(amd_gpus)} GPUs")
            if amd_gpus:
                print(f"   - GPU: {amd_gpus[0]['name']}")
            
            mock_result.stdout = '[{"Name": "Intel(R) UHD Graphics 630", "AdapterRAM": 1073741824}]'
            intel_gpus = monitor._get_all_intel_windows_stats()
            print(f"✅ Windows Intel GPU detection returned: {len(intel_gpus)} GPUs")
            if intel_gpus:
                print(f"   - GPU: {intel_gpus[0]['name']}")
    
    print("✅ Windows simulation tests passed!\n")

@pytest.mark.integration
def test_macos_simulation():
    """Simulate macOS platform and test macOS-specific methods."""
    print("🍎 Testing macOS simulation...")
    
    with patch('platform.system', return_value='Darwin'):
        with patch('subprocess.run') as mock_subprocess:
            # Mock macOS responses
            mock_result = MagicMock()
            mock_result.returncode = 0
            
            monitor = HardwareMonitor()
            
            # Test platform detection
            assert monitor.system == "darwin", f"Expected 'darwin', got '{monitor.system}'"
            print("✅ Platform simulation working")
            
            # Test macOS CPU temperature
            mock_result.stdout = "CPU die temperature: 45.2 C"
            temp = monitor._get_macos_cpu_temp()
            print(f"✅ macOS CPU temp method returned: {temp}")
            
            # Test macOS GPU detection
            mock_gpu_data = '''
            {
                "SPDisplaysDataType": [
                    {
                        "sppci_model": "AMD Radeon Pro 5600M",
                        "sppci_vendor": "AMD (0x1002)"
                    },
                    {
                        "sppci_model": "Apple M1 Pro",
                        "sppci_vendor": "Apple (0x106b)"
                    }
                ]
            }
            '''
            mock_result.stdout = mock_gpu_data
            
            amd_gpus = monitor._get_all_amd_macos_stats()
            integrated_gpus = monitor._get_all_integrated_macos_stats()
            
            print(f"✅ macOS AMD GPU detection returned: {len(amd_gpus)} GPUs")
            print(f"✅ macOS integrated GPU detection returned: {len(integrated_gpus)} GPUs")
            
            if amd_gpus:
                print(f"   - AMD GPU: {amd_gpus[0]['name']}")
            if integrated_gpus:
                print(f"   - Integrated GPU: {integrated_gpus[0]['name']}")
    
    print("✅ macOS simulation tests passed!\n")

@pytest.mark.integration
def test_error_handling():
    """Test error handling when commands fail."""
    print("🛡️ Testing error handling...")
    
    with patch('subprocess.run') as mock_subprocess:
        # Simulate command failures
        mock_subprocess.side_effect = FileNotFoundError("Command not found")
        
        monitor = HardwareMonitor()
        
        # These should not crash, just return None or empty lists
        temp = monitor._get_windows_cpu_temp()
        assert temp is None, "Should return None on command failure"
        
        gpus = monitor._get_all_amd_windows_stats()
        assert gpus == [], "Should return empty list on command failure"
        
        print("✅ Error handling working correctly")
    
    print("✅ Error handling tests passed!\n")

@pytest.mark.integration
def test_cross_platform_gpu_detection():
    """Test that GPU detection chooses the right platform methods."""
    print("🎮 Testing cross-platform GPU detection...")
    
    monitor = HardwareMonitor()
    
    # Test that it calls the right methods based on platform
    with patch.object(monitor, '_get_all_nvidia_stats', return_value=[]):
        with patch.object(monitor, '_get_all_amd_linux_stats', return_value=[]) as linux_amd:
            with patch.object(monitor, '_get_all_amd_windows_stats', return_value=[]) as windows_amd:
                with patch.object(monitor, '_get_all_amd_macos_stats', return_value=[]) as macos_amd:
                    
                    # Test Linux (current platform)
                    gpus = monitor._get_all_gpu_stats()
                    linux_amd.assert_called_once()
                    windows_amd.assert_not_called()
                    macos_amd.assert_not_called()
                    
                    print("✅ Linux GPU detection routing working")
    
    print("✅ Cross-platform GPU detection tests passed!\n")

# Tests are now run via pytest - no main() function needed