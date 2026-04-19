"""Vision review — the "always works" fallback for image-based critique.

When Claude Code's ``Read(image.png)`` tool misbehaves (known-flaky in 2026
per PaperVizAgent.md §3.6), the orchestrator can shell out to this helper
via ``scripts/vision_review.py``. It reads the bytes directly and calls
Claude Opus 4.7 with a base64-encoded image block.
"""

from __future__ import annotations

from pathlib import Path

from .client import ClaudeClient, LLMUnavailable, model_for


def _media_type_for(path: Path) -> str:
    ext = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }.get(ext, "image/png")


def vision_review(
    image_path: str | Path,
    prompt: str,
    *,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 1024,
) -> str:
    """Return the model's textual critique of an image.

    Raises :class:`LLMUnavailable` if Anthropic is not configured — the
    caller should then degrade to rubric-only critique.
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(image_path)

    client = ClaudeClient(model=model or model_for("opus"), max_tokens=max_tokens)
    media = _media_type_for(image_path)
    data = image_path.read_bytes()
    sys_prompt = system or (
        "You are a senior journal reviewer evaluating a scientific figure. "
        "Be specific about what fails and where. Return JSON where asked."
    )
    return client.chat(system=sys_prompt, user=prompt, images=[(data, media)],
                       max_tokens=max_tokens)


__all__ = ["vision_review"]
