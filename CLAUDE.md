# Causal ML Knowledge Base

> Schema document — read at the start of every session together with `wiki/index.md`.
> Update after every major compile, ingest batch, or structural change.

## Scope

What this wiki covers:
- causal machine learning
- statistical inference
- decision making, reinforcement learning
- LLMs and Agents


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
- **Summary pages** (`wiki/summaries/`): paper slug `{author}-{keyword}-{year}`.

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
- PDFs ≤10 MB → run `scripts/ingest_pdf.py --pdf raw/incoming/<file>.pdf` → `raw/papers/<slug>.md`.
- Large binaries / PDFs >10 MB → create a pointer file at `raw/refs/<slug>.md` with `kind: ref`
  and `external_path` fields. Do not copy the binary.

## Current articles

### Problems
- `problems/causal-inference/efficient-nonparametric-functional-estimation`
- `problems/llm-evaluation/ranking-from-preference-data`

### Concepts
- `concepts/statistics/efficient-influence-function`
- `concepts/statistics/von-mises-expansion`
- `concepts/statistics/cramer-rao-bound`
- `concepts/llm-evaluation/generalized-average-ranking-score`
- `concepts/llm-evaluation/bradley-terry-model`
- `concepts/llm-evaluation/rank-centrality`

### Methods
- `methods/statistics/one-step-estimator`
- `methods/statistics/cross-fitting`
- `methods/statistics/influence-function-calculus`
- `methods/llm-evaluation/dml-rank`
- `methods/llm-evaluation/optimal-preference-acquisition`

### Theory
- `theory/statistics/nonparametric-efficiency-bound`
- `theory/statistics/pathwise-differentiability`
- `theory/statistics/remainder-term-analysis-eif-based-estimator`
- `theory/llm-evaluation/gars-efficient-influence-function`

### Entities
- `entities/Edward-Kennedy`
- `entities/Dennis-Frauen`
- `entities/Athiya-Deviyani`
- `entities/Mihaela-van-der-Schaar`
- `entities/Stefan-Feuerriegel`

### Summaries
- `summaries/kennedy-semiparametric-doubly-robust-2023`
- `summaries/frauen-nonparametric-llm-evaluation-2026`

## Papers registry

```yaml
papers:
  - slug: kennedy-semiparametric-doubly-robust-2023
    title: "Semiparametric Doubly Robust Targeted Double Machine Learning: A Review"
    authors: [Edward H. Kennedy]
    venue: arXiv / review
    year: 2023
    domains: [causal-inference, statistics]
    status: ingested
  - slug: frauen-nonparametric-llm-evaluation-2026
    title: "Nonparametric LLM Evaluation from Preference Data"
    authors: [Dennis Frauen, Athiya Deviyani, Mihaela van der Schaar, Stefan Feuerriegel]
    venue: arXiv
    year: 2026
    domains: [llm-evaluation, causal-inference, statistics]
    status: ingested
```

## Open research questions

- <What do you want to understand better?>
- <What are the key open questions in this domain?>

## Research gaps

Sources to ingest:
- [ ] <author-keyword-year or URL> — why it's relevant

## Audit backlog

*(none — run `python3 scripts/audit_review.py <wiki-root> --open` to refresh)*

## Notes for the LLM

- Language: english
- Tone: neutral, candid, academic
- Depth: Deep, theoretic
- Handling contradictions: state both, cite each, add to Open Research Questions.
