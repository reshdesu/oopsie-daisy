#!/usr/bin/env python3
"""
Qt-compatible hardware monitoring for CPU/GPU usage and temperatures during file recovery.
Thread-safe version that avoids Qt cross-thread issues.
"""

import time
import platform
from typing import Dict, Optional, List
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer

try:
    import psutil
except ImportError:
    psutil = None


class HardwareMonitor(QObject):
    """Qt-compatible hardware monitor using QTimer for thread safety."""
    
    # Define signals for updates
    stats_updated = Signal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.system = platform.system().lower()
        self.current_stats = {
            'cpu_percent': 0.0,
            'cpu_temp': 0.0,
            'gpus': [],  # List of all GPUs with their stats
            'gpu_percent': 0.0,  # Keep for backwards compatibility
            'gpu_temp': 0.0,     # Keep for backwards compatibility
            'memory_percent': 0.0
        }
        
        # Use QTimer for thread-safe updates in main thread
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self._update_stats)
        
    def start_monitoring(self):
        """Start hardware monitoring using QTimer."""
        if not self.update_timer.isActive():
            self.update_timer.start(1000)  # Update every 1000ms (1 second)
    
    def stop_monitoring(self):
        """Stop hardware monitoring."""
        if self.update_timer.isActive():
            self.update_timer.stop()
    
    def _update_stats(self):
        """Update all hardware stats and emit signal."""
        try:
            # Update CPU stats
            self._update_cpu_stats()
            
            # Update GPU stats  
            self._update_gpu_stats()
            
            # Update memory stats
            self._update_memory_stats()
            
            # Emit signal with updated stats (already in main thread)
            self.stats_updated.emit(self.current_stats.copy())
            
        except Exception as e:
            print(f"Hardware monitoring error: {e}")
    
    def get_current_stats(self) -> Dict:
        """Get current hardware statistics."""
        return self.current_stats.copy()
    
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
        """Update GPU usage and temperature for all GPUs."""
        try:
            gpu_list = self._get_all_gpu_stats()
            self.current_stats['gpus'] = gpu_list
            
            # For backwards compatibility, set the best GPU as main values
            if gpu_list:
                best_gpu = max(gpu_list, key=lambda g: g.get('usage', 0))
                self.current_stats['gpu_percent'] = best_gpu.get('usage', 0.0)
                self.current_stats['gpu_temp'] = best_gpu.get('temp', 0.0)
            else:
                self.current_stats['gpu_percent'] = 0.0
                self.current_stats['gpu_temp'] = 0.0
            
        except Exception as e:
            print(f"GPU monitoring error: {e}")
            self.current_stats['gpus'] = []
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
                            temp_val = sensor_list[0].current
                            return temp_val
                
                # If no specific sensor found, try any available
                for sensor_name, sensor_list in temps.items():
                    if sensor_list and ('cpu' in sensor_name.lower() or 'core' in sensor_name.lower()):
                        temp_val = sensor_list[0].current
                        return temp_val
                
                # Try first available sensor
                if temps:
                    first_sensor = next(iter(temps.values()))
                    if first_sensor:
                        temp_val = first_sensor[0].current
                        return temp_val
            
            # Fallback methods for Linux
            if self.system == "linux":
                temp_val = self._get_linux_cpu_temp()
                return temp_val
                
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
                    if 0.0 <= temp_celsius <= 120.0:  # Reasonable CPU temp range (relaxed)
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
                                if 0.0 <= temp_celsius <= 120.0:  # Relaxed range
                                    return temp_celsius
                                    
        except Exception as e:
            print(f"Linux CPU temp error: {e}")
            
        return None
    
    def _get_all_gpu_stats(self) -> List[Dict]:
        """Get stats for all available GPUs."""
        gpu_list = []
        
        try:
            # Try NVIDIA GPUs first
            nvidia_gpus = self._get_all_nvidia_stats()
            gpu_list.extend(nvidia_gpus)
            
            # Try AMD GPUs
            amd_gpus = self._get_all_amd_stats()
            gpu_list.extend(amd_gpus)
            
        except Exception as e:
            print(f"Error getting all GPU stats: {e}")
            
        return gpu_list
    
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
                    lines = output.split('\n')
                    
                    # If multiple GPUs, find the most active one
                    best_usage = 0.0
                    best_temp = 0.0
                    
                    for line in lines:
                        if ',' in line:
                            try:
                                usage_str, temp_str = line.split(',')
                                usage = float(usage_str.strip())
                                temp = float(temp_str.strip())
                                
                                # Prefer GPU with higher usage, or higher temp if usage is same
                                if usage > best_usage or (usage == best_usage and temp > best_temp):
                                    best_usage = usage
                                    best_temp = temp
                                    
                            except ValueError:
                                continue
                    
                    return best_usage, best_temp
                    
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
            
        return 0.0, 0.0
    
    def _get_all_nvidia_stats(self) -> List[Dict]:
        """Get stats for all NVIDIA GPUs."""
        gpu_list = []
        
        try:
            import subprocess
            
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=name,utilization.gpu,temperature.gpu', 
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=3)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                if output:
                    lines = output.split('\n')
                    
                    for i, line in enumerate(lines):
                        parts = line.split(',')
                        if len(parts) >= 3:
                            try:
                                name = parts[0].strip()
                                usage = float(parts[1].strip())
                                temp = float(parts[2].strip())
                                
                                gpu_list.append({
                                    'id': i,
                                    'name': name,
                                    'usage': usage,
                                    'temp': temp,
                                    'vendor': 'NVIDIA'
                                })
                                
                            except ValueError:
                                continue
                    
        except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
            pass
            
        return gpu_list
    
    def _get_all_amd_stats(self) -> List[Dict]:
        """Get stats for all AMD GPUs from sysfs."""
        gpu_list = []
        
        try:
            if self.system == "linux":
                drm_path = Path("/sys/class/drm")
                if drm_path.exists():
                    gpu_id = 0
                    for card_dir in sorted(drm_path.iterdir()):
                        if card_dir.name.startswith("card") and not card_dir.name.endswith("-"):
                            device_path = card_dir / "device"
                            
                            # Try to read GPU usage
                            gpu_busy_file = device_path / "gpu_busy_percent"
                            if gpu_busy_file.exists():
                                try:
                                    usage = float(gpu_busy_file.read_text().strip())
                                except (ValueError, OSError):
                                    usage = 0.0
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
                                    try:
                                        temp_raw = temp_file.read_text().strip()
                                        temp = float(temp_raw) / 1000.0  # Convert from millidegrees
                                        break
                                    except (ValueError, OSError):
                                        continue
                            
                            # Try to get GPU name
                            name_file = device_path / "device"
                            gpu_name = f"AMD GPU {gpu_id}"
                            if name_file.exists():
                                try:
                                    # This is simplified - real GPU name detection is more complex
                                    gpu_name = f"AMD GPU {gpu_id}"
                                except:
                                    pass
                            
                            if usage > 0 or temp > 0:  # Only add if we got some data
                                gpu_list.append({
                                    'id': gpu_id,
                                    'name': gpu_name,
                                    'usage': usage,
                                    'temp': temp,
                                    'vendor': 'AMD'
                                })
                            
                            gpu_id += 1
                            
        except Exception as e:
            print(f"AMD GPU enumeration error: {e}")
            
        return gpu_list
    
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_start_time = None
        self.peak_cpu = 0.0
        self.peak_gpu = 0.0
        self.peak_temp_cpu = 0.0
        self.peak_temp_gpu = 0.0
        
        # Connect to our own stats_updated signal to track peaks
        self.stats_updated.connect(self._update_peaks)
    
    def start_scan_monitoring(self):
        """Start monitoring for a scan operation."""
        self.scan_start_time = time.time()
        self.peak_cpu = 0.0
        self.peak_gpu = 0.0 
        self.peak_temp_cpu = 0.0
        self.peak_temp_gpu = 0.0
        self.start_monitoring()
    
    def _update_peaks(self, stats):
        """Update peak values when stats are updated."""
        try:
            self.peak_cpu = max(self.peak_cpu, stats.get('cpu_percent', 0.0))
            self.peak_gpu = max(self.peak_gpu, stats.get('gpu_percent', 0.0))
            self.peak_temp_cpu = max(self.peak_temp_cpu, stats.get('cpu_temp', 0.0))
            self.peak_temp_gpu = max(self.peak_temp_gpu, stats.get('gpu_temp', 0.0))
            
            # Add scan duration to stats
            if self.scan_start_time:
                stats['scan_duration'] = time.time() - self.scan_start_time
                stats['peak_cpu'] = self.peak_cpu
                stats['peak_gpu'] = self.peak_gpu
                stats['peak_temp_cpu'] = self.peak_temp_cpu
                stats['peak_temp_gpu'] = self.peak_temp_gpu
                
        except Exception as e:
            print(f"Peak update error: {e}")
    
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