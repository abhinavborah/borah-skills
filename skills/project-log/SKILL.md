---
name: project-log
description: Log decisions, findings, changes and rejected approaches as shared project history in docs/journal/. Use when the user says to record, log, note or write down a decision or the reason for something, and right after a decision is made, research or a spike finishes, direction changes, or an approach is rejected. Also read active decisions at session start. Not for private notes, session handoffs (use session-handoff) or doc format (use okf-docs).
---

# Project log

Paths below that start with `docs/` are under the docs home. See the `okf-docs` skill.

Git holds what changed. The journal holds why. A decision that lives only in the chat is lost at the next compaction, and an agent that cannot see why an approach was rejected will propose it again.

## Read

At session start, and before changing anything a past decision may cover:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/journal.py" digest --root .
```

It prints active decisions, open questions, recent entries, and entries with unfilled placeholders. Superseded entries are history: never act on them. The digest is a view. Open an entry before relying on it.

## Write

Write at the moment of commitment, not at session end. Triggers:

- A decision was made, by the user or by you.
- Research or a spike finished, and its answer changes what happens next.
- Direction changed, or an approach was tried and rejected.
- A commit carries a reason someone will need later.
- An open question surfaced that blocks a choice.

Skip routine edits, typo fixes and anything the diff already explains.

| Kind | Use for |
|---|---|
| `decision` | A choice between real options |
| `finding` | A fact learned, with its evidence |
| `change` | What changed and why, when the commit message cannot hold it |
| `rejection` | An approach tried or considered and dropped |
| `question` | An unresolved question that blocks a choice |

## Steps

1. Create the entry. The script writes the file, with placeholders, and updates the folder's index and log:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/journal.py" new --root . --kind decision --title "Use Postgres for storage" --confidence high --by <your-name/version>
```

   Add `--neutral` when the ghost level `neutral-docs` is on (see the `okf-docs` skill). Use `--by human:<handle>` only for text the user dictated or confirmed. For `finding`, add `--evidence` with a strength from [references/entry.md](references/entry.md).

2. Replace every `FILL:` line. Lead with the decision or finding. Always give context and the reason. For a decision, list alternatives with why each lost, and what would make the team revisit it. Say whether it is the user's choice or your proposal.
3. Link instead of retelling: research notes, specs and spikes by path, commits by hash.
4. Keep the title and description as generated, because the index repeats them.
5. Validate: `python3 "${CLAUDE_SKILL_DIR}/../okf-docs/scripts/okf_validate.py" --strict docs`

Examples of finished entries: [references/entry.md](references/entry.md).

## Rules

- Append only. Never edit an accepted entry. To change a decision, write a new entry, then:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/journal.py" supersede --root . --old <old-file> --new <new-file>
```

  The same command closes an answered question.
- Label evidence honestly and state the scope: what the conclusion does not cover. Never promote an inference to a fact.
- One decision per entry. Keep entries under about 25 lines.
- No secrets or personal data.
- A plugin hook may remind you after a commit that has no entry. If nothing there is worth recording, ignore it.
