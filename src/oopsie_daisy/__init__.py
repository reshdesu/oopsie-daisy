def main() -> None:
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Oopsie Daisy - File Recovery Tool")
        print("Application loaded successfully")
        
        # Test Windows GUI functionality including Qt components
        try:
            # Test core recovery engine
            from .advanced_recovery import AdvancedRecoveryEngine
            print("Recovery engine import successful")
            
            # Test platform detection
            import platform
            system = platform.system()
            print(f"Platform detected: {system}")
            
            # Test Qt-based hardware monitoring (critical for Windows GUI)
            from .hardware_monitor_qt import HardwareMonitor
            print("Hardware monitor import successful")
            
            # Test GUI components (this is what we want to validate on Windows)
            from .recovery_wizard import DriveSelectionWidget
            print("UI components import successful")
            
            # Test that we can create core components
            engine = AdvancedRecoveryEngine()
            print("Recovery engine creation successful")
            
            # Test hardware monitor creation (Windows GUI functionality)
            monitor = HardwareMonitor()
            print("Hardware monitor creation successful")
            
            print("All Windows GUI functionality tests passed!")
            return
            
        except Exception as e:
            print(f"Import test failed: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    # Normal GUI mode
    from .app import run_app
    run_app()
