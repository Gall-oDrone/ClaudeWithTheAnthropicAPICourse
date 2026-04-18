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

# For ``allowed_domains=["scholar.google.com"]`` — finance / econometrics literature reviews.
SCHOLAR_FINANCE_RESEARCH_SYSTEM = (
    "You are a research assistant. When summarizing Scholar results, name papers and authors when shown, "
    "distinguish survey or review articles from primary empirical work, and flag uncertainty if snippets are incomplete."
)


def scholar_latest_financial_models_user(years_recent: str = "2–3") -> str:
    """User message for Google Scholar–scoped search on recent financial modeling research."""
    return f"""
Search Google Scholar for recent work (roughly the last {years_recent} years) on state-of-the-art or emerging financial models
—for example asset pricing, risk measurement, derivatives, credit, or machine learning applied to finance.

Summarize: (1) main themes or model families, (2) a few representative paper titles and authors if they appear in results,
and (3) what directions look most active right now. Keep the answer concise but concrete.
""".strip()


def user_query_focused(topic: str, constraints: str = "") -> str:
    """Build a user message that asks for current web-grounded info on a topic."""
    base = (
        f"Search the web for up-to-date information about: {topic}. "
        "Summarize key points and mention where the information comes from."
    )
    if constraints.strip():
        return f"{base}\n\nAdditional constraints: {constraints}"
    return base
