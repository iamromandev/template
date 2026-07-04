"""Unified lint + format + type-check runner.

Usage:

    uv run python -m scripts.lint           # run all checks
    uv run python -m scripts.lint --fix      # auto-fix where possible
    uv run python -m scripts.lint --check    # only check (no fix)

Exit code is the number of failed steps (0 = all passed).
"""

from __future__ import annotations

import subprocess
import sys
from typing import NoReturn


def _run(cmd: list[str], description: str) -> bool:
    print(f"\n── {description} ──", flush=True)
    result = subprocess.run(cmd, capture_output=False)
    if result.returncode != 0:
        print(f"✗ {description} FAILED (exit={result.returncode})", flush=True)
        return False
    print(f"✓ {description} passed", flush=True)
    return True


def main() -> NoReturn:
    fix = "--fix" in sys.argv

    steps: list[tuple[list[str], str]] = [
        (["uv", "run", "ruff", "format", "." if not fix else "--check"], "Format"),
        (
            ["uv", "run", "ruff", "check", "."] if not fix else ["uv", "run", "ruff", "check", "--fix", "."],
            "Lint",
        ),
        (["uv", "run", "ty", "check", "src/"], "Type check"),
    ]

    failures = [desc for cmd, desc in steps if not _run(cmd, desc)]
    total = len(steps) - len(failures)

    print(f"\n{'=' * 40}")
    print(f"Results: {total}/{len(steps)} passed")
    if failures:
        print(f"Failed: {', '.join(failures)}")
        sys.exit(len(failures))
    sys.exit(0)


if __name__ == "__main__":
    main()
