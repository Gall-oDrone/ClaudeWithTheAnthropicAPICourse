EVALUATION_DATASET_1_PROMPT = """
Generate a evaluation dataset for a prompt evaluation. \n
The dataset will be used to evaluate prompts that generate Python, JSON, or Regex specifically for AWS-related tasks. \n
Generate an array of JSON objects, each representing task that requires Python, JSON, or a REgex to complete. \n

Example output:
```json
[
    {
        "prompt": "Description of the task",
        "expected_response": "Description of the expected output."
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
        "expected_response": "Description of the expected output."
    }
]
```

* Focus on tasks that can be solved by  writing a simple Python funciton, a single JSON object, or a single regex
* Focus on tasks that do not require writing much code
* Respon only with Python, JSON, or plain Regex
* Do not add any comments or explanations

Please generate 20 tasks.
"""
