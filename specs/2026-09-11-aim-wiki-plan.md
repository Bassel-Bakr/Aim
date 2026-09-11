# Aim Wiki Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Zensical-powered aim training wiki with 30 Markdown pages (29 drafted, plus the generated Tags page), page templates, contributor docs, and GitHub Pages CI.

**Architecture:** Plain Markdown in `docs/`, configured by `mkdocs.yml` and built by Zensical into a static site. Page templates and design documents stay outside `docs/`, so they are never published. `scripts/check_pages.py` enforces the tag list and required sections. `zensical build --clean --strict` catches broken internal links.

**Tech Stack:** Zensical 0.0.60 (reads `mkdocs.yml`, Material theme), Python-Markdown and pymdownx extensions, PyYAML, GitHub Actions, GitHub Pages, lychee link checker.

**Spec:** `specs/2026-09-11-aim-wiki-design.md`

## Global Constraints

- Build tool: `zensical==0.0.60`, pinned in `requirements.txt`. Configuration file: `mkdocs.yml`.
- Use only features supported by both Zensical and Material for MkDocs 9.7.
- Site URL: `https://bassel-bakr.github.io/aim-wiki/`. Repository: `https://github.com/bassel-bakr/aim-wiki`. Default branch: `main`.
- Content license: CC BY-SA 4.0.
- Allowed tags, and no others: type tags `community`, `trainer`, `creator`; topic tags `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`.
- Every page in `docs/` except `tags.md` starts (after front matter) with this exact banner:

  ```markdown
  !!! warning "Draft"
      Written from public sources, pending review.
  ```

- Every concept page (any page in `getting-started/`, `fundamentals/`, `skills/`, or `training/` except `index.md`) has a `## Further resources` section.
- Every resource page (any page under `resources/` except `resources/index.md`) has a `## Related wiki pages` section.
- Page titles come from the front matter `title:` field. Do not add an `#` H1 heading in the page body, because Zensical renders `title:` as the H1.
- Sourcing rules:
  1. Write summaries in our own words and link to the original. Do not copy guides, tables, or images from other sites.
  2. Link facts to their source inline.
  3. Keep the draft banner on every drafted page.
  4. If a claim cannot be verified from a public source, leave it out or mark it `<!-- REVIEW: what needs checking -->`. Never guess names, numbers, dates, handles, or URLs.
- Git commits end with the trailer `Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>`. Repository-local git email is already set to `bassel.bakr@gmail.com`.

## File map

| Path | Responsibility |
|------|----------------|
| `.gitignore`, `.gitattributes` | Ignore build output and caches. Normalize line endings to LF. |
| `requirements.txt` | Pinned build dependencies |
| `mkdocs.yml` | Site config: theme, plugins, Markdown extensions, navigation |
| `includes/abbreviations.md` | Abbreviation tooltips, appended to every page by `pymdownx.snippets` |
| `scripts/check_pages.py` | Checks tags, required sections, and (with `--drafts`) draft banners |
| `templates/concept.md`, `templates/resource.md` | Page templates for authors |
| `README.md`, `CONTRIBUTING.md`, `LICENSE` | Project docs and license |
| `.github/workflows/deploy.yml` | Build and deploy to GitHub Pages on push to `main` |
| `.github/workflows/check.yml` | PR build check, weekly external link check |
| `docs/**` | Published pages (30 files, listed in Task 1 Step 6) |

---

### Task 1: Site scaffold, page stubs, and page checker

**Files:**
- Create: `.gitignore`, `.gitattributes`, `requirements.txt`, `mkdocs.yml`, `includes/abbreviations.md`, `scripts/check_pages.py`
- Create: 30 stub pages under `docs/` (generated in Step 6)

**Interfaces:**
- Produces: `python scripts/check_pages.py [--drafts]`. Exit code 0 when all pages pass, 1 otherwise. Prints one line per problem, in the form `<path relative to docs>: <problem>`.
- Produces: every page path listed in the Step 6 table. Later tasks replace stub bodies but keep paths, titles, and tags unless a task says otherwise.

- [ ] **Step 1: Create a virtual environment and dependency file**

Create `requirements.txt`:

```text
zensical==0.0.60
pyyaml>=6
```

Run:

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/zensical --version
```

Expected: the last command prints a version containing `0.0.60`. On macOS or Linux, use `.venv/bin/` instead of `.venv/Scripts/` in every command in this plan.

- [ ] **Step 2: Create ignore and attribute files**

`.gitignore`:

```text
.venv/
site/
.cache/
__pycache__/
```

`.gitattributes`:

```text
* text=auto eol=lf
```

- [ ] **Step 3: Write the page checker**

Create `scripts/check_pages.py`:

```python
"""Check wiki pages against the rules in CONTRIBUTING.md.

Usage:
    python scripts/check_pages.py           # tags and required sections
    python scripts/check_pages.py --drafts  # also require the draft banner
"""
import re
import sys
from pathlib import Path

import yaml

DOCS = Path(__file__).resolve().parent.parent / "docs"
ALLOWED_TAGS = {
    "community", "trainer", "creator",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
}
CONCEPT_DIRS = {"getting-started", "fundamentals", "skills", "training"}
BANNER = '!!! warning "Draft"'


def front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def check(path, drafts):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    section = rel.split("/")[0]
    is_index = path.name == "index.md"
    errors = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    if section in CONCEPT_DIRS and not is_index and "\n## Further resources" not in text:
        errors.append(f"{rel}: missing '## Further resources' section")
    if section == "resources" and not is_index and "\n## Related wiki pages" not in text:
        errors.append(f"{rel}: missing '## Related wiki pages' section")
    if drafts and rel != "tags.md" and BANNER not in text:
        errors.append(f"{rel}: missing draft banner")
    return errors


def main():
    drafts = "--drafts" in sys.argv[1:]
    errors = [error for path in sorted(DOCS.rglob("*.md")) for error in check(path, drafts)]
    for error in errors:
        print(error)
    print(f"{len(errors)} problem(s) found" if errors else "All pages OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Test the checker against bad pages**

Run:

```bash
mkdir -p docs/skills docs/resources/trainers
printf -- '---\ntags:\n  - aim\n---\nNo sections.\n' > docs/skills/bad.md
printf -- '---\ntags:\n  - trainer\n---\nNo sections.\n' > docs/resources/trainers/bad.md
.venv/Scripts/python scripts/check_pages.py --drafts; echo "exit=$?"
```

Expected output, in this order (sorted paths), followed by `exit=1`:

```text
resources/trainers/bad.md: missing '## Related wiki pages' section
resources/trainers/bad.md: missing draft banner
skills/bad.md: tag 'aim' is not allowed
skills/bad.md: missing '## Further resources' section
skills/bad.md: missing draft banner
5 problem(s) found
```

Then delete the test pages:

```bash
rm docs/skills/bad.md docs/resources/trainers/bad.md
```

- [ ] **Step 5: Create `mkdocs.yml` and abbreviations**

`mkdocs.yml`:

```yaml
site_name: Aim Wiki
site_description: Aim training concepts, routines, and a guide to the best existing resources.
site_url: https://bassel-bakr.github.io/aim-wiki/
repo_url: https://github.com/bassel-bakr/aim-wiki
repo_name: bassel-bakr/aim-wiki
edit_uri: edit/main/docs/
copyright: Content licensed under <a href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0</a>

theme:
  name: material
  features:
    - content.action.edit
    - navigation.tabs
    - navigation.sections
    - navigation.indexes
    - navigation.footer
    - search.suggest
    - search.highlight
    - toc.follow
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

plugins:
  - search
  - tags

markdown_extensions:
  - abbr
  - admonition
  - attr_list
  - md_in_html
  - tables
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.superfences
  - pymdownx.tabbed:
      alternate_style: true
  - pymdownx.snippets:
      auto_append:
        - includes/abbreviations.md

nav:
  - Home: index.md
  - Getting Started:
      - getting-started/index.md
      - getting-started/sensitivity.md
      - getting-started/setup.md
      - getting-started/aim-trainers.md
  - Fundamentals:
      - fundamentals/index.md
      - fundamentals/how-aim-works.md
      - fundamentals/practice-principles.md
      - fundamentals/transfer-to-games.md
  - Skills:
      - skills/index.md
      - skills/clicking.md
      - skills/tracking.md
      - skills/switching.md
  - Training:
      - training/index.md
      - training/routines.md
      - training/benchmarks.md
      - training/progress-and-plateaus.md
      - training/health.md
  - Resources:
      - resources/index.md
      - Communities:
          - resources/communities/voltaic.md
          - resources/communities/jade-palace.md
          - resources/communities/revosect.md
      - Trainers:
          - resources/trainers/kovaaks.md
          - resources/trainers/aimlabs.md
      - Creators:
          - resources/creators/corporate-serf.md
          - resources/creators/matty-ow.md
          - resources/creators/aimer-lew.md
          - resources/creators/viscose.md
  - Glossary: glossary.md
  - Tags: tags.md
```

`includes/abbreviations.md` (the glossary task extends this file):

```markdown
*[DPI]: Dots per inch. How far the cursor moves per inch of mouse movement.
*[eDPI]: Effective DPI. Mouse DPI multiplied by in-game sensitivity.
*[FOV]: Field of view.
*[FPS]: Frames per second.
*[Hz]: Hertz. Monitor refresh rate.
```

- [ ] **Step 6: Generate page stubs**

Run this one-off generator from the repository root. Do not commit the generator.

```bash
.venv/Scripts/python - <<'EOF'
from pathlib import Path

BANNER = '!!! warning "Draft"\n    Written from public sources, pending review.\n'
PAGES = [
    ("index.md", "Aim Wiki", ["beginner"]),
    ("getting-started/index.md", "Start Here", ["beginner"]),
    ("getting-started/sensitivity.md", "Sensitivity", ["sensitivity", "beginner"]),
    ("getting-started/setup.md", "Setup and Gear", ["beginner"]),
    ("getting-started/aim-trainers.md", "Choosing an Aim Trainer", ["beginner"]),
    ("fundamentals/index.md", "Fundamentals", ["beginner"]),
    ("fundamentals/how-aim-works.md", "How Aim Works", ["beginner"]),
    ("fundamentals/practice-principles.md", "Practice Principles", ["routines"]),
    ("fundamentals/transfer-to-games.md", "Transfer to Games", ["beginner"]),
    ("skills/index.md", "Skills", ["clicking", "tracking", "switching"]),
    ("skills/clicking.md", "Clicking", ["clicking"]),
    ("skills/tracking.md", "Tracking", ["tracking"]),
    ("skills/switching.md", "Target Switching", ["switching"]),
    ("training/index.md", "Training", ["routines"]),
    ("training/routines.md", "Routines", ["routines"]),
    ("training/benchmarks.md", "Benchmarks", ["benchmarks"]),
    ("training/progress-and-plateaus.md", "Progress and Plateaus", ["routines", "benchmarks"]),
    ("training/health.md", "Health and Rest", ["beginner"]),
    ("resources/index.md", "Resources", []),
    ("resources/communities/voltaic.md", "Voltaic", ["community", "benchmarks", "routines"]),
    ("resources/communities/jade-palace.md", "Jade Palace", ["community"]),
    ("resources/communities/revosect.md", "Revosect", ["community"]),
    ("resources/trainers/kovaaks.md", "KovaaK's", ["trainer"]),
    ("resources/trainers/aimlabs.md", "Aimlabs", ["trainer"]),
    ("resources/creators/corporate-serf.md", "Corporate Serf", ["creator"]),
    ("resources/creators/matty-ow.md", "VT Matty (MattyOW)", ["creator"]),
    ("resources/creators/aimer-lew.md", "AimerLew", ["creator"]),
    ("resources/creators/viscose.md", "Viscose", ["creator"]),
    ("glossary.md", "Glossary", []),
]
CONCEPT_DIRS = {"getting-started", "fundamentals", "skills", "training"}

for rel, title, tags in PAGES:
    section = rel.split("/")[0]
    is_index = rel.endswith("index.md")
    front = f'---\ntitle: "{title}"\n'
    if tags:
        front += "tags:\n" + "".join(f"  - {tag}\n" for tag in tags)
    front += "---\n\n"
    body = BANNER
    if section in CONCEPT_DIRS and not is_index:
        body += "\n## Further resources\n"
    if section == "resources" and not is_index:
        body += "\n## Related wiki pages\n"
    path = Path("docs") / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(front + body, encoding="utf-8", newline="\n")

Path("docs/tags.md").write_text(
    '---\ntitle: "Tags"\n---\n\nPages grouped by tag.\n\n<!-- material/tags -->\n',
    encoding="utf-8", newline="\n",
)
print(f"{len(PAGES) + 1} pages written")
EOF
```

Expected: `30 pages written`.

- [ ] **Step 7: Verify checker and strict build pass**

Run:

```bash
.venv/Scripts/python scripts/check_pages.py --drafts
.venv/Scripts/zensical build --clean --strict
ls site/tags/index.html site/resources/creators/viscose/index.html
```

Expected: `All pages OK`, then `No issues found` and `Build finished`, then both paths listed with no error.

- [ ] **Step 8: Commit**

```bash
git add .gitignore .gitattributes requirements.txt mkdocs.yml includes scripts docs
git commit -m "feat: scaffold zensical site, page stubs, and page checker

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Templates, README, CONTRIBUTING, and LICENSE

**Files:**
- Create: `templates/concept.md`, `templates/resource.md`, `README.md`, `CONTRIBUTING.md`, `LICENSE`

**Interfaces:**
- Consumes: `scripts/check_pages.py` and the allowed tag list from Task 1.
- Produces: the templates that Tasks 4–10 follow for page structure.

- [ ] **Step 1: Write `templates/concept.md`**

````markdown
---
title: "Concept Name"
tags:
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

Two or three sentences that summarize the concept. A reader who stops here should still learn the
main idea.

## Explanation

What the concept is and why it matters. Link each fact to its source, for example
[Voltaic](https://voltaic.gg).

## Common mistakes

- Mistake: one sentence on why it hurts progress.

## How to train it

Concrete practice advice. Link to specific scenarios, playlists, or routines where possible.

## Further resources

- [Resource page title](../resources/communities/voltaic.md): one line on why it is relevant here.
````

- [ ] **Step 2: Write `templates/resource.md`**

````markdown
---
title: "Resource Name"
tags:
  - community
---

!!! warning "Draft"
    Written from public sources, pending review.

**Links:** [Website](https://example.com) · [Discord](https://example.com) · [YouTube](https://example.com)

## What it is

One or two sentences: what this resource is and who runs it.

## Who it suits

The skill levels and goals this resource serves best.

## What it covers

Topics and skills covered, with links to the matching wiki pages.

## Key content

- [Name of guide or video](https://example.com): one-line summary in our own words.

## Our take

Strengths, limits, and when to use this resource.

## Related wiki pages

- [Page title](../../skills/tracking.md)
````

- [ ] **Step 3: Write `README.md`**

````markdown
# Aim Wiki

An aim training wiki. It explains aim concepts in its own words and points to the best existing
resources, such as Voltaic, Jade Palace, Revosect, KovaaK's, Aimlabs, and aim training creators.

Site: <https://bassel-bakr.github.io/aim-wiki/>

## Run the site locally

You need Python 3.10 or later.

```bash
python -m venv .venv
```

Activate the environment:

- Windows PowerShell: `.venv\Scripts\Activate.ps1`
- macOS or Linux: `source .venv/bin/activate`

Install dependencies and start the preview server:

```bash
pip install -r requirements.txt
zensical serve
```

Open <http://localhost:8000>. The page reloads when you save a file.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

Content is licensed under [CC BY-SA 4.0](LICENSE).
````

- [ ] **Step 4: Write `CONTRIBUTING.md`**

````markdown
# Contributing to Aim Wiki

Thank you for helping. This guide explains how to add or change pages.

## Ways to contribute

- Fix a mistake: click the edit button (pencil icon) on any page. GitHub opens the file so you can
  propose a change.
- Add a page or a large change: open an issue first, so we can agree on scope.

## Run the site locally

Follow the steps in [README.md](README.md#run-the-site-locally).

## Add a page

1. Copy a template from `templates/`:
   - `concept.md` for pages that explain aim concepts or training advice.
   - `resource.md` for pages about a community, trainer, or creator.
2. Save the file in the matching folder under `docs/`.
3. Add the page to the `nav` list in `mkdocs.yml`.
4. Link the new page from at least one related page.

Page titles come from the `title:` field in the front matter. Do not add a `#` heading in the page
body.

## Writing rules

1. Write in your own words and link to the original source. Do not copy guides, tables, or images
   from other sites.
2. Link facts to their source inline.
3. Pages written from research but not yet fact-checked keep this banner at the top:

   ```markdown
   !!! warning "Draft"
       Written from public sources, pending review.
   ```

4. If you cannot verify a claim from a public source, leave it out, or mark it with
   `<!-- REVIEW: what needs checking -->`. HTML comments are hidden on the page but still visible
   in the page source.

## Tags

Use only these tags in the `tags:` front matter field:

- Type (resource pages only): `community`, `trainer`, `creator`
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`

To propose a new tag, open an issue.

## Glossary

Add new terms to `docs/glossary.md`. If the term is an abbreviation, also add it to
`includes/abbreviations.md`, so the site shows its meaning as a tooltip on every page.

## Check before you open a pull request

```bash
python scripts/check_pages.py
zensical build --clean --strict
```

Both commands must finish without problems. The same checks run automatically on every pull request.

## License

By contributing, you agree that your contribution is licensed under
[CC BY-SA 4.0](LICENSE).
````

- [ ] **Step 5: Download the license text**

Source: `https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt` (official Creative Commons plain-text legal code, about 20 KB).

```bash
curl -fsSL https://creativecommons.org/licenses/by-sa/4.0/legalcode.txt -o LICENSE
head -c 300 LICENSE
wc -c LICENSE
```

Expected: the start of the file contains `Attribution-ShareAlike 4.0 International`, and the size is between 15000 and 30000 bytes.

- [ ] **Step 6: Verify nothing in `templates/` is published**

```bash
.venv/Scripts/zensical build --clean --strict
ls site | grep -c templates
```

Expected: build prints `No issues found`. `grep -c` prints `0`.

- [ ] **Step 7: Commit**

```bash
git add templates README.md CONTRIBUTING.md LICENSE
git commit -m "docs: add page templates, readme, contributing guide, and license

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 3: GitHub Actions workflows

**Files:**
- Create: `.github/workflows/deploy.yml`, `.github/workflows/check.yml`

**Interfaces:**
- Consumes: `requirements.txt`, `scripts/check_pages.py`, `zensical build --clean --strict`.

- [ ] **Step 1: Write `.github/workflows/deploy.yml`**

Based on the published Zensical GitHub Pages workflow (<https://zensical.org/docs/publish-your-site/>).

```yaml
name: Deploy

on:
  push:
    branches:
      - main
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - uses: actions/configure-pages@v6
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: zensical build --clean --strict
      - uses: actions/upload-pages-artifact@v5
        with:
          path: site
      - uses: actions/deploy-pages@v5
        id: deployment
```

- [ ] **Step 2: Write `.github/workflows/check.yml`**

```yaml
name: Check

on:
  pull_request:
  schedule:
    - cron: "17 6 * * 1"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  build:
    if: github.event_name == 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install -r requirements.txt
      - run: python scripts/check_pages.py
      - run: zensical build --clean --strict

  links:
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v7
      - uses: lycheeverse/lychee-action@v2
        with:
          args: >-
            --no-progress
            --max-retries 3
            --accept 200,206,429
            --exclude "^https://(x|twitter)\.com/"
            --exclude "^https://discord\.(gg|com)/"
            "docs/**/*.md"
          fail: true
```

X and Discord are excluded because they block automated requests, which would cause false failures.

- [ ] **Step 3: Validate both files parse as YAML with the expected structure**

```bash
.venv/Scripts/python - <<'EOF'
import yaml
deploy = yaml.safe_load(open(".github/workflows/deploy.yml", encoding="utf-8"))
check = yaml.safe_load(open(".github/workflows/check.yml", encoding="utf-8"))
# PyYAML parses the bare key `on` as boolean True.
assert deploy[True]["push"]["branches"] == ["main"]
assert set(check[True]) == {"pull_request", "schedule", "workflow_dispatch"}
assert set(check["jobs"]) == {"build", "links"}
print("workflows OK")
EOF
```

Expected: `workflows OK`.

- [ ] **Step 4: Commit**

```bash
git add .github
git commit -m "ci: add pages deploy and pull request checks

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Content tasks (Tasks 4–10): shared procedure

Each content task drafts a group of pages. Follow this procedure for every page in the task:

1. **Research.** Use web search and fetch the official sources listed in the task. Record each URL you
   use. Prefer official sites, official blogs, official YouTube or X accounts, and Steam store pages.
2. **Write.** Keep the stub's front matter (`title`, `tags`) and the draft banner. Follow the structure
   of `templates/concept.md` or `templates/resource.md`. Concept pages must have a summary paragraph
   and `## Further resources`. Use the other template sections where they fit the topic. Resource
   pages use every template section. Target length: 300–900 words per concept page, 200–500 words per
   resource page.
3. **Link.** Link facts to sources inline. Link to other wiki pages with relative paths to `.md` files,
   for example `[Tracking](../skills/tracking.md)`.
4. **Sourcing rules** from Global Constraints apply without exception. The task lists research
   questions. Use a `<!-- REVIEW: ... -->` comment for any question you cannot answer from a public
   source.
5. **Tags.** A task can add topic tags to a page when research shows the page is about that topic. Use
   only allowed tags.

Verification for every content task:

```bash
.venv/Scripts/python scripts/check_pages.py --drafts
.venv/Scripts/zensical build --clean --strict
```

Expected: `All pages OK`, then `No issues found`.

---

### Task 4: Community resource pages

**Files:**
- Modify: `docs/resources/communities/voltaic.md`, `docs/resources/communities/jade-palace.md`, `docs/resources/communities/revosect.md`

**Interfaces:**
- Consumes: `templates/resource.md` from Task 2.
- Produces: resource pages that concept pages in Tasks 7–10 link to.

- [ ] **Step 1: Research and draft `voltaic.md`**

Starting sources: <https://voltaic.gg>, <https://blog.voltaic.gg>, <https://blog.voltaic.gg/announcing-the-voltaic-season-5-aiming-benchmarks-beta-for-kovaaks/>, <https://blog.voltaic.gg/announcing-the-voltaic-season-3-aiming-benchmarks-beta-for-aimlabs/>.

Research questions:
- What is Voltaic, and what does it offer (benchmarks, Discord, routines or playlists, guides, coaching)?
- Which benchmark season is current for KovaaK's and for Aimlabs?
- What are the Season 5 categories and subcategories? Expected from the announcement: Clicking (dynamic, static, linear), Tracking (precise, reactive, control), Switching (speed, evasive, stability). Confirm against the source.
- How are benchmark ranks named and structured? Describe, do not copy the rank tables.
- Where are the official Discord and social links?

In "Related wiki pages", link: `../../training/benchmarks.md`, `../../training/routines.md`, `../../skills/index.md`, `../trainers/kovaaks.md`, `../trainers/aimlabs.md`.

- [ ] **Step 2: Research and draft `jade-palace.md`**

Starting sources: <https://x.com/Matty_OW/status/1901508775044854146>, <https://x.com/Matty_OW/status/1961519224884523098>.

Research questions:
- What is Jade Palace? The starting sources describe an application-based Discord server where elite aimers and aim content creators chat and collaborate.
- Who runs it? The starting sources point to VT Matty (MattyOW). Confirm.
- How do people join? Is there a public channel for questions from non-members?
- What public output exists, if any (videos, routines, posts)?

Public detail is limited. Keep the page short and state only what sources confirm. Do not put the Discord invite link in the page unless it appears on an official public profile. Invite links expire.

In "Related wiki pages", link: `../creators/matty-ow.md`, `../../training/routines.md`.

- [ ] **Step 3: Research and draft `revosect.md`**

Research questions:
- What is Revosect (community, benchmarks, playlists, Discord)? Find the official site or Discord listing.
- What does it offer, and how does it differ from Voltaic?
- Which trainer does its content target?

Add topic tags (for example `benchmarks` or `routines`) only if research confirms them.

In "Related wiki pages", link: `../communities/voltaic.md`, `../../training/benchmarks.md`, and any skills page that research shows is relevant.

- [ ] **Step 4: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 5: Commit**

```bash
git add docs/resources/communities
git commit -m "docs: draft community resource pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 5: Trainer resource pages

**Files:**
- Modify: `docs/resources/trainers/kovaaks.md`, `docs/resources/trainers/aimlabs.md`

**Interfaces:**
- Consumes: `templates/resource.md`. Links to Task 4 pages.

- [ ] **Step 1: Research and draft `kovaaks.md`**

Starting sources: the KovaaK's Steam store page, the official KovaaK's site.

Research questions:
- Price model (paid, free, DLC) and platform.
- Core features: scenarios, playlists, community-made scenarios, sensitivity matching to games, stats.
- Which major benchmarks run in KovaaK's (Voltaic Season 5, and Revosect if Task 4 confirmed it)?

In "Related wiki pages", link: `../../getting-started/aim-trainers.md`, `../../getting-started/sensitivity.md`, `../communities/voltaic.md`, `../../training/benchmarks.md`.

- [ ] **Step 2: Research and draft `aimlabs.md`**

Starting sources: the Aimlabs Steam store page, the official Aimlabs site.

Research questions:
- Price model and platforms.
- Core features: tasks, game-specific training, playlists, stats.
- Current Voltaic benchmark season for Aimlabs.

In "Related wiki pages", link: `../../getting-started/aim-trainers.md`, `../communities/voltaic.md`, `../../training/benchmarks.md`.

- [ ] **Step 3: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 4: Commit**

```bash
git add docs/resources/trainers
git commit -m "docs: draft trainer resource pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 6: Creator resource pages

**Files:**
- Modify: `docs/resources/creators/corporate-serf.md`, `docs/resources/creators/matty-ow.md`, `docs/resources/creators/aimer-lew.md`, `docs/resources/creators/viscose.md`

**Interfaces:**
- Consumes: `templates/resource.md`. Links to Task 4 and Task 5 pages.

For each creator:

- Find the official YouTube channel and confirm the handle. The owner named: Corporate Serf, MattyOW, `@AimerLew`, ViscoseOC.
- Find other official links (X, Twitch, Discord) only from the creator's own channel or profile.
- Describe the creator's focus (for example tutorials, routines, analysis, benchmarks) from their channel and video list.
- List 3–5 representative videos or guides under "Key content", each with a one-line summary in our own words. Pick videos that match wiki topics.
- Add topic tags that match their main focus.
- Do not state subscriber counts, ranks, or achievements unless an official source confirms them. Such numbers change, so avoid them where they add little.

- [ ] **Step 1: Draft `corporate-serf.md`**

In "Related wiki pages", link at least two skills or training pages that match the creator's content.

- [ ] **Step 2: Draft `matty-ow.md`**

Research questions: What is Matty's connection to Voltaic (the "VT" prefix) and to Jade Palace? Confirm from official profiles.

In "Related wiki pages", link: `../communities/jade-palace.md`, `../communities/voltaic.md`, and at least one skills or training page.

- [ ] **Step 3: Draft `aimer-lew.md`**

In "Related wiki pages", link at least two skills or training pages that match the creator's content.

- [ ] **Step 4: Draft `viscose.md`**

Research questions: Does Viscose publish a written aim guide or document in addition to videos? If yes, link it under "Key content".

In "Related wiki pages", link at least two skills or training pages that match the creator's content.

- [ ] **Step 5: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 6: Commit**

```bash
git add docs/resources/creators
git commit -m "docs: draft creator resource pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 7: Getting Started pages

**Files:**
- Modify: `docs/getting-started/index.md`, `docs/getting-started/sensitivity.md`, `docs/getting-started/setup.md`, `docs/getting-started/aim-trainers.md`

**Interfaces:**
- Consumes: resource pages from Tasks 4–6. Links forward to Fundamentals, Skills, and Training pages (stubs exist, so links resolve).

- [ ] **Step 1: Draft `getting-started/index.md` (overview page)**

Content: who the wiki is for, and a numbered roadmap:
1. Set up gear and sensitivity (link `setup.md`, `sensitivity.md`).
2. Pick a trainer (link `aim-trainers.md`).
3. Learn the fundamentals (link `../fundamentals/index.md`).
4. Run a benchmark to find weaknesses (link `../training/benchmarks.md`).
5. Follow a routine (link `../training/routines.md`).
6. Track progress and handle plateaus (link `../training/progress-and-plateaus.md`).

- [ ] **Step 2: Draft `sensitivity.md`**

Cover: cm/360 (definition and how to measure it), eDPI (DPI × in-game sensitivity; only comparable within one game), trade-offs of low and high sensitivity, how to choose a starting point, converting sensitivity between games and trainers (KovaaK's sensitivity matching, reputable converter tools), when to change sensitivity and when not to. Research whether well-known sources (for example Voltaic) recommend sensitivity variation in training, and cite the source if so. Do not invent "ideal" numeric ranges. Cite any range you give.

Further resources: `../resources/trainers/kovaaks.md`, plus any creator page with a relevant sensitivity video.

- [ ] **Step 3: Draft `setup.md`**

Cover: mouse (shape and weight matter more than sensor for most players), mousepad (control versus speed surfaces), grip styles (palm, claw, fingertip), posture and arm position, monitor refresh rate and FPS, and essential settings: raw input on, mouse acceleration off, Windows "Enhance pointer precision" off. Keep gear advice brand-neutral.

Further resources: at least one resource page with setup content, found in Tasks 4–6.

- [ ] **Step 4: Draft `aim-trainers.md`**

Cover: why use an aim trainer, KovaaK's versus Aimlabs versus in-game practice (deathmatch, practice range), and how to choose. Keep the comparison factual and link to `../resources/trainers/kovaaks.md` and `../resources/trainers/aimlabs.md` for details.

Further resources: both trainer pages and `../resources/communities/voltaic.md`.

- [ ] **Step 5: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 6: Commit**

```bash
git add docs/getting-started
git commit -m "docs: draft getting started pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 8: Fundamentals pages

**Files:**
- Modify: `docs/fundamentals/index.md`, `docs/fundamentals/how-aim-works.md`, `docs/fundamentals/practice-principles.md`, `docs/fundamentals/transfer-to-games.md`

**Interfaces:**
- Consumes: resource pages from Tasks 4–6.

- [ ] **Step 1: Draft `fundamentals/index.md` (overview page)**

Content: one paragraph on why fundamentals come before specific skills, and one line plus a link for each of the three child pages.

- [ ] **Step 2: Draft `how-aim-works.md`**

Cover: arm, wrist, and finger aim, and when each is used; large corrections versus micro-adjustments; the speed versus accuracy trade-off; smoothness; reaction versus prediction. Use the concept template sections: Explanation, Common mistakes, How to train it.

Further resources: resource pages with fundamentals content found in Tasks 4–6.

- [ ] **Step 3: Draft `practice-principles.md`**

Cover: deliberate practice (focused attention on one weakness), quality over volume, scenario variety versus repetition, score chasing versus technique focus, rest and consistency. Cite a source for each principle attributed to a community or creator.

Further resources: `../resources/communities/voltaic.md`, plus creator pages with practice-method content.

- [ ] **Step 4: Draft `transfer-to-games.md`**

Cover: what aim trainers train well (mechanics), what they do not train (crosshair placement, movement, positioning, game sense, recoil), and how to combine trainer practice with in-game practice.

Further resources: at least one resource page on the topic found in Tasks 4–6.

- [ ] **Step 5: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 6: Commit**

```bash
git add docs/fundamentals
git commit -m "docs: draft fundamentals pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 9: Skills pages

**Files:**
- Modify: `docs/skills/index.md`, `docs/skills/clicking.md`, `docs/skills/tracking.md`, `docs/skills/switching.md`

**Interfaces:**
- Consumes: Voltaic Season 5 taxonomy confirmed in Task 4 (`docs/resources/communities/voltaic.md`).

- [ ] **Step 1: Draft `skills/index.md` (overview page)**

Content: one paragraph on the three skill families, and a table with columns Skill, Subcategories, and Short description, one row per family, each linking its page. State that the subcategory names follow the Voltaic Season 5 benchmarks and link the source announcement.

- [ ] **Step 2: Draft `clicking.md`**

One summary paragraph. Then one `##` section each for dynamic clicking, static clicking, and linear clicking. In each section: what it is, what good execution looks like, common mistakes, and how to train it. Name specific scenarios only when a public benchmark list confirms them. End with `## Further resources`.

- [ ] **Step 3: Draft `tracking.md`**

Same structure, with sections for precise tracking, reactive tracking, and control tracking.

- [ ] **Step 4: Draft `switching.md`**

Same structure, with sections for speed switching, evasive switching, and stability switching.

- [ ] **Step 5: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 6: Commit**

```bash
git add docs/skills
git commit -m "docs: draft skills pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 10: Training pages

**Files:**
- Modify: `docs/training/index.md`, `docs/training/routines.md`, `docs/training/benchmarks.md`, `docs/training/progress-and-plateaus.md`, `docs/training/health.md`

**Interfaces:**
- Consumes: resource pages from Tasks 4–6. Links to Skills pages from Task 9.

- [ ] **Step 1: Draft `training/index.md` (overview page)**

Content: one paragraph on how to structure training over weeks, and one line plus a link for each child page.

- [ ] **Step 2: Draft `routines.md`**

Cover: parts of a routine (warm-up, focus block, review), session length, how to pick scenarios for your weaknesses, using existing playlists (link the Voltaic page and any creator routines found in Task 6), and how often to change a routine.

- [ ] **Step 3: Draft `benchmarks.md`**

Cover: what a benchmark is, how to use one to find weaknesses, how Voltaic ranks work (describe the structure and link the official source; do not copy rank tables), how often to rerun a benchmark, and why not to over-focus on rank.

- [ ] **Step 4: Draft `progress-and-plateaus.md`**

Cover: normal progress patterns, tracking scores over time, causes of plateaus (fatigue, one-sided practice, no technique focus), and ways past a plateau (switch focus, rest days, sensitivity or scenario variation where a source supports it).

- [ ] **Step 5: Draft `health.md`**

Directly below the draft banner, add:

```markdown
!!! note "Not medical advice"
    This page shares general information only. If you have pain, numbness, or tingling, stop
    training and see a medical professional.
```

Cover: regular breaks, warm-up before intense sessions, posture and desk setup (link `../getting-started/setup.md`), signs of strain, and sleep and rest days. Cite reputable health sources (for example public health or ergonomics organizations) for health claims.

- [ ] **Step 6: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 7: Commit**

```bash
git add docs/training
git commit -m "docs: draft training pages

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 11: Home, Resources overview, and Glossary

**Files:**
- Modify: `docs/index.md`, `docs/resources/index.md`, `docs/glossary.md`, `includes/abbreviations.md`

**Interfaces:**
- Consumes: all pages from Tasks 4–10.

- [ ] **Step 1: Draft `docs/index.md` (home)**

Content: what the wiki is (a few sentences), a "Start here" link to `getting-started/index.md`, one line plus a link for each top-level section, and a short note that pages are drafts under review, with links to the edit button explanation in CONTRIBUTING and to the GitHub repository.

- [ ] **Step 2: Draft `docs/resources/index.md`**

Content: one paragraph on what the resource pages are for. Then three `##` sections (Communities, Trainers, Creators), each listing its pages with a one-line summary taken from that page's "What it is" section. End with links to the Tags page (`../tags.md`) for filtering by topic.

- [ ] **Step 3: Draft `docs/glossary.md`**

Collect every aim term used across the wiki, in alphabetical order, as a definition list or `###` headings with one or two sentences each. Link each term to the page that explains it in depth. Include at least: cm/360, DPI, eDPI, FOV, FPS, Hz, benchmark, clicking (dynamic, static, linear), flick, micro-adjustment, overflick, underflick, playlist, raw input, routine, scenario, sensitivity, smoothness, target switching, tracking (precise, reactive, control).

- [ ] **Step 4: Extend `includes/abbreviations.md`**

Add a `*[ABBR]: meaning` line for every abbreviation defined in the glossary that is not in the file yet. Only true abbreviations belong here, because every matching word on every page gets a tooltip.

- [ ] **Step 5: Verify**

Run the content task verification commands. Expected: `All pages OK`, `No issues found`.

- [ ] **Step 6: Commit**

```bash
git add docs/index.md docs/resources/index.md docs/glossary.md includes/abbreviations.md
git commit -m "docs: draft home, resources overview, and glossary

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 12: Acceptance check

**Files:**
- Modify: only files that fail a check below.

- [ ] **Step 1: Automated checks**

```bash
.venv/Scripts/python scripts/check_pages.py --drafts
.venv/Scripts/zensical build --clean --strict
grep -rl "TODO\|TBD\|example.com" docs || echo "no placeholders"
```

Expected: `All pages OK`, `No issues found`, `no placeholders`.

- [ ] **Step 2: Review markers report**

```bash
grep -rn "REVIEW:" docs || echo "no review markers"
```

Record the output. It goes in the handoff report to the owner.

- [ ] **Step 3: Visual check**

Run `.venv/Scripts/zensical serve` and open <http://localhost:8000>. Confirm:
- Every navigation tab opens and every page in the nav renders.
- The Tags page lists pages under each tag.
- Hovering "eDPI" on the Sensitivity page shows the tooltip.
- The edit button on a page links to `https://github.com/bassel-bakr/aim-wiki/edit/main/docs/...`.
- The footer shows the CC BY-SA 4.0 notice.
- The light/dark toggle works.

- [ ] **Step 4: Copy check**

For each resource page, open its main source and compare. No sentence in the wiki may match source text word for word, except short quoted names and titles. Rewrite any match.

- [ ] **Step 5: Commit fixes, if any**

```bash
git add -A docs includes
git commit -m "docs: fix issues found in acceptance check

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

Skip this step if no files changed.

## Owner steps after the plan (not automated)

1. Create the repository `bassel-bakr/aim-wiki` on GitHub and push `main`.
2. In repository Settings → Pages, set Source to "GitHub Actions".
3. Fact-check each drafted page, resolve `REVIEW:` markers, and remove the draft banner.
