# Subagent handoff template

The orchestrator writes everything above "Report" before dispatch, except the Agent ID and dispatch time, which it fills in right after dispatch. The subagent fills "Report" when finished, in the same file, so the orchestrator reads one place. Use `type: Subagent Handoff`.

```markdown
---
type: Subagent Handoff
title: "billing_api: invite redemption endpoint"
description: "Brief and report for one subagent."
tags: [handoff, subagent]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# billing_api

## Agent
- Name: `billing_api` (set at dispatch, matches the filename)
- Agent ID: filled by the orchestrator from the dispatch result, so the agent can be messaged or resumed
- Dispatched at: filled by the orchestrator
- Reports to: the orchestrator session

## Task
One or two sentences. What to build or find.

## Read first
Paths and URLs to read before acting. Include the plan file and spec.

## Contract
**Decided** (do not change): interfaces and rules other work depends on.
**Requested** (do this): the target files and the behavior.
**Undefined** (your call, leave a reason): what is left to judgment.

## Ownership
May write: `src/billing/**`, `tests/billing/**`
Must not touch: everything else. If a change outside is needed, stop and report it.

## Rules
- You are a leaf. Do not spawn agents.
- Do not push. Commit only when told.
- Do not weaken or delete a test to make it pass.

## Done when
Commands that must pass, for example `pnpm test billing`.

## Report
Filled by the subagent.
- Branch or commit:
- Files changed:
- Checks run (command and result):
- Known limits:
- Contract changes that affect other work:
- Questions for the orchestrator:
```
