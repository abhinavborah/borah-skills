# Motion

Motion must say something: where an element came from, what changed, what to do next. Decoration is noise.

## Decide whether to animate

| How often it happens | Motion |
|---|---|
| Many times a day (shortcuts, command palette, typing, list navigation) | None, or under 150 ms |
| Several times a session (modals, drawers, toasts, menus) | Standard, 150 to 300 ms |
| Rare or first time (onboarding, success, empty-state reveal) | Can be expressive |

## Timing

- Direct feedback (press, toggle, check): about 100 ms.
- Small UI (dropdown, tooltip, tab): 150 to 200 ms.
- Larger UI (modal, popover, drawer): 200 to 300 ms.
- Page or sheet transitions: 300 to 400 ms. Past 500 ms it feels slow.
- Exits are shorter than entrances.
- Pick durations from a short scale used everywhere. Do not hand-tune 153 ms on one control and 220 ms on its sibling.

## Easing

- Ease-out for things entering. It responds at once and settles.
- Ease-in for things leaving.
- Ease-in-out for things moving between two visible positions.
- Linear only for progress bars, spinners and scroll-linked effects.
- Use springs with low bounce on functional UI. No elastic bounce.

## Properties

- Animate `transform` and `opacity`. Do not animate `width`, `height`, `top` or `left`.
- Never write `transition: all`. List the properties.
- Set the right `transform-origin` so motion starts where it physically should, such as a popover growing from its trigger.
- Motion must be interruptible. A second tap reverses it, and it never blocks input.
- Stagger lists by small steps, and keep the total short. Decorative staggering must not delay interaction.

## Reduced motion

Honor `prefers-reduced-motion`. Replace movement with a fade or an instant change. Keep essential feedback, such as a focus ring change and loading indicators, because a frozen spinner reads as broken.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Prefer the simplest tool

CSS transitions and keyframes first, the Web Animations API next, a library last. For animated numbers, animate with a purpose-built number component rather than re-rendering text.

Based on timing guidance from Nielsen Norman Group and web.dev, and the Vercel interface guidelines (MIT). Checked 2026-10-24.
