# Contributing to Aim Wiki

Thank you for helping. This guide explains how to add or change wiki pages.

It covers the wiki at `/wiki` only. [Articles](#articles-are-not-part-of-the-wiki) at `/articles` are
signed, authored pages and are not open to contributions.

## Ways to contribute

- Fix a mistake: click the edit button (pencil icon) on any wiki page. GitHub opens the file so you
  can propose a change.
- Add a page or a large change: open an issue first, so we can agree on scope.

## Run the site locally

Follow the steps in [README.md](README.md#run-the-site-locally).

## Add a page

1. Copy a template from `templates/`:
   - `concept.md` for pages that explain aim concepts or training advice.
   - `resource.md` for pages about a community, a trainer, or a tool.

   `templates/article.md` is not a wiki template; see
   [Articles are not part of the wiki](#articles-are-not-part-of-the-wiki).
2. Save the file in the matching folder under `docs/wiki/`. (`docs/index.md` is the site's landing page, not a wiki page.)
3. Add the page to the `nav` list in `zensical.toml`.
4. Link the new page from at least one related page.

Page titles come from the `title:` field in the front matter. Do not add a `#` heading in the page
body.

## Writing rules

1. Write in your own words and link to the original source. Do not copy guides, tables, or images
   from other sites.

   Keeping a source's sentence and swapping a few words is still copying, and it is the easy
   mistake to make, because the result reads as though you wrote it. Work out what the source
   claims, then say that from scratch. Where the exact wording is the point, such as a term whose
   definition is disputed, quote it in quotation marks and attribute it:

   ```markdown
   Matty defines it as a deliberate choice to "withhold extra motion on a target."[^matty]
   ```
2. Cite facts with a footnote. Put a `[^label]` marker at the end of the sentence, and define the
   source at the bottom of the file:

   ```markdown
   Fingers make small adjustments and the arm drives large turns.[^wrist-vs-arm]

   [^wrist-vs-arm]: Aimlabs, [Wrist aiming vs arm aiming: why not both?](https://aimlabs.com/articles/aimlabs/wrist-aiming-vs-arm-aiming-why-not-both/)
   ```

   Reuse the same label whenever you cite that source again on the page; it renders as one numbered
   entry with a link back to each use. Use descriptive labels (`wrist-vs-arm`), not numbers, so
   citations never need renumbering. Footnotes are numbered in the order their definitions appear,
   so keep the definition list in order of first use. Name the publisher first in the definition,
   then link the page title.

   Two exceptions stay in the prose rather than becoming footnotes: links to other wiki pages,
   which are navigation rather than citation, and cases where the source's identity is part of the
   claim, such as whose benchmark a rank belongs to.
3. Pages written from research but not yet fact-checked keep this banner at the top:

   ```markdown
   !!! warning "Draft"
       Written from public sources, pending review.
   ```

4. If you cannot verify a claim from a public source, leave it out, or mark it with
   `<!-- REVIEW: what needs checking -->`. HTML comments are hidden on the page but still visible
   in the page source.

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

## Articles are not part of the wiki

Articles live at `/articles`, outside `docs/wiki/`, because they run on a different trust model. A
wiki page earns trust by citing a public source for each claim, and anyone may correct it. An
article earns trust by carrying its author's name, and is not open to contributions. Keeping them in
separate trees means neither set of rules needs an exception clause for the other.

Nothing in this document applies to articles. They are written by the site's maintainer from
`templates/article.md`, carry a `!!! info "Written by <name>"` byline instead of the draft banner,
take no tags, and do not require footnotes. `scripts/check_pages.py` enforces those rules for
anything under `docs/articles/`.

To suggest an article, or a correction to one, open an issue rather than a pull request.

## The Links page

`docs/links.md` catalogues individual guides, articles, and videos, grouped by what
they help with. It works differently from the rest of the wiki in two ways.

The entry is the citation. A line there names the piece, its publisher, and its year where the
source states one, so it takes no footnote; adding one would double every line.

A link earns its place by teaching something: a method, a mechanism, or a mistake. A benchmark
announcement, a score sheet, or a routine handed over without an explanation of how to play it is
not educational content and belongs on the relevant resource page instead. Prefer a primary source
over a re-upload, never add a mirror of someone else's document, and keep an entry only while it
still resolves. Write the one-line description in your own words, as the rest of the wiki requires.

## Tags

Use only these tags in the `tags:` front matter field:

- Type (resource pages only): `community`, `trainer`, `tool`
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`,
  `myth`

To propose a new tag, open an issue.

## Glossary

Add new terms to `docs/wiki/glossary.md`. If the term is an abbreviation, also add it to
`includes/abbreviations.md`, so the site shows its meaning as a tooltip on every page.

## Check before you open a pull request

```bash
python scripts/check_pages.py
zensical build --clean
```

Both commands must finish without problems. The same checks run automatically on every pull request.

## License

By contributing, you agree that your contribution is licensed under
[CC BY-SA 4.0](LICENSE).
