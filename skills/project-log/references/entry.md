# Journal entry examples

## Evidence strengths (findings)

`verified-by-run` (you ran it and saw it), `primary` (official docs, spec, source), `multiple` (independent sources agree), `single` (one source), `vendor` (promotional or interested party), `opinion`, `inferred` (your reasoning, not checked).

## Decision

```markdown
---
type: Journal Entry
title: "Use Postgres for storage"
description: "decision: Use Postgres for storage"
tags: [decision]
kind: decision
status: stable
confidence: high
generated: { by: agent/name, at: 2026-10-24T10:30:00Z }
---

# Use Postgres for storage

## What was decided
Store all app data in Postgres. User's choice, after the options below.

## Why
The demo needs relational queries across teams and invites, and the team already knows SQL. Hosted free tier covers the weekend.

## Alternatives considered
- SQLite: simplest, but two services write concurrently. Lost on concurrency.
- Document store: flexible, but joins are central here. Lost on query shape.

## Consequences
Needs a hosted instance and a connection string in the environment. Revisit if the free tier limits block the demo.

## Links
- [Storage options](../research/storage_options.md)
- Commit 3f2a9c1
```

## Finding

```markdown
---
type: Journal Entry
title: "Pooling removes the connection errors"
description: "finding: Pooling removes the connection errors"
tags: [finding]
kind: finding
evidence: verified-by-run
confidence: medium
generated: { by: agent/name, at: 2026-10-24T11:10:00Z }
---

# Pooling removes the connection errors

## What was found
With a pool of 10, 500 sequential requests produced no connection errors. Without it, 38 failed.

## Evidence and scope
Ran locally against the hosted instance, one client, 500 requests. Says nothing about concurrent clients or the venue network.

## Links
- [Pool spike](../research/spike_pool.md)
```

## Rejection, change, question

Same layout. A rejection states what was tried or considered, why it was dropped, and what evidence would reopen it. A change states what changed and why, with commit hashes. A question states what is unknown, what blocks on it, and what would answer it.
