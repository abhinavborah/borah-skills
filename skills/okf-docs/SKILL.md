---
name: okf-docs
description: Write, update and validate the docs/ folder as an OKF v0.2 bundle (concept files with frontmatter, index.md, log.md). Use when adding or editing any file under docs/, syncing indexes and logs, or checking bundle conformance. Not for prose style (use ste) or session handoffs (use session-handoff).
---

# OKF docs

OKF v0.2 is a directory of markdown files. One concept per file, YAML frontmatter on top, relative links between files. Spec: https://github.com/GoogleCloudPlatform/open-knowledge-format

This skill owns the docs format. Other skills call it and do not restate these rules.

## Convention

- Filenames are `snake_case.md`. `index.md` and `log.md` are reserved.
- Every concept has `type` (required), `title`, `description`, `tags`, plus one time field.
- Time field, by ghost setting:
  - If `$(git rev-parse --path-format=absolute --git-common-dir)/ghost/ghost.json` lists `neutral-docs`, write `timestamp`.
  - Otherwise write `generated: { by: <actor>, at: <time> }`. Actor is `human:<handle>` for a person, `<producer>/<version>` for an agent.
- Times are UTC with a suffix: `date -u +%Y-%m-%dT%H:%M:%SZ`. Never invent one.
- `index.md` and `log.md` carry frontmatter too (`type: Bundle Index`, `type: Change Log`). The root `index.md` also has `okf_version: "0.2"`. This extends the spec on purpose.
- Log headings are `## YYYY-MM-DD`, newest first, entries as `* **Creation**: ...` or `* **Update**: ...`.
- Link with relative markdown links to `.md` files. A link is a graph edge, so link liberally.
- Factual notes cite sources in frontmatter. See [references/format.md](references/format.md).

## Add or change a concept

1. Pick the directory and a `snake_case` name. Read the file first if it exists.
2. Write frontmatter and body from the template in [references/format.md](references/format.md).
3. Add or update one line in that directory's `index.md`: `* [Title](file.md) - description`.
4. Prepend a dated entry to that directory's `log.md`.
5. Run the validator:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/okf_validate.py" docs
```

Fix every ERROR. Fix WARNINGs unless there is a reason. Add `--strict` to fail on warnings.

## New folder

When a skill writes into a folder that has no `index.md` and `log.md`, create both first (types `Bundle Index` and `Change Log`) and add a line for the folder to the parent `index.md`. A concept at the `docs/` root, such as `pitch.md`, goes in the root `index.md`.

## Rules

- Do not put concept content in `index.md`. It holds links and one-line hooks.
- Match the `type` names already used in the bundle. Otherwise choose a plain one: `Research Note`, `Handoff`, `Decision`, `Bundle Index`, `Change Log`.
- Never overwrite a concept you did not read first.
- Do not claim a concept is `verified` unless a person confirmed it.
