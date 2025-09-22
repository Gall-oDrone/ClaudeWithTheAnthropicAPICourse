#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Demo script for FormatAwareEvaluator

This script demonstrates the new run_format_aware_eval method
with a realistic example dataset.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.evaluator import FormatAwareEvaluator
from utils.graders import GradingResult


def create_demo_dataset():
    """Create a demo dataset for testing."""
    return [
        {
            "prompt": "Write a Python function that retrieves the list of EC2 instances in a specific AWS region",
            "format": "python",
            "solution_criteria": "A Python function using boto3 to list EC2 instances",
            "grading_config": {
                "code": {
                    "min_length": 100,
                    "required_words": ["def", "boto3", "ec2", "return"],
                    "syntax_check": True
                }
            }
        },
        {
            "prompt": "Create a JSON object that represents an AWS Lambda function configuration",
            "format": "json", 
            "solution_criteria": "A valid JSON object with Lambda configuration properties",
            "grading_config": {
                "format": {
                    "required_fields": ["FunctionName", "Runtime", "Handler", "Role"],
                    "forbidden_fields": ["AccessKeyId", "SecretAccessKey"],
                    "validate_json_schema": True,
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "FunctionName": {"type": "string"},
                            "Runtime": {"type": "string"},
                            "Handler": {"type": "string"},
                            "Role": {"type": "string"},
                            "MemorySize": {"type": "number"},
                            "Timeout": {"type": "number"}
                        },
                        "required": ["FunctionName", "Runtime", "Handler", "Role"]
                    }
                }
            }
        },
        {
            "prompt": "Write a regular expression to validate an AWS S3 bucket name",
            "format": "regex",
            "solution_criteria": "A regex pattern that validates S3 bucket naming rules",
            "grading_config": {
                "code": {
                    "min_length": 20,
                    "syntax_check": True
                }
            }
        }
    ]


def demo_successful_evaluation():
    """Demo with all tests passing."""
    print("🎯 Demo 1: Successful Evaluation")
    print("=" * 50)
    
    # Create mock chat client
    mock_chat_client = Mock()
    mock_chat_client.get_client.return_value = Mock()
    mock_chat_client.params = {"messages": []}
    mock_chat_client.send_message.return_value = "def get_ec2_instances(region):\n    import boto3\n    ec2 = boto3.client('ec2', region_name=region)\n    return ec2.describe_instances()"
    
    # Create evaluator
    evaluator = FormatAwareEvaluator(mock_chat_client)
    
    # Mock successful grading
    mock_grader = Mock()
    mock_grader.grade_comprehensive.return_value = {
        "code_grader": GradingResult(score=9.0, feedback="Excellent Python function", details={}, passed=True),
        "model_grader": GradingResult(score=8.5, feedback="Good response", details={}, passed=True)
    }
    
    with patch.object(evaluator, '_get_or_create_grader', return_value=mock_grader):
        results = evaluator.run_format_aware_eval(
            test_dataset=create_demo_dataset()[:1],  # Just first test
            save_results=False,
            verbose=True
        )
    
    print(f"\nResults: {results['passed_tests']}/{results['total_tests']} passed")


def demo_mixed_evaluation():
    """Demo with mixed results (some pass, some fail)."""
    print("\n🎯 Demo 2: Mixed Results Evaluation")
    print("=" * 50)
    
    # Create mock chat client
    mock_chat_client = Mock()
    mock_chat_client.get_client.return_value = Mock()
    mock_chat_client.params = {"messages": []}
    mock_chat_client.send_message.return_value = "def get_ec2_instances(region):\n    import boto3\n    ec2 = boto3.client('ec2', region_name=region)\n    return ec2.describe_instances()"
    
    # Create evaluator
    evaluator = FormatAwareEvaluator(mock_chat_client)
    
    # Mock mixed grading results
    mock_grader = Mock()
    mock_grader.grade_comprehensive.side_effect = [
        # First test passes
        {
            "code_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True),
            "model_grader": GradingResult(score=8.5, feedback="Good", details={}, passed=True)
        },
        # Second test fails
        {
            "code_grader": GradingResult(score=3.0, feedback="Syntax error in function", details={}, passed=False),
            "format_grader": GradingResult(score=2.0, feedback="Missing required fields", details={}, passed=False),
            "model_grader": GradingResult(score=7.0, feedback="Good quality", details={}, passed=True)
        },
        # Third test passes
        {
            "code_grader": GradingResult(score=8.0, feedback="Good regex", details={}, passed=True),
            "model_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True)
        }
    ]
    
    with patch.object(evaluator, '_get_or_create_grader', return_value=mock_grader):
        results = evaluator.run_format_aware_eval(
            test_dataset=create_demo_dataset(),
            save_results=False,
            verbose=True
        )
    
    print(f"\nResults: {results['passed_tests']}/{results['total_tests']} passed")


def demo_save_results():
    """Demo saving results to file."""
    print("\n🎯 Demo 3: Save Results to File")
    print("=" * 50)
    
    # Create mock chat client
    mock_chat_client = Mock()
    mock_chat_client.get_client.return_value = Mock()
    mock_chat_client.params = {"messages": []}
    mock_chat_client.send_message.return_value = "def get_ec2_instances(region):\n    import boto3\n    ec2 = boto3.client('ec2', region_name=region)\n    return ec2.describe_instances()"
    
    # Create evaluator
    evaluator = FormatAwareEvaluator(mock_chat_client)
    
    # Mock successful grading
    mock_grader = Mock()
    mock_grader.grade_comprehensive.return_value = {
        "code_grader": GradingResult(score=9.0, feedback="Excellent", details={}, passed=True),
        "model_grader": GradingResult(score=8.5, feedback="Good", details={}, passed=True)
    }
    
    results_file = "demo_format_aware_results.json"
    
    try:
        with patch.object(evaluator, '_get_or_create_grader', return_value=mock_grader):
            results = evaluator.run_format_aware_eval(
                test_dataset=create_demo_dataset()[:1],
                save_results=True,
                results_path=results_file,
                verbose=True
            )
        
        print(f"✅ Results saved to {results_file}")
        
        # Show file contents
        import json
        with open(results_file, 'r') as f:
            saved_data = json.load(f)
        
        print(f"📄 File contains {saved_data['total_tests']} test(s)")
        print(f"📊 Pass rate: {saved_data['pass_rate']:.1%}")
        
    finally:
        # Clean up
        if os.path.exists(results_file):
            os.remove(results_file)
            print(f"🧹 Cleaned up {results_file}")


def main():
    """Run all demos."""
    print("🚀 FormatAwareEvaluator Demo")
    print("=" * 50)
    print("This demo shows the new run_format_aware_eval method in action.")
    print("It demonstrates enhanced display, detailed grading breakdown,")
    print("and proper handling of format-specific grading configurations.")
    
    # Run demos
    demo_successful_evaluation()
    demo_mixed_evaluation()
    demo_save_results()
    
    print("\n🎉 Demo Complete!")
    print("=" * 50)
    print("Key features demonstrated:")
    print("✅ Enhanced display with emojis and progress tracking")
    print("✅ Detailed grading breakdown for failed tests")
    print("✅ Format-specific grading configuration")
    print("✅ Results saving with JSON serialization")
    print("✅ Error handling and mixed result scenarios")


if __name__ == "__main__":
    main()
