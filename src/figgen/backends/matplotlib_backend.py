"""Matplotlib backend: executes a plot script in a subprocess with a timeout.

The script is expected to be self-contained (imports ``figgen``, loads data,
draws, and calls ``figgen.utils.save_figure``). The backend does not inspect
the script's output; it trusts the usual figure-directory convention
(``figures/<id>/<id>.{png,svg,pdf}``).

Separated from the direct ``python figures/<id>/<id>.py`` invocation used by
the Makefile so the orchestrator can capture stderr and apply retries
without shelling out through ``make``.
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from .. import REPO_ROOT
from . import BackendResult


def render(
    source: Path,
    out_dir: Path,
    *,
    timeout_s: float = 90.0,
    python: str | None = None,
    env_overrides: dict[str, str] | None = None,
) -> BackendResult:
    """Run ``python <source>`` in a subprocess. Returns BackendResult."""
    py = python or sys.executable
    source = Path(source).resolve()
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.setdefault("MPLBACKEND", "Agg")
    if env_overrides:
        env.update(env_overrides)

    # Match the Makefile's `python figures/<id>/<id>.py` invocation — which
    # runs from REPO_ROOT so relative `data/raw/...` paths in config.yaml
    # resolve correctly. Falling back to source.parent for scripts outside
    # the main figures/ tree.
    try:
        cwd = str(REPO_ROOT) if str(source).startswith(str(REPO_ROOT)) else str(source.parent)
    except Exception:  # noqa: BLE001
        cwd = str(source.parent)

    start = time.time()
    try:
        proc = subprocess.run(
            [py, str(source)],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return BackendResult(
            backend="matplotlib",
            ok=False,
            stderr=f"timeout after {timeout_s}s: {exc}",
            elapsed_s=time.time() - start,
            tool="python",
        )

    elapsed = time.time() - start
    stem = source.stem
    outputs = [
        out_dir / f"{stem}.{ext}"
        for ext in ("png", "svg", "pdf")
        if (out_dir / f"{stem}.{ext}").exists()
    ]
    return BackendResult(
        backend="matplotlib",
        ok=proc.returncode == 0 and bool(outputs),
        outputs=outputs,
        stderr=proc.stderr or "",
        stdout=proc.stdout or "",
        elapsed_s=elapsed,
        tool="python",
    )


__all__ = ["render"]
