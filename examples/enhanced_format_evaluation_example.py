#!/usr/bin/env python3
"""
Enhanced Format-Aware Evaluation Example

This example demonstrates the new enhanced format-aware evaluation capabilities
with detailed statistics and reporting.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.anthropic_client import ChatClient
from utils.evaluator import FormatAwareEvaluator
from utils.graders import FormatGradingCriteria, GradingCriteria

def main():
    """Run enhanced format-aware evaluation example."""
    
    # Initialize chat client and evaluator
    chat_client = ChatClient()
    evaluator = FormatAwareEvaluator(chat_client)
    
    # Sample format-aware test dataset
    format_aware_dataset = [
        {
            "prompt": "Create a JSON object with user information including name, email, and age",
            "format": "json",
            "grading_config": {
                "format": {
                    "required_fields": ["name", "email", "age"],
                    "validate_json_schema": True,
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string"},
                            "age": {"type": "number"}
                        },
                        "required": ["name", "email", "age"]
                    }
                }
            }
        },
        {
            "prompt": "Write a Python function that calculates the factorial of a number",
            "format": "python",
            "grading_config": {
                "code": {
                    "min_length": 50,
                    "syntax_check": True,
                    "required_words": ["def", "factorial", "return"]
                }
            }
        },
        {
            "prompt": "Create a markdown document with a title, introduction, and code example",
            "format": "markdown",
            "grading_config": {
                "format": {
                    "required_headers": ["Introduction"],
                    "require_code_blocks": True
                }
            }
        }
    ]
    
    print("🚀 Enhanced Format-Aware Evaluation Example")
    print("="*60)
    
    # Run evaluation with detailed display
    results = evaluator.run_format_aware_eval_with_detailed_display(
        test_dataset=format_aware_dataset,
        save_results=True,
        results_path="enhanced_eval_results.json",
        verbose=True,
        show_individual_tests=True,
        max_display=5
    )
    
    print("\n" + "="*60)
    print("✅ Enhanced evaluation completed!")
    print("Check 'enhanced_eval_results.json' for detailed results.")
    
    # Demonstrate statistics calculation separately
    print("\n📊 Additional Statistics Analysis:")
    stats = evaluator.calculate_format_statistics(results['results'])
    
    print(f"Total tests: {stats['overall']['total']}")
    print(f"Passed: {stats['overall']['passed']}")
    print(f"Failed: {stats['overall']['failed']}")
    
    print("\nFormat breakdown:")
    for format_type, format_stats in stats['by_format'].items():
        total = format_stats['passed'] + format_stats['failed']
        pass_rate = format_stats['passed'] / total * 100 if total > 0 else 0
        print(f"  {format_type}: {pass_rate:.1f}% pass rate")

if __name__ == "__main__":
    main()
