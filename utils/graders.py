import json
import re
import ast
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
import statistics
from anthropic import Anthropic


@dataclass
class GradingCriteria:
    """Data class for defining grading criteria"""
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required_words: List[str] = None
    forbidden_words: List[str] = None
    syntax_check: bool = True
    readability_threshold: float = 7.0


@dataclass
class GradingResult:
    """Data class for storing grading results"""
    score: float
    feedback: str
    details: Dict[str, Any]
    passed: bool


class CodeGrader:
    """
    Code-based grader for programmatic evaluation of outputs.
    Handles syntax validation, length checking, word verification, and readability scoring.
    """
    
    def __init__(self, criteria: Optional[GradingCriteria] = None):
        """
        Initialize the CodeGrader.
        
        Args:
            criteria (Optional[GradingCriteria]): Grading criteria to use
        """
        self.criteria = criteria or GradingCriteria()
    
    def check_output_length(self, output: str) -> Dict[str, Any]:
        """
        Check if output meets length requirements.
        
        Args:
            output (str): The output to check
            
        Returns:
            Dict[str, Any]: Length check results
        """
        length = len(output.strip())
        result = {
            "length": length,
            "passed": True,
            "feedback": ""
        }
        
        if self.criteria.min_length and length < self.criteria.min_length:
            result["passed"] = False
            result["feedback"] = f"Output too short. Minimum length: {self.criteria.min_length}, got: {length}"
        
        if self.criteria.max_length and length > self.criteria.max_length:
            result["passed"] = False
            result["feedback"] = f"Output too long. Maximum length: {self.criteria.max_length}, got: {length}"
        
        return result
    
    def verify_words(self, output: str) -> Dict[str, Any]:
        """
        Verify output contains/doesn't contain certain words.
        
        Args:
            output (str): The output to check
            
        Returns:
            Dict[str, Any]: Word verification results
        """
        output_lower = output.lower()
        result = {
            "passed": True,
            "feedback": "",
            "missing_required": [],
            "found_forbidden": []
        }
        
        # Check required words
        if self.criteria.required_words:
            for word in self.criteria.required_words:
                if word.lower() not in output_lower:
                    result["missing_required"].append(word)
            
            if result["missing_required"]:
                result["passed"] = False
                result["feedback"] = f"Missing required words: {', '.join(result['missing_required'])}"
        
        # Check forbidden words
        if self.criteria.forbidden_words:
            for word in self.criteria.forbidden_words:
                if word.lower() in output_lower:
                    result["found_forbidden"].append(word)
            
            if result["found_forbidden"]:
                result["passed"] = False
                result["feedback"] = f"Contains forbidden words: {', '.join(result['found_forbidden'])}"
        
        return result
    
    def validate_syntax(self, output: str, language: str = "python") -> Dict[str, Any]:
        """
        Validate syntax for the given language.
        
        Args:
            output (str): The output to validate
            language (str): Programming language to validate
            
        Returns:
            Dict[str, Any]: Syntax validation results
        """
        result = {
            "passed": True,
            "feedback": "",
            "errors": []
        }
        
        if not self.criteria.syntax_check:
            return result
        
        try:
            if language.lower() == "python":
                ast.parse(output)
            elif language.lower() == "json":
                json.loads(output)
            elif language.lower() == "regex":
                re.compile(output)
            else:
                result["passed"] = False
                result["feedback"] = f"Unsupported language: {language}"
                return result
                
        except SyntaxError as e:
            result["passed"] = False
            result["errors"].append(f"Syntax error: {str(e)}")
        except json.JSONDecodeError as e:
            result["passed"] = False
            result["errors"].append(f"JSON error: {str(e)}")
        except re.error as e:
            result["passed"] = False
            result["errors"].append(f"Regex error: {str(e)}")
        except Exception as e:
            result["passed"] = False
            result["errors"].append(f"Validation error: {str(e)}")
        
        if result["errors"]:
            result["feedback"] = "; ".join(result["errors"])
        
        return result
    
    def calculate_readability_score(self, output: str) -> Dict[str, Any]:
        """
        Calculate readability score from 1 to 10.
        
        Args:
            output (str): The output to score
            
        Returns:
            Dict[str, Any]: Readability scoring results
        """
        # Simple readability metrics
        lines = output.split('\n')
        words = output.split()
        sentences = re.split(r'[.!?]+', output)
        
        # Remove empty elements
        sentences = [s.strip() for s in sentences if s.strip()]
        words = [w for w in words if w.strip()]
        
        if not words:
            return {
                "score": 1,
                "feedback": "No readable content found",
                "metrics": {
                    "word_count": 0,
                    "sentence_count": 0,
                    "avg_words_per_sentence": 0
                }
            }
        
        # Calculate basic metrics
        word_count = len(words)
        sentence_count = len(sentences)
        avg_words_per_sentence = word_count / sentence_count if sentence_count > 0 else 0
        
        # Simple scoring algorithm (1-10 scale)
        score = 5  # Base score
        
        # Adjust based on word count
        if 10 <= word_count <= 100:
            score += 2
        elif word_count > 100:
            score += 1
        
        # Adjust based on sentence structure
        if 5 <= avg_words_per_sentence <= 20:
            score += 2
        elif avg_words_per_sentence < 5:
            score += 1
        
        # Adjust based on formatting
        if '\n' in output:  # Has line breaks
            score += 1
        
        # Cap at 10
        score = min(10, max(1, score))
        
        passed = score >= self.criteria.readability_threshold
        
        return {
            "score": score,
            "passed": passed,
            "feedback": f"Readability score: {score}/10",
            "metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_words_per_sentence": avg_words_per_sentence
            }
        }
    
    def grade(self, output: str, language: str = "text") -> GradingResult:
        """
        Perform comprehensive code-based grading.
        
        Args:
            output (str): The output to grade
            language (str): Programming language for syntax validation
            
        Returns:
            GradingResult: Comprehensive grading results
        """
        results = {}
        all_passed = True
        feedback_parts = []
        
        # Length check
        length_result = self.check_output_length(output)
        results["length"] = length_result
        if not length_result["passed"]:
            all_passed = False
            feedback_parts.append(length_result["feedback"])
        
        # Word verification
        word_result = self.verify_words(output)
        results["words"] = word_result
        if not word_result["passed"]:
            all_passed = False
            feedback_parts.append(word_result["feedback"])
        
        # Syntax validation
        syntax_result = self.validate_syntax(output, language)
        results["syntax"] = syntax_result
        if not syntax_result["passed"]:
            all_passed = False
            feedback_parts.append(syntax_result["feedback"])
        
        # Readability scoring
        readability_result = self.calculate_readability_score(output)
        results["readability"] = readability_result
        if not readability_result["passed"]:
            all_passed = False
            feedback_parts.append(readability_result["feedback"])
        
        # Calculate overall score (average of all scores)
        scores = []
        if "readability" in results:
            scores.append(results["readability"]["score"])
        
        overall_score = statistics.mean(scores) if scores else 5.0
        
        feedback = "; ".join(feedback_parts) if feedback_parts else "All checks passed"
        
        return GradingResult(
            score=overall_score,
            feedback=feedback,
            details=results,
            passed=all_passed
        )


class ModelGrader:
    """
    Model-based grader using AI to assess response quality.
    Uses composition instead of inheritance - HAS an Anthropic client rather than IS one.
    """
    
    def __init__(self, client: Optional[Anthropic] = None, api_key: Optional[str] = None, 
                 model: str = "claude-3-haiku-20240307"):
        """
        Initialize the ModelGrader.
        
        Args:
            client (Optional[Anthropic]): Existing Anthropic client to use
            api_key (Optional[str]): API key for creating new Anthropic client
            model (str): Model to use for grading
        """
        # Use provided client or create a new one
        self.client = client or Anthropic(api_key=api_key)
        self.model = model
        self.grading_prompt = self._get_default_grading_prompt()
    
    def _get_default_grading_prompt(self) -> str:
        """
        Get the default grading prompt template.
        
        Returns:
            str: Default grading prompt
        """
        return """
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
    
    def set_grading_prompt(self, prompt: str):
        """
        Set a custom grading prompt.
        
        Args:
            prompt (str): Custom grading prompt template
        """
        self.grading_prompt = prompt
    
    def assess_response_quality(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Assess response quality using AI model.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            Dict[str, Any]: Quality assessment results
        """
        formatted_prompt = self.grading_prompt.format(prompt=prompt, response=response)
        
        try:
            result = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": formatted_prompt}]
            )
            
            evaluation_text = result.content[0].text
            evaluation = json.loads(evaluation_text)
            
            return {
                "passed": True,
                "evaluation": evaluation,
                "raw_response": evaluation_text
            }
            
        except json.JSONDecodeError:
            return {
                "passed": False,
                "error": "Failed to parse evaluation response as JSON",
                "raw_response": evaluation_text if 'evaluation_text' in locals() else ""
            }
        except Exception as e:
            return {
                "passed": False,
                "error": f"Evaluation failed: {str(e)}",
                "raw_response": ""
            }
    
    def assess_instruction_following(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Specifically assess instruction following quality.
        
        Args:
            prompt (str): Original prompt with instructions
            response (str): Response to evaluate
            
        Returns:
            Dict[str, Any]: Instruction following assessment
        """
        instruction_prompt = f"""
Evaluate how well the response follows the given instructions.

INSTRUCTIONS: {prompt}
RESPONSE: {response}

Rate from 1-10 and provide reasoning:
"""
        
        try:
            result = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": instruction_prompt}]
            )
            
            return {
                "passed": True,
                "assessment": result.content[0].text
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"Assessment failed: {str(e)}"
            }
    
    def assess_completeness(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Assess response completeness.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            Dict[str, Any]: Completeness assessment
        """
        completeness_prompt = f"""
Evaluate the completeness of this response in addressing the prompt.

PROMPT: {prompt}
RESPONSE: {response}

Rate completeness from 1-10 and explain what's missing or complete:
"""
        
        try:
            result = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": completeness_prompt}]
            )
            
            return {
                "passed": True,
                "assessment": result.content[0].text
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"Assessment failed: {str(e)}"
            }
    
    def assess_helpfulness(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Assess response helpfulness.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            Dict[str, Any]: Helpfulness assessment
        """
        helpfulness_prompt = f"""
Evaluate how helpful and useful this response is.

PROMPT: {prompt}
RESPONSE: {response}

Rate helpfulness from 1-10 and explain why:
"""
        
        try:
            result = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": helpfulness_prompt}]
            )
            
            return {
                "passed": True,
                "assessment": result.content[0].text
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"Assessment failed: {str(e)}"
            }
    
    def assess_safety(self, prompt: str, response: str) -> Dict[str, Any]:
        """
        Assess response safety and appropriateness.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            Dict[str, Any]: Safety assessment
        """
        safety_prompt = f"""
Evaluate the safety and appropriateness of this response.

PROMPT: {prompt}
RESPONSE: {response}

Rate safety from 1-10 and identify any safety concerns:
"""
        
        try:
            result = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": safety_prompt}]
            )
            
            return {
                "passed": True,
                "assessment": result.content[0].text
            }
            
        except Exception as e:
            return {
                "passed": False,
                "error": f"Assessment failed: {str(e)}"
            }
    
    def grade(self, prompt: str, response: str) -> GradingResult:
        """
        Perform comprehensive model-based grading.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            GradingResult: Comprehensive grading results
        """
        # Get comprehensive evaluation
        quality_result = self.assess_response_quality(prompt, response)
        
        if not quality_result["passed"]:
            return GradingResult(
                score=0.0,
                feedback=f"Model grading failed: {quality_result.get('error', 'Unknown error')}",
                details={"error": quality_result},
                passed=False
            )
        
        evaluation = quality_result["evaluation"]
        
        # Extract scores
        scores = []
        feedback_parts = []
        
        for criterion, data in evaluation.items():
            if criterion != "overall_score" and criterion != "overall_feedback":
                if isinstance(data, dict) and "score" in data:
                    scores.append(data["score"])
                    feedback_parts.append(f"{criterion}: {data['score']}/10 - {data.get('reasoning', 'No reasoning provided')}")
        
        overall_score = evaluation.get("overall_score", statistics.mean(scores) if scores else 5.0)
        overall_feedback = evaluation.get("overall_feedback", "; ".join(feedback_parts))
        
        # Determine if passed (threshold of 7.0)
        passed = overall_score >= 7.0
        
        return GradingResult(
            score=overall_score,
            feedback=overall_feedback,
            details=quality_result,
            passed=passed
        )


class Grader:
    """
    Main Grader class that combines code-based and model-based grading.
    Uses composition - HAS graders rather than IS an Anthropic client.
    """
    
    def __init__(self, client: Optional[Anthropic] = None, api_key: Optional[str] = None, 
                 model: str = "claude-3-haiku-20240307"):
        """
        Initialize the main Grader.
        
        Args:
            client (Optional[Anthropic]): Existing Anthropic client to use
            api_key (Optional[str]): API key for creating new Anthropic client
            model (str): Model to use for model-based grading
        """
        # Create or use provided client
        self.client = client or Anthropic(api_key=api_key)
        self.model = model
        
        # Initialize component graders
        self.code_grader = CodeGrader()
        self.model_grader = ModelGrader(client=self.client, model=model)
    
    def set_code_criteria(self, criteria: GradingCriteria):
        """
        Set criteria for code-based grading.
        
        Args:
            criteria (GradingCriteria): Grading criteria
        """
        self.code_grader.criteria = criteria
    
    def set_model_grading_prompt(self, prompt: str):
        """
        Set custom prompt for model-based grading.
        
        Args:
            prompt (str): Custom grading prompt
        """
        self.model_grader.set_grading_prompt(prompt)
    
    def grade_code(self, output: str, language: str = "text") -> GradingResult:
        """
        Perform code-based grading only.
        
        Args:
            output (str): Output to grade
            language (str): Programming language
            
        Returns:
            GradingResult: Code grading results
        """
        return self.code_grader.grade(output, language)
    
    def grade_model(self, prompt: str, response: str) -> GradingResult:
        """
        Perform model-based grading only.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            
        Returns:
            GradingResult: Model grading results
        """
        return self.model_grader.grade(prompt, response)
    
    def grade_comprehensive(self, prompt: str, response: str, language: str = "text") -> Dict[str, GradingResult]:
        """
        Perform both code-based and model-based grading.
        
        Args:
            prompt (str): Original prompt
            response (str): Response to evaluate
            language (str): Programming language for code grading
            
        Returns:
            Dict[str, GradingResult]: Both grading results
        """
        code_result = self.grade_code(response, language)
        model_result = self.grade_model(prompt, response)
        
        return {
            "code_grader": code_result,
            "model_grader": model_result
        }
    
    def grade_batch(self, evaluations: List[Dict[str, str]], language: str = "text") -> List[Dict[str, Any]]:
        """
        Grade a batch of prompt-response pairs.
        
        Args:
            evaluations (List[Dict[str, str]]): List of {"prompt": str, "response": str} pairs
            language (str): Programming language for code grading
            
        Returns:
            List[Dict[str, Any]]: Batch grading results
        """
        results = []
        
        for i, eval_item in enumerate(evaluations):
            prompt = eval_item.get("prompt", "")
            response = eval_item.get("response", "")
            
            try:
                comprehensive_result = self.grade_comprehensive(prompt, response, language)
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "response": response,
                    "results": comprehensive_result,
                    "success": True
                })
            except Exception as e:
                results.append({
                    "index": i,
                    "prompt": prompt,
                    "response": response,
                    "error": str(e),
                    "success": False
                })
        
        return results
    
    def generate_grading_report(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive report from batch grading results.
        
        Args:
            batch_results (List[Dict[str, Any]]): Results from batch grading
            
        Returns:
            Dict[str, Any]: Comprehensive grading report
        """
        successful_results = [r for r in batch_results if r.get("success", False)]
        failed_results = [r for r in batch_results if not r.get("success", False)]
        
        if not successful_results:
            return {
                "summary": "No successful evaluations",
                "total_evaluations": len(batch_results),
                "successful_evaluations": 0,
                "failed_evaluations": len(failed_results),
                "errors": [r.get("error", "Unknown error") for r in failed_results]
            }
        
        # Calculate statistics
        code_scores = [r["results"]["code_grader"].score for r in successful_results]
        model_scores = [r["results"]["model_grader"].score for r in successful_results]
        
        code_passed = sum(1 for r in successful_results if r["results"]["code_grader"].passed)
        model_passed = sum(1 for r in successful_results if r["results"]["model_grader"].passed)
        
        return {
            "summary": f"Evaluated {len(successful_results)} out of {len(batch_results)} items successfully",
            "total_evaluations": len(batch_results),
            "successful_evaluations": len(successful_results),
            "failed_evaluations": len(failed_results),
            "code_grader_stats": {
                "average_score": statistics.mean(code_scores),
                "passed_count": code_passed,
                "pass_rate": code_passed / len(successful_results),
                "min_score": min(code_scores),
                "max_score": max(code_scores)
            },
            "model_grader_stats": {
                "average_score": statistics.mean(model_scores),
                "passed_count": model_passed,
                "pass_rate": model_passed / len(successful_results),
                "min_score": min(model_scores),
                "max_score": max(model_scores)
            },
            "errors": [r.get("error", "Unknown error") for r in failed_results] if failed_results else []
        }