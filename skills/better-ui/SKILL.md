---
name: better-ui
description: Audit and polish a web interface, from hierarchy and spacing down to small details and motion. Use when a UI looks plain, cluttered, generic or static, or when asked to improve, polish, restyle or animate screens. Works from the running app, not from guesses. Not for writing UI copy (use ste) or comparing layouts (use spike).
---

# Better UI

Fix structure before details, and details before motion. A polished animation on a confusing layout is still a confusing layout.

## Steps

1. **See it.** Run the app and look at the real screens in a browser, at desktop and phone width. If a browser tool is available, take screenshots. Do not judge from code alone.
2. **Fix the direction.** Name one palette, one type pairing, one spacing scale and one radius scale for the project, and reuse existing ones if the project has them. Write them down as CSS variables or theme tokens. If a design-direction skill is installed, load it for this step.
3. **Audit** in this order, and list findings by impact:
   1. Hierarchy: one primary action per screen, clear reading order, size and weight that match importance.
   2. Layout and spacing: a consistent scale, alignment, breathing room, nothing cramped or lost.
   3. States: empty, loading, error and success exist and look intentional.
   4. Type and color: readable sizes, contrast of at least 4.5:1 for body text, color never the only signal.
   5. Details: see [references/details.md](references/details.md).
   6. Motion: see [references/motion.md](references/motion.md). Last, and sparing.
4. **Fix the top findings first.** Make small, reviewable changes. Keep behavior unchanged.
5. **Verify** in the browser: both widths, keyboard focus order and visible focus rings, reduced-motion setting, and the demo flow end to end.

## Generic-looking UI

These read as unfinished or templated. Replace them with a deliberate choice:

- Default purple-to-blue gradients, glass panels over everything, glowing blobs.
- Emoji used as icons, mixed icon sets or mixed stroke weights.
- Every element in a card with the same radius and shadow.
- Centered hero with a gradient headline and two equal buttons.
- Placeholder copy, lorem ipsum, "Welcome to".

## Hackathon priority

The demo flow gets polished first, one screen at a time. Anything the judge will not see waits. Spend the last hour on the demo path: seeded data that looks real, no layout shift, no empty states on screen.
