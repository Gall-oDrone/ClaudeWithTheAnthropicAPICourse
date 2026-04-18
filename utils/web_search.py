"""
Anthropic built-in web search tool (server-side).

The API runs searches and injects results for Claude; you pass the tool definition
in ``tools=[...]`` on ``messages.create``. See:
https://docs.anthropic.com/en/docs/build-with-claude/tool-use/web-search-tool
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, MutableSequence, Optional, Sequence, Union

# Tool type strings supported by this module (course / reference uses 20250305).
TOOL_TYPE_WEB_SEARCH_20250305 = "web_search_20250305"
TOOL_TYPE_WEB_SEARCH_20260209 = "web_search_20260209"
DEFAULT_WEB_SEARCH_TOOL_NAME = "web_search"
DEFAULT_WEB_SEARCH_MODEL = "claude-sonnet-4-5"


@dataclass(frozen=True)
class UserLocation:
    """Optional hint for geographically relevant search results."""

    type: str = "approximate"
    city: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    timezone: Optional[str] = None

    def to_api_dict(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {"type": self.type}
        if self.city is not None:
            d["city"] = self.city
        if self.country is not None:
            d["country"] = self.country
        if self.region is not None:
            d["region"] = self.region
        if self.timezone is not None:
            d["timezone"] = self.timezone
        return d


@dataclass
class WebSearchToolConfig:
    """
    Configuration for the built-in ``web_search`` tool.

    ``allowed_domains`` and ``blocked_domains`` are mutually exclusive (Anthropic API).
    """

    name: str = DEFAULT_WEB_SEARCH_TOOL_NAME
    tool_type: str = TOOL_TYPE_WEB_SEARCH_20250305
    max_uses: Optional[int] = None
    allowed_domains: Optional[List[str]] = None
    blocked_domains: Optional[List[str]] = None
    user_location: Optional[UserLocation] = None
    cache_control: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
        if self.allowed_domains and self.blocked_domains:
            raise ValueError(
                "allowed_domains and blocked_domains cannot both be set; "
                "use one or the other per Anthropic API rules."
            )

    def to_tool_dict(self) -> Dict[str, Any]:
        """Serialize to the dict shape expected by ``messages.create(..., tools=[...])``."""
        tool: Dict[str, Any] = {
            "type": self.tool_type,
            "name": self.name,
        }
        if self.max_uses is not None:
            tool["max_uses"] = self.max_uses
        if self.allowed_domains:
            tool["allowed_domains"] = list(self.allowed_domains)
        if self.blocked_domains:
            tool["blocked_domains"] = list(self.blocked_domains)
        if self.user_location is not None:
            tool["user_location"] = self.user_location.to_api_dict()
        if self.cache_control is not None:
            tool["cache_control"] = self.cache_control
        return tool


def build_web_search_tool(config: Optional[WebSearchToolConfig] = None) -> Dict[str, Any]:
    """Return a single tool definition dict for the Messages API."""
    cfg = config or WebSearchToolConfig()
    return cfg.to_tool_dict()


def append_message(
    messages: MutableSequence[Dict[str, Any]],
    role: str,
    content: Union[str, List[Dict[str, Any]], Any],
) -> None:
    """
    Append a message. If ``content`` is an Anthropic ``Message``, its ``role`` and
    ``content`` blocks are used (for passing API responses back into history).
    """
    if hasattr(content, "content") and hasattr(content, "role"):
        messages.append({"role": content.role, "content": content.content})
        return
    if isinstance(content, (list, tuple)):
        messages.append({"role": role, "content": list(content)})
    else:
        messages.append({"role": role, "content": content})


def text_from_message(message: Any) -> str:
    """Concatenate all text blocks from a Messages API response."""
    blocks = getattr(message, "content", message)
    if not isinstance(blocks, (list, tuple)):
        return ""
    lines: List[str] = []
    for block in blocks:
        btype = getattr(block, "type", None)
        if btype is None and isinstance(block, dict):
            btype = block.get("type")
        if btype == "text":
            text = getattr(block, "text", None)
            if text is None and isinstance(block, dict):
                text = block.get("text")
            if text:
                lines.append(text)
    return "\n".join(lines)


@dataclass
class WebSearchClient:
    """
    Thin wrapper around ``Anthropic.messages.create`` with the web search tool.

    The server executes searches inside a single request when needed; you typically
    receive one assistant ``Message`` with optional citations in text blocks.
    """

    model: str = DEFAULT_WEB_SEARCH_MODEL
    api_key: Optional[str] = None
    default_tool_config: WebSearchToolConfig = field(default_factory=WebSearchToolConfig)
    _client: Any = field(init=False, repr=False)

    def __post_init__(self) -> None:
        try:
            from anthropic import Anthropic as _Anthropic
        except ImportError as e:  # pragma: no cover - env without package
            raise ImportError(
                "The 'anthropic' package is required for WebSearchClient."
            ) from e
        self._client = _Anthropic(api_key=self.api_key)

    def create(
        self,
        messages: Sequence[Mapping[str, Any]],
        *,
        system: Optional[str] = None,
        tool_config: Optional[WebSearchToolConfig] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        stop_sequences: Optional[List[str]] = None,
        extra_params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Call the Messages API with the web search tool enabled.

        Parameters
        ----------
        messages:
            Conversation history (each item has ``role`` and ``content``).
        system:
            Optional system prompt.
        tool_config:
            Overrides :attr:`default_tool_config` for this call.
        extra_params:
            Additional keyword arguments forwarded to ``messages.create``.
        """
        tools = [build_web_search_tool(tool_config or self.default_tool_config)]
        params: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "messages": [dict(m) for m in messages],
            "temperature": temperature,
            "tools": tools,
        }
        if system:
            params["system"] = system
        if stop_sequences:
            params["stop_sequences"] = stop_sequences
        if extra_params:
            params.update(extra_params)
        return self._client.messages.create(**params)

    def ask(
        self,
        user_text: str,
        *,
        system: Optional[str] = None,
        tool_config: Optional[WebSearchToolConfig] = None,
        max_tokens: int = 4096,
        temperature: float = 1.0,
        messages: Optional[MutableSequence[Dict[str, Any]]] = None,
    ) -> Any:
        """
        Single-turn helper: one user message, optional history appends.

        If ``messages`` is provided, the user text is appended and that list is sent.
        """
        hist: List[Dict[str, Any]] = list(messages) if messages is not None else []
        hist.append({"role": "user", "content": user_text})
        return self.create(
            hist,
            system=system,
            tool_config=tool_config,
            max_tokens=max_tokens,
            temperature=temperature,
        )
