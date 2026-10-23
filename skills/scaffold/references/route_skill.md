# Project-local router skill template

Written to `.claude/skills/route/SKILL.md` in the project, only when the user declined both `CLAUDE.md` and `AGENTS.md`. That folder stays untracked.

````markdown
---
name: route
description: Pick the right hack-kit skill for the current step of this project. Use at the start of a task, when unsure which skill applies, or when switching phase between plan, build, polish and ship.
---

# Route

Load the skill that matches the situation, then follow it.

| Situation | Skill |
|---|---|
| Idea is vague, or a plan needs stress-testing | `spec-interview` |
| Need current facts, versions, prior art | `research` |
| Unsure about a design or data model | `spike` |
| Building a feature or fixing a bug | `test-first` |
| UI looks plain, cluttered or static | `better-ui` |
| Writing docs, READMEs or error text | `ste` |
| Adding or editing anything under `docs/` | `okf-docs` |
| Stopping, or handing work to another agent | `session-handoff` |
| Work splits into independent parts | `orchestrate` |
| Preparing the demo, pitch or submission | `demo-pitch` |

Docs live in `docs/` as an OKF bundle. Do not push or publish without asking.
````
