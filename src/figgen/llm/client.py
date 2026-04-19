"""Thin wrapper around ``anthropic.Anthropic`` that never crashes the pipeline.

Two design goals:

1. The pipeline must still build a figure when no API key is set or the
   ``anthropic`` package is missing. Callers handle :class:`LLMUnavailable`.
2. Model IDs live in one place, routed by role (``opus`` for orchestrator,
   ``sonnet`` for workers) so upgrading to Opus 4.8 / Sonnet 4.7 is a
   single-line edit.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any


class LLMUnavailable(RuntimeError):
    """Raised when the Anthropic client cannot be constructed."""


# Model IDs as of 2026-04 (see env-section of Claude Code).
# Override with env var ``FIGGEN_CLAUDE_<ROLE>`` if you need to pin.
_DEFAULT_MODELS: dict[str, str] = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
    "haiku": "claude-haiku-4-5-20251001",
}


def model_for(role: str = "opus") -> str:
    """Return the model id to use for a role."""
    env_key = f"FIGGEN_CLAUDE_{role.upper()}"
    return os.environ.get(env_key) or _DEFAULT_MODELS.get(role, _DEFAULT_MODELS["sonnet"])


@dataclass
class ClaudeClient:
    """Anthropic Messages API wrapper with a sane default timeout."""

    api_key: str | None = None
    model: str = ""
    max_tokens: int = 4096
    timeout_s: float = 120.0

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = self.model or model_for("opus")
        if not self.api_key:
            raise LLMUnavailable("ANTHROPIC_API_KEY not set; run offline mode instead.")
        try:
            import anthropic  # noqa: WPS433
        except ImportError as exc:  # pragma: no cover
            raise LLMUnavailable(
                "`anthropic` package not installed. pip install anthropic"
            ) from exc
        self._anthropic = anthropic
        self._client = anthropic.Anthropic(api_key=self.api_key, timeout=self.timeout_s)

    def chat(
        self,
        system: str,
        user: str,
        *,
        images: list[tuple[bytes, str]] | None = None,
        max_tokens: int | None = None,
        temperature: float = 0.2,
    ) -> str:
        """Send a single-turn message. ``images`` is ``[(bytes, media_type)]``."""
        import base64

        content: list[dict[str, Any]] = []
        for data, media_type in images or []:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": media_type,
                    "data": base64.standard_b64encode(data).decode(),
                },
            })
        content.append({"type": "text", "text": user})

        msg = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens or self.max_tokens,
            temperature=temperature,
            system=system,
            messages=[{"role": "user", "content": content}],
        )
        # Text-only response for now; tool use is not needed in the figure loop.
        parts = [b.text for b in msg.content if getattr(b, "type", "") == "text"]
        return "\n".join(parts).strip()


__all__ = ["ClaudeClient", "LLMUnavailable", "model_for"]
