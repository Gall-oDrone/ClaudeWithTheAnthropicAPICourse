#!/usr/bin/env python3
"""
Example demonstrating the FormatAwareEvaluator with enhanced display.

This example shows how to use the new run_format_aware_eval method
with the enhanced display logic that provides detailed grading breakdown.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.evaluator import FormatAwareEvaluator
from utils.anthropic_client import AnthropicClient

# Example format-aware dataset (similar to what EVALUATION_DATASET_3_PROMPT generates)
format_aware_dataset = [
    {
        "prompt": "Write a Python function that retrieves the list of EC2 instances in a specific AWS region",
        "format": "python",
        "expected_response": "A Python function using boto3 to list EC2 instances",
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
        "expected_response": "A valid JSON object with Lambda configuration properties",
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
        "expected_response": "A regex pattern that validates S3 bucket naming rules",
        "grading_config": {
            "code": {
                "min_length": 20,
                "syntax_check": True
            }
        }
    }
]

def main():
    """Run the format-aware evaluation example."""
    
    # Initialize the chat client (you'll need to set your API key)
    # chat_client = AnthropicClient(api_key="your-api-key-here")
    
    # For demonstration purposes, we'll create a mock client
    # In real usage, you would use: FormatAwareEvaluator(chat_client)
    print("🚀 Format-Aware Evaluation Example")
    print("="*50)
    print("This example demonstrates the new run_format_aware_eval method.")
    print("The method provides enhanced display with detailed grading breakdown.")
    print("\nKey features:")
    print("✅ Enhanced progress display with format type")
    print("✅ Detailed grading breakdown for failed tests")
    print("✅ Separate scores for code, format, and model graders")
    print("✅ Automatic grading configuration per test case")
    print("✅ Results saving with JSON serialization")
    
    print(f"\nExample dataset contains {len(format_aware_dataset)} test cases:")
    for i, test_case in enumerate(format_aware_dataset, 1):
        print(f"  {i}. {test_case['prompt'][:50]}... ({test_case['format']})")
    
    print("\nTo run the actual evaluation:")
    print("1. Set your Anthropic API key")
    print("2. Uncomment the chat_client initialization")
    print("3. Create FormatAwareEvaluator(chat_client)")
    print("4. Call evaluator.run_format_aware_eval(format_aware_dataset)")
    
    print("\nExample usage:")
    print("""
    # Initialize
    chat_client = AnthropicClient(api_key="your-api-key")
    evaluator = FormatAwareEvaluator(chat_client)
    
    # Run evaluation with enhanced display
    results = evaluator.run_format_aware_eval(
        test_dataset=format_aware_dataset,
        save_results=True,
        results_path="format_aware_results.json",
        verbose=True
    )
    """)

if __name__ == "__main__":
    main()
