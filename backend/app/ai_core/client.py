"""Thin, reusable wrapper around the Anthropic Messages API.

This module is intentionally framework-agnostic so the Agent Orchestrator
(Project 2) can import it directly as the shared "AI foundation".
"""
from __future__ import annotations

from anthropic import Anthropic

from app.config import settings


class AICore:
    """Wraps a single-turn or multi-turn completion against the Messages API."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> None:
        self.model = model or settings.anthropic_model
        self.max_tokens = max_tokens or settings.max_tokens
        self._client = Anthropic(api_key=api_key or settings.anthropic_api_key)

    def complete(self, messages: list[dict[str, str]], system: str | None = None) -> str:
        """Send messages and return the concatenated text of the response."""
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        response = self._client.messages.create(**kwargs)

        # The response content is a list of blocks; collect the text blocks.
        return "".join(
            block.text for block in response.content if getattr(block, "type", None) == "text"
        ).strip()


# A module-level singleton is convenient for simple apps.
ai = AICore()
