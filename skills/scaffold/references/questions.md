# Interview question bank

Use AskUserQuestion, at most four questions per call, two to four options each. Free text comes through the Other option. Do not proceed on an ambiguous answer. Ask again.

## Batch 1: basics

- Project name (becomes the folder, repo and docs title). Offer a derived name plus Other.
- One-line idea. Other only; offer "decide later".
- Deadline and team size. Options: solo, 2 to 3, 4 or more; deadline through Other.
- Docs home. Options: outside the repo in `../<name>.docs/` (recommended), inside the repo as `docs/`.
- Handle for authorship fields, for example `human:handle`. Offer the git user name plus Other.

## Batch 2: repository

- Create a GitHub repo? Options: yes public, yes private, no.
- Repo name, if yes. Default to the project name.
- Make an initial commit after setup? Options: yes, no.

Ask for confirmation again immediately before running `gh repo create`.

## Batch 3: agent files

- Create `CLAUDE.md`? yes or no.
- Create `AGENTS.md`? yes or no.
- If both are no: write the same rules to `.claude/rules/hack-kit.md` (loaded every session, stays untracked) so skill selection and logging still work? yes or no.

## Batch 4: stack

- How to pick the stack? Options: research it for me, I will bring my own, decide later.
- If researched: constraints such as language, hosting, database, mobile or web. Other for details.

## Batch 5: ghost mode

First ask: off, all levels, or choose levels.

If choose, a multi-select:

- `attribution`: blank commit and PR attribution in project settings.
- `untracked`: `CLAUDE.md` and `AGENTS.md` kept out of git through `.git/info/exclude`.
- `neutral-code`: no agent wording in README, source, comments, commit messages.
- `neutral-docs`: no agent wording in docs prose, and no `generated` trust field.
- `checker`: a commit-msg hook that blocks agent markers.

Tell the user that `.claude/` is always kept out of git, that handoff folders are exempt from the docs check because agents read them, and that ghost mode applies to this clone only.
