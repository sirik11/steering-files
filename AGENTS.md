# AGENTS.md

Conventions an agent can't infer from reading this repository.

- `steering_lint.py` stays standard-library only. Adding a dependency defeats the "drop one file into any repo" promise.
- Every check maps to a finding in the article, and the module docstring names its source.
- A heuristic change ships with a regression case in `test_steering_lint.py`, taken from a real public steering file where possible.
- Figures are generated. Edit `figures/make_figures.mjs`, run `node make_figures.mjs`, and commit both the SVG and the PNG. Chrome renders them because rsvg-convert on macOS ignores the bundled fonts.
- Quotes in the article match their source word for word. Anything paraphrased goes without quotation marks.
- Security: test fixtures use deliberately fake, non-functional credentials, and CI runs the linter's secret check on every push to enforce it.
- Performance: the linter makes one pass over each file. Keep patterns line-local so they can't backtrack across a large file.
