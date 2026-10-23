---
name: session-handoff
description: Write a timestamped handoff file in docs/handoffs/ (session) or docs/subagent-handoffs/ (one subagent) so the next agent continues without this conversation. Use when the user asks for a handoff, when context is nearly full, or when orchestrate dispatches a subagent. Not for chat summaries or compaction.
---

# Session handoff

A handoff is a file the next agent reads first. It holds pointers, decisions and tool notes, not a retelling. Two kinds:

| Kind | File | Reader |
|---|---|---|
| Session | `docs/handoffs/handoff_YYYY_MM_DD_HHMMSS.md` | the next session or agent |
| Subagent | `docs/subagent-handoffs/<agent_name>_YYYY_MM_DD_HHMMSS.md` | one dispatched subagent, then the orchestrator |

If the kind is unclear, ask.

## Steps

1. **Time.** Run `date +%Y_%m_%d_%H%M%S` for the filename and `date -u +%Y-%m-%dT%H:%M:%SZ` for frontmatter. Never invent either.
2. **Read first.** Read the newest file in the target folder and `git log -n 5`. Write a delta over it, and verify each claim against disk or git before writing it.
3. **Fill the template.** Session: [references/session.md](references/session.md). Subagent: [references/subagent.md](references/subagent.md).
4. **Settle the next task.** If it is not clear, write "not yet assigned" with ranked candidates, and ask the user now if one question would settle it.
5. **Sync.** Follow the `okf-docs` skill: add the file to the folder's `index.md`, prepend a dated entry to `log.md`, run the validator.
6. **Ask two things.** Commit the handoff (explicit file list, never push)? Print an inline prompt for the next agent? Both are optional.

## Content rules

- Reference plans, specs, issues and diffs by path or URL. Do not copy them.
- Mark each decision as the user's choice or an agent proposal. Never present a proposal as decided.
- List tools, plugins and skills that worked, those that failed with the shortest decisive error, and the order to try them.
- Name the preferences that bind the work: tone, style, process rules the user stated.
- Redact keys, passwords and personal data.

## Inline prompt

When the user wants one, print it in a code block with the real filename:

```text
Read docs/handoffs/handoff_<timestamp>.md first and verify its claims against disk and git. Then <next task>. Ask before <risky action>.
```

For a subagent, the orchestrate skill passes the file path in the dispatch prompt instead.
