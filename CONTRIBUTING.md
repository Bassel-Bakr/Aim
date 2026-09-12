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
   - `resource.md` for pages about a community, a trainer, or a tool.
   - `guide.md` for a signed, first-person guide. See [Guides](#guides) first.
2. Save the file in the matching folder under `docs/wiki/`. (`docs/index.md` is the site's landing page, not a wiki page.)
3. Add the page to the `nav` list in `mkdocs.yml`.
4. Link the new page from at least one related page.

Page titles come from the `title:` field in the front matter. Do not add a `#` heading in the page
body.

## Writing rules

1. Write in your own words and link to the original source. Do not copy guides, tables, or images
   from other sites.
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

## Guides

Pages under `docs/wiki/guides/` run on a different trust model from the rest of the wiki. A
reference page earns trust by citing a public source for each claim. A guide earns it by carrying
its author's name: the reader decides whether to trust the method by deciding whether to trust the
person. Both are honest; they are just not the same thing, and a reader has to be able to tell
which one they are reading.

So a guide follows different rules:

- It carries a byline admonition at the top instead of the draft banner, and
  `scripts/check_pages.py` enforces this:

  ```markdown
  !!! info "Written by Bassel Bakr"
      A practical guide from my own training and experience, not a summary of published sources.
      Treat it as one informed opinion rather than settled fact.
  ```

- First person is expected. A guide says what its author does and why, so write "I" rather than
  hedging into the passive voice.
- Footnotes are welcome but not required. Cite a source where one exists; do not manufacture
  citations for a judgment call, and do not leave out a useful method because no article backs it.
- Writing rules 1 and 3 still apply in full. A guide is your own words and your own experience;
  being signed does not license summarizing someone else's video or guide closely.

Guides are written by this wiki's maintainer for now. Authorship is not open to contributors yet,
so open an issue rather than a pull request that adds one. Corrections to a published guide, such
as a factual error, a dead link, or a typo, are welcome from anyone; changes to the method or the
argument go to the author, because the byline has to keep meaning what it says.

## Tags

Use only these tags in the `tags:` front matter field:

- Type (resource pages only): `community`, `trainer`, `tool`
- Topic: `clicking`, `tracking`, `switching`, `benchmarks`, `routines`, `sensitivity`, `beginner`

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
