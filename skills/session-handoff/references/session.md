# Session handoff template

Frontmatter follows the `okf-docs` skill. Use `type: Handoff`. Title states the state in a phrase, not "handoff".

```markdown
---
type: Handoff
title: "Auth flow done, billing next"
description: "State, next task and open items after the auth session."
tags: [handoff]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# Auth flow done, billing next

Written 2026-10-24T10:00:00Z. Read this first. Delta over [the previous handoff](./handoff_2026_10_23_220000.md). Verify claims against disk and git.

## 1. State
One paragraph: what the project is, where it stands, what is blocked.

## 2. Next task
What the user agreed, or "not yet assigned" with ranked candidates and an instruction to ask.

## 3. What happened
Findings and decisions. Tag each: (user choice) or (agent proposal).

## 4. Files and where to look
| Path | What it holds |
|---|---|

## 5. Open items and unverified claims
Questions, sources not yet read, anything to check before relying on it.

## 6. Preferences that bind the work
Tone, style and process rules the user stated.

## 7. Tools, plugins and skills
What worked, what failed (shortest decisive error), the order to try them, and skills the next agent should load.

## 8. Git state
Branch, last commit, what is pushed, what is not.

## 9. Links
Repo and source URLs, specs, issues.
```

Keep sections that are empty as "none" so the reader knows they were checked.
