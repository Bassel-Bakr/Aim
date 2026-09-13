---
title: "Setup and Gear"
tags:
  - beginner
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
that most players can't feel the difference. So the sensor spec sheet matters far less than fit, per
an [XDA Developers gaming mouse buying guide](https://www.xda-developers.com/gaming-mouse-buying-guide/).

Shape matters most. A mouse that doesn't match your hand size and grip style causes fatigue and
inconsistent aim, however good its sensor, per the same guide.

Weight is a smaller, personal factor after shape. Some players prefer very light mice for lower
inertia; others find them harder to control.[^xda]

**Mousepad: control versus speed surfaces.** Pad surfaces trade glide against stopping power.

- A **speed** surface uses a low-friction weave for fast, consistent glide in every direction.
- A **control** surface uses a denser weave that adds drag, for finer, more deliberate movements.
- A **balanced** surface sits between the two.[^qck]

Pad size matters alongside surface. A pad too small to cover your full sensitivity range forces you
to lift and reset your mouse mid-turn.

**Grip styles.** No grip is strictly correct. Pick the one that lets you hold a comfortable,
repeatable position for as long as you play.

- **Palm grip** rests your whole hand flat on the mouse and moves it mostly from the elbow and
  shoulder. It is the most comfortable grip to sustain over long sessions.[^grip]
- **Claw grip** keeps your palm on the back of the mouse while your fingers arch up off the buttons.
  It trades some comfort for faster flicks and clicking.[^grip]
- **Fingertip grip** lifts your palm off the mouse entirely, so only your fingertips make contact.
  It maximizes quick micro-adjustments, at the cost of finger stamina.[^grip]

**Posture and arm position.** Your wrist position, and how long you hold it, matter more for comfort
than which mouse or keyboard you use.[^1hp]

Keep your upper arm relaxed against your torso, elbow supported, rather than reaching or lifting
your shoulder to use the mouse. Keep your screen roughly an arm's length away, with your eyes
meeting near the top quarter of the monitor.[^1hp]

A setup you can comfortably hold for a full practice session does more for your consistency than
any single piece of gear.

**Monitor refresh rate and FPS.** A higher refresh rate reduces the time between frames the display
can show. For example, a 240Hz display refreshes roughly 2.7ms faster per frame than a 144Hz
display.[^blur]

Blur Busters' testing also found that running your in-game frame rate above your monitor's refresh
rate, with V-Sync off, still measurably reduces input lag.[^blur]

So both help you see and react to targets sooner: a higher refresh-rate monitor, and a frame rate
that comfortably exceeds it.

## Essential settings

- **Raw input: on.** With raw input enabled, a game reads mouse movement more directly from the
  device, instead of relying only on the Windows pointer path. That makes sensitivity more
  predictable. Turn it on in any first-person or third-person shooter that supports it.[^mousecfg]
  It is not a substitute for a clean sensor or stable frame times, per the same guide. It is just a
  setting worth checking is enabled.
- **Mouse acceleration: off.** Acceleration changes how far the cursor or camera moves based on how
  fast you physically move the mouse. That breaks the consistent muscle memory aim training depends
  on. Check both your game's settings and your mouse manufacturer's software for an acceleration
  toggle.
- **Windows "Enhance pointer precision": off.** This is Windows' own built-in pointer acceleration.
  It is under **Settings > Bluetooth & devices > Mouse > Additional mouse settings > Pointer
  Options**, or **Control Panel > Mouse > Pointer Options** on older builds.[^ms-mouse] Most
  competitive games apply raw input and bypass this setting entirely. But leaving it on can still
  affect desktop use and any game without raw input, so turning it off is the safer default.

**Do this next.** Before your next session, check all three settings above, in your game and in
Windows.

## Further resources

- [KovaaK's](../resources/trainers/kovaaks.md): where to put a consistent sensitivity and settings
  to work once your gear and Windows settings are sorted out.

[^xda]: XDA Developers, [gaming mouse buying guide](https://www.xda-developers.com/gaming-mouse-buying-guide/)
[^qck]: SteelSeries, [QcK Performance product page](https://steelseries.com/qck-performance)
[^grip]: WASD Life, [mouse grip styles](https://wasdlife.com/mice/mouse-grip-styles/)
[^1hp]: 1HP, [Esports health: it starts with ergonomics and posture](https://1-hp.org/blog/hpforgamers/esports-health-it-starts-with-ergonomics-and-posture/)
[^blur]: Blur Busters, [Benefits of frame rate above refresh rate](https://blurbusters.com/faq/benefits-of-frame-rate-above-refresh-rate/)
[^mousecfg]: Mouse DPI Analyzer, [Best mouse settings for gaming](https://mousedpianalyzer.com/post/best-mouse-settings-for-gaming/)
[^ms-mouse]: Microsoft, [Change mouse settings](https://support.microsoft.com/en-us/windows/change-mouse-settings-e81356a4-0e74-fe38-7d01-9d79fbf8712b)
