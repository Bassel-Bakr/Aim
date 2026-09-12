---
title: "How Aim Works"
tags:
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

Moving a crosshair onto a target is a chain of small decisions: which joint does the moving, how
fast you close the distance versus how precisely you land, how continuous that motion is, and
whether you're tracking where a target actually is or guessing where it's headed next. None of
this is exotic, but naming the pieces gives you something specific to fix instead of a vague sense
that your aim "feels off."

## Explanation

**Arm, wrist, and finger aim.** Mouse aim isn't one motion; different joints handle different
parts of it. Fingers make small, precise adjustments, the wrist handles moderate movements, and
the upper arm and shoulder drive large sweeping turns, per [Aimlabs](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/).
Which joint dominates shifts with sensitivity and target speed: wrist-led aim tends to suit
precision holds where corrections are small, while arm-led aim is needed for the larger motions a
faster-paced game demands, per the same article. Most players already blend both without thinking
about it, so treating your fingers, wrist, and arm as parts that each do their own job is more
useful than picking a side in an "arm versus wrist" debate, per [Aimlabs](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/).

**Large corrections versus micro-adjustments.** The same division of labor explains why a big
flick onto a far-away target and a small correction to stay on a target you're already tracking
feel like different skills: one leans on the arm and shoulder, the other on the fingers and wrist,
per [Aimlabs](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/).
[Clicking](../skills/clicking.md) and [Switching](../skills/switching.md) scenarios tend to
emphasize acquisition, jumping to a new target; [Tracking](../skills/tracking.md) scenarios tend
to emphasize correction, staying on a target that's already moving.

**The speed-accuracy trade-off.** Speeding up shortens the window your eyes and hands get to
correct a movement mid-flight, and a shorter correction window means more misses. This trade-off holds across aimed
movements generally and is formalized in motor-control research as Fitts's law, which relates how
long a movement takes to how far it travels and how small the target is, per a
[Human Kinetics summary of that research](https://us.humankinetics.com/blogs/excerpt/understanding-fitts-law).
In practice, chasing maximum speed before your accuracy is solid tends to build habits that are
hard to undo later, while building accuracy at a manageable pace first, then gradually pushing
speed, tends to hold up as you get faster, per [Aimlabs](https://aimlabs.com/articles/aimlabs/the-speed-accuracy-tradeoff-and-what-it-means-for-your-aim-training/).

**Smoothness.** Smoothness isn't a separate skill from tracking or flicking so much as a quality
that runs through all of them: whether your crosshair moves as one continuous motion or as a
series of separate corrections. The underlying mechanic is speed matching: your crosshair moves at
the same rate the target does in the moment, rather than lagging behind and then snapping forward
to catch up. That same continuity applies to direction changes too, which read as a smooth
decelerate-and-re-accelerate rather than a hard stop,
per [Aimlabs](https://aimlabs.com/articles/aimlabs/what-smoothness-actually-is-and-why-it-makes-everything-else-better/).
The same source notes that a lot of "smoothness problems" are really tension problems: gripping
the mouse too tightly gets in the way of fluid motion no matter how much you practice.

**Reaction versus prediction.** Reactive tracking means following where a target actually is and
responding to each change in its direction as it happens; predictive tracking means anticipating
where it's going and aiming ahead of it. Prediction can look tighter when it works, but it breaks
down the moment an opponent changes direction to bait it, while reactive tracking has a small
built-in lag but can't be juked the same way, per [Aimlabs](https://aimlabs.com/articles/aimlabs/stop-predicting-and-start-reacting-get-better-at-reactive-tracking/).

## Common mistakes

- Treating arm and wrist aim as a single either/or choice instead of letting fingers, wrist, and
  arm each handle the motion they're suited for, which limits both precision and range.
- Pushing scenario speed before accuracy at a slower pace is solid, which builds habits that are
  harder to unlearn later than they were to avoid, per [Aimlabs](https://aimlabs.com/articles/aimlabs/the-speed-accuracy-tradeoff-and-what-it-means-for-your-aim-training/).
- Anticipating where a target is going instead of tracking where it is, which falls apart against
  any opponent using evasive movement.
- Treating a jerky track as purely a tracking problem to practice through, when it's often a
  tension problem, per [Aimlabs](https://aimlabs.com/articles/aimlabs/what-smoothness-actually-is-and-why-it-makes-everything-else-better/).

## How to train it

Isolate one fundamental at a time rather than practicing all of them at once. A slow, predictable
scenario is a better place to fix smoothness and speed matching than a fast, erratic one; once
that's solid, scenarios that add evasive movement push you toward reactive tracking instead of
prediction. [KovaaK's](../resources/trainers/kovaaks.md) and [Aimlabs](../resources/trainers/aimlabs.md)
both organize their libraries around a similar static/dynamic and precise/reactive split, and
[Voltaic](../resources/communities/voltaic.md)'s benchmark categories (precise, reactive, control;
speed, evasive, stability) map onto the same fundamentals. See
[Practice Principles](practice-principles.md) for how to structure that practice so it sticks.

## Further resources

- [Aimlabs](../resources/trainers/aimlabs.md): source of the mechanics articles above, and the
  trainer to practice arm/wrist balance, pacing, smoothness, and reactive tracking directly.
- [KovaaK's](../resources/trainers/kovaaks.md): scenario library organized around the same
  static/dynamic and precise/reactive split.
- [Voltaic](../resources/communities/voltaic.md): benchmark categories built around these same
  fundamentals.
