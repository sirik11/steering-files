// Figures for "Write What the Model Can't Guess": an editor's markup of a steering file.
//
//   cd figures && npm install && node make_figures.mjs
//
// Hand-drawn strokes come from rough.js (fixed seeds, so output is reproducible).
// Type: Libre Baskerville, IBM Plex Mono, Kalam (all OFL, in ./fonts).
// PNGs are rendered by headless Chrome at 2x so the web fonts are guaranteed.
import rough from "roughjs/bundled/rough.esm.js";
import { spawn } from "node:child_process";
import { existsSync, statSync, writeFileSync, unlinkSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const DIR = dirname(fileURLToPath(import.meta.url));
const g = rough.generator();
let seed = 11;

// palette: paper, ink, and the three pens an editor actually uses
const PAPER = "#F4EFE4", SHEET = "#FBF8F1", INK = "#1D1D1B", PENCIL = "#6F6A60", FAINT = "#C9C1B1";
const RED = "#C8352B", BLUE = "#2E6BA6", HI = "#F2D64B";   // RED/BLUE pass the CVD + chroma validator on PAPER
const SERIF = "'Libre Baskerville', Georgia, serif";
const MONO = "'IBM Plex Mono', Menlo, monospace";
const HAND = "Kalam, 'Bradley Hand', cursive";
const MONO_W = 0.6;                                        // IBM Plex Mono advance width, em

const FONTS = `
@font-face{font-family:'Libre Baskerville';src:url(fonts/LibreBaskerville-Variable.ttf);font-weight:400 700}
@font-face{font-family:'Libre Baskerville';font-style:italic;src:url(fonts/LibreBaskerville-Italic-Variable.ttf);font-weight:400 700}
@font-face{font-family:'IBM Plex Mono';src:url(fonts/IBMPlexMono-Regular.ttf);font-weight:400}
@font-face{font-family:'IBM Plex Mono';src:url(fonts/IBMPlexMono-Bold.ttf);font-weight:700}
@font-face{font-family:Kalam;src:url(fonts/Kalam-Regular.ttf);font-weight:400}
@font-face{font-family:Kalam;src:url(fonts/Kalam-Bold.ttf);font-weight:700}`;

const esc = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function T(x, y, s, { size = 20, fill = INK, font = SERIF, weight = 400, anchor = "start",
  italic = false, ls = 0, rot = 0, opacity } = {}) {
  const tr = rot ? ` transform="rotate(${rot} ${x} ${y})"` : "";
  const op = opacity != null ? ` opacity="${opacity}"` : "";
  return `<text x="${x}" y="${y}" font-family="${font}" font-size="${size}" fill="${fill}" font-weight="${weight}"` +
    ` text-anchor="${anchor}" font-style="${italic ? "italic" : "normal"}" letter-spacing="${ls}"${tr}${op}>${esc(s)}</text>`;
}

// render a rough.js drawable to SVG paths
function draw(d, { opacity, dash, blend } = {}) {
  return g.toPaths(d).map((p) =>
    `<path d="${p.d}" stroke="${p.stroke}" stroke-width="${p.strokeWidth}" fill="${p.fill || "none"}"` +
    ` stroke-linecap="round" stroke-linejoin="round"` +
    (opacity != null ? ` opacity="${opacity}"` : "") + (dash ? ` stroke-dasharray="${dash}"` : "") +
    (blend ? ` style="mix-blend-mode:${blend}"` : "") + `/>`).join("");
}
const o = (opts) => ({ seed: seed++, ...opts });
const line = (x1, y1, x2, y2, opts) => draw(g.line(x1, y1, x2, y2, o({ roughness: 1, ...opts })), opts);
const rect = (x, y, w, h, opts) => draw(g.rectangle(x, y, w, h, o({ roughness: 1, ...opts })), opts);
const ellipse = (cx, cy, w, h, opts) => draw(g.ellipse(cx, cy, w, h, o({ roughness: 1.3, ...opts })), opts);

// pen strike-through across monospace text
const strike = (x, y, chars, size, color = RED) =>
  line(x - 6, y - size * 0.32, x + chars * size * MONO_W + 6, y - size * 0.36,
    { stroke: color, strokeWidth: 2.6, roughness: 1.6, bowing: 1.5 });

// highlighter swipe behind monospace text
const highlight = (x, y, chars, size) =>
  rect(x - 8, y - size * 0.95, chars * size * MONO_W + 16, size * 1.3,
    { fill: HI, fillStyle: "solid", stroke: "none", roughness: 2.4, opacity: 0.7, blend: "multiply" });

// hand-drawn arrow: a curve through a control point, with a two-stroke head
function arrow(x1, y1, cx, cy, x2, y2, color = INK, w = 2.4) {
  const body = draw(g.curve([[x1, y1], [cx, cy], [x2, y2]], o({ stroke: color, strokeWidth: w, roughness: 1.1 })));
  const a = Math.atan2(y2 - cy, x2 - cx), L = 15;
  const head = [a + 2.6, a - 2.6].map((t) =>
    line(x2, y2, x2 + L * Math.cos(t), y2 + L * Math.sin(t), { stroke: color, strokeWidth: w, roughness: 0.8 })).join("");
  return body + head;
}

const DEFS = `
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch"/>
  <feColorMatrix type="saturate" values="0"/>
  <feComponentTransfer><feFuncA type="linear" slope="0.07"/></feComponentTransfer>
</filter>
<filter id="stamp" x="-10%" y="-20%" width="120%" height="140%">
  <feTurbulence type="fractalNoise" baseFrequency="0.55" numOctaves="2" seed="4" result="n"/>
  <feColorMatrix in="n" type="matrix" values="0 0 0 0 1 0 0 0 0 1 0 0 0 0 1 -9 0 0 0 6.2" result="m"/>
  <feComposite in="SourceGraphic" in2="m" operator="in"/>
</filter>
<filter id="lift" x="-10%" y="-10%" width="125%" height="130%">
  <feDropShadow dx="5" dy="9" stdDeviation="11" flood-color="#3B3023" flood-opacity="0.22"/>
</filter>`;

const page = (w, h, body, viewBox) =>
  `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="${viewBox || `0 0 ${w} ${h}`}">` +
  `<style>${FONTS}</style><defs>${DEFS}</defs>` +
  `<rect x="-50" y="-50" width="1700" height="1000" fill="${PAPER}"/>${body}` +
  `<rect x="-50" y="-50" width="1700" height="1000" filter="url(#grain)"/></svg>`;

const header = (title, sub) =>
  T(80, 96, title, { size: 42, weight: 700 }) + T(80, 138, sub, { size: 20, italic: true, fill: PENCIL });

function stamp(cx, cy, text, color, rot, size = 34, fillHi = false) {
  const w = text.length * (size * 0.8 + 4) + 56, h = size + 40, x = cx - w / 2, y = cy - h / 2;
  const hi = fillHi ? rect(x, y, w, h, { fill: HI, fillStyle: "solid", stroke: "none", roughness: 2, opacity: 0.8 }) : "";
  const box = rect(x, y, w, h, { stroke: color, strokeWidth: 3.4, roughness: 1.2 }) +
    rect(x + 7, y + 7, w - 14, h - 14, { stroke: color, strokeWidth: 1.6, roughness: 1.2 });
  return `<g transform="rotate(${rot} ${cx} ${cy})">${hi}<g filter="url(#stamp)">${box}` +
    T(cx, cy + size * 0.36, text, { size, weight: 700, fill: color, anchor: "middle", ls: 4 }) + `</g></g>`;
}

// ---------------------------------------------------------------- cover
function coverBody() {
  let b = T(90, 112, "ON STEERING FILES", { size: 16, weight: 700, fill: RED, ls: 5 });
  b += T(86, 236, "Write what", { size: 90, weight: 700 });
  b += T(86, 340, "the model", { size: 90, weight: 700 });
  b += T(86, 444, "can’t guess.", { size: 90, weight: 700 });
  b += line(92, 470, 668, 462, { stroke: RED, strokeWidth: 5, roughness: 1.8, bowing: 3 });
  b += T(90, 540, "Most of a steering file restates the code.", { size: 27, italic: true, fill: PENCIL });
  b += T(90, 582, "A few lines do all the work.", { size: 27, italic: true, fill: PENCIL });
  b += T(90, 818, "KIRO  ·  CLAUDE CODE  ·  CURSOR  ·  COPILOT  ·  AGENTS.MD",
    { size: 14, weight: 700, fill: PENCIL, ls: 3 });

  // the marked-up file
  const sx = 860, sy = 92, sw = 640, sh = 716, fs = 19, lh = 34, tx = sx + 44;
  let s = `<rect x="${sx}" y="${sy}" width="${sw}" height="${sh}" fill="${SHEET}" filter="url(#lift)"/>`;
  s += T(tx, sy + 50, "AGENTS.md", { size: 15, font: MONO, fill: PENCIL });
  s += line(tx, sy + 66, sx + sw - 44, sy + 66, { stroke: FAINT, strokeWidth: 1.4, roughness: 0.6 });
  const doc = [
    ["## Project structure", "x"], ["src/", "x"], ["├── api/", "x"], ["├── billing/", "x"],
    ["└── web/", "x"], ["", ""], ["## Tech stack", "x"], ["- TypeScript, Node 20", "x"],
    ["- PostgreSQL via Prisma", "x"], ["", ""], ["## Conventions", ""],
    ["- money is integer cents, never floats", "k"], ["- use pnpm, not npm", "k"],
    ["- payments client only in billing/", "k"], ["", ""], ["## Architecture", "x"],
    ["Services talk to each other over REST.", "x"],
  ];
  let y = sy + 112;
  const keepYs = [];
  for (const [txt, mark] of doc) {
    if (mark === "k") { s += highlight(tx, y, txt.length, fs); keepYs.push(y); }
    s += T(tx, y, txt, { size: fs, font: MONO, fill: mark === "x" ? "#5B564D" : INK, weight: mark === "k" ? 700 : 400 });
    if (mark === "x") s += strike(tx, y, txt.length, fs);
    y += lh;
  }
  const midK = (keepYs[0] + keepYs[2]) / 2 - fs * 0.35;
  // margin bracket, the way an editor marks a passage to keep
  const by0 = keepYs[0] - fs - 4, by1 = keepYs[2] + 10, bx = tx - 22;
  s += line(bx, by0, bx, by1, { stroke: RED, strokeWidth: 3, roughness: 1.2 });
  s += line(bx, by0, bx + 12, by0 - 2, { stroke: RED, strokeWidth: 3, roughness: 0.8 });
  s += line(bx, by1, bx + 12, by1 + 1, { stroke: RED, strokeWidth: 3, roughness: 0.8 });
  s += line(bx - 14, midK - 2, bx - 1, midK, { stroke: RED, strokeWidth: 3, roughness: 0.8 });
  s += T(sx + 352, sy + 168, "the agent can", { size: 28, font: HAND, weight: 700, fill: RED, rot: -5 });
  s += T(sx + 352, sy + 204, "already read this", { size: 28, font: HAND, weight: 700, fill: RED, rot: -5 });
  s += arrow(sx + 344, sy + 190, sx + 290, sy + 230, sx + 236, sy + 214, RED);
  s += T(sx + 330, keepYs[0] - 68, "keep only these", { size: 32, font: HAND, weight: 700, fill: RED, rot: -4 });
  s += arrow(sx + 330, keepYs[0] - 62, sx + 300, keepYs[0] - 40, sx + 318, keepYs[0] - 24, RED);
  return b + `<g transform="rotate(2.2 ${sx + sw / 2} ${sy + sh / 2})">${s}</g>`;
}
const cover = () => page(1600, 900, coverBody());
const social = () => page(1200, 630, coverBody(), "0 30 1600 840");

// ---------------------------------------------------------------- figure 1
function fig1() {
  let b = header("Five names, the same four dials", "When each coding agent loads a steering instruction");
  const cols = [["ALWAYS", "every task, every turn"], ["FILE-SCOPED", "only near matching paths"],
    ["AGENT-DECIDED", "when the description fits"], ["ON REQUEST", "only when you invoke it"]];
  const cx = [330, 630, 930, 1230];
  cols.forEach(([h, s], i) => {
    b += T(cx[i], 206, h, { size: 15, weight: 700, ls: 2.6, fill: i === 1 ? BLUE : INK });
    b += T(cx[i], 232, s, { size: 16, italic: true, fill: PENCIL });
  });
  b += line(80, 254, 1514, 254, { stroke: INK, strokeWidth: 1.8, roughness: 0.7 });
  const rows = [
    ["Kiro", "AWS", [["inclusion: always", "product · tech · structure"], ["inclusion: fileMatch", 'fileMatchPattern: "api/**"'],
      ["inclusion: auto", "matched on description"], ["inclusion: manual", "#name or / in chat"]]],
    ["Claude Code", "Anthropic", [["CLAUDE.md", "rules without paths"], ['paths: ["src/api/**"]', ".claude/rules/*.md"],
      ["skills", "loaded when relevant"], ["/skill-name", "invoked by you"]]],
    ["Cursor", "project rules", [["alwaysApply: true", ".cursor/rules/*.mdc"], ['globs: "src/api/**"', "attached on file match"],
      ['description: "…"', "agent pulls it in"], ["@rule-name", "mentioned in chat"]]],
    ["GitHub Copilot", "custom instructions", [["copilot-instructions.md", ".github/"],
      ['applyTo: "src/api/**"', ".github/instructions/"], null, null]],
    ["AGENTS.md", "open format", [["AGENTS.md", "repository root"], ["nested AGENTS.md", "nearest file in the tree wins"], null, null]],
  ];
  rows.forEach(([name, sub, cells], i) => {
    const top = 258 + i * 104;
    b += T(80, top + 50, name, { size: 24, weight: 700 });
    b += T(80, top + 78, sub, { size: 16, italic: true, fill: PENCIL });
    cells.forEach((c, j) => {
      if (!c) { b += line(cx[j] + 110, top + 52, cx[j] + 150, top + 50, { stroke: FAINT, strokeWidth: 3, roughness: 1.2 }); return; }
      b += T(cx[j], top + 50, c[0], { size: 18, font: MONO, weight: 700 });
      b += T(cx[j], top + 78, c[1], { size: 15, italic: true, fill: PENCIL });
    });
    if (i < rows.length - 1) b += line(80, top + 104, 1514, top + 104, { stroke: FAINT, strokeWidth: 1.2, roughness: 0.8 });
  });
  b += rect(606, 178, 312, 610, { stroke: BLUE, strokeWidth: 2.8, roughness: 1.7, bowing: 2 });
  b += arrow(700, 828, 680, 812, 690, 796, BLUE);
  b += T(712, 842, "the dial that matters most. every tool has it. most files never use it.",
    { size: 27, font: HAND, weight: 700, fill: BLUE, rot: -1 });
  b += T(80, 884, "Syntax as documented by each vendor, October 2026. Kiro CLI does not yet support inclusion modes.",
    { size: 14, italic: true, fill: PENCIL });
  return page(1600, 900, b);
}

// ---------------------------------------------------------------- figure 2 (chart)
function fig2() {
  let b = header("What goes into agent context files",
    "We write down how the code works. We rarely write down how to keep it safe.");
  // legend (two series, also direct-labelled; hue + texture, never colour alone)
  b += rect(80, 172, 36, 22, { fill: BLUE, fillStyle: "hachure", hachureAngle: -41, hachureGap: 6, stroke: BLUE, strokeWidth: 1.6 });
  b += T(128, 190, "written often: how the code works", { size: 18 });
  b += rect(520, 172, 36, 22, { fill: RED, fillStyle: "cross-hatch", hachureGap: 7, stroke: RED, strokeWidth: 1.6 });
  b += T(568, 190, "rarely written: guardrails", { size: 18 });

  const x0 = 360, span = 860;
  const rows = [["Test procedures", 75.9, BLUE, 236], ["Implementation details", 70.8, BLUE, 302],
    ["Architecture", 68.1, BLUE, 368], ["Security", 14.8, RED, 470], ["Performance", 14.5, RED, 536]];
  for (const [label, v, c, y] of rows) {
    const w = span * v / 100;
    b += T(340, y + 33, label, { size: 21, anchor: "end" });
    b += rect(x0, y, w, 50, c === BLUE
      ? { fill: BLUE, fillStyle: "hachure", hachureAngle: -41, hachureGap: 7, fillWeight: 2, stroke: BLUE, strokeWidth: 1.8, roughness: 1.1 }
      : { fill: RED, fillStyle: "cross-hatch", hachureGap: 8, fillWeight: 1.6, stroke: RED, strokeWidth: 1.8, roughness: 1.1 });
    b += T(x0 + w + 16, y + 34, `${v}%`, { size: 22, weight: 700 });
  }
  b += line(x0, 218, x0, 604, { stroke: INK, strokeWidth: 2.2, roughness: 0.7 });
  for (const p of [0, 25, 50, 75, 100]) {
    const gx = x0 + span * p / 100;
    b += line(gx, 606, gx, 618, { stroke: INK, strokeWidth: 1.6, roughness: 0.5 });
    b += T(gx, 642, `${p}%`, { size: 15, italic: true, fill: PENCIL, anchor: "middle" });
  }
  // margin notes in ink: annotations wear text colour, never the series colour
  b += T(1086, 372, "overview content like this", { size: 24, font: HAND, rot: -2 });
  b += T(1086, 402, "didn't improve task success", { size: 24, font: HAND, rot: -2 });
  b += T(1086, 432, "in a controlled study", { size: 24, font: HAND, rot: -2 });
  b += arrow(1078, 380, 1062, 388, 1048, 394, INK, 2);
  b += T(640, 512, "fewer than one in six files say anything", { size: 27, font: HAND, weight: 700, rot: -1.5 });
  b += T(640, 546, "about security or performance", { size: 27, font: HAND, weight: 700, rot: -1.5 });
  b += arrow(632, 520, 610, 524, 596, 508, INK, 2.2);
  b += T(800, 730, "we document the code. we forget the guardrails.", { size: 36, font: HAND, weight: 700, anchor: "middle", rot: -1.2 });
  b += line(350, 752, 1250, 746, { stroke: RED, strokeWidth: 3.4, roughness: 1.8, bowing: 2 });
  b += T(80, 868, "Share of 2,303 agent context files from 1,925 repositories containing each instruction type (five of 16 types studied).",
    { size: 14, italic: true, fill: PENCIL });
  b += T(80, 888, "Sources: Chatlatanagulchai et al., arXiv 2511.12884; overview finding, Gloaguen et al., arXiv 2602.11988.",
    { size: 14, italic: true, fill: PENCIL });
  return page(1600, 900, b);
}

// ---------------------------------------------------------------- figure 3
function fig3() {
  let b = header("Every line, four questions", "Answer in order and stop at the first yes.");
  const steps = [
    ["Could the agent work it out", "by reading the code?", "directory layout, dependency list, framework, architecture overview", "CUT IT", RED, -4, false],
    ["Would breaking it cause", "real damage?", "a hook, a permission rule, or a CI check. Not steering.", "ENFORCE ELSEWHERE", INK, 3, false],
    ["Does it only apply to", "part of the codebase?", "inclusion: fileMatch  ·  paths  ·  globs  ·  applyTo", "SCOPE IT", BLUE, -2.5, false],
    ["Otherwise, it’s a convention", "the model can’t infer.", "“money is integer cents”  ·  “pnpm, not npm”", "KEEP IT", INK, 4, true],
  ];
  steps.forEach(([q1, q2, ex, verb, color, rot, hi], i) => {
    const top = 182 + i * 142, last = i === steps.length - 1;
    b += ellipse(112, top + 36, 54, 54, { stroke: INK, strokeWidth: 2.4, roughness: 1.4 });
    b += T(112, top + 47, String(i + 1), { size: 30, font: HAND, weight: 700, anchor: "middle" });
    b += T(164, top + 30, q1, { size: 25, weight: 700, italic: last });
    b += T(164, top + 64, q2, { size: 25, weight: 700, italic: last });
    b += T(164, top + 100, ex, { size: 17, italic: i !== 2, fill: PENCIL, font: i === 2 ? MONO : SERIF });
    if (!last) {
      b += T(814, top + 16, "yes", { size: 24, font: HAND, weight: 700, fill: PENCIL, anchor: "middle" });
      b += line(112, top + 66, 112, top + 152, { stroke: PENCIL, strokeWidth: 2.2, roughness: 1 });
      b += line(112, top + 152, 104, top + 140, { stroke: PENCIL, strokeWidth: 2.2, roughness: 0.6 });
      b += line(112, top + 152, 120, top + 140, { stroke: PENCIL, strokeWidth: 2.2, roughness: 0.6 });
      b += T(126, top + 124, "no", { size: 22, font: HAND, weight: 700, fill: PENCIL });
    }
    b += arrow(744, top + 42, 812, top + 34, 880, top + 42, PENCIL, 2.4);
    b += stamp(1150, top + 40, verb, color, rot, verb.length > 10 ? 27 : 34, hi);
  });
  b += T(110, 800, "what survives is short: the conventions nothing in the code would have told the agent.",
    { size: 30, font: HAND, weight: 700, rot: -0.8 });
  b += line(478, 816, 636, 813, { stroke: RED, strokeWidth: 3.4, roughness: 1.6, bowing: 2 });
  return page(1600, 900, b);
}

// ---------------------------------------------------------------- figure 4
function fig4() {
  let b = header("A suggestion is not a guarantee", "Where an instruction lives decides whether the model can ignore it.");
  // left: the note
  b += T(100, 222, "A steering file is a note.", { size: 30, weight: 700 });
  let note = `<rect x="150" y="262" width="372" height="320" fill="#F7E07A" filter="url(#lift)"/>` +
    `<rect x="150" y="262" width="372" height="40" fill="#EDD45F"/>`;
  note += T(184, 362, "please use", { size: 38, font: HAND, weight: 700 });
  note += T(184, 410, "pnpm, not npm", { size: 38, font: HAND, weight: 700 });
  note += T(184, 470, "money is", { size: 38, font: HAND, weight: 700 });
  note += T(184, 518, "integer cents", { size: 38, font: HAND, weight: 700 });
  note += line(184, 534, 420, 530, { stroke: INK, strokeWidth: 2.4, roughness: 1.6 });
  b += `<g transform="rotate(-3 336 422)">${note}</g>`;
  b += T(100, 656, "The model reads it, weighs it, and decides.", { size: 20 });
  b += T(100, 694, "CLAUDE.md · AGENTS.md · .kiro/steering/", { size: 17, font: MONO, fill: PENCIL });
  b += T(100, 722, "scoped rules · skills · @mentions", { size: 17, font: MONO, fill: PENCIL });
  b += T(100, 764, "weighed, not guaranteed", { size: 19, italic: true, fill: PENCIL });

  b += line(800, 196, 800, 780, { stroke: FAINT, strokeWidth: 2, roughness: 1.4, dash: "10 10" });

  // right: the lock
  b += T(860, 222, "A hook is a lock.", { size: 30, weight: 700 });
  b += draw(g.path("M1086 418 L1086 352 C1086 280 1214 280 1214 352 L1214 418",
    o({ stroke: INK, strokeWidth: 9, roughness: 1.2 })));
  b += rect(1040, 410, 220, 196, { stroke: INK, strokeWidth: 4, roughness: 1.2, fill: "#D8CFBD",
    fillStyle: "hachure", hachureAngle: -30, hachureGap: 9, fillWeight: 1.4 });
  b += ellipse(1150, 486, 40, 40, { fill: INK, fillStyle: "solid", stroke: INK, strokeWidth: 2, roughness: 0.9 });
  b += rect(1141, 496, 18, 52, { fill: INK, fillStyle: "solid", stroke: INK, strokeWidth: 2, roughness: 0.8 });
  b += T(1150, 652, "no migrations against production", { size: 28, font: HAND, weight: 700, fill: RED, anchor: "middle", rot: -1.5 });
  b += line(942, 666, 1360, 660, { stroke: RED, strokeWidth: 2.8, roughness: 1.6 });
  b += T(860, 708, "It runs no matter what the model decides.", { size: 20 });
  b += T(860, 742, "PreToolUse hook · permission deny rule · CI check", { size: 17, font: MONO, fill: PENCIL });
  b += T(860, 778, "enforced, every time", { size: 19, italic: true, fill: RED });

  b += T(800, 858, "preferences go on the note. must-nevers go behind the lock.",
    { size: 34, font: HAND, weight: 700, anchor: "middle", rot: -0.8 });
  return page(1600, 900, b);
}

// ---------------------------------------------------------------- terminal card (README)
const RUN = [
  ["prompt", "$ python3 steering_lint.py ."], ["", ""],
  ["file", ".kiro/steering/api.md  (~37 tokens, scoped)"], ["ok", "nothing flagged"], ["", ""],
  ["file", "AGENTS.md  (~292 tokens, loads every task)"],
  ["derivable", "overview content on lines 3, 5, 6, 7, 9: the agent can read this from the code"],
  ["guardrails", "no security guidance (found in only 14.8% of files studied)"],
  ["guardrails", "no performance guidance (found in only 14.5% of files studied)"],
  ["scope", "74 lines load on every task; scope rules that apply to part of the codebase"],
  ["enforce", "line 14: a must-never; a hook or permission rule enforces it, steering only suggests it"], ["", ""],
  ["summary", "~292 tokens of steering load on every task (chars / 4 estimate)."],
];
const KIND = { ok: "#8DBFEA", derivable: "#EE8B74", guardrails: "#F2D64B", scope: "#8DBFEA", enforce: "#F2D64B" };
function terminal() {
  let b = `<rect x="40" y="40" width="1520" height="600" rx="14" fill="#1E1C19" filter="url(#lift)"/>` +
    `<rect x="40" y="40" width="1520" height="52" rx="14" fill="#2A2723"/><rect x="40" y="76" width="1520" height="16" fill="#2A2723"/>`;
  ["#C8352B", "#E0A43A", "#6FA86A"].forEach((c, k) => { b += `<circle cx="${74 + k * 24}" cy="66" r="7" fill="${c}"/>`; });
  b += T(800, 72, "steering_lint", { size: 16, font: MONO, fill: "#8A8478", anchor: "middle" });
  let y = 148; const ch = 22 * MONO_W;
  for (const [k, msg] of RUN) {
    if (k === "prompt") b += T(92, y, msg, { size: 22, font: MONO, weight: 700, fill: "#F2D64B" });
    else if (k === "file") b += T(92, y, msg, { size: 22, font: MONO, weight: 700, fill: "#F1ECE2" });
    else if (k === "summary") b += T(92, y, msg, { size: 22, font: MONO, fill: "#BDB6A8" });
    else if (k) {
      b += T(92 + 2 * ch, y, k, { size: 22, font: MONO, weight: 700, fill: KIND[k] });
      b += T(92 + 13 * ch, y, msg, { size: 22, font: MONO, fill: "#D9D3C7" });
    }
    y += 38;
  }
  return page(1600, 680, b);
}

// ---------------------------------------------------------------- render
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PROFILE = join(process.env.TMPDIR || "/tmp", "steering-figures-chrome");

function render(name, svg, w, h) {
  writeFileSync(join(DIR, `${name}.svg`), svg);
  const html = join(DIR, `.render-${name}.html`), png = join(DIR, `${name}.png`);
  writeFileSync(html, `<!doctype html><html><head><style>html,body{margin:0;background:${PAPER}}svg{display:block}</style></head><body>${svg}</body></html>`);
  if (existsSync(png)) unlinkSync(png);
  const p = spawn(CHROME, ["--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
    `--user-data-dir=${PROFILE}`, `--window-size=${w},${h}`, "--force-device-scale-factor=2",
    "--virtual-time-budget=4000", `--screenshot=${png}`, `file://${html}`], { stdio: "ignore" });
  return new Promise((resolve, reject) => {
    const t0 = Date.now(); let last = -1;
    const tick = setInterval(() => {
      const size = existsSync(png) ? statSync(png).size : -1;
      if (size > 0 && size === last) { clearInterval(tick); p.kill(); unlinkSync(html); resolve(size); }
      else if (Date.now() - t0 > 30000) { clearInterval(tick); p.kill(); reject(new Error(`timeout: ${name}`)); }
      last = size;
    }, 700);
  });
}

const JOBS = [
  ["cover-write-what-the-model-cant-guess", cover, 1600, 900], ["cover-social-1200x630", social, 1200, 630],
  ["fig1-same-four-dials", fig1, 1600, 900], ["fig2-what-we-write", fig2, 1600, 900],
  ["fig3-four-questions", fig3, 1600, 900], ["fig4-suggestion-vs-guarantee", fig4, 1600, 900],
  ["linter-output", terminal, 1600, 680],
];
const only = process.argv.slice(2);
for (const [name, fn, w, h] of JOBS) {
  if (only.length && !only.some((s) => name.includes(s))) continue;
  const bytes = await render(name, fn(), w, h);
  console.log(`${name}.png  ${(bytes / 1024).toFixed(0)} KB`);
}
