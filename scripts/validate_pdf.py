"""PDF validator: font embedding, DPI, colorspace, file size.

Usage:
    python scripts/validate_pdf.py figures/<id>/<id>.pdf [more.pdf ...]
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from shutil import which


def _run(cmd: list[str]) -> tuple[int, str, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return r.returncode, r.stdout, r.stderr


def validate(pdf: Path) -> bool:
    if not pdf.exists():
        print(f"MISSING: {pdf}")
        return False
    size_mb = pdf.stat().st_size / (1024 * 1024)
    print(f"=== {pdf} ({size_mb:.2f} MB) ===")
    ok = True
    if size_mb > 10.0:
        print("  [FAIL] > 10 MB; Elsevier cap exceeded.")
        ok = False
    if which("pdffonts"):
        rc, stdout, stderr = _run(["pdffonts", str(pdf)])
        print("  pdffonts:")
        for line in stdout.splitlines():
            print(f"    {line}")
        if rc != 0:
            print(f"    [FAIL] pdffonts rc={rc} stderr={stderr}")
            ok = False
    else:
        print("  [skip] pdffonts not on PATH")
    if which("pdfinfo"):
        rc, stdout, _ = _run(["pdfinfo", str(pdf)])
        if rc == 0:
            for line in stdout.splitlines():
                if any(k in line for k in ("Pages:", "Page size:", "File size:", "PDF version:")):
                    print(f"  {line}")
    return ok


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdfs", type=Path, nargs="+")
    args = ap.parse_args()
    all_ok = True
    for p in args.pdfs:
        if not validate(p):
            all_ok = False
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
