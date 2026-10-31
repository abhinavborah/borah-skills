---
name: okf-docs
description: Write, update and validate the docs/ folder as an OKF v0.2 bundle (concept files with frontmatter, index.md, log.md). Use when adding or editing any file under docs/, syncing indexes and logs, or checking bundle conformance. Not for session handoffs (use session-handoff).
---

# OKF docs

OKF v0.2 is a directory of markdown files. One concept per file, YAML frontmatter on top, relative links between files. Spec: https://github.com/GoogleCloudPlatform/open-knowledge-format

This skill owns the docs format. Other skills call it and do not restate these rules.

## Convention

- Filenames are `snake_case.md`. `index.md` and `log.md` are reserved.
- Every concept has `type` (required), `title`, `description`, `tags`, plus one time field.
- Time field, by ghost setting:
  - If `$(git rev-parse --path-format=absolute --git-common-dir)/ghost/ghost.json` lists `neutral-docs`, write `timestamp`.
  - Otherwise write `generated: { by: <actor>, at: <time> }`. Actor is `human:<handle>` for a person, `<producer>/<version>` for an agent, `process:<id>` for an automated run.
- Times are UTC with a suffix: `date -u +%Y-%m-%dT%H:%M:%SZ`. Never invent one.
- `index.md` and `log.md` carry frontmatter too (`type: Bundle Index`, `type: Change Log`). The root `index.md` also has `okf_version: "0.2"`. This extends the spec on purpose.
- Log headings are `## YYYY-MM-DD`, newest first, entries as `* **Creation**: ...` or `* **Update**: ...`.
- Link with file-relative markdown links to `.md` files. Never start a link with `/`. Link a concept once per section, and not from headings or code blocks.
- Factual notes cite sources in frontmatter. See [references/format.md](references/format.md).

## Add or change a concept

1. Pick the directory and a `snake_case` name. Read the file first if it exists.
2. Write frontmatter and body from the template in [references/format.md](references/format.md).
3. Rebuild the indexes. Entries come from each concept's `title` and `description`, so do not edit the link list by hand:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/build_index.py" docs
```

4. Prepend a dated entry to that directory's `log.md`.
5. Run the validator. Add `--repo <repo>` when concepts cite code, to check cited paths and drift since `commit`:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/okf_validate.py" docs
```

Fix every ERROR. Fix WARNINGs unless there is a reason. Add `--strict` to fail on warnings. In CI, `build_index.py --check docs` fails when an index is out of date.

## Docs home

Every `docs/...` path in this plugin is relative to the docs home, which holds the `docs/` bundle. It is not always the repo. Resolve it in this order:

1. A line `hack-kit docs home: <path>` in the project rules file (`CLAUDE.md`, `AGENTS.md` or `.claude/rules/hack-kit.md`).
2. Default: `../<repo-name>.docs/`, a sibling folder outside git. The bundle is then `../<repo-name>.docs/docs/`.

The docs home may be the repo root only after the user says yes. Ask with AskUserQuestion before the first write into a tree git tracks, and write the answer into the rules file. Never write handoffs, journal entries or research notes into a tracked tree on your own. Scripts take `--root <docs home>`. Run validators from the docs home.

## New folder

When a skill writes into a folder that has no `log.md`, create it first (type `Change Log`). Then run `build_index.py`: it creates a missing `index.md` (type `Bundle Index`) and lists the folder in its parent index. A concept at the `docs/` root, such as `pitch.md`, goes in the root `index.md`.

## What to write

Context files help an agent only when they hold what the code and sources do not show. Restating readable code adds cost, not accuracy.

- Write intent, contracts, decisions, hazards, external systems and procedures. Point to code by path and symbol instead of restating it.
- Phrase rules as constraints: "Do not run X without approval" rather than "Be careful with X".
- Do not invent facts, fields, numbers or links. Mark what is unverified.
- Keep provenance in the `sources` frontmatter, not a `# Citations` section.
- Keep `description` to one sentence. It is reused in `index.md`.
- Write for a reader who never saw this session. No talk of leads, teammates or swarms.
- Keep concepts under 250 lines and folders at most two levels deep. Split instead.

## Freshness

A stale instruction wins over the code it once described, so mark what can go stale.

- A concept that describes code carries `commit: <sha>` of the code it read. Prefer symbol names to line numbers. Line numbers without `commit` get a warning.
- Time-bound content carries `stale_after`. The validator warns once it passes.
- The root `index.md` holds this line: "If this bundle and the code disagree, follow the code and report the mismatch." `build_index.py` writes it when it creates the root index.

To test whether a bundle actually helps agents, follow [references/effectiveness_test.md](references/effectiveness_test.md).

## Rules

- Do not put concept content in `index.md`. It holds links and one-line hooks.
- Match the `type` names already used in the bundle. Otherwise choose a plain one: `Research Note`, `Handoff`, `Decision`, `Bundle Index`, `Change Log`.
- Never overwrite a concept you did not read first.
- Do not claim a concept is `verified` unless a person confirmed it.
