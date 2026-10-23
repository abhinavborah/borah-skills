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

`docs/` is an OKF bundle. Use the `okf-docs` skill for any change there. Research notes go in `docs/research/`, handoffs in `docs/handoffs/` and `docs/subagent-handoffs/`.

## Working rules

- Ask before destructive or outward-facing actions: deleting, force pushing, publishing, spending credits.
- Commit in small logical groups with explicit file lists. Do not push unless asked.
- Write a handoff before the context fills up.
- Fix bugs by reproducing them first, as the user would see them.

## Which skill when

| Situation | Skill |
|---|---|
| Idea is vague, or a plan needs stress-testing | `spec-interview` |
| Need current facts, versions, prior art | `research` |
| Unsure about a design or data model | `spike` |
| Building a feature or fixing a bug | `test-first` |
| UI looks plain, cluttered or static | `better-ui` |
| Writing docs, READMEs or error text | `ste` |
| Adding or editing anything under `docs/` | `okf-docs` |
| Stopping, or handing work to another agent | `session-handoff` |
| Work splits into independent parts | `orchestrate` |
| Preparing the demo, pitch or submission | `demo-pitch` |
````
