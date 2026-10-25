---
name: spike
description: Answer one design or logic question with small, disposable, runnable code before committing to a real build. Use when unsure whether an approach, library, data model or UI layout will work, or to compare layouts side by side. Records the answer, then throws the code away. Not for building the real feature (use test-first) or for looking up facts (use research).
---

# Spike

Paths below that start with `docs/` are under the docs home. See the `okf-docs` skill.

A spike produces an answer, not code to ship. Without a question it is just unplanned coding.

## Steps

1. **Write the question** in one sentence, before any code. Two questions mean two spikes. If there is no question, this is not a spike: use `test-first`.

   Good: "Does this streaming API handle backpressure the way we need?" Bad: "Try out the library."

2. **Fix the exit.** Write down:
   - Timebox: 30 to 90 minutes. Stop when it ends, even if unanswered.
   - Keep if: the observable result that means proceed.
   - Kill if: the observable result that means stop.

3. **Pick the shape.**
   - Logic or state question: a small runnable tool, usually a terminal script, with visible state and one command to run it. Keep state in memory unless storage is the question.
   - UI question: two to four variants of the same screen behind a switcher, judged on the same user scenario.

4. **Build in an isolated place**, `spikes/<slug>/`, outside real source paths and never imported by them. Name it as throwaway. Hard-code, skip error handling, skip tests, skip polish. Anything the question does not depend on gets a stub.

5. **Run it and observe.** Show the evidence: output, a timing, a screenshot. For UI, look at it, then ask the user to react.

6. **Write the answer** to `docs/research/spike_<slug>.md` using the `okf-docs` skill, type `Spike Result`:
   - Question
   - Result: answered, partly answered, or not answered
   - Evidence
   - What was not explored
   - Decision: proceed, change approach, or stop

7. **Log the decision** with the `project-log` skill if the project has `docs/journal/`, linking the spike result.

8. **Hand off behaviors, not code.** List the behaviors the spike proved. They become the first tests for `test-first`.

9. **Delete the spike**, or leave `spikes/` uncommitted until the build is done. Ask which.

## Rules

- Spike code is never merged, never adapted, never cleaned up and shipped. A "keep" decision means rewrite in the real project.
- If the question changes shape, start a new spike. Do not patch the old one toward a new question.
- Do not generalize. A spike that works on small data says nothing about load.
- Record the answer before deleting the code. A deleted spike with no record is wasted.
