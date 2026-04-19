# CLAUDE.md Schema Guide

`CLAUDE.md` (also read as `AGENTS.md` by some tools) is the **schema document** for a wiki topic. It tells the LLM agent the scope, conventions, current state, and open questions — every session should start by reading it together with `wiki/index.md`.

## Why it matters

Without a schema, the LLM creates inconsistent page names, overlapping articles, and drifts from the wiki's intended scope. With a well-maintained schema, the LLM becomes a disciplined, consistent wiki maintainer.

**Co-evolve it with the wiki** — update after every major compile, ingest batch, or structural change.

## Full template

```markdown
# <Topic Title> Knowledge Base

> Schema document — read at the start of every session together with wiki/index.md.

## Scope

What this wiki covers:
- <bullet list of included areas>

What this wiki deliberately excludes:
- <bullet list of out-of-scope areas>

## Operations

This wiki follows the llm-wiki skill's six operations: `compile`, `ingest`, `query`, `lint`, `audit`, `brainstorm`.
Every operation appends an entry to `log/YYYYMMDD.md`.

## Naming conventions

### Pages (PCMT ontology)
- **Problem pages** (`wiki/problems/<domain>/`): kebab-case noun phrases naming a research challenge.
  E.g., `long-term-treatment-effects.md`, `out-of-distribution-generalization.md`
- **Concept pages** (`wiki/concepts/<domain>/`): kebab-case noun phrases naming a domain object.
  E.g., `surrogate-index.md`, `average-treatment-effect.md`
- **Method pages** (`wiki/methods/<domain>/`): kebab-case noun phrases naming a procedure.
  E.g., `doubly-robust-estimation.md`, `cross-fitting.md`
- **Theory pages** (`wiki/theory/<domain>/`): kebab-case noun phrases naming a mathematical tool.
  E.g., `efficient-influence-function.md`, `semiparametric-efficiency-bound.md`
- **Entity pages** (`wiki/entities/`): Proper names. E.g., "Susan Athey", "PyTorch".
- **Summary pages** (`wiki/summaries/`): paper slug. E.g., `athey-surrogate-index-2019`.

### Domain subdirectories
`<domain>/` is a namespace prefix inside each PCMT type directory. It prevents naming
collisions across many papers. Use existing domains when possible; create new ones freely.
Suggested starting domains: `causal-inference`, `machine-learning`, `statistics`,
`econometrics`, `optimization`, `information-theory`.

### Wikilinks
- Always use `[[Page Title]]` — exact page title, case-sensitive, or the relative path.
- For PCMT pages use relative path form: `[[concepts/causal-inference/surrogate-index]]`.
- For folder-split pages, link to the index: `[[concepts/causal-inference/foo/index|Foo]]`.
- Link the first mention of every entity or concept. Do not link the same page more than twice per article.

### Frontmatter
Every wiki page has YAML frontmatter:
```yaml
---
title: <Page Title>
type: problem | concept | method | theory | entity | summary
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [list of raw/ slugs this page draws from]
tags: [relevant tags]
---
```

### Diagrams and formulas
- All diagrams are **mermaid**. No ASCII art.
- All formulas are **KaTeX** (inline `$...$` or block `$$...$$`).

### Raw file policy
- Small text sources → copy into `raw/<subfolder>/`.
- PDFs → convert to markdown yourself, drop in `raw/incoming/`, then run ingest → `raw/papers/<slug>.md`.
- Large binaries / PDFs >10 MB → create a pointer file at `raw/refs/<slug>.md` with `kind: ref`
  frontmatter and an `external_path` field. Do not copy the binary.

## Current articles

### Problems
*(none — update after each ingest)*

#### <domain-a>
- [[problems/<domain-a>/<slug>]] — one-line summary

### Concepts

#### <domain-a>
- [[concepts/<domain-a>/<slug>]] — one-line summary
- [[concepts/<domain-a>/<topic>/index|<topic>]] — (folder-split) one-line summary
    - [[concepts/<domain-a>/<topic>/<aspect>]] — ...

### Methods

#### <domain-a>
- [[methods/<domain-a>/<slug>]] — one-line summary

### Theory

#### <domain-a>
- [[theory/<domain-a>/<slug>]] — one-line summary

### Entities
- [[entities/<Name>]] — one-line summary

### Summaries
- [[summaries/<slug>]] — source title (year)

## Papers registry

Track every ingested academic paper here. Update `status` as work progresses.

```yaml
papers:
  - slug: <author>-<keyword>-<year>
    title: "<Full Paper Title>"
    authors: [LastName1, LastName2]
    venue: <Journal / Conference / ArXiv>
    year: YYYY
    domains: [domain1, domain2]
    status: incoming   # incoming | ingested | compiled
```

## Open research questions

- <Questions that should drive future ingest/query work>
- <Things the wiki currently doesn't cover well>
- <Contradictions or gaps noticed between articles>

## Research gaps

Sources to ingest:
- [ ] <author-keyword-year> — why it's relevant

## Audit backlog

Count of open audits per target (filled in after running `audit_review.py --open`):
- <file> — N open
- ...

## Notes for the LLM

<Any special instructions: tone, depth level, language (zh/en), how to handle contradictions, etc.>
```

## What makes a good schema

**Good scope definition** prevents sprawl. A wiki about "causal inference" should exclude "deep learning" even if some papers touch both.

**Explicit naming conventions** keep wikilinks from breaking. If you decide on kebab-case PCMT pages, enforce it — a broken wikilink is an orphan.

**Maintained article list** lets the LLM know what already exists before creating a new page. The most common error is creating duplicate articles with slightly different names.

**Papers registry** is the backbone for a 1000-paper wiki. It lets you query "what papers on causal inference have I ingested?" without traversing the whole wiki directory, and tracks whether each paper has been fully compiled into PCMT pages.

**Open research questions** give the LLM direction. Without them, the LLM defaults to ingesting the most obvious sources and missing your actual questions.

**Audit backlog** surfaces what the human has flagged as wrong. The AI should glance at it at the start of every session to decide whether to run an `audit` op before ingesting new material.

## Update cadence

- After every new PCMT page: add to "Current articles" under the right section.
- After every ingest: append entry to "Papers registry"; update "Sources to ingest" checklist.
- After every lint pass: update "Research gaps".
- After every audit pass: refresh the "Audit backlog" counts.
- Monthly: review scope, prune stale research questions.
