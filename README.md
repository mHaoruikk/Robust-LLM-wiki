# llm-wiki

**A Claude Code skill for building Karpathy-style LLM knowledge bases — optimized for academic research.**

> Experimental skill — will iterate over time.
> Please send your feedback in GitHub issues.

Inspired by [Andrej Karpathy's llm-wiki Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) and the community's work building on it.

## What this is

Instead of RAG (re-retrieving raw docs on every query), this pattern has the LLM **compile** raw sources into a persistent, cross-linked Markdown wiki. Every `ingest`, `query`, `lint`, `audit`, and `brainstorm` pass makes the wiki richer. Knowledge compounds over time — and because the wiki is semantically structured, it becomes a traversable graph for cross-domain research ideation.

- **You** own: sourcing raw material, asking good questions, steering direction, filing feedback on things the AI got wrong.
- **LLM** owns: all writing, cross-referencing, filing, bookkeeping, and acting on your feedback.

---

## Research ontology — PCMT

The core design choice that makes this skill suited for academic research is the **PCMT ontology**: instead of a generic topic hierarchy, every wiki page has a semantically typed role.

| Type | Directory | Grammar role | What belongs here |
|------|-----------|-------------|-------------------|
| **Problem** | `wiki/problems/` | *Questions* | Research challenges that multiple papers address |
| **Concept** | `wiki/concepts/` | *Nouns* | Named domain objects, quantities, phenomena, assumptions |
| **Method** | `wiki/methods/` | *Verbs* | Reusable estimation approaches and algorithms (method families, not bespoke paper estimators) |
| **Theory** | `wiki/theory/` | *Machinery* | Theorems, bounds, and proof techniques used as tools |

A paper's summary page links outward to these four types, acting as a map. PCMT pages are **shared across papers** — 100 papers contribute to 20 theory pages, not 100. The graph that forms is what enables the `brainstorm` operation.

**Example — Athey et al. "The Surrogate Index" (2019):**
```
wiki/problems/causal-inference/long-term-treatment-effects.md
wiki/concepts/causal-inference/surrogate-index.md
wiki/concepts/causal-inference/surrogacy-assumption.md
wiki/theory/statistics/efficient-influence-function.md
wiki/theory/statistics/semiparametric-efficiency-bound.md
wiki/methods/statistics/cross-fitting.md
wiki/summaries/athey-surrogate-index-2019.md        ← links to all of the above
wiki/entities/Susan-Athey.md
```

The paper's specific estimator is described in the summary, not as a method page — method pages are promoted only when a procedure becomes reusable across papers.

---

## The six operations

| Operation | What it does |
|-----------|-------------|
| `compile` | Restructure wiki — split oversized pages, merge duplicates |
| `ingest` | Add a source — create summary + propose PCMT pages for approval |
| `query` | Answer a question grounded in the wiki; optionally promote durable answers |
| `lint` | 8-pass health check: dead links, orphans, PCMT type integrity, stale index, audit shape |
| `audit` | Process human feedback hand-written as YAML files in `audit/` |
| `brainstorm` | Traverse the knowledge graph from a seed to generate cross-domain research directions |
| `build-index` | Regenerate `wiki/index.md` from page frontmatter via `build_index.py` (agent asks permission before running) |

> **Index note**: The agent never edits `wiki/index.md` directly. Use the `build-index` command to regenerate it from page frontmatter. See [Deterministic index builder](#deterministic-index-builder) below.

---

## Install

```bash
# Copy the skill into Claude Code's skills directory
cp -r llm-wiki/ ~/.claude/skills/llm-wiki/
```

Then reference it in your agent config, or paste `llm-wiki/SKILL.md` into your agent context.

---

## Quick start

```bash
# 1. Scaffold a new wiki
python3 llm-wiki/scripts/scaffold.py ~/my-wiki "Causal Inference"

# 2. (Optional) Initialize git
cd ~/my-wiki && git init && git add . && git commit -m "scaffold"

# 3. Convert a PDF to markdown yourself (any tool you prefer) and drop it in incoming/
cp athey2019_converted.md ~/my-wiki/raw/incoming/

# 4. Tell your agent: "ingest all the incoming papers"
#    The agent extracts metadata, moves the file to raw/papers/<slug>.md,
#    then creates the summary and proposes new PCMT pages;
#    you approve before any new PCMT page is written.

# 5. Rebuild the index when ready
#    Tell the agent: "build-index"

# 6. Ask questions
#    "what does the wiki say about long-term treatment effects?"

# 7. Brainstorm
#    "brainstorm from [[concepts/causal-inference/surrogate-index]]"

# 8. Run lint periodically
python3 llm-wiki/scripts/lint_wiki.py ~/my-wiki

# 9. Hand-write audit files under ~/my-wiki/audit/ for corrections, then process them
python3 llm-wiki/scripts/audit_review.py ~/my-wiki --open
# then tell the agent: "audit: process the open comments"
```

---

---

## Deterministic index builder

`wiki/index.md` is a **generated artifact**, not a hand-maintained file. The agent reads it at session start but never writes to it directly. Instead, `llm-wiki/scripts/build_index.py` regenerates it deterministically from each page's frontmatter when you invoke the `build-index` command.

**Why this matters**: the previous pattern had the agent update `wiki/index.md` inline during every ingest and compile. This worked for simple cases but drifted on long multi-page operations — the agent would finish writing content and forget to add the new page to the index, or add it under the wrong domain section. By moving index maintenance to a deterministic script, the index is always exactly what the pages say it should be.

**How it works:**

1. You write and edit content pages normally.
2. When you want the index updated, tell the agent `build-index` (it will ask permission before running the script).
3. The script scans `wiki/`, reads frontmatter from every content page, and regenerates `wiki/index.md` with correct PCMT sections, domain groupings, folder-split hierarchies, and reverse-chronological summaries.

**Manual header is preserved**: the script preserves the H1 title line and the blockquote scope sentence at the top of `index.md` across rebuilds — those are the only two lines you ever edit by hand.

**Open questions** live in `wiki/open-questions.md`, a plain markdown file that the agent edits directly during ingest and audit operations.

**Running the builder manually:**
```bash
# Regenerate index in place
python3 llm-wiki/scripts/build_index.py <wiki-root>

# Check whether the index is stale without writing (useful in CI)
python3 llm-wiki/scripts/build_index.py <wiki-root> --check

# Warn instead of fail on pages with missing frontmatter (migration run)
python3 llm-wiki/scripts/build_index.py <wiki-root> --migrate
```

---

## Paper ingestion pipeline

Convert PDFs to markdown yourself (using any tool you prefer), then drop the `.md` file into `raw/incoming/`. When you tell the agent to ingest, it will:

1. **Extract metadata** — reads the markdown and extracts title, authors, year, venue, domains, and slug via Claude
2. **Copy + rename** — creates `raw/papers/<slug>.md`, copies the complete incoming markdown into it, and adds a YAML front matter header
3. **Clean up** — deletes the original file from `raw/incoming/`
4. **Continue ingest** — creates the summary page and proposes new PCMT pages for your approval

After the file is created in `raw/papers/`, it is treated as immutable source material. The agent must copy the full incoming paper content into `raw/papers/<slug>.md` and must not modify files already under `raw/` after that step.

**Paper slug format:** `{first-author-lastname}-{core-keyword(s)}-{year}` — e.g., `vaswani-attention-2017`, `chernozhukov-double-debiased-ml-2018`.

---

## Repo contents

```
llm-wiki-skill/
└── llm-wiki/                    ← The skill
    ├── SKILL.md                 ← Main skill file (read by agent)
    ├── references/
    │   ├── ontology-guide.md    ← PCMT decision rules + worked examples
    │   ├── paper-guide.md       ← Paper naming, ingest steps, propose-before-create
    │   ├── schema-guide.md      ← CLAUDE.md schema template
    │   ├── article-guide.md     ← Page templates for all 6 types + writing rules
    │   ├── log-guide.md         ← log/ folder convention
    │   ├── audit-guide.md       ← Audit file format + processing workflow
    │   └── tooling-tips.md      ← Obsidian, qmd, Marp, git workflow
    └── scripts/
        ├── scaffold.py          ← Bootstrap new wiki directory (PCMT layout)
        ├── build_index.py       ← Deterministic wiki/index.md generator
        ├── lint_wiki.py         ← 8-pass health check (links, PCMT types, stale index, audit, log)
        └── audit_review.py      ← Group open/resolved audits by target
```

---

## Use cases

- **PhD research** — ingesting hundreds of academic papers; PCMT separates problems, methods, and mathematical tools cleanly; `brainstorm` surfaces cross-domain connections for novel research directions
- **Research deep-dive** — reading papers on a topic over weeks; the wiki evolves with your understanding; the audit trail keeps AI mistakes from silently accumulating
- **Personal wiki** — journal entries and notes compiled into a personal encyclopedia; file corrections later, the AI applies them

---

## Related work

- [Karpathy's original Gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [pedronauck/skills karpathy-kb](https://github.com/pedronauck/skills/tree/main/skills/karpathy-kb) — full Obsidian vault integration
- [Astro-Han/karpathy-llm-wiki](https://github.com/Astro-Han/karpathy-llm-wiki) — example implementation
- [qmd](https://github.com/tobi/qmd) — semantic search for Markdown wikis

## License

MIT
