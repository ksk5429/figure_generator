"""LLM plumbing: Anthropic Claude client wrapper + vision helper.

Both modules degrade gracefully when ``anthropic`` is not installed or
``ANTHROPIC_API_KEY`` is unset — the agents fall back to a rubric-only
mode so the pipeline still runs offline.
"""

from __future__ import annotations

from .client import ClaudeClient, LLMUnavailable
from .vision import vision_review

__all__ = ["ClaudeClient", "LLMUnavailable", "vision_review"]
