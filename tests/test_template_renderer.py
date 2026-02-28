"""
Standalone tests for TemplateRenderer (no dependency on graders/anthropic).
"""

import unittest
from utils.shared_utils import TemplateRenderer


class TestTemplateRenderer(unittest.TestCase):
    def test_render_simple_placeholders(self):
        template = "Hello {name}, you have {count} items."
        result = TemplateRenderer.render(template, {"name": "Alice", "count": 3})
        self.assertEqual(result, "Hello Alice, you have 3 items.")

    def test_render_literal_braces(self):
        template = "JSON looks like {{ \"key\": \"value\" }}."
        result = TemplateRenderer.render(template, {})
        self.assertEqual(result, "JSON looks like { \"key\": \"value\" }.")

    def test_render_missing_placeholder_left_unchanged(self):
        template = "Hello {name}, {missing}."
        result = TemplateRenderer.render(template, {"name": "Bob"})
        self.assertEqual(result, "Hello Bob, {missing}.")

    def test_render_empty_variables(self):
        template = "No placeholders here."
        result = TemplateRenderer.render(template, {})
        self.assertEqual(result, "No placeholders here.")

    def test_render_values_coerced_to_str(self):
        template = "Count: {n}"
        result = TemplateRenderer.render(template, {"n": 42})
        self.assertEqual(result, "Count: 42")


if __name__ == "__main__":
    unittest.main()
