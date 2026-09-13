"""Check wiki pages against the rules in CONTRIBUTING.md.

Usage:
    python scripts/check_pages.py                          # tags, sections, and readability
    python scripts/check_pages.py --drafts                 # also require the draft banner
    python scripts/check_pages.py docs/wiki/glossary.md    # check named pages only
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
    "myth",
}
CONCEPT_DIRS = {"getting-started", "fundamentals", "categories", "techniques", "training"}
BANNER = '!!! warning "Draft"'
# Articles live outside docs/wiki/ because they run on a different trust model: signed opinion
# written from experience, carrying the author's name instead of a citation trail. They are not
# wiki pages and do not follow wiki rules.
ARTICLES = DOCS / "articles"
BYLINE = '!!! info "Written by '
# The inline .aim-myth block's title is the anchor into wiki/myths.md: it must match a hub
# heading word for word, or the link it ships with silently lands at the top of the page.
MYTH_BLOCK = re.compile(r'!!! myth "([^"]*)"')
MYTH_HEADING = re.compile(r"^## (.+)$", re.M)
# Sources live once in references.yml and pages cite them by ID; see extensions/aim_references.py.
REGISTRY = DOCS.parent / "references.yml"
REFERENCE_ID = re.compile(r"^REF-[1-9]\d*$")
REFERENCE_CITATION = re.compile(r"\[\^(REF-[1-9]\d*)\](?!:)")
REFERENCE_DEFINITION = re.compile(r"^\[\^(REF-[^\]]*)\]:", re.M)
REFERENCE_MARKER = re.compile(r"\[\^(REF-[^\]]*)\](?!:)")
REFERENCES_HEADING = re.compile(r"^## References\s*$", re.M)
REFERENCE_FIELDS = {"id", "author", "title", "url", "type", "publication", "notes"}
REFERENCE_REQUIRED = {"id", "author", "title", "url", "type"}
REFERENCE_TYPES = {"article", "document", "documentation", "encyclopedia", "post", "repository", "study", "video", "website"}


def registry_ids():
    """Validate references.yml and return its IDs, with any problems found."""
    errors = []
    entries = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or []
    ids, urls = set(), set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            errors.append(f"references.yml entry {index + 1}: not a mapping")
            continue
        where = f"references.yml {entry.get('id', f'entry {index + 1}')}"
        for field in sorted(REFERENCE_REQUIRED - entry.keys()):
            errors.append(f"{where}: missing '{field}'")
        for field in sorted(entry.keys() - REFERENCE_FIELDS):
            errors.append(f"{where}: unknown field '{field}'")
        ref_id, url = entry.get("id", ""), entry.get("url", "")
        if not REFERENCE_ID.match(str(ref_id)):
            errors.append(f"{where}: id must look like REF-1, with no leading zeros")
        if ref_id in ids:
            errors.append(f"{where}: duplicate id")
        if url in urls:
            errors.append(f"{where}: duplicate url {url}")
        if not str(url).startswith("https://"):
            errors.append(f"{where}: url must start with https://")
        if entry.get("type") not in REFERENCE_TYPES:
            errors.append(f"{where}: type '{entry.get('type')}' is not one of {', '.join(sorted(REFERENCE_TYPES))}")
        ids.add(ref_id)
        urls.add(url)
    return ids, errors


# A key block marks the one point a reader should leave a page with. Two on a page means neither
# is the one.
KEY_BLOCK = re.compile(r'^!!! key "', re.M)

# Readability. Most readers skim and many read with ADHD, so a page has to survive being read in
# passes: short paragraphs, short sentences, the answer first, and a way out at the end. See
# specs/2026-09-13-readability-design.md for where these numbers come from.
PARAGRAPH_LIMIT = 45
SENTENCE_LIMIT = 25
ANSWER_BULLETS = range(3, 6)
NEXT_ACTION = "**Do this next.**"
WORD = re.compile(r"[A-Za-z0-9][A-Za-z0-9'’/-]*")
# A sentence ends at . ! ? : or ; followed by a capital or digit. Abbreviations and decimals are
# shielded first so "e.g. Voltaic" and "0.27 sensitivity" do not end one.
ABBREVIATION = re.compile(r"\b(?:e\.g|i\.e|vs|etc|approx|cf)\.")
DECIMAL = re.compile(r"(\d)\.(\d)")
SENTENCE_END = re.compile(r"(?<=[.!?:;])[\"”’)]*\s+(?=[A-Z0-9\"“(\[])")
# The site writes US English, like its sources. Footnote definitions are exempt: they quote titles.
BRITISH = re.compile(
    r"\b(practis(?:e|ed|es|ing)|organis(?:e|ed|es|ing|ation)|behaviours?|colour(?:ed|ing|s)?"
    r"|centres?|analys(?:e|ed|ing)|labour|favourites?|defence|recognis(?:e|ed|es|ing)"
    r"|realis(?:e|ed|es|ing)|minimis(?:e|ed|es|ing)|optimis(?:e|ed|es|ing|ation))\b",
    re.I,
)


def front_matter(text):
    match = re.match(r"---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def myth_headings():
    text = (WIKI / "myths.md").read_text(encoding="utf-8")
    return set(MYTH_HEADING.findall(text))


def body(text):
    """The page without its front matter, comments, or fenced code."""
    text = re.sub(r"\A---\r?\n.*?\r?\n---\r?\n", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    return re.sub(r"```.*?```", "", text, flags=re.S)


def prose_blocks(text):
    """Paragraphs and lists that readers read as prose, with markup a reader never sees removed.

    Headings, tables, footnote definitions, HTML, and admonitions are skipped: none of them is a
    run of prose, and an admonition body is indented so it is caught by the same test.
    """
    for block in re.split(r"\n\s*\n", body(text)):
        stripped = block.strip()
        if not stripped or block.startswith("    "):
            continue
        if stripped.startswith(("#", "|", "[^", "<", "!!!", "???")):
            continue
        yield stripped


def plain(text):
    text = re.sub(r"\[\^[^\]]+\]", "", text)
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)(\{[^}]*\})?", r"\1", text)
    return " ".join(re.sub(r"[*_`]", "", text).split())


def units(block):
    """A list yields one unit per item; a prose block yields itself as one paragraph."""
    if re.match(r"([-*]|\d+\.)\s", block):
        items = re.split(r"\n\s*(?:[-*]|\d+\.)\s+", "\n" + block)
        return [(False, plain(item)) for item in items if item.strip()]
    return [(True, plain(block))]


def sentences(text):
    shielded = DECIMAL.sub(r"\1§\2", ABBREVIATION.sub(lambda m: m.group(0).replace(".", "§"), text))
    return [part.replace("§", ".") for part in SENTENCE_END.split(shielded) if part.strip()]


def words(text):
    return len(WORD.findall(text))


def excerpt(text):
    return text if len(text) <= 70 else text[:67] + "..."


def readability(rel, text, concept):
    errors = []
    for block in prose_blocks(text):
        for is_paragraph, unit in units(block):
            if is_paragraph and words(unit) > PARAGRAPH_LIMIT:
                errors.append(
                    f"{rel}: paragraph of {words(unit)} words (limit {PARAGRAPH_LIMIT}): "
                    f'"{excerpt(unit)}"'
                )
            for sentence in sentences(unit):
                if words(sentence) > SENTENCE_LIMIT:
                    errors.append(
                        f"{rel}: sentence of {words(sentence)} words (limit {SENTENCE_LIMIT}): "
                        f'"{excerpt(sentence)}"'
                    )
    prose = re.sub(r"^\[\^[^\]]+\]:.*$", "", body(text), flags=re.M)
    for spelling in sorted({match.lower() for match in BRITISH.findall(prose)}):
        errors.append(f"{rel}: British spelling '{spelling}', the site writes US English")
    if concept:
        lead = body(text).split("\n## ", 1)[0]
        bullets = len(re.findall(r"^- ", lead, flags=re.M))
        if bullets not in ANSWER_BULLETS:
            errors.append(
                f"{rel}: opens with {bullets} bullets before its first heading, expected 3 to 5"
            )
        before_related = text.split("\n## Related pages", 1)[0]
        if NEXT_ACTION not in before_related:
            errors.append(f"{rel}: missing a '{NEXT_ACTION}' paragraph before Related pages")
    return errors


def check(path, drafts, headings, known_ids):
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(DOCS).as_posix()
    # Wiki pages live under docs/wiki/; their section is the first segment below that.
    in_wiki = path.is_relative_to(WIKI)
    section = path.relative_to(WIKI).as_posix().split("/")[0] if in_wiki else ""
    in_articles = path.is_relative_to(ARTICLES)
    is_index = path.name == "index.md"
    errors = []

    for tag in front_matter(text).get("tags") or []:
        if tag not in ALLOWED_TAGS:
            errors.append(f"{rel}: tag '{tag}' is not allowed")
    if section in CONCEPT_DIRS and not is_index and "\n## Related pages" not in text:
        errors.append(f"{rel}: missing '## Related pages' section")
    if section == "resources" and not is_index and "\n## Related pages" not in text:
        errors.append(f"{rel}: missing '## Related pages' section")
    # References are the sources for claims on this page; they sit under their own heading, apart
    # from Resources, which point readers to material for learning more.
    cited = set(REFERENCE_CITATION.findall(text))
    if in_wiki and REFERENCES_HEADING.search(text):
        errors.append(f"{rel}: remove '## References'; the references extension adds it")
    for marker in sorted(set(REFERENCE_MARKER.findall(text)) - cited):
        errors.append(f"{rel}: [^{marker}] is not a valid reference ID; use REF-1 style, no leading zeros")
    for ref_id in sorted(cited - known_ids):
        errors.append(f"{rel}: cites {ref_id}, which is not in references.yml")
    for label in REFERENCE_DEFINITION.findall(text):
        errors.append(f"{rel}: defines [^{label}] on the page; references are defined only in references.yml")
    if in_articles:
        # A byline replaces the draft banner: articles are signed, not pending review.
        if not is_index:
            if BYLINE not in text:
                errors.append(f'{rel}: missing byline, expected \'{BYLINE}<name>"\'')
            if "\n## Further resources" not in text:
                errors.append(f"{rel}: missing '## Further resources' section")
        if front_matter(text).get("tags"):
            errors.append(f"{rel}: articles do not carry tags")
    elif drafts and rel not in EXEMPT_FROM_BANNER and BANNER not in text:
        errors.append(f"{rel}: missing draft banner")
    if in_wiki:
        for title in MYTH_BLOCK.findall(text):
            if title not in headings:
                errors.append(
                    f"{rel}: myth block title '{title}' has no matching heading on wiki/myths.md"
                )
        errors += readability(rel, text, section in CONCEPT_DIRS and not is_index)
        keys = len(KEY_BLOCK.findall(text))
        if keys > 1:
            errors.append(f"{rel}: {keys} key blocks, a page carries at most one")
    return errors


def main():
    args = sys.argv[1:]
    drafts = "--drafts" in args
    named = [Path(arg).resolve() for arg in args if not arg.startswith("--")]
    paths = named or sorted(DOCS.rglob("*.md"))
    headings = myth_headings()
    known_ids, errors = registry_ids()
    errors += [error for path in paths for error in check(path, drafts, headings, known_ids)]
    for error in errors:
        print(error)
    print(f"{len(errors)} problem(s) found" if errors else "All pages OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
