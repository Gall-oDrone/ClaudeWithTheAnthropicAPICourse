"""
Optional system and user prompt snippets for web-search–grounded answers.

The web search tool is configured in code (``utils.web_search``); prompts here only
steer citation style and domain focus.
"""

# Encourages cited, factual answers when the model uses web search results.
WEB_SEARCH_SYSTEM_GROUNDED = """You are a careful research assistant. When you use web search results:
- Prefer paraphrasing with clear attribution over copying long passages.
- Cite sources when you state specific facts (titles, dates, statistics).
- If evidence is thin or conflicting, say so briefly."""

# Example system prompt when restricting to health / government sources (pair with allowed_domains).
WEB_SEARCH_SYSTEM_HEALTH = """You focus on evidence-based health and medical information.
Prioritize reputable health institutions and government health agencies."""


def user_query_focused(topic: str, constraints: str = "") -> str:
    """Build a user message that asks for current web-grounded info on a topic."""
    base = (
        f"Search the web for up-to-date information about: {topic}. "
        "Summarize key points and mention where the information comes from."
    )
    if constraints.strip():
        return f"{base}\n\nAdditional constraints: {constraints}"
    return base
