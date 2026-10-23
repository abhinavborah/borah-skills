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
| Idea is vague, or a plan needs stress-testing | `hack-kit:spec-interview` |
| Need current facts, versions, prior art | `hack-kit:research` |
| Unsure about a design or data model | `hack-kit:spike` |
| Building a feature or fixing a bug | `hack-kit:test-first` |
| UI looks plain, cluttered or static | `hack-kit:better-ui` |
| Writing docs, READMEs or error text | `hack-kit:ste` |
| Adding or editing anything under `docs/` | `hack-kit:okf-docs` |
| Recording a decision, finding, change or rejected approach | `hack-kit:project-log` |
| Stopping, or handing work to another agent | `hack-kit:session-handoff` |
| Work splits into independent parts | `hack-kit:orchestrate` |
| Preparing the demo, pitch or submission | `hack-kit:demo-pitch` |

Docs live in `docs/` as an OKF bundle. Do not push or publish without asking.
````
