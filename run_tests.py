#!/usr/bin/env python3
"""
Test runner for room management functionality
"""
import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_room_tests():
    """Run room management tests"""
    print("🧪 Running Room Management Tests...")
    print("=" * 50)
    
    # Load and run room management tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromName('tests.test_room_management')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Some tests failed!")
        return False

def run_all_tests():
    """Run all tests"""
    print("🧪 Running All Tests...")
    print("=" * 50)
    
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run tests for the party room backend')
    parser.add_argument('--room-only', action='store_true', 
                       help='Run only room management tests')
    parser.add_argument('--all', action='store_true', 
                       help='Run all tests')
    
    args = parser.parse_args()
    
    if args.room_only:
        success = run_room_tests()
    elif args.all:
        success = run_all_tests()
    else:
        print("Please specify --room-only or --all")
        print("Usage:")
        print("  python3 run_tests.py --room-only  # Run room management tests")
        print("  python3 run_tests.py --all        # Run all tests")
        sys.exit(1)
    
    sys.exit(0 if success else 1)
