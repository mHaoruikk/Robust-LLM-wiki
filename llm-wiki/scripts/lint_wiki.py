#!/usr/bin/env python3
"""
lint_wiki.py — Health check for an LLM Wiki.

Usage:
    python3 lint_wiki.py <wiki-root>

Example:
    python3 lint_wiki.py ~/wikis/causal-inference

Checks:
  1. Dead wikilinks — [[Target]] where Target.md doesn't exist
  2. Orphan pages — wiki pages with no inbound links
  3. Stale index — wiki/index.md is out of sync with content pages (via build_index.py --check)
  4. Unlinked concepts — terms mentioned 3+ times but lacking their own page
  5. PCMT type integrity — every wiki page has a valid `type` in frontmatter
  6. log/ shape — every file matches YYYYMMDD.md and has the right H1
  7. audit/ shape — every audit/*.md parses as a valid AuditEntry
  8. Audit targets — every open audit's `target` file must exist

Exit codes:
  0 — no issues found
  1 — issues found (printed to stdout)
"""

import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path


WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:[|#][^\]]*)?\]\]")
LOG_FILENAME_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})\.md$")
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

# Valid `type` values for PCMT wiki pages
VALID_PAGE_TYPES = {"problem", "concept", "method", "theory", "entity", "summary"}

# Map from wiki subdirectory to expected `type` value (for directory-type consistency)
PCMT_DIR_TO_TYPE = {
    "problems": "problem",
    "concepts": "concept",
    "methods": "method",
    "theory": "theory",
    "entities": "entity",
    "summaries": "summary",
}

# Required audit frontmatter fields
AUDIT_REQUIRED_FIELDS = {
    "id", "target", "target_lines", "anchor_before", "anchor_text",
    "anchor_after", "severity", "author", "source", "created", "status",
}
VALID_SEVERITIES = {"info", "suggest", "warn", "error"}
VALID_STATUSES = {"open", "resolved"}
VALID_SOURCES = {"obsidian-plugin", "web-viewer", "manual"}


def load_pages(wiki_dir: Path) -> tuple[dict[str, Path], dict[str, list[str]]]:
    """
    Returns:
      pages_by_rel  — {rel_posix_without_ext: abs_path}   primary lookup
      pages_by_stem — {stem: [rel1, rel2, ...]}            ambiguity detection
    Keying by full relative path (not just stem) prevents false matches when two
    pages share the same filename in different domains or type directories.
    """
    pages_by_rel: dict[str, Path] = {}
    pages_by_stem: dict[str, list[str]] = {}
    for p in wiki_dir.rglob("*.md"):
        rel = p.relative_to(wiki_dir).with_suffix("").as_posix()
        pages_by_rel[rel] = p
        pages_by_stem.setdefault(p.stem, []).append(rel)
    return pages_by_rel, pages_by_stem


def resolve_wikilink(
    link: str,
    pages_by_rel: dict[str, Path],
    pages_by_stem: dict[str, list[str]],
) -> tuple[str | None, bool]:
    """
    Resolve a raw wikilink target to a canonical rel path.

    Returns (canonical_rel, is_ambiguous):
      - canonical_rel is the resolved rel path, or None if unresolvable.
      - is_ambiguous is True when a bare stem matches multiple pages in different
        directories. Ambiguous links are reported separately from dead links.
    """
    link = link.strip()
    # Full relative-path match (the preferred wikilink form)
    if link in pages_by_rel:
        return link, False
    # Bare stem or partial path: find all matches by stem
    stem = Path(link).stem
    matches = pages_by_stem.get(stem, [])
    if len(matches) == 1:
        return matches[0], False
    if len(matches) > 1:
        return None, True  # ambiguous — don't silently pick one
    return None, False  # dead link


def extract_wikilinks(text: str) -> list[str]:
    return WIKILINK_RE.findall(text)


def parse_frontmatter(text: str) -> dict | None:
    """Minimal YAML-ish frontmatter parser. Handles the flat key:value fields
    and one-level lists/arrays actually used by audit files. Does not handle
    arbitrary YAML — intentional, to avoid a pyyaml dependency."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    body = m.group(1)
    result: dict = {}
    # Track multi-line folded strings via simple heuristic: quoted scalars
    # can contain \n; unquoted values are single-line.
    i = 0
    lines = body.split("\n")
    while i < len(lines):
        line = lines[i]
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        if ":" not in line:
            i += 1
            continue
        key, _, rest = line.partition(":")
        key = key.strip()
        val = rest.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                result[key] = []
            else:
                parts = [p.strip() for p in inner.split(",")]
                parsed: list = []
                for p in parts:
                    if p.isdigit() or (p.startswith("-") and p[1:].isdigit()):
                        parsed.append(int(p))
                    else:
                        parsed.append(p.strip('"').strip("'"))
                result[key] = parsed
        elif val.startswith('"') and val.endswith('"'):
            result[key] = val[1:-1].replace("\\n", "\n").replace('\\"', '"')
        elif val.startswith("'") and val.endswith("'"):
            result[key] = val[1:-1]
        else:
            result[key] = val
        i += 1
    return result


def lint(root: str) -> int:
    root_path = Path(root)
    wiki_path = root_path / "wiki"
    log_path = root_path / "log"
    audit_path = root_path / "audit"

    if not wiki_path.exists():
        print(f"ERROR: wiki/ directory not found at {wiki_path}", file=sys.stderr)
        return 1

    pages_by_rel, pages_by_stem = load_pages(wiki_path)
    all_wiki_files = list(wiki_path.rglob("*.md"))
    index_path = wiki_path / "index.md"

    issues = 0
    # inbound: {canonical_rel: [source_rel, ...]} — keyed by full rel path
    inbound: dict[str, list[str]] = defaultdict(list)

    # ── Pass 1: dead wikilinks ──────────────────────────────────────────────
    dead_links: list[tuple[str, str]] = []
    ambiguous_links: list[tuple[str, str, list[str]]] = []
    for md_file in all_wiki_files:
        source_rel = md_file.relative_to(wiki_path).with_suffix("").as_posix()
        text = md_file.read_text(encoding="utf-8")
        for link in extract_wikilinks(text):
            canonical, is_ambiguous = resolve_wikilink(link, pages_by_rel, pages_by_stem)
            if is_ambiguous:
                stem = Path(link.strip()).stem
                candidates = pages_by_stem.get(stem, [])
                ambiguous_links.append((str(md_file.relative_to(root_path)), link.strip(), candidates))
            elif canonical is None:
                dead_links.append((str(md_file.relative_to(root_path)), link.strip()))
            else:
                inbound[canonical].append(source_rel)

    if dead_links:
        print(f"\n🔴 Dead wikilinks ({len(dead_links)}):")
        for source, link in dead_links:
            print(f"   {source} → [[{link}]]")
        issues += len(dead_links)
    else:
        print("✅ No dead wikilinks")

    if ambiguous_links:
        print(f"\n🟡 Ambiguous bare-stem wikilinks ({len(ambiguous_links)}) — use full relative paths:")
        for source, link, candidates in ambiguous_links:
            print(f"   {source} → [[{link}]]  matches: {', '.join(candidates)}")
        issues += len(ambiguous_links)

    # ── Pass 2: orphan pages ────────────────────────────────────────────────
    # Skip root-level generated/special files; skip folder-split index.md files
    # (their stem is "index" — they may not be cross-linked in body text even
    # though wiki/index.md links to them, and that is acceptable).
    SKIP_ORPHAN_STEMS = {"index", "open-questions"}
    orphans = []
    for p in all_wiki_files:
        if p.parent == wiki_path:
            continue  # wiki/index.md, wiki/open-questions.md
        if p.stem in SKIP_ORPHAN_STEMS:
            continue  # folder-split index.md files
        rel = p.relative_to(wiki_path).with_suffix("").as_posix()
        if rel not in inbound:
            orphans.append(p)
    if orphans:
        print(f"\n🟡 Orphan pages ({len(orphans)}) — no inbound wikilinks:")
        for p in orphans:
            print(f"   {p.relative_to(root_path)}")
        issues += len(orphans)
    else:
        print("✅ No orphan pages")

    # ── Pass 3: stale index (via build_index.py --check) ───────────────────
    # wiki/index.md is a generated artifact; this pass verifies it matches
    # what build_index.py would produce from current page frontmatter.
    builder = Path(__file__).parent / "build_index.py"
    if not builder.exists():
        print("⚠️  build_index.py not found — skipping index freshness check")
    elif not index_path.exists():
        print("🔴 wiki/index.md not found — run build_index.py to create it")
        issues += 1
    else:
        result = subprocess.run(
            [sys.executable, str(builder), root, "--check"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("✅ wiki/index.md is up-to-date")
        else:
            msg = (result.stdout or result.stderr or "index is stale").strip()
            print(f"\n🔴 wiki/index.md is stale: {msg}")
            print("   Run: python3 llm-wiki/scripts/build_index.py <wiki-root>")
            issues += 1

    # ── Pass 4: unlinked concepts ───────────────────────────────────────────
    all_text = " ".join(p.read_text(encoding="utf-8") for p in all_wiki_files)
    all_links = WIKILINK_RE.findall(all_text)
    link_counts: dict[str, int] = defaultdict(int)
    for link in all_links:
        link_counts[link.strip()] += 1

    missing_pages = [
        (link, count) for link, count in link_counts.items()
        if count >= 3
        and resolve_wikilink(link, pages_by_rel, pages_by_stem) == (None, False)
    ]
    if missing_pages:
        print(f"\n🟡 Frequently linked but no page ({len(missing_pages)}):")
        for link, count in sorted(missing_pages, key=lambda x: -x[1]):
            print(f"   [[{link}]] — mentioned {count}x")
        issues += len(missing_pages)
    else:
        print("✅ No frequently-linked missing pages")

    # ── Pass 5: PCMT type integrity ─────────────────────────────────────────
    type_issues: list[str] = []
    for md_file in all_wiki_files:
        if md_file == index_path:
            continue
        # Determine expected type from the first path component under wiki/
        rel_parts = md_file.relative_to(wiki_path).parts
        if not rel_parts:
            continue
        top_dir = rel_parts[0]
        expected_type = PCMT_DIR_TO_TYPE.get(top_dir)
        if expected_type is None:
            continue  # unknown top-level dir — skip, not our business
        text = md_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        rel = md_file.relative_to(root_path)
        if fm is None:
            type_issues.append(f"   {rel} — missing YAML frontmatter")
            continue
        page_type = fm.get("type", "").strip()
        if not page_type:
            type_issues.append(f"   {rel} — frontmatter missing 'type' field")
        elif page_type not in VALID_PAGE_TYPES:
            type_issues.append(
                f"   {rel} — unknown type '{page_type}' "
                f"(expected one of: {', '.join(sorted(VALID_PAGE_TYPES))})"
            )
        elif page_type != expected_type:
            type_issues.append(
                f"   {rel} — type '{page_type}' doesn't match directory "
                f"'{top_dir}/' (expected '{expected_type}')"
            )
    if type_issues:
        print(f"\n🔴 PCMT type integrity issues ({len(type_issues)}):")
        for s in type_issues:
            print(s)
        issues += len(type_issues)
    else:
        print("✅ PCMT type integrity OK")

    # ── Pass 6: log/ shape ──────────────────────────────────────────────────
    if log_path.exists() and log_path.is_dir():
        log_issues: list[str] = []
        for p in sorted(log_path.iterdir()):
            if p.is_dir():
                continue
            if p.name == ".gitkeep":
                continue
            m = LOG_FILENAME_RE.match(p.name)
            if not m:
                log_issues.append(f"   {p.relative_to(root_path)} — filename doesn't match YYYYMMDD.md")
                continue
            y, mo, d = m.groups()
            iso = f"{y}-{mo}-{d}"
            first_line = p.read_text(encoding="utf-8").splitlines()[:1]
            if not first_line or first_line[0].strip() != f"# {iso}":
                log_issues.append(f"   {p.relative_to(root_path)} — expected H1 '# {iso}'")
        if log_issues:
            print(f"\n🟡 log/ shape issues ({len(log_issues)}):")
            for s in log_issues:
                print(s)
            issues += len(log_issues)
        else:
            print("✅ log/ shape OK")
    else:
        print("⚠️  log/ directory not found — skipping log shape check")

    # ── Pass 7: audit/ shape ─────────────────────────────────────────────────
    audit_targets_to_check: list[tuple[str, str]] = []  # (audit_id, target)
    if audit_path.exists() and audit_path.is_dir():
        audit_files = [
            p for p in audit_path.rglob("*.md") if p.name != ".gitkeep"
        ]
        audit_issues: list[str] = []
        for p in audit_files:
            text = p.read_text(encoding="utf-8")
            fm = parse_frontmatter(text)
            rel = p.relative_to(root_path)
            if fm is None:
                audit_issues.append(f"   {rel} — missing YAML frontmatter")
                continue
            missing = AUDIT_REQUIRED_FIELDS - set(fm.keys())
            if missing:
                audit_issues.append(
                    f"   {rel} — missing fields: {', '.join(sorted(missing))}"
                )
                continue
            if fm["severity"] not in VALID_SEVERITIES:
                audit_issues.append(
                    f"   {rel} — invalid severity '{fm['severity']}' (expected {sorted(VALID_SEVERITIES)})"
                )
            if fm["source"] not in VALID_SOURCES:
                audit_issues.append(
                    f"   {rel} — invalid source '{fm['source']}'"
                )
            expected_status = "resolved" if "resolved" in p.parts else "open"
            if fm["status"] != expected_status:
                audit_issues.append(
                    f"   {rel} — status '{fm['status']}' doesn't match directory (expected '{expected_status}')"
                )
            if fm["status"] == "open":
                audit_targets_to_check.append((fm["id"], fm["target"]))

        if audit_issues:
            print(f"\n🔴 audit/ shape issues ({len(audit_issues)}):")
            for s in audit_issues:
                print(s)
            issues += len(audit_issues)
        else:
            print(f"✅ audit/ shape OK ({len(audit_files)} files)")
    else:
        print("⚠️  audit/ directory not found — skipping audit shape check")

    # ── Pass 8: audit targets exist ──────────────────────────────────────────
    missing_targets: list[tuple[str, str]] = []
    for audit_id, target in audit_targets_to_check:
        target_path = root_path / target
        # Audit target paths are relative to wiki-root but typically point
        # at files under wiki/. Check both locations.
        if not target_path.exists():
            alt = wiki_path / target
            if not alt.exists():
                missing_targets.append((audit_id, target))
    if missing_targets:
        print(f"\n🔴 Open audits with missing target files ({len(missing_targets)}):")
        for audit_id, target in missing_targets:
            print(f"   {audit_id} → {target}")
        issues += len(missing_targets)
    elif audit_targets_to_check:
        print("✅ All open-audit targets exist")

    # ── Summary ─────────────────────────────────────────────────────────────
    print(f"\n{'─'*40}")
    if issues == 0:
        print("✅ Wiki is healthy — no issues found")
    else:
        print(f"⚠️  {issues} issue(s) found — review above and fix before next ingest")

    return 0 if issues == 0 else 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    sys.exit(lint(sys.argv[1]))

