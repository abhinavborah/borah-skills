# Project rules file template

Write to `AGENTS.md` (and a one-line `CLAUDE.md` containing `@AGENTS.md` if both are chosen), or to whichever single file was chosen, or to `.claude/rules/hack-kit.md` if both were declined. Fill the placeholders from the interview. Keep it short: it loads in every session.

````markdown
# <Project name>

<One-line idea>. Deadline: <date>. Team: <size>.

## Stack

<Chosen stack with versions, or "not chosen yet">. Run commands:

```shell
<install, dev, test, build commands once known>
```

## Docs

hack-kit docs home: ../<name>.docs/
hack-kit deadline: <ISO-8601 with offset, or remove this line>

`docs/` is an OKF bundle, found under the docs home above. Use the `hack-kit:okf-docs` skill for any change there. Specs go in `docs/specs/`, decisions, findings and changes in `docs/journal/`, research notes in `docs/research/`, handoffs in `docs/handoffs/` and `docs/subagent-handoffs/`.

## Working rules

- Ask before destructive or outward-facing actions: deleting, force pushing, publishing, spending credits.
- Commit in small logical groups with explicit file lists. Do not push unless asked.
- Record each decision, finding, change of direction and rejected approach with `hack-kit:project-log` as it happens. Read the digest at session start.
- When asked to record, log, note or remember a decision or its reason for this project, write a journal entry with `hack-kit:project-log`. Private memory alone is not shared project history.
- Write a handoff before the context fills up.
- Fix bugs by reproducing them first, as the user would see them.

## Which skill when

| Situation | Skill |
|---|---|
| Idea is vague, or a plan needs stress-testing | `hack-kit:spec-interview` |
| Need current facts, versions, prior art | `hack-kit:research` |
| Adding or editing anything under `docs/` | `hack-kit:okf-docs` |
| Recording a decision, finding, change or rejected approach | `hack-kit:project-log` |
| Stopping, or handing work to another agent | `hack-kit:session-handoff` |
| Work splits into independent parts | `hack-kit:orchestrate` |
| Preparing the demo or pitch | `hack-kit:demo-pitch` |
| Organizer rules to extract and recheck | `hack-kit:contract-check` |
| Labeled data and a score to report | `hack-kit:eval-harness` |
| Packaging, zipping or submitting | `hack-kit:submit-pack` |
````
