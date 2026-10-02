"""Generate every figure for "Write What the Model Can't Guess" as SVG.

Render to PNG with:  rsvg-convert -w 1600 -h 900 <file>.svg -o <file>.png
The social card is 1200x630: rsvg-convert -w 1200 -h 630.
"""
import html
from pathlib import Path

OUT = Path(__file__).parent

F = "Carlito, DejaVu Sans, Helvetica, sans-serif"
M = "DejaVu Sans Mono, Menlo, monospace"

NAVY, SLATE, MUTED = "#12293D", "#5F7285", "#8FA1B0"
BORDER, PANEL, GRID = "#D3DCE3", "#F5F8FA", "#E6ECF0"
RUST, AMBER, TEAL_INK = "#B14B33", "#C97A1E", "#0E8F9C"
TEAL = "#009AA8"   # data/mark teal: passes the CVD + chroma validator against RUST


def t(x, y, s, size=18, fill=NAVY, weight="normal", anchor="start", ls=0,
      font=F, style="normal", opacity=None):
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return (f'<text x="{x}" y="{y}" font-family="{font}" font-size="{size}" '
            f'fill="{fill}" font-weight="{weight}" text-anchor="{anchor}" '
            f'letter-spacing="{ls}" font-style="{style}"{o}>{html.escape(s)}</text>')


def r(x, y, w, h, fill, stroke=None, sw=2, rx=10, dash=None, opacity=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{opacity}"' if opacity is not None else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{d}{o}/>'


def line(x1, y1, x2, y2, stroke=BORDER, sw=1.5, dash=None, marker=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}{m}/>'


def svg(w, h, body, defs="", bg="#FFFFFF", viewbox=None):
    vb = viewbox or f"0 0 {w} {h}"
    markers = "".join(
        f'<marker id="{n}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
        f'markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
        for n, c in (("head", SLATE), ("headTeal", TEAL_INK), ("headAmber", AMBER)))
    bgrect = f'<rect width="100%" height="100%" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}">'
            f'<defs>{markers}{defs}</defs>{bgrect}{body}</svg>')


def header(title, sub):
    return t(60, 56, title, 36, NAVY, "bold") + t(60, 88, sub, 19, SLATE)


def bar(x, y, w, h, fill):
    """Horizontal bar anchored square at the baseline, 4px rounded data-end."""
    rr = min(4, w / 2)
    return (f'<path d="M{x},{y} H{x + w - rr} Q{x + w},{y} {x + w},{y + rr} '
            f'V{y + h - rr} Q{x + w},{y + h} {x + w - rr},{y + h} H{x} Z" fill="{fill}"/>')


# ---------------------------------------------------------------- figure 1
def fig1():
    b = [header("Five names, the same four dials",
                "When each coding agent loads a steering instruction")]
    cols = [("ALWAYS", "every task, every turn", NAVY),
            ("FILE-SCOPED", "only near matching paths", TEAL_INK),
            ("AGENT-DECIDED", "when the description fits", NAVY),
            ("ON REQUEST", "only when you invoke it", NAVY)]
    cx = [300, 610, 920, 1230]
    W = 300
    for (head, sub, c), x in zip(cols, cx):
        b.append(t(x + 16, 146, head, 15, c, "bold", ls=2.4))
        b.append(t(x + 16, 170, sub, 15, SLATE))

    rows = [
        ("Kiro", "AWS",
         [("inclusion: always", "product · tech · structure"),
          ("inclusion: fileMatch", 'fileMatchPattern: "api/**"'),
          ("inclusion: auto", "matched on description"),
          ("inclusion: manual", "#name or / in chat")]),
        ("Claude Code", "Anthropic",
         [("CLAUDE.md", "rules without paths"),
          ('paths: ["src/api/**"]', ".claude/rules/*.md"),
          ("skills", "loaded when relevant"),
          ("/skill-name", "invoked by you")]),
        ("Cursor", "project rules",
         [("alwaysApply: true", ".cursor/rules/*.mdc"),
          ('globs: "src/api/**"', "attached on file match"),
          ('description: "…"', "agent pulls it in"),
          ("@rule-name", "mentioned in chat")]),
        ("GitHub Copilot", "custom instructions",
         [("copilot-instructions.md", ".github/"),
          ('applyTo: "src/api/**"', ".github/instructions/"),
          None, None]),
        ("AGENTS.md", "open format",
         [("AGENTS.md", "repository root"),
          ("nested AGENTS.md", "nearest file in the tree wins"),
          None, None]),
    ]
    y0, H, gap = 196, 106, 12
    for i, (name, sub, cells) in enumerate(rows):
        y = y0 + i * (H + gap)
        b.append(t(60, y + 50, name, 23, NAVY, "bold"))
        b.append(t(60, y + 76, sub, 15, SLATE))
        for j, (cell, x) in enumerate(zip(cells, cx)):
            scoped = j == 1
            if cell is None:
                b.append(r(x, y, W, H, "#FFFFFF", BORDER, 1.5, dash="6 6"))
                b.append(t(x + W / 2, y + H / 2 + 6, "no equivalent", 15, MUTED,
                           anchor="middle", style="italic"))
                continue
            code, cap = cell
            b.append(r(x, y, W, H, "#EEF8F9" if scoped else PANEL,
                       TEAL if scoped else BORDER, 2.5 if scoped else 2))
            b.append(t(x + 18, y + 46, code, 17, NAVY, "bold", font=M))
            b.append(t(x + 18, y + 76, cap, 15, SLATE))

    b.append(t(60, 820, "Scoping is the dial that matters most. Every major tool has it. Most steering files don't use it.",
               19, NAVY, "bold"))
    b.append(t(60, 852, "Syntax as documented by each vendor, October 2026. Kiro CLI does not yet support inclusion modes.",
               15, SLATE))
    return svg(1600, 900, "".join(b))


# ---------------------------------------------------------------- figure 2
def fig2():
    b = [header("What goes into agent context files",
                "We write down how the code works. We rarely write down how to keep it safe.")]
    # legend: two series, so a legend is required; bars are also direct-labelled
    b.append(r(60, 128, 16, 16, TEAL, rx=3))
    b.append(t(86, 142, "Written often: how the code works", 17, NAVY))
    b.append(r(420, 128, 16, 16, RUST, rx=3))
    b.append(t(446, 142, "Rarely written: guardrails", 17, NAVY))

    x0, span = 420, 880              # 0% .. 100%
    top, bottom = 178, 540
    for p in (0, 25, 50, 75, 100):
        gx = x0 + span * p / 100
        b.append(line(gx, top, gx, bottom, GRID, 1.5))
        b.append(t(gx, bottom + 26, f"{p}%", 15, SLATE, anchor="middle"))

    rows = [("Test procedures", 75.9, TEAL, 190), ("Implementation details", 70.8, TEAL, 254),
            ("Architecture", 68.1, TEAL, 318), ("Security", 14.8, RUST, 418),
            ("Performance", 14.5, RUST, 482)]
    for label, v, c, y in rows:
        w = span * v / 100
        b.append(t(400, y + 31, label, 20, NAVY, anchor="end"))
        b.append(bar(x0, y, w, 46, c))
        b.append(t(x0 + w + 14, y + 31, f"{v}%", 21, NAVY, "bold"))

    for x, accent, head, body, src in (
        (60, TEAL, "Mostly what the agent can read for itself",
         ["A controlled study found repository overviews did not",
          "improve task success, while context files added over",
          "20% to inference cost."],
         "Gloaguen et al., ETH Zurich and LogicStar.ai, 2026"),
        (810, RUST, "Rarely, what keeps agent code safe and fast",
         ["Security and performance guidance appears in fewer than",
          "one in six files. The study calls it a significant gap.", ""],
         "Chatlatanagulchai et al., 2025")):
        b.append(r(x, 594, 730, 196, PANEL, BORDER, 1.5, rx=10))
        b.append(r(x, 594, 7, 196, accent, rx=3))
        b.append(t(x + 32, 636, head, 21, NAVY, "bold"))
        for k, ln in enumerate(body):
            b.append(t(x + 32, 670 + k * 28, ln, 18, NAVY))
        b.append(t(x + 32, 772, src, 14, SLATE, style="italic"))

    b.append(t(60, 852, "Share of 2,303 agent context files from 1,925 repositories containing each instruction type "
                        "(five of the 16 types studied). Source: arXiv 2511.12884.", 15, SLATE))
    return svg(1600, 900, "".join(b))


# ---------------------------------------------------------------- figure 3
def fig3():
    b = [header("Every line, four questions",
                "Answer in order and stop at the first yes")]
    steps = [
        ("Could the agent work it out", "by reading the code?", "CUT IT", RUST,
         "Directory layout · dependency list · framework · architecture overview"),
        ("Would breaking it cause", "real damage?", "ENFORCE IT ELSEWHERE", AMBER,
         "A hook, a permission rule, or a CI check. Not steering."),
        ("Does it only apply to", "part of the codebase?", "SCOPE IT", TEAL_INK,
         "inclusion: fileMatch  ·  paths  ·  globs  ·  applyTo"),
        ("Otherwise, it's a convention", "the model can't infer", "KEEP IT", NAVY,
         '"money is integer cents"  ·  "pnpm, not npm"  ·  "payments only in billing/"'),
    ]
    y0, H, step = 132, 104, 140
    for i, (q1, q2, verb, c, ex) in enumerate(steps):
        y = y0 + i * step
        last = i == len(steps) - 1
        b.append(r(60, y, 640, H, "#FFFFFF" if last else PANEL, BORDER, 2,
                   dash="7 6" if last else None))
        b.append(f'<circle cx="104" cy="{y + H / 2}" r="22" fill="{NAVY}"/>')
        b.append(t(104, y + H / 2 + 8, str(i + 1), 22, "#FFFFFF", "bold", anchor="middle"))
        b.append(t(146, y + 44, q1, 23, NAVY, "bold", style="italic" if last else "normal"))
        b.append(t(146, y + 76, q2, 23, NAVY, "bold", style="italic" if last else "normal"))
        b.append(line(704, y + H / 2, 796, y + H / 2, SLATE, 2.5, marker="head"))
        if not last:
            b.append(t(750, y + H / 2 - 12, "yes", 16, SLATE, "bold", anchor="middle"))
            b.append(line(240, y + H, 240, y + step - 4, SLATE, 2.5, marker="head"))
            b.append(t(256, y + H + 25, "no", 16, SLATE, "bold"))
        b.append(r(806, y, 734, H, PANEL, BORDER, 2))
        b.append(r(806, y, 8, H, c, rx=3))
        b.append(t(840, y + 44, verb, 25, c, "bold", ls=1.4))
        b.append(t(840, y + 78, ex, 17, SLATE, font=M if i == 2 else F))

    b.append(r(60, 718, 1480, 96, "#FDF6EC", "#EBD3AE", 1.5))
    b.append(t(800, 768, "What survives is short: the conventions nothing in the code would have told the agent.",
               24, NAVY, "bold", anchor="middle"))
    b.append(t(800, 798, "Write what the model can't guess.", 18, AMBER, "bold", anchor="middle", style="italic"))
    return svg(1600, 900, "".join(b))


# ---------------------------------------------------------------- figure 4
def fig4():
    b = [header("A suggestion is not a guarantee",
                "Where an instruction lives decides whether the model can ignore it")]
    grad = ('<linearGradient id="spec" x1="0" y1="0" x2="1" y2="0">'
            f'<stop offset="0%" stop-color="{TEAL}"/><stop offset="68%" stop-color="{TEAL}"/>'
            f'<stop offset="74%" stop-color="{AMBER}"/><stop offset="100%" stop-color="{AMBER}"/></linearGradient>')
    b.append(t(60, 140, "THE MODEL DECIDES", 15, TEAL_INK, "bold", ls=2.4))
    b.append(t(1540, 140, "THE SYSTEM ENFORCES", 15, AMBER, "bold", anchor="end", ls=2.4))
    b.append(f'<rect x="60" y="154" width="1480" height="8" rx="4" fill="url(#spec)"/>')

    b.append(t(60, 214, "Context: the model weighs it, and can ignore it", 19, NAVY, "bold"))
    b.append(t(1130, 214, "Enforcement: holds regardless", 19, NAVY, "bold"))
    b.append(line(1110, 196, 1110, 690, BORDER, 2, dash="7 6"))

    cards = [
        (60, 330, "Always-on steering", "Read on every task.",
         ["CLAUDE.md", "AGENTS.md", "inclusion: always"], TEAL, False),
        (410, 330, "Scoped rules", "Read near matching files.",
         ["inclusion: fileMatch", "paths  ·  globs", "applyTo"], TEAL, False),
        (760, 330, "On-demand", "Read when relevant or asked.",
         ["inclusion: auto · manual", "skills", "@rule-name"], TEAL, False),
        (1130, 410, "Hooks, permissions, CI", "Run outside the model.",
         ["PreToolUse hook", "permission deny rule", "required CI check"], AMBER, True),
    ]
    for x, w, head, sub, ex, c, enforced in cards:
        y, h = 236, 270
        b.append(r(x, y, w, h, "#FDF6EC" if enforced else PANEL,
                   "#EBD3AE" if enforced else BORDER, 2))
        b.append(f'<rect x="{x}" y="{y}" width="{w}" height="7" rx="3" fill="{c}"/>')
        b.append(t(x + 24, y + 50, head, 23, NAVY, "bold"))
        b.append(t(x + 24, y + 80, sub, 17, SLATE))
        for k, e in enumerate(ex):
            b.append(t(x + 24, y + 124 + k * 30, e, 16, NAVY, font=M))
        if enforced:
            b.append(t(x + 24, y + 248, "holds no matter what it decides", 17, AMBER, "bold"))
        else:
            b.append(t(x + 24, y + 248, "weighed, not guaranteed", 17, SLATE, style="italic"))

    b.append(r(60, 540, 1030, 130, "#FFFFFF", BORDER, 1.5))
    b.append(t(88, 580, "PUT HERE", 14, TEAL_INK, "bold", ls=2.4))
    b.append(t(88, 616, "Preferences: naming, style, and conventions that differ", 21, NAVY))
    b.append(t(88, 646, "from the default.", 21, NAVY))
    b.append(r(1130, 540, 410, 130, "#FFFFFF", BORDER, 1.5))
    b.append(t(1158, 580, "PUT HERE", 14, AMBER, "bold", ls=2.4))
    b.append(t(1158, 616, "Must-nevers: production", 21, NAVY))
    b.append(t(1158, 646, "migrations, credentials.", 21, NAVY))

    b.append(r(60, 716, 1480, 92, PANEL, BORDER, 1.5))
    b.append(t(800, 772, "Put preferences in steering. Put must-nevers in enforcement.", 27, NAVY, "bold",
               anchor="middle"))
    b.append(t(60, 852, "Claude Code's docs: CLAUDE.md is “context, not enforced configuration”; "
                        "to block an action regardless of what Claude decides, use a hook.", 15, SLATE))
    return svg(1600, 900, "".join(b), defs=grad)


# ---------------------------------------------------------------- cover
COVER_DEFS = (
    '<linearGradient id="bg" x1="0.1" y1="0" x2="0.85" y2="1">'
    '<stop offset="0%" stop-color="#081926"/><stop offset="48%" stop-color="#0E2839"/>'
    '<stop offset="100%" stop-color="#091E2C"/></linearGradient>'
    '<radialGradient id="vignette" cx="50%" cy="42%" r="78%">'
    '<stop offset="55%" stop-color="#000" stop-opacity="0"/>'
    '<stop offset="100%" stop-color="#000" stop-opacity="0.42"/></radialGradient>'
    '<radialGradient id="glow" cx="50%" cy="50%" r="50%">'
    '<stop offset="0%" stop-color="#F5AE45" stop-opacity="0.30"/>'
    '<stop offset="100%" stop-color="#F5AE45" stop-opacity="0"/></radialGradient>'
    '<linearGradient id="rule" x1="0" y1="0" x2="1" y2="0">'
    '<stop offset="0%" stop-color="#F5AE45"/><stop offset="48%" stop-color="#3ACBD5"/>'
    '<stop offset="100%" stop-color="#3ACBD5" stop-opacity="0"/></linearGradient>'
)


def cover_body():
    b = ['<rect width="1600" height="900" fill="url(#bg)"/>']
    b.append(t(78, 70, "AI ENGINEERING  ·  CODING AGENTS", 15, "#7A98AB", "bold", ls=3.4))
    b.append(t(78, 172, "Write what", 80, "#FFFFFF", "bold"))
    b.append(t(78, 262, "the model", 80, "#FFFFFF", "bold"))
    b.append(t(78, 352, "can’t guess.", 80, "#F5AE45", "bold"))
    b.append('<rect x="80" y="390" width="330" height="4" rx="2" fill="url(#rule)"/>')
    b.append(t(78, 446, "Most of a steering file restates the code.", 25, "#B9CEDC"))
    b.append(t(78, 482, "A few lines do all the work.", 25, "#B9CEDC"))

    # the file
    px, py, pw, ph = 930, 110, 590, 690
    b.append(r(px, py, pw, ph, "#0B2233", "#1F4257", 1.5, rx=16))
    b.append(r(px, py, pw, 50, "#0F2C40", rx=16))
    b.append(f'<rect x="{px}" y="{py + 34}" width="{pw}" height="16" fill="#0F2C40"/>')
    for k, c in enumerate(("#B14B33", "#C97A1E", "#3ACBD5")):
        b.append(f'<circle cx="{px + 28 + k * 22}" cy="{py + 25}" r="6" fill="{c}" opacity="0.8"/>')
    b.append(t(px + pw / 2, py + 31, "AGENTS.md", 16, "#7A98AB", anchor="middle", font=M))

    doc = [
        ("## Project structure", 0), ("src/", 0), ("├── api/        REST handlers", 0),
        ("├── components/ React UI", 0), ("└── utils/      helpers", 0), ("", 0),
        ("## Tech stack", 0), ("- React 18, TypeScript, Node 20", 0), ("- PostgreSQL via Prisma", 0),
        ("", 0), ("## Conventions", 0),
        ("- money is integer cents, never floats", 1), ("- use pnpm, not npm", 1),
        ("- payments client only in billing/", 1), ("", 0),
        ("## Architecture", 0), ("Services talk to each other over REST.", 0),
    ]
    y = py + 92
    for text_, hot in doc:
        if hot:
            b.append(f'<ellipse cx="{px + 250}" cy="{y - 6}" rx="300" ry="26" fill="url(#glow)"/>')
            b.append(r(px + 22, y - 24, pw - 44, 32, "#F5AE45", rx=6, opacity=0.14))
            b.append(f'<rect x="{px + 22}" y="{y - 24}" width="4" height="32" fill="#F5AE45"/>')
            b.append(t(px + 40, y, text_, 17, "#F5AE45", "bold", font=M))
        elif text_:
            b.append(t(px + 40, y, text_, 16, "#5D7D91", font=M, opacity=0.62))
        y += 32
    b.append(t(px + pw - 26, py + ph - 26, "THREE LINES DO THE WORK", 13, "#F5AE45", "bold",
               anchor="end", ls=2.4))

    b.append('<rect width="1600" height="900" fill="url(#vignette)"/>')
    b.append(t(78, 842, "KIRO  ·  CLAUDE CODE  ·  CURSOR  ·  COPILOT  ·  AGENTS.MD", 13, "#7A98AB", "bold", ls=2.4))
    return "".join(b)


def cover():
    return svg(1600, 900, cover_body(), defs=COVER_DEFS, bg=None)


def social():
    # 1200x630 card: same art, cropped to the 1.905:1 safe area (y 30..870)
    return svg(1200, 630, cover_body(), defs=COVER_DEFS, bg=None, viewbox="0 30 1600 840")


# ---------------------------------------------------------------- terminal card (README)
TERMINAL_RUN = [  # real output of `steering_lint.py` on a demo repo (see README)
    ("prompt", "$ python3 steering_lint.py ."),
    ("", ""),
    ("file", ".kiro/steering/api.md  (~37 tokens, scoped)"),
    ("ok", "nothing flagged"),
    ("", ""),
    ("file", "AGENTS.md  (~292 tokens, loads every task)"),
    ("derivable", "overview content on lines 3, 5, 6, 7, 9: the agent can read this from the code"),
    ("guardrails", "no security guidance (found in only 14.8% of files studied)"),
    ("guardrails", "no performance guidance (found in only 14.5% of files studied)"),
    ("scope", "74 lines load on every task; scope rules that apply to part of the codebase"),
    ("enforce", "line 14: a must-never; a hook or permission rule enforces it, steering only suggests it"),
    ("", ""),
    ("summary", "~292 tokens of steering load on every task (chars / 4 estimate)."),
]
KIND_COLOR = {"ok": "#3ACBD5", "derivable": "#E8846B", "guardrails": "#F5AE45",
              "scope": "#3ACBD5", "enforce": "#F5AE45"}


def terminal():
    b = ['<rect width="1600" height="680" fill="#FFFFFF"/>']
    b.append(r(40, 40, 1520, 600, "#0B2233", "#1F4257", 1.5, rx=16))
    b.append(r(40, 40, 1520, 54, "#0F2C40", rx=16))
    b.append('<rect x="40" y="78" width="1520" height="16" fill="#0F2C40"/>')
    for k, c in enumerate(("#B14B33", "#C97A1E", "#3ACBD5")):
        b.append(f'<circle cx="{72 + k * 24}" cy="67" r="7" fill="{c}" opacity="0.85"/>')
    b.append(t(800, 74, "steering_lint", 17, "#7A98AB", anchor="middle", font=M))
    y, ch = 150, 13.2
    for kind, msg in TERMINAL_RUN:
        if kind == "prompt":
            b.append(t(92, y, msg, 22, "#3ACBD5", "bold", font=M))
        elif kind in ("file", "summary"):
            b.append(t(92, y, msg, 22, "#E8EEF2" if kind == "file" else "#B9CEDC",
                       "bold" if kind == "file" else "normal", font=M))
        elif kind:
            b.append(t(92 + 2 * ch, y, kind, 22, KIND_COLOR[kind], "bold", font=M))
            b.append(t(92 + 13 * ch, y, msg, 22, "#B9CEDC", font=M))
        y += 38
    return svg(1600, 680, "".join(b), bg=None)


if __name__ == "__main__":
    (OUT / "linter-output.svg").write_text(terminal())
    print("wrote linter-output")
    for name, fn in (("fig1-same-four-dials", fig1), ("fig2-what-we-write", fig2),
                     ("fig3-four-questions", fig3), ("fig4-suggestion-vs-guarantee", fig4),
                     ("cover-write-what-the-model-cant-guess", cover),
                     ("cover-social-1200x630", social)):
        (OUT / f"{name}.svg").write_text(fn())
        print("wrote", name)
