# Comprehensive Grading System

This implementation provides a comprehensive grading system that combines code-based and model-based evaluation approaches, designed based on the [Anthropic Academy course content](https://anthropic.skilljar.com/claude-with-the-anthropic-api/287742) for prompt evaluation workflows.

## Overview

The grading system consists of three main components:

1. **CodeGrader**: Programmatic evaluation using custom logic
2. **ModelGrader**: AI-powered assessment using Claude
3. **Grader**: Main class that combines both approaches

## Architecture Decisions

### Inheritance Structure
- **Main Grader Class**: Inherits from `AnthropicClient` to leverage existing API functionality
- **File Organization**: The main Grader class is in its own file (`utils/graders.py`) for better modularity
- **Separation of Concerns**: Code and Model graders are separate classes that can be used independently

### Design Rationale
- **Inheritance from AnthropicClient**: Provides access to API functionality, authentication, and client management
- **Separate File**: Allows for better code organization and reusability
- **Modular Design**: Enables using code-based or model-based grading independently

## Features

### Code-Based Grading (`CodeGrader`)

#### 1. Output Length Checking
- **Parameters**: `min_length`, `max_length`
- **Function**: `check_output_length()`
- **Purpose**: Validates that output meets length requirements

#### 2. Word Verification
- **Parameters**: `required_words`, `forbidden_words`
- **Function**: `verify_words()`
- **Purpose**: Checks for presence/absence of specific words

#### 3. Syntax Validation
- **Parameters**: `syntax_check`
- **Function**: `validate_syntax()`
- **Supported Languages**: Python, JSON, Regex
- **Purpose**: Validates code syntax for specified language

#### 4. Readability Scoring
- **Parameters**: `readability_threshold`
- **Function**: `calculate_readability_score()`
- **Scale**: 1-10
- **Metrics**: Word count, sentence count, average words per sentence, formatting

### Model-Based Grading (`ModelGrader`)

#### 1. Response Quality Assessment
- **Function**: `assess_response_quality()`
- **Scale**: 1-10
- **Purpose**: Evaluates how well the response addresses the question/task

#### 2. Instruction Following Evaluation
- **Function**: `assess_instruction_following()`
- **Scale**: 1-10
- **Purpose**: Assesses how well the response follows given instructions

#### 3. Completeness Checking
- **Function**: `assess_completeness()`
- **Scale**: 1-10
- **Purpose**: Evaluates response completeness in addressing all aspects

#### 4. Helpfulness Scoring
- **Function**: `assess_helpfulness()`
- **Scale**: 1-10
- **Purpose**: Assesses how helpful and useful the response is

#### 5. Safety Assessment
- **Function**: `assess_safety()`
- **Scale**: 1-10
- **Purpose**: Evaluates response safety and appropriateness

## Usage Examples

### Basic Setup

```python
from utils.graders import Grader, CodeGrader, ModelGrader, GradingCriteria
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv('ANTHROPIC_API_KEY')

# Initialize graders
grader = Grader(api_key=api_key, model="claude-3-haiku-20240307")
code_grader = CodeGrader()
model_grader = ModelGrader(api_key=api_key, model="claude-3-haiku-20240307")
```

### Code-Based Grading

```python
# Python code validation
python_code = """
def calculate_sum(a, b):
    return a + b
"""

result = code_grader.grade(python_code, language="python")
print(f"Score: {result.score}/10")
print(f"Passed: {result.passed}")
print(f"Feedback: {result.feedback}")

# Custom criteria
custom_criteria = GradingCriteria(
    min_length=50,
    max_length=500,
    required_words=["python", "function"],
    forbidden_words=["error", "bug"],
    readability_threshold=6.0
)

custom_grader = CodeGrader(criteria=custom_criteria)
result = custom_grader.grade(text, language="text")
```

### Model-Based Grading

```python
prompt = "Explain how to create a Python function that calculates the factorial of a number."
response = """
To create a Python function that calculates the factorial of a number...
"""

result = model_grader.grade(prompt, response)
print(f"Score: {result.score}/10")
print(f"Passed: {result.passed}")
print(f"Feedback: {result.feedback}")

# Individual criterion assessment
instruction_result = model_grader.assess_instruction_following(prompt, response)
completeness_result = model_grader.assess_completeness(prompt, response)
helpfulness_result = model_grader.assess_helpfulness(prompt, response)
safety_result = model_grader.assess_safety(prompt, response)
```

### Comprehensive Grading

```python
# Combine both approaches
comprehensive_result = grader.grade_comprehensive(
    prompt, 
    response, 
    language="python"
)

code_result = comprehensive_result["code_grader"]
model_result = comprehensive_result["model_grader"]

print(f"Code Score: {code_result.score}/10")
print(f"Model Score: {model_result.score}/10")
```

### Batch Grading

```python
batch_evaluations = [
    {"prompt": "Write a function to add two numbers", "response": "def add(a, b): return a + b"},
    {"prompt": "Explain machine learning", "response": "Machine learning is..."},
    {"prompt": "Create a JSON object", "response": "{\"name\": \"John\"}"}
]

batch_results = grader.grade_batch(batch_evaluations, language="text")

# Generate comprehensive report
report = grader.generate_grading_report(batch_results)
print(json.dumps(report, indent=2))
```

### Advanced Usage

```python
# Custom grading prompt for specific domain
custom_prompt = """
You are an expert Python code reviewer. Evaluate the following code response based on these criteria:
1. Code Quality (1-10): Is the code well-written, efficient, and follows best practices?
2. Correctness (1-10): Does the code correctly solve the problem?
...
"""

grader.set_model_grading_prompt(custom_prompt)

# Custom code criteria
advanced_criteria = GradingCriteria(
    min_length=20,
    max_length=1000,
    required_words=["def", "return"],
    forbidden_words=["print", "input"],
    syntax_check=True,
    readability_threshold=5.0
)

grader.set_code_criteria(advanced_criteria)
```

## Data Structures

### GradingCriteria
```python
@dataclass
class GradingCriteria:
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required_words: List[str] = None
    forbidden_words: List[str] = None
    syntax_check: bool = True
    readability_threshold: float = 7.0
```

### GradingResult
```python
@dataclass
class GradingResult:
    score: float
    feedback: str
    details: Dict[str, Any]
    passed: bool
```

## Configuration

### Environment Variables
- `ANTHROPIC_API_KEY`: Your Anthropic API key

### Model Configuration
- Default model: `claude-3-haiku-20240307` (fast and cost-effective for grading)
- Can be customized for different use cases

### Grading Thresholds
- **Code Grader**: Uses `readability_threshold` (default: 7.0)
- **Model Grader**: Uses overall score threshold (default: 7.0)
- **Pass/Fail**: Determined by threshold comparison

## Error Handling

The system includes comprehensive error handling:

1. **API Errors**: Graceful handling of API failures
2. **JSON Parsing**: Fallback for malformed evaluation responses
3. **Syntax Errors**: Detailed error reporting for code validation
4. **Batch Processing**: Continues processing even if individual items fail

## Performance Considerations

1. **Model Selection**: Uses Claude Haiku for cost-effective grading
2. **Batch Processing**: Efficient handling of multiple evaluations
3. **Caching**: Can be extended with prompt caching for repeated evaluations
4. **Parallelization**: Batch processing can be parallelized for large datasets

## Extensibility

The system is designed to be easily extensible:

1. **New Grading Criteria**: Add new criteria to `GradingCriteria`
2. **Additional Languages**: Extend syntax validation in `CodeGrader`
3. **Custom Prompts**: Modify grading prompts for specific domains
4. **New Assessment Types**: Add new assessment methods to `ModelGrader`

## Best Practices

1. **API Key Management**: Use environment variables for API keys
2. **Error Handling**: Always check for errors in batch processing
3. **Customization**: Tailor criteria and prompts for your specific use case
4. **Validation**: Test with various input types and edge cases
5. **Documentation**: Document custom criteria and prompts

## Integration with Anthropic Academy Course

This implementation follows the best practices outlined in the Anthropic Academy course:

1. **Prompt Evaluation Workflows**: Implements both model-based and code-based grading
2. **Test Dataset Generation**: Supports batch evaluation of multiple prompt-response pairs
3. **Automated Grading**: Provides programmatic and AI-powered assessment
4. **Quality Metrics**: Implements comprehensive quality assessment criteria

## Files

- `utils/graders.py`: Main grading system implementation
- `grading_example.py`: Comprehensive usage examples
- `GRADING_SYSTEM_README.md`: This documentation file

## Running the Examples

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env

# Run the example
python grading_example.py
```

## Contributing

When extending the grading system:

1. Follow the existing code structure and patterns
2. Add comprehensive error handling
3. Include unit tests for new functionality
4. Update documentation for new features
5. Maintain backward compatibility

## License

This implementation is part of the Anthropic API course materials and follows the same licensing terms.
