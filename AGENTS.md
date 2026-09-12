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
| `docs/wiki/` | All wiki pages, grouped by section. |
| `docs/wiki/guides/` | Signed first-person guides. Different rules — see below. |
| `includes/abbreviations.md` | Abbreviation definitions shown as tooltips site-wide. |
| `templates/` | Page templates. Not published. |
| `specs/` | Design documents. Not published. |
| `scripts/` | Repository checks. |
| `mkdocs.yml` | Site config and the `nav` tree. |

## Rules that are easy to get wrong

Read [CONTRIBUTING.md](CONTRIBUTING.md) in full before adding a page. These are the constraints
agents most often miss:

1. Start from a template in `templates/` — `concept.md` for explanations, `resource.md` for
   communities, trainers and tools, `guide.md` for signed first-person guides.
2. Page titles come from the `title:` field in front matter. Do not add an `#` heading in the body.
3. Every new page needs a `nav` entry in `mkdocs.yml` and at least one inbound link from a related
   page.
4. Use only the tags listed in [CONTRIBUTING.md](CONTRIBUTING.md#tags). Do not invent new ones.
5. Write in your own words and cite each fact with a footnote — a `[^label]` marker at the end of
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
9. Pages under `docs/wiki/guides/` are the exception to rules 5 and 7. They are signed opinion
   written from the author's experience, so they carry a `!!! info "Written by <name>"` byline
   instead of the draft banner, footnotes are optional rather than required, and first person is
   expected. Do not write one on your own initiative: authorship is not open, and a byline names a
   real person as accountable for the claims. The own-words rule still applies in full.

## Deployment

`.github/workflows/deploy.yml` builds and publishes to GitHub Pages on every push to `main`. Do not
commit the `site/` directory; it is generated and ignored.
