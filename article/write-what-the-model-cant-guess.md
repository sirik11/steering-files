# Write What the Model Can't Guess

*Every coding agent now reads a steering file before it touches your code. The research says most of what we put in them doesn't help, and makes every task cost more.*

![Cover image reading "Write what the model can't guess" beside a printed AGENTS.md marked up in red pen: the project structure, tech stack, and architecture lines are struck through with a note that the agent can already read this, and three conventions are highlighted and bracketed with the note keep only these.](../figures/cover-write-what-the-model-cant-guess.png)

Open almost any active repository in 2026 and you'll find one: a markdown file that tells the coding agent how to behave. Kiro calls them [steering files](https://kiro.dev/docs/steering/). Claude Code reads a [CLAUDE.md](https://code.claude.com/docs/en/memory). Cursor has [project rules](https://cursor.com/docs/context/rules), Copilot has [repository custom instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions), and the cross-tool format [AGENTS.md is used by over 60,000 open-source projects](https://agents.md/).

We write them because we've watched an agent make the same mistake twice. So we add a line. Then another. The file grows, it gets committed, and nobody looks at it again until something breaks.

Over the past year, three independent research groups measured what these files actually do. Their results should change what you put in yours.

## What is a steering file, really?

Every tool implements the same idea: a file the agent reads at the start of a session, before it sees your task. The names differ. The mechanics have converged.

![Matrix comparing five tools across four columns: always loaded, loaded when matching files are touched, loaded when the agent decides it is relevant, and loaded when you ask. Kiro fills all four with inclusion always, fileMatch, auto, and manual. Claude Code uses CLAUDE.md, rules with paths, and skills. Cursor uses alwaysApply, globs, description, and at-mentions. Copilot uses copilot-instructions.md and applyTo. AGENTS.md uses a root file and nested files by directory.](../figures/fig1-same-four-dials.png)

Underneath the branding, the tools now offer the same dials: instructions that load **always**, instructions that load **only when the agent touches matching files**, and instructions that load **only when they're relevant or requested**. Kiro exposes all of them as four [inclusion modes](https://kiro.dev/docs/steering/): `always`, `fileMatch`, `auto`, and `manual`. Cursor encodes the same choices in `alwaysApply`, `globs`, and `description`. Claude Code scopes rules with a [`paths` field](https://code.claude.com/docs/en/memory); Copilot uses [`applyTo`](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions).

One line in [Anthropic's documentation](https://code.claude.com/docs/en/memory) is worth reading slowly, because it holds for every tool: Claude treats these files "as context, not enforced configuration." A steering file is something the model reads and weighs. It is not a rule the system enforces. Hold onto that; it decides what belongs in the file.

## Do steering files actually make agents better?

Nobody had tested this rigorously until February, when researchers at [ETH Zurich and LogicStar.ai](https://arxiv.org/abs/2602.11988) ran coding agents with and without context files, on SWE-bench tasks and on a new set of issues from repositories that already had developer-written AGENTS.md files.

The authors call their result surprising: providing context files "does not generally improve task success rates, while increasing inference cost by over 20% on average." It held across different models, different agents, and for both machine-generated and human-written files.

The detail that matters most is the next sentence. The agents *did* follow the instructions. Compliance wasn't the problem. The instructions simply weren't the kind that change outcomes. In particular, repository overviews, "although popular and recommended by model providers, are not helpful."

Read that against Kiro's defaults. When you set up steering, Kiro generates three [foundation files](https://kiro.dev/docs/steering/): `product.md` for your product's purpose, `tech.md` for your stack, and `structure.md` for your file layout. That is a repository overview, split into three files and loaded into every interaction by default.

That doesn't make Kiro wrong. Those files are a sensible starting point and a genuinely useful onboarding document for humans. But the research says that, as steering, an overview mostly spends tokens restating what the agent could read from the code itself.

## So what are we actually writing in them?

A separate team analyzed [2,303 context files from 1,925 repositories](https://arxiv.org/abs/2511.12884). They found these files "evolve like configuration code through frequent, small additions," which will sound familiar to anyone who maintains one. They also counted what's inside.

![Horizontal bar chart of how often five kinds of content appear in 2,303 agent context files. Test procedures 75.9 percent, implementation details 70.8 percent, architecture 68.1 percent, security 14.8 percent, performance 14.5 percent. A callout notes that overview content is the kind a controlled study found does not help, while the rarely written guardrails are what keep agent code safe and fast.](../figures/fig2-what-we-write.png)

Test procedures appear in 75.9% of files, implementation details in 70.8%, architecture in 68.1%. Security shows up in 14.8%. Performance, 14.5%.

Put the two studies side by side and the pattern is uncomfortable. The content we write most often, how the code is organized, overlaps heavily with the content the controlled study found doesn't help. The guardrails that would keep agent-written code secure and fast are what we almost never write.

## Does the structure of the file matter?

Practitioners trade a lot of advice here: keep it short, put critical rules at the top, split it into modules, eliminate contradictions. In May, a [factorial study](https://arxiv.org/abs/2605.10039) tested four of those variables (file size, instruction position, file architecture, and contradictions between files) across 1,650 Claude Code sessions.

None of them produced a detectable difference in compliance after correcting for multiple comparisons.

What did move compliance was session length. Each additional function the agent wrote was associated with about 5.6% lower odds of following the instruction. The author is careful to say this emerged during analysis rather than being planned, and that it isn't a steady decline. The study also measured a single, deliberately simple instruction, so I wouldn't treat it as the last word. But it points somewhere useful: how long you let a session run may matter more than how you lay out the file.

That doesn't make size irrelevant. Anthropic still recommends keeping a CLAUDE.md [under 200 lines](https://code.claude.com/docs/en/memory) and Cursor suggests [under 500](https://cursor.com/docs/context/rules), because every line is paid for in context on every task. Size may not change adherence. It certainly changes cost.

## What should go in a steering file?

The ETH authors reach one positive conclusion: context files "are useful for specifying non-standard coding practices." That's the whole design principle. Write what the model can't guess.

![Decision flow titled Every line, four questions, answered in order and stopping at the first yes. First, could the agent work it out from the code? Cut it. Second, would breaking it cause real damage? Enforce it with a hook, permission rule, or CI check instead. Third, does it only apply to part of the codebase? Scope it with fileMatch, paths, globs, or applyTo. Otherwise, it is a convention the model cannot infer, so keep it as always-on steering.](../figures/fig3-four-questions.png)

Run every line through four questions, in order.

**Could the agent work this out from the code?** Cut it. Your directory layout, dependency list, and framework are all in the repository already. Anthropic's own [`/doctor` check](https://code.claude.com/docs/en/memory) now proposes trimming exactly this: it "cuts content Claude can derive from the codebase, such as directory layouts, dependency lists, and architecture overviews, and keeps pitfalls, rationale, and conventions that differ from tool defaults." The tool vendor and the research landed in the same place.

**Would breaking it cause real damage?** Then it doesn't belong in a steering file. More on that below.

**Does it only apply to part of the codebase?** Scope it. This is where Kiro's `fileMatch` mode earns its place: a rule about your API error format should load when the agent touches `api/**`, not when it edits a README. Every major tool now supports some form of scoping. Most steering files I see don't use it.

**Otherwise, keep it.** What survives is the short list of conventions that differ from the default: "money is integer cents, never floats," "use pnpm, not npm," "the payments client is only called from `billing/`." These are the lines that change an agent's output, because nothing in the code would have told it.

## When is a steering file the wrong tool?

Remember that the model weighs a steering file; nothing enforces it. That's fine for style. It is not fine for "never run migrations against production" or "never commit credentials."

![Two panels. On the left, a steering file drawn as a sticky note reading please use pnpm, not npm, and money is integer cents: the model reads it, weighs it, and decides. This covers CLAUDE.md, AGENTS.md, .kiro/steering, scoped rules, skills, and mentions. On the right, a hook drawn as a padlock labeled no migrations against production: it runs no matter what the model decides, as a PreToolUse hook, permission deny rule, or CI check. Caption: preferences go on the note, must-nevers go behind the lock.](../figures/fig4-suggestion-vs-guarantee.png)

For anything that must hold, use a mechanism that doesn't depend on the model's judgment. Claude Code's documentation is direct: to block an action regardless of what Claude decides, use a [hook](https://code.claude.com/docs/en/memory), which runs as a shell command at fixed points in the session. Permission rules and CI checks work the same way.

This is also the right answer to the research gap. The study found security guidance in under 15% of files. The fix isn't to write more security paragraphs into AGENTS.md. It's to put security guarantees somewhere they're enforced, and keep the steering file for conventions you merely prefer.

## How do you know yours is working?

Treat it like the code it has become. Review changes to it in pull requests. Delete rules your team no longer follows; an outdated steering file is worse than none, because the agent believes it. In Claude Code, [`/doctor prompt-audit`](https://code.claude.com/docs/en/memory) will flag instructions that contradict each other or point to files that no longer exist.

Then measure it. The ETH paper's closing line is the most useful advice in this piece: "any attempts to improve performance should be rigorously evaluated before deployment." Pick a task your team does often. Run it with your steering file and without it. Compare the result, and compare the bill. If the file doesn't change the outcome, it isn't steering anything. It's just expensive.

I wrote a small, dependency-free [linter that flags the patterns above](https://github.com/sirik11/steering-files): overview content the agent can derive, missing security and performance guidance, unscoped rules, likely secrets, and the context each file costs on every task. When I ran it against steering files from a few large open-source projects, the biggest was 527 lines, its first section was a codebase overview with a directory tree, and it put roughly 7,000 tokens into the context of every task before the agent read a line of code. The linter is a starting point for review, not a substitute for the measurement.

## The filename was never the point

We've spent a year arguing over which file to use. The research suggests that was the wrong argument. AGENTS.md, CLAUDE.md, and `.kiro/steering/` all work the same way: they help when they carry what the model can't infer, and they cost you when they carry what it can.

Your agent already knows how to write code. What it doesn't know is how *your team* writes code. Write that down, scope it to where it applies, and enforce what can't be left to judgment.

Write what the model can't guess.

## Sources

- [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988), Gloaguen et al., ETH Zurich and LogicStar.ai, February 2026
- [Agent READMEs: An Empirical Study of Context Files for Agentic Coding](https://arxiv.org/abs/2511.12884), Chatlatanagulchai et al., November 2025
- [Instruction Adherence in Coding Agent Configuration Files: A Factorial Study of Four File-Structure Variables](https://arxiv.org/abs/2605.10039), McMillan, May 2026
- [Kiro documentation: Steering](https://kiro.dev/docs/steering/)
- [Claude Code documentation: How Claude remembers your project](https://code.claude.com/docs/en/memory)
- [Cursor documentation: Rules](https://cursor.com/docs/context/rules)
- [GitHub Docs: Adding repository custom instructions for GitHub Copilot](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)
- [AGENTS.md](https://agents.md/)
