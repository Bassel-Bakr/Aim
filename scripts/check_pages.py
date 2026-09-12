"""Check wiki pages against the rules in CONTRIBUTING.md.

Usage:
    python scripts/check_pages.py           # tags and required sections
    python scripts/check_pages.py --drafts  # also require the draft banner
"""
import re
import sys
from pathlib import Path

import yaml

DOCS = Path(__file__).resolve().parent.parent / "docs"
WIKI = DOCS / "wiki"
EXEMPT_FROM_BANNER = {"index.md", "wiki/tags.md"}
ALLOWED_TAGS = {
    "community", "trainer", "tool",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
}
CONCEPT_DIRS = {"getting-started", "fundamentals", "skills", "techniques", "training"}
BANNER = '!!! warning "Draft"'
# Guides live outside docs/wiki/ because they run on a different trust model: signed opinion
# written from experience, carrying the author's name instead of a citation trail. They are not
# wiki pages and do not follow wiki rules.
GUIDES = DOCS / "guides"
BYLINE = '!!! info "Written by '


def front_matter(text):
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def check(path, drafts):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    # Wiki pages live under docs/wiki/; their section is the first segment below that.
    in_wiki = path.is_relative_to(WIKI)
    section = path.relative_to(WIKI).as_posix().split("/")[0] if in_wiki else ""
    in_guides = path.is_relative_to(GUIDES)
    is_index = path.name == "index.md"
    errors = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    if section in CONCEPT_DIRS and not is_index and "\n## Further resources" not in text:
        errors.append(f"{rel}: missing '## Further resources' section")
    if section == "resources" and not is_index and "\n## Related wiki pages" not in text:
        errors.append(f"{rel}: missing '## Related wiki pages' section")
    if in_guides:
        # A byline replaces the draft banner: guides are signed, not pending review.
        if not is_index:
            if BYLINE not in text:
                errors.append(f'{rel}: missing byline, expected \'{BYLINE}<name>"\'')
            if "\n## Further resources" not in text:
                errors.append(f"{rel}: missing '## Further resources' section")
        if front_matter(text).get("tags"):
            errors.append(f"{rel}: guides do not carry tags")
    elif drafts and rel not in EXEMPT_FROM_BANNER and BANNER not in text:
        errors.append(f"{rel}: missing draft banner")
    return errors


def main():
    drafts = "--drafts" in sys.argv[1:]
    errors = [error for path in sorted(DOCS.rglob("*.md")) for error in check(path, drafts)]
    for error in errors:
        print(error)
    print(f"{len(errors)} problem(s) found" if errors else "All pages OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
