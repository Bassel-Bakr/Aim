"""Related pages for the Aim wiki, listed under a "Related" heading.

A wiki page lists the pages it connects to in its front matter, each with a reason:

    related:
      - page: wiki/training/routines.md
        why: turning these habits into a session plan.

Paths are relative to docs/. This extension writes the "Related" section from that list: the
heading, then one bullet per page, linked with the target page's title and a path relative to the
page being rendered. The section goes directly above "## Resources", or at the end of the page when
there is no Resources section; the references extension appends References after it.

Configured in zensical.toml:

    [project.markdown_extensions.aim_related]
"""
import os
import re

import yaml
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from zensical.extensions.context import ContextPreprocessor

FRONT_MATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.S)
TITLE_HEADING = re.compile(r"^# (.+)$", re.M)


def page_title(docs_dir, page):
    """The title a page shows: its front matter title, else its first heading, else its file name."""
    text = open(os.path.join(docs_dir, page), encoding="utf-8").read()
    match = FRONT_MATTER.match(text)
    meta = (yaml.safe_load(match.group(1)) or {}) if match else {}
    if meta.get("title"):
        return meta["title"]
    heading = TITLE_HEADING.search(text)
    return heading.group(1).strip() if heading else os.path.splitext(os.path.basename(page))[0]


class RelatedPreprocessor(Preprocessor):
    def __init__(self, md):
        super().__init__(md)
        self._titles = {}

    def title(self, docs_dir, page):
        if page not in self._titles:
            self._titles[page] = page_title(docs_dir, page)
        return self._titles[page]

    def run(self, lines):
        context = ContextPreprocessor.from_markdown(self.md)
        related = context.page.meta.get("related") if context else None
        if not related:
            return lines
        docs_dir = context.config["docs_dir"]
        here = os.path.dirname(context.page.path.replace("\\", "/")) or "."
        section = ["## Related", ""]
        for entry in related:
            page = entry["page"]
            if not os.path.isfile(os.path.join(docs_dir, page)):
                section.append(f"- **Unknown page {page}.**")
                continue
            link = os.path.relpath(page, here).replace("\\", "/")
            section.append(f"- [{self.title(docs_dir, page)}]({link}): {entry['why']}")
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
