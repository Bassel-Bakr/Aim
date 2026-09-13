"""Centralized references for the Aim wiki.

Sources live once, in references.yml, each under a stable ID such as REF-012. A wiki page cites one
with an ordinary footnote marker, [^REF-012], and never defines it: this extension appends the
definition for every REF ID the page cites, built from the registry, so the theme renders it as a
normal footnote. It appends only the IDs the page actually cites, because Python-Markdown lists every
defined footnote whether or not the page refers to it.

Footnotes that are not sources, such as a clarifying aside, keep working as before: give them any
label that is not a REF ID and define them on the page.

The References page carries the marker line <!-- aim:references -->, which this extension replaces
with the whole registry, sorted by author and grouped by first letter.

Configured in zensical.toml:

    [project.markdown_extensions.aim_references]
    registry = "references.yml"
"""
import os
import re
import sys

import yaml
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

CITATION = re.compile(r"\[\^(REF-\d{3})\](?!:)")
REFERENCES_MARKER = "<!-- aim:references -->"
REFERENCES_PAGE = "wiki/references.md"
TYPE_LABELS = {
    "article": "Article",
    "document": "Document",
    "documentation": "Documentation",
    "encyclopedia": "Encyclopedia",
    "post": "Post",
    "repository": "Repository",
    "study": "Study",
    "video": "Video",
    "website": "Website",
}


def load_registry(path):
    with open(path, encoding="utf-8") as handle:
        entries = yaml.safe_load(handle) or []
    return {entry["id"]: entry for entry in entries}


def anchor(ref_id):
    return ref_id.lower()


def sort_key(entry):
    return (entry["author"].casefold(), entry["title"].casefold())


def current_page():
    """The docs-relative path of the page being rendered, or None.

    Python-Markdown does not tell extensions which page they are rendering. Zensical's renderer holds
    it in a local named `path` a few frames up; reading it lets a footnote link to its entry on the
    References page with a correct relative path. If a future Zensical renames that local, the
    footnote still renders, just without that link.
    """
    frame = sys._getframe(1)
    while frame is not None:
        path = frame.f_locals.get("path")
        if frame.f_code.co_name == "render" and isinstance(path, str) and path.endswith(".md"):
            return path.replace("\\", "/")
        frame = frame.f_back
    return None


def source_text(entry):
    text = f"{entry['author']}, [{entry['title']}]({entry['url']})"
    if entry.get("publication"):
        text += f", {entry['publication']}"
    return text


class ReferencesPreprocessor(Preprocessor):
    def __init__(self, md, registry_path):
        super().__init__(md)
        self.registry_path = registry_path
        self._registry = None

    @property
    def registry(self):
        if self._registry is None:
            self._registry = load_registry(self.registry_path)
        return self._registry

    def run(self, lines):
        if REFERENCES_MARKER in (line.strip() for line in lines):
            lines = [out for line in lines for out in (self.bibliography() if line.strip() == REFERENCES_MARKER else [line])]
        cited = []
        fenced = False
        for line in lines:
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
            if not fenced:
                cited += [ref_id for ref_id in CITATION.findall(line) if ref_id not in cited]
        if not cited:
            return lines
        page = current_page()
        link_base = None
        if page:
            link_base = os.path.relpath(REFERENCES_PAGE, os.path.dirname(page) or ".").replace("\\", "/")
        definitions = [""]
        for ref_id in cited:
            entry = self.registry.get(ref_id)
            if entry is None:
                definitions.append(f"[^{ref_id}]: **Unknown reference {ref_id}.**")
                continue
            text = source_text(entry)
            if link_base and page != REFERENCES_PAGE:
                text += f" · [{ref_id}]({link_base}#{anchor(ref_id)})"
            definitions.append(f"[^{ref_id}]: {text}")
        return lines + definitions

    def bibliography(self):
        out = []
        letter = None
        for entry in sorted(self.registry.values(), key=sort_key):
            initial = entry["author"][0].upper()
            # A lone "#" would read as an empty Markdown heading, so digits and symbols group as 0–9.
            initial = initial if initial.isalpha() else "0–9"
            if initial != letter:
                letter = initial
                out += ["", f"## {letter}", ""]
            details = [f"`{entry['id']}`", TYPE_LABELS[entry["type"]]]
            if entry.get("publication"):
                details.append(entry["publication"])
            line = (f'- <span id="{anchor(entry["id"])}"></span>**{entry["author"]}**, '
                    f"[{entry['title']}]({entry['url']}) · " + " · ".join(details))
            if entry.get("notes"):
                line += f"  \n  {entry['notes']}"
            out.append(line)
        return out + [""]


class ReferencesExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {"registry": ["references.yml", "Path to the reference registry, from the project root."]}
        super().__init__(**kwargs)

    def extendMarkdown(self, md):
        md.preprocessors.register(ReferencesPreprocessor(md, self.getConfig("registry")), "aim_references", 25)


def makeExtension(**kwargs):
    return ReferencesExtension(**kwargs)
