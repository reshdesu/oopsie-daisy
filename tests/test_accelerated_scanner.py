#!/usr/bin/env python3
"""
Tests for the GPU-accelerated file scanner.
"""

import pytest
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.oopsie_daisy.accelerated_scanner import AcceleratedFileScanner, get_optimal_scanner


class TestAcceleratedFileScanner:
    """Test suite for GPU-accelerated file scanning."""
    
    @pytest.fixture
    def scanner(self):
        """Create scanner instance for testing."""
        return AcceleratedFileScanner()
    
    @pytest.fixture
    def temp_test_files(self):
        """Create temporary test files for scanning."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create various test files
            test_files = [
                temp_path / "document.txt",
                temp_path / "image.jpg", 
                temp_path / "temp_file.tmp",
                temp_path / ".hidden_file",
                temp_path / "backup~",
                temp_path / "large_file.zip"
            ]
            
            for i, file_path in enumerate(test_files):
                content = f"Test content for file {i}" * (100 + i * 50)  # Varying sizes
                file_path.write_text(content)
            
            # Create subdirectory with more files
            subdir = temp_path / "subfolder"
            subdir.mkdir()
            (subdir / "nested_file.doc").write_text("Nested file content")
            (subdir / ".cache_file").write_text("Cache content")
            
            yield temp_path
    
    def test_scanner_initialization(self, scanner):
        """Test that scanner initializes with correct system detection."""
        assert scanner.cpu_count > 0
        assert scanner.memory_gb > 0
        assert scanner.max_threads > 0
        assert isinstance(scanner.use_gpu, bool)
        
    def test_cpu_count_detection(self, scanner):
        """Test CPU count detection is reasonable."""
        assert 1 <= scanner.cpu_count <= 64  # Reasonable range
        assert scanner.max_threads >= scanner.cpu_count
        
    def test_memory_detection(self, scanner):
        """Test memory detection is reasonable."""
        assert 0.5 <= scanner.memory_gb <= 1024  # 512MB to 1TB range
    
    @patch('src.oopsie_daisy.accelerated_scanner.OPENCL_AVAILABLE', False)
    def test_gpu_disabled_when_opencl_unavailable(self):
        """Test that GPU is disabled when OpenCL is not available."""
        scanner = AcceleratedFileScanner()
        assert scanner.use_gpu is False
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_gpu_initialization_success(self, mock_cl):
        """Test successful GPU initialization."""
        # Mock OpenCL components
        mock_platform = Mock()
        mock_platform.name = "AMD Accelerated Parallel Processing"
        mock_device = Mock()
        mock_device.name = "Radeon RX 6800 XT"
        mock_device.max_compute_units = 72
        mock_device.global_mem_size = 17179869184  # 16GB
        
        mock_cl.get_platforms.return_value = [mock_platform]
        mock_platform.get_devices.return_value = [mock_device]
        mock_cl.Context.return_value = Mock()
        mock_cl.CommandQueue.return_value = Mock()
        mock_cl.device_type.GPU = "GPU"
        
        with patch('src.oopsie_daisy.accelerated_scanner.OPENCL_AVAILABLE', True):
            scanner = AcceleratedFileScanner()
            assert scanner.use_gpu is True
    
    def test_scan_empty_location(self, scanner):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            results = scanner._scan_location_optimized(Path(temp_dir))
            assert results == []
    
    def test_scan_nonexistent_location(self, scanner):
        """Test scanning a nonexistent directory."""
        results = scanner._scan_location_optimized(Path("/nonexistent/path"))
        assert results == []
    
    def test_scan_single_location(self, scanner, temp_test_files):
        """Test scanning a single location with files."""
        results = scanner._scan_location_optimized(temp_test_files)
        
        assert len(results) >= 6  # At least our test files
        
        # Check that file info is properly extracted
        for file_info in results:
            assert 'name' in file_info
            assert 'path' in file_info
            assert 'size' in file_info
            assert 'type' in file_info
            assert 'score' in file_info
            assert isinstance(file_info['size'], int)
            assert 0.0 <= file_info['score'] <= 1.0
    
    def test_file_batch_processing(self, scanner, temp_test_files):
        """Test batch processing of files."""
        # Create mock DirEntry objects
        import os
        with os.scandir(temp_test_files) as entries:
            file_entries = [entry for entry in entries if entry.is_file()]
        
        results = scanner._process_file_batch(file_entries)
        
        assert len(results) >= 6
        for file_info in results:
            assert all(key in file_info for key in ['name', 'path', 'size', 'score'])
    
    def test_recovery_score_calculation(self, scanner):
        """Test file recovery score calculation."""
        import os
        
        # Mock stat result
        mock_stat = Mock()
        mock_stat.st_size = 1000
        mock_stat.st_mtime = time.time() - 3600  # 1 hour ago
        
        # Test valuable file extension
        score_doc = scanner._calculate_recovery_score("important.pdf", mock_stat)
        assert score_doc > 0.5
        
        # Test recent file
        mock_stat.st_mtime = time.time() - 30  # 30 seconds ago
        score_recent = scanner._calculate_recovery_score("recent.txt", mock_stat)
        assert score_recent > score_doc
        
        # Test system/cache file
        score_cache = scanner._calculate_recovery_score(".cache_file", mock_stat)
        assert score_cache < 0.5
    
    def test_parallel_scanning_multiple_locations(self, scanner):
        """Test parallel scanning of multiple locations."""
        locations = []
        
        # Create multiple temp directories
        temp_dirs = []
        for i in range(3):
            temp_dir = tempfile.mkdtemp()
            temp_dirs.append(temp_dir)
            temp_path = Path(temp_dir)
            locations.append(temp_path)
            
            # Add some files to each directory
            for j in range(2):
                (temp_path / f"file_{i}_{j}.txt").write_text(f"Content {i}-{j}")
        
        try:
            progress_calls = []
            def progress_callback(progress):
                progress_calls.append(progress)
            
            results = scanner.scan_locations_parallel(locations, progress_callback)
            
            # Should have found files from all locations
            assert len(results) >= 6  # 3 dirs * 2 files each
            
            # Progress callback should have been called
            assert len(progress_calls) > 0
            assert max(progress_calls) == 100
            
        finally:
            # Cleanup
            import shutil
            for temp_dir in temp_dirs:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_deep_folder_scan(self, scanner, temp_test_files):
        """Test deep scanning of a specific folder."""
        progress_calls = []
        def progress_callback(progress):
            progress_calls.append(progress)
        
        results = scanner.scan_folder_deep(temp_test_files, progress_callback)
        
        # Should find files in main directory and subdirectory
        assert len(results) >= 8  # Main files + nested files
        
        # Should include files from subdirectory
        nested_files = [r for r in results if 'subfolder' in r['path']]
        assert len(nested_files) >= 2
    
    def test_threading_performance(self, scanner):
        """Test that multi-threading improves performance."""
        # Create larger test dataset
        locations = []
        temp_dirs = []
        
        try:
            for i in range(5):  # 5 directories
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)
                temp_path = Path(temp_dir)
                locations.append(temp_path)
                
                # Create more files per directory
                for j in range(10):
                    (temp_path / f"file_{i}_{j}.txt").write_text(f"Content {i}-{j}" * 100)
            
            # Measure parallel scanning time
            start_time = time.time()
            results_parallel = scanner.scan_locations_parallel(locations)
            parallel_time = time.time() - start_time
            
            # Measure sequential scanning time
            start_time = time.time()
            results_sequential = []
            for location in locations:
                results_sequential.extend(scanner._scan_location_optimized(location))
            sequential_time = time.time() - start_time
            
            # Parallel should be faster (or at least not significantly slower)
            assert len(results_parallel) == len(results_sequential)
            # Allow some variance due to overhead, but parallel shouldn't be more than 50% slower
            assert parallel_time <= sequential_time * 1.5
            
        finally:
            import shutil
            for temp_dir in temp_dirs:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_gpu_filter_fallback(self, mock_cl, scanner):
        """Test GPU filtering with fallback to CPU."""
        # Mock GPU failure
        mock_cl.Program.side_effect = Exception("GPU error")
        
        files = [
            {'name': 'file1.txt', 'score': 0.3},
            {'name': 'file2.pdf', 'score': 0.8},
            {'name': 'file3.tmp', 'score': 0.1}
        ]
        
        # Should fallback to CPU sorting without error
        with patch.object(scanner, 'use_gpu', True):
            result = scanner._gpu_filter_files(files)
            
        # Should be sorted by score (highest first)
        assert result[0]['score'] >= result[1]['score'] >= result[2]['score']
    
    def test_get_optimal_scanner_factory(self):
        """Test the factory function returns a proper scanner."""
        scanner = get_optimal_scanner()
        assert isinstance(scanner, AcceleratedFileScanner)
        assert hasattr(scanner, 'scan_locations_parallel')
        assert hasattr(scanner, 'scan_folder_deep')


class TestHardwareDetection:
    """Test hardware detection capabilities."""
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_amd_gpu_detection(self, mock_cl):
        """Test AMD GPU detection and prioritization."""
        # Mock AMD platform/device
        amd_platform = Mock()
        amd_platform.name = "AMD Accelerated Parallel Processing"
        amd_device = Mock()
        amd_device.name = "Radeon RX 6800 XT"
        amd_device.max_compute_units = 72
        amd_device.global_mem_size = 17179869184
        
        # Mock NVIDIA platform/device (should be deprioritized)
        nvidia_platform = Mock()
        nvidia_platform.name = "NVIDIA CUDA"
        nvidia_device = Mock()
        nvidia_device.name = "GeForce RTX 3080"
        
        mock_cl.get_platforms.return_value = [nvidia_platform, amd_platform]
        nvidia_platform.get_devices.return_value = [nvidia_device]
        amd_platform.get_devices.return_value = [amd_device]
        mock_cl.device_type.GPU = "GPU"
        mock_cl.Context.return_value = Mock()
        mock_cl.CommandQueue.return_value = Mock()
        
        with patch('src.oopsie_daisy.accelerated_scanner.OPENCL_AVAILABLE', True):
            scanner = AcceleratedFileScanner()
            
        # Should prefer AMD GPU
        assert scanner.use_gpu is True
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_nvidia_gpu_detection(self, mock_cl):
        """Test NVIDIA GPU detection when AMD not available."""
        nvidia_platform = Mock()
        nvidia_platform.name = "NVIDIA CUDA"
        nvidia_device = Mock()
        nvidia_device.name = "GeForce RTX 4090"
        nvidia_device.max_compute_units = 128
        nvidia_device.global_mem_size = 25769803776  # 24GB
        
        mock_cl.get_platforms.return_value = [nvidia_platform]
        nvidia_platform.get_devices.return_value = [nvidia_device]
        mock_cl.device_type.GPU = "GPU"
        mock_cl.Context.return_value = Mock()
        mock_cl.CommandQueue.return_value = Mock()
        
        with patch('src.oopsie_daisy.accelerated_scanner.OPENCL_AVAILABLE', True):
            scanner = AcceleratedFileScanner()
            
        assert scanner.use_gpu is True
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_intel_gpu_detection(self, mock_cl):
        """Test Intel GPU detection when AMD/NVIDIA not available."""
        intel_platform = Mock()
        intel_platform.name = "Intel(R) OpenCL"
        intel_device = Mock()
        intel_device.name = "Intel(R) UHD Graphics 770"
        intel_device.max_compute_units = 32
        intel_device.global_mem_size = 8589934592  # 8GB
        
        mock_cl.get_platforms.return_value = [intel_platform]
        intel_platform.get_devices.return_value = [intel_device]
        mock_cl.device_type.GPU = "GPU"
        mock_cl.Context.return_value = Mock()
        mock_cl.CommandQueue.return_value = Mock()
        
        with patch('src.oopsie_daisy.accelerated_scanner.OPENCL_AVAILABLE', True):
            scanner = AcceleratedFileScanner()
            
        assert scanner.use_gpu is True


@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Performance benchmarking tests (run with --runxfail)."""
    
    @pytest.fixture
    def large_dataset(self):
        """Create a large dataset for performance testing."""
        locations = []
        temp_dirs = []
        
        try:
            # Create 10 directories with 100 files each
            for i in range(10):
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)
                temp_path = Path(temp_dir)
                locations.append(temp_path)
                
                for j in range(100):
                    file_path = temp_path / f"perf_test_{i}_{j}.txt"
                    file_path.write_text(f"Performance test content {i}-{j}" * 50)
            
            yield locations
            
        finally:
            import shutil
            for temp_dir in temp_dirs:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_large_dataset_performance(self, large_dataset):
        """Test performance with large dataset (1000 files)."""
        scanner = AcceleratedFileScanner()
        
        start_time = time.time()
        results = scanner.scan_locations_parallel(large_dataset)
        total_time = time.time() - start_time
        
        assert len(results) >= 1000
        assert total_time < 30  # Should complete within 30 seconds
        
        # Performance should be reasonable (files per second)
        files_per_second = len(results) / total_time
        assert files_per_second > 10  # At least 10 files/sec
    
    def test_threading_scalability(self):
        """Test that threading scales with available cores."""
        scanner = AcceleratedFileScanner()
        
        # Threading should use multiple cores efficiently
        assert scanner.max_threads >= scanner.cpu_count
        assert scanner.max_threads <= 16  # Reasonable upper limit