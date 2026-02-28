import json
from typing import Optional, List, Dict, Any, Tuple, Callable
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.graders import Grader, GradingResult, GradingCriteria, FormatGradingCriteria
from utils.shared_utils import IncompletenessDetector, ResponseFormatter, FormatDetector, ErrorHandler, TemplateRenderer


class GradingResultEncoder(json.JSONEncoder):
    """Custom JSON encoder for GradingResult objects"""
    
    def default(self, obj):
        if isinstance(obj, GradingResult):
            return {
                "score": obj.score,
                "feedback": obj.feedback,
                "details": obj.details,
                "passed": obj.passed
            }
        return super().default(obj)


class Evaluator:
    """
    Evaluator class that orchestrates evaluation workflows.
    Coordinates between ChatClient and Grader components.
    """
    
    def __init__(self, chat_client, grader: Optional[Grader] = None):
        """
        Initialize the Evaluator.
        
        Args:
            chat_client: ChatClient instance to use for generating responses
            grader (Optional[Grader]): Optional Grader instance. If None, creates a new one.
        """
        self.chat_client = chat_client
        self.grader = grader
    
    def _get_or_create_grader(self) -> Grader:
        """
        Get existing grader or create a new one if needed.
        
        Returns:
            Grader: The grader instance
        """
        if self.grader is None:
            # Share the same Anthropic client for efficiency
            self.grader = Grader(client=self.chat_client.get_client())
        return self.grader
    
    def set_grader(self, grader: Grader):
        """
        Set a custom grader instance.
        
        Args:
            grader (Grader): The grader to use for evaluations
        """
        self.grader = grader
    
    def validate_response_completeness(self, response: str, format_type: str, prompt: str) -> Tuple[bool, str]:
        """
        Validate if a response is complete and usable.
        
        Args:
            response: The response to validate
            format_type: Expected format (python, json, etc.)
            prompt: Original prompt for context
            
        Returns:
            tuple: (is_complete, error_message)
        """
        return IncompletenessDetector.validate_response_completeness(response, format_type, prompt)

    def clean_response_format(self, response: str, format_type: str) -> str:
        """
        Clean response by removing markdown formatting.
        
        Args:
            response: Raw response
            format_type: Expected format
            
        Returns:
            str: Cleaned response
        """
        return ResponseFormatter.clean_response_format(response, format_type)

    def get_format_instructions(self, format_type: str) -> str:
        """
        Get format-specific instructions to append to prompts.
        
        Args:
            format_type: The expected format
            
        Returns:
            str: Instructions to append to prompt
        """
        return ResponseFormatter.get_format_instructions(format_type)


    def _resolve_prompt(self, test_case: Dict[str, Any]) -> str:
        """
        Resolve prompt from test case. If prompt_template and prompt_inputs are present,
        render template; otherwise use prompt.
        """
        if test_case.get("prompt_template") and test_case.get("prompt_inputs"):
            return TemplateRenderer.render(
                test_case["prompt_template"],
                test_case["prompt_inputs"],
            )
        return test_case.get("prompt", "")

    def run_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case evaluation.

        Test case may be:
        - Standard: prompt, solution_criteria, format
        - Parameterized: prompt_template, prompt_inputs (dict), scenario, solution_criteria, format
        - Optional: mandatory_criteria for rubric grading (any violation => low score)
        """
        grader = self._get_or_create_grader()

        prompt = self._resolve_prompt(test_case)
        solution_criteria = test_case.get("solution_criteria", "")
        mandatory_criteria = test_case.get("mandatory_criteria")
        task_description = test_case.get("task_description")
        task_inputs_str = None
        if test_case.get("prompt_inputs") and isinstance(test_case["prompt_inputs"], dict):
            task_inputs_str = ", ".join(
                f"{k}={v!r}" for k, v in test_case["prompt_inputs"].items()
            )
        format_type = test_case.get("format", "text")

        # Add format-specific instructions to the prompt
        enhanced_prompt = prompt + self.get_format_instructions(format_type)

        # Generate response using the chat client
        # Store original messages to restore later
        original_messages = self.chat_client.params.get("messages", []).copy()
        
        # Set up new conversation for this test case
        self.chat_client.params["messages"] = [{"role": "user", "content": prompt}]
        
        # Set format-specific system prompt if needed
        if format_type != "text":
            format_systems = {
                "python": "You are a Python code generator. Output only valid Python code without any explanations or markdown formatting.",
                "json": "You are a JSON generator. Output only valid JSON without any explanations or markdown formatting.",
                "regex": "You are a regex pattern generator. Output only the regular expression pattern without any explanations or delimiters.",
                "xml": "You are an XML generator. Output only valid XML without any explanations or markdown formatting.",
                "yaml": "You are a YAML generator. Output only valid YAML without any explanations or markdown formatting.",
                "csv": "You are a CSV generator. Output only CSV format data without any explanations.",
                "markdown": "You are a Markdown formatter. Output only properly formatted Markdown."
            }
        
            original_system = self.chat_client.params.get("system")
            if format_type in format_systems:
                self.chat_client.set_system(format_systems[format_type])
    
        # Generate response
        self.chat_client.params["messages"] = [{"role": "user", "content": enhanced_prompt}]
        actual_response = self.chat_client.send_message()
        
        # Restore original messages
        self.chat_client.params["messages"] = original_messages
        if 'original_system' in locals():
            if original_system:
                self.chat_client.set_system(original_system)
            else:
                self.chat_client.params.pop("system", None)
        
        # Clean the response
        actual_response = self.clean_response_format(actual_response, format_type)
    
        # Validate response completeness
        is_complete, error_msg = self.validate_response_completeness(actual_response, format_type, prompt)

        # Grade: use rubric when solution_criteria present
        grade_kwargs = {
            "prompt": prompt,
            "response": actual_response,
            "language": format_type,
            "include_format": True,
        }
        if solution_criteria:
            grade_kwargs["solution_criteria"] = (
                solution_criteria
                if isinstance(solution_criteria, list)
                else [s.strip() for s in str(solution_criteria).split("\n") if s.strip()]
                if "\n" in str(solution_criteria)
                else solution_criteria
            )
            if mandatory_criteria is not None:
                grade_kwargs["mandatory_criteria"] = mandatory_criteria
            if task_description is not None:
                grade_kwargs["task_description"] = task_description
            if task_inputs_str is not None:
                grade_kwargs["task_inputs"] = task_inputs_str

        grading_result = grader.grade_comprehensive(**grade_kwargs)
        
        # Force fail if response is incomplete
        if not is_complete:
            # Override grading results for incomplete responses
            if "model_grader" in grading_result:
                grading_result["model_grader"] = ErrorHandler.create_grading_result(
                    score=2.0,
                    feedback=f"FAILED: {error_msg}",
                    details={"incomplete": True, "error": error_msg},
                    passed=False
                )
            if "code_grader" in grading_result and format_type == "python":
                grading_result["code_grader"] = ErrorHandler.create_grading_result(
                    score=2.0,
                    feedback=f"FAILED: {error_msg}",
                    details={"incomplete": True, "error": error_msg},
                    passed=False
                )
        # Determine if test passed
        # For text responses, only require model grader to pass
        # For code responses, require both to pass
        # For format-specific responses, require format grader to pass
        is_code_prompt = FormatDetector.is_code_prompt(prompt)
        is_format_prompt = FormatDetector.is_format_prompt(prompt)
        
        if not is_complete:
            passed = False
        elif is_code_prompt:
            # For code prompts, require both graders to pass
            passed = (
                grading_result["model_grader"].passed and 
                grading_result["code_grader"].passed
            )
        elif is_format_prompt and "format_grader" in grading_result:
            # For format prompts, require format grader to pass
            passed = grading_result["format_grader"].passed
        else:
            # For text prompts, only require model grader to pass
            passed = grading_result["model_grader"].passed
        
        return {
            "test_case": test_case,
            "actual_response": actual_response,
            "solution_criteria": solution_criteria,
            "grading_results": grading_result,
            "passed": passed
        }
    
    def run_eval(
        self,
        test_dataset: List[Dict[str, Any]],
        save_results: bool = True,
        results_path: str = "eval_results.json",
        verbose: bool = True,
        max_workers: int = 1,
        html_report_path: Optional[str] = None,
        progress_milestone_percent: int = 20,
    ) -> Dict[str, Any]:
        """
        Run evaluation on a complete test dataset.

        Args:
            test_dataset: List of test cases (prompt or prompt_template+prompt_inputs, etc.)
            save_results: Whether to save JSON results
            results_path: Path for JSON results
            verbose: Print progress
            max_workers: If > 1, run test cases concurrently (beware rate limits)
            html_report_path: If set, generate HTML report to this path
            progress_milestone_percent: Print progress every N% (e.g. 20 = 20%, 40%, ...)

        Returns:
            Summary dict with total_tests, passed_tests, pass_rate, results
        """
        total_tests = len(test_dataset)
        results = []
        passed_count = 0
        last_milestone = -1

        def run_one(i_tc):
            i, test_case = i_tc
            try:
                return i, self.run_test_case(test_case), None
            except Exception as e:
                return i, ErrorHandler.handle_evaluation_error(test_case, e), e

        if max_workers <= 1:
            for i, test_case in enumerate(test_dataset):
                if verbose:
                    print(f"Running test case {i+1}/{total_tests}...")
                _, test_result, err = run_one((i, test_case))
                results.append(test_result)
                if test_result.get("passed"):
                    passed_count += 1
                    if verbose:
                        print(f"  ✓ Test case {i+1} passed")
                else:
                    if verbose:
                        print(f"  ✗ Test case {i+1} failed")
                if err and verbose:
                    print(f"  ✗ Error: {err}")
                # Milestone progress
                if verbose and total_tests > 0 and progress_milestone_percent > 0:
                    pct = int((len(results) / total_tests) * 100)
                    milestone = (pct // progress_milestone_percent) * progress_milestone_percent
                    if milestone > last_milestone and milestone <= 100:
                        print(f"  Graded {len(results)}/{total_tests} test cases ({pct}%)")
                        last_milestone = milestone
        else:
            completed = 0
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {
                    executor.submit(run_one, (i, tc)): i
                    for i, tc in enumerate(test_dataset)
                }
                result_by_idx = {}
                for future in as_completed(future_to_idx):
                    i, test_result, err = future.result()
                    result_by_idx[i] = test_result
                    completed += 1
                    if verbose and total_tests > 0 and progress_milestone_percent > 0:
                        pct = int((completed / total_tests) * 100)
                        milestone = (pct // progress_milestone_percent) * progress_milestone_percent
                        if milestone > last_milestone and milestone <= 100:
                            print(f"  Graded {completed}/{total_tests} test cases ({pct}%)")
                            last_milestone = milestone
            for i in range(total_tests):
                results.append(result_by_idx[i])
            passed_count = sum(1 for r in results if r.get("passed"))

        pass_rate = passed_count / total_tests if total_tests > 0 else 0
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_count,
            "failed_tests": total_tests - passed_count,
            "pass_rate": pass_rate,
            "results": results,
        }

        if save_results:
            with open(results_path, "w") as f:
                json.dump(summary, f, indent=4, cls=GradingResultEncoder)
            if verbose:
                print(f"\nResults saved to {results_path}")

        if html_report_path:
            from utils.report import generate_evaluation_report
            generate_evaluation_report(summary, output_path=html_report_path)
            if verbose:
                print(f"HTML report saved to {html_report_path}")

        if verbose:
            print(f"\nEvaluation complete: {passed_count}/{total_tests} tests passed ({pass_rate:.2%})")

        return summary
    
    def run_batch_eval(self,
                      test_datasets: Dict[str, List[Dict[str, str]]],
                      save_results: bool = True,
                      results_dir: str = ".",
                      verbose: bool = True) -> Dict[str, Dict[str, Any]]:
        """
        Run evaluation on multiple test datasets.
        
        Args:
            test_datasets (Dict[str, List[Dict[str, str]]]): Dictionary of dataset_name -> test cases
            save_results (bool): Whether to save results to files
            results_dir (str): Directory to save result files
            verbose (bool): Whether to print progress messages
            
        Returns:
            Dict[str, Dict[str, Any]]: Results for each dataset
        """
        all_results = {}
        
        for dataset_name, dataset in test_datasets.items():
            if verbose:
                print(f"\n{'='*50}")
                print(f"Evaluating dataset: {dataset_name}")
                print(f"{'='*50}")
            
            results_path = f"{results_dir}/{dataset_name}_results.json" if save_results else None
            
            results = self.run_eval(
                test_dataset=dataset,
                save_results=save_results,
                results_path=results_path,
                verbose=verbose
            )
            
            all_results[dataset_name] = results
        
        if verbose:
            print(f"\n{'='*50}")
            print("OVERALL SUMMARY")
            print(f"{'='*50}")
            for dataset_name, results in all_results.items():
                print(f"{dataset_name}: {results['passed_tests']}/{results['total_tests']} passed ({results['pass_rate']:.2%})")
        
        return all_results
    
    def analyze_failures(self, eval_results: Dict[str, Any], max_display: int = 5) -> Dict[str, Any]:
        """
        Analyze and summarize failure patterns from evaluation results.
        
        Args:
            eval_results (Dict[str, Any]): Results from run_eval
            max_display (int): Maximum number of failures to display in detail
            
        Returns:
            Dict[str, Any]: Analysis of failures
        """
        failed_tests = [r for r in eval_results['results'] if not r.get('passed', False)]
        
        if not failed_tests:
            return {
                "message": "No failures to analyze!",
                "failure_count": 0
            }
        
        # Categorize failures
        error_failures = []
        code_grader_failures = []
        model_grader_failures = []
        format_grader_failures = []
        both_grader_failures = []
        
        for test in failed_tests:
            if 'error' in test:
                error_failures.append(test)
            else:
                grading = test.get('grading_results', {})
                code_passed = grading.get('code_grader', {}).get('passed', False)
                model_passed = grading.get('model_grader', {}).get('passed', False)
                format_passed = grading.get('format_grader', {}).get('passed', False) if 'format_grader' in grading else True
                
                if not code_passed and not model_passed and not format_passed:
                    both_grader_failures.append(test)
                elif not code_passed and not model_passed:
                    both_grader_failures.append(test)
                elif not code_passed:
                    code_grader_failures.append(test)
                elif not model_passed:
                    model_grader_failures.append(test)
                elif not format_passed:
                    format_grader_failures.append(test)
        
        analysis = {
            "failure_count": len(failed_tests),
            "error_failures": len(error_failures),
            "code_grader_failures": len(code_grader_failures),
            "model_grader_failures": len(model_grader_failures),
            "format_grader_failures": len(format_grader_failures),
            "both_grader_failures": len(both_grader_failures),
            "sample_failures": []
        }
        
        # Include sample failures for inspection
        for i, test in enumerate(failed_tests[:max_display]):
            failure_detail = {
                "prompt": test['test_case'].get('prompt', 'N/A')[:200] + "...",
                "actual_response": test.get('actual_response', 'N/A')[:200] + "..."
            }
            
            if 'error' in test:
                failure_detail['failure_reason'] = f"Error: {test['error']}"
            else:
                grading = test.get('grading_results', {})
                failure_detail['code_grader_feedback'] = grading.get('code_grader', {}).get('feedback', 'N/A')
                failure_detail['model_grader_feedback'] = grading.get('model_grader', {}).get('feedback', 'N/A')
                if 'format_grader' in grading:
                    failure_detail['format_grader_feedback'] = grading.get('format_grader', {}).get('feedback', 'N/A')
            
            analysis['sample_failures'].append(failure_detail)
        
        return analysis

# Create an enhanced evaluator with format grading
class FormatAwareEvaluator(Evaluator):
    """Extended evaluator that handles format-specific grading."""
    
    def run_test_case_with_format(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a test case with format-specific grading criteria."""
        
        # Get format type and grading config
        format_type = test_case.get("format", "text")
        grading_config = test_case.get("grading_config", {})
        
        # Configure graders based on format and config
        grader = self._get_or_create_grader()
        
        # Set code grading criteria if specified
        if "code" in grading_config:
            code_config = grading_config["code"]
            code_criteria = GradingCriteria(
                min_length=code_config.get("min_length"),
                max_length=code_config.get("max_length"),
                required_words=code_config.get("required_words"),
                forbidden_words=code_config.get("forbidden_words"),
                syntax_check=code_config.get("syntax_check", True),
                readability_threshold=code_config.get("readability_threshold", 7.0)
            )
            grader.set_code_criteria(code_criteria)
        
        # Set format grading criteria if specified
        if "format" in grading_config:
            format_config = grading_config["format"]
            format_criteria = FormatGradingCriteria(
                required_format=format_type,
                required_fields=format_config.get("required_fields"),
                forbidden_fields=format_config.get("forbidden_fields"),
                validate_json_schema=format_config.get("validate_json_schema", False),
                json_schema=format_config.get("json_schema"),
                required_sections=format_config.get("required_sections"),
                required_headers=format_config.get("required_headers"),
                require_code_blocks=format_config.get("require_code_blocks", False)
            )
            grader.set_format_criteria(format_criteria)
        
        # Configure model grader with strict, format-aware prompt
        grader.model_grader.set_strict_format_grading(format_type)
    
        # Run the standard test case with all enhancements
        return self.run_test_case(test_case)
    
    def run_format_aware_eval(self, 
                             test_dataset: List[Dict[str, Any]], 
                             save_results: bool = True, 
                             results_path: str = "format_aware_eval_results.json",
                             verbose: bool = True) -> Dict[str, Any]:
        """
        Run format-aware evaluation on a complete test dataset with enhanced display.
        
        Args:
            test_dataset (List[Dict[str, Any]]): List of test cases with 'prompt', 'format', 
                                                'solution_criteria', and 'grading_config'
            save_results (bool): Whether to save results to file
            results_path (str): Path to save evaluation results
            verbose (bool): Whether to print enhanced progress messages
            
        Returns:
            Dict[str, Any]: Complete evaluation results and summary
        """
        if verbose:
            print("🚀 Running Format-Aware Evaluation")
            print("="*50)
        
        results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_dataset, 1):
            if verbose:
                prompt_preview = test_case.get('prompt', '')[:60]
                format_type = test_case.get('format', 'text')
                print(f"\nTest {i}/{len(test_dataset)}: {prompt_preview}...")
                print(f"Format: {format_type}")
            
            try:
                # Run with format-specific grading
                result = self.run_test_case_with_format(test_case)
                results.append(result)
                
                if result["passed"]:
                    passed_count += 1
                    if verbose:
                        print("✅ PASSED")
                else:
                    if verbose:
                        print("❌ FAILED")
                        
                        # Show detailed grading breakdown
                        grading = result.get('grading_results', {})
                        
                        if 'code_grader' in grading:
                            code_grade = grading['code_grader']
                            print(f"  Code Score: {code_grade.score}/10")
                            if not code_grade.passed:
                                print(f"    Issue: {code_grade.feedback[:100]}")
                        
                        if 'format_grader' in grading:
                            format_grade = grading['format_grader']
                            print(f"  Format Score: {format_grade.score}/10")
                            if not format_grade.passed:
                                print(f"    Issue: {format_grade.feedback[:100]}")
                        
                        if 'model_grader' in grading:
                            model_grade = grading['model_grader']
                            print(f"  Model Score: {model_grade.score}/10")
                            if not model_grade.passed:
                                print(f"    Issue: {model_grade.feedback[:100]}")
                
            except Exception as e:
                if verbose:
                    print(f"❌ ERROR: {str(e)}")
                results.append(ErrorHandler.handle_evaluation_error(test_case, e))
        
        # Generate summary
        total_tests = len(test_dataset)
        pass_rate = passed_count / total_tests if total_tests > 0 else 0
        
        summary = {
            "total_tests": total_tests,
            "passed_tests": passed_count,
            "failed_tests": total_tests - passed_count,
            "pass_rate": pass_rate,
            "results": results
        }
        
        # Save results if requested
        if save_results:
            with open(results_path, 'w') as f:
                json.dump(summary, f, indent=4, cls=GradingResultEncoder)
            if verbose:
                print(f"\nResults saved to {results_path}")
        
        if verbose:
            print(f"\n{'='*50}")
            print(f"Format-Aware Evaluation Complete: {passed_count}/{total_tests} tests passed ({pass_rate:.2%})")
            print(f"{'='*50}")
        
        return summary
    
    def calculate_format_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate detailed statistics by format type and grader.
        
        Args:
            results (List[Dict[str, Any]]): List of evaluation results
            
        Returns:
            Dict[str, Any]: Comprehensive statistics breakdown
        """
        stats = {
            "overall": {
                "total": len(results),
                "passed": sum(1 for r in results if r.get('passed', False)),
                "failed": sum(1 for r in results if not r.get('passed', False))
            },
            "by_format": {},
            "by_grader": {
                "code_grader": {"passed": 0, "failed": 0, "total_score": 0, "count": 0},
                "format_grader": {"passed": 0, "failed": 0, "total_score": 0, "count": 0},
                "model_grader": {"passed": 0, "failed": 0, "total_score": 0, "count": 0}
            }
        }
        
        # Analyze by format
        for result in results:
            format_type = result['test_case'].get('format', 'text')
            
            if format_type not in stats['by_format']:
                stats['by_format'][format_type] = {"passed": 0, "failed": 0}
            
            if result.get('passed', False):
                stats['by_format'][format_type]['passed'] += 1
            else:
                stats['by_format'][format_type]['failed'] += 1
            
            # Analyze by grader
            grading = result.get('grading_results', {})
            for grader_name in ['code_grader', 'format_grader', 'model_grader']:
                if grader_name in grading:
                    grader_result = grading[grader_name]
                    stats['by_grader'][grader_name]['count'] += 1
                    stats['by_grader'][grader_name]['total_score'] += grader_result.score
                    if grader_result.passed:
                        stats['by_grader'][grader_name]['passed'] += 1
                    else:
                        stats['by_grader'][grader_name]['failed'] += 1
        
        # Calculate averages
        for grader_name, grader_stats in stats['by_grader'].items():
            if grader_stats['count'] > 0:
                grader_stats['avg_score'] = grader_stats['total_score'] / grader_stats['count']
                grader_stats['pass_rate'] = grader_stats['passed'] / grader_stats['count'] * 100
        
        return stats
    
    def display_detailed_results(self, results: List[Dict[str, Any]], 
                               show_individual_tests: bool = True,
                               max_display: int = 10) -> None:
        """
        Display detailed evaluation results with format-specific feedback.
        
        Args:
            results (List[Dict[str, Any]]): List of evaluation results
            show_individual_tests (bool): Whether to show individual test results
            max_display (int): Maximum number of individual tests to display
        """
        if show_individual_tests:
            print("🚀 Running Format-Aware Evaluation")
            print("="*50)
            
            for i, result in enumerate(results[:max_display], 1):
                test_case = result['test_case']
                prompt_preview = test_case.get('prompt', '')[:60]
                format_type = test_case.get('format', 'text')
                
                print(f"\nTest {i}/{len(results)}: {prompt_preview}...")
                print(f"Format: {format_type}")
                
                if result['passed']:
                    print("✅ PASSED")
                else:
                    print("❌ FAILED")
                    
                    # Show detailed grading breakdown
                    grading = result.get('grading_results', {})
                    
                    if 'code_grader' in grading:
                        code_grade = grading['code_grader']
                        print(f"  Code Score: {code_grade.score}/10")
                        if not code_grade.passed:
                            print(f"    Issue: {code_grade.feedback[:100]}")
                    
                    if 'format_grader' in grading:
                        format_grade = grading['format_grader']
                        print(f"  Format Score: {format_grade.score}/10")
                        if not format_grade.passed:
                            print(f"    Issue: {format_grade.feedback[:100]}")
                    
                    if 'model_grader' in grading:
                        model_grade = grading['model_grader']
                        print(f"  Model Score: {model_grade.score}/10")
                        if not model_grade.passed:
                            print(f"    Issue: {model_grade.feedback[:100]}")
        
        # Generate and display comprehensive statistics
        stats = self.calculate_format_statistics(results)
        
        print("\n" + "="*50)
        print("📊 EVALUATION SUMMARY")
        print("="*50)
        print(f"Overall Pass Rate: {stats['overall']['passed']}/{stats['overall']['total']} "
              f"({stats['overall']['passed']/stats['overall']['total']*100:.1f}%)")

        print("\n📈 Results by Format:")
        for format_type, format_stats in stats['by_format'].items():
            total = format_stats['passed'] + format_stats['failed']
            print(f"  {format_type}: {format_stats['passed']}/{total} passed "
                  f"({format_stats['passed']/total*100:.1f}%)")

        print("\n⚖️ Results by Grader:")
        for grader_name, grader_stats in stats['by_grader'].items():
            if grader_stats['count'] > 0:
                print(f"  {grader_name}:")
                print(f"    Average Score: {grader_stats['avg_score']:.2f}/10")
                print(f"    Pass Rate: {grader_stats['pass_rate']:.1f}%")
                print(f"    Used in: {grader_stats['count']} tests")
    
    def run_format_aware_eval_with_detailed_display(self, 
                                                   test_dataset: List[Dict[str, Any]], 
                                                   save_results: bool = True, 
                                                   results_path: str = "format_aware_eval_results.json",
                                                   verbose: bool = True,
                                                   show_individual_tests: bool = True,
                                                   max_display: int = 10) -> Dict[str, Any]:
        """
        Run format-aware evaluation with enhanced detailed display and statistics.
        
        Args:
            test_dataset (List[Dict[str, Any]]): List of test cases with 'prompt', 'format', 
                                                'solution_criteria', and 'grading_config'
            save_results (bool): Whether to save results to file
            results_path (str): Path to save evaluation results
            verbose (bool): Whether to print enhanced progress messages
            show_individual_tests (bool): Whether to show individual test results
            max_display (int): Maximum number of individual tests to display
            
        Returns:
            Dict[str, Any]: Complete evaluation results and summary
        """
        # Run the standard format-aware evaluation
        summary = self.run_format_aware_eval(
            test_dataset=test_dataset,
            save_results=save_results,
            results_path=results_path,
            verbose=verbose
        )
        
        # Display detailed results with statistics
        if verbose:
            self.display_detailed_results(
                results=summary['results'],
                show_individual_tests=show_individual_tests,
                max_display=max_display
            )
        
        return summary