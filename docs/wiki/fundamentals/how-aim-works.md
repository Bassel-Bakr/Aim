---
title: "How Aim Works"
tags:
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

Aim is a chain of small decisions. Name the pieces and you have something specific to fix, instead
of aim that "feels off".

- **Joints split the work.** Fingers, wrist, arm. Not a side to pick.
- **Speed costs accuracy.** The trade-off is measurable, not a matter of discipline.
- **Smoothness is continuity.** One motion, not a chain of corrections.
- **React, don't predict.** Prediction breaks the moment someone baits it.

## Explanation

**Arm, wrist, and finger aim.** Mouse aim is not one motion. Fingers make small, precise
adjustments. The wrist handles moderate movements, and the upper arm and shoulder drive the large
sweeping turns.[^wrist-vs-arm]

Which joint leads shifts with sensitivity and target speed. Wrist-led aim suits precision holds
where corrections are small. Arm-led aim is needed for the larger motions a faster game
demands.[^wrist-vs-arm]

Most players already blend both without thinking about it. Treating fingers, wrist, and arm as
parts that each do their own job beats picking a side in an "arm versus wrist" debate.

**Large corrections versus micro-adjustments.** The same division of labor explains why a big flick
and a small correction feel like different skills. One leans on the arm and shoulder, the other on
the fingers and wrist.[^wrist-vs-arm]

[Clicking](../categories/clicking.md) and [Switching](../categories/switching.md) scenarios
emphasize acquisition: jumping to a new target. [Tracking](../categories/tracking.md) scenarios
emphasize correction: staying on one that is already moving.

**The speed-accuracy trade-off.** Speeding up shortens the window your eyes and hands get to
correct a movement mid-flight. A shorter window means more misses.

Motor-control research formalizes this as Fitts's law. It ties movement time to how far the
movement travels and how small the target is.[^fitts]

In practice: chase maximum speed before your accuracy is solid and you build habits that are hard
to undo later. Build accuracy at a manageable pace first, then push speed.[^speed-accuracy]

**Smoothness.** Not a separate skill from tracking or flicking. A quality running through both:
does your crosshair move as one continuous motion, or as a series of separate corrections?

The mechanic underneath is speed matching. Your crosshair moves at the rate the target is moving
right now, instead of lagging behind and snapping forward to catch up. Direction changes follow the
same rule: decelerate and re-accelerate, no hard stop.

Most "smoothness problems" are really tension problems. Gripping the mouse too tightly blocks fluid
motion no matter how much you practice.[^smoothness]

**Reaction versus prediction.** Reactive tracking follows where a target actually is, responding to
each change in direction as it happens. Predictive tracking aims ahead of it.

Prediction looks tighter when it works, and breaks the moment an opponent changes direction to bait
it. Reactive tracking carries a small built-in lag, but cannot be juked the same way.[^reactive]

## Common mistakes

- Treating arm and wrist aim as an either/or instead of letting each joint do the motion it suits.
  See [Myths](../myths.md#arm-aiming-is-strictly-better-than-wrist-aiming).
- Pushing scenario speed before accuracy is solid, which builds habits that are harder to unlearn
  than they were to avoid.[^speed-accuracy]
- Aiming where a target is going instead of where it is, which falls apart against evasive
  movement. See [Myths](../myths.md#good-tracking-means-predicting-where-the-target-will-go).
- Training through a jerky track when the cause is a tight grip.[^smoothness]

## How to train it

Isolate one fundamental at a time rather than practicing all of them at once.

A slow, predictable scenario is the place to fix smoothness and speed matching. Once that holds,
scenarios with evasive movement push you toward reacting instead of predicting.

[KovaaK's](../resources/trainers/kovaaks.md) and [Aimlabs](../resources/trainers/aimlabs.md) both
organize their libraries around a static/dynamic and precise/reactive split.
[Voltaic](../resources/communities/voltaic.md)'s benchmark categories (precise, reactive, control;
speed, evasive, stability) map onto the same fundamentals.

**Do this next.** Pick the one fundamental your aim fails on most and run a single slow scenario
for it. [Practice Principles](practice-principles.md) covers how to structure that so it sticks.

## Related pages

- [Practice Principles](practice-principles.md): how to structure practice around these mechanics.
- [Categories](../categories/index.md): the three categories these mechanics add up to.
- [Underaiming](../techniques/underaiming.md): restraint over the corrections covered here.

## Resources

- [Aimlabs](../resources/trainers/aimlabs.md): source of the mechanics articles above, and the
  trainer to practice arm/wrist balance, pacing, smoothness, and reactive tracking directly.
- [KovaaK's](../resources/trainers/kovaaks.md): scenario library organized around the same
  static/dynamic and precise/reactive split.
- [Voltaic](../resources/communities/voltaic.md): benchmark categories built around these same
  fundamentals.
- [Guides](../resources/guides.md#how-aim-works): guides on the mechanics of aim.

## References

[^wrist-vs-arm]: Aimlabs, [Wrist aiming vs arm aiming: why not both?](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/)
[^fitts]: Human Kinetics, [Understanding Fitts's law](https://us.humankinetics.com/blogs/excerpt/understanding-fitts-law)
[^speed-accuracy]: Aimlabs, [The speed-accuracy tradeoff and what it means for your aim training](https://aimlabs.com/articles/aimlabs/the-speed-accuracy-tradeoff-and-what-it-means-for-your-aim-training/)
[^smoothness]: Aimlabs, [What smoothness actually is and why it makes everything else better](https://aimlabs.com/articles/aimlabs/what-smoothness-actually-is-and-why-it-makes-everything-else-better/)
[^reactive]: Aimlabs, [Stop predicting and start reacting: get better at reactive tracking](https://aimlabs.com/articles/aimlabs/stop-predicting-and-start-reacting-get-better-at-reactive-tracking/)
