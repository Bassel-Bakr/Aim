---
title: "Setup and Gear"
tags:
  - beginner
related:
  - page: wiki/getting-started/sensitivity.md
    why: choosing and converting the sensitivity your setup runs.
  - page: wiki/training/health.md
    why: posture and recovery over long sessions.
---

!!! warning "Draft"
    Written from public sources, pending review.

Good aim training starts with gear and settings that get out of your way. None of it requires
expensive hardware.

- **Fit beats sensor.** A mouse that matches your hand matters more than its spec sheet.
- **Cover your sensitivity range.** A pad too small forces you to lift mid-turn.
- **Sit in a position you can hold.** Comfort over a full session beats any single piece of gear.
- **Turn acceleration off.** Raw input on, mouse and Windows acceleration off.

## Explanation

**Mouse: shape and weight over sensor.** Nearly every modern gaming mouse sensor is accurate enough
that most players can't feel the difference. So the sensor spec sheet matters far less than
fit.[^REF-57]

Shape matters most. A mouse that doesn't match your hand size and grip style causes fatigue and
inconsistent aim, however good its sensor.[^REF-57]

Weight is a smaller, personal factor after shape. Some players prefer very light mice for lower
inertia; others find them harder to control.[^REF-57]

**Mousepad: control versus speed surfaces.** Pad surfaces trade glide against stopping power.

- A **speed** surface uses a low-friction weave for fast, consistent glide in every direction.
- A **control** surface uses a denser weave that adds drag, for finer, more deliberate movements.
- A **balanced** surface sits between the two.[^REF-47]

Pad size matters alongside surface. A pad too small to cover your full sensitivity range forces you
to lift and reset your mouse mid-turn.

**Grip styles.** No grip is strictly correct. Pick the one that lets you hold a comfortable,
repeatable position for as long as you play.[^REF-66]

- **Palm grip** rests your whole palm and fingers on the mouse and moves it mostly from the forearm
  and elbow. It is the most stable and comfortable, with less wrist mobility.[^REF-64]
- **Claw grip** keeps the heel of your palm on the back while your fingers arch onto the buttons. It
  balances stability and mobility, but can tire the fingers over long sessions.[^REF-64]
- **Fingertip grip** touches the mouse with your fingertips only and moves it with fingers and
  wrist. It allows fast micro-adjustments, with less stability.[^REF-64]

In a 2024 study of 22 players using their own grips, grip made no significant difference to
flicking or tracking performance.[^REF-65] Its tracking target moved at a constant speed, so that
result is narrower than it sounds.

**Posture and arm position.** Your wrist position, and how long you hold it, matter more for comfort
than which mouse or keyboard you use.[^REF-1]

Keep your upper arm relaxed against your torso, elbow supported, rather than reaching or lifting
your shoulder to use the mouse. Keep your screen roughly an arm's length away, with your eyes
meeting near the top quarter of the monitor.[^REF-1]

A setup you can comfortably hold for a full practice session does more for your consistency than
any single piece of gear.

**Monitor refresh rate and FPS.** A higher refresh rate reduces the time between frames the display
can show. For example, a 240Hz display refreshes roughly 2.7ms faster per frame than a 144Hz
display.[^REF-23]

Blur Busters' testing also found that running your in-game frame rate above your monitor's refresh
rate, with V-Sync off, still measurably reduces input lag.[^REF-23]

So both help you see and react to targets sooner: a higher refresh-rate monitor, and a frame rate
that comfortably exceeds it.

## Essential settings

**Raw input: on.** With raw input enabled, a game reads mouse movement more directly from the
device, instead of only through the Windows pointer path. That makes sensitivity more
predictable.[^REF-39]

Turn it on in any first-person or third-person shooter that supports it. It is no substitute for a
clean sensor or stable frame times, but it is worth checking.[^REF-39]

**Mouse acceleration: off to start.** Acceleration changes how far the cursor or camera moves based
on how fast you physically move the mouse. Off is a sensible default while you learn, so one hand
movement always means one turn.

Some players choose acceleration on purpose later, and [Raw Accel](../resources/tools/rawaccel.md)
is the tool for that. Check both your game's settings and your mouse software for an acceleration
toggle.

**Windows "Enhance pointer precision": off.** This is Windows' own built-in pointer acceleration.
It is under **Settings > Bluetooth & devices > Mouse > Additional mouse settings > Pointer
Options**, or **Control Panel > Mouse > Pointer Options** on older builds.[^REF-38]

Most competitive games apply raw input and bypass this setting. Leaving it on still affects desktop
use and any game without raw input, so turning it off is the safer default.

**Do this next.** Before your next session, check all three settings above, in your game and in
Windows.

## Resources

- [KovaaK's](../resources/trainers/kovaaks.md): where to put a consistent sensitivity and settings
  to work once your gear and Windows settings are sorted out.
- [Guides](../resources/guides.md#gear-and-settings): guides on gear, grips and settings.
