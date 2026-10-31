# Testing whether a bundle helps agents

Use this before trusting a bundle for agent context. A bundle that only restates the code adds cost, not accuracy, so measure it.

## Design

1. Two groups, same model. Control gets a copy of the repo. Treatment gets the same copy plus the bundle. Put each copy in its own folder outside the project, so control cannot read the docs. Use copy-on-write copies (`cp -c` on macOS) to save disk.
2. Tasks the code alone cannot answer: operations, external systems, safety calls, cross-repo procedures, decisions. Pure lookup questions sit at the ceiling and show nothing.
3. Gold answers verified against the code at a pinned commit, never taken from the bundle. Write a rubric per task: 2 correct, 1 partial, 0 wrong, with the MUST items listed.
4. Screen tasks: keep ones a control run solves 30 to 70 percent of the time. Add more tasks before adding more repeats; variance between tasks dominates.
5. At least 3 runs per group. Add a weaker model when possible; orientation help matters more there.
6. If the bundle contains review notes or known answers, add a third group without them to separate their effect.

## Running

- Subjects get read-only rules: stay inside their folder, no network, no scripts, no file writes, answers only in the final message.
- Record tokens, tool calls and wall time per run.
- Audit each transcript: count reads outside the workspace and, for treatment, reads of the bundle. Discard contaminated runs.

## Judging

- Copy answers under shuffled labels and keep the mapping private.
- One judge scores every answer set against the gold rubric and the repo, and records any dispute with the gold.
- Report per group: mean score, spread across runs, cost, and per-task differences. With few runs, call small gaps directional, not significant.
