# Demo script template

Use `type: Pitch Plan`. Frontmatter rules come from the `okf-docs` skill.

````markdown
---
type: Pitch Plan
title: "Demo and pitch plan"
description: "Timed demo script, fallback and rehearsal notes."
tags: [pitch]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# Demo and pitch plan

## Constraints
Time limit: 3 minutes demo, 2 minutes questions.
Judging criteria: (pasted from the rules)
Submission limits: (field names and lengths)

## One-sentence problem
Who feels it, and why it hurts.

## Script
| Time | Say | Show | Owner |
|---|---|---|---|
| 0:00 | The problem in one sentence. | Title screen | A |
| 0:20 | What we built, one line. | Landing screen | A |
| 0:30 | Walk through the flow as the user. | Step 1 of the flow | B |
| 1:30 | The key moment: before versus after. | Result screen | B |
| 2:15 | What works, what does not yet, what is next. | Roadmap line | A |
| 2:45 | Close: the problem solved, the ask. | Title screen | A |

## Risk list
| Risk | Prevention | Fallback |
|---|---|---|
| Network fails | Cache the API responses | Play the recorded video |
| Login screen stalls | Pre-authenticated session | Reset script restores it |

## Cut list
Features hidden or not mentioned, so the flow stays short.

## Likely questions
Question, short honest answer.

## Submission text
Title, tagline, problem, what it does, how it was built, challenges, what is next, links.

## Rehearsal log
| Run | Time | Notes |
|---|---|---|
````
