"""
steering_lint: audit the steering files in a repository.

Every check maps to a finding in "Write What the Model Can't Guess":
  derivable    overview content the agent can read from the code
               (repository overviews did not improve task success, arXiv 2602.11988)
  guardrails   no security or performance guidance
               (each appears in under 15% of 2,303 files, arXiv 2511.12884)
  scope        a long file that loads on every task, with no scoping
  enforce      a must-never that belongs in a hook or permission rule
  secret       something that looks like a credential (exits non-zero)
  size         over the vendor-recommended length (Claude 200, Cursor 500)

Heuristics, not proofs. A starting point for review, not a substitute for
measuring your agent with and without the file.

Usage:  python3 steering_lint.py [repo_path]
"""
import re
import sys
from pathlib import Path

PATTERNS = ["AGENTS.md", "CLAUDE.md", "CLAUDE.local.md", "GEMINI.md", ".cursorrules",
            ".claude/rules/**/*.md", ".cursor/rules/**/*.mdc", ".kiro/steering/**/*.md",
            ".github/copilot-instructions.md", ".github/instructions/**/*.instructions.md"]
SKIP = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}

TREE = re.compile(r"[├└│]──|^\s*[│├└]")
OVERVIEW_HEAD = re.compile(r"^#+\s*(project|directory|folder|repo(sitory)?)\s+(structure|layout|overview)"
                           r"|^#+\s*(tech(nology)?\s+stack|architecture|overview|dependencies)\b", re.I)
SECURITY = re.compile(r"secur|secret|credential|auth[nz]?|inject|xss|csrf|sanitiz|escap|permission|\bpii\b", re.I)
PERF = re.compile(r"perform|latenc|n\+1|\bcach|paginat|complexit|\bmemory\b|throughput|\bslow", re.I)
# the dangerous thing must be the object of the prohibition, within a few words of it:
# "never commit secret files" flags; "deploy tests never run on forks" does not
MUST_NEVER = re.compile(r"\b(never|must not|do not|don't)\b[^.;:]{0,50}?"
                        r"(\bprod(uction)?\b|migrat|\bdrop\b|force[- ]push|\bdeploy|secret|"
                        r"credential|password|\bpush\b[^.;]{0,15}\bmain\b)", re.I)
IMPORT = re.compile(r"^@\S+$")                              # Claude Code @path import
SECRETS = [re.compile(p) for p in (
    r"AKIA[0-9A-Z]{16}",                                        # AWS access key id
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-/+]{12,}",
    r"gh[pousr]_[A-Za-z0-9]{36}",                               # GitHub token
)]
SCOPED = re.compile(r"inclusion:\s*(fileMatch|manual|auto)|^paths:|^globs:|alwaysApply:\s*false|"
                    r"^applyTo:\s*['\"]?(?!\*\*['\"]?\s*$)", re.I | re.M)


def find(root):
    seen = set()
    for pat in PATTERNS:
        for p in root.glob("**/" + pat if "/" not in pat else pat):
            if p.is_file() and not SKIP & set(p.relative_to(root).parts):
                seen.add(p)
    return sorted(seen)


def frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return m.group(1) if m else ""


def is_scoped(path, root, text):
    if SCOPED.search(frontmatter(text)):
        return True
    rel = path.relative_to(root)
    return rel.name == "AGENTS.md" and len(rel.parts) > 1  # nested: directory-scoped


def lint(path, root):
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    out = []
    body = [l.strip() for l in lines if l.strip()]
    if body and all(IMPORT.match(l) for l in body):
        return [("imports", f"only imports {', '.join(l[1:] for l in body)}; checked there")], \
            len(text) // 4, is_scoped(path, root, text)

    derivable = [i + 1 for i, l in enumerate(lines) if TREE.search(l) or OVERVIEW_HEAD.search(l)]
    if derivable:
        out.append(("derivable", f"overview content on lines {', '.join(map(str, derivable[:6]))}"
                    f"{' …' if len(derivable) > 6 else ''}: the agent can read this from the code"))
    if not SECURITY.search(text):
        out.append(("guardrails", "no security guidance (found in only 14.8% of files studied)"))
    if not PERF.search(text):
        out.append(("guardrails", "no performance guidance (found in only 14.5% of files studied)"))
    if not is_scoped(path, root, text) and len(lines) > 60:
        out.append(("scope", f"{len(lines)} lines load on every task; scope rules that apply to part of the codebase"))
    for i, l in enumerate(lines):
        if MUST_NEVER.search(l):
            out.append(("enforce", f"line {i + 1}: a must-never; a hook or permission rule enforces it, steering only suggests it"))
    for i, l in enumerate(lines):
        if any(s.search(l) for s in SECRETS):
            out.append(("secret", f"line {i + 1}: looks like a credential; remove it and rotate it"))
    limit = 500 if path.suffix == ".mdc" else 200
    if len(lines) > limit:
        out.append(("size", f"{len(lines)} lines, over the {limit}-line vendor guidance"))
    return out, len(text) // 4, is_scoped(path, root, text)


def main(argv):
    root = Path(argv[1] if len(argv) > 1 else ".").resolve()
    files = find(root)
    if not files:
        print(f"No steering files found under {root}")
        return 0
    always_tokens, secrets = 0, 0
    for f in files:
        findings, tokens, scoped = lint(f, root)
        if not scoped:
            always_tokens += tokens
        print(f"\n{f.relative_to(root)}  (~{tokens:,} tokens, {'scoped' if scoped else 'loads every task'})")
        for kind, msg in findings or [("ok", "nothing flagged")]:
            print(f"  {kind:<10} {msg}")
        secrets += sum(k == "secret" for k, _ in findings)
    print(f"\n~{always_tokens:,} tokens of steering load on every task (chars / 4 estimate).")
    print("Measure it: run a common task with and without these files and compare outcome and cost.")
    return 1 if secrets else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
