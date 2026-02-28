"""
Tests for utils.report HTML evaluation report generator.
"""

import os
import tempfile
import unittest
from types import SimpleNamespace

from utils.report import generate_evaluation_report


def _make_grader_result(score: float, feedback: str, passed: bool):
    """Minimal GradingResult-like object (avoids importing graders/anthropic)."""
    return SimpleNamespace(score=score, feedback=feedback, passed=passed)


def _make_result(score: float, feedback: str, test_case: dict, actual_response: str):
    """Build a single result dict like evaluator.run_test_case returns."""
    gr = _make_grader_result(score, feedback, score >= 7.0)
    return {
        "test_case": test_case,
        "actual_response": actual_response,
        "grading_results": {"model_grader": gr},
        "passed": gr.passed,
    }


class TestGenerateEvaluationReport(unittest.TestCase):
    def test_generate_report_empty_results(self):
        summary = {"total_tests": 0, "passed_tests": 0, "pass_rate": 0.0, "results": []}
        html = generate_evaluation_report(summary)
        self.assertIn("Prompt Evaluation Report", html)
        self.assertIn("Total Test Cases", html)
        self.assertIn("0", html)

    def test_generate_report_with_results(self):
        results = [
            _make_result(
                8.0,
                "Good response",
                {"prompt": "Say hello", "solution_criteria": "Must say hello"},
                "Hello!",
            ),
            _make_result(
                4.0,
                "Incomplete",
                {"prompt": "Write a function", "solution_criteria": "Must have def"},
                "def f(): pass",
            ),
        ]
        summary = {
            "total_tests": 2,
            "passed_tests": 1,
            "pass_rate": 0.5,
            "results": results,
        }
        html = generate_evaluation_report(summary)
        self.assertIn("2", html)
        self.assertIn("6.0", html)  # average (8+4)/2
        self.assertIn("Say hello", html)
        self.assertIn("Good response", html)
        self.assertIn("score-high", html)
        self.assertIn("score-low", html)

    def test_generate_report_parameterized_test_case(self):
        results = [
            _make_result(
                9.0,
                "Meets criteria",
                {
                    "scenario": "Athlete meal plan",
                    "prompt_inputs": {"height": "170", "weight": "70"},
                    "solution_criteria": ["Has calories", "Has macros"],
                },
                "Breakfast: oats...",
            ),
        ]
        summary = {"total_tests": 1, "passed_tests": 1, "pass_rate": 1.0, "results": results}
        html = generate_evaluation_report(summary)
        self.assertIn("Athlete meal plan", html)
        self.assertIn("height", html)
        self.assertIn("170", html)
        self.assertIn("Has calories", html)

    def test_generate_report_writes_file(self):
        summary = {"total_tests": 0, "passed_tests": 0, "pass_rate": 0.0, "results": []}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            path = f.name
        try:
            generate_evaluation_report(summary, output_path=path, title="Custom Title")
            with open(path, encoding="utf-8") as f:
                content = f.read()
            self.assertIn("Custom Title", content)
        finally:
            os.unlink(path)

    def test_generate_report_custom_pass_threshold(self):
        summary = {"total_tests": 0, "passed_tests": 0, "pass_rate": 0.0, "results": []}
        html = generate_evaluation_report(summary, pass_threshold=8.0)
        self.assertIn("≥8", html)


if __name__ == "__main__":
    unittest.main()
