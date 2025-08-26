#!/usr/bin/env python3
"""
Integration tests for GPU acceleration and full system functionality.
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch

from src.oopsie_daisy.accelerated_scanner import AcceleratedFileScanner
from src.oopsie_daisy.app import OopsieDaisyMainWindow, AcceleratedScanThread


class TestGPUIntegration:
    """Test GPU acceleration integration with the full application."""
    
    @pytest.fixture
    def large_test_dataset(self):
        """Create a large dataset for GPU performance testing."""
        locations = []
        temp_dirs = []
        
        try:
            # Create multiple directories with many files
            for i in range(5):
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)
                temp_path = Path(temp_dir)
                locations.append(temp_path)
                
                # Create different file types
                file_types = [
                    ('.txt', 'Text document'),
                    ('.pdf', 'PDF document'), 
                    ('.jpg', 'JPEG image'),
                    ('.docx', 'Word document'),
                    ('.xlsx', 'Excel spreadsheet'),
                    ('.tmp', 'Temporary file'),
                    ('.log', 'Log file'),
                    ('.cache', 'Cache file'),
                    ('.bak', 'Backup file'),
                    ('~', 'Backup suffix')
                ]
                
                for j in range(20):  # 20 files per directory
                    ext, desc = file_types[j % len(file_types)]
                    filename = f"file_{i}_{j}{ext}"
                    content = f"{desc} content for {filename}" * 10
                    (temp_path / filename).write_text(content)
            
            yield locations
            
        finally:
            import shutil
            for temp_dir in temp_dirs:
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_gpu_vs_cpu_performance_comparison(self, large_test_dataset):
        """Compare GPU-accelerated vs CPU-only performance."""
        scanner = AcceleratedFileScanner()
        
        # Test with GPU (if available)
        gpu_available = scanner.use_gpu
        
        start_time = time.time()
        results_accelerated = scanner.scan_locations_parallel(large_test_dataset)
        accelerated_time = time.time() - start_time
        
        # Force CPU-only mode
        original_gpu = scanner.use_gpu
        scanner.use_gpu = False
        
        start_time = time.time()
        results_cpu = scanner.scan_locations_parallel(large_test_dataset)
        cpu_time = time.time() - start_time
        
        # Restore original setting
        scanner.use_gpu = original_gpu
        
        # Results should be similar
        assert len(results_accelerated) == len(results_cpu)
        
        # Performance should be reasonable
        assert accelerated_time < 30  # Should complete within 30 seconds
        assert cpu_time < 30
        
        if gpu_available:
            # GPU might be faster for large datasets, but not always
            print(f"GPU+CPU time: {accelerated_time:.2f}s, CPU-only time: {cpu_time:.2f}s")
    
    def test_end_to_end_gpu_accelerated_scan(self, large_test_dataset, qtbot):
        """Test complete workflow with GPU acceleration."""
        app = OopsieDaisyMainWindow()
        qtbot.addWidget(app)
        
        # Mock folder selection
        test_folder = large_test_dataset[0]  # Use first test directory
        
        with patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory') as mock_dialog:
            mock_dialog.return_value = str(test_folder)
            
            # Track scan completion
            scan_completed = []
            app.recovery_thread.finished.connect(lambda: scan_completed.append(True))
            
            # Start folder scan
            qtbot.mouseClick(app.folder_scan_button, Qt.LeftButton)
            
            # Wait for completion
            qtbot.waitUntil(lambda: len(scan_completed) > 0, timeout=30000)  # 30 second timeout
            
            # Verify results
            assert len(app.found_files) > 0
            assert app.files_list.count() > 0
            assert app.restore_button.isEnabled()
    
    def test_gpu_hardware_detection_integration(self):
        """Test that GPU hardware detection works in real application context."""
        scanner = AcceleratedFileScanner()
        
        # Should have initialized without errors
        assert isinstance(scanner.cpu_count, int)
        assert scanner.cpu_count > 0
        assert isinstance(scanner.memory_gb, float)
        assert scanner.memory_gb > 0
        assert isinstance(scanner.use_gpu, bool)
        
        # Test that scanner methods work regardless of GPU availability
        test_locations = [Path.home() / "Downloads"]  # Use a real directory
        if test_locations[0].exists():
            results = scanner.scan_locations_parallel(test_locations)
            assert isinstance(results, list)
    
    @patch('src.oopsie_daisy.accelerated_scanner.cl')
    def test_opencl_error_handling_integration(self, mock_cl):
        """Test that OpenCL errors are handled gracefully."""
        # Mock OpenCL to raise various errors
        mock_cl.get_platforms.side_effect = Exception("OpenCL driver error")
        
        # Scanner should still initialize
        scanner = AcceleratedFileScanner()
        assert scanner.use_gpu is False  # Should fallback to CPU-only
        
        # Should still be able to scan
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            (temp_path / "test.txt").write_text("Test content")
            
            results = scanner.scan_locations_parallel([temp_path])
            assert len(results) >= 1
    
    def test_memory_efficiency_with_large_datasets(self, large_test_dataset):
        """Test memory usage doesn't grow excessively with large datasets."""
        import psutil
        import os
        
        scanner = AcceleratedFileScanner()
        process = psutil.Process(os.getpid())
        
        # Measure initial memory
        initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
        
        # Scan large dataset
        results = scanner.scan_locations_parallel(large_test_dataset)
        
        # Measure memory after scan
        final_memory = process.memory_info().rss / (1024 * 1024)  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 500MB for test dataset)
        assert memory_increase < 500
        assert len(results) > 0
    
    def test_concurrent_scans_prevention(self, qtbot):
        """Test that concurrent GPU scans are properly prevented."""
        app = OopsieDaisyMainWindow()
        qtbot.addWidget(app)
        
        # Mock a long-running scan
        with patch('src.oopsie_daisy.app.AcceleratedScanThread') as mock_thread_class:
            mock_thread = Mock()
            mock_thread.isRunning.return_value = True
            mock_thread_class.return_value = mock_thread
            
            # Set up mock thread
            app.recovery_thread = mock_thread
            
            # Try to start another scan
            with patch('src.oopsie_daisy.app.QFileDialog.getExistingDirectory') as mock_dialog:
                qtbot.mouseClick(app.folder_scan_button, Qt.LeftButton)
                
                # Dialog should not be called because scan is already running
                assert not mock_dialog.called
    
    def test_progress_reporting_accuracy(self, large_test_dataset):
        """Test that progress reporting is accurate and reasonable."""
        folder_path = large_test_dataset[0]
        thread = AcceleratedScanThread(str(folder_path))
        
        progress_values = []
        thread.progress_updated.connect(progress_values.append)
        
        thread.run()
        
        if progress_values:
            # Progress should be reasonable
            assert all(0 <= p <= 100 for p in progress_values)
            # Should have some progression
            assert len(set(progress_values)) > 1  # Not all the same value
    
    def test_file_type_scoring_integration(self, large_test_dataset):
        """Test that file scoring works correctly in integrated environment."""
        scanner = AcceleratedFileScanner()
        results = scanner.scan_locations_parallel(large_test_dataset)
        
        # All results should have scores
        assert all('score' in file_info for file_info in results)
        assert all(0.0 <= file_info['score'] <= 1.0 for file_info in results)
        
        # Different file types should have different average scores
        pdf_scores = [f['score'] for f in results if f['name'].endswith('.pdf')]
        tmp_scores = [f['score'] for f in results if f['name'].endswith('.tmp')]
        
        if pdf_scores and tmp_scores:
            avg_pdf = sum(pdf_scores) / len(pdf_scores)
            avg_tmp = sum(tmp_scores) / len(tmp_scores)
            # PDFs should generally score higher than temp files
            assert avg_pdf > avg_tmp
    
    def test_error_recovery_in_gpu_scan(self):
        """Test error recovery when GPU scan encounters problems."""
        # Test with non-existent directory
        thread = AcceleratedScanThread("/definitely/does/not/exist")
        
        results = []
        errors = []
        finished = []
        
        thread.files_found.connect(results.append)
        thread.finished.connect(lambda: finished.append(True))
        
        # Should complete without crashing
        thread.run()
        
        assert len(finished) == 1
        assert len(results) == 1
        assert results[0] == []  # Empty results for non-existent directory


@pytest.mark.slow
class TestRealWorldScenarios:
    """Test real-world scanning scenarios."""
    
    def test_realistic_user_folder_scan(self):
        """Test scanning a realistic user folder structure."""
        # Use user's actual Downloads folder if it exists
        downloads_folder = Path.home() / "Downloads"
        if not downloads_folder.exists():
            pytest.skip("Downloads folder not available")
        
        scanner = AcceleratedFileScanner()
        
        # This is a real scan that might take time
        start_time = time.time()
        results = scanner.scan_folder_deep(downloads_folder)
        scan_time = time.time() - start_time
        
        # Basic sanity checks
        assert isinstance(results, list)
        assert scan_time < 60  # Should complete within 1 minute
        
        if results:
            # All results should have required fields
            for file_info in results:
                assert 'name' in file_info
                assert 'path' in file_info
                assert 'size' in file_info
                assert isinstance(file_info['size'], int)
    
    def test_cross_platform_compatibility(self):
        """Test that GPU scanner works across platforms."""
        scanner = AcceleratedFileScanner()
        
        # Should initialize on any platform
        assert scanner.cpu_count > 0
        assert scanner.memory_gb > 0
        
        # Should handle platform-specific paths
        import platform
        system = platform.system().lower()
        
        if system == "windows":
            # Test Windows paths
            test_path = Path("C:/") if Path("C:/").exists() else Path.home()
        elif system == "darwin":
            # Test macOS paths
            test_path = Path("/Applications") if Path("/Applications").exists() else Path.home()
        else:
            # Test Linux paths
            test_path = Path("/tmp") if Path("/tmp").exists() else Path.home()
        
        if test_path.exists():
            results = scanner._scan_location_optimized(test_path)
            assert isinstance(results, list)