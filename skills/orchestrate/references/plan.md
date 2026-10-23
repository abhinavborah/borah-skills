# Orchestration plan template

Use `type: Orchestration Plan`. Frontmatter rules come from the `okf-docs` skill.

````markdown
---
type: Orchestration Plan
title: "Invite flow: three packets"
description: "Boundary contract, ownership and checks for parallel work on the invite flow."
tags: [plan, orchestration]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

# Invite flow: three packets

## Boundary contract
`POST /api/invites/redeem` returns `201 {userId, teamId}`, `409 {code: "invite_used"}`, or `422 {fieldErrors}`.

## Packets
| Packet | May write | Reads as authority | Waits for |
|---|---|---|---|
| api | `src/api/invites/**`, `tests/api/**` | contract above | nothing |
| form | `src/web/signup/**` | contract above | nothing |
| docs | `docs/guides/invites.md` | merged behavior | api, form |

## Shared files
`openapi.yaml` is owned by api. Others send change requests through their Report.

## Checks
- api: `pnpm test api`
- form: `pnpm test web`

## Release boundary
The user decides on push, merge to main, and publish.

```json ownership
{"packets": {
  "api":  {"may_write": ["src/api/invites/**", "tests/api/**"]},
  "form": {"may_write": ["src/web/signup/**"]},
  "docs": {"may_write": ["docs/guides/invites.md"]}
}}
```
````
