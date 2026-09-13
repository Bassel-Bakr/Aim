# Readability Pass Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every wiki page readable in passes — short paragraphs, short sentences, the answer
first, one next action — and enforce that in the page checker so it stays that way.

**Architecture:** The rules land in `scripts/check_pages.py` behind a `--readability` flag, with a
new `scripts/check_rewrite.py` that proves a rewrite kept every link, citation, heading, and the
front matter. Six batches of page rewrites follow, each checked by both scripts. The last task makes
the readability rules the checker's default, which puts them in CI.

**Tech Stack:** Markdown built by Zensical; Python 3.10+ checks using the standard library and
PyYAML, both already in `requirements.txt`. No new dependency.

**Spec:** `specs/2026-09-13-readability-design.md`

## Global Constraints

These bind every task. The page rewrite procedure below is part of every page task's requirements.

- Paragraph limit: 45 words. Sentence limit: 25 words, list items included.
- Concept pages — pages in `getting-started`, `fundamentals`, `categories`, `techniques`,
  `training`, other than `index.md` — open with 3 to 5 bullets before their first `##` heading, and
  carry a paragraph opening `**Do this next.**` before `## Further resources`.
- US spelling in wiki prose. Footnote definitions are exempt.
- A rewrite never renames a `##` or `###` heading, never adds or removes a link target, never adds or
  removes a footnote reference, and never touches front matter or the draft banner.
- No slang, no casual voice, no change of register. Plain and technical, as the pages are now.
- No fact added, none removed. A footnote stays attached to the claim it supports.
- Prose in the repository's own words. Never paste source wording; never attribute to a source a
  claim it does not make.
- Topic pages under `docs/topics/` are out of scope and must not be edited.
- `zensical build` is not run with `--strict`: link problems show as warnings, so read its output
  rather than trusting the exit code.
- The shell's `grep` in this repository is wrapped by a proxy that has returned whole files instead
  of matches. Use Python, or a dedicated search tool, to count or locate text.
- Activate the virtualenv before running Python: `.venv\Scripts\Activate.ps1` in PowerShell,
  `source .venv/Scripts/activate` in bash.

### The approved model

`docs/wiki/fundamentals/how-aim-works.md` as of commit `0c1fed6` is the approved sample of every
rule. Read it before rewriting anything. Its shape:

- One short intro sentence, then four bullets, each a bold lead plus one short sentence.
- Sections of short paragraphs, one idea each, the bold lead-ins kept as scan anchors.
- `## Common mistakes` bullets of one clause each.
- `**Do this next.**` closing the last content section, with a link the page already had.

### The page rewrite procedure

Apply to every page a page task names, one page at a time.

1. Record the base: `git rev-parse HEAD`. Every gate below compares against this commit.
2. Run the checker on the page and read every problem it lists:
   `python scripts/check_pages.py --readability <page>`
3. Rewrite the page to the rules. Split long sentences at their natural joints. Give each idea its
   own paragraph. Turn a run-on procedure into numbered steps. Replace British spellings.
4. On a concept page, write the answer-first bullets from what the page already says, and write the
   `**Do this next.**` paragraph. The next action may link only to a target the page already links
   to, because the rewrite gate rejects added links. If the page's sources do not support a specific
   action, the action states the page's principle instead — never invent a drill, a scenario name,
   or a number.
5. Run the checker on the page until it prints `All pages OK`:
   `python scripts/check_pages.py --readability <page>`
6. Run the rewrite gate until it prints `Invariants unchanged`:
   `python scripts/check_rewrite.py <base> <page>`
   A reported change is fixed by restoring what was lost, not by editing the gate.
7. Read the rewritten page end to end once. Confirm every claim from the original is still there
   and every footnote still follows the sentence that makes its claim.
8. Commit that page alone, with a message in the repository's style: an imperative subject under 72
   characters, a body saying why, and the `Co-Authored-By` trailer.

After the last page in a task, run once for the whole site:

```bash
python scripts/check_pages.py
```

Expected: `All pages OK` — the default run, without `--readability`, must still pass.

```bash
zensical build --clean
```

Expected: `No issues found`.

---

## File Structure

| File | Responsibility | Task |
| --- | --- | --- |
| `scripts/check_pages.py` | The readability rules, behind `--readability`; page-path arguments | 1, 8 |
| `scripts/check_rewrite.py` | New. Proves a rewrite kept links, citations, headings, front matter | 1 |
| `templates/concept.md` | Models the rules for new concept pages | 1 |
| `CONTRIBUTING.md` | Human-facing statement of the rules | 1, 8 |
| `AGENTS.md` | Agent-facing statement of the rules | 1, 8 |
| `docs/wiki/**/*.md` | The 30 pages that do not yet pass | 2–7 |

## Addition to the spec

The spec requires every rewrite to be gated on its link set, footnote set, headings, and front
matter, but names no tool. This plan adds `scripts/check_rewrite.py` for that, committed rather than
kept as a one-off: six tasks and thirty pages use it, and any later restructuring edit carries the
same risk. Its cost is one short script with no dependencies. It was run against the approved sample
before this plan was written: it passes the real rewrite, and it reports all four changes when the
sample's first-draft regression is replayed — a dropped myth link, a dropped citation, and a renamed
heading counted as one removal and one addition.

---

### Task 1: The checker, the rewrite gate, the template, and the docs

**Files:**
- Modify: `scripts/check_pages.py` (whole file replaced; shown in full below)
- Create: `scripts/check_rewrite.py`
- Modify: `templates/concept.md` (whole file replaced)
- Modify: `AGENTS.md:47-52` and the numbered list under "Rules that are easy to get wrong"
- Modify: `CONTRIBUTING.md` — the Tags list, a new "Readability" section, and "Check before you
  open a pull request"

**Interfaces:**
- Consumes: nothing.
- Produces:
  - `python scripts/check_pages.py --readability [<page> ...]` — exits 0 and prints
    `All pages OK` when the named pages (or all pages) pass; otherwise exits 1, prints one line per
    problem, and a final `<n> problem(s) found`.
  - `python scripts/check_rewrite.py <git-ref> <page> [<page> ...]` — exits 0 and prints
    `Invariants unchanged`, or exits 1 and prints one line per changed invariant, and a final
    `<n> change(s) to invariants`.

- [ ] **Step 1: Record the checker's current behaviour on the whole site**

Run: `python scripts/check_pages.py`
Expected: `All pages OK`, exit 0. If not, stop and report: the task must start from a passing site.

- [ ] **Step 2: Replace `scripts/check_pages.py`**

Write exactly this file. Every rule that exists today is kept unchanged; the readability rules and
page-path arguments are added.

````python
"""Check wiki pages against the rules in CONTRIBUTING.md.

Usage:
    python scripts/check_pages.py                  # tags and required sections
    python scripts/check_pages.py --drafts         # also require the draft banner
    python scripts/check_pages.py --readability    # also enforce the readability rules
    python scripts/check_pages.py --readability docs/wiki/glossary.md   # check named pages only
"""
import re
import sys
from pathlib import Path

import yaml

DOCS = Path(__file__).resolve().parent.parent / "docs"
WIKI = DOCS / "wiki"
EXEMPT_FROM_BANNER = {"index.md", "wiki/tags.md"}
ALLOWED_TAGS = {
    "community", "trainer", "tool",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
    "myth",
}
CONCEPT_DIRS = {"getting-started", "fundamentals", "categories", "techniques", "training"}
BANNER = '!!! warning "Draft"'
# Topics live outside docs/wiki/ because they run on a different trust model: signed opinion
# written from experience, carrying the author's name instead of a citation trail. They are not
# wiki pages and do not follow wiki rules.
TOPICS = DOCS / "topics"
BYLINE = '!!! info "Written by '
# The inline .aim-myth block's title is the anchor into wiki/myths.md: it must match a hub
# heading word for word, or the link it ships with silently lands at the top of the page.
MYTH_BLOCK = re.compile(r'!!! myth "([^"]*)"')
MYTH_HEADING = re.compile(r"^## (.+)$", re.M)

# Readability. Most readers skim and many read with ADHD, so a page has to survive being read in
# passes: short paragraphs, short sentences, the answer first, and a way out at the end. See
# specs/2026-09-13-readability-design.md for where these numbers come from.
PARAGRAPH_LIMIT = 45
SENTENCE_LIMIT = 25
ANSWER_BULLETS = range(3, 6)
NEXT_ACTION = "**Do this next.**"
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’/-]*")
# A sentence ends at . ! ? : or ; followed by a capital or digit. Abbreviations and decimals are
# shielded first so "e.g. Voltaic" and "0.27 sensitivity" do not end one.
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|vs|etc|approx|cf)\.")
DECIMAL = re.compile(r"(\d)\.(\d)")
SENTENCE_END = re.compile(r"(?<=[.!?:;])[\"”’)]*\s+(?=[A-Z0-9\"“(\[])")
# The site writes US English, like its sources. Footnote definitions are exempt: they quote titles.
BRITISH = re.compile(
    r"\b(practis(?:e|ed|es|ing)|organis(?:e|ed|es|ing|ation)|behaviours?|colour(?:ed|ing|s)?"
    r"|centres?|analys(?:e|ed|es|ing)|labour|favourites?|defence|recognis(?:e|ed|es|ing)"
    r"|realis(?:e|ed|es|ing)|minimis(?:e|ed|es|ing)|optimis(?:e|ed|es|ing|ation))\b",
    re.I,
)


def front_matter(text):
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def myth_headings():
    text = (WIKI / "myths.md").read_text(encoding="utf-8")
    return set(MYTH_HEADING.findall(text))


def body(text):
    """The page without its front matter, comments, or fenced code."""
    text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S)


def prose_blocks(text):
    """Paragraphs and lists that readers read as prose, with markup a reader never sees removed.

    Headings, tables, footnote definitions, HTML, and admonitions are skipped: none of them is a
    run of prose, and an admonition body is indented so it is caught by the same test.
    """
    for block in re.split(r"\n\s*\n", body(text)):
        stripped = block.strip()
        if not stripped or block.startswith("    "):
            continue
        if stripped.startswith(("#", "|", "[^", "<", "!!!", "???")):
            continue
        yield stripped


def plain(text):
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?", r"\1", text)
    return " ".join(re.sub(r"[*_`]", "", text).split())


def units(block):
    """A list yields one unit per item; a prose block yields itself as one paragraph."""
    if re.match(r"([-*]|\d+\.)\s", block):
        items = re.split(r"\n\s*(?:[-*]|\d+\.)\s+", "\n" + block)
        return [(False, plain(item)) for item in items if item.strip()]
    return [(True, plain(block))]


def sentences(text):
    shielded = DECIMAL.sub(r"\1§\2", ABBREVIATION.sub(lambda m: m.group(0).replace(".", "§"), text))
    return [part.replace("§", ".") for part in SENTENCE_END.split(shielded) if part.strip()]


def words(text):
    return len(WORD.findall(text))


def excerpt(text):
    return text if len(text) <= 70 else text[:67] + "..."


def readability(rel, text, concept):
    errors = []
    for block in prose_blocks(text):
        for is_paragraph, unit in units(block):
            if is_paragraph and words(unit) > PARAGRAPH_LIMIT:
                errors.append(
                    f"{rel}: paragraph of {words(unit)} words (limit {PARAGRAPH_LIMIT}): "
                    f'"{excerpt(unit)}"'
                )
            for sentence in sentences(unit):
                if words(sentence) > SENTENCE_LIMIT:
                    errors.append(
                        f"{rel}: sentence of {words(sentence)} words (limit {SENTENCE_LIMIT}): "
                        f'"{excerpt(sentence)}"'
                    )
    prose = re.sub(r"^\[\^[^\]]+\]:.*$", "", body(text), flags=re.M)
    for spelling in sorted({match.lower() for match in BRITISH.findall(prose)}):
        errors.append(f"{rel}: British spelling '{spelling}', the site writes US English")
    if concept:
        lead = body(text).split("\n## ", 1)[0]
        bullets = len(re.findall(r"^- ", lead, flags=re.M))
        if bullets not in ANSWER_BULLETS:
            errors.append(
                f"{rel}: opens with {bullets} bullets before its first heading, expected 3 to 5"
            )
        before_resources = text.split("\n## Further resources", 1)[0]
        if NEXT_ACTION not in before_resources:
            errors.append(f"{rel}: missing a '{NEXT_ACTION}' paragraph before Further resources")
    return errors


def check(path, drafts, headings, readable):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    # Wiki pages live under docs/wiki/; their section is the first segment below that.
    in_wiki = path.is_relative_to(WIKI)
    section = path.relative_to(WIKI).as_posix().split("/")[0] if in_wiki else ""
    in_topics = path.is_relative_to(TOPICS)
    is_index = path.name == "index.md"
    errors = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    if section in CONCEPT_DIRS and not is_index and "\n## Further resources" not in text:
        errors.append(f"{rel}: missing '## Further resources' section")
    if section == "resources" and not is_index and "\n## Related wiki pages" not in text:
        errors.append(f"{rel}: missing '## Related wiki pages' section")
    if in_topics:
        # A byline replaces the draft banner: topic pages are signed, not pending review.
        if not is_index:
            if BYLINE not in text:
                errors.append(f'{rel}: missing byline, expected \'{BYLINE}<name>"\'')
            if "\n## Further resources" not in text:
                errors.append(f"{rel}: missing '## Further resources' section")
        if front_matter(text).get("tags"):
            errors.append(f"{rel}: topic pages do not carry tags")
    elif drafts and rel not in EXEMPT_FROM_BANNER and BANNER not in text:
        errors.append(f"{rel}: missing draft banner")
    if in_wiki:
        for title in MYTH_BLOCK.findall(text):
            if title not in headings:
                errors.append(
                    f"{rel}: myth block title '{title}' has no matching heading on wiki/myths.md"
                )
        if readable:
            errors += readability(rel, text, section in CONCEPT_DIRS and not is_index)
    return errors


def main():
    args = sys.argv[1:]
    drafts = "--drafts" in args
    readable = "--readability" in args
    named = [Path(arg).resolve() for arg in args if not arg.startswith("--")]
    paths = named or sorted(DOCS.rglob("*.md"))
    headings = myth_headings()
    errors = [error for path in paths for error in check(path, drafts, headings, readable)]
    for error in errors:
        print(error)
    print(f"{len(errors)} problem(s) found" if errors else "All pages OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
````

- [ ] **Step 3: Confirm the default run is unchanged**

Run: `python scripts/check_pages.py`
Expected: `All pages OK`, exit 0 — identical to Step 1. The readability rules must not run without
the flag.

- [ ] **Step 4: Confirm the approved sample passes and the rest of the wiki does not**

Run: `python scripts/check_pages.py --readability docs/wiki/fundamentals/how-aim-works.md`
Expected: `All pages OK`, exit 0.

Run: `python scripts/check_pages.py --readability docs/wiki/tags.md`
Expected: `All pages OK`, exit 0.

Run: `python scripts/check_pages.py --readability`
Expected: exit 1, last line `384 problem(s) found`. These counts were observed before the plan was
written; a different total means the file in Step 2 was not transcribed exactly.

- [ ] **Step 5: Prove each rule fires**

A rule that cannot fail is not a rule. Mutate the sample page with this script, run the checker,
then restore the page.

```bash
python - <<'PY'
p = "docs/wiki/fundamentals/how-aim-works.md"
t = open(p, encoding="utf-8").read()
t = t.replace("- **Speed costs accuracy.** The trade-off is measurable, not a matter of discipline.\n", "", 1)
t = t.replace("- **Smoothness is continuity.** One motion, not a chain of corrections.\n", "", 1)
t = t.replace("**Do this next.**", "**Next.**", 1)
t = t.replace("A shorter window means more misses.", "A shorter window means more misses, because every small correction you would have made during the time you no longer have simply never gets made at all, on any target.", 1)
t = t.replace("no matter how much you practice.", "no matter how much you practise.", 1)
open(p, "w", encoding="utf-8").write(t)
PY
```

Run: `python scripts/check_pages.py --readability docs/wiki/fundamentals/how-aim-works.md`
Expected: exit 1, and exactly these five problems plus the summary line:

```
wiki/fundamentals/how-aim-works.md: paragraph of 48 words (limit 45): "The speed-accuracy trade-off. Speeding up shortens the window your ..."
wiki/fundamentals/how-aim-works.md: sentence of 30 words (limit 25): "A shorter window means more misses, because every small correction ..."
wiki/fundamentals/how-aim-works.md: British spelling 'practise', the site writes US English
wiki/fundamentals/how-aim-works.md: opens with 2 bullets before its first heading, expected 3 to 5
wiki/fundamentals/how-aim-works.md: missing a '**Do this next.**' paragraph before Further resources
5 problem(s) found
```

Restore: `git checkout -- docs/wiki/fundamentals/how-aim-works.md`
Then run: `python scripts/check_pages.py --readability docs/wiki/fundamentals/how-aim-works.md`
Expected: `All pages OK`.

- [ ] **Step 6: Create `scripts/check_rewrite.py`**

```python
"""Check that rewriting a page changed its wording and nothing it depends on.

A rewrite restructures prose. It must not drop a link, a citation, or a heading another page links
to, and it must not touch front matter or the draft banner. Reading a diff by eye misses a link that
quietly fell out of a split sentence; this compares what the page points at, before and after.

Usage:
    python scripts/check_rewrite.py <git-ref> <page> [<page> ...]

<git-ref> is the commit to compare against, usually the one before the rewrite began.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)\)")
FOOTNOTE = re.compile(r"\[\^([^\]]+)\](?!:)")
HEADING = re.compile(r"^(#{2,3} .+)$", re.M)
FRONT_MATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
BANNER = '!!! warning "Draft"'


def invariants(text):
    front = FRONT_MATTER.match(text)
    return {
        "link target": set(LINK.findall(text)),
        "footnote reference": set(FOOTNOTE.findall(text)),
        "heading": set(HEADING.findall(text)),
        "front matter": {front.group(0)} if front else set(),
        "draft banner": {BANNER} if BANNER in text else set(),
    }


def compare(ref, page):
    rel = Path(page).resolve().relative_to(ROOT).as_posix()
    before = subprocess.run(
        ["git", "show", f"{ref}:{rel}"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    )
    if before.returncode != 0:
        return [f"{rel}: not found at {ref}"]
    after = (ROOT / rel).read_text(encoding="utf-8")
    old, new = invariants(before.stdout), invariants(after)
    errors = []
    for name in old:
        for item in sorted(old[name] - new[name]):
            errors.append(f"{rel}: {name} removed: {item.strip()}")
        for item in sorted(new[name] - old[name]):
            errors.append(f"{rel}: {name} added: {item.strip()}")
    return errors


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ref, pages = sys.argv[1], sys.argv[2:]
    errors = [error for page in pages for error in compare(ref, page)]
    for error in errors:
        print(error)
    print(f"{len(errors)} change(s) to invariants" if errors else "Invariants unchanged")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 7: Prove the gate passes a real rewrite and catches a real regression**

Run: `python scripts/check_rewrite.py 9e29fc2 docs/wiki/fundamentals/how-aim-works.md`
Expected: `Invariants unchanged`, exit 0. `9e29fc2` is the commit before the approved rewrite.

Then replay the regression the sample's first draft made:

```bash
python - <<'PY'
import re
p = "docs/wiki/fundamentals/how-aim-works.md"
t = open(p, encoding="utf-8").read()
t = re.sub(r"\n  See \[Myths\]\(\.\./myths\.md#arm-aiming-is-strictly-better-than-wrist-aiming\)\.", "", t)
t = t.replace("## Common mistakes", "## Mistakes", 1)
t = t.replace("[^fitts]", "", 1)
open(p, "w", encoding="utf-8").write(t)
PY
```

Run: `python scripts/check_rewrite.py 9e29fc2 docs/wiki/fundamentals/how-aim-works.md`
Expected: exit 1, and:

```
docs/wiki/fundamentals/how-aim-works.md: link target removed: ../myths.md#arm-aiming-is-strictly-better-than-wrist-aiming
docs/wiki/fundamentals/how-aim-works.md: footnote reference removed: fitts
docs/wiki/fundamentals/how-aim-works.md: heading removed: ## Common mistakes
docs/wiki/fundamentals/how-aim-works.md: heading added: ## Mistakes
4 change(s) to invariants
```

Restore: `git checkout -- docs/wiki/fundamentals/how-aim-works.md`

- [ ] **Step 8: Replace `templates/concept.md`**

```markdown
---
title: "Concept Name"
tags:
  - beginner
---

!!! warning "Draft"
    Written from public sources, pending review.

One short sentence on what this page covers.

- **The main idea.** One sentence. A reader who stops here still has the point.
- **The second idea.** Three to five of these, each a bold lead and a short sentence.
- **The third idea.** Write them last, from what the page below actually says.

## Explanation

**A bold lead-in.** One idea per paragraph: 45 words at most, 25 words per sentence. Cite each
fact with a footnote at the end of the sentence that makes it.[^source]

## Common mistakes

- Mistake, and why it hurts progress, in one sentence.

## How to train it

Concrete practice advice. Link to specific scenarios, playlists, or routines where possible.

**Do this next.** One concrete action a reader can take today, using a link this page already has.

## Further resources

- [Resource page title](../resources/communities/voltaic.md): one line on why it is relevant here.

[^source]: Publisher, [Page title](https://voltaic.gg)
```

- [ ] **Step 9: Update `CONTRIBUTING.md`**

Under `## Tags`, the Topic line currently omits `myth`, which the checker has allowed since the
Myths page shipped. Replace:

```markdown
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`
```

with:

```markdown
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`,
  `myth`
```

Insert this new section immediately before `## Topics are not part of the wiki`:

````markdown
## Readability

Most people reading this wiki skim, and many read with ADHD. A page has to work when it is read in
passes, so every page under `docs/wiki/` follows four rules:

1. **Paragraphs run 45 words at most.** One idea per paragraph. A bold lead-in counts toward the
   paragraph it opens.
2. **Sentences run 25 words at most**, in lists as well as prose.
3. **A concept page opens with its answer:** three to five bullets before its first `##` heading. A
   reader who stops there still has the point.
4. **A concept page ends on one next action:** a paragraph opening `**Do this next.**` before
   `## Further resources`, giving a reader who lost the thread somewhere to go.

Concept pages are those in `getting-started`, `fundamentals`, `categories`, `techniques`, and
`training`, other than `index.md`. [How Aim Works](docs/wiki/fundamentals/how-aim-works.md) shows
all four rules on a real page.

Write in US English, as the sources do: `practice` as a verb, `organize`, `behavior`. Footnote
definitions keep a source's own spelling, because they quote its title.

None of this means a casual voice. Keep the register plain and technical, and keep every fact.

When you restructure an existing page, do not rename a heading, add or remove a link or a footnote,
or touch the front matter. Other pages link to headings, and a link that falls out of a split
sentence is easy to miss in a diff. `scripts/check_rewrite.py` compares a page against an earlier
commit and reports anything of that kind:

```bash
python scripts/check_rewrite.py main docs/wiki/glossary.md
```
````

Under `## Check before you open a pull request`, replace the code block and the sentence after it:

````markdown
```bash
python scripts/check_pages.py
zensical build --clean
```

Both commands must finish without problems. The same checks run automatically on every pull request.
````

with:

````markdown
```bash
python scripts/check_pages.py
zensical build --clean
```

Both commands must finish without problems. The same checks run automatically on every pull request.

While existing pages are being brought up to the readability rules, check the pages you changed
against them by name: `python scripts/check_pages.py --readability docs/wiki/glossary.md`.
````

The interim sentence names pages because `--readability` on the whole site fails until Task 7 is
done; telling a contributor to run it bare would hand them hundreds of problems that are not theirs.

- [ ] **Step 10: Update `AGENTS.md`**

Replace the paragraph that begins "`scripts/check_pages.py` enforces three content rules" and ends
"do not rely on the exit code alone." with:

```markdown
`scripts/check_pages.py` enforces three content rules: every `tags:` value is on the allowed list,
each concept page carries a `## Further resources` section, and each resource page carries a
`## Related wiki pages` section. It also checks that every myth block's title matches a heading on
`docs/wiki/myths.md`. Pass `--drafts` to also require the draft banner on every page, and
`--readability` to also enforce the readability rules in [CONTRIBUTING.md](CONTRIBUTING.md#readability).
Name pages after the flags to check only those.
`zensical build` catches broken internal links and missing nav targets. The build no longer runs
with `--strict`, so link problems appear as warnings rather than failures — read the build output,
do not rely on the exit code alone.
```

In the numbered list under `## Rules that are easy to get wrong`, add after item 8:

```markdown
9. Every wiki page follows the readability rules in
   [CONTRIBUTING.md](CONTRIBUTING.md#readability): 45-word paragraphs, 25-word sentences, and on
   concept pages three to five answer bullets up top and a `**Do this next.**` paragraph at the end.
   Run `python scripts/check_pages.py --readability <page>` on any page you write or edit.
10. When restructuring an existing page, run `python scripts/check_rewrite.py <base> <page>` before
    committing, where `<base>` is the commit before you started. It must print
    `Invariants unchanged`. A rewrite that drops a link or renames a heading breaks pages that link
    to it, and the build does not always say so.
```

- [ ] **Step 11: Run the checks**

Run: `python scripts/check_pages.py`
Expected: `All pages OK`.

Run: `zensical build --clean`
Expected: `No issues found`.

- [ ] **Step 12: Commit**

Two commits: the scripts, then the template and documentation.

```bash
git add scripts/check_pages.py scripts/check_rewrite.py
git commit -m "test: add the readability rules and a rewrite gate

Most readers skim and many read with ADHD, so the checker gains four
rules behind --readability: 45-word paragraphs, 25-word sentences, and
on concept pages answer bullets up top and a next action at the end,
plus US spelling. They sit behind a flag until every page passes.

check_rewrite.py compares a page against an earlier commit and reports
any link, citation, heading, or front matter a rewrite lost. The sample
rewrite's first draft silently dropped two links; this catches that.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

```bash
git add templates/concept.md CONTRIBUTING.md AGENTS.md
git commit -m "docs: document the readability rules

The concept template now models them, CONTRIBUTING.md states them for
people, and AGENTS.md for agents. The Tags list also gains myth, which
the checker has allowed since the Myths page shipped but the docs never
listed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

### Task 2: Getting Started

**Files:**
- Modify: `docs/wiki/getting-started/index.md` (3 problems)
- Modify: `docs/wiki/getting-started/aim-trainers.md` (18 problems)
- Modify: `docs/wiki/getting-started/sensitivity.md` (22 problems)
- Modify: `docs/wiki/getting-started/setup.md` (21 problems)

**Interfaces:**
- Consumes: `scripts/check_pages.py --readability <page>` and `scripts/check_rewrite.py <ref> <page>`
  from Task 1.
- Produces: four pages passing both. Nothing later depends on their wording.

Problem counts are from `python scripts/check_pages.py --readability` before any rewrite.

- [ ] **Step 1: Rewrite `getting-started/index.md`** by the page rewrite procedure. Index page: rules
  1, 2 and spelling only; no answer bullets or next action required.
- [ ] **Step 2: Rewrite `getting-started/aim-trainers.md`** by the page rewrite procedure. Concept
  page: all four rules.
- [ ] **Step 3: Rewrite `getting-started/sensitivity.md`** by the page rewrite procedure. Concept
  page: all four rules. The page carries a `!!! myth` block under "When to change sensitivity, and
  when not to". The checker skips admonition bodies, so leave that block exactly as it is: its title
  must keep matching its heading on `myths.md`, and its body already follows the component's own
  rules. "Choosing a starting point" and "Converting sensitivity between games and trainers" are
  procedures; numbered steps suit them.
- [ ] **Step 4: Rewrite `getting-started/setup.md`** by the page rewrite procedure. Concept page: all
  four rules.
- [ ] **Step 5: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 3: Fundamentals

**Files:**
- Modify: `docs/wiki/fundamentals/index.md` (2 problems)
- Modify: `docs/wiki/fundamentals/practice-principles.md` (17 problems)
- Modify: `docs/wiki/fundamentals/transfer-to-games.md` (14 problems)

**Interfaces:**
- Consumes: both scripts from Task 1.
- Produces: three pages passing both.

`fundamentals/how-aim-works.md` is the approved sample and is not modified.

- [ ] **Step 1: Rewrite `fundamentals/index.md`** by the page rewrite procedure. Index page: rules 1,
  2 and spelling only.
- [ ] **Step 2: Rewrite `fundamentals/practice-principles.md`** by the page rewrite procedure. Concept
  page: all four rules. The page describes "five practice habits"; the answer bullets must not
  exceed five, so the natural fit is one bullet per habit only if there are exactly five and each
  fits in one short sentence — otherwise summarize them in three to five.
- [ ] **Step 3: Rewrite `fundamentals/transfer-to-games.md`** by the page rewrite procedure. Concept
  page: all four rules.
- [ ] **Step 4: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 4: Categories and Techniques

**Files:**
- Modify: `docs/wiki/categories/index.md` (1 problem)
- Modify: `docs/wiki/categories/clicking.md` (20 problems)
- Modify: `docs/wiki/categories/switching.md` (18 problems)
- Modify: `docs/wiki/categories/tracking.md` (21 problems)
- Modify: `docs/wiki/techniques/underaiming.md` (16 problems)

**Interfaces:**
- Consumes: both scripts from Task 1.
- Produces: five pages passing both.

`categories/index.md` links nine subsection anchors on the three category pages —
`#static-clicking`, `#dynamic-clicking`, `#linear-clicking`, `#precise-tracking`,
`#reactive-tracking`, `#control-tracking`, `#speed-switching`, `#evasive-switching`,
`#stability-switching`. Those headings must survive exactly; the rewrite gate enforces it.

- [ ] **Step 1: Rewrite `categories/index.md`** by the page rewrite procedure. Index page: rules 1, 2
  and spelling only. It may use `.aim-category` components; keep each component's markup exactly as
  it is, and keep one link per card item.
- [ ] **Step 2: Rewrite `categories/clicking.md`** by the page rewrite procedure. Concept page: all
  four rules. The page has no `## How to train it`; its `**Do this next.**` closes the last
  subsection before `## Further resources`.
- [ ] **Step 3: Rewrite `categories/switching.md`** by the page rewrite procedure. Concept page: all
  four rules, with the same placement note as Step 2.
- [ ] **Step 4: Rewrite `categories/tracking.md`** by the page rewrite procedure. Concept page: all
  four rules, with the same placement note as Step 2.
- [ ] **Step 5: Rewrite `techniques/underaiming.md`** by the page rewrite procedure. Concept page: all
  four rules. Fix `practised` to `practiced`. Keep the `<!-- REVIEW: ... -->` comment under
  `## How to train it` exactly as it is. It records that no public source gives drills for this
  technique, so the `**Do this next.**` paragraph states the principle — commit no more movement
  than the shot needs — and must not name a scenario, a drill, or a number. Keep Matty's quoted
  definition in its quotation marks.
- [ ] **Step 6: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 5: Training

**Files:**
- Modify: `docs/wiki/training/index.md` (4 problems)
- Modify: `docs/wiki/training/benchmarks.md` (19 problems)
- Modify: `docs/wiki/training/health.md` (19 problems)
- Modify: `docs/wiki/training/progress-and-plateaus.md` (22 problems)
- Modify: `docs/wiki/training/routines.md` (21 problems)

**Interfaces:**
- Consumes: both scripts from Task 1.
- Produces: five pages passing both.

- [ ] **Step 1: Rewrite `training/index.md`** by the page rewrite procedure. Index page: rules 1, 2
  and spelling only.
- [ ] **Step 2: Rewrite `training/benchmarks.md`** by the page rewrite procedure. Concept page: all
  four rules.
- [ ] **Step 3: Rewrite `training/health.md`** by the page rewrite procedure. Concept page: all four
  rules. This page gives health guidance: keep every hedge that carries medical meaning, such as a
  recommendation to see a professional. Shortening a sentence must never turn a cited "may" into an
  uncited "will".
- [ ] **Step 4: Rewrite `training/progress-and-plateaus.md`** by the page rewrite procedure. Concept
  page: all four rules. Its "Ways past a plateau" section is a single 192-word paragraph holding
  three bold lead-ins; each lead-in becomes its own paragraph or paragraphs. The third
  `## Common mistakes` bullet ends with a link to `../myths.md#a-plateau-means-you-have-hit-your-ceiling`;
  it stays.
- [ ] **Step 5: Rewrite `training/routines.md`** by the page rewrite procedure. Concept page: all four
  rules.
- [ ] **Step 6: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 6: Resources

**Files:**
- Modify: `docs/wiki/resources/index.md` (2 problems)
- Modify: `docs/wiki/resources/communities/jade-palace.md` (6 problems)
- Modify: `docs/wiki/resources/communities/revosect.md` (7 problems)
- Modify: `docs/wiki/resources/communities/voltaic.md` (9 problems)
- Modify: `docs/wiki/resources/tools/evxl.md` (4 problems)
- Modify: `docs/wiki/resources/tools/kova.md` (5 problems)
- Modify: `docs/wiki/resources/tools/kovobs.md` (4 problems)
- Modify: `docs/wiki/resources/trainers/aimbeast.md` (11 problems)
- Modify: `docs/wiki/resources/trainers/aimlabs.md` (7 problems)
- Modify: `docs/wiki/resources/trainers/kovaaks.md` (6 problems)

**Interfaces:**
- Consumes: both scripts from Task 1.
- Produces: ten pages passing both.

Resource pages are not concept pages: rules 1, 2 and spelling apply; answer bullets and a next
action do not. Keep each page's existing structure and its required `## Related wiki pages` section.
Many of these pages use a "Label: value" list, such as a "What it covers" list; a list item over 25
words becomes two sentences within the item, not two items.

- [ ] **Step 1: Rewrite `resources/index.md`** by the page rewrite procedure.
- [ ] **Step 2: Rewrite `resources/communities/jade-palace.md`** by the page rewrite procedure.
- [ ] **Step 3: Rewrite `resources/communities/revosect.md`** by the page rewrite procedure.
- [ ] **Step 4: Rewrite `resources/communities/voltaic.md`** by the page rewrite procedure.
- [ ] **Step 5: Rewrite `resources/tools/evxl.md`** by the page rewrite procedure.
- [ ] **Step 6: Rewrite `resources/tools/kova.md`** by the page rewrite procedure. Fix `practise` to
  `practice`.
- [ ] **Step 7: Rewrite `resources/tools/kovobs.md`** by the page rewrite procedure.
- [ ] **Step 8: Rewrite `resources/trainers/aimbeast.md`** by the page rewrite procedure. Fix
  `organised`, `practise`, and `practising` to US forms.
- [ ] **Step 9: Rewrite `resources/trainers/aimlabs.md`** by the page rewrite procedure.
- [ ] **Step 10: Rewrite `resources/trainers/kovaaks.md`** by the page rewrite procedure.
- [ ] **Step 11: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 7: Glossary, Myths, and the wiki index

**Files:**
- Modify: `docs/wiki/glossary.md` (26 problems)
- Modify: `docs/wiki/myths.md` (34 problems)
- Modify: `docs/wiki/index.md` (5 problems)

**Interfaces:**
- Consumes: both scripts from Task 1.
- Produces: three pages passing both. After this task every page under `docs/wiki/` passes
  `python scripts/check_pages.py --readability`, which Task 8 depends on.

None of these three is a concept page: rules 1, 2 and spelling apply.

- [ ] **Step 1: Rewrite `glossary.md`** by the page rewrite procedure. Every term is a `###` heading
  that other pages may link to; the gate keeps them. Each definition keeps its closing
  "See [Page](…)." link. Where a definition is two ideas — what the term is, then how it compares to
  another — it may become two short paragraphs under the same heading.
- [ ] **Step 2: Rewrite `myths.md`** by the page rewrite procedure. Fix `labour` to `labor`. Every
  `##` heading is a live anchor: myth blocks, Common mistakes bullets, and the myth-title check all
  depend on its exact text, so none may change. Each entry keeps its three bold leads in order —
  **The claim.**, **What sources say.**, **What to do instead.** — and a lead whose paragraph runs
  over 45 words is continued in further paragraphs after it, not given a new lead.
- [ ] **Step 3: Rewrite `wiki/index.md`** by the page rewrite procedure. The `## Sections` list is an
  `.aim-cards` grid: keep exactly one link per item, written as the item's title, and keep the
  `<div class="aim-cards" markdown>` wrapper and the blank lines around its content.
- [ ] **Step 4: Confirm the whole wiki passes**

Run: `python scripts/check_pages.py --readability`
Expected: `All pages OK`, exit 0. If any page fails, fix that page by the page rewrite procedure
before continuing.

- [ ] **Step 5: Run the whole-site checks** listed at the end of the page rewrite procedure.

---

### Task 8: Make the readability rules the default

**Files:**
- Modify: `scripts/check_pages.py` (docstring and `main`)
- Modify: `CONTRIBUTING.md` (the "Check before you open a pull request" section)
- Modify: `AGENTS.md` (the checker paragraph and list item 9)

**Interfaces:**
- Consumes: every page passing `--readability`, from Task 7.
- Produces: `python scripts/check_pages.py`, as CI runs it, enforcing the readability rules.

- [ ] **Step 1: Confirm the precondition**

Run: `python scripts/check_pages.py --readability`
Expected: `All pages OK`. If not, stop: Task 7 is incomplete.

- [ ] **Step 2: Change the docstring in `scripts/check_pages.py`**

Replace:

```python
Usage:
    python scripts/check_pages.py                  # tags and required sections
    python scripts/check_pages.py --drafts         # also require the draft banner
    python scripts/check_pages.py --readability    # also enforce the readability rules
    python scripts/check_pages.py --readability docs/wiki/glossary.md   # check named pages only
```

with:

```python
Usage:
    python scripts/check_pages.py                          # tags, sections, and readability
    python scripts/check_pages.py --drafts                 # also require the draft banner
    python scripts/check_pages.py docs/wiki/glossary.md    # check named pages only
```

- [ ] **Step 3: Change `main` in `scripts/check_pages.py`**

Four edits, which together remove the flag entirely rather than leaving it as a no-op.

Delete this line from `main`:

```python
    readable = "--readability" in args
```

In `main`, replace:

```python
    errors = [error for path in paths for error in check(path, drafts, headings, readable)]
```

with:

```python
    errors = [error for path in paths for error in check(path, drafts, headings)]
```

Change the signature of `check` from `def check(path, drafts, headings, readable):` to
`def check(path, drafts, headings):`.

In `check`, replace:

```python
        if readable:
            errors += readability(rel, text, section in CONCEPT_DIRS and not is_index)
```

with:

```python
        errors += readability(rel, text, section in CONCEPT_DIRS and not is_index)
```

- [ ] **Step 4: Confirm the default run now enforces the rules**

Run: `python scripts/check_pages.py`
Expected: `All pages OK`, exit 0.

Prove it enforces: run the mutation script from Task 1 Step 5 again, then run
`python scripts/check_pages.py docs/wiki/fundamentals/how-aim-works.md` — with no flag — and expect
the same five problems and `5 problem(s) found`. Restore with
`git checkout -- docs/wiki/fundamentals/how-aim-works.md` and confirm `All pages OK`.

- [ ] **Step 5: Update `CONTRIBUTING.md`**

Under `## Check before you open a pull request`, delete the interim paragraph Task 1 added, so the
section ends at "The same checks run automatically on every pull request.":

```markdown
While existing pages are being brought up to the readability rules, check the pages you changed
against them by name: `python scripts/check_pages.py --readability docs/wiki/glossary.md`.
```

- [ ] **Step 6: Update `AGENTS.md`**

In the checker paragraph, replace:

```markdown
`docs/wiki/myths.md`. Pass `--drafts` to also require the draft banner on every page, and
`--readability` to also enforce the readability rules in [CONTRIBUTING.md](CONTRIBUTING.md#readability).
Name pages after the flags to check only those.
```

with:

```markdown
`docs/wiki/myths.md`, and enforces the readability rules in
[CONTRIBUTING.md](CONTRIBUTING.md#readability). Pass `--drafts` to also require the draft banner on
every page. Name pages after the flags to check only those.
```

In list item 9, replace:

```markdown
   Run `python scripts/check_pages.py --readability <page>` on any page you write or edit.
```

with:

```markdown
   Run `python scripts/check_pages.py <page>` on any page you write or edit.
```

- [ ] **Step 7: Run the checks**

Run: `python scripts/check_pages.py`
Expected: `All pages OK`.

Run: `zensical build --clean`
Expected: `No issues found`.

- [ ] **Step 8: Commit**

```bash
git add scripts/check_pages.py CONTRIBUTING.md AGENTS.md
git commit -m "test: enforce the readability rules by default

Every wiki page now meets them, so they leave the --readability flag and
run on every check, which puts them in CI: a page that grows a 60-word
paragraph fails its pull request instead of waiting for the next pass.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"
```

---

## Self-review

**Spec coverage.** Rule 1, paragraph limit: Task 1 Step 2 `PARAGRAPH_LIMIT`, proven in Step 5.
Rule 2, sentence limit: `SENTENCE_LIMIT`, proven in Step 5. Rule 3, answer bullets: `ANSWER_BULLETS`,
proven in Step 5. Rule 4, next action on every concept page: `NEXT_ACTION`, proven in Step 5.
What the limits measure — skipped constructs, footnote and link stripping, sentence endings,
abbreviations and decimals: `prose_blocks`, `plain`, `SENTENCE_END`, `ABBREVIATION`, `DECIMAL`.
Spelling, footnotes exempt: `BRITISH` over prose with definitions removed, proven in Step 5; the
four named pages are fixed in Task 4 Step 5, Task 6 Steps 6 and 8, and Task 7 Step 2. Invariants —
links, footnotes, headings, front matter and banner: `check_rewrite.py`, proven in Task 1 Step 7 and
run on every page by the procedure. Rollout behind a flag, with page arguments: Task 1 Step 2.
Default at the end: Task 8. Template: Task 1 Step 8. `AGENTS.md` and `CONTRIBUTING.md`: Task 1
Steps 9 and 10, Task 8 Steps 5 and 6. All eight steps in the spec's order of work map to Tasks 1–8.
`how-aim-works.md` untouched and `tags.md` passing: Task 3 note, Task 1 Step 4. Out of scope, topic
pages: Global Constraints.

The one spec requirement given a tool it did not name — the rewrite gate — is recorded under
"Addition to the spec".

**Placeholders.** None in code or commands. The page tasks state rules, per-page hazards, and exact
checks rather than prose, because the prose is the deliverable; the approved sample is the model
and both scripts are the acceptance test.

**Name consistency.** `check(path, drafts, headings, readable)` in Task 1 becomes
`check(path, drafts, headings)` in Task 8, and Task 8 Step 3 changes both the definition and its
only call. `readability(rel, text, concept)` is unchanged by Task 8. The checker's messages quoted in
Task 1 Step 5 and Task 8 Step 4 are the same five lines. `check_rewrite.py` uses the singular
invariant names — `link target`, `footnote reference`, `heading` — in both its code and the expected
output in Task 1 Step 7.
