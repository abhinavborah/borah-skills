---
name: orchestrate
description: Split work into independent packets, get approval, then dispatch in-process subagents with disjoint file ownership and collect their reports. Use when a task has two or more parts that can run in parallel and touch different files. Not for sequential work or a single change.
---

# Orchestrate

Parallel agents cost coordination: contracts, briefs, a merge gate. Use them only when the parts are independent. Otherwise do the work directly.

## 1. Gate

Proceed only if all hold:

- Two or more packets that can start without each other's output.
- Each packet has its own write set, with no file shared.
- The interface between packets can be written down before work starts.

If not, say so and work sequentially or with one subagent.

## 2. Plan

Write the plan to `docs/subagent-handoffs/plan_<timestamp>.md` with the template in [references/plan.md](references/plan.md), following the `okf-docs` skill. It decides:

1. Boundary contract: the shared interface each packet relies on.
2. Ownership table: per packet, what it may write, what it reads as authority, what it waits for.
3. Shared files: one owner each. Others request changes through that owner.
4. Evidence: the checks that must pass before a result is accepted.
5. Release boundary: push, merge and publish stay with the user.

The ownership table is also a fenced `json ownership` block, which the merge gate reads.

## 3. Approve

Show the plan and ask the user to approve it with AskUserQuestion. State the packet count. Run at most 5 subagents at once; if there are more packets, run them in waves. The user may lower the cap.

## 4. Dispatch

1. For each packet, write a brief with the `session-handoff` skill (subagent kind) before dispatch. Add the brief's own path to that packet's `may_write`. Then commit the plan and the briefs, because a worktree starts from the last commit and would not contain uncommitted files.
2. Start independent packets together with the Agent tool, one call each in a single message. Packets that write files use worktree isolation. Read-only packets run in place.
3. Name each subagent after its packet. Right after dispatch, record the returned agent ID and the time in the brief's Agent section. To continue or correct a running or finished subagent, message it by name or ID instead of starting a new one.
4. The dispatch prompt gives the brief path, the packet name, and these rules: you are a leaf and do not spawn agents; stay inside your ownership; stop and report if the plan looks wrong; fill the Report section of your brief. When `<git-common-dir>/ghost/ghost.json` exists, also: write commit messages with no co-author or generated-with lines.

## 5. Collect and gate

1. Read each subagent's final message, which repeats its Report. The same text sits in its brief on its branch. Subagents do not write to `docs/journal/`; journal their decisions and findings yourself with the `project-log` skill.
2. Run the merge gate on the packets that wrote files:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/check_ownership.py" --plan docs/subagent-handoffs/plan_<timestamp>.md --base <base-ref> --packet <name>=<branch> --packet <name>=<branch>
```

3. Run each packet's declared checks yourself. A report is a claim, not evidence.

## 6. Integrate

Merge one packet at a time, then re-run the checks. Do not push.

On a conflict, never take one side across a file. Compare both changes with the contract and tests. If the packets made incompatible assumptions, stop and bring the decision to the user.

| Failure | Do |
|---|---|
| Missing context | Fix the brief, then resume or reassign |
| Wrong architecture | Return to the plan, do not patch around it |
| Repeated test failure | Escalate after two retries, with commands and logs |
| Wrote outside ownership | Keep in-scope changes only, tighten the brief |
| Stalled or lost | Start a fresh subagent from the brief and the latest commit |

When reassigning, pass the brief and failure evidence, not the whole earlier conversation.

## 7. Close

Record the plan's key decisions and any failure causes with the `project-log` skill when `docs/journal/` exists. Write a session handoff with the `session-handoff` skill and report to the user what merged, what failed, and what is left.
