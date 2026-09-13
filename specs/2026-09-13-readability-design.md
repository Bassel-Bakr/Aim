# Readability pass — Design

Date: 2026-09-13
Status: Approved in conversation, pending spec review
Maintenance: kept in step with the repository. Changes made after approval are marked inline with
the date they landed, rather than rewritten silently.

## Goal

Every wiki page can be read in passes. A reader who skims, loses focus, or stops early still leaves
with the point, because the page leads with its answer, gives each idea its own short paragraph,
and never asks anyone to hold a 40-word sentence in their head. The site's readers are mostly
young, and many read with ADHD; the pass is written for how they read, not for a younger
vocabulary.

## Non-goals

- Slang, a casual voice, or any change of register. Pages stay plain and technical, the register
  the community's own guides use.
- Adding or removing facts. The pass restructures what a page says; it never changes what it
  claims.
- Changing citations, links, or headings. See Invariants.
- Pages outside `docs/wiki/`. Topics are signed, first-person pages under their author's control,
  and the landing page already reads short.
- A reading-level score such as Flesch–Kincaid. Those grade syllable counts; the problem measured
  on this site is sentence and paragraph length, so those are what the rules measure.

## Evidence

Measured on 2026-09-13 across the 32 wiki pages, with the tokenizer the checker will use:

- 30 of 32 pages break a 45-word paragraph or 25-word sentence limit.
- The longest paragraph runs 192 words; the longest sentence runs 65.
- `fundamentals/how-aim-works.md` was rewritten to these rules as a sample and approved on
  2026-09-13. It went from paragraphs averaging 94 words and 14 sentences over 25 words to a
  40-word longest paragraph, a 23-word longest sentence, and the same five citations and fourteen
  links.

## Rules

Four rules, all enforced by `scripts/check_pages.py`, on every page under `docs/wiki/`.

**1. Paragraphs run 45 words at most.** One idea per paragraph. A bold lead-in such as
`**Smoothness.**` counts toward the paragraph it opens.

**2. Sentences run 25 words at most.** This applies to list items as well as prose.

**3. A concept page opens with its answer.** A page in `getting-started`, `fundamentals`,
`categories`, `techniques`, or `training`, other than an `index.md`, carries a bullet list of 3 to
5 items before its first `##` heading. One short intro paragraph may come before the list. A reader
who stops at the list still has the page's point.

**4. A training section ends on one next action.** A page with a `## How to train it` section ends
that section with a paragraph opening `**Do this next.**`: a single concrete thing to do, for a
reader who has lost the thread and needs somewhere to go.

### What the limits measure

Rules 1 and 2 read prose paragraphs and list items. They skip headings, tables, footnote
definitions, admonition bodies, HTML blocks, code, and front matter. Before counting, footnote
references are removed and links are reduced to their text. A sentence ends at `.`, `!`, `?`, `:`
or `;` followed by a capital letter or digit, so a colon introducing a clause starts a new sentence
and a colon introducing a lowercase list does not. Abbreviations such as `e.g.` and `vs.`, and
decimals such as `0.27`, do not end a sentence.

This was checked by hand against the longest flagged sentences on `glossary.md`,
`resources/tools/kova.md`, and `index.md`: every one was a genuine long sentence, none a tokenizer
artifact.

### Why these numbers

45 and 25 are the tightest limits the approved sample passes with margin. They are limits, not
targets; most sentences on the sample run near 13 words.

## Spelling

The site standardizes on US spelling, matching its sources — Aimlabs, KovaaK's, Voltaic,
Revosect and ProSettings all publish in US English. As of 2026-09-13 the wiki mixes the two:
`practise`, `practised`, `practising`, `organised` and `labour` appear on four pages — `myths.md`,
`resources/tools/kova.md`, `resources/trainers/aimbeast.md` and `techniques/underaiming.md`. The
pass corrects them page by page, and the checker rejects a short list of British forms in wiki
prose so the mix does not return. Footnote definitions are exempt, because they quote source
titles.

## Invariants

A rewrite changes structure and wording only. For every page it touches:

- **The set of link targets is unchanged.** On 2026-09-13 the sample rewrite silently dropped two
  hub links that an earlier review had added; only a before-and-after comparison of the link set
  caught it. Every page is gated on that comparison.
- **The set of footnote references is unchanged**, and each reference stays attached to the claim
  it supports.
- **No `##` or `###` heading is renamed.** Headings are anchors. `categories/index.md` links nine
  subsection anchors on the three category pages, and `myths.md` headings are anchor targets for
  myth blocks and Common mistakes bullets, besides being what the existing myth-title check
  compares against.
- **Front matter, the draft banner, and required sections are unchanged.**

## Rollout

The rules land in the checker before the pages comply, behind a `--readability` flag, following
the existing `--drafts` precedent. That lets each rewrite be checked while CI, which runs the
checker without flags, stays green on untouched pages. The checker also accepts page paths, so a
rewrite can be checked on its own.

When every page passes, the flag's rules become the default and CI enforces them from then on.

## Documentation

`templates/concept.md` is rewritten to model the rules: an answer-first bullet list in place of the
summary paragraph, and a `**Do this next.**` line in `## How to train it`. `AGENTS.md` and
`CONTRIBUTING.md` describe the four rules, the spelling rule, and the invariants, because both
currently describe the checker as enforcing three rules and would otherwise go stale.

## Order of work

1. Checker, template, and documentation, with the rules behind `--readability`.
2. `getting-started/`: `index.md`, `aim-trainers.md`, `sensitivity.md`, `setup.md`.
3. `fundamentals/`: `index.md`, `practice-principles.md`, `transfer-to-games.md`.
4. `categories/` and `techniques/`: `index.md`, `clicking.md`, `switching.md`, `tracking.md`,
   `underaiming.md`.
5. `training/`: `index.md`, `benchmarks.md`, `health.md`, `progress-and-plateaus.md`,
   `routines.md`.
6. `resources/`: `index.md` and the nine community, tool and trainer pages.
7. `glossary.md`, `myths.md`, and `wiki/index.md`.
8. Make the readability rules the default.

`fundamentals/how-aim-works.md` is already done. `tags.md` is generated and passes as it stands.
