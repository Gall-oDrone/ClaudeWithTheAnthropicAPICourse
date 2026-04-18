"""Unit tests for utils.web_search (tool definition and client wiring)."""

import unittest
from unittest.mock import MagicMock, patch


from utils.web_search import (
    TOOL_TYPE_WEB_SEARCH_20250305,
    UserLocation,
    WebSearchToolConfig,
    append_message,
    build_web_search_tool,
    text_from_message,
)


class TestWebSearchToolConfig(unittest.TestCase):
    def test_build_default_tool_dict(self):
        d = build_web_search_tool()
        self.assertEqual(d["type"], TOOL_TYPE_WEB_SEARCH_20250305)
        self.assertEqual(d["name"], "web_search")

    def test_allowed_domains_serialized(self):
        cfg = WebSearchToolConfig(allowed_domains=["nih.gov"], max_uses=5)
        d = cfg.to_tool_dict()
        self.assertEqual(d["allowed_domains"], ["nih.gov"])
        self.assertEqual(d["max_uses"], 5)

    def test_mutually_exclusive_domains_raises(self):
        with self.assertRaises(ValueError):
            WebSearchToolConfig(allowed_domains=["a.com"], blocked_domains=["b.com"])

    def test_user_location(self):
        loc = UserLocation(city="Austin", country="US", timezone="America/Chicago")
        cfg = WebSearchToolConfig(user_location=loc)
        self.assertIn("user_location", cfg.to_tool_dict())
        self.assertEqual(cfg.to_tool_dict()["user_location"]["city"], "Austin")


class TestMessageHelpers(unittest.TestCase):
    def test_text_from_message_with_objects(self):
        block = MagicMock()
        block.type = "text"
        block.text = "Hello"
        msg = MagicMock()
        msg.content = [block]
        self.assertEqual(text_from_message(msg), "Hello")

    def test_text_from_message_dict_blocks(self):
        msg = MagicMock()
        msg.content = [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}]
        self.assertEqual(text_from_message(msg), "A\nB")

    def test_append_message_plain_string(self):
        m: list = []
        append_message(m, "user", "hi")
        self.assertEqual(m, [{"role": "user", "content": "hi"}])

    def test_append_message_from_api_message_object(self):
        inner = MagicMock()
        inner.role = "assistant"
        inner.content = [{"type": "text", "text": "x"}]
        m: list = []
        append_message(m, "user", inner)
        self.assertEqual(m[0]["role"], "assistant")


class TestWebSearchClient(unittest.TestCase):
    @patch("anthropic.Anthropic")
    def test_create_passes_tools(self, mock_anthropic):
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        from utils.web_search import WebSearchClient

        client = WebSearchClient(api_key="test", model="claude-sonnet-4-5")
        client.create([{"role": "user", "content": "test"}], max_tokens=1000)

        mock_client.messages.create.assert_called_once()
        call_kw = mock_client.messages.create.call_args[1]
        self.assertEqual(call_kw["model"], "claude-sonnet-4-5")
        self.assertEqual(call_kw["max_tokens"], 1000)
        self.assertEqual(len(call_kw["tools"]), 1)
        self.assertEqual(call_kw["tools"][0]["type"], TOOL_TYPE_WEB_SEARCH_20250305)


if __name__ == "__main__":
    unittest.main()
