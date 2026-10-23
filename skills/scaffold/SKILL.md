---
name: scaffold
description: Opt-in setup of a hackathon project. Creates the git repo, a docs/ OKF bundle, optional CLAUDE.md or AGENTS.md, a researched stack, an optional GitHub repo, and optional ghost mode. Runs only when the user types /hack-kit:scaffold, and asks before creating anything.
disable-model-invocation: true
argument-hint: "[project name]"
---

# Scaffold

Nothing is created until the user agrees. Skipped answers mean skipped steps. Scripts never overwrite existing files.

## 1. Confirm

Show the current directory and whether it is a git repository, then ask whether to scaffold here. If the directory is not empty, ask whether to use it as is or create a subfolder.

## 2. Preflight

Run the preflight from the `research` skill and tell the user which research tools work. Also check `git`, `gh` and `python3`, since the later steps need them.

## 3. Interview

Ask in batches of at most four questions with AskUserQuestion. The question bank is in [references/questions.md](references/questions.md). Cover:

1. Basics: project name, one-line idea, deadline, team size, the user's handle.
2. Repository: GitHub repo name and visibility, and whether to create it. Ask again right before creating.
3. Agent files: `CLAUDE.md`, `AGENTS.md`, both or neither. Ask each one separately.
4. Stack: research one, bring your own, or decide later.
5. Ghost mode: off, all levels, or chosen levels. Explain the levels in one line each.

## 4. Stack

Only if the user asked. Run the `research` skill for the idea: current stable options with version and release date, no legacy stacks unless the user asks. Present two or three options with a recommendation. After the user picks, show the generator command and run it only on a yes.

## 5. Create

In this order. Report each step as it finishes.

1. `git init` if needed.
2. Docs bundle:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/scaffold_docs.py" --root . --project "<name>" --by "human:<handle>" [--neutral]
python3 "${CLAUDE_SKILL_DIR}/../okf-docs/scripts/okf_validate.py" --strict docs
```

Add `--neutral` when ghost level `neutral-docs` is chosen.

3. Agent files, from [references/rules_file.md](references/rules_file.md). If both are chosen, put the content in `AGENTS.md` and make `CLAUDE.md` a single line: `@AGENTS.md`. If both are declined, write the project-local router skill from [references/route_skill.md](references/route_skill.md) to `.claude/skills/route/SKILL.md` instead.
4. Stack bootstrap, if confirmed.
5. Ghost mode, if chosen. Always last, so the files above exist to be excluded:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/ghost.py" apply --root . --levels all
python3 "${CLAUDE_SKILL_DIR}/scripts/ghost.py" check
```

Use `--levels attribution,untracked` style lists for chosen levels. Even with ghost off, keep `.claude/` out of git through `.git/info/exclude`, never `.gitignore`. Ghost mode applies to this clone only.

## 6. Commit and publish

Both are separate questions, asked after the files exist.

- Initial commit: explicit file list, neutral message such as `chore: initial project setup`. Never push.
- GitHub repo: `gh repo create <name> --public|--private --source=. --remote=origin`. No push flag. The user pushes.

## 7. Report

List what was created and where, what was skipped, the ghost levels applied, and the next command to run.
