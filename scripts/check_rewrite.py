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
