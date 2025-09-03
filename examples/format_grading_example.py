#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Format Grading System Example

This script demonstrates the implementation of format-specific grading criteria
as outlined in the Anthropic API course curriculum. The system evaluates outputs
based on format requirements including JSON, XML, Markdown, CSV, and YAML.

The format grading system provides:
1. Format validation (syntax, structure)
2. Content validation (required fields, forbidden fields)
3. Schema validation (JSON schema, XML schema)
4. Style validation (markdown formatting, table structures)
5. Integration with existing code and model grading
"""

import os
import json
from dotenv import load_dotenv
from utils.graders import (
    Grader, FormatGrader, FormatGradingCriteria, 
    GradingCriteria, GradingResult
)

def main():
    """Main function to demonstrate the format grading system."""
    
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
    print("\n=== Initializing Format Grading System ===")
    grader = Grader(api_key=api_key, model="claude-3-haiku-20240307")
    format_grader = FormatGrader()
    print("✅ Graders initialized!")
    
    # Example 1: JSON Format Grading
    print("\n=== JSON Format Grading Examples ===")
    
    # Basic JSON validation
    json_criteria = FormatGradingCriteria(
        required_format="json",
        required_fields=["name", "age", "email"],
        forbidden_fields=["password", "ssn"]
    )
    
    format_grader.criteria = json_criteria
    
    valid_json = '''
    {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com",
        "city": "New York"
    }
    '''
    
    print("1. Valid JSON with Required Fields:")
    result = format_grader.grade(valid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    invalid_json = '''
    {
        "name": "Jane Doe",
        "age": 25,
        "password": "secret123"
    }
    '''
    
    print("\n2. Invalid JSON (Missing Required Fields + Forbidden Field):")
    result = format_grader.grade(invalid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 2: JSON Schema Validation
    print("\n=== JSON Schema Validation ===")
    
    json_schema_criteria = FormatGradingCriteria(
        required_format="json",
        validate_json_schema=True,
        json_schema={
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "number"},
                        "name": {"type": "string"},
                        "active": {"type": "boolean"}
                    },
                    "required": ["id", "name", "active"]
                }
            },
            "required": ["user"]
        }
    )
    
    format_grader.criteria = json_schema_criteria
    
    schema_valid_json = '''
    {
        "user": {
            "id": 12345,
            "name": "Alice Smith",
            "active": true
        }
    }
    '''
    
    print("1. JSON Valid Against Schema:")
    result = format_grader.grade(schema_valid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    schema_invalid_json = '''
    {
        "user": {
            "id": "not_a_number",
            "name": "Bob Johnson",
            "active": "not_a_boolean"
        }
    }
    '''
    
    print("\n2. JSON Invalid Against Schema:")
    result = format_grader.grade(schema_invalid_json, "json")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 3: XML Format Grading
    print("\n=== XML Format Grading Examples ===")
    
    xml_criteria = FormatGradingCriteria(
        required_format="xml",
        required_sections=["header", "body", "footer"]
    )
    
    format_grader.criteria = xml_criteria
    
    valid_xml = '''
    <document>
        <header>
            <title>Sample Document</title>
            <author>John Doe</author>
        </header>
        <body>
            <section>This is the main content.</section>
        </body>
        <footer>
            <copyright>2024</copyright>
        </footer>
    </document>
    '''
    
    print("1. Valid XML with Required Sections:")
    result = format_grader.grade(valid_xml, "xml")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    invalid_xml = '''
    <document>
        <header>
            <title>Sample Document</title>
        </header>
        <body>
            <section>This is the main content.</section>
        </body>
    </document>
    '''
    
    print("\n2. Invalid XML (Missing Footer Section):")
    result = format_grader.grade(invalid_xml, "xml")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 4: Markdown Format Grading
    print("\n=== Markdown Format Grading Examples ===")
    
    markdown_criteria = FormatGradingCriteria(
        required_format="markdown",
        required_headers=["Introduction", "Methods", "Results", "Conclusion"],
        require_code_blocks=True,
        require_bullet_points=True
    )
    
    format_grader.criteria = markdown_criteria
    
    valid_markdown = '''
    # Research Paper
    
    ## Introduction
    This is the introduction section.
    
    ## Methods
    The methods used include:
    - Data collection
    - Analysis
    - Validation
    
    ## Results
    Here are the results:
    
    ```python
    def analyze_data():
        return "Analysis complete"
    ```
    
    ## Conclusion
    This concludes the research.
    '''
    
    print("1. Valid Markdown with Required Elements:")
    result = format_grader.grade(valid_markdown, "markdown")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    invalid_markdown = '''
    # Research Paper
    
    ## Introduction
    This is the introduction section.
    
    ## Methods
    The methods used include data collection and analysis.
    
    ## Results
    Here are the results.
    
    ## Conclusion
    This concludes the research.
    '''
    
    print("\n2. Invalid Markdown (Missing Code Blocks and Bullet Points):")
    result = format_grader.grade(invalid_markdown, "markdown")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 5: CSV Format Grading
    print("\n=== CSV Format Grading Examples ===")
    
    csv_criteria = FormatGradingCriteria(
        required_format="csv",
        required_fields=["Name", "Age", "City"]
    )
    
    format_grader.criteria = csv_criteria
    
    valid_csv = '''
    Name,Age,City
    John,30,New York
    Jane,25,Los Angeles
    Bob,35,Chicago
    '''
    
    print("1. Valid CSV with Required Columns:")
    result = format_grader.grade(valid_csv, "csv")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    invalid_csv = '''
    Name,Age
    John,30
    Jane,25,Los Angeles
    Bob,35
    '''
    
    print("\n2. Invalid CSV (Missing Required Column + Inconsistent Rows):")
    result = format_grader.grade(invalid_csv, "csv")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 6: YAML Format Grading
    print("\n=== YAML Format Grading Examples ===")
    
    yaml_criteria = FormatGradingCriteria(
        required_format="yaml",
        required_fields=["database", "server", "port"],
        forbidden_fields=["password", "secret_key"]
    )
    
    format_grader.criteria = yaml_criteria
    
    valid_yaml = '''
    database:
      host: localhost
      name: myapp
      user: admin
    server:
      host: 0.0.0.0
      port: 8080
    environment: production
    '''
    
    print("1. Valid YAML with Required Fields:")
    result = format_grader.grade(valid_yaml, "yaml")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    invalid_yaml = '''
    database:
      host: localhost
      name: myapp
      password: secret123
    server:
      host: 0.0.0.0
    '''
    
    print("\n2. Invalid YAML (Missing Required Field + Forbidden Field):")
    result = format_grader.grade(invalid_yaml, "yaml")
    print(f"   Score: {result.score}/10")
    print(f"   Passed: {result.passed}")
    print(f"   Feedback: {result.feedback}")
    
    # Example 7: Comprehensive Grading with Format
    print("\n=== Comprehensive Grading with Format ===")
    
    # Set format criteria for the main grader
    format_criteria = FormatGradingCriteria(
        required_format="json",
        required_fields=["title", "content", "tags"],
        validate_json_schema=True,
        json_schema={
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "content": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["title", "content", "tags"]
        }
    )
    
    grader.set_format_criteria(format_criteria)
    
    prompt = "Create a JSON response with a blog post structure including title, content, and tags."
    response = '''
    {
        "title": "Getting Started with AI",
        "content": "This is a comprehensive guide to artificial intelligence.",
        "tags": ["AI", "Machine Learning", "Technology"]
    }
    '''
    
    comprehensive_result = grader.grade_comprehensive(
        prompt, response, language="json", include_format=True
    )
    
    print("Comprehensive Grading Results:")
    print(f"Code Grader: {comprehensive_result['code_grader'].score}/10 - {comprehensive_result['code_grader'].passed}")
    print(f"Model Grader: {comprehensive_result['model_grader'].score}/10 - {comprehensive_result['model_grader'].passed}")
    print(f"Format Grader: {comprehensive_result['format_grader'].score}/10 - {comprehensive_result['format_grader'].passed}")
    
    # Example 8: Batch Format Grading
    print("\n=== Batch Format Grading Example ===")
    
    batch_evaluations = [
        {
            "prompt": "Create a JSON user profile",
            "response": '{"name": "Alice", "age": 30, "email": "alice@example.com"}'
        },
        {
            "prompt": "Write a markdown document with headers",
            "response": "# Title\n## Section\nContent here"
        },
        {
            "prompt": "Generate CSV data for sales",
            "response": "Product,Price,Quantity\nWidget,10.99,100\nGadget,25.50,50"
        }
    ]
    
    # Set different format criteria for each evaluation
    json_batch_criteria = FormatGradingCriteria(
        required_format="json",
        required_fields=["name", "age", "email"]
    )
    
    markdown_batch_criteria = FormatGradingCriteria(
        required_format="markdown",
        required_headers=["Title", "Section"]
    )
    
    csv_batch_criteria = FormatGradingCriteria(
        required_format="csv",
        required_fields=["Product", "Price", "Quantity"]
    )
    
    batch_results = []
    
    for i, eval_item in enumerate(batch_evaluations):
        prompt = eval_item["prompt"]
        response = eval_item["response"]
        
        # Set appropriate criteria based on prompt
        if "json" in prompt.lower():
            grader.set_format_criteria(json_batch_criteria)
        elif "markdown" in prompt.lower():
            grader.set_format_criteria(markdown_batch_criteria)
        elif "csv" in prompt.lower():
            grader.set_format_criteria(csv_batch_criteria)
        
        try:
            result = grader.grade_comprehensive(prompt, response, include_format=True)
            batch_results.append({
                "index": i,
                "prompt": prompt,
                "response": response,
                "results": result,
                "success": True
            })
        except Exception as e:
            batch_results.append({
                "index": i,
                "prompt": prompt,
                "response": response,
                "error": str(e),
                "success": False
            })
    
    print("Batch Format Grading Results:")
    for result in batch_results:
        if result["success"]:
            format_score = result["results"]["format_grader"].score
            format_passed = result["results"]["format_grader"].passed
            print(f"  Evaluation {result['index']+1}: {format_score}/10 - {'✓' if format_passed else '✗'}")
        else:
            print(f"  Evaluation {result['index']+1}: Error - {result.get('error', 'Unknown error')}")
    
    # Generate comprehensive report
    print("\n=== Format Grading Report ===")
    report = grader.generate_grading_report(batch_results)
    
    if report.get("format_grader_stats"):
        format_stats = report["format_grader_stats"]
        print(f"Format Grader Statistics:")
        print(f"  Average Score: {format_stats['average_score']:.2f}/10")
        print(f"  Passed: {format_stats['passed_count']}/{report['successful_evaluations']}")
        print(f"  Pass Rate: {format_stats['pass_rate']:.2%}")
        print(f"  Score Range: {format_stats['min_score']:.1f} - {format_stats['max_score']:.1f}")
    
    print("\n=== Summary ===")
    print("The Format Grading System provides:")
    print("\nFormat Validation Features:")
    print("- ✅ JSON format and schema validation")
    print("- ✅ XML structure and section validation")
    print("- ✅ Markdown formatting and content validation")
    print("- ✅ CSV structure and column validation")
    print("- ✅ YAML format and field validation")
    
    print("\nAdvanced Features:")
    print("- ✅ Required/forbidden field checking")
    print("- ✅ Schema-based validation")
    print("- ✅ Content structure validation")
    print("- ✅ Style and presentation checking")
    print("- ✅ Automatic format detection")
    
    print("\nIntegration Features:")
    print("- ✅ Seamless integration with existing graders")
    print("- ✅ Comprehensive grading workflows")
    print("- ✅ Batch processing capabilities")
    print("- ✅ Detailed failure analysis")
    print("- ✅ Comprehensive reporting")
    
    print("\nThis system implements the format grading criteria outlined in the")
    print("Anthropic API course curriculum, providing robust evaluation of")
    print("output format compliance across multiple data formats.")

if __name__ == "__main__":
    main()
