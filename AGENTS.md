# Agent guide

Instructions for AI coding agents working in this repository. Human contributors should read
[CONTRIBUTING.md](CONTRIBUTING.md) instead — this file points at the same rules and adds nothing
that contradicts them.

## What this repository is

A static documentation site about aim training, built with [Zensical](https://zensical.org) from
Markdown in `docs/`. Content is prose, not code. Most changes are edits to Markdown files plus a
matching `nav` entry in `mkdocs.yml`.

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
each concept page carries a `## Further resources` section, and each resource page carries a
`## Related wiki pages` section. Pass `--drafts` to also require the draft banner on every page.
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
| `docs/topics/` | Signed first-person pages. Not wiki pages, not open — see below. |
| `docs/assets/` | Favicon and `stylesheets/aim.css`, which documents each page component it defines. |
| `includes/abbreviations.md` | Abbreviation definitions shown as tooltips site-wide. |
| `templates/` | Page templates. Not published. |
| `specs/` | Design documents. Not published. |
| `scripts/` | Repository checks. |
| `mkdocs.yml` | Site config and the `nav` tree. |

## Page components

`docs/assets/stylesheets/aim.css` defines a handful of classes that Markdown pages opt into. Each
one is documented above its own rules in the stylesheet, with the Markdown that produces it. Read
that before using one, and add a new component only when a page actually needs it.

| Class | What it does |
| --- | --- |
| `.aim-hero` | Landing-page opener. A page with a hero has the theme's generated title hidden, so the hero has to carry the title itself. |
| `.aim-cards` | Turns a list of links into a card grid. The whole card is the link, so each item needs exactly one link, written as its title. A second link in the same item ends up under the stretched hit area and cannot be clicked. |
| `.aim-steps` | Turns an ordered list into a numbered route. |
| `.aim-skill` | Inline badge on a link naming a skill, with `.aim-skill--clicking`, `--tracking` or `--switching` alongside it. |
| `.aim-table-stack` | Wraps a table whose last column should drop onto its own line below 38em instead of squeezing. |

All of these except `.aim-skill` are wrappers:

```markdown
<div class="aim-cards" markdown>

- **[Skills](wiki/skills/index.md)**: what the section covers.

</div>
```

The `markdown` attribute and the blank lines around the content are both required, or the Markdown
inside the wrapper is passed through as literal text. `.aim-skill` goes on the link itself with
`attr_list`: `[Clicking](clicking.md){ .aim-skill .aim-skill--clicking }`.

## Rules that are easy to get wrong

Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before adding a page. These are the constraints
agents most often miss:

1. Start from a template in `templates/` — `concept.md` for explanations, `resource.md` for
   communities, trainers and tools.
2. Page titles come from the `title:` field in front matter. Do not add an `#` heading in the body.
3. Every new page needs a `nav` entry in `mkdocs.yml` and at least one inbound link from a related
   page.
4. Use only the tags listed in [CONTRIBUTING.md](CONTRIBUTING.md#tags). Do not invent new ones.
5. Write in your own words, and note that reusing a source's sentence with a few words changed is
   still copying — restate the claim from scratch, or quote and attribute it. Cite each fact with a
   footnote — a `[^label]` marker at the end of
   the sentence, defined at the bottom of the file. Reuse one label for repeat citations of the
   same source, keep the definition list in order of first use, and use descriptive labels rather
   than numbers. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full rule and its two exceptions.
   Never copy guides, tables, or images from other sites — content here is CC BY-SA 4.0 and the
   sources are not.
6. Do not assert a claim you cannot verify from a public source. Leave it out, or mark it with
   `<!-- REVIEW: what needs checking -->`.
7. A page written from research but not yet fact-checked keeps the draft banner at the top, exactly
   as shown in [CONTRIBUTING.md](CONTRIBUTING.md).
8. New abbreviations go in both `docs/wiki/glossary.md` and `includes/abbreviations.md`.

## Topics are not wiki pages

`docs/topics/` is a separate part of the site at `/topics`, and none of the rules above apply to
it. Topic pages are signed opinion written from the maintainer's own experience: they use
`templates/topic.md`, carry a `!!! info "Written by <name>"` byline instead of the draft banner,
take no tags, and do not require footnotes. `scripts/check_pages.py` enforces that.

Never write or edit a topic page on your own initiative. A byline names a real person as
accountable for every claim on the page, so its content is theirs to decide. Fix a typo or a dead
link if asked; send anything touching the argument itself back to the author.

## Deployment

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main`. Do not
commit the `site/` directory; it is generated and ignored.
