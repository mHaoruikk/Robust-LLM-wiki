#!/usr/bin/env python3
"""
build_index.py — Deterministic wiki/index.md generator.

Usage:
    python3 build_index.py <wiki-root>           # regenerate wiki/index.md in place
    python3 build_index.py <wiki-root> --check   # diff only; exit 1 if index is stale
    python3 build_index.py <wiki-root> --migrate # warn on bad frontmatter instead of failing

The script is the sole authoritative writer of wiki/index.md.
The agent must NOT edit wiki/index.md manually.

Exit codes:
    0 — success (or index is up-to-date in --check mode)
    1 — frontmatter issues (hard errors), or index is stale (--check mode)
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path

# ── regex ─────────────────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
SIMPLE_KV_RE = re.compile(r"^(\w[\w-]*)\s*:\s*(.+)$")

# ── constants ─────────────────────────────────────────────────────────────────

# Directories under wiki/ that follow wiki/<type>/<domain>/<page> layout
PCMT_DIRS = {"problems", "concepts", "methods", "theory"}

# Display labels for each type section
TYPE_LABELS = {
    "problems": "Problems",
    "concepts": "Concepts",
    "methods": "Methods",
    "theory": "Theory",
    "entities": "Entities",
    "summaries": "Summaries",
}

# Canonical render order for type sections
TYPE_ORDER = ["problems", "concepts", "methods", "theory", "summaries", "entities"]

# Files that are NOT content pages — excluded from the catalog
EXCLUDED_FILES = {"index.md", "open-questions.md"}

# Required frontmatter fields per type group
REQUIRED_PCMT = {"type", "domain"}
REQUIRED_FLAT = {"type"}  # entities and summaries

# The string that marks the start of the generated body (navigation section).
# Everything before this in index.md is the preserved manual header.
NAV_SENTINEL = "## 🔖 Navigation"


# ── data model ────────────────────────────────────────────────────────────────

@dataclass
class PageEntry:
    """Represents one content page found under wiki/."""
    abs_path: Path
    # Path relative to wiki/ without .md extension, e.g. "concepts/statistics/eif"
    wiki_rel: str
    type_dir: str         # "problems", "concepts", "methods", "theory", "entities", "summaries"
    domain: str           # domain subdir for PCMT pages; empty for entities/summaries
    title: str            # from frontmatter `title` or stem
    oneliner: str         # first body sentence, used as the inline description
    year: int | None      # for summaries, used in sort + display
    ingested: str | None  # "YYYY-MM-DD" for summaries display date
    # Folder-split support
    is_folder_index: bool  # True if this file is a <topic>/index.md
    folder_rel: str | None # For children: wiki_rel of the parent <topic>/index.md


# ── frontmatter parser ────────────────────────────────────────────────────────

def parse_frontmatter(text: str) -> dict:
    """
    Minimal YAML frontmatter parser — handles the flat key:value fields and
    inline lists ([a, b, c]) used by wiki pages. No pyyaml dependency.
    """
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    result: dict = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        km = SIMPLE_KV_RE.match(line)
        if not km:
            continue
        key, val = km.group(1), km.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            result[key] = [p.strip().strip('"').strip("'") for p in inner.split(",") if p.strip()] if inner else []
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1]
        elif val.startswith("'") and val.endswith("'"):
            result[key] = val[1:-1]
        else:
            result[key] = val
    return result


def body_after_frontmatter(text: str) -> str:
    """Return the text body with frontmatter stripped."""
    m = FRONTMATTER_RE.match(text)
    if m:
        return text[m.end():]
    return text


def extract_oneliner(abs_path: Path, is_summary: bool) -> str:
    """
    For summaries: extract the H1 title (= paper/article title).
    For all other pages: extract the first non-heading, non-empty body line.
    Truncated to 120 chars.
    """
    try:
        text = abs_path.read_text(encoding="utf-8")
    except OSError:
        return ""
    body = body_after_frontmatter(text)
    if is_summary:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                return stripped[2:].strip()[:120]
        return abs_path.stem  # fallback: slug
    # Non-summary: first non-heading, non-empty line
    for line in body.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            result = stripped[:120]
            if len(stripped) > 120:
                result += "…"
            return result
    return ""


# ── page collection ───────────────────────────────────────────────────────────

def collect_pages(wiki_path: Path, migrate: bool) -> tuple[list[PageEntry], list[str]]:
    """
    Walk wiki/ and build the list of PageEntry objects.
    Returns (entries, errors).
    errors contains hard frontmatter problems; in migrate mode these become warnings.
    """
    entries: list[PageEntry] = []
    errors: list[str] = []

    for md_file in sorted(wiki_path.rglob("*.md")):
        # Only skip the root-level catalog and open-questions file,
        # not folder-split index.md files deeper in the tree.
        if md_file.parent == wiki_path and md_file.name in EXCLUDED_FILES:
            continue

        rel = md_file.relative_to(wiki_path)
        parts = rel.parts  # e.g. ("concepts", "statistics", "efficient-influence-function.md")

        if len(parts) < 2:
            continue  # wiki/index.md already excluded; nothing else at depth 1

        type_dir = parts[0]

        # ── entities and summaries: wiki/<type>/<name>.md ──────────────────
        if type_dir in ("entities", "summaries"):
            if len(parts) != 2:
                continue  # unexpected nesting; skip
            wiki_rel = rel.with_suffix("").as_posix()
            text = md_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            missing = REQUIRED_FLAT - set(fm.keys())
            if missing:
                msg = f"  {rel} — missing frontmatter: {', '.join(sorted(missing))}"
                errors.append(msg)
                if not migrate:
                    continue

            is_summary = type_dir == "summaries"
            year = None
            ingested = None
            if is_summary:
                y = fm.get("year", "")
                try:
                    year = int(str(y).strip()[:4])
                except (ValueError, TypeError):
                    year = None
                ingested = fm.get("ingested") or (str(year) if year else None)

            entries.append(PageEntry(
                abs_path=md_file,
                wiki_rel=wiki_rel,
                type_dir=type_dir,
                domain="",
                title=fm.get("title", md_file.stem),
                oneliner=extract_oneliner(md_file, is_summary),
                year=year,
                ingested=ingested,
                is_folder_index=False,
                folder_rel=None,
            ))
            continue

        # ── PCMT types: wiki/<type>/<domain>/... ──────────────────────────
        if type_dir not in PCMT_DIRS:
            continue

        if len(parts) < 3:
            continue  # malformed path

        domain = parts[1]

        # Depth 3: wiki/<type>/<domain>/<slug>.md — normal page
        if len(parts) == 3:
            wiki_rel = rel.with_suffix("").as_posix()
            text = md_file.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            missing = REQUIRED_PCMT - set(fm.keys())
            if missing:
                msg = f"  {rel} — missing frontmatter: {', '.join(sorted(missing))}"
                errors.append(msg)
                if not migrate:
                    continue
            entries.append(PageEntry(
                abs_path=md_file,
                wiki_rel=wiki_rel,
                type_dir=type_dir,
                domain=domain,
                title=fm.get("title", md_file.stem),
                oneliner=extract_oneliner(md_file, False),
                year=None,
                ingested=None,
                is_folder_index=False,
                folder_rel=None,
            ))
            continue

        # Depth 4+: wiki/<type>/<domain>/<topic>/... — folder-split
        if len(parts) >= 4:
            topic = parts[2]
            folder_index_rel = f"{type_dir}/{domain}/{topic}/index"

            if md_file.name == "index.md" and len(parts) == 4:
                # Folder-split root: wiki/<type>/<domain>/<topic>/index.md
                wiki_rel = rel.with_suffix("").as_posix()
                text = md_file.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                missing = REQUIRED_PCMT - set(fm.keys())
                if missing:
                    msg = f"  {rel} — missing frontmatter: {', '.join(sorted(missing))}"
                    errors.append(msg)
                    if not migrate:
                        continue
                entries.append(PageEntry(
                    abs_path=md_file,
                    wiki_rel=wiki_rel,
                    type_dir=type_dir,
                    domain=domain,
                    title=fm.get("title", topic),
                    oneliner=extract_oneliner(md_file, False),
                    year=None,
                    ingested=None,
                    is_folder_index=True,
                    folder_rel=None,
                ))
            else:
                # Folder-split child: wiki/<type>/<domain>/<topic>/<aspect>.md
                wiki_rel = rel.with_suffix("").as_posix()
                text = md_file.read_text(encoding="utf-8")
                fm = parse_frontmatter(text)
                missing = REQUIRED_PCMT - set(fm.keys())
                if missing:
                    msg = f"  {rel} — missing frontmatter: {', '.join(sorted(missing))}"
                    errors.append(msg)
                    if not migrate:
                        continue
                entries.append(PageEntry(
                    abs_path=md_file,
                    wiki_rel=wiki_rel,
                    type_dir=type_dir,
                    domain=domain,
                    title=fm.get("title", md_file.stem),
                    oneliner=extract_oneliner(md_file, False),
                    year=None,
                    ingested=None,
                    is_folder_index=False,
                    folder_rel=folder_index_rel,
                ))

    return entries, errors


# ── index rendering ───────────────────────────────────────────────────────────

def _entry_link(entry: PageEntry) -> str:
    """Wikilink for a page entry."""
    if entry.is_folder_index:
        # e.g. [[concepts/statistics/variance-decomp/index|variance-decomp]]
        topic = entry.wiki_rel.rsplit("/", 1)[-1]  # "index" — we want the folder name
        folder = entry.wiki_rel[: -len("/index")]
        topic_name = folder.rsplit("/", 1)[-1]
        return f"[[{entry.wiki_rel}|{topic_name}]]"
    return f"[[{entry.wiki_rel}]]"


def _fmt_line(entry: PageEntry, indent: str = "") -> str:
    link = _entry_link(entry)
    if entry.oneliner:
        return f"{indent}- {link} — {entry.oneliner}"
    return f"{indent}- {link}"


def render_pcmt_section(type_dir: str, entries: list[PageEntry]) -> str:
    """Render one PCMT section (Problems / Concepts / Methods / Theory)."""
    label = TYPE_LABELS[type_dir]
    lines = [f"## {label}"]

    # Group by domain
    domains: dict[str, list[PageEntry]] = {}
    for e in entries:
        domains.setdefault(e.domain, []).append(e)

    for domain in sorted(domains):
        lines.append(f"### {domain}")
        domain_entries = sorted(domains[domain], key=lambda e: e.title.lower())

        # Separate: folder indexes, folder children, and normal pages
        folder_indexes = {e.wiki_rel: e for e in domain_entries if e.is_folder_index}
        folder_children: dict[str, list[PageEntry]] = {}
        normal_pages: list[PageEntry] = []

        for e in domain_entries:
            if e.is_folder_index:
                continue
            if e.folder_rel and e.folder_rel in folder_indexes:
                folder_children.setdefault(e.folder_rel, []).append(e)
            else:
                normal_pages.append(e)

        # Render normal pages
        for e in sorted(normal_pages, key=lambda e: e.title.lower()):
            lines.append(_fmt_line(e))

        # Render folder-split groups
        for folder_rel, fidx in sorted(folder_indexes.items(), key=lambda kv: kv[1].title.lower()):
            lines.append(_fmt_line(fidx))
            children = sorted(folder_children.get(folder_rel, []), key=lambda e: e.title.lower())
            for child in children:
                lines.append(_fmt_line(child, indent="    "))

    lines.append("")
    return "\n".join(lines)


def render_entities_section(entries: list[PageEntry]) -> str:
    lines = ["## Entities"]
    for e in sorted(entries, key=lambda e: e.title.lower()):
        lines.append(_fmt_line(e))
    lines.append("")
    return "\n".join(lines)


def render_summaries_section(entries: list[PageEntry]) -> str:
    lines = ["## Summaries (chronological)"]
    # Sort by year desc, then by wiki_rel asc
    sorted_entries = sorted(
        entries,
        key=lambda e: (-(e.year or 0), e.wiki_rel),
    )
    for e in sorted_entries:
        date_str = e.ingested or (str(e.year) if e.year else "????")
        link = f"[[{e.wiki_rel}]]"
        if e.oneliner:
            lines.append(f"- {date_str} — {link} — {e.oneliner}")
        else:
            lines.append(f"- {date_str} — {link}")
    lines.append("")
    return "\n".join(lines)


def generate_body(entries: list[PageEntry]) -> str:
    """Generate the navigation + PCMT sections body."""
    nav = (
        "## 🔖 Navigation\n"
        "- [[#Problems]] · [[#Concepts]] · [[#Methods]] · [[#Theory]] "
        "· [[#Summaries]] · [[#Entities]]\n"
    )

    by_type: dict[str, list[PageEntry]] = {t: [] for t in TYPE_ORDER}
    for e in entries:
        if e.type_dir in by_type:
            by_type[e.type_dir].append(e)

    parts = [nav]
    for type_dir in ["problems", "concepts", "methods", "theory"]:
        elist = by_type[type_dir]
        if elist:
            parts.append(render_pcmt_section(type_dir, elist))
        else:
            parts.append(f"## {TYPE_LABELS[type_dir]}\n\n*(none yet)*\n")

    if by_type["summaries"]:
        parts.append(render_summaries_section(by_type["summaries"]))
    else:
        parts.append("## Summaries (chronological)\n\n*(none yet)*\n")

    if by_type["entities"]:
        parts.append(render_entities_section(by_type["entities"]))
    else:
        parts.append("## Entities\n\n*(none yet)*\n")

    return "\n".join(parts)


# ── header preservation ───────────────────────────────────────────────────────

def extract_preserved_header(index_text: str) -> str:
    """
    Return everything in the current index.md that appears before the generated
    body (i.e. before the '## 🔖 Navigation' sentinel).
    If the sentinel is absent, return the entire file as the header.
    """
    idx = index_text.find(NAV_SENTINEL)
    if idx == -1:
        return index_text.rstrip() + "\n\n"
    return index_text[:idx]


def default_header(wiki_root: Path) -> str:
    """Fallback header when wiki/index.md doesn't exist yet."""
    topic = wiki_root.name.replace("-", " ").title()
    return f"# Index — {topic}\n\n> One-sentence scope of the wiki.\n\n"


# ── main ──────────────────────────────────────────────────────────────────────

def build(root: str, check_only: bool = False, migrate: bool = False) -> int:
    """
    Build (or check) wiki/index.md.
    Returns 0 on success, 1 on failure.
    """
    root_path = Path(root)
    wiki_path = root_path / "wiki"
    index_path = wiki_path / "index.md"

    if not wiki_path.exists():
        print(f"ERROR: wiki/ directory not found at {wiki_path}", file=sys.stderr)
        return 1

    # Collect pages
    entries, errors = collect_pages(wiki_path, migrate)

    had_errors = bool(errors)
    if errors:
        label = "Warnings" if migrate else "Errors"
        print(f"\n🔴 Frontmatter {label} ({len(errors)}):")
        for e in errors:
            print(e)
        if not migrate:
            print("\nFix the above issues before regenerating the index.")
            print("(Run with --migrate to treat these as warnings and proceed anyway.)")
            return 1

    # Preserve manual header from existing index
    if index_path.exists():
        existing = index_path.read_text(encoding="utf-8")
        header = extract_preserved_header(existing)
    else:
        header = default_header(root_path)

    # Generate new body
    body = generate_body(entries)
    new_content = header + body

    if check_only:
        if not index_path.exists():
            print("🔴 wiki/index.md does not exist — run build_index.py to create it")
            return 1
        existing = index_path.read_text(encoding="utf-8")
        if existing == new_content:
            print("✅ wiki/index.md is up-to-date")
            return 1 if had_errors else 0
        else:
            print("🔴 wiki/index.md is stale — run build_index.py to regenerate")
            return 1

    # Write
    index_path.write_text(new_content, encoding="utf-8")
    n = sum(1 for e in entries if not e.is_folder_index or True)  # count all entries
    print(f"✅ Regenerated wiki/index.md ({len(entries)} pages indexed)")
    return 1 if had_errors else 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0].startswith("-"):
        print(__doc__)
        sys.exit(1)

    root_arg = args[0]
    check_only = "--check" in args
    migrate = "--migrate" in args

    sys.exit(build(root_arg, check_only=check_only, migrate=migrate))
