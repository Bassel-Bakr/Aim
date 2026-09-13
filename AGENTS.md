# Agent guide

Instructions for AI coding agents working in this repository. Human contributors should read
[CONTRIBUTING.md](CONTRIBUTING.md) instead — this file points at the same rules and adds nothing
that contradicts them.

## What this repository is

A static documentation site about aim training, built with [Zensical](https://zensical.org) from
Markdown in `docs/`. Content is prose, not code. Most changes are edits to Markdown files plus a
matching `nav` entry in `zensical.toml`.

## Setup

Python 3.10 or later. See [README.md](README.md#run-the-site-locally) for the full walkthrough.

```bash
python -m venv .venv
```

Activate the environment (`.venv\Scripts\Activate.ps1` on Windows PowerShell, `source
.venv/bin/activate` on macOS or Linux), then:

```bash
pip install -r requirements.txt
```

## Commands

Preview the site locally with live reload on <http://localhost:8000>:

```bash
zensical serve
```

Verify a change before committing. Both commands must finish without errors, and the same checks
run on every pull request via `.github/workflows/check.yml`:

```bash
python scripts/check_pages.py
```

```bash
zensical build --clean
```

`scripts/check_pages.py` enforces three content rules: every `tags:` value is on the allowed list,
each concept page and each resource page carries a `related:` list in front matter where every
entry has a real reason, and every citation names an ID in `references.yml`. It also checks that every myth block's title matches a heading on
`docs/wiki/myths.md`, and enforces the readability rules in
[CONTRIBUTING.md](CONTRIBUTING.md#readability). Pass `--drafts` to also require the draft banner on
every page. Name pages after the flags to check only those.
`zensical build` catches broken internal links and missing nav targets. The build no longer runs
with `--strict`, so link problems appear as warnings rather than failures — read the build output,
do not rely on the exit code alone.

External links are checked separately by lychee, on a weekly schedule rather than per pull request,
so a dead outbound link will not show up in the checks you run locally.

## Layout

| Path | Contents |
| --- | --- |
| `docs/index.md` | Site landing page. Not a wiki page. |
| `docs/wiki/` | All wiki pages, grouped by section. Sourced, open to contributions. |
| `docs/articles/` | Signed first-person pages. Not wiki pages, not open — see below. |
| `docs/assets/` | Favicon, `stylesheets/aim.css`, which documents each page component it defines, and `javascripts/aim-theme.js`, the colour picker. |
| `overrides/` | Theme template overrides. `main.html` loads the colour picker script in `<head>`. |
| `includes/abbreviations.md` | Abbreviation definitions shown as tooltips site-wide. |
| `references.yml` | Every source the wiki cites, once, under a stable `REF-<number>` ID. |
| `extensions/aim_related.py` | Markdown extension that writes the Related section from a page's `related:` front matter, adding bare links back from pages of the same kind that list it. Its helpers are shared by the checker and `scripts/suggest_related.py`. |
| `extensions/aim_references.py` | Markdown extension that turns `[^REF-<number>]` citations into footnotes and builds the References page. Installed by `pyproject.toml` through `requirements.txt`. |
| `templates/` | Page templates. Not published. |
| `specs/` | Design documents. Not published. |
| `scripts/` | Repository checks. |
| `zensical.toml` | Site config and the `nav` tree. |

## Page components

`docs/assets/stylesheets/aim.css` defines a handful of classes that Markdown pages opt into. Each
one is documented above its own rules in the stylesheet, with the Markdown that produces it. Read
that before using one, and add a new component only when a page actually needs it.

| Class | What it does |
| --- | --- |
| `.aim-hero` | Landing-page opener. A page with a hero has the theme's generated title hidden, so the hero has to carry the title itself. |
| `.aim-cards` | Turns a list of links into a card grid. The whole card is the link, so each item needs exactly one link, written as its title. A second link in the same item ends up under the stretched hit area and cannot be clicked. |
| `.aim-steps` | Turns an ordered list into a numbered route. |
| `.aim-category` | Inline badge on a link naming a skill, with `.aim-category--clicking`, `--tracking` or `--switching` alongside it. |
| `.aim-table-stack` | Wraps a table whose last column should drop onto its own line below 38em instead of squeezing. |

All of these except `.aim-category` are wrappers:

```markdown
<div class="aim-cards" markdown>

- **[Categories](wiki/categories/index.md)**: what the section covers.

</div>
```

The `markdown` attribute and the blank lines around the content are both required, or the Markdown
inside the wrapper is passed through as literal text. `.aim-category` goes on the link itself with
`attr_list`: `[Clicking](clicking.md){ .aim-category .aim-category--clicking }`.

Colour tokens in `aim.css` are also written by `docs/assets/javascripts/aim-theme.js` when a reader
picks a colour. A new scheme-dependent colour token has to be added to `derive` there as well, or it
keeps its default colour under every picked colour, and no test catches that.

## Rules that are easy to get wrong

Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before adding a page. These are the constraints
agents most often miss:

1. Start from a template in `templates/` — `concept.md` for explanations, `resource.md` for
   communities, trainers and tools.
2. Page titles come from the `title:` field in front matter. Do not add an `#` heading in the body.
3. Every new page needs a `nav` entry in `zensical.toml` and at least one inbound link from a related
   page.
4. Use only the tags listed in [CONTRIBUTING.md](CONTRIBUTING.md#tags). Do not invent new ones.
5. Write in your own words, and note that reusing a source's sentence with a few words changed is
   still copying — restate the claim from scratch, or quote and attribute it. Cite each fact with its
   source's ID from `references.yml` as a footnote marker, `[^REF-15]`, and never define it on the
   page: `extensions/aim_references.py` adds the definition. Add a missing source to the registry
   with the next unused ID; never renumber one. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full
   rule and its two exceptions.
   Never copy guides, tables, or images from other sites — content here is CC BY-SA 4.0 and the
   sources are not.
6. Do not assert a claim you cannot verify from a public source. Leave it out, or mark it with
   `<!-- REVIEW: what needs checking -->`.
7. A page written from research but not yet fact-checked keeps the draft banner at the top, exactly
   as shown in [CONTRIBUTING.md](CONTRIBUTING.md).
8. New abbreviations go in both `docs/wiki/glossary.md` and `includes/abbreviations.md`.
9. Every wiki page follows the readability rules in
   [CONTRIBUTING.md](CONTRIBUTING.md#readability): 45-word paragraphs, 25-word sentences, and on
   concept pages three to five answer bullets up top and a `**Do this next.**` paragraph at the end.
   Run `python scripts/check_pages.py <page>` on any page you write or edit.
10. When restructuring an existing page, run `python scripts/check_rewrite.py <base> <page>` before
    committing, where `<base>` is the commit before you started. It must print
    `Invariants unchanged`. A rewrite that drops a link or renames a heading breaks pages that link
    to it, and the build does not always say so.
11. When you add or edit a page's `related:` list, run `python scripts/suggest_related.py <page>`.
    Draft a reason for each suggestion worth keeping from what both pages actually say, and drop the
    rest. A reason names how the other page connects to this one; do not invent a connection the
    pages do not support. Do the same for any bare link back the build shows on the other page.

## Articles are not wiki pages

`docs/articles/` is a separate part of the site at `/articles`, and none of the rules above apply to
it. Articles are signed opinion written from the maintainer's own experience: they use
`templates/article.md`, carry a `!!! info "Written by <name>"` byline instead of the draft banner,
take no tags, and do not require footnotes. `scripts/check_pages.py` enforces that.

Never write or edit an article on your own initiative. A byline names a real person as
accountable for every claim on the page, so its content is theirs to decide. Fix a typo or a dead
link if asked; send anything touching the argument itself back to the author.

## Deployment

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main`. Do not
commit the `site/` directory; it is generated and ignored.
