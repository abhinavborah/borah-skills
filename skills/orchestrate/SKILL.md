---
name: orchestrate
description: Split work into independent packets, get approval, then dispatch in-process subagents with disjoint file ownership and collect their reports from files. Two modes, worktree per packet or one shared tree. Use when a task has two or more parts that can run in parallel and touch different files. Not for sequential work or a single change.
---

# Orchestrate

Parallel agents cost coordination: contracts, briefs, a merge gate, and your own context. Use them only when the parts are independent. Otherwise do the work directly.

Paths below that start with `docs/` are under the docs home. See the `okf-docs` skill. If `~/.claude/swarm.md` exists, read it first and obey its limits. They win over the caps here.

## 1. Gate

Proceed only if all hold:

- Two or more packets that can start without each other's output.
- Each packet has its own write set, with no file shared. Tests count: each packet owns the tests for its files, and shared helpers get one owner.
- The interface between packets can be written down before work starts.

If not, say so and work sequentially or with one subagent.

## 2. Plan

Write the plan to `docs/subagent-handoffs/plan_<timestamp>.md` with the template in [references/plan.md](references/plan.md), following the `okf-docs` skill. It decides:

1. Boundary contract: the shared interface each packet relies on.
2. Ownership table: per packet, what it may write, what it reads as authority, what it waits for.
3. Shared files: one owner each. Others request changes through that owner.
4. Evidence: the checks that must pass before a result is accepted.
5. Mode: `worktree` or `shared` (below).
6. Release boundary: push, merge and publish stay with the user.

The ownership table is also a fenced `json ownership` block. It is the ledger the gate reads, and the only source of ownership. A scope change goes through you: edit the ledger and commit it before the worker continues. Never widen a worker's scope by message.

| Mode | Use when | Workers | Gate |
|---|---|---|---|
| `worktree` | The repo has a commit to branch from and packets are large | `packet-worker`, own worktree and branch, commits itself | `check_ownership.py --packet` on branches |
| `shared` | Early project, no stable base, or many small packets | `packet-worker-shared`, one tree, never runs git write commands | `check_ownership.py --shared` after each packet, then you commit |

## 3. Approve

Show the plan and ask the user to approve it with AskUserQuestion. State the packet count and the mode. Run at most 5 subagents at once; if there are more packets, run them in waves. The user may lower the cap.

Dispatch only in a turn after the approval answer arrives. Never ask and dispatch in the same turn.

Then commit the skeleton: the plan, the briefs, the contract files and the empty module layout. A worktree branches from your last commit only when `worktree.baseRef` is `head`. The preflight checks this and that the tree is clean:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/preflight.py" --root .
```

If it reports `baseRef`, ask the user, then run it again with `--fix`. That writes `worktree.baseRef = "head"` to `.claude/settings.json`. Shared mode needs only the clean tree.

## 4. Dispatch

1. For each packet, write a brief with the `session-handoff` skill (subagent kind). Add the brief's own path to that packet's `may_write`. Commit the plan and briefs, then run the preflight again.
2. Start independent packets together with the Agent tool, one call each in a single message. Use `hack-kit:packet-worker` (worktree mode) or `hack-kit:packet-worker-shared` (shared mode). Read-only packets run in place with `hack-kit:reviewer` or a plain agent.
3. Name each subagent after its packet. Right after dispatch, record the returned agent ID and the time in the brief's Agent section. To continue or correct a subagent, message it by name or ID instead of starting a new one.
4. The dispatch prompt gives the brief path and the packet name only. The agent definition carries the rules.
5. Wait for task notifications. Do not poll. Use Monitor only with an until-condition on a file the worker was told to write.

## 5. Collect and gate

Each worker writes its full Report into its brief file and ends with at most 5 lines: the brief path, a verdict (done, blocked, partial) and the check results. Read the Report file when you need it. Do not paste reports into your own context.

Subagents do not write the journal. Journal their decisions and findings yourself with the `project-log` skill, after the user agrees to a journal (see the docs home rules in `okf-docs`).

Worktree mode: run the gate with each packet's branch and worktree directory, so uncommitted work is caught.

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/check_ownership.py" --plan <plan-file> --base <base-ref> --packet <name>=<branch> --worktree <name>=<dir>
```

It fails when a packet wrote outside its files (a rename counts), when two packets touched the same file, when a packet has no commits, or when its worktree is dirty.

Shared mode: after each packet reports, check the tree, then commit that packet's files with an explicit file list.

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/check_ownership.py" --plan <plan-file> --shared <name>
```

Run the test suite once after the whole wave, not while workers are still editing. Concurrent edits cause failures that no packet owns. A report is a claim, so run each packet's declared checks yourself. For a second opinion on a wave, dispatch `hack-kit:reviewer` on the diff.

## 6. Integrate

Worktree mode: merge one packet at a time, then re-run the checks. Do not push.

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

Remove the worktrees and branches you created, after the merge. Record key decisions and failure causes with the `project-log` skill if the user agreed to a journal. Write a session handoff with the `session-handoff` skill and report to the user what merged, what failed, and what is left.
