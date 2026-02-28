"""
Tests for notebook integrations: parameterized test cases, rubric grading, concurrency, HTML report.
Requires anthropic package; tests are skipped if not installed.
"""

import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

try:
    from utils.evaluator import Evaluator
    from utils.graders import Grader, GradingResult
    from utils.report import generate_evaluation_report
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False


@unittest.skipIf(not _HAS_ANTHROPIC, "anthropic not installed")
class TestEvaluatorResolvePrompt(unittest.TestCase):
    """Test parameterized prompt resolution (prompt_template + prompt_inputs)."""

    def test_resolve_prompt_uses_prompt_when_no_template(self):
        evaluator = Evaluator(chat_client=MagicMock(), grader=MagicMock())
        tc = {"prompt": "Hello world"}
        self.assertEqual(evaluator._resolve_prompt(tc), "Hello world")

    def test_resolve_prompt_uses_template_when_prompt_inputs_present(self):
        evaluator = Evaluator(chat_client=MagicMock(), grader=MagicMock())
        tc = {
            "prompt_template": "Hello {name}, you have {n} items.",
            "prompt_inputs": {"name": "Alice", "n": "3"},
        }
        self.assertEqual(
            evaluator._resolve_prompt(tc),
            "Hello Alice, you have 3 items.",
        )

    def test_resolve_prompt_empty_inputs(self):
        evaluator = Evaluator(chat_client=MagicMock(), grader=MagicMock())
        tc = {"prompt_template": "Just text", "prompt_inputs": {}}
        self.assertEqual(evaluator._resolve_prompt(tc), "Just text")


@unittest.skipIf(not _HAS_ANTHROPIC, "anthropic not installed")
class TestEvaluatorRunEvalOptions(unittest.TestCase):
    """Test run_eval with max_workers, html_report_path, and progress."""

    def test_run_eval_generates_html_when_path_given(self):
        mock_client = MagicMock()
        mock_client.params = {"messages": []}
        mock_client.send_message = MagicMock(return_value="def add(a, b): return a + b")
        mock_client.get_client = MagicMock(return_value=MagicMock())

        grader = Grader(client=mock_client.get_client())
        with patch.object(grader, "grade_comprehensive") as mock_grade:
            mock_grade.return_value = {
                "model_grader": GradingResult(8.0, "Good", {}, True),
                "code_grader": GradingResult(8.0, "OK", {}, True),
            }

            evaluator = Evaluator(chat_client=mock_client, grader=grader)
            dataset = [
                {"prompt": "Write add function", "format": "python", "solution_criteria": "Has def"}
            ]
            with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
                html_path = f.name
            try:
                summary = evaluator.run_eval(
                    dataset,
                    save_results=False,
                    verbose=False,
                    html_report_path=html_path,
                )
                self.assertEqual(summary["total_tests"], 1)
                self.assertTrue(os.path.exists(html_path))
                with open(html_path, encoding="utf-8") as f:
                    content = f.read()
                self.assertIn("Prompt Evaluation Report", content)
            finally:
                os.unlink(html_path)

    def test_run_eval_accepts_max_workers(self):
        mock_client = MagicMock()
        mock_client.params = {"messages": []}
        mock_client.send_message = MagicMock(return_value="def f(): return 1")
        mock_client.get_client = MagicMock(return_value=MagicMock())

        grader = Grader(client=mock_client.get_client())
        with patch.object(grader, "grade_comprehensive") as mock_grade:
            mock_grade.return_value = {
                "model_grader": GradingResult(7.0, "OK", {}, True),
                "code_grader": GradingResult(7.0, "OK", {}, True),
            }

            evaluator = Evaluator(chat_client=mock_client, grader=grader)
            dataset = [
                {"prompt": "Write f", "format": "python"},
                {"prompt": "Write g", "format": "python"},
            ]
            summary = evaluator.run_eval(
                dataset,
                save_results=False,
                verbose=False,
                max_workers=2,
            )
            self.assertEqual(summary["total_tests"], 2)
            self.assertEqual(len(summary["results"]), 2)


@unittest.skipIf(not _HAS_ANTHROPIC, "anthropic not installed")
class TestRubricGradingIntegration(unittest.TestCase):
    """Test that solution_criteria and mandatory_criteria are passed to grader."""

    def test_grade_comprehensive_accepts_rubric_params(self):
        from utils.graders import Grader
        mock_client = MagicMock()
        grader = Grader(client=mock_client)
        with patch.object(grader.model_grader, "grade_with_rubric") as mock_rubric:
            mock_rubric.return_value = GradingResult(8.0, "Good", {}, True)
            result = grader.grade_comprehensive(
                prompt="Write a meal plan",
                response="Breakfast: oats...",
                language="text",
                include_format=False,
                solution_criteria=["Has calories", "Has macros"],
                mandatory_criteria="Must list portions",
            )
            self.assertIn("model_grader", result)
            mock_rubric.assert_called_once()
            call_kw = mock_rubric.call_args[1]
            self.assertEqual(call_kw["solution_criteria"], ["Has calories", "Has macros"])
            self.assertEqual(call_kw["mandatory_criteria"], "Must list portions")


if __name__ == "__main__":
    unittest.main()
