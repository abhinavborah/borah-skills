# OKF frontmatter and templates

## Concept

```markdown
---
type: Research Note
title: Short display name
description: One sentence that says what this concept holds.
tags: [topic, area]
generated: { by: human:handle, at: 2026-10-24T10:00:00Z }
---

Body. Link to related concepts like [this one](../research/other_note.md).
```

With `neutral-docs`, replace the `generated` line with `timestamp: 2026-10-24T10:00:00Z`.

## Optional families

- `sources`: where a factual concept comes from. Each entry needs `resource` (URL or path). Add `id` to cite a claim with a footnote of the same label.
- `verified`: `{ by: human:handle, at: <time> }`. Only a person confirming the content justifies a `human:` actor.
- `status`: `draft`, `stable` or `deprecated`. Absent means `stable`.
- `stale_after`: an absolute time after which the content is stale.
- `resource`: canonical URI of the thing the concept describes.

```yaml
sources:
  - id: spec
    resource: https://example.com/spec
    title: The spec
    last_modified: 2026-05-30T00:00:00Z
```

Cite a claim: `The format is plain markdown.[^spec]` then `[^spec]: The spec`.

## Index

```markdown
---
type: Bundle Index
title: research
description: Dated research notes.
tags: [index]
timestamp: 2026-10-24T10:00:00Z
---

* [Stack options](stack_options.md) - latest stable web stacks, checked 2026-10-24
```

Root index adds `okf_version: "0.2"` to the frontmatter.

## Log

```markdown
---
type: Change Log
title: research log
description: History of changes to research notes.
tags: [log]
timestamp: 2026-10-24T10:00:00Z
---

## 2026-10-24
* **Creation**: Added [Stack options](stack_options.md).
```
