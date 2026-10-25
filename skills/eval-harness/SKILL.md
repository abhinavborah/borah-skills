---
name: eval-harness
description: Set up honest evaluation before tuning anything. Makes a deterministic dev and holdout split of labeled data, adds a scorer, and guards production code from reading gold labels or sample answers. Use when a project has labeled examples and a score to report, before the first tuning round. Not for unit tests (use a test skill).
---

# Eval harness

An accuracy number is only a claim if the data it was measured on was never used to tune. Build the split and the guard first, then tune.

Paths that start with `docs/` are under the docs home. See the `okf-docs` skill.

## Steps

1. **List the labeled data.** Find every file with known answers: public samples, sample outputs, golden files. Ask the user which are allowed at run time. Anything organizer-only is never allowed for predictions.
2. **Split before tuning.** Pick the group key, the unit that must not straddle both sides (user, case family, document). Make the split once, with a seed, and commit the split files:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/split.py" labeled.csv --group user_id --holdout 0.3 --seed 1 --out eval/
```

   If there are too few examples for a holdout, say so in the report and use leave-one-group-out. Never report an in-sample score as accuracy.
3. **Write the scorer** once, outside production code, with the metrics the task defines. Report dev and holdout scores separately, with counts.
4. **Guard the code.** List the forbidden strings: sample output paths, golden file names, organizer-only folders. Run the guard in CI or before every commit:

```shell
python3 "${CLAUDE_SKILL_DIR}/scripts/leak_guard.py" --code code --forbid sample_output.csv --forbid golden
```

   It scans production code and skips `tests/` and `evaluation/` by default. Add `--skip` for other folders.
5. **Tune on dev only.** Look at the holdout only after the dev work is frozen, and then once. If a holdout result drives a change, the holdout is spent: say so, and make a fresh split or add new cases.
6. **Write the report** with the dev score, the holdout score, the cases you added yourself, the failures found and what changed. A claim like "100%" needs the split next to it.
