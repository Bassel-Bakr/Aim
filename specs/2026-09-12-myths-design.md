# Myths — Design

Date: 2026-09-12
Status: Approved in brainstorming, pending spec review
Maintenance: kept in step with the repository. Changes made after approval are marked inline with
the date they landed, rather than rewritten silently.

## Goal

A Myths page that answers the false claims aim training players repeat as fact, each one corrected
from a source already cited on this site, plus a reusable block that places a short version of a
correction on the page whose subject it belongs to.

## Why a new section rather than more Common mistakes

Seven wiki pages already carry a `## Common mistakes` section, and those sections describe
behaviour: practising the scenario you are already good at, stacking long sessions without rest.
A myth is different in kind. It is a claim a reader states as true, and it needs the claim quoted
before it can be answered. Mixing the two blurs both, so the split is drawn on belief versus
behaviour:

- A myth is a false claim someone would say out loud as fact. "Lower sens means better aim."
- A common mistake is a behaviour. "Only running scenarios you already score well in."

Existing `## Common mistakes` sections keep their content. Nothing moves out of them except the
muscle memory passage named below, which is a claim rather than a behaviour.

## Non-goals (version 1)

- Myth entries for claims with no source already cited on the site. New outbound sources are a
  later change, so the weekly lychee run gains nothing new to break in this one.
- A myth block on every page it could apply to. Version 1 converts one existing passage, which is
  enough to prove the component against real content.
- Per-game myths (Valorant sens conversion folklore, and so on).
- A page per myth. Most entries run a few hundred words and would read as stubs on their own.

## Shape

Two surfaces, one source of truth.

**The hub**, `docs/wiki/myths.md`, is canonical. It carries the full treatment of every myth: the
claim, what sources say, what to do instead, and the citation.

**The inline block**, `.aim-myth`, carries a two sentence correction and a link to the hub entry.
It never carries a citation, because the citation belongs to the hub entry it links to. This is
what keeps the two surfaces from drifting: the short form states the correction, the long form
proves it, and only one of them can go stale.

## Hub page anatomy

Front matter carries `tags: [myth]`, the draft banner follows, then a short opener explaining the
belief-versus-behaviour line and pointing at the `## Common mistakes` sections for the other half.

Each myth is an `h2`, which `toc.permalink` turns into an anchor for the inline blocks to target.
The heading states the myth as the false claim, not as the correction: a reader scanning the page
is looking for the sentence they currently believe, and will not recognise their own belief in a
heading that already answers it.

The body is three bolded leads in the same order every time:

```markdown
## Reps burn a motion into muscle memory

**The claim.** Enough repetitions of a flick store the motion, and it replays on demand
afterwards.

**What sources say.** ... [^muscle]

**What to do instead.** ... [^muscle]
```

Footnotes collect at the bottom of the page, matching every other wiki page.

## Version 1 entries

Eight, each answerable from a footnote already present on the site.

| Myth stated as the claim | Source |
| --- | --- |
| Reps burn a motion into muscle memory | Voltaic, `blog.voltaic.gg/muscle-memory` |
| Arm aiming is strictly better than wrist aiming | Aimlabs, wrist aiming vs arm aiming |
| Lower sensitivity means better aim | Aimlabs cm/360, ProSettings eDPI |
| Accuracy comes first, so train slow | Aimlabs, speed-accuracy tradeoff |
| Good tracking means predicting where the target will go | Aimlabs, reactive tracking |
| A plateau means you have hit your ceiling | plateau study, `PMC3186792` |
| More hours is more progress | overtraining review, `PMC3435910` |
| A pro's settings are the correct settings | ProSettings eDPI, Aimlabs cm/360 |

## The `.aim-myth` component

Implemented as a Material custom admonition, so the `admonition` extension already enabled in
`zensical.toml` produces it and the block inherits the theme's admonition layout in both colour
schemes. It needs a colour, an icon custom property, and the two selectors Material's custom
admonitions require.

```markdown
!!! myth "Reps burn a motion into muscle memory"
    Repetition builds the read and the correction, not a stored motion.
    See [Myths](../myths.md#reps-burn-a-motion-into-muscle-memory).
```

Two rules constrain use, and both go in the stylesheet's comment above the component so they are
read before it is used: the title is the myth stated as the claim, matching its hub heading, and
the body is at most two sentences plus the hub link, with no citation.

`docs/assets/stylesheets/aim.css` opens with a comment listing the components it defines. Adding
`.aim-myth` means adding it to that list as well as documenting it above its own rules.

## Version 1 inline conversion

`docs/wiki/training/progress-and-plateaus.md` already answers the muscle memory claim in prose,
citing `[^muscle]`. That passage becomes an `!!! myth` block linking the hub entry, and the
`[^muscle]` footnote leaves the page if no other reference to it remains. This is the only page
whose prose changes.

## Entry points

The page is reachable from three places, because the site has three lists a wiki page belongs to.

**Nav**, inside the `Wiki` list, between `Resources` and `Glossary`.

**The landing page**, `docs/index.md`, gets a card in the `## Where to start` grid. That grid is
curated rather than exhaustive, so the card has to earn its place: it does, because a reader who
arrives believing one of the eight claims is better served by having it answered than by being
sent to gear and sensitivity first. It goes last, after `Topics`, since it corrects the other
cards rather than sequencing before them.

**The wiki index**, `docs/wiki/index.md`, gets a card in the `## Sections` grid. Unlike the
landing page's grid, this one lists every sibling the nav holds, down to `Glossary` and `Tags`, so
a missing entry reads as an oversight rather than a choice. It goes between `Resources` and
`Glossary`, matching nav order.

Both grids use `.aim-cards`, where the whole card is the link, so each item carries exactly one
link written as its title. A second link in the same item lands under the stretched hit area and
cannot be clicked.

## Files

```
docs/wiki/myths.md                           new   hub page, eight entries
docs/assets/stylesheets/aim.css              edit  .aim-myth component, and the header list
docs/wiki/training/progress-and-plateaus.md  edit  muscle memory passage becomes a myth block
docs/index.md                                edit  card in the Where to start grid
docs/wiki/index.md                           edit  card in the Sections grid
zensical.toml                                edit  nav entry
scripts/check_pages.py                       edit  "myth" added to ALLOWED_TAGS
```

The nav entry is a page rather than a section:

```toml
{ "Myths" = "wiki/myths.md" },
```

## Interaction with the existing checks

`scripts/check_pages.py` derives a wiki page's section from the first path segment below
`docs/wiki/`. For `wiki/myths.md` that segment is `myths.md`, which is not in `CONCEPT_DIRS`, so
the `## Further resources` requirement does not apply — the same position `wiki/glossary.md`
holds. The page is not in `EXEMPT_FROM_BANNER`, so it carries the draft banner. `myth` is added to
`ALLOWED_TAGS`, which the checker validates every `tags:` value against.

## Verification

```bash
python scripts/check_pages.py
```

```bash
zensical build --clean
```

Both must finish without errors. The build is not run with `--strict`, so link problems surface as
warnings rather than a non-zero exit: read the output rather than trusting the exit code, and
confirm specifically that the inline block's anchor into `myths.md` resolves.

## Later changes

- Myth blocks on `sensitivity.md`, `transfer-to-games.md`, `how-aim-works.md`, and `routines.md`,
  one per myth that page's subject covers.
- Entries for claims that need a source this site does not yet cite.
