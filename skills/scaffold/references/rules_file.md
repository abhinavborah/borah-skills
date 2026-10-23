# Project rules file template

Write to `AGENTS.md` (and a one-line `CLAUDE.md` containing `@AGENTS.md` if both are chosen), or to whichever single file was chosen. Fill the placeholders from the interview. Keep it short: it loads in every session.

````markdown
# <Project name>

<One-line idea>. Deadline: <date>. Team: <size>.

## Stack

<Chosen stack with versions, or "not chosen yet">. Run commands:

```shell
<install, dev, test, build commands once known>
```

## Docs

`docs/` is an OKF bundle. Use the `hack-kit:okf-docs` skill for any change there. Specs go in `docs/specs/`, decisions, findings and changes in `docs/journal/`, research notes in `docs/research/`, handoffs in `docs/handoffs/` and `docs/subagent-handoffs/`.

## Working rules

- Ask before destructive or outward-facing actions: deleting, force pushing, publishing, spending credits.
- Commit in small logical groups with explicit file lists. Do not push unless asked.
- Record each decision, finding, change of direction and rejected approach with `hack-kit:project-log` as it happens. Read the digest at session start.
- Write a handoff before the context fills up.
- Fix bugs by reproducing them first, as the user would see them.

## Which skill when

| Situation | Skill |
|---|---|
| Idea is vague, or a plan needs stress-testing | `hack-kit:spec-interview` |
| Need current facts, versions, prior art | `hack-kit:research` |
| Unsure about a design or data model | `hack-kit:spike` |
| Building a feature or fixing a bug | `hack-kit:test-first` |
| UI looks plain, cluttered or static | `hack-kit:better-ui` |
| Writing docs, READMEs or error text | `hack-kit:ste` |
| Adding or editing anything under `docs/` | `hack-kit:okf-docs` |
| Recording a decision, finding, change or rejected approach | `hack-kit:project-log` |
| Stopping, or handing work to another agent | `hack-kit:session-handoff` |
| Work splits into independent parts | `hack-kit:orchestrate` |
| Preparing the demo, pitch or submission | `hack-kit:demo-pitch` |
````
