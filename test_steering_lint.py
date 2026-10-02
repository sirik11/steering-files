"""One runnable check: every rule fires on a file built to trip it, and stays
quiet on a file built to pass.  Run: python3 test_steering_lint.py"""
import tempfile
from pathlib import Path

from steering_lint import MUST_NEVER, lint, main

# Regression cases taken from real public steering files (next.js, VS Code).
ENFORCE = {
    "- Never print or paste secret values (tokens, API keys) in chat responses.": True,
    "- Never commit local secret files; use placeholder-only examples.": True,
    "- never run migrations against production": True,
    "Fork PRs run without repository secrets, so deploy tests never run on them.": False,
    "- Do not stub a global object in tests. Instead, make it injectable for production code.": False,
}
for line, expected in ENFORCE.items():
    assert bool(MUST_NEVER.search(line)) is expected, line

BAD = """# Project
## Project structure
src/
├── api/
└── utils/
## Tech stack
- React
- never run migrations against production
- api_key = sk_live_abcdefghijklmnop1234
""" + "\n".join(f"- filler rule {i}" for i in range(60))

GOOD = """---
inclusion: fileMatch
fileMatchPattern: "api/**"
---
- money is integer cents, never floats
- validate and sanitize every request body
- paginate list endpoints; no unbounded queries
"""


def kinds(text, name="AGENTS.md"):
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / name).parent.mkdir(parents=True, exist_ok=True)
        (root / name).write_text(text)
        findings, _, _ = lint(root / name, root)
        return {k for k, _ in findings}


bad = kinds(BAD)
assert {"derivable", "guardrails", "scope", "enforce", "secret"} <= bad, bad
assert kinds(GOOD, ".kiro/steering/api.md") == set(), kinds(GOOD, ".kiro/steering/api.md")
assert kinds("@AGENTS.md\n", "CLAUDE.md") == {"imports"}   # ruff's CLAUDE.md is one import line

with tempfile.TemporaryDirectory() as d:
    (Path(d) / "AGENTS.md").write_text(BAD)
    assert main(["x", d]) == 1          # a credential fails the run, for CI
    (Path(d) / "AGENTS.md").write_text(GOOD)
    assert main(["x", d]) == 0

print("\nall checks pass")
