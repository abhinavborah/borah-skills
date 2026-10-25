# Contract template

Use `type: Contract`. Frontmatter rules come from the `okf-docs` skill.

````markdown
---
type: Contract
title: "Contest rules contract"
description: "Numbered MUST and SHOULD rules from the organizer documents, with status and proof."
tags: [contract, rules]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# Contest rules contract

Deadline: 2026-10-26T18:00:00+05:30 (source: problem_statement.md, Timeline)

| id | level | source | rule | status | proof |
|---|---|---|---|---|---|
| C-001 | MUST | problem_statement.md, Output | output.csv has columns `case_id,deletion_status,steps_json` in that order | met | `python3 check_output.py` passes |
| C-002 | MUST | AGENTS.md, 6.7 | read secrets from environment variables only | open | |
| C-003 | SHOULD | README.md, Judging | include setup and run instructions | waived | user said skip, 2026-10-24 |

## Conflicts
- C-004: AGENTS.md says the report goes to `evaluation/report.md`. README says `report/summary.md`. Decision: pending.
````

Status values: `open`, `met`, `waived`, `conflict`. A `waived` row needs the user's reason in the proof column.
