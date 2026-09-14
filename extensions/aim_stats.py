"""Site statistics for the Aim wiki's landing page.

The landing page carries the marker line <!-- aim:stats -->, which this extension replaces with a
row of counts, so the numbers follow the content instead of going stale. Each count links to the
page it counts:

- Wiki pages: pages under wiki/, not counting section index pages or the generated Tags and
  References pages. Links to the wiki home.
- Sources cited: entries in the reference registry. Links to the References page.
- Guides: entries on the Guides page, one per list item that opens with a link. Links to Guides.

The row is a list of links styled by .aim-stats in aim.css. The extension writes raw HTML, which
the Markdown link rewriting never sees, so it builds each href itself, relative to the page and in
the site's URL style. A count whose target page is missing is written without a link.

Like the Related section, a live preview only re-renders the page you edited, so run
zensical build --clean to refresh the counts.

Configured in zensical.toml:

    [project.markdown_extensions.aim_stats]
    registry = "references.yml"
"""
import os
import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from aim_references import REFERENCES_PAGE, load_registry

STATS_MARKER = "<!-- aim:stats -->"
WIKI_HOME = "wiki/index.md"
GUIDES_PAGE = "wiki/resources/guides.md"
GENERATED_PAGES = {"wiki/tags.md", REFERENCES_PAGE}
GUIDE_ENTRY = re.compile(r"^- \[", re.M)


def wiki_pages(docs_dir):
    """Docs-relative paths of the wiki's own pages: no section index pages, no generated pages."""
    pages = []
    for root, _dirs, files in os.walk(os.path.join(docs_dir, "wiki")):
        for name in files:
            page = os.path.relpath(os.path.join(root, name), docs_dir).replace("\\", "/")
            if name.endswith(".md") and name != "index.md" and page not in GENERATED_PAGES:
                pages.append(page)
    return pages


def stats(docs_dir, registry_path):
    """(label, count, docs-relative page the count links to), in display order."""
    with open(os.path.join(docs_dir, GUIDES_PAGE), encoding="utf-8") as handle:
        guides = len(GUIDE_ENTRY.findall(handle.read()))
    return [
        ("Wiki pages", len(wiki_pages(docs_dir)), WIKI_HOME),
        ("Sources cited", len(load_registry(registry_path)), REFERENCES_PAGE),
        ("Guides", guides, GUIDES_PAGE),
    ]


def page_url(target, here, directory_urls):
    """The href from docs-relative page `here` to docs-relative page `target`."""
    def url(page):
        stem = page[: -len(".md")]
        if not directory_urls:
            return stem + ".html"
        if stem == "index" or stem.endswith("/index"):
            return stem[: -len("index")]
        return stem + "/"

    base, dest = url(here), url(target)
    base_dir = (base if base.endswith("/") or not base else os.path.dirname(base) + "/").rstrip("/")
    href = os.path.relpath(dest.rstrip("/") or ".", base_dir or ".").replace("\\", "/")
    # A directory URL keeps its trailing slash, or the browser resolves the next link one level up.
    return href + "/" if directory_urls and not href.endswith("/") else href


class StatsPreprocessor(Preprocessor):
    def __init__(self, md, registry_path):
        super().__init__(md)
        self.registry_path = registry_path

    def run(self, lines):
        if STATS_MARKER not in (line.strip() for line in lines):
            return lines
        from zensical.extensions.context import ContextPreprocessor

        context = ContextPreprocessor.from_markdown(self.md)
        if context is None:
            return lines
        docs_dir = context.config["docs_dir"]
        here = context.page.path.replace("\\", "/")
        directory_urls = context.config.get("use_directory_urls", True)
        items = []
        for label, count, target in stats(docs_dir, self.registry_path):
            inner = (f'<span class="aim-stats__count">{count}</span> '
                     f'<span class="aim-stats__label">{label}</span>')
            if os.path.isfile(os.path.join(docs_dir, target)):
                inner = f'<a href="{page_url(target, here, directory_urls)}">{inner}</a>'
            items.append(f"<li>{inner}</li>")
        row = ["", f'<ul class="aim-stats">{"".join(items)}</ul>', ""]
        return [out for line in lines for out in (row if line.strip() == STATS_MARKER else [line])]


class StatsExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {"registry": ["references.yml", "Path to the reference registry, from the project root."]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(StatsPreprocessor(md, self.getConfig("registry")), "aim_stats", 27)


def makeExtension(**kwargs):
    return StatsExtension(**kwargs)
