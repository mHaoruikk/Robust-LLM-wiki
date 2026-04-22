#!/usr/bin/env python3
"""
scaffold.py — Bootstrap a new LLM Wiki directory structure.

Usage:
    python3 scaffold.py <wiki-root> "<Topic Title>"

Example:
    python3 scaffold.py ~/wikis/causal-inference "Causal Inference"

Creates:
    <wiki-root>/
    ├── CLAUDE.md          (schema template)
    ├── log/
    │   └── YYYYMMDD.md    (first day's log with scaffold entry)
    ├── audit/
    │   ├── .gitkeep
    │   └── resolved/
    │       └── .gitkeep
    ├── raw/
    │   ├── incoming/      (drop converted markdown here before running ingest)
    │   ├── articles/
    │   ├── papers/
    │   ├── notes/
    │   └── refs/
    ├── wiki/
    │   ├── index.md       (PCMT-structured catalog)
    │   ├── problems/      (research questions)
    │   ├── concepts/      (domain objects and quantities)
    │   ├── methods/       (procedures and estimators)
    │   ├── theory/        (mathematical foundations)
    │   ├── entities/      (people, tools, datasets, organizations)
    │   └── summaries/     (per-paper/source summary pages)
    └── outputs/
        ├── queries/
        └── brainstorm/
"""

import os
import sys
from datetime import date, datetime


def scaffold(root: str, title: str) -> None:
    today = date.today()
    today_iso = today.isoformat()
    today_compact = today.strftime("%Y%m%d")
    now_hm = datetime.now().strftime("%H:%M")

    dirs = [
        "raw/incoming",
        "raw/articles",
        "raw/papers",
        "raw/notes",
        "raw/refs",
        "wiki/problems",
        "wiki/concepts",
        "wiki/methods",
        "wiki/theory",
        "wiki/entities",
        "wiki/summaries",
        "outputs/queries",
        "outputs/brainstorm",
        "log",
        "audit",
        "audit/resolved",
    ]

    for d in dirs:
        os.makedirs(os.path.join(root, d), exist_ok=True)
    print(f"✓ Created directory tree under {root}/")

    # .gitkeep for empty audit dirs
    _write(root, "audit/.gitkeep", "")
    _write(root, "audit/resolved/.gitkeep", "")

    # CLAUDE.md
    claude_md = f"""# {title} Knowledge Base

> Schema document — read at the start of every session together with `wiki/index.md`.
> Update after every major compile, ingest batch, or structural change.

## Scope

What this wiki covers:
- <describe the topic area>

What this wiki deliberately excludes:
- <describe out-of-scope areas>

## Operations

This wiki follows the llm-wiki skill's seven operations: `compile`, `ingest`, `query`, `lint`, `audit`, `brainstorm`, `build-index`.
Every operation appends an entry to `log/YYYYMMDD.md`.

## Naming conventions (PCMT ontology)

- **Problem pages** (`wiki/problems/<domain>/`): kebab-case noun phrases naming a research challenge.
  E.g., `long-term-treatment-effects.md`
- **Concept pages** (`wiki/concepts/<domain>/`): kebab-case noun phrases naming a domain object.
  E.g., `surrogate-index.md`, `average-treatment-effect.md`
- **Method pages** (`wiki/methods/<domain>/`): kebab-case noun phrases naming a procedure.
  E.g., `doubly-robust-estimation.md`
- **Theory pages** (`wiki/theory/<domain>/`): kebab-case noun phrases naming a mathematical tool.
  E.g., `efficient-influence-function.md`
- **Entity pages** (`wiki/entities/`): Proper names. E.g., "Susan Athey".
- **Summary pages** (`wiki/summaries/`): paper slug `{{author}}-{{keyword}}-{{year}}`.

**Domain subdirectories** are namespace prefixes within each PCMT type dir. Start with the most
relevant domain name (e.g., `causal-inference`, `statistics`, `machine-learning`). Create new
domains freely; no registration needed.

**⚠️ Agent must ask user permission before creating any new problem/concept/method/theory page.**

All pages require YAML frontmatter: `title`, `type`, `domain`, `created`, `updated`, `sources`, `tags`.

### Diagrams and formulas
- All structural diagrams are **mermaid**. No ASCII art.
- All formulas are **KaTeX** (inline `$...$` or block `$$...$$`).
- Method pages use mathematical equations, not mermaid flowcharts.

### Raw file policy
- Small text sources → copy into `raw/<subfolder>/`.
- PDFs → convert to markdown yourself, drop in `raw/incoming/`, then run ingest → `raw/papers/<slug>.md`.
- Large binaries / PDFs >10 MB → create a pointer file at `raw/refs/<slug>.md` with `kind: ref`
  and `external_path` fields. Do not copy the binary.

## Papers registry

```yaml
papers: []
```

## Open research questions

See [[wiki/open-questions]] for the detailed question list.
Add new questions there during ingest, compile, and audit operations.

## Research gaps

Sources to ingest:
- [ ] <author-keyword-year or URL> — why it's relevant

## Audit backlog

*(none — run `python3 scripts/audit_review.py <wiki-root> --open` to refresh)*

## Notes for the LLM

- Language: <en | zh | bilingual>
- Tone: <neutral, academic, conversational, ...>
- Depth: <survey-level | deep technical>
- Handling contradictions: state both, cite each, add to Open Research Questions.
"""
    _write(root, "CLAUDE.md", claude_md)
    print("✓ Created CLAUDE.md")

    # log/<today>.md
    log_md = f"""# {today_iso}

## [{now_hm}] scaffold | Initialized {title} knowledge base
- Created directory tree (raw/, wiki/, log/, audit/, outputs/)
- Created CLAUDE.md schema template
- Created wiki/index.md (generated artifact — do not edit manually)
- Created wiki/open-questions.md (manually maintained open questions)
"""
    _write(root, f"log/{today_compact}.md", log_md)
    print(f"✓ Created log/{today_compact}.md")

    # wiki/index.md — generated artifact; do NOT edit manually.
    # build_index.py regenerates this file from page frontmatter.
    # Only the header (H1 + blockquote) is preserved across rebuilds.
    index_md = f"""# Index — {title}

> One-sentence scope of the wiki.

## 🔖 Navigation
- [[#Problems]] · [[#Concepts]] · [[#Methods]] · [[#Theory]] · [[#Entities]] · [[#Summaries]]

## Problems

*(none yet)*

## Concepts

*(none yet)*

## Methods

*(none yet)*

## Theory

*(none yet)*

## Entities

*(none yet)*

## Summaries (chronological)

*(none yet)*
"""
    _write(root, "wiki/index.md", index_md)
    print("✓ Created wiki/index.md")

    # wiki/open-questions.md — manually maintained; NOT generated by build_index.py
    open_questions_md = f"""# Open Questions — {title}

Research questions that remain unresolved or need deeper investigation.
Add entries here during ingest, compile, and audit operations.

## Active questions

- <What do you want to understand better?>
- <What are the key open questions in this domain?>

## Deferred (awaiting more sources)

*(none yet)*
"""
    _write(root, "wiki/open-questions.md", open_questions_md)
    print("✓ Created wiki/open-questions.md")

    print(f"""
✅ Wiki scaffolded at: {root}/

Next steps:
  1. Fill in CLAUDE.md — define scope and naming conventions
  2. Set up the pre-commit hook (run once):
       ln -sf ../../.hooks/pre-commit .git/hooks/pre-commit
  3. Convert PDFs to markdown yourself and drop them into raw/incoming/ as .md files
  4. Tell your LLM agent "ingest all the incoming papers" (or name a specific file)
  5. Ask questions: "what does the wiki say about X?"
  6. Brainstorm: "brainstorm from [[concepts/<domain>/<concept>]]"
  7. Run lint periodically:  python3 llm-wiki/scripts/lint_wiki.py {root}
  8. Process feedback:       python3 llm-wiki/scripts/audit_review.py {root} --open
""")


def _write(root: str, path: str, content: str) -> None:
    full = os.path.join(root, path)
    os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    scaffold(sys.argv[1], sys.argv[2])
