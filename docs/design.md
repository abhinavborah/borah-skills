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
- Selection is made explicit in the project: a routing table in the project rules file, or a project-local router skill when that file is declined. The table points at skills by name.
- Only `scaffold` sets `disable-model-invocation: true`. That flag also blocks preloading into subagents, and a router table cannot call a skill the model may not load. Every other skill stays loadable.

## Composition

- One skill owns each contract. `okf` owns the docs format and its validator. `handoff`, `research` and `scaffold` call the validator through `${CLAUDE_SKILL_DIR}/../okf/scripts/` and do not restate the rules.
- Skills compose by instruction ("run the `okf` skill"), not by copied text. Duplicated rules drift.
- `orchestrate` plans and asks before it spawns. Subagents are leaves: they never spawn. Concurrent subagents are capped at 5.

## Quality gates

- Skills are written against failures, not imagined needs: observe the gap, write the minimum, test on a fresh session ([authoring guide](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), [Authoring Agent Skills, 2026-07](https://arxiv.org/html/2607.25032v1)).
- Over 99% of surveyed `SKILL.md` files carry at least one authoring smell ([From Anatomy to Smells, 2026-07](https://www.alphaxiv.org/abs/2607.01456)), so `scripts/lint.py` runs before every commit.
- Each skill ships `evals/evals.json` with at least two prompts that should trigger it and two near misses that should not.

## Ghost mode

Ghost mode removes agent traces from a project. It is a set of independent levels, chosen by the user at scaffold time, either all or a selected few:

| Level | Effect |
|---|---|
| `attribution` | blank commit and pull request attribution in project settings |
| `untracked` | agent folders and rule files excluded through `.git/info/exclude`, never `.gitignore` |
| `neutral-code` | README, source, comments, commit messages and PR text carry no agent wording |
| `neutral-docs` | docs prose carries none either; trust fields such as `generated` are omitted |
| `checker` | a deterministic script scans tracked files and commit messages |

The chosen levels are stored in an untracked local file, and the checker reads it. Ghost mode applies per clone.
