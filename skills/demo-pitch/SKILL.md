---
name: demo-pitch
description: Prepare a hackathon demo, pitch and submission. Picks the one flow to show, cuts scope to it, writes a timed demo script with a fallback, drafts submission text, and sets a rehearsal checklist. Use in the last third of a hackathon, or when asked for a pitch, demo script or submission. Includes a UI polish pass for the demo path. Not for general documentation.
---

# Demo and pitch

Paths below that start with `docs/` are under the docs home. See the `okf-docs` skill.

Judges remember the demo. A clear demo of a simple project beats a confusing demo of a strong one. Most winners were decided by the few minutes spent presenting.

## Steps

1. **Get the rules.** Ask for the judging criteria, time limit, submission fields and length limits. If the user gives a link, read it with the `research` skill. Do not assume the rubric.
2. **State the problem in one sentence.** Who feels it, and why it hurts. Start the pitch here, so the room shares the frustration before seeing the fix.
3. **Pick one flow.** The single path that shows the project working end to end. If the demo runs long, the scope is too big: list what to cut or hide, and ask the user to confirm.
4. **Write the script** with the template in [references/script.md](references/script.md). Something must work on screen within about 90 seconds. Put the judge in the user's seat and walk through what happens.
5. **Make the demo safe.** For every place it could stall, remove the risk:
   - Seed realistic data. Pre-fill forms and logged-in state.
   - Mock or cache slow or flaky calls.
   - Add a reset command that restores the starting state.
   - Record a short fallback video of the full flow.
   - Test on the venue's network and screen, or offline.
6. **Be direct about limits.** One line each: what works, what does not yet, how it could extend. Do not talk around a missing feature.
7. **Draft the submission text** to the field limits: title, one-line tagline, problem, what it does, how it was built, challenges, what is next, links. Keep it short, concrete and free of hype.
8. **Rehearse.** Run it out loud and time it. Run it once with someone who has not seen it. Run it once with the main path failing on purpose to practice the fallback.
9. **Save the plan** to `docs/pitch.md` as type `Pitch Plan`, using the `okf-docs` skill. Keep the script and checklist there so teammates share one version.

## Polish the demo path

Only for screens the judge will see. Fix structure before details, and details before motion.

1. Run the app and look at the real screens in a browser at desktop and phone width. Do not judge from code alone.
2. Name one palette, one type pairing, one spacing scale and one radius scale. Write them as CSS variables or theme tokens.
3. Audit in this order and fix the top findings first: hierarchy (one primary action per screen), spacing, states (empty, loading, error, success), type and color (contrast of at least 4.5:1), then details ([references/ui-details.md](references/ui-details.md)), then motion ([references/ui-motion.md](references/ui-motion.md)), last and sparing.
4. Replace generic looks: default purple-to-blue gradients, emoji as icons, every element in the same card, placeholder copy.
5. Verify in the browser: both widths, focus order and rings, reduced-motion setting, and the demo flow end to end, with seeded data that looks real.

## Final checklist

- Problem stated in the first 20 seconds.
- One flow, working, inside the time limit.
- Fallback video exists and plays.
- Reset command works.
- Submission fields filled, links open, repo is public if required.
- Everyone knows who speaks when.
- Phone and laptop charged, notifications off, screen resolution tested.

Based on judging advice in [How to Win a Hackathon: Notes From the Judging Table](https://blog.jetbrains.com/ai/2026/06/how-to-win-a-hackathon-notes-from-the-judging-table/) (JetBrains, 2026-06) and similar judge write-ups. Checked 2026-10-24.
