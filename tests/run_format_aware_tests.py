#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test runner for FormatAwareEvaluator tests

This script runs all the tests for the FormatAwareEvaluator class
and provides a summary of the results.
"""

import sys
import os
import unittest

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from test_format_aware_evaluator import TestFormatAwareEvaluator, TestFormatAwareEvaluatorIntegration


def run_tests():
    """Run all FormatAwareEvaluator tests."""
    print("🧪 Running FormatAwareEvaluator Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestFormatAwareEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatAwareEvaluatorIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print("\n💥 Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
