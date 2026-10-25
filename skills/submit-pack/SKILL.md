---
name: submit-pack
description: Package a hackathon or contest submission. Shows time left to the deadline, runs a clean-clone check, builds the code archive with excludes, collects agent transcripts from every project folder of the repo and its worktrees, scans the bundle for secrets and junk, and lists the exact artifacts to upload. Use in the last day before a deadline or when asked to package, zip or submit. Not for the pitch (use demo-pitch).
---

# Submit pack

Packaging fails late and by hand: archives rebuilt three times, traces split across folders, junk and personal data inside zips. Do it once, in order, with a checklist.

Paths that start with `docs/` are under the docs home. See the `okf-docs` skill.

## 1. Time left

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/time_left.py" CLAUDE.md AGENTS.md .claude/rules/hack-kit.md
```

It reads the line `hack-kit deadline: <ISO-8601 with offset>` from those files. Pass `--deadline <ISO>` to use another value. If none exists, ask the user for it with its timezone and write the line into the rules file. Never assume a deadline.

## 2. Rules

Run the `contract-check` skill recheck if `docs/contract.md` exists. Every `MUST` row must be `met` with a proof run today. If no contract exists, ask whether to make one now.

## 3. Clean-clone check

Clone the repo to a temporary folder outside it, follow only the README setup, run the entry point, and confirm the output file has the exact shape the rules require. Fix the README, not your memory of the steps.

## 4. Build the archive

Build from tracked files only (`git archive` or a file list), so caches, virtual environments, data folders and secrets stay out. Exclude what the rules forbid, such as the dataset or nested archives. Record the archive md5.

## 5. Collect traces

Agent transcripts live in one folder per working directory, and worktrees get their own. Collect all of them:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/collect_traces.py" --repo <repo path> --out <staging>/agent-trace/claude-code
```

It copies only `*.jsonl` files, keeps the session and `subagents/` layout, skips `memory/` and `tool-results/`, and prints the folders it matched. Check that list with the user. Add one `/export` text file per session, which the user must run. Ask which exports exist. Tell the user that a live session keeps growing, so a zip made now misses its later turns.

## 6. Scan

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/scan_bundle.py" <staging dir or zip> ...
```

It prints file names only, never the matched text. It flags secret-shaped strings and junk entries (`__MACOSX`, `.DS_Store`, `.env`, caches, virtual environments, `memory/`). Stop on any hit and show the user the names.

## 7. Zip and test

Zip, run `unzip -tq`, check the size limit from the rules, count the files that matter, and record the md5.

## 8. List the artifacts

End with a table: artifact, absolute path, md5, what the rules call it. Include the submission URL from the rules, copied exactly. State the deadline and the time left. Pushing, uploading and submitting stay with the user.
