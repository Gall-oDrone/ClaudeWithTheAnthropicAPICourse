GRADING_PROMPT_1 = """
You are an expert evaluator. Please assess the quality of the following response based on the given criteria.

CRITERIA:
1. Response Quality (1-10): How well does the response address the question/task?
2. Instruction Following (1-10): How well does the response follow the given instructions?
3. Completeness (1-10): How complete is the response in addressing all aspects?
4. Helpfulness (1-10): How helpful and useful is the response?
5. Safety (1-10): How safe and appropriate is the response?

Please provide your evaluation in the following JSON format:
{{
    "response_quality": {{"score": X, "reasoning": "explanation"}},
    "instruction_following": {{"score": X, "reasoning": "explanation"}},
    "completeness": {{"score": X, "reasoning": "explanation"}},
    "helpfulness": {{"score": X, "reasoning": "explanation"}},
    "safety": {{"score": X, "reasoning": "explanation"}},
    "overall_score": X,
    "overall_feedback": "summary of evaluation"
}}

ORIGINAL PROMPT: {prompt}

RESPONSE TO EVALUATE: {response}

EVALUATION:
"""

STRICT_PYTHON_GRADING_PROMPT_1 = """
You are a strict Python code evaluator. Evaluate with ZERO tolerance for incompleteness.

REQUIREMENTS FOR PASSING (ALL must be met):
1. The code MUST be complete and executable (no placeholders, no "...", no TODO)
2. If a function was requested, it MUST have proper def, parameters, and return
3. The code MUST be syntactically correct
4. The code MUST do what was requested

SCORING:
- Incomplete code (TODO, ..., placeholder): Score 1-3
- Missing key components: Score 2-4
- Syntax errors: Score 1-3
- Only give 7+ if complete and correct
- Only give 9-10 if excellent with error handling

Evaluate in JSON format:
{{
    "is_complete": true/false,
    "has_required_structure": true/false,
    "addresses_prompt": true/false,
    "overall_score": X,
    "overall_feedback": "specific feedback"
}}

PROMPT: {prompt}
RESPONSE: {response}
"""

STRICT_JSON_GRADING_PROMPT_1 = """
You are a strict JSON evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid JSON
2. MUST have ALL required fields
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid JSON: Score 1-2
- Missing fields: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid

Evaluate in JSON format:
{{
    "is_valid_json": true/false,
    "has_all_required_fields": true/false,
    "overall_score": X,
    "overall_feedback": "specific feedback"
}}

PROMPT: {prompt}
RESPONSE: {response}
"""

STRICT_REGEX_GRADING_PROMPT_1 = """
You are a strict regex evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid regex
2. MUST match the pattern exactly
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid regex: Score 1-2
- Missing pattern: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

STRICT_XML_GRADING_PROMPT_1 = """
You are a strict XML evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid XML
2. MUST have ALL required elements
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid XML: Score 1-2
- Missing elements: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

STRICT_YAML_GRADING_PROMPT_1 = """
You are a strict YAML evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid YAML
2. MUST have ALL required fields
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid YAML: Score 1-2
- Missing fields: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

STRICT_CSV_GRADING_PROMPT_1 = """
You are a strict CSV evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid CSV
2. MUST have ALL required columns
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid CSV: Score 1-2
- Missing columns: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

STRICT_MARKDOWN_GRADING_PROMPT_1 = """
You are a strict Markdown evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid Markdown
2. MUST have ALL required sections
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid Markdown: Score 1-2
- Missing sections: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

STRICT_HTML_GRADING_PROMPT_1 = """
You are a strict HTML evaluator. Evaluate with ZERO tolerance for errors.

REQUIREMENTS:
1. MUST be valid HTML
2. MUST have ALL required elements
3. NO placeholder values ("...", "TODO", empty strings)
4. Values must be appropriate

SCORING:
- Invalid HTML: Score 1-2
- Missing elements: Score 2-4
- Placeholder values: Score 3-5
- Only give 7+ if complete and valid
"""

# Rubric-based grading with optional mandatory criteria (task/solution-criteria style)
RUBRIC_GRADING_PROMPT = """
Your task is to evaluate the following AI-generated solution with rigor.

Original task description:
<task_description>
{task_description}
</task_description>

Original task inputs:
<task_inputs>
{task_inputs}
</task_inputs>

Solution to Evaluate:
<solution>
{solution}
</solution>

Criteria you should use to evaluate the solution:
<criteria>
{solution_criteria}
</criteria>

{extra_criteria_section}

Scoring Guidelines:
* Score 1-3: Solution fails to meet one or more MANDATORY requirements
* Score 4-6: Solution meets all mandatory requirements but has significant deficiencies in secondary criteria
* Score 7-8: Solution meets all mandatory requirements and most secondary criteria, with minor issues
* Score 9-10: Solution meets all mandatory and secondary criteria

IMPORTANT SCORING INSTRUCTIONS:
* Grade the output based ONLY on the listed criteria. Do not add your own extra requirements.
* If a solution meets all of the mandatory and secondary criteria give it a 10
* ANY violation of a mandatory requirement MUST result in a score of 3 or lower
* The full 1-10 scale should be utilized

Output Format: Provide your evaluation as a structured JSON object with the following fields, in this order:
- "strengths": An array of 1-3 key strengths
- "weaknesses": An array of 1-3 key areas for improvement
- "reasoning": A concise explanation of your overall assessment
- "score": A number between 1-10

Respond with JSON only. Example shape:
{{
    "strengths": ["string"],
    "weaknesses": ["string"],
    "reasoning": "string",
    "score": number
}}
"""
