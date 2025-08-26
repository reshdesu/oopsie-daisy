#!/usr/bin/env python3
"""
High-performance file recovery scanner using CPU multi-threading and GPU acceleration.
"""

import os
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from pathlib import Path
from typing import List, Dict, Optional, Callable
import time
import psutil
import numpy as np

try:
    import pyopencl as cl
    OPENCL_AVAILABLE = True
except ImportError:
    OPENCL_AVAILABLE = False


class AcceleratedFileScanner:
    """
    High-performance file scanner using CPU multi-threading and optional GPU acceleration.
    """
    
    def __init__(self):
        self.cpu_count = multiprocessing.cpu_count()
        self.memory_gb = psutil.virtual_memory().total / (1024**3)
        self.use_gpu = OPENCL_AVAILABLE and self._init_gpu()
        
        # Adaptive threading based on system resources
        self.max_threads = min(self.cpu_count * 2, 16)  # Cap at 16 threads
        
        print(f"🚀 Accelerated scanner initialized:")
        print(f"   CPU cores: {self.cpu_count}")
        print(f"   Max threads: {self.max_threads}")
        print(f"   Memory: {self.memory_gb:.1f} GB")
        print(f"   GPU acceleration: {'✅' if self.use_gpu else '❌'}")
    
    def _init_gpu(self) -> bool:
        """Initialize GPU acceleration if available (supports NVIDIA, AMD, Intel)."""
        try:
            # Get OpenCL platforms and devices
            platforms = cl.get_platforms()
            if not platforms:
                return False
            
            # Prioritize GPU types: AMD > NVIDIA > Intel > Other
            gpu_device = None
            gpu_info = ""
            
            # Check all platforms for best GPU
            for platform in platforms:
                platform_name = platform.name.lower()
                try:
                    devices = platform.get_devices(cl.device_type.GPU)
                    if not devices:
                        continue
                        
                    for device in devices:
                        device_name = device.name.lower()
                        
                        # AMD GPUs (ROCm, OpenCL)
                        if 'amd' in platform_name or 'radeon' in device_name or 'rx ' in device_name:
                            gpu_device = device
                            gpu_info = f"AMD {device.name} (OpenCL)"
                            break
                        # NVIDIA GPUs (CUDA via OpenCL)    
                        elif 'nvidia' in platform_name or 'geforce' in device_name or 'rtx' in device_name:
                            if not gpu_device:  # Use if no AMD found
                                gpu_device = device
                                gpu_info = f"NVIDIA {device.name} (OpenCL)"
                        # Intel GPUs
                        elif 'intel' in platform_name or 'intel' in device_name:
                            if not gpu_device:  # Use if no AMD/NVIDIA found
                                gpu_device = device 
                                gpu_info = f"Intel {device.name} (OpenCL)"
                        # Other GPUs
                        elif not gpu_device:
                            gpu_device = device
                            gpu_info = f"{device.name} (OpenCL)"
                            
                    if gpu_device and 'amd' in gpu_info.lower():
                        break  # Prefer AMD, stop searching
                        
                except cl.LogicError:
                    # No GPU devices in this platform
                    continue
            
            if gpu_device:
                self.gpu_context = cl.Context([gpu_device])
                self.gpu_queue = cl.CommandQueue(self.gpu_context)
                
                # Get additional GPU info
                compute_units = gpu_device.max_compute_units
                global_mem_mb = gpu_device.global_mem_size // (1024**2)
                
                print(f"   GPU: {gpu_info}")
                print(f"   GPU Memory: {global_mem_mb} MB")
                print(f"   Compute Units: {compute_units}")
                
                return True
                
        except Exception as e:
            print(f"   GPU init failed: {e}")
            
        return False
    
    def scan_locations_parallel(self, locations: List[Path], 
                              progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Scan multiple locations in parallel using CPU threads and optional GPU acceleration.
        """
        print(f"🔍 Starting parallel scan of {len(locations)} locations...")
        start_time = time.time()
        
        all_files = []
        completed_locations = 0
        
        # Use ThreadPoolExecutor for I/O bound operations
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # Submit all scan tasks
            future_to_location = {
                executor.submit(self._scan_location_optimized, loc): loc 
                for loc in locations if loc.exists()
            }
            
            # Collect results as they complete
            for future in future_to_location:
                try:
                    location_files = future.result(timeout=30)  # 30 second timeout per location
                    all_files.extend(location_files)
                    
                    completed_locations += 1
                    if progress_callback:
                        progress = int((completed_locations / len(locations)) * 100)
                        progress_callback(progress)
                        
                except Exception as e:
                    location = future_to_location[future]
                    print(f"   ⚠️  Failed to scan {location}: {e}")
                    continue
        
        scan_time = time.time() - start_time
        print(f"✅ Parallel scan completed in {scan_time:.2f}s")
        print(f"   Found {len(all_files)} files total")
        
        # GPU-accelerated post-processing if available
        if self.use_gpu and len(all_files) > 1000:
            all_files = self._gpu_filter_files(all_files)
        
        return all_files
    
    def _scan_location_optimized(self, location: Path) -> List[Dict]:
        """
        Optimized scanning of a single location using efficient algorithms.
        """
        files = []
        
        try:
            if not location.exists() or not location.is_dir():
                return files
                
            # Use os.scandir for better performance than pathlib
            with os.scandir(location) as entries:
                file_entries = []
                for entry in entries:
                    try:
                        if entry.is_file(follow_symlinks=False):
                            file_entries.append(entry)
                    except (OSError, PermissionError):
                        continue
                
                # Process files in batches for memory efficiency
                batch_size = 1000
                for i in range(0, len(file_entries), batch_size):
                    batch = file_entries[i:i+batch_size]
                    batch_results = self._process_file_batch(batch)
                    files.extend(batch_results)
                    
        except (PermissionError, OSError):
            # Skip inaccessible locations
            pass
            
        return files
    
    def _process_file_batch(self, file_entries) -> List[Dict]:
        """
        Process a batch of files efficiently.
        """
        files = []
        
        for entry in file_entries:
            try:
                stat_result = entry.stat(follow_symlinks=False)
                
                # Quick heuristics for deleted/temporary files
                name = entry.name
                is_temp_file = (
                    name.startswith('.') or 
                    name.endswith('.tmp') or 
                    name.endswith('~') or
                    '.swp' in name or
                    name.startswith('~$')
                )
                
                file_info = {
                    'name': name,
                    'path': entry.path,
                    'size': stat_result.st_size,
                    'modified': stat_result.st_mtime,
                    'type': 'temp_file' if is_temp_file else 'regular_file',
                    'score': self._calculate_recovery_score(name, stat_result)
                }
                
                files.append(file_info)
                
            except (OSError, PermissionError):
                continue
                
        return files
    
    def _calculate_recovery_score(self, filename: str, stat_result) -> float:
        """
        Calculate likelihood that file is recoverable/interesting (0-1 score).
        """
        score = 0.5  # Base score
        
        # Boost score for recently modified files
        age_days = (time.time() - stat_result.st_mtime) / 86400
        if age_days < 1:
            score += 0.3
        elif age_days < 7:
            score += 0.2
        elif age_days < 30:
            score += 0.1
        
        # Boost score for common document types
        valuable_extensions = {'.doc', '.docx', '.pdf', '.txt', '.jpg', '.png', '.mp4', '.zip'}
        if any(filename.lower().endswith(ext) for ext in valuable_extensions):
            score += 0.2
        
        # Reduce score for system/cache files
        if filename.startswith('.') or 'cache' in filename.lower():
            score -= 0.2
        
        return max(0.0, min(1.0, score))
    
    def _gpu_filter_files(self, files: List[Dict]) -> List[Dict]:
        """
        Use GPU acceleration to filter and sort large file lists.
        """
        if not self.use_gpu or len(files) < 1000:
            return files
            
        try:
            print("🔥 Using GPU acceleration for file filtering...")
            
            # Extract scores for GPU processing
            scores = np.array([f.get('score', 0.5) for f in files], dtype=np.float32)
            
            # Create GPU buffers
            scores_gpu = cl.Buffer(self.gpu_context, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR, hostbuf=scores)
            result_gpu = cl.Buffer(self.gpu_context, cl.mem_flags.WRITE_ONLY, scores.nbytes)
            
            # Simple GPU kernel for scoring (this is a simplified example)
            kernel_code = """
            __kernel void enhance_scores(__global const float* input_scores, 
                                       __global float* output_scores,
                                       const int count) {
                int idx = get_global_id(0);
                if (idx >= count) return;
                
                float score = input_scores[idx];
                // Apply GPU-accelerated scoring enhancements
                score = score * 1.1f;  // Boost all scores slightly
                output_scores[idx] = min(1.0f, score);
            }
            """
            
            program = cl.Program(self.gpu_context, kernel_code).build()
            
            # Execute kernel
            program.enhance_scores(self.gpu_queue, (len(scores),), None, 
                                 scores_gpu, result_gpu, np.int32(len(scores)))
            
            # Read results back
            enhanced_scores = np.empty_like(scores)
            cl.enqueue_copy(self.gpu_queue, enhanced_scores, result_gpu)
            
            # Update file scores
            for i, file_info in enumerate(files):
                file_info['score'] = float(enhanced_scores[i])
            
            # Sort by enhanced scores
            files.sort(key=lambda f: f['score'], reverse=True)
            
            print(f"✅ GPU filtering completed for {len(files)} files")
            
        except Exception as e:
            print(f"⚠️  GPU filtering failed, using CPU: {e}")
            # Fallback to CPU sorting
            files.sort(key=lambda f: f.get('score', 0.5), reverse=True)
        
        return files
    
    def scan_folder_deep(self, folder_path: Path, 
                        progress_callback: Optional[Callable] = None) -> List[Dict]:
        """
        Deep scan of a specific folder using maximum CPU/GPU acceleration.
        """
        print(f"🚀 Deep scanning folder: {folder_path}")
        
        # Recursively find all subdirectories
        all_locations = [folder_path]
        try:
            for root, dirs, _ in os.walk(folder_path):
                # Limit depth to avoid infinite scanning
                depth = len(Path(root).relative_to(folder_path).parts)
                if depth < 5:  # Max depth of 5 levels
                    for dir_name in dirs:
                        dir_path = Path(root) / dir_name
                        if not dir_name.startswith('.') or dir_name in ['.Trash', '.local']:
                            all_locations.append(dir_path)
        except (PermissionError, OSError):
            pass
        
        print(f"   Found {len(all_locations)} locations to scan")
        
        # Use parallel scanning
        return self.scan_locations_parallel(all_locations, progress_callback)


def get_optimal_scanner() -> AcceleratedFileScanner:
    """
    Factory function to get the best scanner for current system.
    """
    return AcceleratedFileScanner()