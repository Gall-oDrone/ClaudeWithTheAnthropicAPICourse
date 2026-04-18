#!/usr/bin/env python3
"""Minimal script demonstrating the built-in web search tool via ``WebSearchClient``."""

import os

from dotenv import load_dotenv

from utils.web_search import WebSearchClient, WebSearchToolConfig, text_from_message


def main() -> None:
    load_dotenv()
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Set ANTHROPIC_API_KEY in the environment or a .env file.")
        return

    # Match course notebook: restrict search domains (optional).
    tool_cfg = WebSearchToolConfig(
        max_uses=5,
        allowed_domains=["nih.gov"],
    )
    client = WebSearchClient(
        api_key=api_key,
        model=os.getenv("ANTHROPIC_WEB_SEARCH_MODEL", "claude-sonnet-4-5"),
        default_tool_config=tool_cfg,
    )

    response = client.ask("What are evidence-based tips for leg strength training?")
    print(text_from_message(response))


if __name__ == "__main__":
    main()
