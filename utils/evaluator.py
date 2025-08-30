import json
from typing import Optional, List, Dict, Any

from utils.graders import Grader, GradingResult


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
    
    def run_test_case(self, test_case: Dict[str, str]) -> Dict[str, Any]:
        """
        Run a single test case evaluation.
        
        Args:
            test_case (Dict[str, str]): Dictionary containing 'prompt' and optionally 'expected_response' keys
            
        Returns:
            Dict[str, Any]: Test case results including response and grading
        """
        grader = self._get_or_create_grader()
        
        prompt = test_case.get("prompt", "")
        expected_response = test_case.get("expected_response", "")
        
        # Generate response using the chat client
        # Store original messages to restore later
        original_messages = self.chat_client.params.get("messages", []).copy()
        
        # Set up new conversation for this test case
        self.chat_client.params["messages"] = [{"role": "user", "content": prompt}]
        actual_response = self.chat_client.send_message()
        
        # Restore original messages
        self.chat_client.params["messages"] = original_messages
        
        # Grade the response
        grading_result = grader.grade_comprehensive(prompt, actual_response)
        
        # Determine if test passed
        passed = (
            grading_result["model_grader"].passed and 
            grading_result["code_grader"].passed
        )
        
        return {
            "test_case": test_case,
            "actual_response": actual_response,
            "expected_response": expected_response,
            "grading_results": grading_result,
            "passed": passed
        }
    
    def run_eval(self, 
                 test_dataset: List[Dict[str, str]], 
                 save_results: bool = True, 
                 results_path: str = "eval_results.json",
                 verbose: bool = True) -> Dict[str, Any]:
        """
        Run evaluation on a complete test dataset.
        
        Args:
            test_dataset (List[Dict[str, str]]): List of test cases with 'prompt' and optionally 'expected_response'
            save_results (bool): Whether to save results to file
            results_path (str): Path to save evaluation results
            verbose (bool): Whether to print progress messages
            
        Returns:
            Dict[str, Any]: Complete evaluation results and summary
        """
        results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_dataset):
            if verbose:
                print(f"Running test case {i+1}/{len(test_dataset)}...")
            
            try:
                test_result = self.run_test_case(test_case)
                results.append(test_result)
                
                if test_result["passed"]:
                    passed_count += 1
                    if verbose:
                        print(f"  ✓ Test case {i+1} passed")
                else:
                    if verbose:
                        print(f"  ✗ Test case {i+1} failed")
                    
            except Exception as e:
                if verbose:
                    print(f"  ✗ Error in test case {i+1}: {str(e)}")
                results.append({
                    "test_case": test_case,
                    "error": str(e),
                    "passed": False
                })
        
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
        both_grader_failures = []
        
        for test in failed_tests:
            if 'error' in test:
                error_failures.append(test)
            else:
                grading = test.get('grading_results', {})
                code_passed = grading.get('code_grader', {}).get('passed', False)
                model_passed = grading.get('model_grader', {}).get('passed', False)
                
                if not code_passed and not model_passed:
                    both_grader_failures.append(test)
                elif not code_passed:
                    code_grader_failures.append(test)
                elif not model_passed:
                    model_grader_failures.append(test)
        
        analysis = {
            "failure_count": len(failed_tests),
            "error_failures": len(error_failures),
            "code_grader_failures": len(code_grader_failures),
            "model_grader_failures": len(model_grader_failures),
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
            
            analysis['sample_failures'].append(failure_detail)
        
        return analysis