EVALUATION_DATASET_1_PROMPT = """
Generate a evaluation dataset for a prompt evaluation. \n
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. \n
Generate an array of JSON objects, each representing task that requires Python, JSON, or a REgex to complete. \n

Example output:
```json
[
    {
        "prompt": "Description of the task",
        "solution_criteria": "Description of the expected output."
    }
]
```

* Focus on tasks that can be solved by  writing a simple Python funciton, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code

Please generate 20 tasks.
"""

EVALUATION_DATASET_2_PROMPT = """
Generate a evaluation dataset for a prompt evaluation. \n
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. \n
Generate an array of JSON objects, each representing task that requires Python, JSON, or a REgex to complete. \n

Example output:
```json
[
    {
        "prompt": "Description of the task",
        "format": "python" or "json" or "regex",
        "solution_criteria": "Description of the expected output."
    }
]
```

* Focus on tasks that can be solved by  writing a simple Python funciton, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code
* Respon only with Python, JSON, or plain Regex
* Do not add any comments or explanations

Please generate 20 tasks.
"""

#  Enhanced evaluation dataset prompt with format specifications and grading configuration
EVALUATION_DATASET_3_PROMPT = """
Generate an evaluation dataset for a prompt evaluation. \n
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. \n
Generate an array of JSON objects, each representing a task that requires Python, JSON, or a Regex to complete. \n

Example output:
```json
[
    {
        "prompt": "Write a Python function that retrieves the list of EC2 instances in a specific AWS region",
        "format": "python",
        "solution_criteria": "A Python function using boto3 to list EC2 instances",
        "grading_config": {
            "code": {
                "min_length": 100,
                "required_words": ["def", "boto3", "ec2", "return"],
                "syntax_check": true
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
                "validate_json_schema": true,
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
                "syntax_check": true
            }
        }
    }
]
```

* Focus on tasks that can be solved by writing a simple Python function, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code
* Each task must include a comprehensive grading_config that specifies evaluation criteria
* For Python tasks: include code validation, required keywords, minimum length, and syntax checking
* For JSON tasks: include required/forbidden fields, JSON schema validation, and format checking
* For Regex tasks: include syntax validation and minimum length requirements
* Respond only with Python, JSON, or plain Regex
* Do not add any comments or explanations

Please generate 20 tasks with diverse AWS services and appropriate grading configurations.
"""