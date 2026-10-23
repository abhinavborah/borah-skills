# Research note template

Use `type: Research Note`. Frontmatter rules come from the `okf-docs` skill.

```markdown
---
type: Research Note
title: "Web stack options, October 2026"
description: "Latest stable web stacks for a two-day build, checked 2026-10-24."
tags: [research, stack]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
sources:
  - id: nextjs-releases
    resource: https://github.com/vercel/next.js/releases
    title: Next.js releases
    last_modified: 2026-10-20T00:00:00Z
---

# Web stack options, October 2026

## Question
What was asked, and what decision it feeds.

## Findings
Claims with their strength in brackets, cited by footnote.
- Next.js 16.x is the current stable line. [primary][^nextjs-releases]

## Recommendation
Options ranked, with the reason for the top one. Say what would change the ranking.

## Caveats
Single-source claims, vendor posts, anything older than a year, license limits.

## Tool log
| Tool | Status | Note |
|---|---|---|
| firecrawl | ok | search with highlights |
| exa | failed | shortest error line |

Checked on 2026-10-24.

[^nextjs-releases]: Next.js releases
```
