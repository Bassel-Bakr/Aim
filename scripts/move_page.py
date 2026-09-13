"""Move a page and repoint everything that refers to it.

Usage:
    python scripts/move_page.py wiki/categories/tracking.md wiki/skills/tracking.md

Paths are relative to docs/; a leading docs/ is accepted. The script:

1. Rewrites every relative Markdown link to the page, in docs/ and in the Markdown files at the
   repository root, and recomputes the moved page's own relative links for its new folder.
2. Repoints `related:` front matter entries that list the page.
3. Updates the page's `nav` entry in zensical.toml.
4. Adds a redirect from the old URL, so bookmarks and outside links keep working, and repoints
   existing redirects that led to the old path.
5. Moves the file with `git mv`.

Links inside fenced code blocks are left alone: they are examples, not links. Templates and specs
are not touched. Afterwards it checks that every relative link in docs/ resolves, exits non-zero if
one does not, and lists other mentions of the old path, such as in scripts, for you to review.
Undo a move with `git restore --staged --worktree .` before committing.
"""
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
CONFIG = ROOT / "zensical.toml"
# An inline Markdown link or image: ](target) or ](target "title").
LINK = re.compile(r"(\]\()([^)\s]+)((?:\s+\"[^\"]*\")?\))")
FENCE = re.compile(r"^\s*(```|~~~)")
FRONT_MATTER = re.compile(r"\A(---\r?\n.*?\r?\n---\r?\n)", re.S)


def normalize(path):
    """A docs-relative path, whether or not it was given with a leading docs/."""
    path = PurePosixPath(path.replace("\\", "/"))
    return str(path.relative_to("docs")) if path.parts[:1] == ("docs",) else str(path)


def join(folder, href):
    """Resolve href against a repository-relative folder, collapsing . and .. segments."""
    parts = []
    for part in (PurePosixPath(folder) / href).parts:
        if part == "..":
            if parts:
                parts.pop()
        elif part != ".":
            parts.append(part)
    return "/".join(parts)


def relative(target, folder):
    """The relative path from a repository-relative folder to a repository-relative target."""
    target_parts, folder_parts = target.split("/"), [p for p in folder.split("/") if p not in ("", ".")]
    common = 0
    while common < min(len(target_parts) - 1, len(folder_parts)) and target_parts[common] == folder_parts[common]:
        common += 1
    return "/".join([".."] * (len(folder_parts) - common) + target_parts[common:])


def is_relative(href):
    return not re.match(r"^([a-z][a-z0-9+.-]*:|#|/)", href, re.I)


def rewrite_links(text, before, after, old, new):
    """Repoint links in one file. before/after are its repository-relative paths."""
    lines, fenced = text.split("\n"), False
    for index, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
        if fenced:
            continue

        def repoint(match):
            href = match.group(2)
            if not is_relative(href):
                return match.group(0)
            path, hash_, fragment = href.partition("#")
            if not path:
                return match.group(0)
            target = join(str(PurePosixPath(before).parent), path)
            if target != old and before == after:
                return match.group(0)
            target = new if target == old else target
            return match.group(1) + relative(target, str(PurePosixPath(after).parent)) + hash_ + fragment + match.group(3)

        lines[index] = LINK.sub(repoint, line)
    return "\n".join(lines)


def rewrite_related(text, old, new):
    match = FRONT_MATTER.match(text)
    if not match:
        return text
    front = re.sub(rf"^(\s*-?\s*page:\s*){re.escape(old)}(\s*)$", rf"\g<1>{new}\g<2>", match.group(1), flags=re.M)
    return front + text[match.end():]


def rewrite_config(text, old, new):
    # The nav entry: the page's path in quotes inside the nav list.
    start = text.index("nav = [")
    end = text.index("\n]", start)
    text = text[:start] + text[start:end].replace(f'"{old}"', f'"{new}"') + text[end:]
    # Redirects: repoint any that led to the old path, drop one whose old URL is now a real page
    # again, and send the old URL to the new one.
    header = "[project.plugins.redirects.redirect_maps]\n"
    start = text.index(header) + len(header)
    end = text.find("\n[", start)
    end = len(text) if end == -1 else end + 1
    entries = [line for line in text[start:end].splitlines() if line.strip()]
    kept = []
    for line in entries:
        source, _, target = (part.strip().strip('"') for part in line.partition("="))
        if source == new:
            continue
        kept.append(f'"{source}" = "{new if target == old else target}"')
    kept.append(f'"{old}" = "{new}"')
    return text[:start] + "\n".join(kept) + "\n" + ("\n" if end < len(text) else "") + text[end:]


def broken_links():
    problems = []
    for path in sorted(DOCS.rglob("*.md")):
        rel = path.relative_to(ROOT).as_posix()
        fenced = False
        for number, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
            if FENCE.match(line):
                fenced = not fenced
            if fenced:
                continue
            for href in (match.group(2) for match in LINK.finditer(line)):
                target = href.partition("#")[0]
                if is_relative(href) and target and not (ROOT / join(str(PurePosixPath(rel).parent), target)).exists():
                    problems.append(f"{rel}:{number}: {href} does not resolve")
    return problems


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    old_page, new_page = normalize(sys.argv[1]), normalize(sys.argv[2])
    old, new = f"docs/{old_page}", f"docs/{new_page}"
    if not (ROOT / old).is_file():
        sys.exit(f"{old} does not exist")
    if (ROOT / new).exists():
        sys.exit(f"{new} already exists")
    if not new.endswith(".md"):
        sys.exit("the new path must end in .md")

    tracked = subprocess.run(["git", "ls-files", "*.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    files = [name for name in tracked if name.startswith("docs/") or "/" not in name]
    changed = []
    for name in files:
        text = (ROOT / name).read_text(encoding="utf-8")
        updated = rewrite_links(text, name, new if name == old else name, old, new)
        if name.startswith("docs/"):
            updated = rewrite_related(updated, old_page, new_page)
        if updated != text:
            (ROOT / name).write_text(updated, encoding="utf-8", newline="\n")
            changed.append(name)
    config = CONFIG.read_text(encoding="utf-8")
    CONFIG.write_text(rewrite_config(config, old_page, new_page), encoding="utf-8", newline="\n")

    (ROOT / new).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", old, new], cwd=ROOT, check=True)

    print(f"moved {old} -> {new}")
    print(f"updated {len(changed)} file(s): " + ", ".join(new if name == old else name for name in changed))
    print(f"zensical.toml: nav entry and a redirect from {old_page}")
    mentions = subprocess.run(["git", "grep", "-n", "-F", old_page, "--", ".", ":!zensical.toml", ":!specs"],
                              cwd=ROOT, capture_output=True, text=True).stdout.strip()
    if mentions:
        print("\nOther mentions of the old path, not changed:\n" + mentions)
    problems = broken_links()
    if problems:
        print("\nBroken links:\n" + "\n".join(problems))
        return 1
    print("\nAll relative links in docs/ resolve. Run `zensical build --clean` and check the output.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
