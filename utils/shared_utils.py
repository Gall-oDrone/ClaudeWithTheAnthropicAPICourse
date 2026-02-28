"""
Shared utilities for evaluation and grading systems.
Contains common functionality to avoid code duplication.
"""

from typing import List, Tuple, Dict, Any
import re
import json


class TemplateRenderer:
    """
    Renders template strings with {placeholder} substitution.
    Use {{ and }} for literal braces in the output.
    """

    PLACEHOLDER_PATTERN = re.compile(r"{([^{}]+)}")

    @classmethod
    def render(cls, template_string: str, variables: Dict[str, Any]) -> str:
        """
        Replace {key} with variables[key] in template_string.
        Use {{ and }} to emit literal { and }.

        Args:
            template_string: String containing {key} placeholders and optional {{ }}
            variables: Dict of placeholder name -> value

        Returns:
            str: Rendered string
        """
        placeholders = cls.PLACEHOLDER_PATTERN.findall(template_string)
        result = template_string
        for placeholder in placeholders:
            if placeholder in variables:
                result = result.replace(
                    "{" + placeholder + "}", str(variables[placeholder])
                )
        # Literal braces: {{ -> {, }} -> }
        result = result.replace("{{", "\x00").replace("}}", "\x01")
        result = result.replace("\x00", "{").replace("\x01", "}")
        return result


class IncompletenessDetector:
    """Utility class for detecting incomplete responses."""
    
    # Common incompleteness indicators
    INCOMPLETENESS_INDICATORS = [
        "...",
        "TODO",
        "FIXME", 
        "placeholder",
        "# Add your",
        "# Implement",
        "pass  # Implement",
        "raise NotImplementedError",
        "# Your code here",
        "coming soon",
        "to be implemented",
        "Coming soon",
        "To be implemented"
    ]
    
    @classmethod
    def detect_incomplete_response(cls, response: str) -> Tuple[bool, str]:
        """
        Detect if a response contains incompleteness indicators.
        
        Args:
            response: The response to check
            
        Returns:
            tuple: (is_incomplete, error_message)
        """
        for indicator in cls.INCOMPLETENESS_INDICATORS:
            if indicator in response:
                return True, f"Response contains incomplete marker: '{indicator}'"
        return False, "Complete"
    
    @classmethod
    def validate_response_completeness(cls, response: str, format_type: str, prompt: str) -> Tuple[bool, str]:
        """
        Validate if a response is complete and usable.
        
        Args:
            response: The response to validate
            format_type: Expected format (python, json, etc.)
            prompt: Original prompt for context
            
        Returns:
            tuple: (is_complete, error_message)
        """
        # Check for common incompleteness indicators
        is_incomplete, error_msg = cls.detect_incomplete_response(response)
        if is_incomplete:
            return False, error_msg
        
        # Format-specific completeness checks
        if format_type == "python":
            if any(word in prompt.lower() for word in ["function", "def ", "method"]):
                if "def " not in response:
                    return False, "Function requested but no 'def' statement found"
                if "return" not in response and "yield" not in response:
                    return False, "Function has no return or yield statement"
                if response.strip().endswith("pass"):
                    return False, "Function body is just 'pass'"
                # Check for incomplete return statements
                if "return" in response and response.count("return") == 1:
                    return_line = [line for line in response.split('\n') if 'return' in line][0]
                    if return_line.strip() == 'return' or return_line.strip().endswith('return'):
                        return False, "Function has incomplete return statement"
            # Only check line count for very short responses
            if len(response.strip()) < 20:
                return False, "Response too short to be a complete implementation"
                
        elif format_type == "json":
            try:
                parsed = json.loads(response)
                if isinstance(parsed, dict):
                    if all(v in ["", None, [], {}] for v in parsed.values()):
                        return False, "JSON has only empty values"
            except json.JSONDecodeError as e:
                return False, f"Invalid JSON: {e}"
                
        elif format_type == "regex":
            try:
                re.compile(response)
                if len(response) < 5:
                    return False, "Regex pattern too short to be meaningful"
            except re.error as e:
                return False, f"Invalid regex: {e}"
        
        return True, "Complete"


class ResponseFormatter:
    """Utility class for cleaning and formatting responses."""
    
    @staticmethod
    def clean_response_format(response: str, format_type: str) -> str:
        """
        Clean response by removing markdown formatting.
        
        Args:
            response: Raw response
            format_type: Expected format
            
        Returns:
            str: Cleaned response
        """
        if format_type == "python" and "```" in response:
            if "```python" in response:
                response = response.split("```python")[1].split("```")[0]
            elif "```" in response:
                parts = response.split("```")
                if len(parts) >= 3:
                    response = parts[1]
            return response.strip()
            
        elif format_type == "json" and "```" in response:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                parts = response.split("```")
                if len(parts) >= 3:
                    response = parts[1]
            # Try to extract valid JSON
            response = response.strip()
            try:
                json.loads(response)
                return response
            except:
                # Try to find JSON in response
                json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
                if json_match:
                    try:
                        # Validate the extracted JSON
                        json.loads(json_match.group(0))
                        return json_match.group(0)
                    except:
                        pass
            return response
            
        elif format_type == "regex":
            if "```" in response:
                response = response.replace("```", "").strip()
            response = response.replace("`", "").strip()
            if response.startswith("/") and response.endswith("/"):
                response = response[1:-1]
            return response
            
        return response.strip()
    
    @staticmethod
    def get_format_instructions(format_type: str) -> str:
        """
        Get format-specific instructions to append to prompts.
        
        Args:
            format_type: The expected format
            
        Returns:
            str: Instructions to append to prompt
        """
        instructions = {
            "python": "\n\nIMPORTANT: Provide COMPLETE, WORKING Python code only. No explanations, no markdown formatting (no ```python), no comments, no TODO, no placeholders, no '...'. The code must be fully functional and ready to run.",
            "json": "\n\nIMPORTANT: Provide ONLY valid JSON. No explanations, no markdown formatting (no ```json), no comments, no placeholders, no '...' values. All fields must have real, appropriate values.",
            "regex": "\n\nIMPORTANT: Provide ONLY the regular expression pattern. No explanations, no delimiters (no / /), no markdown formatting, no placeholders. Just the raw regex pattern.",
            "xml": "\n\nIMPORTANT: Provide ONLY valid XML. No explanations, no markdown formatting, no comments.",
            "yaml": "\n\nIMPORTANT: Provide ONLY valid YAML. No explanations, no markdown formatting, no comments.",
            "csv": "\n\nIMPORTANT: Provide ONLY CSV data. No explanations, no markdown formatting.",
            "markdown": "\n\nProvide properly formatted Markdown."
        }
        return instructions.get(format_type, "")


class FormatDetector:
    """Utility class for detecting and working with different formats."""
    
    @staticmethod
    def detect_format_type(prompt: str, response: str) -> str:
        """
        Detect the expected format type from prompt and response.
        
        Args:
            prompt: The original prompt
            response: The response to analyze
            
        Returns:
            str: Detected format type
        """
        prompt_lower = prompt.lower()
        response_lower = response.lower()
        
        # Check prompt for format indicators
        if any(word in prompt_lower for word in ["json", "javascript object notation"]):
            return "json"
        elif any(word in prompt_lower for word in ["xml", "extensible markup language"]):
            return "xml"
        elif any(word in prompt_lower for word in ["markdown", "md", "github"]):
            return "markdown"
        elif any(word in prompt_lower for word in ["csv", "comma separated", "spreadsheet"]):
            return "csv"
        elif any(word in prompt_lower for word in ["yaml", "yml", "yaml file"]):
            return "yaml"
        
        # Check response content for format indicators
        if response.strip().startswith('{') and response.strip().endswith('}'):
            return "json"
        elif response.strip().startswith('<') and '>' in response:
            return "xml"
        elif '#' in response and ('```' in response or '**' in response or '*' in response):
            return "markdown"
        elif ',' in response and '\n' in response and response.count(',') >= 1 and not 'def ' in response:
            return "csv"
        elif ':' in response and ('-' in response or response.count(':') >= 1) and not 'def ' in response and not 'return ' in response:
            return "yaml"
        
        # Default to text if no format detected
        return "text"
    
    @staticmethod
    def is_code_prompt(prompt: str) -> bool:
        """Check if a prompt is requesting code generation."""
        code_indicators = [
            "function", "code", "program", "script", "def ", "class ", "import ",
            "write a", "create a", "implement", "algorithm", "syntax"
        ]
        return any(keyword in prompt.lower() for keyword in code_indicators)
    
    @staticmethod
    def is_format_prompt(prompt: str) -> bool:
        """Check if a prompt is requesting a specific format."""
        format_indicators = [
            "json", "xml", "markdown", "csv", "yaml", "format", "structure"
        ]
        return any(keyword in prompt.lower() for keyword in format_indicators)


class ErrorHandler:
    """Utility class for consistent error handling patterns."""
    
    @staticmethod
    def create_grading_result(score: float, feedback: str, details: Dict[str, Any], passed: bool):
        """Create a consistent GradingResult object."""
        from utils.graders import GradingResult
        return GradingResult(
            score=score,
            feedback=feedback,
            details=details,
            passed=passed
        )
    
    @staticmethod
    def handle_evaluation_error(test_case: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """Create a consistent error result for evaluation failures."""
        return {
            "test_case": test_case,
            "error": str(error),
            "passed": False,
            "grading_results": {},
            "actual_response": ""
        }
