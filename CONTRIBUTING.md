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
   - `resource.md` for pages about a community or a trainer.
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

- Type (resource pages only): `community`, `trainer`
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
