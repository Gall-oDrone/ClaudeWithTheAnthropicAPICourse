#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the Format Grading System

This module tests the format grading capabilities including:
- JSON format validation
- XML format validation  
- Markdown format validation
- CSV format validation
- YAML format validation
"""

import unittest
from utils.graders import FormatGrader, FormatGradingCriteria, GradingResult


class TestFormatGrading(unittest.TestCase):
    """Test cases for the FormatGrading system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.format_grader = FormatGrader()
    
    def test_json_format_validation_valid(self):
        """Test valid JSON format validation."""
        criteria = FormatGradingCriteria(
            required_format="json",
            required_fields=["name", "age"],
            forbidden_fields=["password"]
        )
        self.format_grader.criteria = criteria
        
        valid_json = '{"name": "John", "age": 30}'
        result = self.format_grader.grade(valid_json, "json")
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
        self.assertIn("JSON format validation passed", result.feedback)
    
    def test_json_format_validation_invalid(self):
        """Test invalid JSON format validation."""
        criteria = FormatGradingCriteria(
            required_format="json",
            required_fields=["name", "age"],
            forbidden_fields=["password"]
        )
        self.format_grader.criteria = criteria
        
        invalid_json = '{"name": "John"}'  # Missing required field 'age'
        result = self.format_grader.grade(invalid_json, "json")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertLess(result.score, 10.0)
        self.assertIn("Missing required fields", result.feedback)
    
    def test_json_format_validation_forbidden_field(self):
        """Test JSON validation with forbidden fields."""
        criteria = FormatGradingCriteria(
            required_format="json",
            required_fields=["name"],
            forbidden_fields=["password", "ssn"]
        )
        self.format_grader.criteria = criteria
        
        json_with_forbidden = '{"name": "John", "password": "secret123"}'
        result = self.format_grader.grade(json_with_forbidden, "json")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Contains forbidden fields", result.feedback)
    
    def test_xml_format_validation_valid(self):
        """Test valid XML format validation."""
        criteria = FormatGradingCriteria(
            required_format="xml",
            required_sections=["header", "body"]
        )
        self.format_grader.criteria = criteria
        
        valid_xml = '''
        <document>
            <header>Title</header>
            <body>Content</body>
        </document>
        '''
        result = self.format_grader.grade(valid_xml, "xml")
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
    
    def test_xml_format_validation_missing_section(self):
        """Test XML validation with missing required sections."""
        criteria = FormatGradingCriteria(
            required_format="xml",
            required_sections=["header", "body", "footer"]
        )
        self.format_grader.criteria = criteria
        
        xml_missing_section = '''
        <document>
            <header>Title</header>
            <body>Content</body>
        </document>
        '''
        result = self.format_grader.grade(xml_missing_section, "xml")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Missing required sections", result.feedback)
    
    def test_markdown_format_validation_valid(self):
        """Test valid Markdown format validation."""
        criteria = FormatGradingCriteria(
            required_format="markdown",
            required_headers=["Title", "Introduction"],
            require_code_blocks=True
        )
        self.format_grader.criteria = criteria
        
        valid_markdown = '''# Title
## Introduction
Content here.

```python
print("Hello")
```
'''
        result = self.format_grader.grade(valid_markdown, "markdown")
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
    
    def test_markdown_format_validation_missing_elements(self):
        """Test Markdown validation with missing required elements."""
        criteria = FormatGradingCriteria(
            required_format="markdown",
            required_headers=["Title", "Introduction"],
            require_code_blocks=True
        )
        self.format_grader.criteria = criteria
        
        invalid_markdown = '''# Title
Content here.
'''
        result = self.format_grader.grade(invalid_markdown, "markdown")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Missing required headers", result.feedback)
    
    def test_csv_format_validation_valid(self):
        """Test valid CSV format validation."""
        criteria = FormatGradingCriteria(
            required_format="csv",
            required_fields=["Name", "Age"]
        )
        self.format_grader.criteria = criteria
        
        valid_csv = '''Name,Age
John,30
Jane,25
'''
        result = self.format_grader.grade(valid_csv, "csv")
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
    
    def test_csv_format_validation_missing_column(self):
        """Test CSV validation with missing required columns."""
        criteria = FormatGradingCriteria(
            required_format="csv",
            required_fields=["Name", "Age", "City"]
        )
        self.format_grader.criteria = criteria
        
        invalid_csv = '''Name,Age
John,30
Jane,25
'''
        result = self.format_grader.grade(invalid_csv, "csv")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Missing required columns", result.feedback)
    
    def test_yaml_format_validation_valid(self):
        """Test valid YAML format validation."""
        criteria = FormatGradingCriteria(
            required_format="yaml",
            required_fields=["database", "server"]
        )
        self.format_grader.criteria = criteria
        
        valid_yaml = '''database:
  host: localhost
server:
  port: 8080
'''
        result = self.format_grader.grade(valid_yaml, "yaml")
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
    
    def test_yaml_format_validation_missing_field(self):
        """Test YAML validation with missing required fields."""
        criteria = FormatGradingCriteria(
            required_format="yaml",
            required_fields=["database", "server", "port"]
        )
        self.format_grader.criteria = criteria
        
        invalid_yaml = '''database:
  host: localhost
server:
  host: 0.0.0.0
'''
        result = self.format_grader.grade(invalid_yaml, "yaml")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Missing required fields", result.feedback)
    
    def test_automatic_format_detection(self):
        """Test automatic format detection from content."""
        # Test JSON detection
        json_content = '{"name": "John", "age": 30}'
        result = self.format_grader.grade(json_content)
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
        self.assertEqual(result.score, 10.0)
        
        # Test XML detection
        xml_content = '<root><item>test</item></root>'
        result = self.format_grader.grade(xml_content)
        
        self.assertIsInstance(result, GradingResult)
        self.assertTrue(result.passed)
    
    def test_invalid_format_type(self):
        """Test handling of invalid format types."""
        result = self.format_grader.grade("some content", "invalid_format")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("Unsupported format type", result.feedback)
    
    def test_no_format_type_specified(self):
        """Test handling when no format type is specified."""
        result = self.format_grader.grade("some content")
        
        self.assertIsInstance(result, GradingResult)
        self.assertFalse(result.passed)
        self.assertIn("No format type specified", result.feedback)


if __name__ == '__main__':
    unittest.main()
