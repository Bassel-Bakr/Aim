# Aim Wiki — Design

Date: 2026-09-11
Status: Approved in brainstorming, pending spec review
Maintenance: kept in step with the repository. Changes made after approval are marked inline with
the date they landed, rather than rewritten silently.

## Goal

A public aim training wiki. Concept pages are written for the wiki, and each one points readers to
existing work (Voltaic, Jade Palace, Revosect, and aim trainers) through dedicated resource pages.
Content is Markdown maintained by the owner, with the repository set up so outside contributors can
send pull requests later.

## Non-goals (version 1)

- Per-game sections (Valorant, CS2, Apex, and so on).
- Blog, comments, accounts, or any server-side feature.
- Branch protection, review rules, and issue templates. Add these when collaborators join.
- Copying or mirroring content from other sites.
- Pages about individual content creators (YouTube channels and similar). The owner dropped this
  section on 2026-09-11.

## Stack

- **Zensical 0.0.60**, pinned in `requirements.txt`. Zensical is the successor to Material for MkDocs
  (maintenance mode since November 2025, end of life on November 5, 2026). MkDocs 1.x core has not
  been maintained since August 2024.
- **Configuration in `zensical.toml`** (2026-09-12: was `mkdocs.yml`). The original reason for the
  MkDocs format was keeping `mkdocs build` with Material available as a fallback, but Material
  reaches end of life on 2026-11-05, so the fallback expires before it is likely to be needed.
  Both formats parse to the same configuration in Zensical, and the two were diffed to confirm the
  migration changed nothing.
- Features used: light/dark palette toggle, built-in search, `tags` plugin, admonitions, content tabs,
  glossary abbreviations shown as tooltips, "edit this page" action.
- 2026-09-12: a theme layer was added — `extra_css` pointing at `docs/assets/stylesheets/aim.css`,
  a crosshair favicon, and `theme.icon.logo`. The stylesheet holds the site's colour and type
  layer plus the page components Markdown opts into, each documented above its own rules.
- Hosting: GitHub Pages, deployed by GitHub Actions.

## Repository layout

```
Aim/
  zensical.toml
  requirements.txt
  README.md
  CONTRIBUTING.md
  LICENSE                 # CC BY-SA 4.0
  specs/                  # design documents, not published
  templates/              # page templates, not published
    concept.md
    resource.md
    topic.md              # 2026-09-12
  scripts/                # tag/section checker, not published
    check_pages.py
  includes/               # abbreviation snippets, injected into built pages
    abbreviations.md
  docs/                   # published content
    index.md              # landing page, served at /
    assets/               # 2026-09-12: favicon and stylesheets/aim.css
    topics/               # 2026-09-12: signed pages, served at /topics/
    wiki/                 # the wiki itself, served at /wiki/
      index.md
      getting-started/
      fundamentals/
      skills/
      techniques/         # 2026-09-12
      training/
      resources/
      glossary.md
      tags.md
  .github/workflows/
    deploy.yml
    check.yml
```

## Content structure

Navigation follows a learner journey. 26 wiki pages under `docs/wiki/`, plus a landing page at `docs/index.md` (2026-09-12: the wiki moved to the `/wiki/` subpath; page paths below are relative to `docs/wiki/`, and the wiki has since grown to 31 pages).

- **Home** — `index.md`: what the wiki is, how to use it, "start here" links.
- **Getting Started** — `getting-started/`
  - `index.md`: roadmap for new aimers
  - `sensitivity.md`: cm/360, eDPI, choosing a sensitivity, converting between games
  - `setup.md`: mouse, mousepad, grip, posture, monitor refresh rate and FPS
  - `aim-trainers.md`: what an aim trainer is, why isolating a skill is worth doing, and how that
    trades against in-game practice (2026-09-12: this page no longer compares named trainers. What
    each one costs and ships with changes on its developer's schedule, so it lives on that
    trainer's resource page only, and the page hands the reader the questions to decide on
    instead)
- **Fundamentals** — `fundamentals/`
  - `index.md`
  - `how-aim-works.md`: arm, wrist, and finger aim; micro and macro corrections; speed versus
    accuracy; smoothness
  - `practice-principles.md`: deliberate practice, focus, variety, rest
  - `transfer-to-games.md`: what trainers cover and what they miss (crosshair placement, movement,
    game sense)
- **Skills** — `skills/`
  - `index.md`: taxonomy overview
  - `clicking.md`: sections for dynamic, static, and linear clicking
  - `tracking.md`: sections for precise, reactive, and control tracking
  - `switching.md`: sections for speed, evasive, and stability switching
  - Subcategory names follow the Voltaic Season 5 benchmarks.
- **Techniques** — `techniques/` (2026-09-12). Concept pages for named techniques that belong to no
  one person, such as underaiming. They are wiki pages under the normal sourcing rules, and they
  take the topic tags of the skills they apply to rather than a tag of their own.
- **Training** — `training/`
  - `index.md`
  - `routines.md`: building a routine, warm-ups, playlists
  - `benchmarks.md`: what benchmarks are, how to use Voltaic ranks
  - `progress-and-plateaus.md`
  - `health.md`: breaks, strain, warm-ups. General information only, with a clear
    "not medical advice" note.
- **Resources** — `resources/`
  - `index.md`: overview of all resources, grouped by type, with links to tag listings
  - `communities/`: `voltaic.md`, `jade-palace.md`, `revosect.md`
  - `trainers/`: `kovaaks.md`, `aimlabs.md`, `aimbeast.md` (2026-09-12)
  - `tools/` (2026-09-12): `evxl.md`, `kova.md`, `kovobs.md`
- **Glossary** — `glossary.md`, with terms also defined as abbreviations so they show as tooltips.
- **Tags** — `tags.md`, the tag index generated by the `tags` plugin.

Every concept page ends with a "Further resources" section that links to resource pages.

## Topics (2026-09-12)

`docs/topics/`, served at `/topics/`, sits outside the wiki and outside these rules. A wiki page
earns trust by citing a public source for each claim and is open to correction by anyone; a topic
page earns trust by carrying its author's name and is not open to contributions. Topic pages use
`templates/topic.md`, carry a byline instead of the draft banner, take no tags, and require no
footnotes. Keeping the two in separate trees means neither set of rules needs an exception clause
for the other, and `scripts/check_pages.py` enforces each set against its own tree.

The section was introduced as Guides and renamed to Topics on 2026-09-12, when the remit widened
from walkthroughs of a specific problem to anything worth a signed opinion. The trust model did not
change with the name.

## Templates

`templates/` sits outside `docs/`, so templates are never published.

**`templates/resource.md`**

- Front matter: `title`, `tags`.
- Sections: What it is / Who it suits / What it covers / Key content (links to specific guides or
  videos) / Our take / Related wiki pages.
- External links (site, Discord, YouTube, and so on) go in a "Links" list at the top of the page body.

**`templates/concept.md`**

- Front matter: `title`, `tags`.
- Sections: Summary (two or three lines) / Explanation / Common mistakes / How to train it /
  Further resources.

**`templates/topic.md`** (2026-09-12)

- Front matter: `title` only. Topic pages take no tags.
- A `!!! info "Written by <name>"` byline in place of the draft banner, then headings of the
  author's choosing, then Further resources. Shape is deliberately not fixed: a topic page is
  signed, so how it argues is the author's call.

## Tags

Only these tags are allowed. `CONTRIBUTING.md` lists them.

- Type: `community`, `trainer`, `tool` (2026-09-12)
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`

## Sourcing rules

These rules apply to the drafted content and to future contributors.

1. Write summaries in the wiki's own words and link to the original. Do not copy guides, tables, or
   images from other sites.
2. Link facts to their source inline. For example, a benchmark rank definition links to the Voltaic
   page that defines it.
3. Every drafted page starts with this admonition, which the owner removes after fact-checking:
   `!!! warning "Draft"` — "Written from public sources, pending review."
4. A claim that cannot be verified from a public source is left out or marked with an HTML comment
   `<!-- REVIEW: ... -->` for the owner. No guessing.

## Initial content

Version 1 ships drafted text for every page above, researched from public sources and following the
sourcing rules, plus both templates.

## CI

- **`deploy.yml`**: on push to `main`, install `requirements.txt`, run `zensical build --clean`,
  upload `site/`, and deploy to GitHub Pages. The repository must have Pages set to publish from
  GitHub Actions.
- **`check.yml`**:
  - On every pull request: build the site. Build errors fail the check.
  - Weekly schedule and manual dispatch: check external links in `docs/` with lychee. A failed run
    triggers the standard GitHub failure email to the owner.

## Collaboration

- `repo_url` and `edit_uri` are set in `zensical.toml`, so each page shows an edit button that opens the
  file on GitHub.
- `CONTRIBUTING.md` covers: running the site locally, using the templates, the sourcing rules, the
  allowed tags, and the pull request flow.
- Content license: CC BY-SA 4.0, stated in `LICENSE`, `README.md`, and the site footer.

## Acceptance

- `zensical build --clean` succeeds locally with no errors, and the local preview renders every page
  in the navigation.
- Tags page lists pages under each tag.
- Every page in `docs/` except `tags.md` has the draft banner (2026-09-12: index pages are exempt
  too, and pages under `docs/topics/` carry a byline instead, which `scripts/check_pages.py`
  enforces).
- Every concept page has a "Further resources" section, and every resource page has a
  "Related wiki pages" section.
- No page in `docs/` contains copied text from a source site.
- Both workflow files are valid YAML and use the published Zensical GitHub Pages workflow as a base.

## Open items for the owner

- Create the GitHub repository and set Pages to publish from GitHub Actions.
- Fact-check each drafted page and remove its draft banner.
