"""Related pages for the Aim wiki, listed under a "Related" heading.

A wiki page lists the pages it connects to in its front matter, each with a reason:

    related:
      - page: wiki/training/routines.md
        why: turning these habits into a session plan.

Paths are relative to docs/. This extension writes the "Related" section from that list: the
heading, then one bullet per page, linked with the target page's title and a path relative to the
page being rendered. The section goes directly above "## Resources", or at the end of the page when
there is no Resources section; the references extension appends References after it.

Links between two pages of the same kind run both ways. When a concept page lists another concept
page, or a resource page lists another resource page, and that page does not list it back, the
section on that page gains a link back with no reason, after its own entries. Writing a reason for
it in that page's front matter replaces the bare link. Links across the two kinds stay one-way:
concept pages point to resources under Resources only where they are worth a look. Pages without a
related list of their own, such as the Glossary and section index pages, gain no links back.

scripts/check_pages.py and scripts/suggest_related.py import the helpers here, so the rules live in
one place.

Configured in zensical.toml:

    [project.markdown_extensions.aim_related]
"""
import os
import re

import yaml
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

FRONT_MATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
TITLE_HEADING = re.compile(r"^# (.+)$", re.M)
CONCEPT_DIRS = {"getting-started", "fundamentals", "categories", "techniques", "training"}
# What a suggested entry carries until someone writes its reason; the checker rejects it.
PLACEHOLDER = "TODO"


def front_matter(text):
    match = FRONT_MATTER.match(text)
    return (yaml.safe_load(match.group(1)) or {}) if match else {}


def kind(page):
    """'concept' or 'resource' for a docs-relative wiki page in those sections, else None."""
    parts = page.split("/")
    if len(parts) < 3 or parts[0] != "wiki":
        return None
    return "concept" if parts[1] in CONCEPT_DIRS else "resource" if parts[1] == "resources" else None


def listed(meta):
    """The pages a page's front matter lists as related, in order."""
    related = meta.get("related")
    if not isinstance(related, list):
        return []
    return [entry["page"] for entry in related if isinstance(entry, dict) and isinstance(entry.get("page"), str)]


def related_lists(docs_dir):
    """Every docs-relative page that carries a related list, mapped to the pages it lists."""
    lists = {}
    for root, _, files in os.walk(docs_dir):
        for name in files:
            if name.endswith(".md"):
                path = os.path.join(root, name)
                page = os.path.relpath(path, docs_dir).replace("\\", "/")
                meta = front_matter(open(path, encoding="utf-8").read())
                if isinstance(meta.get("related"), list):
                    lists[page] = listed(meta)
    return lists


def links_back(lists, page):
    """Pages of the same kind that list this page when it does not list them."""
    if page not in lists or kind(page) is None:
        return []
    return sorted(source for source, pages in lists.items()
                  if page in pages and source not in lists[page] and kind(source) == kind(page))


def page_title(docs_dir, page):
    """The title a page shows: its front matter title, else its first heading, else its file name."""
    text = open(os.path.join(docs_dir, page), encoding="utf-8").read()
    title = front_matter(text).get("title")
    if title:
        return title
    heading = TITLE_HEADING.search(text)
    return heading.group(1).strip() if heading else os.path.splitext(os.path.basename(page))[0]


class RelatedPreprocessor(Preprocessor):
    def run(self, lines):
        # Imported here so the checker and the suggestion script can use this module without
        # Zensical's rendering machinery.
        from zensical.extensions.context import ContextPreprocessor

        context = ContextPreprocessor.from_markdown(self.md)
        if context is None:
            return lines
        page = context.page.path.replace("\\", "/")
        docs_dir = context.config["docs_dir"]
        related = context.page.meta.get("related")
        if not related:
            return lines
        here = os.path.dirname(page) or "."

        def link(target):
            href = os.path.relpath(target, here).replace("\\", "/")
            return f"[{page_title(docs_dir, target)}]({href})"

        section = ["## Related", ""]
        for entry in related:
            if not os.path.isfile(os.path.join(docs_dir, entry["page"])):
                section.append(f"- **Unknown page {entry['page']}.**")
                continue
            section.append(f"- {link(entry['page'])}: {entry['why']}")
        section += [f"- {link(source)}" for source in links_back(related_lists(docs_dir), page)]
        section.append("")
        fenced = False
        for index, line in enumerate(lines):
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
            if not fenced and line.rstrip() == "## Resources":
                return lines[:index] + section + lines[index:]
        return lines + [""] + section


class RelatedExtension(Extension):
    def extendMarkdown(self, md):
        # Runs before the references extension (priority 25), so References still lands last.
        md.preprocessors.register(RelatedPreprocessor(md), "aim_related", 26)


def makeExtension(**kwargs):
    return RelatedExtension(**kwargs)
