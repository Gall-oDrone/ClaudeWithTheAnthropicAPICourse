"""
Test suite for shared utilities module.
Tests IncompletenessDetector, ResponseFormatter, FormatDetector, and ErrorHandler.
"""

import unittest
import json
import re
from unittest.mock import patch, MagicMock

from utils.shared_utils import (
    IncompletenessDetector,
    ResponseFormatter,
    FormatDetector,
    ErrorHandler,
    TemplateRenderer,
)
from utils.graders import GradingResult


class TestIncompletenessDetector(unittest.TestCase):
    """Test cases for IncompletenessDetector utility class."""
    
    def test_detect_incomplete_response_complete(self):
        """Test detection of complete responses."""
        complete_responses = [
            "def calculate_sum(a, b):\n    return a + b",
            '{"name": "John", "age": 30}',
            "This is a complete response with no issues.",
            "import os\nprint('Hello World')"
        ]
        
        for response in complete_responses:
            with self.subTest(response=response):
                is_incomplete, error_msg = IncompletenessDetector.detect_incomplete_response(response)
                self.assertFalse(is_incomplete)
                self.assertEqual(error_msg, "Complete")
    
    def test_detect_incomplete_response_incomplete(self):
        """Test detection of incomplete responses."""
        incomplete_cases = [
            ("def calculate_sum(a, b):\n    # TODO: implement", "TODO"),
            ("This is incomplete...", "..."),
            ("# Add your code here", "# Add your"),
            ("pass  # Implement this", "# Implement"),
            ("raise NotImplementedError", "raise NotImplementedError"),
            ("# Your code here", "# Your code here"),
            ("Coming soon", "Coming soon"),
            ("To be implemented", "To be implemented")
        ]
        
        for response, expected_indicator in incomplete_cases:
            with self.subTest(response=response):
                is_incomplete, error_msg = IncompletenessDetector.detect_incomplete_response(response)
                self.assertTrue(is_incomplete)
                self.assertIn(expected_indicator, error_msg)
    
    def test_validate_response_completeness_python_complete(self):
        """Test Python response completeness validation for complete responses."""
        complete_python_cases = [
            ("def add(a, b):\n    return a + b", "python", "Write a function to add two numbers"),
            ("class Calculator:\n    def __init__(self):\n        pass", "python", "Create a calculator class"),
            ("import os\nprint('Hello')\nprint('World')", "python", "Write a script")
        ]
        
        for response, format_type, prompt in complete_python_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertTrue(is_complete)
                self.assertEqual(error_msg, "Complete")
    
    def test_validate_response_completeness_python_incomplete(self):
        """Test Python response completeness validation for incomplete responses."""
        incomplete_python_cases = [
            ("def add(a, b):\n    pass", "python", "Write a function to add two numbers"),
            ("def calculate():\n    # TODO", "python", "Write a function"),
            ("def incomplete():\n    return", "python", "Write a function"),
            ("short", "python", "Write a function")
        ]
        
        for response, format_type, prompt in incomplete_python_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertFalse(is_complete)
                self.assertNotEqual(error_msg, "Complete")
    
    def test_validate_response_completeness_json_complete(self):
        """Test JSON response completeness validation for complete responses."""
        complete_json_cases = [
            ('{"name": "John", "age": 30}', "json", "Create a JSON object"),
            ('{"users": [{"id": 1, "name": "Alice"}]}', "json", "Create user data")
        ]
        
        for response, format_type, prompt in complete_json_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertTrue(is_complete)
                self.assertEqual(error_msg, "Complete")
    
    def test_validate_response_completeness_json_incomplete(self):
        """Test JSON response completeness validation for incomplete responses."""
        incomplete_json_cases = [
            ('{"name": "", "age": null}', "json", "Create a JSON object"),
            ('{"name": "John", "age": "..."}', "json", "Create a JSON object"),
            ('invalid json', "json", "Create a JSON object")
        ]
        
        for response, format_type, prompt in incomplete_json_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertFalse(is_complete)
                self.assertNotEqual(error_msg, "Complete")
    
    def test_validate_response_completeness_regex_complete(self):
        """Test regex response completeness validation for complete responses."""
        complete_regex_cases = [
            (r"\d{3}-\d{3}-\d{4}", "regex", "Create a phone number regex"),
            (r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "regex", "Create email regex")
        ]
        
        for response, format_type, prompt in complete_regex_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertTrue(is_complete)
                self.assertEqual(error_msg, "Complete")
    
    def test_validate_response_completeness_regex_incomplete(self):
        """Test regex response completeness validation for incomplete responses."""
        incomplete_regex_cases = [
            ("abc", "regex", "Create a phone number regex"),  # Too short
            ("[invalid", "regex", "Create a regex"),  # Invalid regex
        ]
        
        for response, format_type, prompt in incomplete_regex_cases:
            with self.subTest(response=response):
                is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
                    response, format_type, prompt
                )
                self.assertFalse(is_complete)
                self.assertNotEqual(error_msg, "Complete")


class TestResponseFormatter(unittest.TestCase):
    """Test cases for ResponseFormatter utility class."""
    
    def test_clean_response_format_python(self):
        """Test cleaning Python responses."""
        test_cases = [
            ("```python\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
            ("```\ndef add(a, b):\n    return a + b\n```", "def add(a, b):\n    return a + b"),
            ("def add(a, b):\n    return a + b", "def add(a, b):\n    return a + b"),  # No change needed
        ]
        
        for input_response, expected in test_cases:
            with self.subTest(input=input_response):
                result = ResponseFormatter.clean_response_format(input_response, "python")
                self.assertEqual(result, expected)
    
    def test_clean_response_format_json(self):
        """Test cleaning JSON responses."""
        test_cases = [
            ("```json\n{\"name\": \"John\"}\n```", '{"name": "John"}'),
            ("```\n{\"name\": \"John\"}\n```", '{"name": "John"}'),
            ('{"name": "John"}', '{"name": "John"}'),  # No change needed
            ("Some text {\"name\": \"John\"} more text", 'Some text {"name": "John"} more text'),  # No extraction for mixed text
        ]
        
        for input_response, expected in test_cases:
            with self.subTest(input=input_response):
                result = ResponseFormatter.clean_response_format(input_response, "json")
                self.assertEqual(result, expected)
    
    def test_clean_response_format_regex(self):
        """Test cleaning regex responses."""
        test_cases = [
            ("```\n\\d{3}-\\d{3}-\\d{4}\n```", r"\d{3}-\d{3}-\d{4}"),
            ("/\\d{3}-\\d{3}-\\d{4}/", r"\d{3}-\d{3}-\d{4}"),
            ("`\\d{3}-\\d{3}-\\d{4}`", r"\d{3}-\d{3}-\d{4}"),
            (r"\d{3}-\d{3}-\d{4}", r"\d{3}-\d{3}-\d{4}"),  # No change needed
        ]
        
        for input_response, expected in test_cases:
            with self.subTest(input=input_response):
                result = ResponseFormatter.clean_response_format(input_response, "regex")
                self.assertEqual(result, expected)
    
    def test_clean_response_format_other_formats(self):
        """Test cleaning other format responses."""
        test_cases = [
            ("Some text", "text", "Some text"),
            ("<xml>content</xml>", "xml", "<xml>content</xml>"),
            ("# Header\nContent", "markdown", "# Header\nContent"),
        ]
        
        for input_response, format_type, expected in test_cases:
            with self.subTest(input=input_response, format=format_type):
                result = ResponseFormatter.clean_response_format(input_response, format_type)
                self.assertEqual(result, expected)
    
    def test_get_format_instructions(self):
        """Test getting format-specific instructions."""
        test_cases = [
            ("python", "IMPORTANT: Provide COMPLETE, WORKING Python code only"),
            ("json", "IMPORTANT: Provide ONLY valid JSON"),
            ("regex", "IMPORTANT: Provide ONLY the regular expression pattern"),
            ("xml", "IMPORTANT: Provide ONLY valid XML"),
            ("yaml", "IMPORTANT: Provide ONLY valid YAML"),
            ("csv", "IMPORTANT: Provide ONLY CSV data"),
            ("markdown", "Provide properly formatted Markdown"),
            ("unknown", ""),  # Unknown format should return empty string
        ]
        
        for format_type, expected_contains in test_cases:
            with self.subTest(format=format_type):
                result = ResponseFormatter.get_format_instructions(format_type)
                if expected_contains:
                    self.assertIn(expected_contains, result)
                else:
                    self.assertEqual(result, "")


class TestFormatDetector(unittest.TestCase):
    """Test cases for FormatDetector utility class."""
    
    def test_detect_format_type_from_prompt(self):
        """Test format detection from prompt content."""
        test_cases = [
            ("Create a JSON object with user data", "json"),
            ("Generate XML for the configuration", "xml"),
            ("Write markdown documentation", "markdown"),
            ("Create a CSV file with data", "csv"),
            ("Generate YAML configuration", "yaml"),
            ("Write a Python function", "text"),  # Should default to text
        ]
        
        for prompt, expected in test_cases:
            with self.subTest(prompt=prompt):
                result = FormatDetector.detect_format_type(prompt, "")
                self.assertEqual(result, expected)
    
    def test_detect_format_type_from_response(self):
        """Test format detection from response content."""
        test_cases = [
            ('{"name": "John"}', "json"),
            ("<root><item>value</item></root>", "xml"),
            ("# Header\n**Bold text**", "markdown"),
            ("name,age\nJohn,30", "csv"),
            ("name: John\nage: 30", "yaml"),
            ("def function(): pass", "text"),  # Should default to text
        ]
        
        for response, expected in test_cases:
            with self.subTest(response=response):
                result = FormatDetector.detect_format_type("", response)
                self.assertEqual(result, expected)
    
    def test_detect_format_type_combined(self):
        """Test format detection with both prompt and response."""
        test_cases = [
            ("Create a JSON object", '{"name": "John"}', "json"),
            ("Write some code", "def add(a, b): return a + b", "text"),
            ("Generate XML", "<root></root>", "xml"),
        ]
        
        for prompt, response, expected in test_cases:
            with self.subTest(prompt=prompt, response=response):
                result = FormatDetector.detect_format_type(prompt, response)
                self.assertEqual(result, expected)
    
    def test_is_code_prompt(self):
        """Test code prompt detection."""
        code_prompts = [
            "Write a function to calculate the sum",
            "Create a Python class for a calculator",
            "Implement an algorithm to sort data",
            "Write a script to process files",
            "Create a method to handle user input",
            "Write a program to solve this problem"
        ]
        
        non_code_prompts = [
            "Explain the concept of machine learning",
            "What is the capital of France?",
            "Describe the benefits of exercise",
            "Tell me a story about a cat"
        ]
        
        for prompt in code_prompts:
            with self.subTest(prompt=prompt):
                self.assertTrue(FormatDetector.is_code_prompt(prompt))
        
        for prompt in non_code_prompts:
            with self.subTest(prompt=prompt):
                self.assertFalse(FormatDetector.is_code_prompt(prompt))
    
    def test_is_format_prompt(self):
        """Test format prompt detection."""
        format_prompts = [
            "Create a JSON object with user data",
            "Generate XML configuration",
            "Write markdown documentation",
            "Create a CSV file",
            "Generate YAML config",
            "Format the data as a table"
        ]
        
        non_format_prompts = [
            "Write a function to calculate",
            "Explain the concept",
            "What is the answer",
            "Tell me about"
        ]
        
        for prompt in format_prompts:
            with self.subTest(prompt=prompt):
                self.assertTrue(FormatDetector.is_format_prompt(prompt))
        
        for prompt in non_format_prompts:
            with self.subTest(prompt=prompt):
                self.assertFalse(FormatDetector.is_format_prompt(prompt))


class TestErrorHandler(unittest.TestCase):
    """Test cases for ErrorHandler utility class."""
    
    def test_create_grading_result(self):
        """Test creating a GradingResult object."""
        score = 7.5
        feedback = "Good response with minor issues"
        details = {"issue": "minor formatting"}
        passed = True
        
        result = ErrorHandler.create_grading_result(score, feedback, details, passed)
        
        self.assertIsInstance(result, GradingResult)
        self.assertEqual(result.score, score)
        self.assertEqual(result.feedback, feedback)
        self.assertEqual(result.details, details)
        self.assertEqual(result.passed, passed)
    
    def test_handle_evaluation_error(self):
        """Test handling evaluation errors."""
        test_case = {
            "prompt": "Test prompt",
            "format": "python",
            "solution_criteria": "Should work"
        }
        error = ValueError("Test error message")
        
        result = ErrorHandler.handle_evaluation_error(test_case, error)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["test_case"], test_case)
        self.assertEqual(result["error"], "Test error message")
        self.assertFalse(result["passed"])
        self.assertEqual(result["grading_results"], {})
        self.assertEqual(result["actual_response"], "")
    
    def test_handle_evaluation_error_with_complex_error(self):
        """Test handling complex evaluation errors."""
        test_case = {"prompt": "Complex test"}
        error = RuntimeError("Complex error with details")
        
        result = ErrorHandler.handle_evaluation_error(test_case, error)
        
        self.assertEqual(result["error"], "Complex error with details")
        self.assertFalse(result["passed"])


class TestTemplateRenderer(unittest.TestCase):
    """Test cases for TemplateRenderer utility class."""

    def test_render_simple_placeholders(self):
        """Test simple {key} substitution."""
        template = "Hello {name}, you have {count} items."
        result = TemplateRenderer.render(template, {"name": "Alice", "count": 3})
        self.assertEqual(result, "Hello Alice, you have 3 items.")

    def test_render_literal_braces(self):
        """Test {{ and }} emit literal { and }."""
        template = "JSON looks like {{ \"key\": \"value\" }}."
        result = TemplateRenderer.render(template, {})
        self.assertEqual(result, "JSON looks like { \"key\": \"value\" }.")

    def test_render_missing_placeholder_left_unchanged(self):
        """Test that missing keys leave placeholder in place."""
        template = "Hello {name}, {missing}."
        result = TemplateRenderer.render(template, {"name": "Bob"})
        self.assertEqual(result, "Hello Bob, {missing}.")

    def test_render_empty_variables(self):
        """Test with empty variables dict."""
        template = "No placeholders here."
        result = TemplateRenderer.render(template, {})
        self.assertEqual(result, "No placeholders here.")

    def test_render_values_coerced_to_str(self):
        """Test that values are converted to string."""
        template = "Count: {n}"
        result = TemplateRenderer.render(template, {"n": 42})
        self.assertEqual(result, "Count: 42")


class TestIntegration(unittest.TestCase):
    """Integration tests for shared utilities working together."""
    
    def test_complete_evaluation_workflow(self):
        """Test a complete evaluation workflow using all utilities."""
        # Test case
        test_case = {
            "prompt": "Write a Python function to add two numbers",
            "format": "python"
        }
        
        # Simulate a complete response
        response = "def add(a, b):\n    return a + b"
        
        # Test format detection
        detected_format = FormatDetector.detect_format_type(test_case["prompt"], response)
        self.assertEqual(detected_format, "text")  # Should detect as text, not python format
        
        # Test if it's a code prompt
        is_code = FormatDetector.is_code_prompt(test_case["prompt"])
        self.assertTrue(is_code)
        
        # Test completeness validation
        is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
            response, "python", test_case["prompt"]
        )
        self.assertTrue(is_complete)
        self.assertEqual(error_msg, "Complete")
        
        # Test response cleaning (should not change)
        cleaned_response = ResponseFormatter.clean_response_format(response, "python")
        self.assertEqual(cleaned_response, response)
        
        # Test format instructions
        instructions = ResponseFormatter.get_format_instructions("python")
        self.assertIn("IMPORTANT: Provide COMPLETE, WORKING Python code only", instructions)
    
    def test_incomplete_evaluation_workflow(self):
        """Test evaluation workflow with incomplete response."""
        test_case = {
            "prompt": "Write a Python function to add two numbers",
            "format": "python"
        }
        
        # Simulate an incomplete response
        response = "def add(a, b):\n    # TODO: implement"
        
        # Test completeness validation
        is_complete, error_msg = IncompletenessDetector.validate_response_completeness(
            response, "python", test_case["prompt"]
        )
        self.assertFalse(is_complete)
        self.assertIn("TODO", error_msg)
        
        # Test error handling
        error = ValueError("Incomplete response")
        error_result = ErrorHandler.handle_evaluation_error(test_case, error)
        self.assertFalse(error_result["passed"])
        self.assertEqual(error_result["error"], "Incomplete response")


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestIncompletenessDetector,
        TestResponseFormatter,
        TestFormatDetector,
        TestErrorHandler,
        TestTemplateRenderer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*50}")
