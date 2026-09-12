# Myths Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `docs/wiki/myths.md`, a wiki page answering eight false claims aim players repeat as
fact, plus an `.aim-myth` block that places a short correction on the page whose subject it
corrects.

**Architecture:** Two surfaces, one source of truth. The hub page carries every myth in full —
claim, what sources say, what to do instead, citation. The inline block carries a two-sentence
correction and a link to the hub anchor, and never carries a citation. Three entry points reach the
page: nav, the landing page card grid, and the wiki index card grid.

**Tech Stack:** Markdown built by Zensical with the Material theme. `admonition`, `attr_list`,
`footnotes`, `md_in_html` and `pymdownx.details` are already enabled in `zensical.toml`. Checks are
`scripts/check_pages.py` and `zensical build --clean`.

**Spec:** `specs/2026-09-12-myths-design.md`

## Global Constraints

- Every wiki page carries the draft banner verbatim: `!!! warning "Draft"` with the indented body
  `Written from public sources, pending review.`
- Every `tags:` value must be in `ALLOWED_TAGS` in `scripts/check_pages.py`, or the check fails.
- Version 1 introduces no new outbound URL. Every citation reuses a source already cited on the
  site, so the weekly lychee run gains nothing new to break.
- Hub headings state the myth as the false claim, never as the correction.
- Inline `.aim-myth` blocks are at most two sentences plus a hub link, and carry no footnote.
- `.aim-cards` items carry exactly one link each, written as the item's title. A second link in the
  same item falls under the stretched hit area and cannot be clicked.
- Prose is written in this repository's own words from the cited source. Do not paste source
  wording, and do not attribute a claim to a source that does not make it.
- `zensical build` does not run with `--strict`, so link problems appear as warnings and the exit
  code alone is not proof. Read the build output.

## Two corrections to the spec

Both were found while grounding the eight entries against what the cited sources actually support.
Apply the plan as written here; the spec's own wording on these two points is superseded.

**1. The entry "Accuracy comes first, so train slow" is dropped.** It is not a myth on this site:
`docs/wiki/fundamentals/how-aim-works.md` states the opposite as fact, that pushing speed before
accuracy is solid builds habits that are harder to unlearn, citing the Aimlabs speed-accuracy
article. Publishing it as a myth would contradict a live page. It is replaced by **"Changing your
sensitivity will ruin your aim"**, which `docs/wiki/getting-started/sensitivity.md` already names
as "a common fear" and answers from the Voltaic muscle-memory piece. The count stays at eight.

**2. The version 1 inline block moves from `progress-and-plateaus.md` to `sensitivity.md`.** The
spec assumed a standalone muscle-memory passage in `docs/wiki/training/progress-and-plateaus.md`.
There is none: that page mentions the muscle-memory piece only inside "Ways past a plateau", as
one route past a stall, which is guidance rather than a claim being corrected. The passage that
is a myth stated in prose lives in `docs/wiki/getting-started/sensitivity.md`, under "When to
change sensitivity, and when not to", opening "A common fear is that changing sensitivity will
permanently damage your aim." That is the passage Task 2 converts. `progress-and-plateaus.md` is
not modified by this plan, and its `[^muscle]` footnote stays where it is.

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `docs/wiki/myths.md` | Canonical treatment of all eight myths, with the citations | 1 |
| `scripts/check_pages.py` | Allows the `myth` tag | 1 |
| `zensical.toml` | Nav entry inside the `Wiki` list | 1 |
| `docs/assets/stylesheets/aim.css` | `.aim-myth` component, plus the header component list | 2 |
| `docs/wiki/getting-started/sensitivity.md` | First real use of the inline block | 2 |
| `docs/index.md` | Card in the `## Where to start` grid | 3 |
| `docs/wiki/index.md` | Card in the `## Sections` grid | 3 |

Three tasks. Task 1 ships a reachable, checked page. Task 2 adds the component and proves it on
real content. Task 3 adds the two card entries. Each ends with both checks run and a commit.

---

### Task 1: The hub page, its tag, and its nav entry

**Files:**
- Create: `docs/wiki/myths.md`
- Modify: `scripts/check_pages.py:16-20` (the `ALLOWED_TAGS` set)
- Modify: `zensical.toml` (the `Wiki` list in `nav`, after the `Resources` entry)

**Interfaces:**
- Consumes: nothing.
- Produces: eight `h2` headings whose generated anchors Task 2 and Task 3 link to. The anchor is
  the heading lowercased, with spaces replaced by hyphens and apostrophes and commas dropped. The
  two anchors later tasks use are `#reps-burn-a-motion-into-muscle-memory` and
  `#changing-your-sensitivity-will-ruin-your-aim`.

- [ ] **Step 1: Add the `myth` tag to the checker**

In `scripts/check_pages.py`, the `ALLOWED_TAGS` set becomes:

```python
ALLOWED_TAGS = {
    "community", "trainer", "tool",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
    "myth",
}
```

- [ ] **Step 2: Run the checker to watch it fail on the missing page**

Run: `python scripts/check_pages.py`

Expected: PASS, with no output about `myths.md`, because the page does not exist yet. This step
confirms the checker currently sees nothing to complain about, so any failure after Step 3 comes
from the new page rather than from a pre-existing problem. If it fails here, stop and fix the
pre-existing failure before continuing.

- [ ] **Step 3: Write the hub page**

Create `docs/wiki/myths.md` with exactly this content:

````markdown
---
title: "Myths"
tags:
  - myth
---

!!! warning "Draft"
    Written from public sources, pending review.

Some of the most repeated advice in aim training is a claim that the sources it appeals to do not
actually make. This page collects those claims, states each one the way a player would say it, and
answers it from the same sources the rest of this wiki cites.

A myth here is a claim someone would state as fact: "lower sensitivity means better aim." That is
a different thing from a habit that costs you progress, such as only running the scenarios you
already score well in. Habits like that belong to the **Common mistakes** section of the page whose
subject they belong to, and they stay there.

## Reps burn a motion into muscle memory

**The claim.** Repeat a flick enough times and the motion is stored. From then on it replays on
demand, so anything that disturbs it, a new sensitivity or a new mouse, wipes out the work.

**What sources say.** Voltaic's breakdown of muscle memory in aiming pushes back on the second
half directly. Changing your sensitivity costs some short-term readjustment rather than any lasting
setback, and the piece points to community members who swap settings often, some rolling a new
sensitivity at random, with no long-run drop in their aim.[^muscle] A stored motion that could be
wiped would not survive that.

**What to do instead.** Judge practice by whether your read of a target and your corrections are
getting better, which is what carries across settings, and read a score as a trend across several
[benchmark](training/benchmarks.md) runs rather than as the state of a stored motion.

## Changing your sensitivity will ruin your aim

**The claim.** Your current sensitivity is what your hand knows. Change it and you start from
nothing, so the safe move is to never touch it again.

**What sources say.** This one is common enough that this wiki's own
[Sensitivity](getting-started/sensitivity.md) page names it as a fear rather than a finding.
Voltaic's muscle-memory piece answers it: a change costs short-term readjustment, not a lasting
setback.[^muscle] The same piece lists a deliberate sensitivity change among the ways players work
past a stall, on the logic that an unfamiliar setting puts you back where there is obvious room to
improve.[^muscle]

**What to do instead.** Change it for a reason and then leave it alone long enough to judge it.
What costs you is changing constantly, since every change spends readjustment time, not the fact
of changing at all. See [Progress and Plateaus](training/progress-and-plateaus.md) for when a
change is worth making.

## Lower sensitivity means better aim

**The claim.** The lower your sensitivity, the more precise your aim. Pros play low, so low is
correct, and a high sensitivity is a habit to grow out of.

**What sources say.** It is a trade-off in which joints do the work, not a ranking. A lower
sensitivity spreads a turn over more physical distance, which leaves more room to correct small
errors but demands a larger mousepad and more arm movement; a higher sensitivity turns on small
wrist movements and less desk space, but magnifies the same small tremor on screen. Aimlabs
publishes typical cm/360 ranges per game and notes in the same article that the right number
depends on your equipment, desk space, posture and comfort, which makes the ranges a starting
reference rather than a target.[^cm360]

**What to do instead.** Pick a sensitivity that reaches every part of your mousepad while still
letting you turn 180 degrees without lifting the mouse, then leave it alone long enough to judge it
fairly. [Sensitivity](getting-started/sensitivity.md) covers cm/360 and eDPI, the two ways to
compare a setting to someone else's.

## Arm aiming is strictly better than wrist aiming

**The claim.** Arm aim is the correct technique and wrist aim is a beginner habit, so the fix for
inconsistency is to aim from the arm and stop using your wrist.

**What sources say.** Aimlabs treats the joints as a division of labour rather than a choice:
fingers make small precise adjustments, the wrist handles moderate movements, and the upper arm and
shoulder drive large sweeping turns.[^wrist-vs-arm] Which one leads shifts with sensitivity and
target speed, wrist-led aim suiting precision holds where corrections are small and arm-led aim
being needed for the larger motions a faster game demands.[^wrist-vs-arm] Most players already
blend both without thinking about it.[^wrist-vs-arm]

**What to do instead.** Ask which joint suits the movement in front of you rather than which one
to commit to. [How Aim Works](fundamentals/how-aim-works.md) covers the same split as it applies to
large corrections versus micro-adjustments.

## Good tracking means predicting where the target will go

**The claim.** Strong tracking is anticipation. Read the movement pattern, aim where the target is
going, and your crosshair is waiting when it arrives.

**What sources say.** Prediction can look tighter when it works, and it breaks the moment an
opponent changes direction to bait it. Reactive tracking, following where the target actually is
and responding to each change as it happens, carries a small built-in lag but cannot be juked the
same way.[^reactive]

**What to do instead.** Train the reaction. Scenarios with evasive movement push you toward
responding rather than anticipating, because anticipation stops paying there.
[Tracking](categories/tracking.md) covers the category this sits in.

## A plateau means you have hit your ceiling

**The claim.** Your score stopped moving, so you have found your limit. Talent set it, and more
training will not move it.

**What sources say.** Motor-learning research treats a stretch of flat performance as an ordinary,
expected stage of learning rather than evidence that something has broken.[^plateau-study] The
same literature describes early learning as large, inconsistent jumps followed by a slower stage of
smaller refinements, so gains shrinking is the normal shape of progress.[^hk-stages] A flat stretch
also has causes you can act on, fatigue among them: training hard without enough recovery can tip
into overreaching and then overtraining, where performance declines rather than
stalls.[^overtraining]

**What to do instead.** Judge the trend across several [benchmark](training/benchmarks.md) runs
spaced weeks apart rather than any one result, and if a flat score comes with feeling generally run
down, treat it as fatigue first. [Progress and Plateaus](training/progress-and-plateaus.md) covers
the causes and the ways past one.

## More hours is more progress

**The claim.** Improvement is volume. Whoever puts in the most hours improves the most, so the way
to get better faster is to train longer.

**What sources say.** General motor-learning research finds shorter, more frequent sessions with
real rest between them tend to beat one long session, both for retaining a skill and for how
fatigue affects performance while training.[^hk-distribution] Past a point, more stops helping at
all: sustained training without enough recovery can tip into overreaching and then into
overtraining syndrome, where performance actually declines.[^overtraining] Ericsson's original
definition of deliberate practice is also narrower than time spent, requiring a specific
performance goal, immediate feedback on each attempt, and tasks that get harder as you
improve.[^ericsson]

**What to do instead.** Spend the time on your current weakness in sessions short enough to stay
sharp, with rest between them. [Practice Principles](fundamentals/practice-principles.md) covers
the five habits that decide what an hour is worth.

## A pro's settings are the correct settings

**The claim.** Copy the sensitivity, DPI and crosshair of a player at the top and you remove a
variable, because those settings are the ones that win.

**What sources say.** Aimlabs publishes the cm/360 ranges players use per game and says in the
same article that the right number depends on your own equipment, desk space, posture and
comfort.[^cm360] A copied number also does not always mean what it appears to: eDPI is comparable
only within one game, because games scale the sensitivity multiplier differently, so the same eDPI
in another title is a different setting.[^edpi]

**What to do instead.** Treat someone else's number as a starting point to adjust from, and
compare across games in cm/360 rather than raw sensitivity or eDPI.
[Sensitivity](getting-started/sensitivity.md) covers both measures and the converters that move a
setting between titles.

[^muscle]: Voltaic, [Muscle memory](https://blog.voltaic.gg/muscle-memory/)
[^cm360]: Aimlabs, [A quick explainer on cm/360 and the common cm/360 by game](https://aimlabs.com/articles/aimlabs/a-quick-explainer-on-cm-360-and-the-common-cm-360-by-game/)
[^edpi]: ProSettings.net, [What is DPI and eDPI?](https://prosettings.net/blog/what-is-dpi-edpi/)
[^wrist-vs-arm]: Aimlabs, [Wrist aiming vs arm aiming: why not both?](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/)
[^reactive]: Aimlabs, [Stop predicting and start reacting: get better at reactive tracking](https://aimlabs.com/articles/aimlabs/stop-predicting-and-start-reacting-get-better-at-reactive-tracking/)
[^plateau-study]: Journal of Neuroscience via PMC, [a study on plateaued motor skill](https://pmc.ncbi.nlm.nih.gov/articles/PMC3186792/)
[^hk-stages]: Human Kinetics, [Understanding motor learning stages improves skill instruction](https://us.humankinetics.com/blogs/excerpt/understanding-motor-learning-stages-improves-skill-instruction)
[^overtraining]: Sports Health via PMC, [a clinical review of overtraining syndrome](https://pmc.ncbi.nlm.nih.gov/articles/PMC3435910/)
[^hk-distribution]: Human Kinetics, [Distribution of practice in motor learning and development](https://us.humankinetics.com/blogs/excerpt/distribution-of-practice-in-motor-learning-and-development)
[^ericsson]: Macnamara & Hambrick, [a 2019 review examining Ericsson's original definition of deliberate practice](https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.02396/full)
````

Note the link depths: `myths.md` sits directly in `docs/wiki/`, so its internal links have no
`../` prefix — `getting-started/sensitivity.md`, not `../getting-started/sensitivity.md`. Getting
this wrong is the most likely warning in Step 6.

- [ ] **Step 4: Run the checker and confirm the page passes**

Run: `python scripts/check_pages.py`

Expected: PASS. `wiki/myths.md` is outside `CONCEPT_DIRS`, so no `## Further resources` section is
required of it, and the `myth` tag is now allowed.

If it fails with `unknown tag 'myth'`, Step 1 was not applied. If it fails with
`missing '## Further resources' section`, the page was created somewhere under a concept directory
such as `docs/wiki/fundamentals/` instead of `docs/wiki/`.

- [ ] **Step 5: Add the nav entry**

In `zensical.toml`, inside the `Wiki` list, immediately after the `Resources` entry's closing
`] },` and before the `Glossary` line:

```toml
    { "Myths" = "wiki/myths.md" },
```

The surrounding lines should then read:

```toml
    { "Glossary" = "wiki/glossary.md" },
```

is preceded by the new `Myths` line, which is preceded by the end of the `Resources` block.

- [ ] **Step 6: Build and read the output for link warnings**

Run: `zensical build --clean`

Expected: finishes without errors, and the output contains no warning naming `myths.md`. A warning
such as an unrecognised relative link means a link in Step 3 has the wrong depth. Fix and rebuild.
Do not treat a zero exit code as proof on its own — the build is not `--strict`.

- [ ] **Step 7: Commit**

```bash
git add docs/wiki/myths.md scripts/check_pages.py zensical.toml
git commit -m "docs: add a Myths page answering eight repeated claims

Each entry states the myth the way a player would say it, then answers it
from a source the site already cites. Myths are claims stated as fact,
which is what separates them from the behaviours the Common mistakes
sections cover.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: The `.aim-myth` component, proven on the sensitivity page

**Files:**
- Modify: `docs/assets/stylesheets/aim.css` (header comment component list, and a new component
  block in the page components section)
- Modify: `docs/wiki/getting-started/sensitivity.md` (the "When to change sensitivity, and when
  not to" section)

**Interfaces:**
- Consumes: the anchor `#changing-your-sensitivity-will-ruin-your-aim` produced by Task 1.
- Produces: the `myth` admonition type, written `!!! myth "<the claim>"`, usable on any wiki page.

- [ ] **Step 1: Add the component to the stylesheet's header list**

The file opens with a comment ending in a list of the components it defines. That sentence
currently reads:

```
 * page components. Each component is documented above its rules with the Markdown that produces
 * it: .aim-hero, .aim-cards, .aim-steps, .aim-category, .aim-table-stack.
```

Change the list to end with the new component:

```
 * page components. Each component is documented above its rules with the Markdown that produces
 * it: .aim-hero, .aim-cards, .aim-steps, .aim-category, .aim-table-stack, .aim-myth.
```

- [ ] **Step 2: Add the component's rules**

Append to the page components section, at the end of the file. The comment is part of the
deliverable: the two usage rules have to be readable where the component is defined, because
that is where `AGENTS.md` sends a reader before using one.

```css
/* .aim-myth is an admonition type, not a class you write. It marks a claim that is repeated as
 * fact and is wrong, on the page whose subject it gets wrong, and sends the reader to the full
 * answer on wiki/myths.md.
 *
 *   !!! myth "Changing your sensitivity will ruin your aim"
 *       A change costs short-term readjustment, not a lasting setback.
 *       See [Myths](../myths.md#changing-your-sensitivity-will-ruin-your-aim).
 *
 * Two rules. The title is the myth stated as the claim, word for word as its heading on the hub
 * page, because that heading is the anchor. The body is at most two sentences plus the hub link,
 * and carries no footnote: the citation lives on the hub, so a myth is only ever sourced in one
 * place and cannot go stale in two.
 *
 * The bar and transparent title come from the admonition rules in the chrome section above; these
 * rules only set the colour and the icon. They come later in the file, so they win the tie on
 * specificity against that section's [class] selectors. */
:root {
  /* A crossed-out claim: a ring with a slash through it. */
  --md-admonition-icon--myth: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="black" d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20m0 2c1.85 0 3.55.63 4.9 1.69L5.69 16.9A7.9 7.9 0 0 1 4 12a8 8 0 0 1 8-8m0 16a7.9 7.9 0 0 1-4.9-1.69L18.31 7.1A7.9 7.9 0 0 1 20 12a8 8 0 0 1-8 8"/></svg>');
}

.md-typeset .admonition.myth,
.md-typeset details.myth {
  border-color: var(--aim-accent);
}

.md-typeset .myth > .admonition-title::before,
.md-typeset .myth > summary::before {
  background-color: var(--aim-accent);
  -webkit-mask-image: var(--md-admonition-icon--myth);
  mask-image: var(--md-admonition-icon--myth);
}
```

`--aim-accent` is already redefined for the slate scheme, so the block takes the right accent in
both themes with no second rule.

- [ ] **Step 3: Convert the sensitivity passage**

In `docs/wiki/getting-started/sensitivity.md`, the section `## When to change sensitivity, and when
not to` currently opens:

```markdown
A common fear is that changing sensitivity will permanently damage your aim. Voltaic's own
breakdown of "muscle memory" in aiming pushes back on this directly: changing your sensitivity
costs you some short-term readjustment rather than any lasting setback, and it points to community
members who swap settings often, some even rolling a new sensitivity at random, with no long-run
drop in their aim.[^muscle]
```

Replace those five lines with the block, keeping the rest of the section, which begins "Switching
sensitivity on purpose is also one way people try to break a plateau", exactly as it is:

```markdown
!!! myth "Changing your sensitivity will ruin your aim"
    A change costs some short-term readjustment rather than any lasting setback.
    See [Myths](../myths.md#changing-your-sensitivity-will-ruin-your-aim).
```

The `[^muscle]` footnote definition stays at the bottom of the page: the sentences that follow the
block still cite it. Confirm this before committing with:

```bash
grep -c '\[\^muscle\]' docs/wiki/getting-started/sensitivity.md
```

Expected: `3` or more — the remaining in-text references plus the definition. If it returns `1`,
only the definition is left and it must be deleted too.

- [ ] **Step 4: Run the checker**

Run: `python scripts/check_pages.py`

Expected: PASS. `sensitivity.md` keeps its `## Further resources` section, which is what the
checker requires of a page in `getting-started`.

- [ ] **Step 5: Build, and confirm the anchor resolves**

Run: `zensical build --clean`

Expected: no warning naming `sensitivity.md` or `myths.md`. The build checks the link, not the
fragment, so verify the anchor by hand — the slug must match the heading Task 1 wrote:

```bash
grep -n "^## Changing your sensitivity will ruin your aim$" docs/wiki/myths.md
```

Expected: one match. A heading that differs by even a comma produces a link that builds cleanly and
lands at the top of the page instead of the entry.

- [ ] **Step 6: Look at the rendered block**

Run: `zensical serve`

Open <http://localhost:8000/aim/wiki/getting-started/sensitivity/> and confirm the block shows the
accent left bar, the uppercase display-font title, and the slashed-ring icon, then switch the
theme toggle and confirm it still reads in the other scheme. Click the link and confirm it lands on
the matching entry rather than the top of the Myths page.

- [ ] **Step 7: Commit**

```bash
git add docs/assets/stylesheets/aim.css docs/wiki/getting-started/sensitivity.md
git commit -m "docs: add the .aim-myth block and use it on sensitivity

The block states a claim on the page whose subject it gets wrong and links
the full answer on the Myths page. It carries no citation: the hub holds
the source, so a myth cannot go stale in two places. The sensitivity page
already answered this claim in prose, so it is the first real use.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: The two card entries

**Files:**
- Modify: `docs/index.md` (the `## Where to start` grid)
- Modify: `docs/wiki/index.md` (the `## Sections` grid)

**Interfaces:**
- Consumes: `docs/wiki/myths.md` from Task 1.
- Produces: nothing later tasks depend on.

- [ ] **Step 1: Add the landing page card**

In `docs/index.md`, inside the `.aim-cards` div, after the `Topics` item and before the closing
`</div>`:

```markdown
- **[Myths](wiki/myths.md)**: the claims players repeat as fact, answered from the same sources
  the rest of the wiki cites.
```

It goes last because it corrects the other cards rather than sequencing before them. One link in
the item, as the title, per the `.aim-cards` constraint.

- [ ] **Step 2: Add the wiki index card**

In `docs/wiki/index.md`, inside the `.aim-cards` div, between the `Resources` item and the
`Glossary` item, matching nav order:

```markdown
- **[Myths](myths.md)**: the claims about aim training that get repeated as fact, and what the
  sources actually say.
```

- [ ] **Step 3: Run the checker**

Run: `python scripts/check_pages.py`

Expected: PASS. Neither file's front matter or required sections changed.

- [ ] **Step 4: Build and read the output**

Run: `zensical build --clean`

Expected: no warning naming `index.md` or `myths.md`. The two cards use different link depths —
`wiki/myths.md` from the landing page, `myths.md` from the wiki index — and a warning here means
one of them is wrong.

- [ ] **Step 5: Confirm both grids still render as cards**

Run: `zensical serve`

Open <http://localhost:8000/aim/> and <http://localhost:8000/aim/wiki/> and confirm the new item
renders as a card in the grid rather than as a plain list item, and that clicking anywhere on the
card opens the Myths page.

- [ ] **Step 6: Commit**

```bash
git add docs/index.md docs/wiki/index.md
git commit -m "docs: link Myths from the landing page and the wiki index

The landing grid is curated, and a reader who arrives believing one of the
claims is better served by having it answered than by being sent to gear
first. The wiki index grid lists every sibling in the nav, so an omission
there would read as an oversight.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.** Hub page, Task 1. Belief-versus-behaviour opener, Task 1 Step 3. Eight entries,
Task 1 Step 3, with the one substitution recorded above. `h2` states the claim, Task 1 Step 3 and
enforced by the stylesheet comment in Task 2 Step 2. `.aim-myth` as a Material custom admonition,
Task 2 Step 2. Two-sentence cap and no citation inline, Task 2 Steps 2 and 3. Stylesheet header
list, Task 2 Step 1. Version 1 inline conversion, Task 2 Step 3, target corrected. Nav entry,
Task 1 Step 5. Landing card, Task 3 Step 1. Wiki index card, Task 3 Step 2. `myth` in
`ALLOWED_TAGS`, Task 1 Step 1. Draft banner, Task 1 Step 3. No new outbound source: every footnote
in Task 1 Step 3 already appears on `sensitivity.md`, `how-aim-works.md`,
`practice-principles.md`, or `progress-and-plateaus.md`. Verification commands, every task's last
steps.

No spec requirement is left without a task.

**Placeholders.** None. Every content step carries the exact text or code to write, and every run
step carries the command and the expected result.

**Name consistency.** The anchor `#changing-your-sensitivity-will-ruin-your-aim` in Task 2 Steps 2,
3 and 5 matches the Task 1 heading "Changing your sensitivity will ruin your aim" character for
character. `--md-admonition-icon--myth` is defined and consumed in the same block. `.aim-myth` is
the name in the header list, the comment, and the spec, while the admonition type written in
Markdown is `myth` — the distinction is stated in Task 2 Step 2's comment so it does not read as a
mismatch. `ALLOWED_TAGS` and `CONCEPT_DIRS` match the identifiers in `scripts/check_pages.py`.
