# Skill system design

How the skills in this plugin are structured, and the evidence behind each rule. Research dated 2026-10-24.

## Loading model

Three tiers, each with a cost ([Anthropic engineering post](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), 2025-10-16):

| Tier | Content | Loaded | Limit |
|---|---|---|---|
| 1 | `name` + `description` (+ `when_to_use`) | always, for every installed skill | 1,536 characters combined ([skills docs](https://code.claude.com/docs/en/skills.md)) |
| 2 | `SKILL.md` body | when the skill triggers | under 500 lines ([authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)) |
| 3 | `references/`, `scripts/`, `templates/` | on demand | none |

Rules that follow:

- The body is an index. Depth goes in `references/`, linked straight from `SKILL.md`, never from another reference.
- Deterministic work is a script, run and not read. Output costs tokens, source does not.
- Match freedom to fragility: prose for judgment calls, parameterized scripts for preferred patterns, exact commands for fragile steps.

## Selection

Selection reads only tier 1, and it degrades as the library grows. With 1,000 irrelevant skills installed, loaded-skill recall fell from 73.6% to 27.4%, while explicit selection from the same library held at 73.9% ([Lost in Implicit Routing, 2026-10](https://www.alphaxiv.org/abs/2610.18522)). Similar skills installed together also displace each other, and install location decides the winner ([One Skill Too Many, 2026-10](https://www.alphaxiv.org/abs/2610.11647)).

Rules that follow:

- Descriptions name concrete triggers and a boundary ("not for X, use Y"). Overlapping pairs get distinct verbs.
- Selection is made explicit in the project: a routing table in the project rules file, or in `.claude/rules/hack-kit.md` when the user declines `CLAUDE.md` and `AGENTS.md`. Rules files without path scopes load at the start of every session, and `.claude/` stays untracked. The table points at skills by name.
- The skill listing always keeps every name but drops descriptions when it exceeds its budget (1% of the context window by default), least-used skills first ([skills docs](https://code.claude.com/docs/en/skills.md), troubleshooting). In a test session with many skills installed, only one hack-kit description survived and the rest were matched by name. So names must say what the skill does, and the key use case goes first in every description. Users with large libraries can raise `skillListingBudgetFraction`.
- Only `scaffold` sets `disable-model-invocation: true`. That flag also blocks preloading into subagents, and a router table cannot call a skill the model may not load. Every other skill stays loadable.

## Composition

- One skill owns each contract. `okf-docs` owns the docs format and its validator. `session-handoff`, `research` and `scaffold` call the validator through `${CLAUDE_SKILL_DIR}/../okf-docs/scripts/` and do not restate the rules. `ste` owns writing style and is called, not restated.
- Skills compose by instruction ("run the `okf-docs` skill"), not by copied text. Duplicated rules drift.
- Merge two skills when they share a core loop and produce the same kind of artifact. Split them when the procedure differs, even if the triggers sound alike. `spec-interview` covers drafting and stress-testing, `test-first` covers new features and bug fixes, and `better-ui` carries motion as a reference file.
- A skill whose job duplicates a skill the user may already have installed gets a distinct name, because the model chooses between similar skills by name and description alone.
- `orchestrate` plans and asks before it spawns. Subagents are leaves: they never spawn. Concurrent subagents are capped at 5.

## Quality gates

- Skills are written against failures, not imagined needs: observe the gap, write the minimum, test on a fresh session ([authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [Authoring Agent Skills, 2026-07](https://arxiv.org/html/2607.25032v1)).
- Over 99% of surveyed `SKILL.md` files carry at least one authoring smell ([From Anatomy to Smells, 2026-07](https://www.alphaxiv.org/abs/2607.01456)), so `scripts/lint.py` runs before every commit.
- Each skill ships `evals/evals.json` with two prompts that should trigger it and two near misses that should not. These files document intended triggers. They are not yet runnable: the native runner (`claude plugin eval`) expects `case.yaml` or `prompt.md` plus `graders/`, so converting them is future work.

## Ghost mode

Ghost mode removes agent traces from a project. It is a set of independent levels, chosen by the user at scaffold time, either all or a selected few:

| Level | Effect |
|---|---|
| `attribution` | blank commit and pull request attribution in project settings |
| `untracked` | agent folders and rule files excluded through `.git/info/exclude`, never `.gitignore` |
| `neutral-code` | README, source, comments, commit messages and PR text carry no agent wording |
| `neutral-docs` | docs prose carries none either; trust fields such as `generated` are omitted |
| `checker` | a deterministic script scans tracked files and commit messages |

The script and the chosen levels live in the git common directory, so linked worktrees used by subagents share them and nothing new is tracked. Ghost mode applies per clone. Project settings such as `attribution` do not reach a worktree: in a test on 2026-10-24 a commit from a linked worktree still carried a co-author trailer although the main checkout's project settings blanked it, while a commit from the main checkout did not. The `checker` hook, whose script lives in the common dir, is therefore the real backstop in worktrees, and subagent briefs tell the agent to leave such lines out.

## Journal

`docs/journal/` records why things happened: decisions, findings, changes, rejected approaches and open questions, one file per entry. Git keeps what changed. Research dated 2026-10-24.

Model, from decision-record practice ([Fowler, 2026-03](https://www.martinfowler.com/bliki/ArchitectureDecisionRecord.html), [Azure Well-Architected, 2026-04](https://learn.microsoft.com/en-us/azure/well-architected/architect-role/architecture-decision-record), [AWS guidance](https://docs.aws.amazon.com/pdfs/prescriptive-guidance/latest/architectural-decision-records/architectural-decision-records.pdf), [MADR](https://adr.github.io/madr/)) and the progress-journal pattern ([Hexlet](https://mokevnin.github.io/agentic-coding-design-patterns/en/progress-file.html)):

- One decision per entry, with context, the reason, alternatives and consequences.
- Accepted entries are never edited. A new entry supersedes the old one, and both link to each other. In OKF terms, `draft` is proposed, `stable` is accepted and `deprecated` is superseded.
- Entries are named by timestamp, not by sequence number, so parallel subagents cannot collide on the next number.
- Findings carry an evidence strength and a scope, because agents can carry forward a conclusion that its evidence does not support ([From Experiments to Decisions, 2026-09](https://www.alphaxiv.org/abs/2609.13299)).
- Reading goes through a digest of active decisions, so superseded entries and old noise do not bloat context.

Trigger, from Anthropic's guidance ([memory docs](https://code.claude.com/docs/en/memory.md), [steering article, 2026-06](https://claude.com/resources/articles/steering-claude-code-skills-hooks-rules-subagents-and-more)): instructions and skills are context, and a model can skip them in a long session or under pressure. Anything that must happen at a fixed point belongs in a hook. But a hook cannot write the reason, which needs judgment. So the design layers two parts:

1. The `project-log` skill and a line in the project rules file make the model write entries when a decision, finding or rejection happens.
2. A plugin `PostToolUse` hook on `git commit` is the backstop. It adds a one-line reminder when a commit carries no entry and none was written in the last 20 minutes. It is silent in projects without `docs/journal/`, adds nothing to the repository, and also runs inside subagents.

The hook only nudges. It never writes content itself, because an auto-written reason would be unsourced text stored as memory. A field report on file-based agent memory ([claude-code#68546](https://github.com/anthropics/claude-code/issues/68546)) found the same failure.

Observed on 2026-10-24 in headless sessions with the plugin loaded (five runs, so a signal and not a measurement). The prompt asked the model to record a decision:

| Setup | Result |
|---|---|
| No rules file, first description | Saved to the model's private memory. The journal was not touched. |
| Rules file with a journal line | Wrote a valid journal entry and stated that the claim had no evidence beyond the user's word. |
| No rules file, reworded description, "Record this." | Wrote a journal entry. |
| No rules file, reworded description, "make sure we remember why" | Saved to private memory again. |
| Rules in `.claude/rules/hack-kit.md` only, same "remember why" wording | Wrote a valid journal entry. |

The model's own memory feature competes with the skill for any request phrased as "remember". The rules file line is therefore required for dependable logging, and it names that phrasing directly. The commit hook stays as a second layer.
