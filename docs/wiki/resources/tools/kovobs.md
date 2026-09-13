---
title: "KovOBS"
tags:
  - tool
---

!!! warning "Draft"
    Written from public sources, pending review.

**Links:** [GitHub](https://github.com/Bassel-Bakr/KovOBS)

!!! note "Disclosure"
    KovOBS is written by this wiki's maintainer.

## What it is

A small open-source desktop application that watches your [KovaaK's](../trainers/kovaaks.md) stats
folder. When you set a personal best, it tells OBS to save a replay-buffer clip. The run is recorded
without you reaching for a hotkey mid-scenario.[^REF-035]

## Who it suits

Players who already record or stream their training and want their best runs kept automatically.
It is not a training or [benchmark](../../training/benchmarks.md) tool: it captures video, and
nothing about your scores or ranks.

## What it covers

- **Personal-best detection**: reads the stats files KovaaK's writes after each run and triggers
  only when a run beats your previous best for that scenario.[^REF-035]
- **Replay saving and screenshots**: saves the OBS replay buffer, optionally takes a screenshot,
  and trims the resulting clip.[^REF-035]
- **Aimbeast support**, marked experimental rather than finished.[^REF-035]
- **Setup without config files**: a graphical interface for choosing the stats folder and entering
  the OBS WebSocket password.[^REF-035]

## Requirements

OBS Studio 28 or later with the built-in WebSocket server and Replay Buffer both enabled. Windows
is the supported platform; the project notes Linux as reported working but untested.[^REF-035]

## Key content

- [KovOBS on GitHub](https://github.com/Bassel-Bakr/KovOBS): source, releases, and setup
  instructions.

## Our take

Narrow by design, which is the point. It removes the one step most likely to be missed: hitting save
after a run you did not expect to be your best.

The requirements are the real constraint, since it depends on OBS's replay buffer already running.
And a personal best is only as meaningful as the scenario it was set in.

## Related pages

- [KovaaK's](../trainers/kovaaks.md)
- [Progress and Plateaus](../../training/progress-and-plateaus.md)
- [Benchmarks](../../training/benchmarks.md)

## References
