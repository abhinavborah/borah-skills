# Details that add up

Small, cheap fixes. Apply the ones the audit finds.

## Shape and depth

- Nested rounded elements: outer radius = inner radius + the padding between them. Mismatched radii are the most common reason a UI feels slightly off.
- For cards and buttons whose border only exists to show depth, use layered low-opacity `box-shadow` instead. Keep real borders for dividers and for selected or focus states.
- Add a faint 1px outline to images so edges hold on any background: pure black at about 10% in light mode, pure white at about 10% in dark mode. Tinted greys pick up the surface color and look dirty.
- Do not stack translucent surfaces on each other. Text over layered transparency loses contrast.

## Alignment

- Align optically when geometric centering looks wrong: play triangles, icons beside text, asymmetric glyphs. A button with an icon and text usually needs a little less padding on the icon side.
- Match an icon's stroke weight to the text beside it.

## Type

- `font-variant-numeric: tabular-nums` for numbers that update or line up in columns: timers, counters, prices, tables.
- `text-wrap: balance` on headings and `text-wrap: pretty` on short descriptions. Do not use either on long articles.
- Keep long text lines to about 60 to 75 characters.
- Keep long words, URLs and IDs inside their box with `overflow-wrap: break-word`. Use `white-space: nowrap` for badges and labels.
- Use curly quotes, real ellipses and en dashes for ranges.
- Truncated text needs a way to read the full text.

## Targets and focus

- Hit areas at least 24 by 24 CSS pixels. Aim for 44 by 44 on touch. Extend a small control with a pseudo-element instead of enlarging its drawing. Hit areas must not overlap.
- Style `:focus-visible`. Never remove the outline without a replacement that has at least 3:1 contrast.
- Put hover styles under `@media (hover: hover)` so touch screens do not keep a stuck hover.
- Inputs use at least 16px text, or iOS Safari zooms on focus.
- Every input has a visible label. Icon-only buttons have an accessible name.

## States

- Empty states say what goes here and offer the next action.
- Loading states keep the layout's shape (skeletons or fixed-size placeholders) so nothing jumps.
- Errors say what happened and what to do, next to the thing that failed.
- Disabled controls look disabled and say why when it is not obvious.

Sources of ideas, summarized and not copied: web interface guidelines from Vercel (MIT), interface cheat sheet at interfaces.dev, writing by Jakub Krehel on interface details, Emil Kowalski's UI skills. Checked 2026-10-24.
