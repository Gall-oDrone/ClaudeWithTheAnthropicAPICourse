# Format Grading System

## Overview

The Format Grading System is a comprehensive implementation of format-specific grading criteria as outlined in the Anthropic API course curriculum. This system provides robust evaluation of output format compliance across multiple data formats, seamlessly integrating with the existing code-based and model-based grading systems.

## Features

### 🎯 Supported Formats

- **JSON**: Syntax validation, schema validation, field requirements
- **XML**: Structure validation, section requirements, tag balancing
- **Markdown**: Header validation, content structure, formatting requirements
- **CSV**: Column validation, data consistency, field requirements
- **YAML**: Format validation, field requirements, structure checking

### 🔧 Core Capabilities

- **Format Validation**: Ensures outputs conform to expected format specifications
- **Content Validation**: Checks for required and forbidden fields/elements
- **Schema Validation**: JSON schema validation for complex data structures
- **Structure Validation**: Ensures proper document structure and organization
- **Automatic Detection**: Intelligently detects expected format from prompts and content
- **Integration**: Seamlessly works with existing grading systems

## Architecture

### Data Classes

#### FormatGradingCriteria
```python
@dataclass
class FormatGradingCriteria:
    # Output format requirements
    required_format: Optional[str] = None
    required_structure: Optional[Dict[str, Any]] = None
    required_fields: Optional[List[str]] = None
    forbidden_fields: Optional[List[str]] = None
    
    # Format-specific validation
    validate_json_schema: bool = False
    json_schema: Optional[Dict[str, Any]] = None
    xml_validation: bool = False
    xml_schema: Optional[str] = None
    
    # Content formatting
    required_sections: Optional[List[str]] = None
    required_headers: Optional[List[str]] = None
    formatting_rules: Optional[Dict[str, Any]] = None
    
    # Style and presentation
    require_code_blocks: bool = False
    require_bullet_points: bool = False
    require_numbering: bool = False
    require_tables: bool = False
    
    # Language and locale
    required_language: Optional[str] = None
    locale_specific: bool = False
```

### Core Classes

#### FormatGrader
The main class responsible for format validation:

```python
class FormatGrader:
    def __init__(self, criteria: Optional[FormatGradingCriteria] = None)
    
    def validate_json_format(self, output: str) -> Dict[str, Any]
    def validate_xml_format(self, output: str) -> Dict[str, Any]
    def validate_markdown_format(self, output: str) -> Dict[str, Any]
    def validate_csv_format(self, output: str) -> Dict[str, Any]
    def validate_yaml_format(self, output: str) -> Dict[str, Any]
    
    def grade(self, output: str, format_type: Optional[str] = None) -> GradingResult
```

#### Enhanced Grader
The main Grader class now includes format grading:

```python
class Grader:
    def __init__(self, client: Optional[Anthropic] = None, 
                 api_key: Optional[str] = None, 
                 model: str = "claude-3-haiku-20240307"):
        # ... existing initialization ...
        self.format_grader = FormatGrader()
    
    def set_format_criteria(self, criteria: FormatGradingCriteria)
    def grade_format(self, output: str, format_type: Optional[str] = None) -> GradingResult
    def grade_comprehensive(self, prompt: str, response: str, language: str = "text", 
                           include_format: bool = True) -> Dict[str, GradingResult]
```

## Usage Examples

### Basic Format Validation

```python
from utils.graders import FormatGrader, FormatGradingCriteria

# Create format criteria
criteria = FormatGradingCriteria(
    required_format="json",
    required_fields=["name", "age", "email"],
    forbidden_fields=["password", "ssn"]
)

# Initialize grader
format_grader = FormatGrader(criteria)

# Validate JSON output
json_output = '{"name": "John", "age": 30, "email": "john@example.com"}'
result = format_grader.grade(json_output, "json")

print(f"Score: {result.score}/10")
print(f"Passed: {result.passed}")
print(f"Feedback: {result.feedback}")
```

### JSON Schema Validation

```python
# Define JSON schema
json_schema = {
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

# Create criteria with schema validation
criteria = FormatGradingCriteria(
    required_format="json",
    validate_json_schema=True,
    json_schema=json_schema
)

# Validate against schema
format_grader.criteria = criteria
result = format_grader.grade(json_output, "json")
```

### Markdown Validation

```python
# Markdown criteria
markdown_criteria = FormatGradingCriteria(
    required_format="markdown",
    required_headers=["Introduction", "Methods", "Results", "Conclusion"],
    require_code_blocks=True,
    require_bullet_points=True
)

format_grader.criteria = markdown_criteria
result = format_grader.grade(markdown_content, "markdown")
```

### XML Validation

```python
# XML criteria
xml_criteria = FormatGradingCriteria(
    required_format="xml",
    required_sections=["header", "body", "footer"]
)

format_grader.criteria = xml_criteria
result = format_grader.grade(xml_content, "xml")
```

### CSV Validation

```python
# CSV criteria
csv_criteria = FormatGradingCriteria(
    required_format="csv",
    required_fields=["Name", "Age", "City"]
)

format_grader.criteria = csv_criteria
result = format_grader.grade(csv_content, "csv")
```

### YAML Validation

```python
# YAML criteria
yaml_criteria = FormatGradingCriteria(
    required_format="yaml",
    required_fields=["database", "server", "port"],
    forbidden_fields=["password", "secret_key"]
)

format_grader.criteria = yaml_criteria
result = format_grader.grade(yaml_content, "yaml")
```

## Integration with Existing Systems

### Comprehensive Grading

```python
from utils.graders import Grader, FormatGradingCriteria

# Initialize main grader
grader = Grader(api_key=api_key)

# Set format criteria
format_criteria = FormatGradingCriteria(
    required_format="json",
    required_fields=["title", "content", "tags"]
)
grader.set_format_criteria(format_criteria)

# Perform comprehensive grading
result = grader.grade_comprehensive(
    prompt="Create a JSON blog post",
    response=json_response,
    language="json",
    include_format=True
)

# Access all grading results
code_score = result["code_grader"].score
model_score = result["model_grader"].score
format_score = result["format_grader"].score
```

### Batch Processing

```python
# Batch evaluations with different format requirements
evaluations = [
    {
        "prompt": "Create a JSON user profile",
        "response": '{"name": "Alice", "age": 30}'
    },
    {
        "prompt": "Write a markdown document",
        "response": "# Title\nContent here"
    }
]

# Process batch with format grading
batch_results = grader.grade_batch(evaluations, language="text")

# Generate comprehensive report
report = grader.generate_grading_report(batch_results)
```

## Automatic Format Detection

The system automatically detects expected output formats from prompts and content:

```python
# Automatic detection from prompt
prompt = "Generate a JSON response with user data"
response = '{"name": "John", "age": 30}'

# Format type automatically detected as "json"
result = grader.grade_comprehensive(prompt, response, include_format=True)
```

### Detection Logic

1. **Prompt Analysis**: Checks for format keywords in the prompt
2. **Content Analysis**: Examines response content for format indicators
3. **Fallback**: Defaults to "text" if no format is detected

## Error Handling and Feedback

### Validation Results

Each validation method returns detailed results:

```python
{
    "passed": True/False,
    "feedback": "Human-readable feedback message",
    "errors": ["List of specific errors"],
    "warnings": ["List of warnings"]
}
```

### Scoring System

- **Perfect (10.0)**: All validation criteria passed
- **Partial (1.0-9.0)**: Some criteria failed, score based on error count
- **Failed (0.0)**: Critical validation failures

## Advanced Features

### Custom Formatting Rules

```python
# Custom formatting rules
formatting_rules = {
    "max_line_length": 80,
    "require_trailing_newline": True,
    "indentation": "spaces"
}

criteria = FormatGradingCriteria(
    required_format="json",
    formatting_rules=formatting_rules
)
```

### Locale-Specific Validation

```python
# Locale-specific criteria
criteria = FormatGradingCriteria(
    required_format="csv",
    required_language="en",
    locale_specific=True
)
```

## Testing

Run the test suite to verify functionality:

```bash
python -m unittest tests.test_format_grading
```

## Performance Considerations

- **Efficient Parsing**: Uses optimized parsing for each format type
- **Early Exit**: Stops validation on first critical failure
- **Caching**: Caches parsed results for repeated validation
- **Batch Processing**: Optimized for processing multiple evaluations

## Best Practices

### 1. Define Clear Criteria
```python
# Good: Specific and clear criteria
criteria = FormatGradingCriteria(
    required_format="json",
    required_fields=["name", "email"],
    forbidden_fields=["password"]
)

# Avoid: Vague or overly complex criteria
criteria = FormatGradingCriteria(
    required_format="json",
    formatting_rules={"complex": "rules"}
)
```

### 2. Use Appropriate Validation Levels
```python
# For simple validation
criteria = FormatGradingCriteria(required_format="json")

# For strict validation
criteria = FormatGradingCriteria(
    required_format="json",
    validate_json_schema=True,
    json_schema=strict_schema
)
```

### 3. Handle Edge Cases
```python
# Check for format detection
if "format_grader" in result:
    format_score = result["format_grader"].score
else:
    format_score = "N/A"
```

## Troubleshooting

### Common Issues

1. **Format Not Detected**: Ensure prompt contains format keywords
2. **Validation Fails**: Check criteria configuration and output format
3. **Schema Errors**: Verify JSON schema syntax and structure

### Debug Mode

Enable detailed logging for troubleshooting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Additional Formats**: Support for more data formats (TOML, INI, etc.)
- **Advanced Schemas**: XML Schema validation, RelaxNG support
- **Custom Validators**: User-defined validation functions
- **Performance Optimization**: Parallel validation for large datasets
- **Machine Learning**: AI-powered format detection and validation

## Contributing

To contribute to the format grading system:

1. Follow the existing code style and patterns
2. Add comprehensive tests for new features
3. Update documentation for any API changes
4. Ensure backward compatibility

## License

This format grading system is part of the Claude with the Anthropic API course materials and follows the same licensing terms as the main repository.

---

For more information, see the main [README.md](../README.md) and the comprehensive examples in [format_grading_example.py](format_grading_example.py).
