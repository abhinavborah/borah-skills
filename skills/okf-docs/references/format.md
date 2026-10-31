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

With `neutral-docs`, replace the `generated` line with `timestamp: 2026-10-24T10:00:00Z`. The validator notes that `timestamp` is the older v0.1 field, which v0.2 consumers still accept. Quote `by` if it holds a comma, for example `by: "human:a, b"`.

## Optional families

- `sources`: where a factual concept comes from. Each entry needs `resource` (URL or path). Add `id` to cite a claim with a footnote of the same label.
- `verified`: `{ by: human:handle, at: <time> }`. Only a person confirming the content justifies a `human:` actor.
- Actors: `human:<handle>` for a person, `<producer>/<version>` for an agent or tool, `process:<id>` for an automated run.
- `status`: `draft`, `stable` or `deprecated`. Absent means `stable`.
- `stale_after`: an absolute time after which the content is stale.
- `resource`: canonical URI of the thing the concept describes.
- `commit`: the git commit of the code a concept describes. A producer extension the spec allows. Pair it with `path:line` refs, and run the validator with `--repo` to flag cited files that changed since.

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

<!-- okf-index:start -->
* [Stack options](stack_options.md) - Latest stable web stacks, checked 2026-10-24.
<!-- okf-index:end -->
```

`build_index.py` owns the block between the markers and fills it from each concept's `title` and `description`. Text outside the markers stays. Root index adds `okf_version: "0.2"` to the frontmatter and this line above the block: "If this bundle and the code disagree, follow the code and report the mismatch."

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
