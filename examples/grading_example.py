#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Grading System Example

This script demonstrates the implementation of a comprehensive grading system that combines:
1. Code-based Grading: Programmatic evaluation using custom logic
2. Model-based Grading: AI-powered assessment using Claude

The system is designed based on the Anthropic Academy course content for prompt evaluation workflows.
"""

import os
import json
from dotenv import load_dotenv
from utils.graders import Grader, CodeGrader, ModelGrader, FormatGrader, FormatGradingCriteria, GradingCriteria, GradingResult

def main():
    """Main function to demonstrate the grading system."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if api_key is None:
        print("❌ ANTHROPIC_API_KEY not found in environment variables")
        print("Please set your API key in a .env file")
        return
    
    print("✅ Setup complete!")
    
    # Initialize the grading system
    print("\n=== Initializing Grading System ===")
    grader = Grader(api_key=api_key, model="claude-3-haiku-20240307")
    code_grader = CodeGrader()
    model_grader = ModelGrader(api_key=api_key, model="claude-3-haiku-20240307")
    format_grader = FormatGrader()
    print("✅ Graders initialized!")
    
    # Example 1: Code-based grading
    print("\n=== Code-Based Grading Examples ===")
    
    # Python code validation
    python_code = """
def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 3)
print(f"The sum is: {result}")
"""
    
    print("1. Python Code Validation:")
    result = code_grader.grade(python_code, language="python")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # JSON validation
    json_data = """
{
    "name": "John Doe",
    "age": 30,
    "city": "New York"
}
"""
    
    print("\n2. JSON Validation:")
    result = code_grader.grade(json_data, language="json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Custom criteria evaluation
    custom_criteria = GradingCriteria(
        min_length=50,
        max_length=500,
        required_words=["python", "function"],
        forbidden_words=["error", "bug"],
        readability_threshold=6.0
    )
    
    custom_code_grader = CodeGrader(criteria=custom_criteria)
    
    text_with_criteria = """
This is a python function that demonstrates how to work with data.
It shows various programming concepts and best practices.
The function is well-structured and follows good coding standards.
"""
    
    print("\n3. Custom Criteria Evaluation:")
    result = custom_code_grader.grade(text_with_criteria, language="text")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 2: Model-based grading
    print("\n=== Model-Based Grading Examples ===")
    
    prompt = "Explain how to create a Python function that calculates the factorial of a number."
    response = """
To create a Python function that calculates the factorial of a number, you can use recursion or iteration.
Here's a simple recursive implementation:

def factorial(n):
    if n == 0 or n == 1:
        return 1
    else:
        return n * factorial(n-1)

This function works by:
1. Checking if n is 0 or 1 (base cases)
2. If so, returning 1
3. Otherwise, multiplying n by the factorial of n-1

You can call it like: factorial(5) which returns 120.
"""
    
    print("1. Response Quality Assessment:")
    result = model_grader.grade(prompt, response)
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 3: Comprehensive grading
    print("\n=== Comprehensive Grading Example ===")
    
    comprehensive_prompt = "Write a Python function to sort a list of numbers in ascending order."
    comprehensive_response = '''
def sort_numbers(numbers):
    """Sort a list of numbers in ascending order."""
    return sorted(numbers)

# Example usage
my_list = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_list = sort_numbers(my_list)
print(f"Original: {my_list}")
print(f"Sorted: {sorted_list}")
'''
    
    comprehensive_result = grader.grade_comprehensive(
        comprehensive_prompt, 
        comprehensive_response, 
        language="python"
    )
    
    print("Code Grader Results:")
    code_result = comprehensive_result["code_grader"]
    print(f"   Score: {code_result.score}/10")
    print(f"   Passed: {code_result.passed}")
    print(f"   Feedback: {code_result.feedback}")
    
    print("\nModel Grader Results:")
    model_result = comprehensive_result["model_grader"]
    print(f"   Score: {model_result.score}/10")
    print(f"   Passed: {model_result.passed}")
    print(f"   Feedback: {model_result.feedback}")
    
    # Example 4: Batch grading
    print("\n=== Batch Grading Example ===")
    
    batch_evaluations = [
        {
            "prompt": "Write a function to add two numbers",
            "response": "def add(a, b): return a + b"
        },
        {
            "prompt": "Explain what is machine learning",
            "response": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed."
        },
        {
            "prompt": "Create a JSON object for a user profile",
            "response": "{\"name\": \"John\", \"age\": 25, \"email\": \"john@example.com\"}"
        }
    ]
    
    batch_results = grader.grade_batch(batch_evaluations, language="text")
    
    for i, result in enumerate(batch_results):
        print(f"\nEvaluation {i+1}:")
        print(f"   Success: {result['success']}")
        if result['success']:
            code_score = result['results']['code_grader'].score
            model_score = result['results']['model_grader'].score
            print(f"   Code Score: {code_score}/10")
            print(f"   Model Score: {model_score}/10")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Generate comprehensive report
    print("\n=== Grading Report ===")
    report = grader.generate_grading_report(batch_results)
    print(json.dumps(report, indent=2))
    
    # Example 5: Advanced usage
    print("\n=== Advanced Usage Examples ===")
    
    # Custom grading prompt for specific domain
    custom_grading_prompt = """
You are an expert Python code reviewer. Evaluate the following code response based on these criteria:

1. Code Quality (1-10): Is the code well-written, efficient, and follows best practices?
2. Correctness (1-10): Does the code correctly solve the problem?
3. Readability (1-10): Is the code easy to understand and well-documented?
4. Efficiency (1-10): Is the code optimized and performant?

Provide evaluation in JSON format:
{{
    "code_quality": {{"score": X, "reasoning": "explanation"}},
    "correctness": {{"score": X, "reasoning": "explanation"}},
    "readability": {{"score": X, "reasoning": "explanation"}},
    "efficiency": {{"score": X, "reasoning": "explanation"}},
    "overall_score": X,
    "overall_feedback": "summary"
}}

PROMPT: {prompt}
CODE: {response}

EVALUATION:
"""
    
    # Set custom prompt
    grader.set_model_grading_prompt(custom_grading_prompt)
    
    # Test with Python code
    python_prompt = "Write a function to find the maximum value in a list"
    python_response = """
def find_max(numbers):
    if not numbers:
        return None
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val
"""
    
    print("1. Custom Domain-Specific Grading:")
    custom_result = grader.grade_model(python_prompt, python_response)
    print(f"   Score: {custom_result.score}/10")
    print(f"   Passed: {custom_result.passed}")
    print(f"   Feedback: {custom_result.feedback}")
    
    # Custom code grading criteria
    advanced_criteria = GradingCriteria(
        min_length=20,
        max_length=1000,
        required_words=["def", "return"],
        forbidden_words=["print", "input"],
        syntax_check=True,
        readability_threshold=5.0
    )
    
    grader.set_code_criteria(advanced_criteria)
    
    test_code = '''
def multiply_numbers(a, b):
    """Multiply two numbers and return the result."""
    result = a * b
    return result
'''
    
    print("\n2. Advanced Code Criteria:")
    advanced_result = grader.grade_code(test_code, language="python")
    print(f"   Score: {advanced_result.score}/10")
    print(f"   Passed: {advanced_result.passed}")
    print(f"   Feedback: {advanced_result.feedback}")
    
    # Example 6: Format-based grading
    print("\n=== Format-Based Grading Examples ===")
    
    # JSON format validation
    json_criteria = FormatGradingCriteria(
        required_format="json",
        required_fields=["name", "age", "email"],
        forbidden_fields=["password"]
    )
    
    format_grader.criteria = json_criteria
    
    valid_json = '{"name": "John Doe", "age": 30, "email": "john@example.com"}'
    invalid_json = '{"name": "Jane Doe", "age": 25, "password": "secret123"}'
    
    print("1. Valid JSON Format:")
    result = format_grader.grade(valid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    print("\n2. Invalid JSON Format:")
    result = format_grader.grade(invalid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Markdown format validation
    markdown_criteria = FormatGradingCriteria(
        required_format="markdown",
        required_headers=["Title", "Introduction", "Conclusion"],
        require_code_blocks=True
    )
    
    format_grader.criteria = markdown_criteria
    
    valid_markdown = """# Title
## Introduction
This is the introduction.

## Conclusion
This concludes the document.

```python
print("Hello World")
```
"""
    
    print("\n3. Valid Markdown Format:")
    result = format_grader.grade(valid_markdown, "markdown")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 7: Comprehensive grading with format
    print("\n=== Comprehensive Grading with Format ===")
    
    # Set format criteria for the main grader
    grader.set_format_criteria(json_criteria)
    
    comprehensive_with_format = grader.grade_comprehensive(
        "Create a JSON user profile", 
        valid_json, 
        language="json", 
        include_format=True
    )
    
    print("Comprehensive Grading Results (with Format):")
    print(f"Code Grader: {comprehensive_with_format['code_grader'].score}/10")
    print(f"Model Grader: {comprehensive_with_format['model_grader'].score}/10")
    print(f"Format Grader: {comprehensive_with_format['format_grader'].score}/10")
    
    print("\n=== Summary ===")
    print("This comprehensive grading system provides:")
    print("\nCode-Based Grading Features:")
    print("- ✅ Output length checking (min/max)")
    print("- ✅ Word verification (required/forbidden)")
    print("- ✅ Syntax validation (Python, JSON, Regex)")
    print("- ✅ Readability scoring (1-10 scale)")
    print("- ✅ Customizable criteria")
    
    print("\nModel-Based Grading Features:")
    print("- ✅ Response quality assessment")
    print("- ✅ Instruction following evaluation")
    print("- ✅ Completeness checking")
    print("- ✅ Helpfulness scoring")
    print("- ✅ Safety assessment")
    print("- ✅ Custom grading prompts")
    
    print("\nFormat-Based Grading Features:")
    print("- ✅ JSON format and schema validation")
    print("- ✅ XML structure validation")
    print("- ✅ Markdown formatting validation")
    print("- ✅ CSV structure validation")
    print("- ✅ YAML format validation")
    print("- ✅ Required/forbidden field checking")
    
    print("\nMain Grader Features:")
    print("- ✅ Combined code, model, and format grading")
    print("- ✅ Batch processing capabilities")
    print("- ✅ Comprehensive reporting")
    print("- ✅ Error handling and recovery")
    print("- ✅ Automatic format detection")
    
    print("\nThe system is designed to be flexible, extensible, and follows the best practices")
    print("outlined in the Anthropic Academy course for prompt evaluation workflows.")
    print("It now includes format grading criteria as specified in the course curriculum.")

if __name__ == "__main__":
    main()
