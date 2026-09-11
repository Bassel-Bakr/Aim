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
ALLOWED_TAGS = {
    "community", "trainer", "creator",
    "clicking", "tracking", "switching",
    "benchmarks", "routines", "sensitivity", "beginner",
}
CONCEPT_DIRS = {"getting-started", "fundamentals", "skills", "training"}
BANNER = '!!! warning "Draft"'


def front_matter(text):
    match = re.match(r"---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def check(path, drafts):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    section = rel.split("/")[0]
    is_index = path.name == "index.md"
    errors = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    if section in CONCEPT_DIRS and not is_index and "\n## Further resources" not in text:
        errors.append(f"{rel}: missing '## Further resources' section")
    if section == "resources" and not is_index and "\n## Related wiki pages" not in text:
        errors.append(f"{rel}: missing '## Related wiki pages' section")
    if drafts and rel != "tags.md" and BANNER not in text:
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
