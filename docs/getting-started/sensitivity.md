---
title: "Sensitivity"
tags:
  - sensitivity
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

Mouse sensitivity controls how far your view turns for a given amount of hand movement. Because
DPI and in-game sensitivity numbers do not mean the same thing from one game to the next, players
compare sensitivity using cm/360 or eDPI instead of raw settings. There is no single correct
sensitivity, but picking one deliberately, and understanding how to carry it between games, saves
you from relearning your aim every time you switch titles.

## Explanation

**cm/360** is the physical distance your mouse travels across your pad to turn your in-game view a
full 360 degrees. You can measure it by aiming at a fixed point, turning a full circle, and
measuring how far your hand moved, or by using a calculator that combines your DPI and in-game
sensitivity value, per [Aimlabs' cm/360 explainer](https://aimlabs.com/articles/aimlabs/a-quick-explainer-on-cm-360-and-the-common-cm-360-by-game/).
Because it is measured in real-world distance, cm/360 is comparable across any game, engine, or
mouse.

**eDPI** (effective DPI) is your mouse DPI multiplied by your in-game sensitivity multiplier, for
example 800 DPI × 0.27 sensitivity = 216 eDPI, per [ProSettings.net](https://prosettings.net/blog/what-is-dpi-edpi/).
Two players with the same eDPI move their crosshair the same amount for the same hand movement in
that game, regardless of their raw DPI or sensitivity values. Unlike cm/360, eDPI is only
comparable **within one game**, because different games apply different scaling to the sensitivity
multiplier, per [ProSettings.net](https://prosettings.net/blog/what-is-dpi-edpi/).

**Low versus high sensitivity** is a trade-off in how much of the work your arm does versus your
wrist and fingers. A lower sensitivity (higher cm/360) spreads a given turn over more physical
distance, which gives you more room to correct small tracking errors, but demands a larger
mousepad and more arm movement. A higher sensitivity (lower cm/360) lets you turn and flick with
small wrist movements and less desk space, but the same small hand tremor produces a much larger
error on screen. Some sources, including [Aimlabs](https://aimlabs.com/articles/aimlabs/a-quick-explainer-on-cm-360-and-the-common-cm-360-by-game/),
publish typical cm/360 ranges used by players per game; treat these as a starting reference rather
than a target, since the article itself notes the right number depends on your equipment, desk
space, posture, and comfort.

## Choosing a starting point

Rather than searching for an "ideal" number, pick a sensitivity that lets you comfortably reach
every part of your mousepad while still being able to turn 180 degrees without lifting your mouse,
then leave it alone long enough to judge it fairly. If you genuinely have no reference point,
looking at the range other players in your game use (via a tool like the one linked above) is a
reasonable way to pick a starting value to adjust from, not a rule to lock into.

## Converting sensitivity between games and trainers

When you play more than one game, or move between a game and an aim trainer, matching your
physical sensitivity keeps your muscle memory consistent instead of forcing you to relearn your
aim per title:

- **KovaaK's** publishes an official web-based [sensitivity converter](https://kovaaks.com/kovaaks/sens-converter)
  for a fixed list of supported games, and separately maintains an open-source
  [Sensitivity Matcher](https://github.com/KovaaK/SensitivityMatcher) tool that measures your
  actual in-game turn rate to match sensitivity for games not on that list, per the
  [KovaaK's](../resources/trainers/kovaaks.md) resource page.
- **Aimlabs** has a built-in Sensitivity Finder for calibrating your in-app sensitivity, per the
  [Aimlabs](../resources/trainers/aimlabs.md) resource page.
- Independent, cross-game calculators such as [mouse-sensitivity.com](https://www.mouse-sensitivity.com/)
  cover conversion for a range of popular titles if your specific game or trainer is not covered
  by the tools above.

## When to change sensitivity, and when not to

A common fear is that changing sensitivity will permanently damage your aim. Voltaic's own
breakdown of "muscle memory" in aiming pushes back on this directly: changing your sensitivity
does not ruin your aim, it only requires a period of readjustment, and the community has plenty of
anecdotal cases of players changing sensitivity constantly, even using sensitivity randomizers,
without a lasting penalty, per [Voltaic](https://blog.voltaic.gg/muscle-memory/). The same article
notes that deliberately changing sensitivity is sometimes suggested as a way to break out of a
plateau, since a new sensitivity gives you a fresh starting point to improve from, per
[Voltaic](https://blog.voltaic.gg/muscle-memory/). The practical takeaway is not to avoid changing
your sensitivity out of fear, but to avoid changing it constantly without a reason, since every
change costs you some readjustment time. See [Progress and Plateaus](../training/progress-and-plateaus.md)
for more on working through a stalled score.

## Further resources

- [KovaaK's](../resources/trainers/kovaaks.md): built-in sensitivity converter and the
  Sensitivity Matcher tool for matching sensitivity to games it does not directly support.
- [Aimlabs](../resources/trainers/aimlabs.md): built-in Sensitivity Finder for calibrating
  sensitivity inside the trainer.
