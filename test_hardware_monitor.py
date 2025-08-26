#!/usr/bin/env python3
"""
Test script for hardware monitoring functionality.
"""

import time
from src.oopsie_daisy.hardware_monitor import ScanHardwareMonitor

def test_hardware_monitoring():
    """Test hardware monitoring capabilities."""
    
    print("🖥️  Testing Hardware Monitoring")
    print("=" * 40)
    
    monitor = ScanHardwareMonitor()
    
    # Test initial stats
    stats = monitor.get_current_stats()
    print("📊 Initial Stats:")
    print(f"  CPU: {stats['cpu_percent']:.1f}%")
    print(f"  GPU: {stats['gpu_percent']:.1f}%")
    print(f"  CPU Temp: {stats['cpu_temp']:.1f}°C")
    print(f"  GPU Temp: {stats['gpu_temp']:.1f}°C")
    print(f"  Memory: {stats['memory_percent']:.1f}%")
    
    print("\n🚀 Starting monitoring for 10 seconds...")
    
    def update_callback(stats):
        print(f"  🔧 CPU: {stats['cpu_percent']:5.1f}% ({stats['cpu_temp']:4.1f}°C) | "
              f"🎮 GPU: {stats['gpu_percent']:5.1f}% ({stats['gpu_temp']:4.1f}°C) | "
              f"💾 RAM: {stats['memory_percent']:5.1f}%")
    
    # Start monitoring
    monitor.start_scan_monitoring(update_callback)
    
    # Let it run for 10 seconds
    start_time = time.time()
    try:
        while time.time() - start_time < 10:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n⚠️  Monitoring interrupted")
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Show summary
    summary = monitor.get_scan_summary()
    print(f"\n📈 Monitoring Summary:")
    print(f"  Duration: {summary['duration']:.1f} seconds")
    print(f"  Peak CPU: {summary['peak_cpu_percent']:.1f}%")
    print(f"  Peak GPU: {summary['peak_gpu_percent']:.1f}%")
    print(f"  Peak CPU Temp: {summary['peak_cpu_temp']:.1f}°C")
    print(f"  Peak GPU Temp: {summary['peak_gpu_temp']:.1f}°C")
    
    print("\n✅ Hardware monitoring test complete!")

if __name__ == "__main__":
    test_hardware_monitoring()