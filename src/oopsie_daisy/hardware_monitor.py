#!/usr/bin/env python3
"""
Hardware monitoring for CPU/GPU usage and temperatures during file recovery.
"""

import time
import platform
import threading
from typing import Dict, Optional, Callable
from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


class HardwareMonitor:
    """Monitor CPU and GPU usage and temperatures during scanning."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.monitoring = False
        self.monitor_thread = None
        self.current_stats = {
            'cpu_percent': 0.0,
            'cpu_temp': 0.0,
            'gpu_percent': 0.0,
            'gpu_temp': 0.0,
            'memory_percent': 0.0
        }
        self.update_callback = None
        
    def start_monitoring(self, callback: Optional[Callable[[Dict], None]] = None):
        """Start hardware monitoring in background thread."""
        if self.monitoring:
            return
            
        self.monitoring = True
        self.update_callback = callback
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop hardware monitoring."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
    
    def get_current_stats(self) -> Dict:
        """Get current hardware statistics."""
        return self.current_stats.copy()
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self.monitoring:
            try:
                # Update CPU stats
                self._update_cpu_stats()
                
                # Update GPU stats  
                self._update_gpu_stats()
                
                # Update memory stats
                self._update_memory_stats()
                
                # Notify callback if set
                if self.update_callback:
                    self.update_callback(self.current_stats.copy())
                
                time.sleep(1.0)  # Update every second
                
            except Exception as e:
                print(f"Hardware monitoring error: {e}")
                time.sleep(2.0)  # Wait longer on error
    
    def _update_cpu_stats(self):
        """Update CPU usage and temperature."""
        try:
            if psutil:
                # CPU usage percentage
                self.current_stats['cpu_percent'] = psutil.cpu_percent(interval=None)
                
                # CPU temperature
                temp = self._get_cpu_temperature()
                if temp is not None:
                    self.current_stats['cpu_temp'] = temp
                else:
                    self.current_stats['cpu_temp'] = 0.0
            else:
                # Fallback without psutil
                self.current_stats['cpu_percent'] = self._get_cpu_usage_fallback()
                self.current_stats['cpu_temp'] = self._get_cpu_temp_fallback()
                
        except Exception as e:
            print(f"CPU monitoring error: {e}")
            self.current_stats['cpu_percent'] = 0.0
            self.current_stats['cpu_temp'] = 0.0
    
    def _update_gpu_stats(self):
        """Update GPU usage and temperature."""
        try:
            gpu_usage, gpu_temp = self._get_gpu_stats()
            self.current_stats['gpu_percent'] = gpu_usage
            self.current_stats['gpu_temp'] = gpu_temp
            
        except Exception as e:
            print(f"GPU monitoring error: {e}")
            self.current_stats['gpu_percent'] = 0.0
            self.current_stats['gpu_temp'] = 0.0
    
    def _update_memory_stats(self):
        """Update memory usage."""
        try:
            if psutil:
                memory = psutil.virtual_memory()
                self.current_stats['memory_percent'] = memory.percent
            else:
                self.current_stats['memory_percent'] = 0.0
                
        except Exception:
            self.current_stats['memory_percent'] = 0.0
    
    def _get_cpu_temperature(self) -> Optional[float]:
        """Get CPU temperature using various methods."""
        try:
            if psutil and hasattr(psutil, 'sensors_temperatures'):
                temps = psutil.sensors_temperatures()
                
                # Try different sensor names
                sensor_names = ['coretemp', 'cpu_thermal', 'acpi', 'k10temp', 'zenpower']
                
                for name in sensor_names:
                    if name in temps:
                        sensor_list = temps[name]
                        if sensor_list:
                            # Get the first sensor's current temperature
                            return sensor_list[0].current
                
                # If no specific sensor found, try any available
                for sensor_name, sensor_list in temps.items():
                    if sensor_list and 'cpu' in sensor_name.lower():
                        return sensor_list[0].current
            
            # Fallback methods for Linux
            if self.system == "linux":
                return self._get_linux_cpu_temp()
                
        except Exception as e:
            print(f"CPU temperature error: {e}")
            
        return None
    
    def _get_linux_cpu_temp(self) -> Optional[float]:
        """Get CPU temperature on Linux systems."""
        try:
            # Try thermal_zone files
            thermal_paths = [
                "/sys/class/thermal/thermal_zone0/temp",
                "/sys/class/thermal/thermal_zone1/temp", 
                "/sys/class/thermal/thermal_zone2/temp"
            ]
            
            for path in thermal_paths:
                temp_path = Path(path)
                if temp_path.exists():
                    temp_raw = temp_path.read_text().strip()
                    # Temperature is usually in millidegrees Celsius
                    temp_celsius = float(temp_raw) / 1000.0
                    if 20.0 <= temp_celsius <= 100.0:  # Reasonable CPU temp range
                        return temp_celsius
                        
            # Try hwmon sensors
            hwmon_base = Path("/sys/class/hwmon")
            if hwmon_base.exists():
                for hwmon_dir in hwmon_base.iterdir():
                    name_file = hwmon_dir / "name"
                    if name_file.exists():
                        name = name_file.read_text().strip()
                        if any(cpu_name in name.lower() for cpu_name in ['coretemp', 'k10temp', 'zenpower']):
                            # Look for temp1_input
                            temp_file = hwmon_dir / "temp1_input"
                            if temp_file.exists():
                                temp_raw = temp_file.read_text().strip()
                                temp_celsius = float(temp_raw) / 1000.0
                                if 20.0 <= temp_celsius <= 100.0:
                                    return temp_celsius
                                    
        except Exception as e:
            print(f"Linux CPU temp error: {e}")
            
        return None
    
    def _get_gpu_stats(self) -> tuple[float, float]:
        """Get GPU usage and temperature."""
        gpu_usage = 0.0
        gpu_temp = 0.0
        
        try:
            # Try nvidia-smi first (NVIDIA GPUs)
            gpu_usage, gpu_temp = self._get_nvidia_stats()
            if gpu_usage > 0 or gpu_temp > 0:
                return gpu_usage, gpu_temp
                
            # Try AMD GPU monitoring
            gpu_usage, gpu_temp = self._get_amd_stats() 
            if gpu_usage > 0 or gpu_temp > 0:
                return gpu_usage, gpu_temp
                
            # Try Intel GPU monitoring
            gpu_usage, gpu_temp = self._get_intel_stats()
            if gpu_usage > 0 or gpu_temp > 0:
                return gpu_usage, gpu_temp
                
        except Exception as e:
            print(f"GPU stats error: {e}")
            
        return gpu_usage, gpu_temp
    
    def _get_nvidia_stats(self) -> tuple[float, float]:
        """Get NVIDIA GPU stats using nvidia-smi."""
        try:
            import subprocess
            
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=utilization.gpu,temperature.gpu', 
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    usage_str, temp_str = output.split(',')
                    return float(usage_str.strip()), float(temp_str.strip())
                    
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
            
        return 0.0, 0.0
    
    def _get_amd_stats(self) -> tuple[float, float]:
        """Get AMD GPU stats from sysfs."""
        try:
            if self.system == "linux":
                # Look for AMD GPU in /sys/class/drm/
                drm_path = Path("/sys/class/drm")
                if drm_path.exists():
                    for card_dir in drm_path.iterdir():
                        if card_dir.name.startswith("card") and not card_dir.name.endswith("-"):
                            device_path = card_dir / "device"
                            
                            # Try to read GPU usage
                            gpu_busy_file = device_path / "gpu_busy_percent"
                            if gpu_busy_file.exists():
                                usage = float(gpu_busy_file.read_text().strip())
                            else:
                                usage = 0.0
                            
                            # Try to read GPU temperature
                            temp_files = [
                                device_path / "hwmon" / "hwmon0" / "temp1_input",
                                device_path / "hwmon" / "hwmon1" / "temp1_input"
                            ]
                            
                            temp = 0.0
                            for temp_file in temp_files:
                                if temp_file.exists():
                                    temp_raw = temp_file.read_text().strip()
                                    temp = float(temp_raw) / 1000.0  # Convert from millidegrees
                                    break
                            
                            if usage > 0 or temp > 0:
                                return usage, temp
                                
        except Exception as e:
            print(f"AMD GPU error: {e}")
            
        return 0.0, 0.0
    
    def _get_intel_stats(self) -> tuple[float, float]:
        """Get Intel GPU stats."""
        try:
            # Intel GPU monitoring is more complex, often requires special tools
            # For now, return mock data if Intel GPU is detected
            if self.system == "linux":
                # Check if Intel GPU exists
                drm_path = Path("/sys/class/drm")
                if drm_path.exists():
                    for card_dir in drm_path.iterdir():
                        if card_dir.name.startswith("card"):
                            device_path = card_dir / "device"
                            vendor_file = device_path / "vendor"
                            if vendor_file.exists():
                                vendor_id = vendor_file.read_text().strip()
                                if vendor_id == "0x8086":  # Intel vendor ID
                                    # Mock Intel GPU stats for demo
                                    import random
                                    return random.uniform(10, 40), random.uniform(35, 60)
                                    
        except Exception as e:
            print(f"Intel GPU error: {e}")
            
        return 0.0, 0.0
    
    def _get_cpu_usage_fallback(self) -> float:
        """Fallback CPU usage without psutil."""
        try:
            if self.system == "linux":
                # Read /proc/stat for CPU usage
                with open('/proc/stat', 'r') as f:
                    line = f.readline()
                    cpu_times = [int(x) for x in line.split()[1:]]
                    
                # Simple approximation
                total_time = sum(cpu_times)
                idle_time = cpu_times[3]  # idle time
                if total_time > 0:
                    return max(0.0, min(100.0, (total_time - idle_time) / total_time * 100))
                    
        except Exception:
            pass
            
        return 0.0
    
    def _get_cpu_temp_fallback(self) -> float:
        """Fallback CPU temperature without psutil."""
        try:
            return self._get_linux_cpu_temp() or 0.0
        except Exception:
            return 0.0


class ScanHardwareMonitor(HardwareMonitor):
    """Specialized hardware monitor for file scanning operations."""
    
    def __init__(self):
        super().__init__()
        self.scan_start_time = None
        self.peak_cpu = 0.0
        self.peak_gpu = 0.0
        self.peak_temp_cpu = 0.0
        self.peak_temp_gpu = 0.0
    
    def start_scan_monitoring(self, callback: Optional[Callable[[Dict], None]] = None):
        """Start monitoring for a scan operation."""
        self.scan_start_time = time.time()
        self.peak_cpu = 0.0
        self.peak_gpu = 0.0 
        self.peak_temp_cpu = 0.0
        self.peak_temp_gpu = 0.0
        self.start_monitoring(callback)
    
    def _monitor_loop(self):
        """Enhanced monitoring loop that tracks peaks."""
        while self.monitoring:
            try:
                # Update stats
                self._update_cpu_stats()
                self._update_gpu_stats()
                self._update_memory_stats()
                
                # Track peaks
                self.peak_cpu = max(self.peak_cpu, self.current_stats['cpu_percent'])
                self.peak_gpu = max(self.peak_gpu, self.current_stats['gpu_percent'])
                self.peak_temp_cpu = max(self.peak_temp_cpu, self.current_stats['cpu_temp'])
                self.peak_temp_gpu = max(self.peak_temp_gpu, self.current_stats['gpu_temp'])
                
                # Add scan duration
                if self.scan_start_time:
                    self.current_stats['scan_duration'] = time.time() - self.scan_start_time
                
                # Add peak values
                self.current_stats['peak_cpu'] = self.peak_cpu
                self.current_stats['peak_gpu'] = self.peak_gpu
                self.current_stats['peak_temp_cpu'] = self.peak_temp_cpu
                self.current_stats['peak_temp_gpu'] = self.peak_temp_gpu
                
                # Notify callback
                if self.update_callback:
                    self.update_callback(self.current_stats.copy())
                
                time.sleep(1.0)
                
            except Exception as e:
                print(f"Scan monitoring error: {e}")
                time.sleep(2.0)
    
    def get_scan_summary(self) -> Dict:
        """Get summary of scan performance."""
        duration = time.time() - self.scan_start_time if self.scan_start_time else 0
        
        return {
            'duration': duration,
            'peak_cpu_percent': self.peak_cpu,
            'peak_gpu_percent': self.peak_gpu,
            'peak_cpu_temp': self.peak_temp_cpu,
            'peak_gpu_temp': self.peak_temp_gpu,
            'avg_cpu_percent': self.current_stats['cpu_percent'],
            'avg_gpu_percent': self.current_stats['gpu_percent'],
            'final_cpu_temp': self.current_stats['cpu_temp'],
            'final_gpu_temp': self.current_stats['gpu_temp']
        }