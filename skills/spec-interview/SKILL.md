---
name: spec-interview
description: Turn a vague idea into a testable spec by interviewing the user, or stress-test an existing plan before building. Use at the start of a project or feature, when requirements are unclear,. Writes docs/specs/<name>.md. Not for looking up facts (use research) or trying a design in code.
---

# Spec interview

When the source is an organizer's rules document, run the `contract-check` skill first and use its contract as the fixed requirements.

Paths below that start with `docs/` are under the docs home. See the `okf-docs` skill.

The first prompt is an impulse, not a spec. Interview until every requirement can be checked by someone who did not write it. Do not build anything in this skill.

Two modes. If the user does not say which, ask.

| Mode | Input | Output |
|---|---|---|
| Draft | an idea | a spec |
| Stress | a plan or spec | ranked risks and changes |

## How to interview

- Use AskUserQuestion. Group related questions, at most four per call. Offer a recommended default as the first option when one exists.
- Ask what is not obvious. Skip anything the code, docs or earlier answers already settle.
- After each batch, restate your understanding in one or two lines so misreadings show early.
- Press a thin answer once ("what happens when nothing matches?"). Then move on.
- If the user says "you decide", decide and record the decision.
- Stop when each requirement has a checkable acceptance criterion. Not before, not long after.

## Draft mode

Cover these in the order the conversation leads:

1. Problem: who has it, how they cope today, what happens if nothing is built.
2. The success moment: the one flow a user or judge sees working.
3. Must-haves: each concrete enough to test. "Fast" is not checkable. "Responds in under 200 ms" is.
4. Out of scope: ask for it explicitly. This fence stops scope creep.
5. Constraints: stack, time, team, hosting, data, existing conventions.
6. Failure and edges: empty input, bad input, limits, conflicts, what is visible when it fails.
7. Data and decisions: what to keep, what to start fresh, who wins on conflict.
8. Definition of done.

Then write the spec with [references/spec.md](references/spec.md), following the `okf-docs` skill. Save it to `docs/specs/<name>.md`. Set `status: draft` and show it to the user. Change it to `stable` only after the user approves it.

## Stress mode

1. Restate the plan in your own words and get a yes.
2. List the assumptions it depends on, then mark which have evidence.
3. Run a pre-mortem: "It is demo time and this failed. Why?" Collect causes.
4. Walk the decision tree one branch at a time, resolving dependencies in order. For each branch ask: what is the risk, what is the evidence, what is the cheapest test?
5. Route open questions: facts to `research`, design doubts to a throwaway experiment.
6. End with the risks ranked by impact and the changes to the plan. Ask which to adopt.

## Rules

- One recommendation per decision, with the reason. Not a survey of options.
- Never mark a requirement done or approved on the user's behalf.
- Keep the spec to what and why. How belongs to the build.
- Record decisions the user makes during the interview with the `project-log` skill when `docs/journal/` exists.
