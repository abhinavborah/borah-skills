---
name: test-first
description: Build features test-first, or fix bugs by reproducing them first. Feature mode writes one failing test at a time. Bug mode reproduces the bug end to end as a user would see it, shrinks it, writes a regression test that fails, then fixes the root cause. Use when implementing a behavior or when something is broken, throwing or failing. Not for trying ideas (use spike).
---

# Test first

A test that has never failed proves nothing. Agents skip the red step unless told not to, and some delete tests to get green. Both are banned here.

Hackathon scale: test the core logic and the demo flow. Skip tests for glue code, config and pure layout.

Pick the mode from the task. A new behavior is feature mode. A reported failure is bug mode.

## Feature mode

1. List the behaviors to build, as short sentences. Order them by value to the demo flow. Confirm the list with the user if it is not obvious.
2. For the first behavior, write one test through the public interface. Run it. It must fail, and for the right reason: the behavior is missing, not a typo or an import error. Show the failure.
3. Write the least code that passes. No extra features, no anticipated needs.
4. Run the test and the whole suite. All green.
5. Refactor only while green. Run the suite after each change.
6. Commit the test and the code together, then take the next behavior.

Test behavior, not implementation. Mock only at boundaries you do not own, such as network and clock. When work is delegated to a subagent, commit the failing tests first and tell it not to edit them.

## Bug mode

Start before touching code.

1. **Reproduce as the user sees it.** Use the real entry point: the browser, the CLI, the HTTP call. Capture the exact error, the steps and the input. If it is intermittent, loop or stress it until it fails often enough to work with. If it cannot be reproduced, say so and ask for more detail. Do not guess a fix.
2. **Shrink it.** Remove steps, input and code until the smallest case still fails. Bisect inputs, code or git history when the cause is far away.
3. **Hypothesize and test.** State one hypothesis. Change one variable. Confirm or rule it out. Add temporary logging, tagged so it can be found and removed.
4. **Write the regression test** at the lowest seam that still catches the cause. Run it. It must fail now.
5. **Fix the root cause.** Before editing, search for every caller of the code you are about to change. Change the shared code so every caller is covered, not only the path named in the report. A guard that hides the symptom is not a fix.
6. **Verify.** Re-run the original end-to-end reproduction, the new test and the full suite. Remove the temporary logging.

Never skip, disable or loosen a failing test to get green. Never call a flaky failure fixed because it passed once.

## Done when

The test you wrote failed before the change and passes after, the suite is green, and for a bug the original reproduction no longer fails.
