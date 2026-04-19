"""Belt-and-braces vision review for the figure critic.

Used when Claude Code's ``Read(image.png)`` is unreliable. Takes a path to
an image and a prompt file, prints the model's response to stdout.

Usage:
    python scripts/vision_review.py figures/<id>/<id>.png prompts/critic_vision.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(description="Vision review fallback for figure critic.")
    ap.add_argument("image", type=Path, help="Path to the image file (PNG).")
    ap.add_argument("prompt", type=Path, help="Path to the prompt file (text).")
    ap.add_argument("--model", default=None, help="Override model id (default claude-opus-4-7).")
    ap.add_argument("--max-tokens", type=int, default=1024)
    args = ap.parse_args()

    if not args.image.exists():
        print(f"ERR: image not found: {args.image}", file=sys.stderr)
        return 2
    if not args.prompt.exists():
        print(f"ERR: prompt not found: {args.prompt}", file=sys.stderr)
        return 2

    from figgen.llm import LLMUnavailable, vision_review

    try:
        out = vision_review(
            args.image,
            args.prompt.read_text(encoding="utf-8"),
            model=args.model,
            max_tokens=args.max_tokens,
        )
    except LLMUnavailable as exc:
        print(f"LLM unavailable: {exc}. Set ANTHROPIC_API_KEY to enable.",
              file=sys.stderr)
        return 3
    except Exception as exc:  # noqa: BLE001
        print(f"ERR: vision review failed: {exc}", file=sys.stderr)
        return 4
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
