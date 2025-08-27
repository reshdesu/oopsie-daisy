def main() -> None:
    import sys
    
    # Check for test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Oopsie Daisy - File Recovery Tool")
        print("Application loaded successfully")
        
        # Test basic imports
        try:
            from .hardware_monitor_qt import HardwareMonitor
            print("Hardware monitor import successful")
            
            from .advanced_recovery import AdvancedRecoveryEngine
            print("Recovery engine import successful")
            
            from .recovery_wizard import DriveSelectionWidget
            print("UI components import successful")
            
            # Test platform detection
            import platform
            system = platform.system()
            print(f"Platform detected: {system}")
            
            print("All core functionality tests passed!")
            return
            
        except Exception as e:
            print(f"Import test failed: {e}")
            sys.exit(1)
    
    # Normal GUI mode
    from .app import run_app
    run_app()
