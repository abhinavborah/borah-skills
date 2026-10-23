# Spec template

Use `type: Spec`. Frontmatter rules come from the `okf-docs` skill. Requirement IDs are stable: add new ones, never renumber.

````markdown
---
type: Spec
title: "Invite flow"
description: "What the invite flow must do and how to check it."
tags: [spec]
status: draft
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# Invite flow

## Objective
One paragraph: the problem, who has it, why it matters now.

## Demo flow
The single flow a user or judge will see, in 3 to 6 steps.

## Requirements

### REQ-001: Redeem an invite
The system MUST create the user when a valid invite code is redeemed.
Acceptance: given an unused code, when the user submits it, then an account exists and the response is 201.

### REQ-002: ...

## Edge cases

### EDGE-001: Used code
Redeeming a used code MUST fail without creating an account.
Acceptance: given a used code, when submitted, then the response is 409 and no account is created.

## Out of scope
- Explicit non-goals.

## Open questions
- Anything unresolved, with who can answer.

## Definition of done
- [ ] Every acceptance check above passes.
- [ ] The demo flow runs end to end.
- [ ] Nothing outside the requirements was built.
````

## Writing acceptance checks

- Given, when, then. All three filled.
- The "then" names something a test can observe: a status code, a file, a row, a visible text.
- One behavior per check. If the "then" needs "and" between unrelated outcomes, split it.
- Replace adjectives with measures, or delete them. "Quickly" becomes "within 2 seconds".
- Describe behavior, not implementation. "Uses SQLite" is a decision for the build.
- Cover the success case, its boundaries, how it fails, and any constraint such as speed or permission. One check per answer that exists.
