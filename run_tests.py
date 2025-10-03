#!/usr/bin/env python3
"""
Stacktalk Test Runner

Runs unit tests, integration tests, or all tests for the Stacktalk system.
"""

import sys
import unittest
import argparse
from pathlib import Path

# Add src directory to path for imports
sys.path.append(str(Path(__file__).parent / "src"))


def discover_and_run_tests(test_dir: str, pattern: str = "test_*.py", verbosity: int = 2):
    """
    Discover and run tests from a directory
    
    Args:
        test_dir: Directory to search for tests
        pattern: Test file pattern to match
        verbosity: Test output verbosity level
    """
    loader = unittest.TestLoader()
    start_dir = str(Path(__file__).parent / "tests" / test_dir)
    suite = loader.discover(start_dir, pattern=pattern)
    
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    return result.wasSuccessful()


def run_unit_tests(verbosity: int = 2):
    """Run all unit tests"""
    print("\n🧪 Running Unit Tests...")
    print("=" * 50)
    success = discover_and_run_tests("unit", verbosity=verbosity)
    
    if success:
        print("\n✅ All unit tests passed!")
    else:
        print("\n❌ Some unit tests failed!")
    
    return success


def run_integration_tests(verbosity: int = 2):
    """Run all integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    success = discover_and_run_tests("integration", verbosity=verbosity)
    
    if success:
        print("\n✅ All integration tests passed!")
    else:
        print("\n❌ Some integration tests failed!")
    
    return success


def run_all_tests(verbosity: int = 2):
    """Run all tests (unit + integration)"""
    print("\n🏦 Running All Stacktalk Tests...")
    print("=" * 60)
    
    unit_success = run_unit_tests(verbosity)
    integration_success = run_integration_tests(verbosity)
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"   Unit Tests: {'✅ PASSED' if unit_success else '❌ FAILED'}")
    print(f"   Integration Tests: {'✅ PASSED' if integration_success else '❌ FAILED'}")
    
    overall_success = unit_success and integration_success
    if overall_success:
        print("\n🎉 All tests passed! Stacktalk is ready for production.")
    else:
        print("\n⚠️ Some tests failed. Please review the output above.")
    
    return overall_success


def run_specific_test(test_path: str, verbosity: int = 2):
    """Run a specific test file"""
    print(f"\n🎯 Running Specific Test: {test_path}")
    print("=" * 50)
    
    # Handle both full paths and relative paths
    if test_path.startswith("tests/"):
        test_file = Path(__file__).parent / test_path
    else:
        test_file = Path(__file__).parent / "tests" / test_path
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    # Convert file path to module path
    module_path = str(test_file.relative_to(Path(__file__).parent)).replace("/", ".").replace("\\", ".")[:-3]
    
    try:
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module_path)
        runner = unittest.TextTestRunner(verbosity=verbosity)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print(f"\n✅ Test {test_path} passed!")
        else:
            print(f"\n❌ Test {test_path} failed!")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Error running test {test_path}: {e}")
        return False


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(
        description="Stacktalk Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --unit                    # Run unit tests only
  python run_tests.py --integration            # Run integration tests only
  python run_tests.py --all                    # Run all tests (default)
  python run_tests.py --test tests/unit/test_dsl_parser.py  # Run specific test
  python run_tests.py --unit --verbose         # Run unit tests with verbose output
        """
    )
    
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    parser.add_argument('--test', type=str, help='Run specific test file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose test output')
    parser.add_argument('--quiet', '-q', action='store_true', help='Quiet test output')
    
    args = parser.parse_args()
    
    # Determine verbosity level
    verbosity = 2  # Default
    if args.verbose:
        verbosity = 2
    elif args.quiet:
        verbosity = 1
    
    # Determine which tests to run
    if args.test:
        success = run_specific_test(args.test, verbosity)
    elif args.unit:
        success = run_unit_tests(verbosity)
    elif args.integration:
        success = run_integration_tests(verbosity)
    else:  # Default or --all
        success = run_all_tests(verbosity)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
