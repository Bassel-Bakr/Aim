---
title: "Sensitivity"
tags:
  - sensitivity
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

Mouse sensitivity is how far your view turns for a given amount of hand movement.

- **Compare in cm/360 or eDPI, not raw settings.** Raw numbers mean different things per game.
- **There is no single correct sensitivity.** Pick one deliberately, then give it time.
- **Match it across games** so you don't relearn your aim every time you switch titles.
- **Changing it is fine with a reason.** Changing it constantly is what costs you.

## Explanation

**cm/360** is the physical distance your mouse travels across your pad to turn your in-game view a
full 360 degrees.

You can measure it: aim at a fixed point, turn a full circle, and measure how far your hand moved.
Or use a calculator that combines your DPI and in-game sensitivity value.[^cm360]

Because it is measured in real-world distance, cm/360 is comparable across any game, engine, or
mouse.

**eDPI** (effective DPI) is your mouse DPI multiplied by your in-game sensitivity multiplier. For
example, 800 DPI × 0.27 sensitivity = 216 eDPI.[^edpi]

Two players with the same eDPI move their crosshair the same amount for the same hand movement in
that game. Their raw DPI and sensitivity values don't matter.

Unlike cm/360, eDPI is only comparable **within one game**. Different games apply different scaling
to the sensitivity multiplier.[^edpi]

**Low versus high sensitivity** is a trade-off in how much of the work your arm does versus your
wrist and fingers.

A lower sensitivity (higher cm/360) spreads a turn over more physical distance. That leaves more room
to correct small tracking errors, but demands a larger mousepad and more arm movement.

A higher sensitivity (lower cm/360) lets you turn and flick with small wrist movements and less desk
space. The catch: the same small hand tremor produces a much larger error on screen.

Some sources, including [Aimlabs](https://aimlabs.com/articles/aimlabs/a-quick-explainer-on-cm-360-and-the-common-cm-360-by-game/),
publish typical cm/360 ranges used by players per game. Treat these as a starting reference, not a
target. The article itself notes the right number depends on your equipment, desk space, posture,
and comfort.

## Choosing a starting point

Don't search for an "ideal" number. Instead:

1. Pick a sensitivity that lets you comfortably reach every part of your mousepad.
2. Check you can still turn 180 degrees without lifting your mouse.
3. Leave it alone long enough to judge it fairly.

No reference point at all? Look at the range other players in your game use, via a tool like the
one linked above. Use it as a starting value to adjust from, not a rule to lock into.

## Converting sensitivity between games and trainers

If you play more than one game, or move between a game and an aim trainer, match your physical
sensitivity. That keeps your muscle memory consistent instead of forcing you to relearn your aim per
title.

- **KovaaK's** publishes an official web-based [sensitivity converter](https://kovaaks.com/kovaaks/sens-converter)
  for a fixed list of supported games. It also maintains an open-source
  [Sensitivity Matcher](https://github.com/KovaaK/SensitivityMatcher) tool. That tool measures your
  actual in-game turn rate, to match sensitivity for games not on that list. Both are per the
  [KovaaK's](../resources/trainers/kovaaks.md) resource page.
- **Aimlabs** has a built-in Sensitivity Finder for calibrating your in-app sensitivity, per the
  [Aimlabs](../resources/trainers/aimlabs.md) resource page.
- **Independent cross-game calculators** such as [mouse-sensitivity.com](https://www.mouse-sensitivity.com/)
  cover a range of popular titles. Use one if the tools above don't cover your game or trainer.

## When to change sensitivity, and when not to

!!! myth "Changing your sensitivity will ruin your aim"
    A change costs some short-term readjustment rather than any lasting setback.
    [Myths](../myths.md#changing-your-sensitivity-will-ruin-your-aim){ .aim-myth-more }

Switching sensitivity on purpose is one way people try to break a plateau. Starting from an
unfamiliar setting can reset your sense of what feels "normal" and open room to improve.[^muscle]

So don't avoid changing your sensitivity at all. Avoid changing it constantly without a reason,
since every change costs you some readjustment time. See
[Progress and Plateaus](../training/progress-and-plateaus.md) for more on working through a stalled
score.

**Do this next.** Work out your current cm/360, then leave that sensitivity alone long enough to
judge it fairly.

## Further resources

- [KovaaK's](../resources/trainers/kovaaks.md): built-in sensitivity converter and the
  Sensitivity Matcher tool for matching sensitivity to games it does not directly support.
- [Aimlabs](../resources/trainers/aimlabs.md): built-in Sensitivity Finder for calibrating
  sensitivity inside the trainer.

[^cm360]: Aimlabs, [A quick explainer on cm/360 and the common cm/360 by game](https://aimlabs.com/articles/aimlabs/a-quick-explainer-on-cm-360-and-the-common-cm-360-by-game/)
[^edpi]: ProSettings.net, [What is DPI and eDPI?](https://prosettings.net/blog/what-is-dpi-edpi/)
[^muscle]: Voltaic, [Muscle memory](https://blog.voltaic.gg/muscle-memory/)
