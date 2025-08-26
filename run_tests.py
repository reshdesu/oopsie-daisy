#!/usr/bin/env python3
"""
Test runner script for Oopsie Daisy UI testing.
This script provides an easy way to run all tests or specific test categories.
"""

import sys
import subprocess
import os
from pathlib import Path


def run_tests(test_type="all", verbose=True, coverage=True):
    """
    Run tests with specified parameters.
    
    Args:
        test_type: Type of tests to run ("all", "ui", "integration", "unit")
        verbose: Whether to show verbose output
        coverage: Whether to generate coverage report
    """
    
    # Ensure we're in the project directory
    os.chdir(Path(__file__).parent)
    
    # Base command
    cmd = ["uv", "run", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=src/oopsie_daisy", "--cov-report=term-missing"])
    
    # Select test type
    if test_type == "ui":
        cmd.extend(["-m", "ui", "tests/test_ui.py", "tests/test_automated_interactions.py"])
    elif test_type == "integration":
        cmd.extend(["-m", "integration", "tests/test_integration.py"])
    elif test_type == "unit":
        cmd.extend(["tests/", "-m", "not ui and not integration"])
    else:  # all
        cmd.append("tests/")
    
    print(f"Running command: {' '.join(cmd)}")
    return subprocess.run(cmd)


if __name__ == "__main__":
    test_type = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print(f"🐱 Running {test_type} tests for Oopsie Daisy...")
    result = run_tests(test_type)
    
    if result.returncode == 0:
        print("🎉 All tests passed!")
    else:
        print("😿 Some tests failed.")
    
    sys.exit(result.returncode)