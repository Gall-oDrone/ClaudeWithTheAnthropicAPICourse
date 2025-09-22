#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the FormatAwareEvaluator class

This module tests the format-aware evaluation capabilities including:
- run_format_aware_eval method
- Enhanced display functionality
- Grading configuration handling
- JSON serialization with GradingResult objects
"""

import unittest
import os
import sys
import json
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.evaluator import FormatAwareEvaluator, GradingResultEncoder
from utils.graders import GradingResult, GradingCriteria, FormatGradingCriteria


class TestFormatAwareEvaluator(unittest.TestCase):
    """Test cases for the FormatAwareEvaluator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock chat client
        self.mock_chat_client = Mock()
        self.mock_chat_client.get_client.return_value = Mock()
        self.mock_chat_client.params = {"messages": []}
        self.mock_chat_client.send_message.return_value = "Mock response"
        
        # Create the evaluator
        self.evaluator = FormatAwareEvaluator(self.mock_chat_client)
        
        # Sample format-aware test dataset
        self.sample_dataset = [
            {
                "prompt": "Write a Python function that retrieves EC2 instances",
                "format": "python",
                "solution_criteria": "A Python function using boto3",
                "grading_config": {
                    "code": {
                        "min_length": 50,
                        "required_words": ["def", "boto3", "return"],
                        "syntax_check": True
                    }
                }
            },
            {
                "prompt": "Create a JSON object for Lambda configuration",
                "format": "json",
                "solution_criteria": "A valid JSON object with Lambda properties",
                "grading_config": {
                    "format": {
                        "required_fields": ["FunctionName", "Runtime"],
                        "forbidden_fields": ["AccessKeyId"],
                        "validate_json_schema": True
                    }
                }
            },
            {
                "prompt": "Write a regex for S3 bucket validation",
                "format": "regex",
                "solution_criteria": "A regex pattern for S3 bucket naming",
                "grading_config": {
                    "code": {
                        "min_length": 20,
                        "syntax_check": True
                    }
                }
            }
        ]
    
    def test_run_format_aware_eval_basic_functionality(self):
        """Test basic functionality of run_format_aware_eval."""
        # Mock the grader to return successful results
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
            "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
        }
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = self.evaluator.run_format_aware_eval(
                test_dataset=self.sample_dataset,
                save_results=False,
                verbose=False
            )
        
        # Verify results structure
        self.assertIn("total_tests", results)
        self.assertIn("passed_tests", results)
        self.assertIn("failed_tests", results)
        self.assertIn("pass_rate", results)
        self.assertIn("results", results)
        
        # Verify counts
        self.assertEqual(results["total_tests"], 3)
        self.assertEqual(results["passed_tests"], 3)
        self.assertEqual(results["failed_tests"], 0)
        self.assertEqual(results["pass_rate"], 1.0)
        self.assertEqual(len(results["results"]), 3)
    
    def test_run_format_aware_eval_with_failures(self):
        """Test run_format_aware_eval with some failing tests."""
        # Mock the grader to return mixed results
        mock_grader = Mock()
        mock_grader.grade_comprehensive.side_effect = [
            # First test passes
            {
                "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
                "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
            },
            # Second test fails
            {
                "code_grader": GradingResult(score=3.0, feedback="Syntax error", details={}, passed=False),
                "model_grader": GradingResult(score=7.0, feedback="Good", details={}, passed=True)
            },
            # Third test passes
            {
                "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
                "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
            }
        ]
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = self.evaluator.run_format_aware_eval(
                test_dataset=self.sample_dataset,
                save_results=False,
                verbose=False
            )
        
        # Verify results
        self.assertEqual(results["total_tests"], 3)
        self.assertEqual(results["passed_tests"], 2)
        self.assertEqual(results["failed_tests"], 1)
        self.assertAlmostEqual(results["pass_rate"], 2/3, places=2)
    
    def test_run_format_aware_eval_with_format_grading(self):
        """Test run_format_aware_eval with format-specific grading."""
        # Mock the grader to return format grading results
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "format_grader": GradingResult(score=9.0, feedback="Format valid", details={}, passed=True),
            "model_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True)
        }
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = self.evaluator.run_format_aware_eval(
                test_dataset=self.sample_dataset,
                save_results=False,
                verbose=False
            )
        
        # Verify that format grading was used
        self.assertEqual(results["total_tests"], 3)
        self.assertEqual(results["passed_tests"], 3)
    
    def test_run_format_aware_eval_verbose_output(self):
        """Test that verbose output works correctly."""
        # Capture stdout
        captured_output = StringIO()
        
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
            "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
        }
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            with patch('sys.stdout', captured_output):
                results = self.evaluator.run_format_aware_eval(
                    test_dataset=self.sample_dataset[:1],  # Just one test for speed
                    save_results=False,
                    verbose=True
                )
        
        # Check that verbose output was produced
        output = captured_output.getvalue()
        self.assertIn("🚀 Running Format-Aware Evaluation", output)
        self.assertIn("Test 1/1:", output)
        self.assertIn("Format: python", output)
        self.assertIn("✅ PASSED", output)
        self.assertIn("Format-Aware Evaluation Complete", output)
    
    def test_run_format_aware_eval_verbose_output_with_failures(self):
        """Test verbose output with failed tests shows detailed breakdown."""
        # Capture stdout
        captured_output = StringIO()
        
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "code_grader": GradingResult(score=3.0, feedback="Syntax error in function", details={}, passed=False),
            "format_grader": GradingResult(score=2.0, feedback="Missing required fields", details={}, passed=False),
            "model_grader": GradingResult(score=7.0, feedback="Good quality", details={}, passed=True)
        }
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            with patch('sys.stdout', captured_output):
                results = self.evaluator.run_format_aware_eval(
                    test_dataset=self.sample_dataset[:1],
                    save_results=False,
                    verbose=True
                )
        
        # Check that detailed failure output was produced
        output = captured_output.getvalue()
        self.assertIn("❌ FAILED", output)
        self.assertIn("Code Score: 3.0/10", output)
        self.assertIn("Format Score: 2.0/10", output)
        self.assertIn("Model Score: 7.0/10", output)
        self.assertIn("Issue: Syntax error in function", output)
        self.assertIn("Issue: Missing required fields", output)
    
    def test_run_format_aware_eval_save_results(self):
        """Test that results are saved to file when requested."""
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
            "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
        }
        
        test_file = "test_format_aware_results.json"
        
        try:
            with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
                results = self.evaluator.run_format_aware_eval(
                    test_dataset=self.sample_dataset[:1],
                    save_results=True,
                    results_path=test_file,
                    verbose=False
                )
            
            # Verify file was created
            self.assertTrue(os.path.exists(test_file))
            
            # Verify file contents can be loaded
            with open(test_file, 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(saved_data["total_tests"], 1)
            self.assertEqual(saved_data["passed_tests"], 1)
            self.assertIn("results", saved_data)
            
        finally:
            # Clean up
            if os.path.exists(test_file):
                os.remove(test_file)
    
    def test_run_format_aware_eval_error_handling(self):
        """Test error handling in run_format_aware_eval."""
        # Mock the grader to raise an exception
        mock_grader = Mock()
        mock_grader.grade_comprehensive.side_effect = Exception("Test error")
        
        with patch.object(self.evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = self.evaluator.run_format_aware_eval(
                test_dataset=self.sample_dataset[:1],
                save_results=False,
                verbose=False
            )
        
        # Verify error handling
        self.assertEqual(results["total_tests"], 1)
        self.assertEqual(results["passed_tests"], 0)
        self.assertEqual(results["failed_tests"], 1)
        self.assertEqual(results["pass_rate"], 0.0)
        
        # Check that error was recorded
        result = results["results"][0]
        self.assertFalse(result["passed"])
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Test error")
    
    def test_grading_result_encoder(self):
        """Test that GradingResultEncoder works correctly."""
        # Create a GradingResult object
        grading_result = GradingResult(
            score=8.5,
            feedback="Test feedback",
            details={"test": "value"},
            passed=True
        )
        
        # Test JSON encoding
        encoded = json.dumps(grading_result, cls=GradingResultEncoder)
        decoded = json.loads(encoded)
        
        # Verify encoding worked correctly
        self.assertEqual(decoded["score"], 8.5)
        self.assertEqual(decoded["feedback"], "Test feedback")
        self.assertEqual(decoded["details"], {"test": "value"})
        self.assertTrue(decoded["passed"])
    
    def test_run_format_aware_eval_with_empty_dataset(self):
        """Test run_format_aware_eval with empty dataset."""
        results = self.evaluator.run_format_aware_eval(
            test_dataset=[],
            save_results=False,
            verbose=False
        )
        
        # Verify empty dataset handling
        self.assertEqual(results["total_tests"], 0)
        self.assertEqual(results["passed_tests"], 0)
        self.assertEqual(results["failed_tests"], 0)
        self.assertEqual(results["pass_rate"], 0.0)
        self.assertEqual(len(results["results"]), 0)
    
    def test_run_format_aware_eval_criteria_application(self):
        """Test that grading criteria are properly applied per test case."""
        # This test verifies that the run_test_case_with_format method is called
        # which should apply the grading_config from each test case
        
        with patch.object(self.evaluator, 'run_test_case_with_format') as mock_run_with_format:
            mock_run_with_format.return_value = {
                "test_case": self.sample_dataset[0],
                "actual_response": "Mock response",
                "solution_criteria": "A Python function using boto3",
                "grading_results": {
                    "code_grader": GradingResult(score=8.0, feedback="Good", details={}, passed=True),
                    "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
                },
                "passed": True
            }
            
            results = self.evaluator.run_format_aware_eval(
                test_dataset=self.sample_dataset[:1],
                save_results=False,
                verbose=False
            )
        
        # Verify that run_test_case_with_format was called
        self.assertEqual(mock_run_with_format.call_count, 1)
        
        # Verify the call was made with the correct test case
        call_args = mock_run_with_format.call_args[0][0]
        self.assertEqual(call_args["prompt"], "Write a Python function that retrieves EC2 instances")
        self.assertEqual(call_args["format"], "python")
        self.assertIn("grading_config", call_args)


class TestFormatAwareEvaluatorIntegration(unittest.TestCase):
    """Integration tests for FormatAwareEvaluator."""
    
    def test_full_workflow_simulation(self):
        """Test the full workflow with realistic data."""
        # Create a mock chat client that returns different responses
        mock_chat_client = Mock()
        mock_chat_client.get_client.return_value = Mock()
        mock_chat_client.params = {"messages": []}
        
        # Mock different responses for different prompts
        def mock_send_message():
            # This would normally be called by the evaluator
            return "def get_ec2_instances(region):\n    import boto3\n    ec2 = boto3.client('ec2', region_name=region)\n    return ec2.describe_instances()"
        
        mock_chat_client.send_message.side_effect = mock_send_message
        
        # Create evaluator
        evaluator = FormatAwareEvaluator(mock_chat_client)
        
        # Test dataset with realistic grading configs
        test_dataset = [
            {
                "prompt": "Write a Python function that retrieves EC2 instances",
                "format": "python",
                "solution_criteria": "A Python function using boto3",
                "grading_config": {
                    "code": {
                        "min_length": 50,
                        "required_words": ["def", "boto3", "return"],
                        "syntax_check": True
                    }
                }
            }
        ]
        
        # Mock the grader to simulate realistic grading
        mock_grader = Mock()
        mock_grader.grade_comprehensive.return_value = {
            "code_grader": GradingResult(
                score=9.0, 
                feedback="Excellent Python function with proper boto3 usage", 
                details={"length_check": True, "syntax_check": True, "word_check": True}, 
                passed=True
            ),
            "model_grader": GradingResult(
                score=8.5, 
                feedback="Good response that addresses the prompt", 
                details={"quality": "high"}, 
                passed=True
            )
        }
        
        with patch.object(evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = evaluator.run_format_aware_eval(
                test_dataset=test_dataset,
                save_results=False,
                verbose=False
            )
        
        # Verify the full workflow
        self.assertEqual(results["total_tests"], 1)
        self.assertEqual(results["passed_tests"], 1)
        self.assertEqual(results["failed_tests"], 0)
        self.assertEqual(results["pass_rate"], 1.0)
        
        # Verify the result structure
        result = results["results"][0]
        self.assertIn("test_case", result)
        self.assertIn("actual_response", result)
        self.assertIn("grading_results", result)
        self.assertIn("passed", result)
        self.assertTrue(result["passed"])


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
