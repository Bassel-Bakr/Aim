# Owner fact-check list

Every page in `docs/` carries this banner until you check it:

```markdown
!!! warning "Draft"
    Written from public sources, pending review.
```

Remove the banner from a page once you have read it and agree with it. The page checker only warns
about missing banners when you run it with `--drafts`, so removing them does not break anything:

```bash
.venv/Scripts/python scripts/check_pages.py
.venv/Scripts/zensical build --clean --strict
```

## Check these first (highest risk of being wrong)

These are claims where the source was hard to verify, or where reviewers disagreed with the wording.

1. **Voltaic rank mechanics** — `docs/training/benchmarks.md`, `docs/resources/communities/voltaic.md`.
   Both pages now say the overall Energy score is a harmonic mean of your subcategory scores. Confirm
   against <https://app.voltaic.gg/leaderboards/about>, and confirm the current seasons (the pages say
   KovaaK's Season 5 and Aimlabs Season 3).
2. **Revosect details** — `docs/resources/communities/revosect.md`, `docs/training/benchmarks.md`.
   revosect.com blocks automated fetching, so these facts came from a browser session. Check the tier
   names, the season, and the VOD requirement. Both pages say a VOD is required "at the top Advanced
   tier"; one reviewer read the site as requiring it for the whole Immortal+ range. Fix both pages
   together.
3. **Season 5 scenario descriptions** — `docs/skills/clicking.md`, `tracking.md`, `switching.md`.
   Nine scenarios are named (Pasu, 1wxts, Frogtagon, PGT, Aether, Raw Control, DotTS, DriftTS,
   ControlTS). Names and categories were verified, but two descriptions are more specific than the
   announcement:
   - `tracking.md`: PGT is called "a small, curved target"; the source describes targets that move
     along an arcing path on a slanted floor.
   - `switching.md`: DotTS is said to spread dots wide "specifically to force" fast transitions, which
     asserts design intent the source does not state.
4. **Jade Palace** — `docs/resources/communities/jade-palace.md`. Public information is thin, and the
   page still holds the one open `<!-- REVIEW: ... -->` marker in the wiki (about who runs the server
   day to day and whether a public application link exists). You likely know this better than any
   public source does.

## Smaller things reviewers flagged and left to you

- `docs/getting-started/setup.md` — the Windows 10 route to "Enhance pointer precision" is written as
  Control Panel; Microsoft's page documents Settings › Devices › Mouse › Additional mouse options.
- `docs/fundamentals/practice-principles.md` — the Revosect variety advice cites a Google Doc URL.
  A `revosect.com/resources` link would be more stable.
- `docs/glossary.md` — the Underflick entry's wording sits close to its source's sentence. Reword it
  when you pass through.
- `docs/training/routines.md` and `docs/training/health.md` — the warm-up advice is explained twice.
  Consider keeping the full version in one page and linking to it from the other.
- **Tone drift.** The Getting Started and resource pages avoid contractions; Fundamentals, Skills, and
  Training pages use them. Pick one and normalize.
- **Secondary sources.** Most citations are primary (Steam, official blogs, OSHA, NHS, Mayo Clinic,
  AAO, peer-reviewed papers). Three lean on smaller sites: `mousedpianalyzer.com` (raw input),
  `wasdlife.com` (grip styles), and a SteelSeries product page (pad surfaces). Replace them if you
  know better sources.

## Before you push

1. Create the GitHub repository `bassel-bakr/aim-wiki`.
2. In Settings → Pages, set Source to "GitHub Actions". The deploy workflow fails without this.
3. Push `main`. The first deploy runs automatically.
4. The weekly link check runs Mondays. It accepts 403 responses because several cited sites block
   bots, so a red run means a genuinely broken link.
