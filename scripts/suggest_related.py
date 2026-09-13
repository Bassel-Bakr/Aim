"""Suggest related pages a wiki page does not list yet.

Usage:
    python scripts/suggest_related.py                                # every concept and resource page
    python scripts/suggest_related.py docs/wiki/training/routines.md # named pages only

For each page it prints front matter entries ready to paste under `related:`, strongest first, each
with a placeholder reason and a comment saying why it was suggested:

    - links here: the other page lists this one, so the build already shows a bare link back.
    - linked in text: this page links to it in its own text.
    - shares tags: both pages carry the same tags. One shared tag alone is too common to suggest a
      page, so a page suggested for its tags alone shares at least two.

A concept page is only offered concept pages, since it points to resource pages under Resources. A
resource page is offered both. Replace each TODO with a reason, or drop the entry; the checker
rejects a TODO left in place.
"""
import posixpath
import re
import sys
from pathlib import Path

from aim_related import PLACEHOLDER, front_matter, kind, links_back, listed, related_lists

DOCS = Path(__file__).resolve().parent.parent / "docs"
PAGE_LINK = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")
BODY = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n|<!--.*?-->|```.*?```", re.S)


def candidates(page, pages, lists):
    """(target, reasons) pairs for one page, strongest first."""
    text = pages[page]
    meta = front_matter(text)
    tags = set(meta.get("tags") or [])
    taken = set(listed(meta)) | {page}
    allowed = {"concept"} if kind(page) == "concept" else {"concept", "resource"}
    found = {}

    def add(target, reason):
        if target in pages and target not in taken and kind(target) in allowed:
            found.setdefault(target, []).append(reason)

    for source in links_back(lists, page):
        add(source, "links here")
    for href in PAGE_LINK.findall(BODY.sub("", text)):
        target = posixpath.normpath(posixpath.join(posixpath.dirname(page), href))
        if "linked in text" not in found.get(target, []):
            add(target, "linked in text")
    for target, other in pages.items():
        shared = sorted(tags & set(front_matter(other).get("tags") or []))
        if len(shared) >= 2 or (shared and target in found):
            add(target, "shares tags: " + ", ".join(shared))
    return sorted(found.items(), key=lambda item: (-len(item[1]), item[0]))


def main():
    pages = {path.relative_to(DOCS).as_posix(): path.read_text(encoding="utf-8") for path in sorted(DOCS.rglob("*.md"))}
    lists = related_lists(DOCS)
    named = [Path(arg).resolve().relative_to(DOCS).as_posix() for arg in sys.argv[1:]]
    for page in named or [page for page in pages if kind(page) and not page.endswith("/index.md")]:
        found = candidates(page, pages, lists)
        if not found:
            continue
        print(page)
        for target, reasons in found:
            print(f"  - page: {target}")
            print(f"    why: {PLACEHOLDER}  # {'; '.join(reasons)}")
        print()


if __name__ == "__main__":
    main()
