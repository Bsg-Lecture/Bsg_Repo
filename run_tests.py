#!/usr/bin/env python3
"""
Test Runner for EmuOCPP

Runs all automated tests for setup validation.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Discover and run all tests"""
    loader = unittest.TestLoader()
    start_dir = project_root / 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def run_config_tests():
    """Run only configuration validation tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_config_validation')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


def run_connectivity_tests():
    """Run only connectivity tests"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_connectivity')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == 'config':
            print("Running configuration validation tests...\n")
            sys.exit(run_config_tests())
        elif test_type == 'connectivity':
            print("Running connectivity tests...\n")
            sys.exit(run_connectivity_tests())
        elif test_type == 'all':
            print("Running all tests...\n")
            sys.exit(run_all_tests())
        else:
            print(f"Unknown test type: {test_type}")
            print("Usage: python run_tests.py [all|config|connectivity]")
            sys.exit(1)
    else:
        print("Running all tests...\n")
        sys.exit(run_all_tests())
