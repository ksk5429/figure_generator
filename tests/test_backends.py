"""Backend dispatch + result-object contract tests.

These do NOT spawn subprocess compilers — they verify the pure-Python
pieces: backend name selection, BackendResult shape, graceful failure when
the matching compiler is missing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from figgen.backends import BackendResult, choose_backend


def test_choose_backend_hint_wins():
    assert choose_backend("tikz", Path("a.py")) == "tikz"
    assert choose_backend("mermaid", None) == "mermaid"
    assert choose_backend("drawsvg", Path("a.py")) == "svg"
    assert choose_backend("python", Path("a.tex")) == "matplotlib"


def test_choose_backend_infers_from_extension():
    assert choose_backend(None, Path("fig.tex")) == "tikz"
    assert choose_backend(None, Path("fig.mmd")) == "mermaid"
    assert choose_backend(None, Path("fig.svg")) == "svg"
    assert choose_backend(None, Path("fig.py")) == "matplotlib"


def test_choose_backend_defaults_to_matplotlib():
    assert choose_backend(None, None) == "matplotlib"
    assert choose_backend(None, Path("fig.txt")) == "matplotlib"


def test_backend_result_summary_shape():
    r = BackendResult(backend="tikz", ok=True,
                      outputs=[Path("a.pdf")], tool="tectonic",
                      elapsed_s=1.23)
    s = r.summary()
    assert "tikz" in s and "tectonic" in s and "OK" in s


def test_tikz_backend_graceful_when_no_compiler(tmp_path, monkeypatch):
    """tikz backend must not crash when tectonic/latexmk are absent."""
    from figgen.backends import tikz_backend

    monkeypatch.setattr("shutil.which", lambda name: None)
    tex = tmp_path / "dummy.tex"
    tex.write_text(r"\documentclass{standalone}\begin{document}x\end{document}")
    result = tikz_backend.render(tex, tmp_path, timeout_s=2)
    assert not result.ok
    # stderr contains one of the two "not found" messages
    assert "not found" in result.stderr.lower() or "tectonic" in result.stderr.lower()


def test_mermaid_backend_graceful_when_mmdc_missing(tmp_path, monkeypatch):
    from figgen.backends import mermaid_backend

    monkeypatch.setattr("shutil.which", lambda name: None)
    mmd = tmp_path / "dummy.mmd"
    mmd.write_text("flowchart TD\nA --> B")
    result = mermaid_backend.render(mmd, tmp_path, timeout_s=2)
    assert not result.ok
    assert "mmdc" in result.stderr.lower()
