# Steering files: write what the model can't guess

Companion code for the article **[Write What the Model Can't Guess](article/write-what-the-model-cant-guess.md)**.

Every coding agent now reads a steering file before it touches your code: Kiro's `.kiro/steering/`, Claude Code's `CLAUDE.md`, Cursor's `.cursor/rules/`, Copilot's `.github/copilot-instructions.md`, and the cross-tool `AGENTS.md`. Research published over the past year suggests most of what we put in them doesn't help:

- Context files "do not generally improve task success rates, while increasing inference cost by over 20% on average," and repository overviews in particular "are not helpful" ([Gloaguen et al., 2026](https://arxiv.org/abs/2602.11988))
- Across 2,303 files, security guidance appears in 14.8% and performance in 14.5% ([Chatlatanagulchai et al., 2025](https://arxiv.org/abs/2511.12884))
- File size, instruction position, file architecture, and contradictions produced no detectable difference in compliance across 1,650 sessions ([McMillan, 2026](https://arxiv.org/abs/2605.10039))

The useful part is narrow: conventions the model can't infer from the code.

## Repository layout

| Path | What it is |
| --- | --- |
| [`article/write-what-the-model-cant-guess.md`](article/write-what-the-model-cant-guess.md) | The full article |
| [`steering_lint.py`](steering_lint.py) | Dependency-free linter for the steering files in a repository |
| [`test_steering_lint.py`](test_steering_lint.py) | Self-check, including regression cases from real public steering files |
| [`figures/`](figures/) | The cover and four diagrams: PNG to publish, SVG to edit, and the script that generates them |

## `steering_lint.py`

Python 3, standard library only.

```bash
python3 steering_lint.py path/to/your/repo
```

It finds `AGENTS.md`, `CLAUDE.md`, `CLAUDE.local.md`, `GEMINI.md`, `.claude/rules/`, `.cursor/rules/`, `.cursorrules`, `.kiro/steering/`, `.github/copilot-instructions.md`, and `.github/instructions/`, then reports per file:

| Check | What it flags | Why |
| --- | --- | --- |
| `derivable` | Directory trees and overview sections (structure, tech stack, architecture) | The agent can read these from the code; overviews didn't improve task success |
| `guardrails` | No security or performance guidance at all | Each appears in under 15% of files studied |
| `scope` | A long file that loads on every task | Kiro `fileMatch`, Claude `paths`, Cursor `globs`, and Copilot `applyTo` all exist for this |
| `enforce` | "Never" rules about production, secrets, migrations, or deploys | Steering is weighed, not enforced; a hook or permission rule holds regardless |
| `secret` | Strings that look like credentials | Exits non-zero, so it can gate CI |
| `size` | Over 200 lines (500 for Cursor `.mdc`) | Vendor guidance; every line costs context on every task |

It ends with an estimate of how many tokens of steering load on every task (characters / 4).

These are heuristics, not proofs. The real test is the one the ETH authors recommend: run a common task with and without your steering file, and compare both the outcome and the cost.

```bash
python3 test_steering_lint.py
```

## Figures

```bash
cd figures && python3 make_figures.py
for f in fig1-same-four-dials fig2-what-we-write fig3-four-questions fig4-suggestion-vs-guarantee cover-write-what-the-model-cant-guess; do
  rsvg-convert -w 1600 -h 900 $f.svg -o $f.png
done
rsvg-convert -w 1200 -h 630 cover-social-1200x630.svg -o cover-social-1200x630.png
```

The diagrams are original. Reuse them with attribution.

## License

[MIT](LICENSE).
